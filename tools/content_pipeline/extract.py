#!/usr/bin/env python3
"""
阶段2：提取内容

从 pending_review.json 读取筛选后的条目，并行提取内容
"""

import asyncio
from datetime import datetime
from collections import defaultdict

from core.config import Config
from core.youtube import YouTube
from core.web import Web
from core.models import YouTubeItem, WebItem
from core.utils import load_json, save_json, ensure_dir


def deduplicate_items(items_by_keyword, item_type="video"):
    """
    对所有关键词的视频/网页进行去重

    Args:
        items_by_keyword: {keyword: [item_dict, ...]}
        item_type: "video" 或 "page"

    Returns:
        - unique_items: 去重后的 item_dict 列表
        - url_to_keywords: URL 到关键词列表的映射 {url: [keyword1, keyword2, ...]}
    """
    url_map = {}  # url -> {item_dict, keywords: []}

    for keyword, items in items_by_keyword.items():
        for item_dict in items:
            url = item_dict.get('url')
            if not url:
                continue

            if url not in url_map:
                url_map[url] = {
                    'item': item_dict,
                    'keywords': []
                }

            # 添加关键词（避免重复）
            if keyword not in url_map[url]['keywords']:
                url_map[url]['keywords'].append(keyword)

    # 构建返回结果
    unique_items = []
    url_to_keywords = {}

    for url, data in url_map.items():
        unique_items.append(data['item'])
        url_to_keywords[url] = data['keywords']

    return unique_items, url_to_keywords


