#!/usr/bin/env python3
"""
使用示例：演示如何使用修改后的 YouTube MCP 服务

展示如何：
1. 获取字幕并接收缓存文件路径
2. 读取缓存文件获取完整字幕内容
3. 处理多个视频的字幕
"""

import json
import asyncio
from core.youtube import YouTube
from server import format_transcript_response


async def example_1_single_video():
    """示例 1: 获取单个视频字幕"""
    print("=" * 60)
    print("示例 1: 获取单个视频字幕")
    print("=" * 60)

    youtube = YouTube()
    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up

    print(f"\n步骤 1: 调用 youtube.get_transcript()")
    print(f"视频 ID: {video_id}")

    # 获取字幕（内部已经缓存）
    result = await youtube.get_transcript(video_id, languages=["en"])

    print(f"\n步骤 2: 格式化响应（移除完整字幕）")
    formatted_response = format_transcript_response(result)

    print(f"\nAPI 响应（发送给 Claude）:")
    print(json.dumps(formatted_response, ensure_ascii=False, indent=2))

    print(f"\n步骤 3: Claude 使用 Read 工具读取缓存文件")
    cache_file = formatted_response.get("cache_file")
    print(f"读取文件: {cache_file}")

    # 模拟 Claude 读取缓存文件
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        print(f"\n缓存文件内容:")
        print(f"  - video_id: {cache_data['video_id']}")
        print(f"  - language: {cache_data['language']}")
        print(f"  - content length: {len(cache_data['content'])} 字符")
        print(f"  - cached_at: {cache_data['cached_at']}")
        print(f"\n  - 字幕前 200 字符:")
        print(f"    {cache_data['content'][:200]}...")

    except FileNotFoundError:
        print(f"⚠️  缓存文件不存在: {cache_file}")


async def example_2_search_and_transcribe():
    """示例 2: 搜索并获取多个视频字幕"""
    print("\n\n" + "=" * 60)
    print("示例 2: 搜索并获取多个视频字幕")
    print("=" * 60)

    youtube = YouTube()
    keyword = "Python tutorial"

    print(f"\n步骤 1: 搜索关键词: {keyword}")

    # 搜索并获取字幕
    result = await youtube.search_and_transcribe(
        keyword,
        num_videos=2,
        max_duration=600  # 10 分钟以内
    )

    print(f"\n步骤 2: 格式化响应（移除完整字幕，添加缓存路径）")

    # 格式化每个视频的响应
    formatted_videos = []
    for video in result["videos"]:
        video_data = {
            "title": video.get("title"),
            "video_id": video.get("video_id"),
            "url": video.get("url"),
            "duration": video.get("duration"),
            "transcript_available": video.get("transcript_available", False)
        }

        if video.get("transcript_available"):
            cache_file = f"cache/youtube/{video['video_id']}.json"
            video_data["cache_file"] = cache_file
            video_data["transcript_length"] = len(video.get("transcript", ""))
            video_data["language"] = video.get("language")

        formatted_videos.append(video_data)

    formatted_response = {
        "keyword": keyword,
        "count": len(formatted_videos),
        "videos": formatted_videos,
        "message": "Transcripts saved to cache files. Use Read tool to access content."
    }

    print(f"\nAPI 响应（发送给 Claude）:")
    print(json.dumps(formatted_response, ensure_ascii=False, indent=2))

    print(f"\n步骤 3: Claude 可以选择性地读取感兴趣的视频字幕")
    for i, video in enumerate(formatted_videos, 1):
        if video.get("transcript_available"):
            print(f"\n视频 {i}: {video['title']}")
            print(f"  - 缓存文件: {video['cache_file']}")
            print(f"  - 字幕长度: {video['transcript_length']} 字符")
            print(f"  - Claude 可以使用: Read(file_path='{video['cache_file']}')")


async def example_3_response_size_comparison():
    """示例 3: 响应大小对比"""
    print("\n\n" + "=" * 60)
    print("示例 3: 响应大小对比")
    print("=" * 60)

    # 模拟一个包含长字幕的响应
    mock_transcript = "This is a sample transcript. " * 200  # 约 5800 字符

    # 旧格式（包含完整字幕）
    old_format = {
        "success": True,
        "video_id": "test123",
        "url": "https://www.youtube.com/watch?v=test123",
        "transcript": mock_transcript,
        "language": "en",
        "cached": False
    }

    # 新格式（只包含路径）
    new_format = {
        "success": True,
        "video_id": "test123",
        "url": "https://www.youtube.com/watch?v=test123",
        "cache_file": "cache/youtube/test123.json",
        "transcript_length": len(mock_transcript),
        "language": "en",
        "cached": False,
        "message": "Transcript saved to cache/youtube/test123.json. Use Read tool to access content."
    }

    old_size = len(json.dumps(old_format, ensure_ascii=False))
    new_size = len(json.dumps(new_format, ensure_ascii=False))
    reduction = (1 - new_size / old_size) * 100

    print(f"\n旧格式响应大小: {old_size:,} 字节")
    print(f"新格式响应大小: {new_size:,} 字节")
    print(f"大小减少: {reduction:.1f}%")

    print(f"\n优势:")
    print(f"  ✅ 避免上下文溢出")
    print(f"  ✅ 更快的响应时间")
    print(f"  ✅ 按需加载字幕内容")
    print(f"  ✅ 更好的可扩展性")


async def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("YouTube MCP 缓存响应使用示例")
    print("=" * 60)

    # 运行示例
    await example_1_single_video()
    await example_2_search_and_transcribe()
    await example_3_response_size_comparison()

    print("\n\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("""
新的工作流程:

1. 调用 MCP 工具（youtube_get_transcript 或 youtube_search_and_transcribe）
   → 返回轻量级响应，包含 cache_file 路径

2. Claude 检查响应中的 cache_file 路径
   → 决定是否需要读取完整字幕

3. 如果需要，使用 Read 工具读取缓存文件
   → 获取完整字幕内容进行分析

优势:
- 响应大小减少 90%+
- 避免上下文窗口溢出
- 支持按需加载
- 缓存可以跨会话复用
    """)


if __name__ == "__main__":
    asyncio.run(main())
