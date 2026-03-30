#!/usr/bin/env python3
"""
测试 YouTube MCP 服务器的 MCP 接口
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """测试 MCP 服务器"""

    # 创建服务器参数
    server_params = StdioServerParameters(
        command="python3",
        args=["server.py"],
        env=None
    )

    print("🚀 连接到 YouTube MCP 服务器...")
    print("=" * 70)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化
            await session.initialize()
            print("✅ 连接成功！\n")

            # 测试 1: 列出可用工具
            print("📋 测试 1: 列出可用工具")
            print("-" * 70)
            tools = await session.list_tools()
            print(f"找到 {len(tools.tools)} 个工具:\n")
            for tool in tools.tools:
                print(f"  • {tool.name}")
                print(f"    {tool.description}")
                print()

            # 测试 2: YouTube 搜索
            print("\n🔍 测试 2: YouTube 搜索")
            print("-" * 70)
            print("搜索关键词: Python tutorial\n")

            result = await session.call_tool(
                "youtube_search",
                arguments={
                    "keyword": "Python tutorial",
                    "max_results": 2,
                    "max_duration": 3600
                }
            )

            # 解析结果
            if result.content:
                data = json.loads(result.content[0].text)
                print(f"✅ 找到 {data['count']} 个视频:\n")
                for i, video in enumerate(data['videos'], 1):
                    print(f"{i}. {video['title']}")
                    print(f"   URL: {video['url']}")
                    print(f"   时长: {video['duration']}")
                    print(f"   观看: {video['view_count']:,}")
                    print()

                # 保存第一个视频的 URL 用于测试 3
                first_video_url = data['videos'][0]['url'] if data['videos'] else None

            # 测试 3: 获取字幕
            if first_video_url:
                print("\n📥 测试 3: 获取字幕")
                print("-" * 70)
                print(f"视频 URL: {first_video_url}\n")

                result = await session.call_tool(
                    "youtube_get_transcript",
                    arguments={
                        "url": first_video_url,
                        "languages": ["en"]
                    }
                )

                if result.content:
                    data = json.loads(result.content[0].text)
                    if data['success']:
                        print(f"✅ 字幕获取成功")
                        print(f"   语言: {data['language']}")
                        print(f"   长度: {len(data['transcript'])} 字符")
                        print(f"   缓存: {'是' if data.get('cached') else '否'}")
                        print(f"   重试: {data.get('retries', 0)} 次")
                        print(f"\n   前 200 字符:")
                        print(f"   {data['transcript'][:200]}...")
                    else:
                        print(f"❌ 字幕获取失败: {data.get('error')}")
                    print()

            # 测试 4: 搜索并获取字幕
            print("\n🎯 测试 4: 搜索并获取字幕（组合功能）")
            print("-" * 70)
            print("搜索关键词: Python basics\n")

            result = await session.call_tool(
                "youtube_search_and_transcribe",
                arguments={
                    "keyword": "Python basics",
                    "num_videos": 2,
                    "max_duration": 3600
                }
            )

            if result.content:
                data = json.loads(result.content[0].text)
                print(f"✅ 找到 {data['count']} 个视频:\n")
                for i, video in enumerate(data['videos'], 1):
                    print(f"{i}. {video['title']}")
                    print(f"   URL: {video['url']}")
                    print(f"   时长: {video['duration']}")
                    if video.get('transcript_available'):
                        print(f"   ✓ 字幕可用 ({len(video['transcript'])} 字符)")
                    else:
                        print(f"   ✗ 字幕不可用")
                    print()

            print("=" * 70)
            print("✅ 所有测试完成！")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
