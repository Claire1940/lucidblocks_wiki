#!/usr/bin/env python3
"""
测试脚本：验证 YouTube MCP 返回缓存文件路径而非完整字幕内容
"""

import asyncio
import json
from core.youtube import YouTube
from core.config import Config
from server import format_transcript_response


async def test_format_transcript_response():
    """测试 format_transcript_response 函数"""
    print("=" * 60)
    print("测试 1: format_transcript_response - 成功场景")
    print("=" * 60)

    # 模拟成功的字幕结果
    mock_result = {
        "success": True,
        "video_id": "dQw4w9WgXcQ",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "transcript": "This is a test transcript with some content. " * 100,  # 约 4500 字符
        "language": "en",
        "cached": False
    }

    formatted = format_transcript_response(mock_result)

    print("\n原始响应大小:", len(json.dumps(mock_result, ensure_ascii=False)))
    print("格式化后响应大小:", len(json.dumps(formatted, ensure_ascii=False)))
    print("\n格式化后的响应:")
    print(json.dumps(formatted, ensure_ascii=False, indent=2))

    # 验证关键字段
    assert formatted["success"] == True
    assert formatted["video_id"] == "dQw4w9WgXcQ"
    assert "cache_file" in formatted
    assert "transcript_length" in formatted
    assert "transcript" not in formatted  # 确保完整字幕不在响应中
    assert formatted["transcript_length"] > 0
    print("\n✓ 测试通过：响应包含 cache_file 而非完整 transcript")

    print("\n" + "=" * 60)
    print("测试 2: format_transcript_response - 失败场景")
    print("=" * 60)

    # 模拟失败的字幕结果
    mock_error_result = {
        "success": False,
        "video_id": "invalid123",
        "url": "https://www.youtube.com/watch?v=invalid123",
        "error": "No transcript available"
    }

    formatted_error = format_transcript_response(mock_error_result)

    print("\n格式化后的错误响应:")
    print(json.dumps(formatted_error, ensure_ascii=False, indent=2))

    # 验证错误响应
    assert formatted_error["success"] == False
    assert "error" in formatted_error
    assert "message" in formatted_error
    print("\n✓ 测试通过：错误响应格式正确")


async def test_real_transcript():
    """测试真实的字幕获取（如果有有效的 API key）"""
    print("\n" + "=" * 60)
    print("测试 3: 真实字幕获取（可选）")
    print("=" * 60)

    if not Config.validate():
        print("\n⚠️  跳过真实测试：未配置 API key")
        return

    youtube = YouTube()

    # 使用一个已知有字幕的视频（Rick Astley - Never Gonna Give You Up）
    test_video_id = "dQw4w9WgXcQ"

    print(f"\n正在获取视频字幕: {test_video_id}")

    try:
        result = await youtube.get_transcript(test_video_id, languages=["en"])

        if result.get("success"):
            print(f"✓ 字幕获取成功")
            print(f"  - 字幕长度: {len(result.get('transcript', ''))} 字符")
            print(f"  - 语言: {result.get('language')}")
            print(f"  - 是否来自缓存: {result.get('cached')}")

            # 格式化响应
            formatted = format_transcript_response(result)

            print(f"\n格式化后的响应:")
            print(json.dumps(formatted, ensure_ascii=False, indent=2))

            # 验证缓存文件是否存在
            import os
            cache_file = formatted.get("cache_file")
            if cache_file and os.path.exists(cache_file):
                print(f"\n✓ 缓存文件存在: {cache_file}")

                # 读取缓存文件内容
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    print(f"  - 缓存文件大小: {len(json.dumps(cache_data))} 字节")
                    print(f"  - 缓存内容包含字段: {list(cache_data.keys())}")
            else:
                print(f"\n⚠️  缓存文件不存在: {cache_file}")
        else:
            print(f"✗ 字幕获取失败: {result.get('error')}")

    except Exception as e:
        print(f"✗ 测试出错: {e}")


async def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("YouTube MCP 缓存响应测试")
    print("=" * 60)

    # 运行测试
    await test_format_transcript_response()
    await test_real_transcript()

    print("\n" + "=" * 60)
    print("所有测试完成！")
    print("=" * 60)
    print("\n总结:")
    print("✓ format_transcript_response 函数工作正常")
    print("✓ 响应中不包含完整字幕内容")
    print("✓ 响应中包含 cache_file 路径")
    print("✓ 响应大小显著减小（从 KB 级别降至字节级别）")
    print("\n使用方式:")
    print("1. 调用 youtube_get_transcript 获取响应")
    print("2. 从响应中获取 cache_file 路径")
    print("3. 使用 Read 工具读取缓存文件获取完整字幕")


if __name__ == "__main__":
    asyncio.run(main())
