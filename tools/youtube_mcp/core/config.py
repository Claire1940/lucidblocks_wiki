"""
YouTube MCP 服务器配置管理（简化版）

只保留 YouTube 相关配置，移除 Web 搜索相关配置
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """YouTube MCP 服务器配置"""

    # ============================================================
    # 代理配置
    # ============================================================
    TUNNEL_HOST = os.getenv("TUNNEL_HOST", "")
    TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "17407"))
    TUNNEL_USER = os.getenv("TUNNEL_USER", "")
    TUNNEL_PASS = os.getenv("TUNNEL_PASS", "")
    USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"

    # 代理格式配置
    TUNNEL_PROXY_FORMAT = os.getenv("TUNNEL_PROXY_FORMAT", "tagged").lower()
    TUNNEL_CHANNEL_PREFIX = os.getenv("TUNNEL_CHANNEL_PREFIX", "channel")
    TUNNEL_TTL = int(os.getenv("TUNNEL_TTL", "10"))

    # ============================================================
    # YouTube 配置
    # ============================================================
    # 搜索参数
    YOUTUBE_INITIAL_RESULTS = int(os.getenv("YOUTUBE_INITIAL_RESULTS", "5"))
    YOUTUBE_MAX_DURATION = int(os.getenv("YOUTUBE_MAX_DURATION", "3600"))
    YOUTUBE_RETRIES = int(os.getenv("YOUTUBE_RETRIES", "3"))
    YOUTUBE_TIMEOUT = int(os.getenv("YOUTUBE_TIMEOUT", "180"))

    # ============================================================
    # 缓存配置
    # ============================================================
    CACHE_DIR = os.getenv("CACHE_DIR", "cache")

    @classmethod
    def get_proxy_url(cls, stage: str = "default") -> str:
        """
        获取代理 URL

        Args:
            stage: 阶段标识（用于生成不同的通道名称）

        Returns:
            代理 URL 字符串，如果不使用代理则返回 None
        """
        if not cls.USE_PROXY or not cls.TUNNEL_HOST:
            return None

        # 根据配置选择代理格式
        if cls.TUNNEL_PROXY_FORMAT == "tagged":
            # 青果隧道 - 普通模式打标记格式
            # http://user:password:channel:ttl@host:port
            channel = f"{cls.TUNNEL_CHANNEL_PREFIX}-{stage}"
            return f"http://{cls.TUNNEL_USER}:{cls.TUNNEL_PASS}:{channel}:{cls.TUNNEL_TTL}@{cls.TUNNEL_HOST}:{cls.TUNNEL_PORT}"
        else:
            # 简单格式（默认）
            # http://user:password@host:port
            return f"http://{cls.TUNNEL_USER}:{cls.TUNNEL_PASS}@{cls.TUNNEL_HOST}:{cls.TUNNEL_PORT}"

    @classmethod
    def validate(cls) -> bool:
        """
        验证必需的配置是否存在

        Returns:
            配置是否有效
        """
        errors = []

        if cls.USE_PROXY and not cls.TUNNEL_HOST:
            errors.append("USE_PROXY=true 但 TUNNEL_HOST 未设置")

        if errors:
            print("⚠️  配置错误:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    @classmethod
    def print_summary(cls):
        """打印配置摘要"""
        print("\n" + "=" * 70)
        print("  YouTube MCP 服务器配置")
        print("=" * 70)
        print(f"YouTube:")
        print(f"  - 初始搜索结果: {cls.YOUTUBE_INITIAL_RESULTS}")
        print(f"  - 最大时长: {cls.YOUTUBE_MAX_DURATION}s")
        print(f"  - 重试次数: {cls.YOUTUBE_RETRIES}")
        print(f"  - 搜索超时: {cls.YOUTUBE_TIMEOUT}s")
        print(f"\n代理:")
        print(f"  - 使用代理: {'是' if cls.USE_PROXY else '否'}")
        if cls.USE_PROXY:
            print(f"  - 代理服务器: {cls.TUNNEL_HOST}:{cls.TUNNEL_PORT}")
            print(f"  - 代理格式: {cls.TUNNEL_PROXY_FORMAT}")
            if cls.TUNNEL_PROXY_FORMAT == "tagged":
                print(f"  - 通道前缀: {cls.TUNNEL_CHANNEL_PREFIX}")
                print(f"  - IP 存活时间: {cls.TUNNEL_TTL}秒")
        print(f"\n缓存:")
        print(f"  - 缓存目录: {cls.CACHE_DIR}")
        print("=" * 70 + "\n")
