#!/usr/bin/env python3
"""
API 连接测试脚本
测试不同模型和不同内容大小的 API 响应
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path


async def test_api_call(api_key: str, api_base_url: str, model: str, content: str, test_name: str):
    """
    测试单个 API 调用

    Args:
        api_key: API 密钥
        api_base_url: API 基础 URL
        model: 模型名称
        content: 测试内容
        test_name: 测试名称
    """
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"{'='*60}")
    print(f"模型: {model}")
    print(f"内容长度: {len(content)} 字符")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"Translate the following text to Portuguese:\n\n{content}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "stream": False,
        "group": "default"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Connection": "keep-alive"
    }

    start_time = time.time()

    try:
        timeout = aiohttp.ClientTimeout(
            total=120,
            connect=30,
            sock_read=90
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=api_base_url,
                json=payload,
                headers=headers,
                timeout=timeout
            ) as response:
                elapsed = time.time() - start_time

                if response.status == 200:
                    data = await response.json()
                    result = data['choices'][0]['message']['content']
                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    print(f"  响应长度: {len(result)} 字符")
                    print(f"  响应预览: {result[:100]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"✗ 失败 (耗时: {elapsed:.2f}秒)")
                    print(f"  状态码: {response.status}")
                    print(f"  错误: {error_text[:200]}")
                    return False

    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"✗ 超时 (耗时: {elapsed:.2f}秒)")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ 异常 (耗时: {elapsed:.2f}秒)")
        print(f"  异常类型: {type(e).__name__}")
        print(f"  异常信息: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("API 连接测试")
    print("="*60)

    # 加载配置
    config_path = Path(__file__).parent / 'transpage_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    api_key = config['api_key']
    api_base_url = config['api_base_url']

    print(f"\nAPI 地址: {api_base_url}")
    print(f"API 密钥: {api_key[:20]}...")

    # 测试不同的模型
    models_to_test = [
        "aws.amazon/claude-opus-4-5:once",
        "gemini-2.0-flash-exp",
        "gpt-4o",
        "claude-3-5-sonnet-20241022"
    ]

    # 测试内容（不同大小）
    test_contents = {
        "小内容 (50字符)": "Home\nMore\nPlay Now\nLearn More\nGet Started",
        "中等内容 (200字符)": "\n".join([
            "Home", "More", "Play Now", "Learn More", "Get Started",
            "Welcome to Slayerbound", "Your ultimate resource",
            "Discover powerful units", "Master the game",
            "Join the community", "Latest updates", "Game guides"
        ]),
        "大内容 (1000字符)": "\n".join([f"Test line {i}: This is a sample text for translation testing." for i in range(20)])
    }

    results = {}

    # 测试每个模型
    for model in models_to_test:
        print(f"\n{'#'*60}")
        print(f"测试模型: {model}")
        print(f"{'#'*60}")

        model_results = {}

        # 测试不同大小的内容
        for content_name, content in test_contents.items():
            success = await test_api_call(
                api_key=api_key,
                api_base_url=api_base_url,
                model=model,
                content=content,
                test_name=content_name
            )
            model_results[content_name] = success

            # 避免请求过快
            await asyncio.sleep(2)

        results[model] = model_results

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    for model, model_results in results.items():
        success_count = sum(1 for v in model_results.values() if v)
        total_count = len(model_results)
        print(f"\n{model}:")
        print(f"  成功: {success_count}/{total_count}")
        for content_name, success in model_results.items():
            status = "✓" if success else "✗"
            print(f"    {status} {content_name}")

    # 推荐最佳模型
    print("\n" + "="*60)
    print("推荐配置")
    print("="*60)

    best_model = None
    best_score = 0

    for model, model_results in results.items():
        score = sum(1 for v in model_results.values() if v)
        if score > best_score:
            best_score = score
            best_model = model

    if best_model:
        print(f"\n推荐使用模型: {best_model}")
        print(f"成功率: {best_score}/{len(test_contents)}")
    else:
        print("\n警告: 所有模型测试均失败！")


if __name__ == "__main__":
    asyncio.run(main())
