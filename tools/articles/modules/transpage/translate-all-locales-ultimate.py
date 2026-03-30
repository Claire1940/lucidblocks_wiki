#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译所有 routing.ts 中定义的语言（最终增强版）
修复问题：
1. 路径解析 - 自动定位项目根目录
2. API 响应处理 - 支持流式和非流式响应
3. Windows 编码 - 强制使用 UTF-8
4. 输出缓冲 - 强制实时输出 ⭐ 新增
5. 进度显示 - 实时显示翻译进度 ⭐ 新增
"""

import asyncio
import json
import re
import sys
import os
from pathlib import Path

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    # 强制使用 UTF-8 编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 > nul 2>&1')

# 添加父目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from translator import MessagesTranslator
from smart_chunk_translator import SmartChunkTranslator


def print_flush(msg, end="\n"):
    """强制刷新输出"""
    print(msg, end=end, flush=True)
    sys.stdout.flush()


def find_project_root():
    """
    查找项目根目录（包含 package.json 的目录）
    从脚本所在目录向上查找
    """
    current = Path(script_dir)

    # 向上查找最多 5 层
    for _ in range(5):
        package_json = current / 'package.json'
        if package_json.exists():
            return current
        current = current.parent

    # 如果找不到，假设脚本在 tools/articles/modules/transpage/
    # 项目根目录在 ../../../../
    return Path(script_dir).parent.parent.parent.parent


def extract_locales_from_routing(project_root):
    """从 routing.ts 提取语言列表"""
    routing_file = project_root / 'src' / 'i18n' / 'routing.ts'

    if not routing_file.exists():
        print_flush(f"[错误] 找不到 {routing_file}")
        return None

    content = routing_file.read_text(encoding='utf-8')

    # 匹配 locales: ['en', 'es', ...]
    match = re.search(r"locales:\s*\[([^\]]+)\]", content)

    if not match:
        print_flush("[错误] 无法从 routing.ts 解析语言列表")
        return None

    # 提取语言代码
    locales_str = match.group(1)
    locales = [loc.strip().strip("'\"") for loc in locales_str.split(',')]

    # 移除 'en'（源语言）
    locales = [loc for loc in locales if loc != 'en']

    return locales


async def translate_language(translator, smart_translator, lang, project_root, overwrite=False):
    """翻译单个语言"""
    locales_dir = project_root / 'src' / 'locales'
    output_file = locales_dir / f'{lang}.json'

    # 检查是否已存在
    if output_file.exists() and not overwrite:
        print_flush(f"[跳过] {lang.upper()} - 文件已存在（使用 --overwrite 强制覆盖）")
        return {'lang': lang, 'status': 'skipped'}

    # 读取英文源文件
    en_file = locales_dir / 'en.json'
    if not en_file.exists():
        print_flush(f"[错误] 找不到英文源文件: {en_file}")
        return {'lang': lang, 'status': 'failed', 'error': 'Source file not found'}

    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    print_flush(f"\n{'='*70}")
    print_flush(f"[开始] 翻译 {lang.upper()}")
    print_flush(f"{'='*70}")
    print_flush(f"[信息] 源文件大小: {len(json.dumps(en_data))} 字符")
    print_flush(f"[信息] 顶层键数量: {len(en_data)}")

    # 使用智能分块翻译
    import aiohttp

    # 创建带超时的连接器
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=10)
    timeout = aiohttp.ClientTimeout(total=3600, connect=120, sock_read=1800)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        print_flush(f"[开始] 使用智能分块翻译...")
        success, translated_data, report = await smart_translator.translate_with_fallback(
            en_data,
            lang,
            session
        )

    if success:
        # 保存结果
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_data, f, indent=2, ensure_ascii=False)

        print_flush(f"\n[成功] {lang.upper()} - 已保存到 {output_file}")
        print_flush(f"[信息] 输出文件大小: {len(json.dumps(translated_data))} 字符")
        return {'lang': lang, 'status': 'success', 'file': str(output_file)}
    else:
        print_flush(f"\n[失败] {lang.upper()} - {report.get('error', 'Unknown error')}")
        return {'lang': lang, 'status': 'failed', 'error': report.get('error')}


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='翻译所有 routing.ts 中定义的语言（最终增强版）')
    parser.add_argument('--overwrite', action='store_true', help='覆盖已有翻译文件')
    parser.add_argument('--lang', type=str, help='只翻译指定语言（逗号分隔），如: es,pt')
    args = parser.parse_args()

    # 查找项目根目录
    project_root = find_project_root()
    print_flush(f"[项目根目录] {project_root}")

    # 验证项目根目录
    if not (project_root / 'package.json').exists():
        print_flush(f"[错误] 无法找到项目根目录（package.json 不存在）")
        sys.exit(1)

    # 获取语言列表
    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
        print_flush(f"[模式] 手动指定语言: {', '.join(target_langs)}")
    else:
        target_langs = extract_locales_from_routing(project_root)
        if not target_langs:
            print_flush("[错误] 无法获取语言列表")
            sys.exit(1)
        print_flush(f"[模式] 从 routing.ts 读取语言: {', '.join(target_langs)}")

    # 加载配置
    config_file = Path(script_dir) / 'transpage_config.json'
    if not config_file.exists():
        print_flush(f"[错误] 找不到配置文件: {config_file}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化翻译器
    print_flush(f"\n[初始化] 正在初始化翻译系统...")
    translator = MessagesTranslator(config)
    smart_translator = SmartChunkTranslator(translator, config)

    print_flush(f"\n{'='*70}")
    print_flush(f"[配置] 翻译系统已初始化")
    print_flush(f"  - API: {config.get('api_base_url')}")
    print_flush(f"  - 模型: {config.get('model')}")
    print_flush(f"  - 超时: {config.get('timeout')}秒")
    print_flush(f"  - 重试次数: {config.get('retry_attempts')}")
    print_flush(f"  - 目标语言数: {len(target_langs)}")
    print_flush(f"  - 覆盖模式: {'是' if args.overwrite else '否'}")
    print_flush(f"{'='*70}\n")

    # 翻译所有语言（逐个翻译，避免并发问题）
    results = []
    for idx, lang in enumerate(target_langs, 1):
        print_flush(f"\n[进度] {idx}/{len(target_langs)} - 正在翻译 {lang.upper()}...")
        result = await translate_language(translator, smart_translator, lang, project_root, args.overwrite)
        results.append(result)

        # 每个语言之间稍微延迟，避免 API 限流
        if idx < len(target_langs):
            print_flush(f"[等待] 2秒后继续下一个语言...")
            await asyncio.sleep(2)

    # 统计结果
    success_count = len([r for r in results if r['status'] == 'success'])
    failed_count = len([r for r in results if r['status'] == 'failed'])
    skipped_count = len([r for r in results if r['status'] == 'skipped'])

    print_flush(f"\n{'='*70}")
    print_flush(f"[完成] 翻译任务总结")
    print_flush(f"{'='*70}")
    print_flush(f"  总计:   {len(results)}")
    print_flush(f"  成功:   {success_count}")
    print_flush(f"  失败:   {failed_count}")
    print_flush(f"  跳过:   {skipped_count}")

    if success_count > 0:
        print_flush(f"\n  成功率: {success_count / len(results) * 100:.1f}%")

    # 显示失败详情
    failed_results = [r for r in results if r['status'] == 'failed']
    if failed_results:
        print_flush("\n  失败详情:")
        for result in failed_results:
            print_flush(f"    - {result['lang'].upper()}: {result.get('error', 'Unknown error')}")

    print_flush(f"{'='*70}\n")


if __name__ == '__main__':
    # 设置事件循环策略（Windows 兼容）
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
