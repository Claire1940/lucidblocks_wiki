"""
工具函数（简化版）

只保留 YouTube MCP 服务器需要的工具函数
"""

import os
import json
import hashlib
import re
from typing import Dict, Any
from datetime import datetime


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def load_json(file_path: str) -> Dict:
    """加载 JSON 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Any, file_path: str, indent: int = 2):
    """保存 JSON 文件"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def format_duration(seconds: int) -> str:
    """
    格式化时长

    Args:
        seconds: 秒数

    Returns:
        格式化的时长字符串 (例如: "10:30", "1:05:30")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    清理文件名，移除特殊字符

    Args:
        filename: 原始文件名
        max_length: 最大长度

    Returns:
        清理后的文件名
    """
    # 移除或替换特殊字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('._')

    # 截断到最大长度
    if len(filename) > max_length:
        filename = filename[:max_length]

    return filename


def get_cache_path(identifier: str, cache_type: str, title: str = None) -> str:
    """
    获取缓存文件路径

    Args:
        identifier: 缓存标识符（video_id 或 url_hash）
        cache_type: 缓存类型（"youtube" 或 "web"）
        title: 标题（可选，用于生成可读的文件名）

    Returns:
        缓存文件的完整路径
    """
    from .config import Config
    cache_dir = f"{Config.CACHE_DIR}/{cache_type}"
    ensure_dir(cache_dir)

    # 如果提供了标题，使用 "标题_identifier" 格式
    if title:
        clean_title = sanitize_filename(title, max_length=80)
        # 使用短哈希（前8位）来保证唯一性
        short_hash = identifier[:8] if len(identifier) > 8 else identifier
        filename = f"{clean_title}_{short_hash}.json"
    else:
        filename = f"{identifier}.json"

    return f"{cache_dir}/{filename}"


def get_url_hash(url: str) -> str:
    """
    获取 URL 的 MD5 哈希值

    Args:
        url: URL 字符串

    Returns:
        MD5 哈希值（32 字符）
    """
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def load_cache(identifier: str, cache_type: str, title: str = None) -> Dict:
    """
    从缓存加载内容

    Args:
        identifier: 缓存标识符
        cache_type: 缓存类型
        title: 标题（可选）

    Returns:
        缓存数据字典，如果不存在返回 None
    """
    cache_path = get_cache_path(identifier, cache_type, title)
    try:
        return load_json(cache_path)
    except FileNotFoundError:
        # 如果使用标题的文件不存在，尝试使用旧格式（仅 identifier）
        if title:
            old_cache_path = get_cache_path(identifier, cache_type, title=None)
            try:
                return load_json(old_cache_path)
            except FileNotFoundError:
                pass
        return None


def save_cache(identifier: str, cache_type: str, data: dict, title: str = None) -> None:
    """
    保存内容到缓存

    Args:
        identifier: 缓存标识符
        cache_type: 缓存类型
        data: 要缓存的数据
        title: 标题（可选）
    """
    cache_path = get_cache_path(identifier, cache_type, title)
    cache_data = {
        **data,
        "cached_at": datetime.now().isoformat()
    }
    save_json(cache_data, cache_path)


def extract_video_id(url: str) -> str:
    """
    从 YouTube URL 提取 video_id

    Args:
        url: YouTube URL

    Returns:
        video_id

    Raises:
        ValueError: 如果 URL 格式不正确
    """
    import re

    # 支持多种 YouTube URL 格式
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    # 如果 URL 本身就是 video_id（11 个字符）
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url

    raise ValueError(f"无法从 URL 提取 video_id: {url}")
