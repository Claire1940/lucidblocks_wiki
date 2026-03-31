#!/usr/bin/env python3
"""
translate-messages.py - 顺序翻译脚本

完全独立实现，不依赖 smart_chunk_translator.py / translator.py / translate-messages-enhanced.py。

设计原则：
- 语言顺序执行（不并发）
- chunk 顺序执行（不并发）
- API 失败自动用英文兜底，不阻塞
- 自动读取 transpage_config.json 配置

使用方法：
    # 翻译所有配置语言（读取 transpage_config.json 的 languages 字段）
    python3 translate-messages.py --overwrite

    # 翻译指定语言
    python3 translate-messages.py --lang ja,es --overwrite

    # 增量翻译（只翻译缺失的顶层 key）
    python3 translate-messages.py --incremental

    # 自定义 chunk 数
    python3 translate-messages.py --overwrite --chunks 10
"""

import json
import os
import sys
import re
import time
import argparse
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

# ─── 自动定位项目根目录 ────────────────────────────────────────────────────────

script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = script_dir / 'transpage_config.json'


def find_project_root() -> Path:
    """向上查找含 package.json 的目录"""
    current = script_dir
    for _ in range(8):
        if (current / 'package.json').exists():
            return current
        current = current.parent
    return script_dir.parent.parent.parent.parent


PROJECT_ROOT = find_project_root()

# ─── 加载配置 ─────────────────────────────────────────────────────────────────


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print(f"[FAIL] 找不到配置文件: {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# ─── API 调用 ─────────────────────────────────────────────────────────────────


def call_api(content: str, lang_name: str, config: dict, timeout: int = 60, retries: int = 3) -> Optional[str]:
    """调用翻译 API，失败返回 None"""
    base = config['api_base_url'].rstrip('/')
    # 兼容各种写法：/v1、/v1/、/v1/chat/completions 均可正常工作
    if base.endswith('/chat/completions'):
        api_url = base
    else:
        api_url = f"{base}/chat/completions"
    api_key = config['api_key']
    model = config.get('model', 'gemini-2.5-flash')
    temperature = config.get('temperature', 0.1)

    # 构建专有名词保护列表
    protected = config.get('protected_terms', {})
    protected_list = (
        protected.get('game_names', []) +
        protected.get('character_names', []) +
        protected.get('technical_terms', [])
    )
    protect_note = f"\nKeep these terms unchanged: {', '.join(protected_list)}" if protected_list else ''

    prompt = (
        f"Translate the following JSON values to {lang_name}.\n"
        f"IMPORTANT: Return ONLY valid JSON without markdown code blocks.\n"
        f"Keep ALL keys exactly as-is. Only translate string values.{protect_note}\n\n"
        f"{content}"
    )

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": config.get('max_tokens', 8192),
        "temperature": temperature,
    }).encode('utf-8')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(api_url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"    [retry {attempt}/{retries}] {e}")
            if attempt < retries:
                time.sleep(5)

    return None

# ─── JSON 清理 ────────────────────────────────────────────────────────────────


def clean_json_response(text: str) -> str:
    """去除 markdown 代码块，提取纯 JSON，移除非法控制字符"""
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    # 移除 JSON 字符串中的非法控制字符（保留 \t \n \r）
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    return text.strip()

# ─── chunk 拆分 ───────────────────────────────────────────────────────────────


