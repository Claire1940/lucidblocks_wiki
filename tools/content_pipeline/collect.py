#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段1：搜集元数据

并行搜索 YouTube 和 Web，生成 pending_review.json 供用户筛选
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 设置 UTF-8 输出编码（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from core.config import Config
from core.youtube import YouTube
from core.web import Web
from core.utils import load_keywords_from_json, save_json, ensure_dir


def load_existing_results() -> Dict[str, Dict]:
    """
    加载已有的 pending_review.json 结果

    Returns:
        {keyword: {"youtube": {...}, "web": {...}}}
    """
    pending_file = Path(Config.OUT_DIR) / "pending_review.json"

    if not pending_file.exists():
        return {}

    try:
        with open(pending_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 构建关键词 -> 结果的映射
        existing = {}
        for kw_data in data.get('keywords', []):
            keyword = kw_data['keyword']
            existing[keyword] = {
                'youtube': kw_data.get('youtube', {'count': 0, 'items': []}),
                'web': kw_data.get('web', {'count': 0, 'items': []})
            }

        return existing
    except Exception as e:
        print(f"⚠️  加载已有结果失败: {e}")
        return {}


def filter_keywords_for_retry(
    all_keywords: List[str],
    existing_results: Dict[str, Dict]
) -> Tuple[List[str], List[str]]:
    """
    过滤需要重试的关键词（YouTube 和 Web 独立判断）

    Args:
        all_keywords: 所有关键词列表
        existing_results: 已有结果 {keyword: {"youtube": {...}, "web": {...}}}

    Returns:
        (youtube_retry_keywords, web_retry_keywords)

    注意：
        - YouTube 和 Web 的重试列表是独立的
        - 如果某关键词只缺少 Web，只会出现在 web_retry 中
        - 如果某关键词只缺少 YouTube，只会出现在 youtube_retry 中
        - 如果某关键词两者都缺少，会同时出现在两个列表中
    """
    youtube_retry = []
    web_retry = []

    for keyword in all_keywords:
        existing = existing_results.get(keyword, {})

        # 检查 YouTube 是否需要重试（独立判断）
        youtube_data = existing.get('youtube', {})
        if youtube_data.get('count', 0) == 0 or len(youtube_data.get('items', [])) == 0:
            youtube_retry.append(keyword)

        # 检查 Web 是否需要重试（独立判断）
        web_data = existing.get('web', {})
        if web_data.get('count', 0) == 0 or len(web_data.get('items', [])) == 0:
            web_retry.append(keyword)

    return youtube_retry, web_retry


def merge_results(
    all_keywords: List[str],
    existing_results: Dict[str, Dict],
    youtube_new: Dict[str, List],
    web_new: Dict[str, List]
) -> List[Dict]:
    """
    合并新旧结果

    Args:
        all_keywords: 所有关键词
        existing_results: 已有结果
        youtube_new: 新的 YouTube 结果
        web_new: 新的 Web 结果

    Returns:
        合并后的结果列表
    """
    merged = []

    for keyword in all_keywords:
        # 获取已有结果
        existing = existing_results.get(keyword, {})
        existing_youtube = existing.get('youtube', {'count': 0, 'items': []})
        existing_web = existing.get('web', {'count': 0, 'items': []})

        # 获取新结果（如果有）
        new_youtube = youtube_new.get(keyword, [])
        new_web = web_new.get(keyword, [])

        # 决定使用哪个结果
        # 如果有新结果，使用新结果；否则使用已有结果
        final_youtube = {
            'count': len(new_youtube),
            'items': [item.to_dict() for item in new_youtube]
        } if new_youtube else existing_youtube

        final_web = {
            'count': len(new_web),
            'items': [item.to_dict() for item in new_web]
        } if new_web else existing_web

        merged.append({
            'keyword': keyword,
            'youtube': final_youtube,
            'web': final_web
        })

    return merged


async def search_with_retry(
    search_func,
    keywords: List[str],
    source_name: str,
    max_retries: int = None,
    retry_delay: int = None
) -> Dict[str, List]:
    """
    带重试机制的搜索函数

    Args:
        search_func: 搜索函数（yt.search_batch 或 web.search_batch）
        keywords: 需要搜索的关键词列表
        source_name: 数据源名称（"YouTube" 或 "Web"）
        max_retries: 最大重试次数（默认从配置读取）
        retry_delay: 重试间隔秒数（默认从配置读取）

    Returns:
        搜索结果字典 {keyword: [items]}
    """
    if not keywords:
        return {}

    # 从配置读取默认值
    if max_retries is None:
        max_retries = Config.SEARCH_MAX_RETRIES
    if retry_delay is None:
        retry_delay = Config.SEARCH_RETRY_DELAY

    results = {}
    failed_keywords = keywords.copy()

    for attempt in range(1, max_retries + 1):
        if not failed_keywords:
            break

        print(f"\n{source_name} 第 {attempt} 次尝试: {len(failed_keywords)} 个关键词")

        # 搜索当前失败的关键词
        batch_results = await search_func(failed_keywords)

        # 分离成功和失败的关键词
        new_failed = []
        for keyword in failed_keywords:
            items = batch_results.get(keyword, [])
            if items:  # 搜索成功
                results[keyword] = items
                print(f"  ✓ {keyword}: {len(items)} 个结果")
            else:  # 搜索失败
                new_failed.append(keyword)
                if attempt < max_retries:
                    print(f"  ✗ {keyword}: 无结果，将重试")
                else:
                    print(f"  ✗ {keyword}: 无结果，已达最大重试次数")

        failed_keywords = new_failed

        # 如果还有失败的关键词且未达到最大重试次数，等待后重试
        if failed_keywords and attempt < max_retries:
            print(f"  等待 {retry_delay} 秒后重试...")
            await asyncio.sleep(retry_delay)

    # 打印最终统计
    success_count = len(results)
    failed_count = len(failed_keywords)
    print(f"\n{source_name} 搜索完成:")
    print(f"  - 成功: {success_count} 个关键词")
    if failed_count > 0:
        print(f"  - 失败: {failed_count} 个关键词（已重试 {max_retries} 次）")

    return results


async def main():
    parser = argparse.ArgumentParser(description="阶段1：搜集元数据")
    parser.add_argument("--json", required=True, help="关键词 JSON 文件路径")
    parser.add_argument("--category", help="筛选特定分类（可选）")
    args = parser.parse_args()

    print("=" * 70)
    print("  阶段1：搜集")
    print("=" * 70)

    # 验证配置
    if not Config.validate():
        print("\n⚠️  配置不完整，但将继续执行")

    # 打印配置摘要
    Config.print_summary()

    # 加载关键词
    keywords = load_keywords_from_json(
        args.json,
        category=args.category,
        ignored_categories=Config.IGNORED_CATEGORIES
    )

    if not keywords:
        print("❌ 没有找到关键词")
        return

    print(f"📋 关键词: {len(keywords)} 个")
    if args.category:
        print(f"📁 分类: {args.category}")

    # 加载已有结果
    existing_results = load_existing_results()

    # 过滤需要重试的关键词
    youtube_retry, web_retry = filter_keywords_for_retry(keywords, existing_results)

    # 打印统计信息
    print(f"\n📊 重试统计:")
    print(f"  - 总关键词: {len(keywords)}")
    print(f"  - YouTube 需要重试: {len(youtube_retry)}")
    print(f"  - Web 需要重试: {len(web_retry)}")
    print(f"  - YouTube 已有结果: {len(keywords) - len(youtube_retry)}")
    print(f"  - Web 已有结果: {len(keywords) - len(web_retry)}")

    # 初始化
    yt = YouTube()
    web = Web()

    # 并行搜索（只搜索需要重试的）
    yt_results = {}
    web_results = {}

    if youtube_retry or web_retry:
        print("\n" + "=" * 70)
        print("  开始搜索（带自动重试）")
        print("=" * 70)

        # YouTube 和 Web 独立搜索，每个都有重试机制
        yt_results, web_results = await asyncio.gather(
            search_with_retry(yt.search_batch, youtube_retry, "YouTube"),
            search_with_retry(web.search_batch, web_retry, "Web")
        )
    else:
        print("\n✅ 所有关键词都已有结果，跳过搜索")

    # 合并新旧结果
    keyword_data = merge_results(keywords, existing_results, yt_results, web_results)

    # 保存结果
    pending = {
        "version": "2.0",
        "created_at": datetime.now().isoformat(),
        "keywords": keyword_data
    }

    output_file = f"{Config.OUT_DIR}/pending_review.json"
    ensure_dir(Config.OUT_DIR)
    save_json(pending, output_file)

    # 统计
    total_yt = sum(kw['youtube']['count'] for kw in keyword_data)
    total_web = sum(kw['web']['count'] for kw in keyword_data)

    print("\n" + "=" * 70)
    print("  ✅ 搜集完成")
    print("=" * 70)
    print(f"YouTube: {total_yt} 个视频")
    print(f"Web: {total_web} 个页面")
    print(f"输出: {output_file}")
    print("\n下一步:")
    print("  1. 编辑 pending_review.json")
    print("  2. 设置 'selected': false 排除不需要的条目")
    print("  3. 运行: python3 extract.py")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
