"""
API Response Handler - 处理流式和非流式响应
"""

import json
import re


async def parse_api_response(response, target_lang: str):
    """
    解析 API 响应（支持流式和非流式）

    Args:
        response: aiohttp response object
        target_lang: 目标语言代码

    Returns:
        tuple: (success: bool, content: str, error: str)
    """
    content_type = response.headers.get('Content-Type', '')

    # 检查是否是流式响应
    if 'text/event-stream' in content_type or 'stream' in content_type:
        return await parse_stream_response(response, target_lang)
    else:
        return await parse_json_response(response, target_lang)


async def parse_json_response(response, target_lang: str):
    """解析 JSON 响应"""
    try:
        data = await response.json()

        # 标准 OpenAI 格式
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content'].strip()
            return True, content, None

        # 其他格式
        if 'content' in data:
            return True, data['content'].strip(), None

        return False, None, f"未知的响应格式: {list(data.keys())}"

    except json.JSONDecodeError as e:
        return False, None, f"JSON 解析失败: {str(e)}"
    except Exception as e:
        return False, None, f"响应解析异常: {type(e).__name__}: {str(e)}"


async def parse_stream_response(response, target_lang: str):
    """解析流式响应（SSE 格式）"""
    try:
        full_content = []

        async for line in response.content:
            line_text = line.decode('utf-8').strip()

            # 跳过空行和注释
            if not line_text or line_text.startswith(':'):
                continue

            # 解析 SSE 数据行
            if line_text.startswith('data: '):
                data_str = line_text[6:]  # 移除 "data: " 前缀

                # 跳过 [DONE] 标记
                if data_str == '[DONE]':
                    break

                try:
                    data = json.loads(data_str)

                    # 提取内容
                    if 'choices' in data and len(data['choices']) > 0:
                        delta = data['choices'][0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            full_content.append(content)

                except json.JSONDecodeError:
                    # 某些流式响应可能直接返回文本
                    full_content.append(data_str)

        if full_content:
            content = ''.join(full_content).strip()
            return True, content, None
        else:
            return False, None, "流式响应为空"

    except Exception as e:
        return False, None, f"流式响应解析异常: {type(e).__name__}: {str(e)}"


def clean_markdown_code_blocks(content: str) -> str:
    """移除 Markdown 代码块标记"""
    if not content:
        return content

    # 移除开头的代码块标记
    if content.startswith('```'):
        lines = content.split('\n')
        # 移除第一行（```json 或 ```）
        if lines[0].startswith('```'):
            lines = lines[1:]
        # 移除最后一行（```）
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        content = '\n'.join(lines)

    return content.strip()


def extract_json_from_text(text: str) -> str:
    """从文本中提取 JSON（处理 AI 可能添加的额外文本）"""
    # 尝试找到 JSON 对象
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        return json_match.group(0)

    # 尝试找到 JSON 数组
    array_match = re.search(r'\[[\s\S]*\]', text)
    if array_match:
        return array_match.group(0)

    return text
