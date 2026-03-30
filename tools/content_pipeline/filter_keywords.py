#!/usr/bin/env python3
"""
筛选 pending_review.json，每个分类只保留前4个关键词
"""

import json
from pathlib import Path

def main():
    # 读取 keywords.json
    keywords_file = Path(__file__).parent.parent / "keywords.json"
    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords_data = json.load(f)

    # 提取每个分类的前4个关键词
    selected_keywords = set()
    for category in keywords_data['categories']:
        # 每个分类取前4个关键词
        for keyword in category['keywords'][:4]:
            selected_keywords.add(keyword)

    print(f"总共选择了 {len(selected_keywords)} 个关键词")
    print(f"关键词列表: {sorted(selected_keywords)}")

    # 读取 pending_review.json
    pending_file = Path(__file__).parent / "out" / "pending_review.json"
    with open(pending_file, 'r', encoding='utf-8') as f:
        pending_data = json.load(f)

    # 筛选关键词
    original_count = len(pending_data['keywords'])
    filtered_keywords = [
        item for item in pending_data['keywords']
        if item['keyword'] in selected_keywords
    ]

    # 更新数据
    pending_data['keywords'] = filtered_keywords

    # 写回文件
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump(pending_data, f, ensure_ascii=False, indent=2)

    print(f"\n筛选完成:")
    print(f"  原始关键词数量: {original_count}")
    print(f"  筛选后数量: {len(filtered_keywords)}")
    print(f"  已更新文件: {pending_file}")

if __name__ == "__main__":
    main()
