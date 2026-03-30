#!/usr/bin/env python3
"""
测试 Articles Modules 的输入输出格式
验证 API 配置和响应处理是否正确
"""

import json
import asyncio
import aiohttp
from pathlib import Path
import sys

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "articles" / "modules"))

def test_config_loading():
    """测试配置文件加载"""
    print("\n" + "=" * 60)
    print("  测试 1: 配置文件加载")
    print("=" * 60 + "\n")

    configs = {
        "generation": Path("tools/articles/modules/generation/config.json"),
        "translate": Path("tools/articles/modules/translate/translate_config.json")
    }

    results = {}
    for name, config_path in configs.items():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            print(f"✅ {name} 配置加载成功")
            print(f"   - API 端点: {config['api_base_url']}")
            print(f"   - 模型: {config['model']}")
            print(f"   - 最大 tokens: {config.get('max_tokens', 'N/A')}")
            print(f"   - 温度: {config.get('temperature', 'N/A')}")
            print()

            results[name] = True
        except Exception as e:
            print(f"❌ {name} 配置加载失败: {e}\n")
            results[name] = False

    return all(results.values())

async def test_api_request_format():
    """测试 API 请求格式"""
    print("\n" + "=" * 60)
    print("  测试 2: API 请求格式")
    print("=" * 60 + "\n")

    # 加载配置
    config_path = Path("tools/articles/modules/generation/config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 构建请求
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": config['model'],
        "max_tokens": 100,  # 使用小值进行测试
        "temperature": config['temperature'],
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say 'Hello, World!' in one sentence."
            }
        ],
        "stream": False,
        "group": "default"
    }

    print("📤 请求格式:")
    print(f"   - URL: {config['api_base_url']}")
    print(f"   - 模型: {payload['model']}")
    print(f"   - 消息数: {len(payload['messages'])}")
    print(f"   - 流式: {payload['stream']}")
    print()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=config['api_base_url'],
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"📥 响应状态: {response.status}")

                if response.status == 200:
                    data = await response.json()

                    # 验证响应格式
                    print("✅ API 请求成功")
                    print("\n📋 响应结构验证:")

                    checks = {
                        "'choices' 字段存在": 'choices' in data,
                        "'choices' 是列表": isinstance(data.get('choices'), list),
                        "'choices' 非空": len(data.get('choices', [])) > 0,
                        "'message' 字段存在": 'message' in data.get('choices', [{}])[0],
                        "'content' 字段存在": 'content' in data.get('choices', [{}])[0].get('message', {}),
                    }

                    all_passed = True
                    for check_name, passed in checks.items():
                        status = "✅" if passed else "❌"
                        print(f"   {status} {check_name}")
                        if not passed:
                            all_passed = False

                    if all_passed:
                        content = data['choices'][0]['message']['content']
                        print(f"\n💬 AI 回复: {content}")

                        if 'usage' in data:
                            print(f"\n📊 Token 使用:")
                            print(f"   - 提示词: {data['usage'].get('prompt_tokens', 'N/A')}")
                            print(f"   - 完成: {data['usage'].get('completion_tokens', 'N/A')}")
                            print(f"   - 总计: {data['usage'].get('total_tokens', 'N/A')}")

                        return True
                    else:
                        print("\n❌ 响应格式不符合预期")
                        return False

                elif response.status == 429:
                    error_text = await response.text()
                    print(f"⚠️  API 配额已用完")
                    print(f"   错误信息: {error_text[:200]}")
                    return False

                else:
                    error_text = await response.text()
                    print(f"❌ API 请求失败")
                    print(f"   状态码: {response.status}")
                    print(f"   错误信息: {error_text[:200]}")
                    return False

    except asyncio.TimeoutError:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 请求异常: {type(e).__name__}: {e}")
        return False

def test_code_compatibility():
    """测试代码兼容性"""
    print("\n" + "=" * 60)
    print("  测试 3: 代码兼容性检查")
    print("=" * 60 + "\n")

    # 检查关键文件
    files_to_check = [
        "tools/articles/modules/generation/api_client.py",
        "tools/articles/modules/translate/translator.py",
        "tools/articles/modules/transpage/translator.py"
    ]

    all_compatible = True

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ 文件不存在: {file_path}")
            all_compatible = False
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否使用标准的响应格式
        if "['choices'][0]['message']['content']" in content or '["choices"][0]["message"]["content"]' in content:
            print(f"✅ {path.name} - 使用标准 OpenAI 响应格式")
        else:
            print(f"⚠️  {path.name} - 未找到标准响应格式")
            all_compatible = False

    return all_compatible

async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  Articles Modules 输入输出格式测试")
    print("=" * 60)

    results = {}

    # 测试 1: 配置加载
    results['config_loading'] = test_config_loading()

    # 测试 2: API 请求格式
    results['api_format'] = await test_api_request_format()

    # 测试 3: 代码兼容性
    results['code_compatibility'] = test_code_compatibility()

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60 + "\n")

    for test_name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过! 输入输出格式正确")
    else:
        print("⚠️  部分测试失败,请检查配置")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
