#!/usr/bin/env python3
"""
测试脚本: 验证文章生成功能的警告机制
测试场景:
1. 有效的文章 - 应该正常保存
2. 缺少字段的文章 - 应该保存但显示警告
3. 缺少前置内容的文章 - 应该保存但显示警告
"""
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules', 'generation'))

from file_writer import FileWriter

def test_valid_article():
    """测试1: 有效的文章"""
    print("\n" + "=" * 60)
    print("测试 1: 有效的文章")
    print("=" * 60)

    writer = FileWriter("test_output/", "https://test.com")

    valid_content = """---
title: "Valid Test Article"
description: "This is a valid test article with all required fields"
keywords: ["test", "valid", "article"]
canonical: "/test/valid-article/"
date: "2025-12-18"
---

## Introduction
This is a test article with proper formatting.

## Section 2
More content here.

## Section 3
Even more content.
"""

    article_info = {
        'url_path': '/test/valid-article/',
        'title': 'Valid Test Article',
        'keyword': 'valid test',
        'row_number': 1
    }

    result = writer.save_article(valid_content, article_info, overwrite=True, locale='en')
    print(f"\n结果: {'成功' if result else '失败'}")
    writer.print_stats()


def test_missing_field():
    """测试2: 缺少description字段的文章"""
    print("\n" + "=" * 60)
    print("测试 2: 缺少description字段的文章")
    print("=" * 60)

    writer = FileWriter("test_output/", "https://test.com")

    invalid_content = """---
title: "Invalid Test Article"
keywords: ["test", "invalid", "article"]
canonical: "/test/invalid-article/"
date: "2025-12-18"
---

## Introduction
This article is missing the description field.

## Section 2
But it should still be written to disk with a warning.
"""

    article_info = {
        'url_path': '/test/invalid-article/',
        'title': 'Invalid Test Article',
        'keyword': 'invalid test',
        'row_number': 2
    }

    result = writer.save_article(invalid_content, article_info, overwrite=True, locale='en')
    print(f"\n结果: {'文件已写入' if result else '文件未写入'}")
    writer.print_stats()


def test_no_frontmatter():
    """测试3: 完全缺少前置内容的文章"""
    print("\n" + "=" * 60)
    print("测试 3: 完全缺少前置内容的文章")
    print("=" * 60)

    writer = FileWriter("test_output/", "https://test.com")

    no_frontmatter = """
## Introduction
This article has no frontmatter at all.

## Section 2
It should still be saved with a warning.
"""

    article_info = {
        'url_path': '/test/no-frontmatter/',
        'title': 'No Frontmatter Article',
        'keyword': 'no frontmatter',
        'row_number': 3
    }

    result = writer.save_article(no_frontmatter, article_info, overwrite=True, locale='en')
    print(f"\n结果: {'文件已写入' if result else '文件未写入'}")
    writer.print_stats()


def check_failed_log():
    """检查失败日志"""
    print("\n" + "=" * 60)
    print("检查 failed_articles.json")
    print("=" * 60)

    writer = FileWriter("test_output/", "https://test.com")
    failed_articles = writer.get_failed_articles()

    if failed_articles:
        print(f"\n找到 {len(failed_articles)} 个带警告的文章:")
        for article in failed_articles:
            print(f"\n- {article['title']}")
            print(f"  路径: {article['url_path']}")
            print(f"  错误: {article['error']}")
            print(f"  已写入但有警告: {article.get('written_with_warnings', False)}")
    else:
        print("\n没有找到失败或警告的文章记录")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始测试文章生成功能的警告机制")
    print("=" * 60)

    # 清理旧的测试输出
    import shutil
    if os.path.exists("test_output"):
        shutil.rmtree("test_output")

    # 运行测试
    test_valid_article()
    test_missing_field()
    test_no_frontmatter()
    check_failed_log()

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    print("\n请检查 test_output/ 目录确认文件是否正确写入")
    print("请检查 tools/articles/logs/failed_articles.json 确认警告记录")
