#!/usr/bin/env python3
"""
translate-messages.py - 顺序翻译脚本

与 translate-messages-enhanced.py 的唯一区别：
多语言时按语言依次翻译，而不是 asyncio.gather 并发。
避免并发请求过多导致 API 超时/rate limit。

使用方法：
    # 翻译所有配置语言（从 transpage_config.json 读取 languages 字段）
    python3 translate-messages.py --overwrite

    # 翻译指定语言
    python3 translate-messages.py --lang ja,es --overwrite

    # 增量翻译（只翻译新增/修改内容）
    python3 translate-messages.py --incremental
"""

import asyncio
import importlib.util
import json
import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# 动态导入 translate-messages-enhanced.py（文件名含连字符，不能直接 import）
script_dir = os.path.dirname(os.path.abspath(__file__))

# enhanced 脚本内部用 `from translator import ...`，需要把 transpage 目录加入 sys.path
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

enhanced_path = os.path.join(script_dir, 'translate-messages-enhanced.py')
spec = importlib.util.spec_from_file_location('translate_messages_enhanced', enhanced_path)
enhanced_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_module)

EnhancedTranslationManager = enhanced_module.EnhancedTranslationManager


class SequentialTranslationManager(EnhancedTranslationManager):
    """顺序翻译管理器 - 按语言依次翻译，不并发"""

    async def translate_all(
        self,
        target_langs: List[str],
        overwrite: bool = False,
        incremental: bool = False,
        strategy: Optional[str] = None,
        generate_report: bool = False
    ):
        print("\n" + "=" * 70)
        print("[启动] 顺序翻译系统（按语言依次执行）")
        print("=" * 70)
        print(f"目标语言: {', '.join(target_langs)}")
        print(f"模式: {'增量翻译' if incremental else '完整翻译'}")
        print(f"覆盖: {'是' if overwrite else '否'}")
        if strategy:
            print(f"策略: {strategy}")
        print("=" * 70 + "\n")

        results = []

        # 关键改动：顺序执行，不使用 asyncio.gather
        for i, lang in enumerate(target_langs):
            print(f"[进度] {i + 1}/{len(target_langs)} - 翻译 {lang.upper()}")
            result = await self.translate_language(lang, overwrite, incremental, strategy, generate_report)
            results.append(result)
            print()

        # 统计
        stats = {
            'total': len(results),
            'success': len([r for r in results if r.get('status') == 'success']),
            'failed': len([r for r in results if r.get('status') == 'failed']),
            'skipped': len([r for r in results if r.get('status') == 'skipped'])
        }

        print("\n" + "=" * 70)
        print("[完成] 翻译任务总结")
        print("=" * 70)
        print(f"总计:   {stats['total']}")
        print(f"成功:   {stats['success']}")
        print(f"失败:   {stats['failed']}")
        print(f"跳过:   {stats['skipped']}")
        if stats['success'] > 0:
            print(f"成功率: {stats['success'] / stats['total'] * 100:.1f}%")

        failed_results = [r for r in results if r.get('status') == 'failed']
        if failed_results:
            print("\n失败详情:")
            for r in failed_results:
                print(f"  - {r['lang'].upper()}: {r.get('error', '未知错误')}")

        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='顺序翻译脚本 - 多语言按顺序依次翻译（不并发）')
    parser.add_argument('--lang', type=str, default=None,
                        help='目标语言（逗号分隔，如: ja,es,pt）；不传则读取 transpage_config.json 的 languages 字段')
    parser.add_argument('--overwrite', action='store_true', help='覆盖已有翻译文件')
    parser.add_argument('--incremental', action='store_true', help='增量翻译（只翻译新增/修改内容）')
    parser.add_argument('--strategy', type=str,
                        choices=['top_level', 'medium', 'small', 'tiny'], default=None,
                        help='分块策略（默认自动降级）')
    parser.add_argument('--report', action='store_true', help='生成详细翻译报告')
    args = parser.parse_args()

    manager = SequentialTranslationManager()

    if not manager.load_config():
        sys.exit(1)

    if not manager.initialize():
        sys.exit(1)

    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
    else:
        target_langs = manager.config.get('languages', [])

    if not target_langs:
        print("[FAIL] 没有目标语言，请通过 --lang 参数或 transpage_config.json 的 languages 字段配置")
        sys.exit(1)

    asyncio.run(manager.translate_all(
        target_langs=target_langs,
        overwrite=args.overwrite,
        incremental=args.incremental,
        strategy=args.strategy,
        generate_report=args.report
    ))


if __name__ == '__main__':
    main()
