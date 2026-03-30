#!/usr/bin/env python3
"""
测试大内容的超时阈值
找出最佳的批次大小
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path


async def test_large_content(api_key: str, api_base_url: str, model: str, num_lines: int):
    """
    测试指定行数的内容翻译

    Args:
        api_key: API 密钥
        api_base_url: API 基础 URL
        model: 模型名称
        num_lines: 行数
    """
    # 生成测试内容
    content = "\n".join([f"Line {i}: This is a test line for translation." for i in range(num_lines)])

    print(f"\n{'='*60}")
    print(f"测试: {num_lines} 行内容")
    print(f"{'='*60}")
    print(f"内容长度: {len(content)} 字符")

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": f"Translate the following text to Portuguese (one line per line):\n\n{content}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 8192,
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
            total=180,  # 3分钟总超时
            connect=30,
            sock_read=150
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
                    result_lines = result.strip().split('\n')

                    print(f"✓ 成功 (耗时: {elapsed:.2f}秒)")
                    print(f"  响应长度: {len(result)} 字符")
                    print(f"  响应行数: {len(result_lines)} 行")
                    return True, elapsed
                else:
                    error_text = await response.text()
                    print(f"✗ 失败 (耗时: {elapsed:.2f}秒)")
                    print(f"  状态码: {response.status}")
                    print(f"  错误: {error_text[:200]}")
                    return False, elapsed

    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"✗ 超时 (耗时: {elapsed:.2f}秒)")
        return False, elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ 异常 (耗时: {elapsed:.2f}秒)")
        print(f"  异常: {type(e).__name__}: {str(e)}")
        return False, elapsed


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("大内容超时阈值测试")
    print("="*60)

    # 加载配置
    config_path = Path(__file__).parent / 'transpage_config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    api_key = config['api_key']
    api_base_url = config['api_base_url']
    model = "aws.amazon/claude-opus-4-5:once"

    print(f"\n模型: {model}")

    # 测试不同的行数
    test_sizes = [50, 100, 150, 200, 250, 300, 400, 500]

    results = []

    for num_lines in test_sizes:
        success, elapsed = await test_large_content(api_key, api_base_url, model, num_lines)
        results.append({
            'lines': num_lines,
            'success': success,
            'time': elapsed
        })

        # 如果失败，不再测试更大的
        if not success:
            print(f"\n⚠️  在 {num_lines} 行时失败，停止测试更大的内容")
            break

        # 避免请求过快
        await asyncio.sleep(2)

    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)

    max_success_lines = 0
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['lines']:3d} 行 - {result['time']:.2f}秒")
        if result['success']:
            max_success_lines = result['lines']

    print("\n" + "="*60)
    print("推荐配置")
    print("="*60)

    if max_success_lines > 0:
        # 建议使用成功的最大值的 80% 作为安全批次大小
        recommended_batch = int(max_success_lines * 0.8)
        print(f"\n最大成功行数: {max_success_lines}")
        print(f"推荐批次大小: {recommended_batch} 行/批")
        print(f"\n对于 468 个值，需要分成: {(468 + recommended_batch - 1) // recommended_batch} 批")
    else:
        print("\n警告: 所有测试均失败！")


if __name__ == "__main__":
    asyncio.run(main())
