"""
YouTube 搜索和提取模块

支持并行搜索和字幕提取
"""

import asyncio
import subprocess
import json
import re
from typing import List, Dict, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
import requests

from .config import Config
from .models import YouTubeItem
from .utils import format_duration, load_cache, save_cache


class YouTube:
    """YouTube 搜索和提取（支持并行）"""

    def __init__(self):
        self.config = Config

    async def search_batch(self, keywords: List[str]) -> Dict[str, List[YouTubeItem]]:
        """
        并行搜索多个关键词（带实时进度反馈）

        Args:
            keywords: 关键词列表

        Returns:
            {keyword: [YouTubeItem, ...]}
        """
        print(f"\n🔍 YouTube 搜索: {len(keywords)} 个关键词")

        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(self.config.YOUTUBE_SEARCH_WORKERS)

        # 包装函数：搜索并返回 (keyword, result, error, retry_count)
        async def search_and_tag(keyword: str, index: int, total: int):
            retry_count = 0
            async with semaphore:
                # 开始搜索时立即打印
                print(f"  🔄 [{index}/{total}] 开始搜索: {keyword}")

                for attempt in range(self.config.YOUTUBE_RETRIES):
                    try:
                        # 使用 yt-dlp 搜索
                        videos = await self._ytdlp_search(keyword)

                        # 过滤时长
                        filtered = self._filter_by_duration(videos)

                        # 转换为 YouTubeItem
                        items = [self._to_item(v) for v in filtered]

                        return (keyword, items, None, retry_count)

                    except Exception as e:
                        retry_count = attempt + 1
                        if attempt == self.config.YOUTUBE_RETRIES - 1:
                            return (keyword, [], e, retry_count)
                        await asyncio.sleep(2 ** attempt)

        # 创建所有任务
        tasks = [search_and_tag(kw, i+1, len(keywords)) for i, kw in enumerate(keywords)]

        # 实时处理完成的任务
        result_dict = {}
        completed = 0
        total = len(keywords)

        for coro in asyncio.as_completed(tasks):
            keyword, result, error, retry_count = await coro
            completed += 1

            if error:
                retry_info = f" (重试 {retry_count} 次)" if retry_count > 0 else ""
                print(f"  ✗ [{completed}/{total}] {keyword}: {error}{retry_info}")
                result_dict[keyword] = []
            else:
                retry_info = f" (重试 {retry_count} 次)" if retry_count > 0 else ""
                print(f"  ✓ [{completed}/{total}] {keyword}: {len(result)} 个视频{retry_info}")
                result_dict[keyword] = result

        return result_dict

    async def _search_single(self, keyword: str, semaphore) -> List[YouTubeItem]:
        """
        搜索单个关键词

        Args:
            keyword: 关键词
            semaphore: 并发控制信号量

        Returns:
            YouTubeItem 列表
        """
        async with semaphore:
            for attempt in range(self.config.YOUTUBE_RETRIES):
                try:
                    # 使用 yt-dlp 搜索
                    videos = await self._ytdlp_search(keyword)

                    # 过滤时长
                    filtered = self._filter_by_duration(videos)

                    # 转换为 YouTubeItem
                    items = [self._to_item(v) for v in filtered]

                    return items

                except Exception as e:
                    if attempt == self.config.YOUTUBE_RETRIES - 1:
                        raise Exception(f"搜索失败: {e}")
                    await asyncio.sleep(2 ** attempt)

    async def _ytdlp_search(self, keyword: str) -> List[Dict]:
        """
        使用 yt-dlp 搜索视频

        Args:
            keyword: 关键词

        Returns:
            视频信息列表
        """
        search_query = f"ytsearch{self.config.YOUTUBE_INITIAL_RESULTS}:{keyword}"

        # 构建命令
        cmd = [
            "yt-dlp",
            search_query,
            "--skip-download",
            "--dump-json",
            "--no-warnings",
            "--ignore-errors",
            "--flat-playlist",  # 只获取基本信息，不获取格式列表（减少 98% 数据量）
        ]

        # 添加代理（搜索阶段）
        proxy_url = self.config.get_proxy_url_for_stage("search")
        if proxy_url:
            cmd.extend(["--proxy", proxy_url])

        # 执行命令
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.config.YOUTUBE_TIMEOUT
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise Exception("搜索超时")

        # 解析结果
        videos = []
        for line in stdout.decode().strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    videos.append({
                        'title': data.get('title', ''),
                        'video_id': data.get('id', ''),
                        'url': f"https://www.youtube.com/watch?v={data.get('id', '')}",
                        'channel': data.get('uploader', ''),
                        'duration': data.get('duration_string', ''),
                        'duration_seconds': data.get('duration', 0),
                        'view_count': data.get('view_count', 0)
                    })
                except json.JSONDecodeError:
                    continue

        if not videos:
            raise Exception("未找到任何视频")

        return videos

    def _filter_by_duration(self, videos: List[Dict]) -> List[Dict]:
        """
        根据时长过滤视频

        Args:
            videos: 视频列表

        Returns:
            过滤后的视频列表
        """
        if not videos:
            return []

        # 过滤掉超过最大时长的视频
        filtered = [
            v for v in videos
            if v.get('duration_seconds', 0) <= self.config.YOUTUBE_MAX_DURATION
        ]

        # 如果过滤后有视频，返回所有过滤后的视频（不限制数量）
        if filtered:
            return filtered

        # 如果所有视频都超时长，返回时长最短的 1 个
        sorted_by_duration = sorted(
            videos,
            key=lambda v: v.get('duration_seconds', float('inf'))
        )
        return sorted_by_duration[:1]

    def _to_item(self, video: Dict) -> YouTubeItem:
        """
        转换为 YouTubeItem

        Args:
            video: 视频信息字典

        Returns:
            YouTubeItem 对象
        """
        return YouTubeItem(
            title=video.get('title', ''),
            url=video.get('url', ''),
            video_id=video.get('video_id', ''),
            channel=video.get('channel', ''),
            duration=video.get('duration', ''),
            duration_seconds=video.get('duration_seconds', 0),
            view_count=video.get('view_count', 0),
            selected=True
        )

    async def extract_batch(self, items: List[YouTubeItem]) -> List[Tuple[YouTubeItem, str]]:
        """
        并行提取多个视频字幕

        Args:
            items: YouTubeItem 列表

        Returns:
            [(item, content), ...]
        """
        print(f"\n📥 YouTube 提取: {len(items)} 个视频")

        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(self.config.YOUTUBE_EXTRACT_WORKERS)

        # 并行提取
        tasks = [self._extract_single(item, semaphore) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计成功和失败
        success_count = sum(1 for _, content in results if content and not isinstance(content, Exception))
        failed_count = len(items) - success_count

        print(f"  ✓ 成功: {success_count}/{len(items)}")

        # 显示失败统计
        if failed_count > 0:
            print(f"  ✗ 失败: {failed_count}/{len(items)}")
            failed_items = [(item, content) for item, content in results if not content or isinstance(content, Exception)]
            if failed_items and failed_count <= 10:
                # 如果失败数量不多，列出所有失败项
                for item, _ in failed_items:
                    print(f"    - {item.video_id}: {item.title[:50]}...")
            elif failed_items:
                # 失败太多，只显示前5个
                print(f"    显示前5个失败项:")
                for item, _ in failed_items[:5]:
                    print(f"    - {item.video_id}: {item.title[:50]}...")

        return results

    async def _extract_single(self, item: YouTubeItem, semaphore) -> Tuple[YouTubeItem, str]:
        """
        提取单个视频字幕（带缓存）

        Args:
            item: YouTubeItem 对象
            semaphore: 并发控制信号量

        Returns:
            (item, content) 元组
        """
        async with semaphore:
            # 1. 检查缓存
            cache_data = load_cache(item.video_id, "youtube", title=item.title)
            if cache_data and cache_data.get("content"):
                print(f"  💾 缓存命中: {item.title[:50]}...")
                return (item, cache_data["content"])

            # 2. 缓存未命中，提取内容
            for attempt in range(self.config.YOUTUBE_RETRIES):
                try:
                    # 在线程池中运行同步代码
                    loop = asyncio.get_event_loop()
                    content = await loop.run_in_executor(
                        None,
                        self._get_transcript,
                        item.video_id
                    )

                    # 3. 保存到缓存
                    if content:
                        save_cache(item.video_id, "youtube", {
                            "title": item.title,
                            "url": item.url,
                            "video_id": item.video_id,
                            "content": content,
                            "source_type": "youtube"
                        }, title=item.title)

                    return (item, content)

                except Exception as e:
                    if attempt == self.config.YOUTUBE_RETRIES - 1:
                        # 最后一次重试失败，记录并返回空内容
                        print(f"    ✗ {item.video_id}: 重试{self.config.YOUTUBE_RETRIES}次后失败")
                        return (item, "")
                    await asyncio.sleep(2 ** attempt)

    def _get_transcript(self, video_id: str) -> str:
        """
        获取字幕（同步方法）

        Args:
            video_id: 视频 ID

        Returns:
            字幕文本
        """
        try:
            # 如果使用代理，创建带代理的 session（提取阶段）
            if self.config.use_proxy_for_stage("extract") and self.config.get_proxy_url_for_stage("extract"):
                proxies = {
                    "http": self.config.get_proxy_url_for_stage("extract"),
                    "https": self.config.get_proxy_url_for_stage("extract")
                }
                session = requests.Session()
                session.proxies.update(proxies)

                # 使用自定义 session 创建 API 实例
                api = YouTubeTranscriptApi(http_client=session)
            else:
                # 不使用代理
                api = YouTubeTranscriptApi()

            # 尝试获取字幕（优先中文，然后英文）
            languages = ['zh-Hans', 'zh', 'en']
            try:
                fetched_transcript = api.fetch(video_id, languages=languages)
                # 合并所有字幕文本
                return " ".join([snippet.text for snippet in fetched_transcript])
            except Exception as e:
                # 如果指定语言失败，尝试获取任何可用字幕
                try:
                    fetched_transcript = api.fetch(video_id)
                    return " ".join([snippet.text for snippet in fetched_transcript])
                except Exception as e2:
                    # 记录失败原因
                    error_msg = str(e2).lower()
                    if "transcript" not in error_msg and "subtitle" not in error_msg and "disabled" not in error_msg:
                        # 非字幕相关的错误才打印（避免太多噪音）
                        print(f"    ⚠️ {video_id}: {type(e2).__name__}")
                    return ""

        except Exception as e:
            # 记录外层异常
            print(f"    ⚠️ {video_id}: {type(e).__name__}")
            return ""

