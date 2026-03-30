#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 配置测试脚本

测试 Gemini API 连接和配置是否正常工作
"""

import json
import sys
import time
from pathlib import Path

# 设置 UTF-8 输出编码（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请安装: pip install requests")
    sys.exit(1)


def load_config():
    """加载配置文件"""
    config_file = Path(__file__).parent / "config.json"

    if not config_file.exists():
        print(f"❌ 配置文件不存在: {config_file}")
        sys.exit(1)

    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_api_connection(config):
    """测试 API 连接"""
    print("\n" + "=" * 70)
    print("  测试 API 连接")
    print("=" * 70)

    api_key = config.get("api_key")
    api_base_url = config.get("api_base_url")
    model = config.get("model")

    if not api_key:
        print("❌ API Key 未配置")
        return False

    if not api_base_url:
        print("❌ API Base URL 未配置")
        return False

    print(f"📡 API Base URL: {api_base_url}")
    print(f"🤖 Model: {model}")
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")

    # 构建请求
    url = f"{api_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with 'API test successful' if you can read this."
            }
        ],
        "temperature": config.get("temperature", 0.7),
        "max_tokens": 50
    }

    print("\n🔄 发送测试请求...")

    try:
        start_time = time.time()
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=config.get("timeout", 30)
        )
        elapsed_time = time.time() - start_time

        print(f"⏱️  响应时间: {elapsed_time:.2f}s")
        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # 提取响应内容
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                print(f"\n✅ API 连接成功！")
                print(f"📝 响应内容: {content}")

                # 显示使用情况
                if "usage" in data:
                    usage = data["usage"]
                    print(f"\n📈 Token 使用:")
                    print(f"   - Prompt Tokens: {usage.get('prompt_tokens', 0)}")
                    print(f"   - Completion Tokens: {usage.get('completion_tokens', 0)}")
                    print(f"   - Total Tokens: {usage.get('total_tokens', 0)}")

                return True
            else:
                print(f"❌ 响应格式异常: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return False
        else:
            print(f"❌ API 请求失败")
            print(f"响应内容: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（超过 {config.get('timeout', 30)}s）")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


def test_config_paths(config):
    """测试配置中的路径是否存在"""
    print("\n" + "=" * 70)
    print("  测试配置路径")
    print("=" * 70)

    base_dir = Path(__file__).parent
    all_valid = True

    # 测试关键词文件
    keywords_file = base_dir / config.get("keywords_file", "")
    print(f"\n📋 关键词文件: {keywords_file}")
    if keywords_file.exists():
        print(f"   ✅ 文件存在")
        try:
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
                print(f"   📊 关键词数量: {len(keywords)}")
        except Exception as e:
            print(f"   ⚠️  读取失败: {e}")
            all_valid = False
    else:
        print(f"   ❌ 文件不存在")
        all_valid = False

    # 测试合并目录
    merged_dir = base_dir / config.get("merged_dir", "")
    print(f"\n📁 合并内容目录: {merged_dir}")
    if merged_dir.exists():
        print(f"   ✅ 目录存在")
        json_files = list(merged_dir.glob("*.json"))
        print(f"   📊 JSON 文件数量: {len(json_files)}")
    else:
        print(f"   ⚠️  目录不存在（首次运行时正常）")

    # 测试输出目录
    output_dir = base_dir / config.get("output_dir", "")
    print(f"\n📂 输出目录: {output_dir}")
    if output_dir.exists():
        print(f"   ✅ 目录存在")
    else:
        print(f"   ⚠️  目录不存在（将自动创建）")

    return all_valid


def test_config_values(config):
    """测试配置值是否合理"""
    print("\n" + "=" * 70)
    print("  测试配置参数")
    print("=" * 70)

    all_valid = True

    # 温度参数
    temperature = config.get("temperature", 0.7)
    print(f"\n🌡️  Temperature: {temperature}")
    if 0 <= temperature <= 2:
        print(f"   ✅ 参数合理")
    else:
        print(f"   ⚠️  建议范围: 0-2")
        all_valid = False

    # Max tokens
    max_tokens = config.get("max_tokens", 24576)
    print(f"\n📏 Max Tokens: {max_tokens}")
    if max_tokens > 0:
        print(f"   ✅ 参数合理")
    else:
        print(f"   ❌ 必须大于 0")
        all_valid = False

    # 超时时间
    timeout = config.get("timeout", 900)
    print(f"\n⏱️  Timeout: {timeout}s")
    if timeout > 0:
        print(f"   ✅ 参数合理")
    else:
        print(f"   ❌ 必须大于 0")
        all_valid = False

    # 并发限制
    concurrent_limit = config.get("concurrent_limit", 1000)
    print(f"\n🔀 Concurrent Limit: {concurrent_limit}")
    if concurrent_limit > 0:
        print(f"   ✅ 参数合理")
    else:
        print(f"   ❌ 必须大于 0")
        all_valid = False

    # 重试配置
    retry_attempts = config.get("retry_attempts", 2)
    retry_delay = config.get("retry_delay", 5)
    print(f"\n🔄 Retry Config:")
    print(f"   - Attempts: {retry_attempts}")
    print(f"   - Delay: {retry_delay}s")
    if retry_attempts >= 0 and retry_delay >= 0:
        print(f"   ✅ 参数合理")
    else:
        print(f"   ❌ 必须大于等于 0")
        all_valid = False

    return all_valid


def main():
    """主函数"""
    print("=" * 70)
    print("  Gemini API 配置测试")
    print("=" * 70)

    # 加载配置
    try:
        config = load_config()
        print("✅ 配置文件加载成功")
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        sys.exit(1)

    # 运行测试
    results = {
        "config_values": test_config_values(config),
        "config_paths": test_config_paths(config),
        "api_connection": test_api_connection(config)
    }

    # 总结
    print("\n" + "=" * 70)
    print("  测试总结")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 所有测试通过！API 配置正常，可以开始生成文章。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查配置后重试。")
        sys.exit(1)


if __name__ == "__main__":
    main()
