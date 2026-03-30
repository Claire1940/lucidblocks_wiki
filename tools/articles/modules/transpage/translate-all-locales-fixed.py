#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译所有 routing.ts 中定义的语言（修复版）
修复问题：
1. 路径解析 - 自动定位项目根目录
2. API 响应处理 - 支持流式和非流式响应
3. Windows 编码 - 强制使用 UTF-8
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
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # 设置控制台代码页为 UTF-8
    os.system('chcp 65001 > nul 2>&1')

# 添加父目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

from translator import MessagesTranslator
from smart_chunk_translator import SmartChunkTranslator


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
        print(f"[错误] 找不到 {routing_file}")
        return None

    content = routing_file.read_text(encoding='utf-8')

    # 匹配 locales: ['en', 'es', ...]
    match = re.search(r"locales:\s*\[([^\]]+)\]", content)

    if not match:
        print("[错误] 无法从 routing.ts 解析语言列表")
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
        print(f"[跳过] {lang.upper()} - 文件已存在（使用 --overwrite 强制覆盖）")
        return {'lang': lang, 'status': 'skipped'}

    # 读取英文源文件
    en_file = locales_dir / 'en.json'
    if not en_file.exists():
        print(f"[错误] 找不到英文源文件: {en_file}")
        return {'lang': lang, 'status': 'failed', 'error': 'Source file not found'}

    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    print(f"\n{'='*70}")
    print(f"[开始] 翻译 {lang.upper()}")
    print(f"{'='*70}")

    # 使用智能分块翻译
    import aiohttp
    async with aiohttp.ClientSession() as session:
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

        print(f"\n[成功] {lang.upper()} - 已保存到 {output_file}")
        return {'lang': lang, 'status': 'success', 'file': str(output_file)}
    else:
        print(f"\n[失败] {lang.upper()} - {report.get('error', 'Unknown error')}")
        return {'lang': lang, 'status': 'failed', 'error': report.get('error')}


async def main():
    import argparse

    parser = argparse.ArgumentParser(description='翻译所有 routing.ts 中定义的语言（修复版）')
    parser.add_argument('--overwrite', action='store_true', help='覆盖已有翻译文件')
    parser.add_argument('--lang', type=str, help='只翻译指定语言（逗号分隔），如: es,pt')
    args = parser.parse_args()

    # 查找项目根目录
    project_root = find_project_root()
    print(f"[项目根目录] {project_root}")

    # 验证项目根目录
    if not (project_root / 'package.json').exists():
        print(f"[错误] 无法找到项目根目录（package.json 不存在）")
        sys.exit(1)

    # 获取语言列表
    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
        print(f"[模式] 手动指定语言: {', '.join(target_langs)}")
    else:
        target_langs = extract_locales_from_routing(project_root)
        if not target_langs:
            print("[错误] 无法获取语言列表")
            sys.exit(1)
        print(f"[模式] 从 routing.ts 读取语言: {', '.join(target_langs)}")

    # 加载配置
    config_file = Path(script_dir) / 'transpage_config.json'
    if not config_file.exists():
        print(f"[错误] 找不到配置文件: {config_file}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化翻译器
    translator = MessagesTranslator(config)
    smart_translator = SmartChunkTranslator(translator, config)

    print(f"\n{'='*70}")
    print(f"[配置] 翻译系统已初始化")
    print(f"  - API: {config.get('api_base_url')}")
    print(f"  - 模型: {config.get('model')}")
    print(f"  - 目标语言数: {len(target_langs)}")
    print(f"  - 覆盖模式: {'是' if args.overwrite else '否'}")
    print(f"{'='*70}\n")

    # 翻译所有语言
    results = []
    for lang in target_langs:
        result = await translate_language(translator, smart_translator, lang, project_root, args.overwrite)
        results.append(result)

    # 统计结果
    success_count = len([r for r in results if r['status'] == 'success'])
    failed_count = len([r for r in results if r['status'] == 'failed'])
    skipped_count = len([r for r in results if r['status'] == 'skipped'])

    print(f"\n{'='*70}")
    print(f"[完成] 翻译任务总结")
    print(f"{'='*70}")
    print(f"  总计:   {len(results)}")
    print(f"  成功:   {success_count}")
    print(f"  失败:   {failed_count}")
    print(f"  跳过:   {skipped_count}")

    if success_count > 0:
        print(f"\n  成功率: {success_count / len(results) * 100:.1f}%")

    # 显示失败详情
    failed_results = [r for r in results if r['status'] == 'failed']
    if failed_results:
        print("\n  失败详情:")
        for result in failed_results:
            print(f"    - {result['lang'].upper()}: {result.get('error', 'Unknown error')}")

    print(f"{'='*70}\n")


if __name__ == '__main__':
    asyncio.run(main())
