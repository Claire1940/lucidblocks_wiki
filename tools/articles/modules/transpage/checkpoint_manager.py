#!/usr/bin/env python3
"""
Checkpoint Manager - 断点续传管理器
保存和恢复翻译进度
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime


class CheckpointManager:
    """管理翻译进度的保存和恢复"""

    def __init__(self, checkpoint_dir: str = "temp/checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir = Path("temp/chunks")
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

    def get_checkpoint_path(self, lang: str) -> Path:
        """获取检查点文件路径"""
        return self.checkpoint_dir / f"{lang}_checkpoint.json"

    def get_chunk_path(self, lang: str, chunk_name: str) -> Path:
        """获取分块文件路径"""
        return self.chunks_dir / f"{lang}_{chunk_name}.json"

    def save_checkpoint(self, lang: str, strategy: str, completed_chunks: List[str],
                       total_chunks: int, metadata: dict = None):
        """
        保存检查点

        Args:
            lang: 目标语言
            strategy: 当前策略
            completed_chunks: 已完成的分块名称列表
            total_chunks: 总分块数
            metadata: 额外的元数据
        """
        checkpoint = {
            'lang': lang,
            'strategy': strategy,
            'completed_chunks': completed_chunks,
            'total_chunks': total_chunks,
            'progress': f"{len(completed_chunks)}/{total_chunks}",
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        checkpoint_path = self.get_checkpoint_path(lang)
        with open(checkpoint_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

        print(f"  [保存] 检查点已保存: {len(completed_chunks)}/{total_chunks} 分块完成")

    def load_checkpoint(self, lang: str) -> Optional[dict]:
        """
        加载检查点

        Args:
            lang: 目标语言

        Returns:
            检查点数据，如果不存在返回 None
        """
        checkpoint_path = self.get_checkpoint_path(lang)
        if not checkpoint_path.exists():
            return None

        try:
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)

            print(f"  [恢复] 找到检查点: {checkpoint['progress']} ({checkpoint['timestamp']})")
            return checkpoint
        except Exception as e:
            print(f"  [警告] 检查点加载失败: {str(e)}")
            return None

    def save_chunk(self, lang: str, chunk_name: str, chunk_data: dict):
        """
        保存单个分块的翻译结果

        Args:
            lang: 目标语言
            chunk_name: 分块名称
            chunk_data: 分块数据
        """
        chunk_path = self.get_chunk_path(lang, chunk_name)
        with open(chunk_path, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)

    def load_chunk(self, lang: str, chunk_name: str) -> Optional[dict]:
        """
        加载单个分块的翻译结果

        Args:
            lang: 目标语言
            chunk_name: 分块名称

        Returns:
            分块数据，如果不存在返回 None
        """
        chunk_path = self.get_chunk_path(lang, chunk_name)
        if not chunk_path.exists():
            return None

        try:
            with open(chunk_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  [警告] 分块 {chunk_name} 加载失败: {str(e)}")
            return None

    def merge_chunks(self, lang: str, chunk_names: List[str]) -> dict:
        """
        合并所有分块

        Args:
            lang: 目标语言
            chunk_names: 分块名称列表

        Returns:
            合并后的完整数据
        """
        merged = {}

        for chunk_name in chunk_names:
            chunk_data = self.load_chunk(lang, chunk_name)
            if chunk_data:
                merged.update(chunk_data)
            else:
                print(f"  [警告] 分块 {chunk_name} 不存在，跳过")

        return merged

    def clear_checkpoint(self, lang: str):
        """
        清除检查点和所有分块文件

        Args:
            lang: 目标语言
        """
        # 删除检查点文件
        checkpoint_path = self.get_checkpoint_path(lang)
        if checkpoint_path.exists():
            checkpoint_path.unlink()

        # 删除所有分块文件
        for chunk_file in self.chunks_dir.glob(f"{lang}_*.json"):
            chunk_file.unlink()

        print(f"  [清理] 已清除 {lang} 的检查点和分块文件")

    def list_checkpoints(self) -> List[dict]:
        """
        列出所有检查点

        Returns:
            检查点信息列表
        """
        checkpoints = []

        for checkpoint_file in self.checkpoint_dir.glob("*_checkpoint.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    checkpoints.append(checkpoint)
            except Exception as e:
                print(f"  [警告] 读取检查点失败 {checkpoint_file}: {str(e)}")

        return checkpoints


def test_checkpoint_manager():
    """测试检查点管理器"""
    print("=== 测试 CheckpointManager ===\n")

    manager = CheckpointManager()

    # 测试保存检查点
    print("1. 保存检查点")
    manager.save_checkpoint(
        lang='pt',
        strategy='top_level',
        completed_chunks=['seo', 'nav', 'hero'],
        total_chunks=10,
        metadata={'test': True}
    )
    print()

    # 测试保存分块
    print("2. 保存分块数据")
    manager.save_chunk('pt', 'seo', {'seo': {'home': {'title': 'Teste'}}})
    manager.save_chunk('pt', 'nav', {'nav': {}})
    print("  分块已保存")
    print()

    # 测试加载检查点
    print("3. 加载检查点")
    checkpoint = manager.load_checkpoint('pt')
    if checkpoint:
        print(f"  语言: {checkpoint['lang']}")
        print(f"  策略: {checkpoint['strategy']}")
        print(f"  进度: {checkpoint['progress']}")
        print(f"  已完成: {checkpoint['completed_chunks']}")
    print()

    # 测试合并分块
    print("4. 合并分块")
    merged = manager.merge_chunks('pt', ['seo', 'nav'])
    print(f"  合并结果: {json.dumps(merged, ensure_ascii=False, indent=2)}")
    print()

    # 测试列出检查点
    print("5. 列出所有检查点")
    checkpoints = manager.list_checkpoints()
    for cp in checkpoints:
        print(f"  - {cp['lang']}: {cp['progress']} ({cp['timestamp']})")
    print()

    # 测试清理
    print("6. 清理检查点")
    manager.clear_checkpoint('pt')
    print()


if __name__ == "__main__":
    test_checkpoint_manager()