async def main():
    print("=" * 70)
    print("  阶段2：提取")
    print("=" * 70)

    # 加载 pending_review
    input_file = f"{Config.OUT_DIR}/pending_review.json"
    try:
        data = load_json(input_file)
    except FileNotFoundError:
        print(f"❌ 未找到 {input_file}")
        print("请先运行: python3 collect.py --json ../keywords.json")
        return

    # 第一步：收集所有关键词的 selected 条目
    yt_items_by_keyword = {}  # keyword -> [item_dict]
    web_items_by_keyword = {}  # keyword -> [item_dict]

    for kw_data in data["keywords"]:
        keyword = kw_data["keyword"]

        # YouTube - 只选取前 K 个 selected 的视频
        if "youtube" in kw_data and kw_data["youtube"].get("items"):
            selected_yt = [
                item_dict for item_dict in kw_data["youtube"]["items"]
                if item_dict.get("selected", True)
            ]
            yt_items_by_keyword[keyword] = selected_yt[:Config.YOUTUBE_EXTRACT_TOP_K]
        else:
            yt_items_by_keyword[keyword] = []

        # Web - 只选取前 K 个 selected 的页面
        if "web" in kw_data and kw_data["web"].get("items"):
            selected_web = [
                item_dict for item_dict in kw_data["web"]["items"]
                if item_dict.get("selected", True)
            ]
            web_items_by_keyword[keyword] = selected_web[:Config.WEB_EXTRACT_TOP_K]
        else:
            web_items_by_keyword[keyword] = []

    # 第二步：去重
    print("\n📋 去重前统计:")
    total_yt_before = sum(len(items) for items in yt_items_by_keyword.values())
    total_web_before = sum(len(items) for items in web_items_by_keyword.values())
    print(f"  - YouTube: {total_yt_before} 个视频")
    print(f"  - Web: {total_web_before} 个页面")

    unique_yt_dicts, yt_url_to_keywords = deduplicate_items(yt_items_by_keyword, "video")
    unique_web_dicts, web_url_to_keywords = deduplicate_items(web_items_by_keyword, "page")

    print("\n📋 去重后统计:")
    print(f"  - YouTube: {len(unique_yt_dicts)} 个唯一视频 (去除 {total_yt_before - len(unique_yt_dicts)} 个重复)")
    print(f"  - Web: {len(unique_web_dicts)} 个唯一页面 (去除 {total_web_before - len(unique_web_dicts)} 个重复)")

    # 第三步：转换为对象
    yt_items = [YouTubeItem(**item_dict) for item_dict in unique_yt_dicts]
    web_items = [WebItem(**item_dict) for item_dict in unique_web_dicts]

    print(f"\n📋 待提取:")
    print(f"  - YouTube: {len(yt_items)} 个视频")
    print(f"  - Web: {len(web_items)} 个页面")

    if not yt_items and not web_items:
        print("\n⚠️  没有需要提取的内容")
        return

    # 初始化
    yt = YouTube()
    web = Web()

    # 并行提取
    print("\n" + "=" * 70)
    print("  开始提取")
    print("=" * 70)

    yt_results, web_results = await asyncio.gather(
        yt.extract_batch(yt_items),
        web.extract_batch(web_items)
    )

    # 按关键词组织结果（一个 URL 可能对应多个关键词）
    results = defaultdict(lambda: {"youtube": [], "web": []})

    for item, content in yt_results:
        if content:
            url = item.url
            # 获取该 URL 对应的所有关键词
            keywords = yt_url_to_keywords.get(url, [])

            # 将内容添加到所有相关关键词
            for keyword in keywords:
                results[keyword]["youtube"].append({
                    "type": "youtube",
                    "title": item.title,
                    "url": item.url,
                    "content": content
                })

    for item, content in web_results:
        if content:
            url = item.url
            # 获取该 URL 对应的所有关键词
            keywords = web_url_to_keywords.get(url, [])

            # 将内容添加到所有相关关键词
            for keyword in keywords:
                results[keyword]["web"].append({
                    "type": "web",
                    "title": item.title,
                    "url": item.url,
                    "content": content
                })

    # 保存（按关键词）
    print("\n" + "=" * 70)
    print("  保存结果")
    print("=" * 70)

    merged_dir = f"{Config.OUT_DIR}/merged"
    ensure_dir(merged_dir)

    total_saved = 0
    for keyword, data in results.items():
        keyword_file = keyword.replace(" ", "_").replace("/", "_")
        output_file = f"{merged_dir}/{keyword_file}.json"

        # 构建输出（与现有 merged 格式完全一致）
        output = {
            "keyword": keyword,
            "merged_at": datetime.now().isoformat(),  # 使用 merged_at 而不是 extracted_at
            "sources": {
                "youtube": {
                    "count": len(data["youtube"]),
                    "videos": data["youtube"]
                },
                "web": {
                    "count": len(data["web"]),
                    "pages": data["web"]
                }
            },
            "total_sources": len(data["youtube"]) + len(data["web"])
        }

        save_json(output, output_file)
        total_saved += 1
        print(f"  ✓ {keyword_file}.json")

    # 添加提取摘要
    print("\n" + "=" * 70)
    print("  提取摘要")
    print("=" * 70)

    # YouTube 统计
    yt_success = sum(1 for _, content in yt_results if content)
    yt_failed = len(yt_results) - yt_success
    print(f"YouTube:")
    print(f"  - 成功: {yt_success}/{len(yt_results)}")
    print(f"  - 失败: {yt_failed}/{len(yt_results)}")

    if yt_failed > 0:
        print(f"\n失败的 YouTube 视频:")
        for item, content in yt_results:
            if not content:
                print(f"  - {item.video_id}: {item.title}")

    # Web 统计
    web_success = sum(1 for _, content in web_results if content)
    web_failed = len(web_results) - web_success
    print(f"\nWeb:")
    print(f"  - 成功: {web_success}/{len(web_results)}")
    print(f"  - 失败: {web_failed}/{len(web_results)}")

    if web_failed > 0:
        print(f"\n失败的 Web 页面:")
        for item, content in web_results:
            if not content:
                print(f"  - {item.url}: {item.title}")

    print("\n" + "=" * 70)
    print("  ✅ 提取完成")
    print("=" * 70)
    print(f"保存: {total_saved} 个文件")
    print(f"输出目录: {merged_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
