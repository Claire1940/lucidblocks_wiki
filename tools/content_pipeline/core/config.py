"""
统一配置管理

从 .env 文件加载所有配置参数
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Config:
    """统一配置管理"""

    # ============================================================
    # API Keys
    # ============================================================
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    JINA_API_KEY = os.getenv("JINA_API_KEY", "")

    # ============================================================
    # 代理配置
    # ============================================================
    TUNNEL_HOST = os.getenv("TUNNEL_HOST", "")
    TUNNEL_PORT = int(os.getenv("TUNNEL_PORT", "18866"))
    TUNNEL_USER = os.getenv("TUNNEL_USER", "")
    TUNNEL_PASS = os.getenv("TUNNEL_PASS", "")
    USE_PROXY = os.getenv("USE_PROXY", "true").lower() == "true"

    # 代理格式配置
    TUNNEL_PROXY_FORMAT = os.getenv("TUNNEL_PROXY_FORMAT", "tagged").lower()
    TUNNEL_CHANNEL_PREFIX = os.getenv("TUNNEL_CHANNEL_PREFIX", "channel")
    TUNNEL_TTL = int(os.getenv("TUNNEL_TTL", "60"))

    # 分阶段代理配置（优先级高于 USE_PROXY）
    USE_PROXY_FOR_SEARCH = os.getenv("USE_PROXY_FOR_SEARCH", "").lower()
    USE_PROXY_FOR_EXTRACT = os.getenv("USE_PROXY_FOR_EXTRACT", "").lower()

    # ============================================================
    # YouTube 配置
    # ============================================================
    # 搜索参数
    YOUTUBE_INITIAL_RESULTS = int(os.getenv("YOUTUBE_INITIAL_SEARCH_RESULTS", "5"))
    YOUTUBE_MAX_RESULTS = int(os.getenv("YOUTUBE_MAX_RESULTS_AFTER_FILTER", "2"))
    YOUTUBE_MAX_DURATION = int(os.getenv("YOUTUBE_MAX_DURATION", "3600"))
    YOUTUBE_EXTRACT_TOP_K = int(os.getenv("YOUTUBE_EXTRACT_TOP_K", "2"))

    # 并发和重试
    YOUTUBE_SEARCH_WORKERS = int(os.getenv("YOUTUBE_SEARCH_WORKERS", "10"))
    YOUTUBE_EXTRACT_WORKERS = int(os.getenv("YOUTUBE_TRANSCRIPT_WORKERS", "15"))
    YOUTUBE_RETRIES = int(os.getenv("YOUTUBE_TRANSCRIPT_RETRIES", "3"))
    YOUTUBE_TIMEOUT = int(os.getenv("YOUTUBE_SEARCH_TIMEOUT", "180"))

    # ============================================================
    # Web 配置
    # ============================================================
    WEB_SEARCH_TOP_N = int(os.getenv("WEB_SEARCH_TOP_N", "10"))
    WEB_EXTRACT_TOP_K = int(os.getenv("WEB_EXTRACT_TOP_K", "1"))
    WEB_EXTRACT_WORKERS = int(os.getenv("JINA_CONCURRENCY", "20"))
    WEB_SEARCH_CONCURRENCY = int(os.getenv("WEB_SEARCH_CONCURRENCY", "5"))
    JINA_RPM = int(os.getenv("JINA_RPM", "200"))
    JINA_CONCURRENCY = int(os.getenv("JINA_CONCURRENCY", "20"))

    # ============================================================
    # 通用配置
    # ============================================================
    OUT_DIR = os.getenv("OUT_DIR", "out")
    BASE_DIR = os.getenv("BASE_DIR", "out")
    CACHE_DIR = os.getenv("CACHE_DIR", "out/cache")

    # 搜索重试配置
    SEARCH_MAX_RETRIES = int(os.getenv("SEARCH_MAX_RETRIES", "3"))
    SEARCH_RETRY_DELAY = int(os.getenv("SEARCH_RETRY_DELAY", "2"))

    # 分类过滤
    IGNORED_CATEGORIES = [
        cat.strip()
        for cat in os.getenv("IGNORED_CATEGORIES", "Server,Community").split(",")
        if cat.strip()
    ]

    # 域名屏蔽
    BLOCKED_DOMAINS = set(
        domain.strip()
        for domain in os.getenv("BLOCKED_DOMAINS",
            "youtube.com,youtu.be,reddit.com,discord.com").split(",")
        if domain.strip()
    )

    @classmethod
    def get_proxy_url(cls) -> str:
        """
        获取代理 URL

        Returns:
            代理 URL 字符串，如果不使用代理则返回 None
        """
        if not cls.USE_PROXY or not cls.TUNNEL_HOST:
            return None

        # 根据配置选择代理格式
        if cls.TUNNEL_PROXY_FORMAT == "tagged":
            # 青果隧道 - 普通模式打标记格式
            # http://user:password:channel:ttl@host:port
            channel = f"{cls.TUNNEL_CHANNEL_PREFIX}-default"
            return f"http://{cls.TUNNEL_USER}:{cls.TUNNEL_PASS}:{channel}:{cls.TUNNEL_TTL}@{cls.TUNNEL_HOST}:{cls.TUNNEL_PORT}"
        else:
            # 简单格式（默认）
            # http://user:password@host:port
            return f"http://{cls.TUNNEL_USER}:{cls.TUNNEL_PASS}@{cls.TUNNEL_HOST}:{cls.TUNNEL_PORT}"

    @classmethod
    def use_proxy_for_stage(cls, stage: str) -> bool:
        """
        获取指定阶段是否使用代理

        Args:
            stage: "search" 或 "extract"

        Returns:
            是否使用代理
        """
        if stage == "search":
            # 如果设置了 USE_PROXY_FOR_SEARCH，使用该配置
            if cls.USE_PROXY_FOR_SEARCH in ("true", "false"):
                return cls.USE_PROXY_FOR_SEARCH == "true"
            # 否则回退到全局配置
            return cls.USE_PROXY

        elif stage == "extract":
            # 如果设置了 USE_PROXY_FOR_EXTRACT，使用该配置
            if cls.USE_PROXY_FOR_EXTRACT in ("true", "false"):
                return cls.USE_PROXY_FOR_EXTRACT == "true"
            # 否则回退到全局配置
            return cls.USE_PROXY

        else:
            # 未知阶段，回退到全局配置
            return cls.USE_PROXY

    @classmethod
    def get_proxy_url_for_stage(cls, stage: str) -> str:
        """
        获取指定阶段的代理 URL

        Args:
            stage: "search" 或 "extract"

        Returns:
            代理 URL 字符串，如果不使用代理则返回 None
        """
        if not cls.use_proxy_for_stage(stage) or not cls.TUNNEL_HOST:
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

        if not cls.SERPER_API_KEY:
            errors.append("SERPER_API_KEY 未设置")

        if not cls.JINA_API_KEY:
            errors.append("JINA_API_KEY 未设置（可选，但建议设置以提高速率限制）")

        if cls.USE_PROXY and not cls.TUNNEL_HOST:
            errors.append("USE_PROXY=true 但 TUNNEL_HOST 未设置")

        if errors:
            print("⚠️  配置警告:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    @classmethod
    def print_summary(cls):
        """打印配置摘要"""
        print("\n" + "=" * 70)
        print("  配置摘要")
        print("=" * 70)
        print(f"YouTube:")
        print(f"  - 初始搜索结果: {cls.YOUTUBE_INITIAL_RESULTS}")
        print(f"  - 最大返回结果: {cls.YOUTUBE_MAX_RESULTS}")
        print(f"  - 最大时长: {cls.YOUTUBE_MAX_DURATION}s")
        print(f"  - 提取视频数: {cls.YOUTUBE_EXTRACT_TOP_K}")
        print(f"  - 搜索并发: {cls.YOUTUBE_SEARCH_WORKERS}")
        print(f"  - 提取并发: {cls.YOUTUBE_EXTRACT_WORKERS}")
        print(f"\nWeb:")
        print(f"  - 搜索结果数: {cls.WEB_SEARCH_TOP_N}")
        print(f"  - 搜索并发: {cls.WEB_SEARCH_CONCURRENCY}")
        print(f"  - 提取页面数: {cls.WEB_EXTRACT_TOP_K}")
        print(f"  - Jina RPM: {cls.JINA_RPM}")
        print(f"  - Jina 并发: {cls.JINA_CONCURRENCY}")
        print(f"\n通用:")
        print(f"  - 输出目录: {cls.OUT_DIR}")
        print(f"  - 忽略分类: {', '.join(cls.IGNORED_CATEGORIES)}")
        print(f"  - 屏蔽域名: {len(cls.BLOCKED_DOMAINS)} 个")
        print(f"  - 使用代理: {'是' if cls.USE_PROXY else '否'}")
        print(f"  - 搜索阶段代理: {'是' if cls.use_proxy_for_stage('search') else '否'}")
        print(f"  - 提取阶段代理: {'是' if cls.use_proxy_for_stage('extract') else '否'}")
        print(f"  - 代理格式: {cls.TUNNEL_PROXY_FORMAT}")
        if cls.TUNNEL_PROXY_FORMAT == "tagged":
            print(f"  - 通道前缀: {cls.TUNNEL_CHANNEL_PREFIX}")
            print(f"  - IP 存活时间: {cls.TUNNEL_TTL}秒")
        print(f"  - 搜索最大重试次数: {cls.SEARCH_MAX_RETRIES}")
        print(f"  - 搜索重试间隔: {cls.SEARCH_RETRY_DELAY}秒")
        print("=" * 70 + "\n")
