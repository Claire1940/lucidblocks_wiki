#!/usr/bin/env python3
"""
Gemini API 连通性测试脚本

测试 Gemini API 的基础连通性、流式响应和非流式响应功能。
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# API 配置
API_BASE_URL = "https://svip.theapi.top"
API_KEY = "sk-b1BiTAg1LgdknGwIsujlTzbb6h4aLSYXspD2dULCz3W5e3gc"
MODEL = "gemini-2.5-flash"
TIMEOUT = 30  # 请求超时时间(秒)


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")

def test_non_stream_response() -> bool:
    """
    测试非流式响应功能

    Returns:
        bool: 测试是否成功
    """
    print_section("测试 3: 非流式响应测试")

    url = f"{API_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "什么是 Universal Tower Defense?"}
        ],
        "stream": False,
        "max_tokens": 12288
    }

    try:
        print(f"📡 发送非流式请求到: {url}")
        print(f"🤖 使用模型: {MODEL}")
        print(f"💬 测试消息: 什么是 Universal Tower Defense?\n")

        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        elapsed_time = time.time() - start_time

        print(f"⏱️  响应时间: {elapsed_time:.2f}秒")
        print(f"📊 状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # 将完整响应写入文件
            output_file = "utils/api_response_non_stream.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"📁 完整响应已保存到: {output_file}")

            print(f"✅ 请求成功!")

            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                print(f"\n🤖 AI 回复:\n{content}")

                # 显示完整响应结构
                print(f"\n📋 响应结构:")
                print(f"   - ID: {data.get('id', 'N/A')}")
                print(f"   - 对象类型: {data.get('object', 'N/A')}")
                print(f"   - 创建时间: {data.get('created', 'N/A')}")
                print(f"   - 模型: {data.get('model', 'N/A')}")

                if "usage" in data:
                    usage = data["usage"]
                    print(f"\n📈 Token 使用:")
                    print(f"   - 提示词: {usage.get('prompt_tokens', 'N/A')}")
                    print(f"   - 完成: {usage.get('completion_tokens', 'N/A')}")
                    print(f"   - 总计: {usage.get('total_tokens', 'N/A')}")

                return True
            else:
                print("⚠️  响应格式异常: 缺少 choices 字段")
                return False
        else:
            print(f"❌ 请求失败!")
            print(f"错误信息: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ 请求超时 (>{TIMEOUT}秒)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求错误: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


def main():
    """主函数: 执行所有测试"""
    print("\n" + "=" * 60)
    print("  Gemini API 连通性测试")
    print("=" * 60)
    print(f"\n🔧 配置信息:")
    print(f"   - API 端点: {API_BASE_URL}")
    print(f"   - 模型: {MODEL}")
    print(f"   - 超时设置: {TIMEOUT}秒")

    results = {
        "基础连通性": False,
        "流式响应": False,
        "非流式响应": False
    }

    results["非流式响应"] = test_non_stream_response()

    # 显示测试总结
    print_section("测试总结")

    all_passed = all(results.values())

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    print(f"\n{'=' * 60}")
    if all_passed:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  部分测试失败,请检查配置和网络连接")
    print(f"{'=' * 60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
