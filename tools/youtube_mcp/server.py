#!/usr/bin/env python3
"""
YouTube MCP 服务器

提供 YouTube 搜索和字幕获取功能
"""

import asyncio
import json
import sys
import os
from typing import Any

# 设置环境变量强制使用 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

from mcp.server import Server
from mcp.types import Tool, TextContent

from core.config import Config
from core.youtube import YouTube
from core.utils import extract_video_id


# 创建 MCP 服务器实例
app = Server("youtube-mcp")

# 创建 YouTube 实例
youtube = YouTube()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="youtube_search",
            description="搜索 YouTube 视频，返回视频链接和元数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "返回结果数量（默认 5）",
                        "default": 5
                    },
                    "max_duration": {
                        "type": "number",
                        "description": "最大视频时长（秒，默认 3600）",
                        "default": 3600
                    }
                },
                "required": ["keyword"]
            }
        ),
        Tool(
            name="youtube_get_transcript",
            description="获取 YouTube 视频字幕并保存到缓存文件，返回文件路径而非完整内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "YouTube 视频 URL 或 video_id"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "字幕语言优先级（默认 ['zh', 'en']）",
                        "default": ["zh", "en"]
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="youtube_search_and_transcribe",
            description="搜索关键词并获取前 N 个视频的字幕，保存到缓存文件并返回文件路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "num_videos": {
                        "type": "number",
                        "description": "获取字幕的视频数量（默认 2）",
                        "default": 2
                    },
                    "max_duration": {
                        "type": "number",
                        "description": "最大视频时长（秒，默认 3600）",
                        "default": 3600
                    }
                },
                "required": ["keyword"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "youtube_search":
            return await handle_youtube_search(arguments)
        elif name == "youtube_get_transcript":
            return await handle_youtube_get_transcript(arguments)
        elif name == "youtube_search_and_transcribe":
            return await handle_youtube_search_and_transcribe(arguments)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"未知工具: {name}"}, indent=2)
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


def format_transcript_response(transcript_result: dict) -> dict:
    """
    Format transcript result to return cache file path instead of full content

    Args:
        transcript_result: Result from youtube.get_transcript()

    Returns:
        Formatted response with cache file path
    """
    video_id = transcript_result.get("video_id")
    success = transcript_result.get("success", False)

    if success:
        # Get cache file path
        cache_file = f"{Config.CACHE_DIR}/youtube/{video_id}.json"

        # Get transcript length
        transcript = transcript_result.get("transcript", "")
        transcript_length = len(transcript)

        return {
            "success": True,
            "video_id": video_id,
            "url": transcript_result.get("url"),
            "cache_file": cache_file,
            "transcript_length": transcript_length,
            "language": transcript_result.get("language"),
            "cached": transcript_result.get("cached", False),
            "message": f"Transcript saved to {cache_file}. Use Read tool to access content."
        }
    else:
        # Return error response
        return {
            "success": False,
            "video_id": video_id,
            "url": transcript_result.get("url"),
            "error": transcript_result.get("error", "Unknown error"),
            "message": "Transcript not available"
        }


async def handle_youtube_search(args: dict) -> list[TextContent]:
    """处理 YouTube 搜索"""
    keyword = args["keyword"]
    max_results = args.get("max_results", 5)
    max_duration = args.get("max_duration", 3600)

    print(f"\n[SEARCH] 搜索 YouTube: {keyword}")

    # 搜索视频
    videos = await youtube.search(keyword, max_results=max_results, max_duration=max_duration)

    result = {
        "keyword": keyword,
        "count": len(videos),
        "videos": videos
    }

    print(f"[OK] 找到 {len(videos)} 个视频")

    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def handle_youtube_get_transcript(args: dict) -> list[TextContent]:
    """处理 YouTube 字幕获取"""
    url = args["url"]
    languages = args.get("languages", ["zh", "en"])

    print(f"\n[TRANSCRIPT] 获取字幕: {url}")

    # 提取 video_id
    try:
        video_id = extract_video_id(url)
    except ValueError as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)
        )]

    # 获取字幕
    transcript_result = await youtube.get_transcript(video_id, languages=languages)

    # 格式化响应（返回缓存文件路径）
    result = format_transcript_response(transcript_result)

    if result.get("success"):
        cached_info = " (from cache)" if result.get("cached") else ""
        print(f"[OK] 字幕已保存{cached_info}: {result['cache_file']} ({result['transcript_length']} 字符)")
    else:
        print(f"[ERROR] 字幕获取失败: {result.get('error', '未知错误')}")

    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def handle_youtube_search_and_transcribe(args: dict) -> list[TextContent]:
    """处理 YouTube 搜索并获取字幕"""
    keyword = args["keyword"]
    num_videos = args.get("num_videos", 2)
    max_duration = args.get("max_duration", 3600)

    print(f"\n[SEARCH+TRANSCRIPT] 搜索并获取字幕: {keyword}")

    # 搜索并获取字幕
    search_result = await youtube.search_and_transcribe(
        keyword,
        num_videos=num_videos,
        max_duration=max_duration
    )

    # 格式化每个视频的响应（移除完整字幕，添加缓存文件路径）
    formatted_videos = []
    for video in search_result["videos"]:
        video_data = {
            "title": video.get("title"),
            "video_id": video.get("video_id"),
            "url": video.get("url"),
            "channel": video.get("channel"),
            "duration": video.get("duration"),
            "view_count": video.get("view_count"),
            "transcript_available": video.get("transcript_available", False)
        }

        if video.get("transcript_available"):
            cache_file = f"{Config.CACHE_DIR}/youtube/{video['video_id']}.json"
            video_data["cache_file"] = cache_file
            video_data["transcript_length"] = len(video.get("transcript", ""))
            video_data["language"] = video.get("language")

        formatted_videos.append(video_data)

    result = {
        "keyword": keyword,
        "count": len(formatted_videos),
        "videos": formatted_videos,
        "message": "Transcripts saved to cache files. Use Read tool to access content."
    }

    # 统计成功数量
    success_count = sum(1 for v in formatted_videos if v.get("transcript_available"))
    print(f"[OK] 完成: {success_count}/{len(formatted_videos)} 个视频获取到字幕")

    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def main():
    """主函数"""
    # 验证配置
    if not Config.validate():
        print("\n[ERROR] 配置验证失败，请检查 .env 文件")
        sys.exit(1)

    # 打印配置摘要
    Config.print_summary()

    # 运行服务器
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        print("[START] YouTube MCP 服务器已启动")
        print("等待客户端连接...\n")
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
