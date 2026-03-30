#!/usr/bin/env python3
"""
Smart Chunk Translator - 智能分块翻译器
解决 token 限制和格式错误问题

特性：
1. 自动按顶层键分块（避免 token 限制）
2. 翻译结果验证（JSON 格式、结构完整性）
3. 专有名词保护（游戏名、角色名）
4. 自动降级重试（大块 → 小块）
5. 详细错误报告
6. 断点续传（保存进度，失败后可恢复）
7. 增强验证（空值、FAQ 结构、专有名词）
"""

import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import hashlib
import os
import sys

# 导入新模块
try:
    from checkpoint_manager import CheckpointManager
    from enhanced_validator import EnhancedTranslationValidator
except ImportError:
    # 如果导入失败，添加当前目录到路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from checkpoint_manager import CheckpointManager
    from enhanced_validator import EnhancedTranslationValidator


@dataclass
class ChunkResult:
    """分块翻译结果"""
    success: bool
    chunk_name: str
    content: Optional[dict] = None
    error: Optional[str] = None
    tokens_estimate: int = 0


class ProtectedTermsManager:
    """专有名词保护管理器"""

    def __init__(self, config: dict):
        self.protected_terms = self._load_protected_terms(config)
        self.placeholder_map = {}

    def _load_protected_terms(self, config: dict) -> List[str]:
        """从配置加载专有名词"""
        terms = []
        protected = config.get('protected_terms', {})

        # 游戏名称
        terms.extend(protected.get('game_names', []))
        # 角色名称
        terms.extend(protected.get('character_names', []))
        # 技术术语
        terms.extend(protected.get('technical_terms', []))

        return terms

    def protect(self, text: str) -> str:
        """将专有名词替换为占位符"""
        protected_text = text
        self.placeholder_map = {}

        for term in self.protected_terms:
            if term in text:
                placeholder = f"__PROTECTED_{hashlib.md5(term.encode()).hexdigest()[:8]}__"
                self.placeholder_map[placeholder] = term
                protected_text = protected_text.replace(term, placeholder)

        return protected_text

    def restore(self, text: str) -> str:
        """还原专有名词"""
        restored_text = text
        for placeholder, term in self.placeholder_map.items():
            restored_text = restored_text.replace(placeholder, term)
        return restored_text


class TranslationValidator:
    """翻译结果验证器"""

    @staticmethod
    def validate_json_format(content: str) -> Tuple[bool, Optional[str]]:
        """验证 JSON 格式"""
        try:
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON 格式错误: {str(e)}"

    @staticmethod
    def validate_structure(original: dict, translated: dict) -> Tuple[bool, Optional[str]]:
        """验证结构完整性"""
        def get_keys_recursive(obj, prefix=''):
            keys = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key_path = f"{prefix}.{k}" if prefix else k
                    keys.append(key_path)
                    keys.extend(get_keys_recursive(v, key_path))
            return keys

        original_keys = set(get_keys_recursive(original))
        translated_keys = set(get_keys_recursive(translated))

        if original_keys != translated_keys:
            missing = original_keys - translated_keys
            extra = translated_keys - original_keys
            error_msg = []
            if missing:
                error_msg.append(f"缺失键: {list(missing)[:5]}")
            if extra:
                error_msg.append(f"多余键: {list(extra)[:5]}")
            return False, "; ".join(error_msg)

        return True, None

    @staticmethod
    def validate_size(original: dict, translated: dict) -> Tuple[bool, Optional[str]]:
        """验证文件大小合理性（±50%）"""
        original_str = json.dumps(original, ensure_ascii=False)
        translated_str = json.dumps(translated, ensure_ascii=False)

        original_size = len(original_str)
        translated_size = len(translated_str)

        ratio = translated_size / original_size

        if ratio < 0.5 or ratio > 1.5:
            return False, f"大小异常: 原始 {original_size} 字符, 翻译后 {translated_size} 字符 (比例 {ratio:.2f})"

        return True, None


