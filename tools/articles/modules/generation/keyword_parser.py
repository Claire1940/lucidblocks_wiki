"""
Keyword Parser Module
解析 keywords.json，生成文章元数据列表
"""
import json
import os
import re
from typing import List, Dict, Optional


class KeywordParser:
    def __init__(self, keywords_file: str):
        """
        初始化关键词解析器

        Args:
            keywords_file: keywords.json 文件路径
        """
        self.keywords_file = keywords_file
        self.categories_data = self._load_keywords()

    def _load_keywords(self) -> List[Dict]:
        """
        加载 keywords.json 文件

        Returns:
            分类列表
        """
        if not os.path.exists(self.keywords_file):
            raise FileNotFoundError(f"Keywords file not found: {self.keywords_file}")

        with open(self.keywords_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('categories', [])

    def get_keywords_by_category(self, category: str = None) -> List[Dict]:
        """
        获取关键词列表，可选按分类过滤

        Args:
            category: 分类名称（可选）。如果为 None，返回所有关键词

        Returns:
            关键词元数据列表，每个元素包含：
            - keyword: 关键词
            - category: 分类
            - merged_data_path: merged 文件路径
        """
        keywords = []

        for cat_data in self.categories_data:
            cat_name = cat_data.get('category', '')

            # 如果指定了分类，只处理该分类
            if category and cat_name != category:
                continue

            for keyword in cat_data.get('keywords', []):
                keywords.append({
                    'keyword': keyword,
                    'category': cat_name,
                    'merged_data_path': self._get_merged_path(keyword)
                })

        return keywords

    def _get_merged_path(self, keyword: str) -> str:
        """
        根据关键词生成 merged 文件路径

        Args:
            keyword: 关键词（如 "apogea best weapons"）

        Returns:
            merged 文件路径（如 "out/merged/apogea_best_weapons.json"）
        """
        filename = self.keyword_to_filename(keyword)
        return f"out/merged/{filename}.json"

    @staticmethod
    def keyword_to_filename(keyword: str) -> str:
        """
        将关键词转换为文件名格式

        Args:
            keyword: 关键词（如 "apogea best weapons"）

        Returns:
            文件名（如 "apogea_best_weapons"）
        """
        # 转换为小写，空格替换为下划线
        filename = keyword.lower().replace(' ', '_')

        # 移除特殊字符，只保留字母、数字、下划线
        filename = re.sub(r'[^a-z0-9_]', '', filename)

        return filename

    def get_all_categories(self) -> List[str]:
        """
        获取所有分类名称

        Returns:
            分类名称列表
        """
        return [cat.get('category', '') for cat in self.categories_data]

    def get_keyword_count(self, category: str = None) -> int:
        """
        获取关键词数量

        Args:
            category: 分类名称（可选）

        Returns:
            关键词数量
        """
        return len(self.get_keywords_by_category(category))
