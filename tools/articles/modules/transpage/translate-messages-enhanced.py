#!/usr/bin/env python3
"""
Enhanced Messages Translation Script - 增强版翻译脚本
解决 token 限制、格式错误、字段错位等问题

新特性：
1. 智能分块翻译（自动避免 token 限制）
2. 翻译结果验证（JSON 格式、结构完整性）
3. 专有名词保护（游戏名、角色名自动保持不变）
4. 自动降级重试（大块失败自动尝试小块）
5. 详细错误报告（保存诊断信息）
6. 增量翻译支持（只翻译变化的部分）

使用方法：
    # 基础用法（智能分块模式）
    python3 translate-messages-enhanced.py --lang vi,th

    # 强制覆盖已有翻译
    python3 translate-messages-enhanced.py --lang vi --overwrite

    # 增量翻译（只翻译新增/修改的内容）
    python3 translate-messages-enhanced.py --lang vi --incremental

    # 指定分块策略
    python3 translate-messages-enhanced.py --lang vi --strategy medium

    # 生成详细报告
    python3 translate-messages-enhanced.py --lang vi --report
"""

import asyncio
import json
import os
import sys
import argparse
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Import modules
from translator import MessagesTranslator
from smart_chunk_translator import SmartChunkTranslator


class EnhancedTranslationManager:
    """增强版翻译管理器"""

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config()
        self.config = None
        self.translator = None
        self.smart_tlator = None
        self.messages_dir = Path('src/locales/')
        self.reports_dir = Path('temp/translation-reports/')

    def _find_config(self) -> str:
        """查找配置文件"""
        transpage_config = os.path.join(script_dir, 'transpage_config.json')
        if os.path.exists(transpage_config):
            return transpage_config

        modules_dir = os.path.dirname(script_dir)
        translate_config = os.path.join(modules_dir, 'translate', 'translate_config.json')
        return translate_config

    def load_config(self) -> bool:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            # 添加默认的专有名词保护配置
            if 'protected_terms' not in self.config:
                self.config['protected_terms'] = {
                    'game_names': list(self.config.get('game_names', {}).values()),
                    'character_names': [],
                    'technical_terms': ['PvP', 'PvE', 'HP', 'XP', 'DPS', 'NPC', 'UI', 'API']
                }

            print(f"[OK] 配置已加载: {self.config_path}")
            return True
        except Exception as e:
            print(f"[FAIL] 配置加载失败: {str(e)}")
            return False

    def initialize(self) -> bool:
        """初始化翻译器"""
        try:
            self.translator = MessagesTranslator(self.config)
            self.smart_translator = SmartChunkTranslator(self.translator, self.config)
            self.reports_dir.mkdir(parents=True, exist_ok=True)
            print("[OK] 翻译器初始化完成")
            return True
        except Exception as e:
            print(f"[FAIL] 翻译器初始化失败: {str(e)}")
            return False

    def read_json_file(self, file_path: Path) -> Optional[dict]:
        """读取 JSON 文件"""
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 读取文件失败 {file_path}: {str(e)}")
            return None

    def get_translation_diff(self, old_en: dict, new_en: dict, existing_translation: dict) -> Optional[dict]:
        """计算需要翻译的差异部分"""
        def get_all_paths(obj, prefix=''):
            """获取所有键路径和值"""
            paths = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key_path = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, dict):
                        paths.update(get_all_paths(v, key_path))
                    else:
                        paths[key_path] = v
            return paths

        old_paths = get_all_paths(old_en) if old_en else {}
        new_paths = get_all_paths(new_en)

        # 找出新增或修改的键
        changed_keys = []
        for key, value in new_paths.items():
            if key not in old_paths or old_paths[key] != value:
                changed_keys.append(key)

        if not changed_keys:
            return None

        # 提取需要翻译的部分（按顶层键分组）
        to_translate = {}
        for key in changed_keys:
            top_key = key.split('.')[0]
            if top_key not in to_translate:
                to_translate[top_key] = new_en[top_key]

        return to_translate

    def merge_translations(self, base: dict, updates: dict) -> dict:
        """合并翻译结果"""
        def deep_merge(target, source):
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value

        result = base.copy()
        deep_merge(result, updates)
        return result

    async def translate_language(
        self,
        target_lang: str,
        overwrite: bool = False,
        incremental: bool = False,
        strategy: Optional[str] = None,
        generate_report: bool = False
    ) -> dict:
        """翻译单个语言"""
        output_path = self.messages_dir / f'{target_lang}.json'

        # 读取英文源文件
        en_file = self.messages_dir / 'en.json'
        en_data = self.read_json_file(en_file)

        if not en_data:
            return {
                'lang': target_lang,
                'status': 'failed',
                'error': 'English source file not found or invalid'
            }

        # 检查是否需要翻译
        if output_path.exists() and not overwrite and not incremental:
            return {
                'lang': target_lang,
                'status': 'skipped',
                'reason': 'File already exists (use --overwrite or --incremental)'
            }

        # 增量翻译模式
        to_translate = en_data
        existing_translation = None

        if incremental and output_path.exists():
            existing_translation = self.read_json_file(output_path)
            if existing_translation:
                # 读取旧的 en.json（如果有备份）
                old_en_backup = self.messages_dir / 'en.json.backup'
                old_en = self.read_json_file(old_en_backup) if old_en_backup.exists() else None

                # 计算差异
                diff = self.get_translation_diff(old_en, en_data, existing_translation)

                if not diff:
                    return {
                        'lang': target_lang,
                        'status': 'skipped',
                        'reason': 'No changes detected'
                    }

                to_translate = diff
                print(f"[增量] {target_lang.upper()} - 只翻译 {len(diff)} 个顶层键")

        # 使用智能分块翻译
        async with aiohttp.ClientSession() as session:
            # 如果指定了策略，只使用该策略
            if strategy:
                strategies = [(strategy, self._get_chunk_size(strategy))]
                self.smart_translator.chunk_strategies = strategies

            success, translated_data, report = await self.smart_translator.translate_with_fallback(
                to_translate,
                target_lang,
                session
            )

            # 增量模式：合并翻译结果
            if incremental and existing_translation:
                translated_data = self.merge_translations(existing_translation, translated_data)

            # 保存结果
            if success:
                try:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(translated_data, f, indent=2, ensure_ascii=False)

                    report['status'] = 'success'
                    report['output_file'] = str(output_path)
                    print(f"[OK] {target_lang.upper()} - 翻译完成并保存")

                except Exception as e:
                    report['status'] = 'failed'
                    report['error'] = f"保存文件失败: {str(e)}"
                    print(f"[FAIL] {target_lang.upper()} - 保存失败: {str(e)}")

            # 生成详细报告
            if generate_report:
                self._save_report(target_lang, report)

            return report

    def _get_chunk_size(self, strategy: str) -> Optional[int]:
        """获取策略对应的分块大小"""
        strategy_map = {
            'top_level': None,
            'medium': 30,
            'small': 15,
            'tiny': 5
        }
        return strategy_map.get(strategy)

    def _save_report(self, lang: str, report: dict):
        """保存翻译报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'{lang}_{timestamp}.json'

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"[报告] 已保存到 {report_file}")
        except Exception as e:
            print(f"[WARN] 报告保存失败: {str(e)}")

    async def translate_all(
        self,
        target_langs: List[str],
        overwrite: bool = False,
        incremental: bool = False,
        strategy: Optional[str] = None,
        generate_report: bool = False
    ):
        """翻译所有语言"""
        print("\n" + "=" * 70)
        print("[启动] 增强版翻译系统")
        print("=" * 70)
        print(f"目标语言: {', '.join(target_langs)}")
        print(f"模式: {'增量翻译' if incremental else '完整翻译'}")
        print(f"覆盖: {'是' if overwrite else '否'}")
        if strategy:
            print(f"策略: {strategy}")
        print("=" * 70 + "\n")

        # 并行翻译所有语言
        tasks = [
            self.translate_language(lang, overwrite, incremental, strategy, generate_report)
            for lang in target_langs
        ]

        results = await asyncio.gather(*tasks)

        # 统计结果
        stats = {
            'total': len(results),
            'success': len([r for r in results if r.get('status') == 'success']),
            'failed': len([r for r in results if r.get('status') == 'failed']),
            'skipped': len([r for r in results if r.get('status') == 'skipped'])
        }

        # 打印总结
        print("\n" + "=" * 70)
        print("[完成] 翻译任务总结")
        print("=" * 70)
        print(f"总计:   {stats['total']}")
        print(f"成功:   {stats['success']}")
        print(f"失败:   {stats['failed']}")
        print(f"跳过:   {stats['skipped']}")

        if stats['success'] > 0:
            print(f"\n成功率: {stats['success'] / stats['total'] * 100:.1f}%")

        # 显示失败详情
        failed_results = [r for r in results if r.get('status') == 'failed']
        if failed_results:
            print("\n失败详情:")
            for result in failed_results:
                print(f"  - {result['lang'].upper()}: {result.get('error', 'Unknown error')}")

        print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Enhanced translation script with smart chunking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础翻译
  python3 translate-messages-enhanced.py --lang vi,th

  # 强制覆盖
  python3 translate-messages-enhanced.py --lang vi --overwrite

  # 增量翻译（只翻译变化部分）
  python3 translate-messages-enhanced.py --lang vi --incremental

  # 指定分块策略
  python3 translate-messages-enhanced.py --lang vi --strategy medium

  # 生成详细报告
  python3 translate-messages-enhanced.py --lang vi --report
        """
    )

    parser.add_argument(
        '--lang',
        type=str,
        default=None,
        help='目标语言（逗号分隔，如: vi,th,es）'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖已有翻译文件'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='增量翻译模式（只翻译新增/修改的内容）'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['top_level', 'medium', 'small', 'tiny'],
        default=None,
        help='分块策略（默认自动降级）'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='生成详细翻译报告'
    )

    args = parser.parse_args()

    # 初始化管理器
    manager = EnhancedTranslationManager()

    if not manager.load_config():
        sys.exit(1)

    if not manager.initialize():
        sys.exit(1)

    # 确定目标语言
    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
    else:
        target_langs = manager.config.get('languages', ['vi', 'th', 'es', 'pt', 'ru'])

    # 运行翻译
    asyncio.run(manager.translate_all(
        target_langs=target_langs,
        overwrite=args.overwrite,
        incremental=args.incremental,
        strategy=args.strategy,
        generate_report=args.report
    ))


if __name__ == '__main__':
    main()