def count_values(obj) -> int:
    """递归统计 leaf string value 数量"""
    if isinstance(obj, str):
        return 1
    if isinstance(obj, dict):
        return sum(count_values(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_values(v) for v in obj)
    return 0


def split_into_chunks(data: dict, chunk_count: int = 10) -> list:
    """按 leaf string value 数量均匀装箱。
    超大顶层 key（value 数 > target）会按其子 key 拆分，合并时用 deep_merge。
    """
    total = count_values(data)
    target = max(1, total // chunk_count)

    # 展开：超大 key 按子 key 拆分成独立 item
    items = []  # (top_key, sub_key_or_None, value, weight)
    for k, v in data.items():
        w = count_values(v)
        if w > target and isinstance(v, dict) and len(v) > 1:
            for sub_k, sub_v in v.items():
                items.append((k, sub_k, sub_v, count_values(sub_v)))
        else:
            items.append((k, None, v, w))

    # 贪心装箱
    raw_chunks, current, cur_w = [], [], 0
    for item in items:
        current.append(item)
        cur_w += item[3]
        if cur_w >= target and len(raw_chunks) < chunk_count - 1:
            raw_chunks.append(current)
            current, cur_w = [], 0
    if current:
        raw_chunks.append(current)

    # 重建 dict（同 top_key 的子项合并到同一父 key 下）
    chunks = []
    for raw in raw_chunks:
        chunk = {}
        for k, sub_k, v, _ in raw:
            if sub_k is None:
                chunk[k] = v
            else:
                chunk.setdefault(k, {})[sub_k] = v
        chunks.append(chunk)
    return chunks

# ─── deep merge ──────────────────────────────────────────────────────────────


def deep_merge(base: dict, update: dict) -> dict:
    """递归合并两个 dict，update 优先；同名 dict 子树递归合并"""
    result = dict(base)
    for k, v in update.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result

# ─── 翻译单个语言 ─────────────────────────────────────────────────────────────


def translate_chunk_task(idx: int, total: int, chunk: dict, lang_name: str, config: dict) -> tuple:
    """单个 chunk 的翻译任务，返回 (idx, chunk_key_order, translated_dict)"""
    keys_preview = ', '.join(list(chunk.keys())[:3])
    suffix = '...' if len(chunk) > 3 else ''
    print(f"    chunk {idx}/{total}: [{keys_preview}{suffix}] 开始", flush=True)

    chunk_json = json.dumps(chunk, ensure_ascii=False, indent=2)
    result = call_api(chunk_json, lang_name, config)

    if result:
        cleaned = clean_json_response(result)
        try:
            parsed = json.loads(cleaned)
            print(f"    chunk {idx}/{total}: [{keys_preview}{suffix}] ✓")
            return (idx, list(chunk.keys()), parsed)
        except json.JSONDecodeError as e:
            print(f"    chunk {idx}/{total}: [{keys_preview}{suffix}] ✗ JSON解析失败({e})，英文兜底")
            return (idx, list(chunk.keys()), chunk)
    else:
        print(f"    chunk {idx}/{total}: [{keys_preview}{suffix}] ✗ API失败，英文兜底")
        return (idx, list(chunk.keys()), chunk)


def translate_language(
    lang: str,
    lang_name: str,
    en_data: dict,
    config: dict,
    overwrite: bool = False,
    incremental: bool = False,
    chunk_count: int = 10,
    concurrency: int = 5,
) -> bool:
    output_dir = PROJECT_ROOT / config.get('output_dir', 'src/locales/')
    output_path = output_dir / f'{lang}.json'

    # 读取已有翻译
    existing: dict = {}
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    # 决定需要翻译的数据
    if incremental:
        to_translate = {k: v for k, v in en_data.items() if k not in existing}
        if not to_translate:
            print(f"  [跳过] {lang.upper()} - 无新增内容\n")
            return True
        print(f"  [增量] {lang.upper()} - 翻译 {len(to_translate)} 个缺失顶层 key")
    elif not overwrite and output_path.exists():
        print(f"  [跳过] {lang.upper()} - 文件已存在（使用 --overwrite 强制覆盖）\n")
        return True
    else:
        to_translate = en_data

    # 按 chunk_count 拆分
    chunks = split_into_chunks(to_translate, chunk_count)
    total = len(chunks)
    print(f"  [开始] {lang.upper()} ({lang_name}) - {total} 个 chunk，并发度 {concurrency}")

    # 并发度 concurrency 执行所有 chunk
    results = [None] * total
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {
            executor.submit(translate_chunk_task, idx + 1, total, chunk, lang_name, config): idx
            for idx, chunk in enumerate(chunks)
        }
        for future in as_completed(futures):
            idx_result, _, translated_chunk = future.result()
            results[idx_result - 1] = translated_chunk

    # 按原始顺序 deep merge（同一顶层 key 可能来自多个 chunk）
    translated: dict = {}
    for r in results:
        if r:
            translated = deep_merge(translated, r)

    # incremental 模式：保留已有翻译，新翻译补充；overwrite 模式：完全替换
    if incremental:
        merged = deep_merge(existing, translated)
    else:
        merged = translated

    # 保存
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    lines = sum(1 for _ in open(output_path, encoding='utf-8'))
    print(f"  [完成] {lang.upper()} → {output_path.relative_to(PROJECT_ROOT)} ({lines} 行)\n")
    return True

# ─── 主流程 ───────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description='顺序翻译脚本 - 语言和 chunk 均顺序执行，不并发')
    parser.add_argument('--lang', type=str, default=None,
                        help='目标语言（逗号分隔，如: ja,es,pt）；不传则读取 transpage_config.json 的 languages 字段')
    parser.add_argument('--overwrite', action='store_true', help='覆盖已有翻译文件')
    parser.add_argument('--incremental', action='store_true', help='增量翻译（只翻译缺失的顶层 key）')
    parser.add_argument('--chunks', type=int, default=10, help='每个语言拆成几个 chunk（默认 10）')
    parser.add_argument('--concurrency', type=int, default=5, help='chunk 并发度（默认 5）')
    args = parser.parse_args()

    config = load_config()
    print(f"[OK] 配置已加载: {CONFIG_PATH}")
    print(f"[OK] 项目根目录: {PROJECT_ROOT}")
    print(f"[OK] API: {config['api_base_url']} / 模型: {config.get('model')}\n")

    # 读取英文源文件
    en_path = PROJECT_ROOT / config.get('output_dir', 'src/locales/') / 'en.json'
    if not en_path.exists():
        print(f"[FAIL] 找不到英文源文件: {en_path}")
        sys.exit(1)
    with open(en_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    print(f"[OK] 英文源文件: {en_path} ({len(en_data)} 个顶层 key)\n")

    # 确定目标语言
    if args.lang:
        target_langs = [l.strip() for l in args.lang.split(',')]
    else:
        target_langs = config.get('languages', [])

    if not target_langs:
        print("[FAIL] 没有目标语言，请通过 --lang 参数或 transpage_config.json 的 languages 字段配置")
        sys.exit(1)

    lang_names: dict = config.get('lang_names', {})

    print("=" * 60)
    print(f"目标语言: {', '.join(target_langs)}")
    print(f"模式: {'增量' if args.incremental else '完整覆盖' if args.overwrite else '跳过已存在'}")
    print(f"Chunk 数: {args.chunks}，并发度: {args.concurrency}")
    print("=" * 60 + "\n")

    for i, lang in enumerate(target_langs, 1):
        lang_name = lang_names.get(lang, lang)
        print(f"[{i}/{len(target_langs)}] {lang.upper()} ({lang_name})")
        translate_language(
            lang=lang,
            lang_name=lang_name,
            en_data=en_data,
            config=config,
            overwrite=args.overwrite,
            incremental=args.incremental,
            chunk_count=args.chunks,
            concurrency=args.concurrency,
        )

    print("=" * 60)
    print(f"[完成] {len(target_langs)} 个语言处理完毕")
    print("=" * 60)


if __name__ == '__main__':
    main()
