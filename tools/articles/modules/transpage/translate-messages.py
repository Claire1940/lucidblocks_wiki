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
    api_url = f"{config['api_base_url'].rstrip('/')}/chat/completions"
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
    """去除 markdown 代码块，提取纯 JSON"""
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```\w*\n?', '', text)
        text = re.sub(r'\n?```$', '', text)
    return text.strip()

# ─── chunk 拆分 ───────────────────────────────────────────────────────────────


def split_into_chunks(data: dict, chunk_count: int = 10) -> list:
    """将顶层 key 均匀分成 chunk_count 组"""
    keys = list(data.keys())
    n = len(keys)
    size = max(1, -(-n // chunk_count))  # 向上取整
    chunks = []
    for i in range(0, n, size):
        chunk_keys = keys[i:i + size]
        chunks.append({k: data[k] for k in chunk_keys})
    return chunks

# ─── 翻译单个语言 ─────────────────────────────────────────────────────────────


def translate_language(
    lang: str,
    lang_name: str,
    en_data: dict,
    config: dict,
    overwrite: bool = False,
    incremental: bool = False,
    chunk_count: int = 10,
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
    print(f"  [开始] {lang.upper()} ({lang_name}) - {total} 个 chunk")

    translated: dict = {}

    for idx, chunk in enumerate(chunks, 1):
        keys_preview = ', '.join(list(chunk.keys())[:3])
        suffix = '...' if len(chunk) > 3 else ''
        print(f"    chunk {idx}/{total}: [{keys_preview}{suffix}]", end=' ', flush=True)

        chunk_json = json.dumps(chunk, ensure_ascii=False, indent=2)
        result = call_api(chunk_json, lang_name, config)

        if result:
            cleaned = clean_json_response(result)
            try:
                parsed = json.loads(cleaned)
                translated.update(parsed)
                print("✓")
            except json.JSONDecodeError as e:
                print(f"✗ JSON解析失败({e})，使用英文兜底")
                translated.update(chunk)
        else:
            print("✗ API失败，使用英文兜底")
            translated.update(chunk)

    # 合并：existing + 新翻译（新翻译优先）
    merged = {**existing, **translated}

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
    print(f"Chunk 数: {args.chunks}")
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
        )

    print("=" * 60)
    print(f"[完成] {len(target_langs)} 个语言处理完毕")
    print("=" * 60)


if __name__ == '__main__':
    main()
