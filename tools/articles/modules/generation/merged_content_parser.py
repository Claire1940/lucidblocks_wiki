"""
Merged Content Parser Module
加载和解析 merged/{keyword}.json 文件
"""
import json
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class MergedContentParser:
    def __init__(self, merged_dir: str):
        """
        初始化 merged 内容解析器

        Args:
            merged_dir: merged 目录路径（如 "../../content_pipeline/out/merged"）
        """
        self.merged_dir = merged_dir

        if not os.path.exists(merged_dir):
            logger.warning(f"Merged directory does not exist: {merged_dir}")

    def load_merged_content(self, keyword: str) -> Optional[Dict]:
        """
        加载指定关键词的 merged 内容

        Args:
            keyword: 关键词（如 "apogea_best_weapons" 或 "apogea best weapons"）

        Returns:
            merged 数据字典，如果文件不存在返回 None
        """
        # 将关键词转换为文件名格式（空格替换为下划线）
        filename = keyword.lower().replace(' ', '_')
        filepath = os.path.join(self.merged_dir, f"{filename}.json")

        if not os.path.exists(filepath):
            logger.warning(f"Merged file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证内容
            if not self.validate_content(data):
                logger.warning(f"Invalid merged content in {filepath}")
                return None

            return data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {filepath}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading merged content from {filepath}: {e}")
            return None

    def validate_content(self, merged_data: Dict) -> bool:
        """
        验证 merged 内容的完整性

        Args:
            merged_data: merged 数据字典

        Returns:
            是否有效（至少有1个来源）
        """
        if not merged_data:
            return False

        # 检查必需字段
        if 'keyword' not in merged_data:
            logger.warning("Missing 'keyword' field in merged data")
            return False

        if 'sources' not in merged_data:
            logger.warning("Missing 'sources' field in merged data")
            return False

        # 检查是否至少有一个来源
        total_sources = merged_data.get('total_sources', 0)
        if total_sources == 0:
            logger.warning(f"No sources found for keyword: {merged_data.get('keyword')}")
            return False

        return True

    def format_for_prompt(self, merged_data: Dict) -> str:
        """
        将 merged 数据格式化为 JSON 字符串供 LLM 使用

        Args:
            merged_data: merged 数据字典

        Returns:
            格式化的 JSON 字符串
        """
        return json.dumps(merged_data, indent=2, ensure_ascii=False)

    def get_source_summary(self, merged_data: Dict) -> Dict:
        """
        获取来源摘要信息

        Args:
            merged_data: merged 数据字典

        Returns:
            摘要字典，包含 youtube_count, web_count, total_sources
        """
        if not merged_data:
            return {
                'youtube_count': 0,
                'web_count': 0,
                'total_sources': 0
            }

        sources = merged_data.get('sources', {})
        youtube_count = sources.get('youtube', {}).get('count', 0)
        web_count = sources.get('web', {}).get('count', 0)

        return {
            'youtube_count': youtube_count,
            'web_count': web_count,
            'total_sources': merged_data.get('total_sources', 0)
        }