class SmartChunkTranslator:
    """智能分块翻译器（支持断点续传和增强验证）"""

    def __init__(self, translator, config: dict):
        self.translator = translator
        self.config = config
        self.protected_terms = ProtectedTermsManager(config)
        self.validator = TranslationValidator()

        # 新增：增强验证器和断点管理器
        self.enhanced_validator = EnhancedTranslationValidator()
        self.checkpoint_manager = CheckpointManager()
        self.protected_terms_list = self.protected_terms.protected_terms

        # 分块配置
        self.chunk_strategies = [
            ('top_level', None),      # 按顶层键分块
            ('medium', 30),           # 30 个键一块
            ('small', 15),            # 15 个键一块
            ('tiny', 5)               # 5 个键一块（最后手段）
        ]

    def split_by_top_level(self, data: dict) -> Dict[str, dict]:
        """按顶层键分块"""
        chunks = {}
        for key, value in data.items():
            chunks[key] = {key: value}
        return chunks

    def split_by_size(self, data: dict, max_keys: int) -> Dict[str, dict]:
        """按键数量分块"""
        chunks = {}
        current_chunk = {}
        chunk_index = 0

        for key, value in data.items():
            current_chunk[key] = value

            if len(current_chunk) >= max_keys:
                chunks[f"chunk_{chunk_index:02d}"] = current_chunk
                current_chunk = {}
                chunk_index += 1

        # 保存最后一块
        if current_chunk:
            chunks[f"chunk_{chunk_index:02d}"] = current_chunk

        return chunks

    async def translate_chunk(
        self,
        chunk_name: str,
        chunk_data: dict,
        target_lang: str,
        session: aiohttp.ClientSession
    ) -> ChunkResult:
        """翻译单个分块"""
        try:
            # 转换为 JSON 字符串
            chunk_json = json.dumps(chunk_data, indent=2, ensure_ascii=False)

            # 保护专有名词
            protected_json = self.protected_terms.protect(chunk_json)

            # 估算 tokens（粗略估计：1 token ≈ 4 字符）
            tokens_estimate = len(protected_json) // 4

            print(f"    [{chunk_name}] 翻译中... ({len(chunk_data)} 个键, 约 {tokens_estimate} tokens)")

            # 调用翻译
            translated_content = await self.translator.translate_to_language(
                protected_json,
                target_lang,
                session
            )

            if not translated_content:
                return ChunkResult(
                    success=False,
                    chunk_name=chunk_name,
                    error="翻译 API 返回空结果",
                    tokens_estimate=tokens_estimate
                )

            # 还原专有名词
            restored_content = self.protected_terms.restore(translated_content)

            # 验证 JSON 格式
            valid, error = self.validator.validate_json_format(restored_content)
            if not valid:
                return ChunkResult(
                    success=False,
                    chunk_name=chunk_name,
                    error=error,
                    tokens_estimate=tokens_estimate
                )

            # 解析 JSON
            translated_data = json.loads(restored_content)

            # 验证结构
            valid, error = self.validator.validate_structure(chunk_data, translated_data)
            if not valid:
                return ChunkResult(
                    success=False,
                    chunk_name=chunk_name,
                    error=error,
                    tokens_estimate=tokens_estimate
                )

            # 新增：立即保存分块结果
            self.checkpoint_manager.save_chunk(target_lang, chunk_name, translated_data)
            print(f"    [{chunk_name}] ✓ 翻译成功并已保存")

            return ChunkResult(
                success=True,
                chunk_name=chunk_name,
                content=translated_data,
                tokens_estimate=tokens_estimate
            )

        except Exception as e:
            return ChunkResult(
                success=False,
                chunk_name=chunk_name,
                error=f"异常: {type(e).__name__}: {str(e)}",
                tokens_estimate=0
            )

    async def translate_with_strategy(
        self,
        data: dict,
        target_lang: str,
        strategy: str,
        chunk_size: Optional[int],
        session: aiohttp.ClientSession
    ) -> Tuple[bool, Optional[dict], List[ChunkResult]]:
        """使用指定策略翻译（支持断点恢复）"""
        print(f"\n  [策略] {strategy} (chunk_size={chunk_size})")

        # 分块
        if strategy == 'top_level':
            chunks = self.split_by_top_level(data)
        else:
            chunks = self.split_by_size(data, chunk_size)

        total_chunks = len(chunks)
        print(f"  [分块] 共 {total_chunks} 个分块")

        # 新增：检查断点
        checkpoint = self.checkpoint_manager.load_checkpoint(target_lang)
        completed_chunks = []
        chunks_to_translate = dict(chunks)

        if checkpoint and checkpoint['strategy'] == strategy:
            completed_chunks = checkpoint['completed_chunks']
            print(f"  [恢复] 已完成 {len(completed_chunks)}/{total_chunks} 个分块，继续翻译剩余部分")

            # 从待翻译列表中移除已完成的分块
            for chunk_name in completed_chunks:
                if chunk_name in chunks_to_translate:
                    del chunks_to_translate[chunk_name]

        # 翻译剩余分块
        if chunks_to_translate:
            print(f"  [翻译] 开始翻译 {len(chunks_to_translate)} 个分块")
            tasks = [
                self.translate_chunk(name, chunk, target_lang, session)
                for name, chunk in chunks_to_translate.items()
            ]

            results = await asyncio.gather(*tasks)
        else:
            print(f"  [跳过] 所有分块已完成，无需翻译")
            results = []

        # 新增：更新检查点
        newly_completed = [r.chunk_name for r in results if r.success]
        all_completed = completed_chunks + newly_completed

        self.checkpoint_manager.save_checkpoint(
            lang=target_lang,
            strategy=strategy,
            completed_chunks=all_completed,
            total_chunks=total_chunks
        )

        # 检查结果
        failed_chunks = [r for r in results if not r.success]

        if failed_chunks:
            print(f"  [失败] {len(failed_chunks)}/{len(results)} 个分块失败")
            for result in failed_chunks:
                print(f"    - {result.chunk_name}: {result.error}")
            return False, None, results

        # 合并结果（包括从检查点恢复的）
        merged_data = self.checkpoint_manager.merge_chunks(target_lang, all_completed)

        # 最终验证
        valid, error = self.validator.validate_structure(data, merged_data)
        if not valid:
            print(f"  [失败] 合并后结构验证失败: {error}")
            return False, None, results

        valid, error = self.validator.validate_size(data, merged_data)
        if not valid:
            print(f"  [警告] {error}")

        print(f"  [成功] 所有分块翻译完成")
        return True, merged_data, results

    async def translate_with_fallback(
        self,
        data: dict,
        target_lang: str,
        session: aiohttp.ClientSession
    ) -> Tuple[bool, Optional[dict], dict]:
        """带降级策略的翻译"""
        print(f"\n[开始] 智能分块翻译 - {target_lang.upper()}")

        report = {
            'lang': target_lang,
            'strategies_tried': [],
            'final_status': 'failed',
            'error': None
        }

        # 尝试所有策略
        for strategy, chunk_size in self.chunk_strategies:
            success, translated_data, results = await self.translate_with_strategy(
                data, target_lang, strategy, chunk_size, session
            )

            report['strategies_tried'].append({
                'strategy': strategy,
                'chunk_size': chunk_size,
                'success': success,
                'chunks_count': len(results),
                'failed_chunks': len([r for r in results if not r.success])
            })

            if success:
                report['final_status'] = 'success'

                # 新增：成功后清理检查点
                self.checkpoint_manager.clear_checkpoint(target_lang)

                # 新增：执行增强验证
                print(f"\n  [验证] 执行增强质量检查...")
                validation_results = self.enhanced_validator.validate_all(
                    original=data,
                    translated=translated_data,
                    protected_terms=self.protected_terms_list
                )

                report['validation'] = validation_results

                if not validation_results['passed']:
                    print(f"  [警告] 翻译质量检查发现问题:")
                    for check_name, check_result in validation_results['checks'].items():
                        if not check_result.get('passed', True):
                            if check_name == 'empty_values':
                                count = check_result.get('count', 0)
                                if count > 0:
                                    print(f"    - {check_name}: 发现 {count} 个空值")
                                    print(f"      {check_result.get('empty_fields', [])[:3]}")
                            elif check_name == 'protected_terms':
                                count = check_result.get('count', 0)
                                if count > 0:
                                    print(f"    - {check_name}: 发现 {count} 个专有名词问题")
                                    print(f"      {check_result.get('violations', [])[:3]}")
                            elif check_name == 'faq_structure':
                                count = check_result.get('count', 0)
                                if count > 0:
                                    print(f"    - {check_name}: 发现 {count} 个 FAQ 结构问题")
                                    print(f"      {check_result.get('errors', [])[:3]}")
                            else:
                                print(f"    - {check_name}: {check_result.get('error', 'unknown')}")
                else:
                    print(f"  [验证] ✓ 所有质量检查通过")

                return True, translated_data, report

            print(f"  [降级] 尝试下一个策略...")

        # 所有策略都失败
        report['error'] = '所有分块策略都失败'
        return False, None, report
