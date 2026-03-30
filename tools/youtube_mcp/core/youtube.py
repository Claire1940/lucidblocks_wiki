"""
YouTube 搜索和字幕提取模块（简化版，适配 MCP 服务器）

支持并行搜索和字幕提取，使用代理
"""

import asyncio
import subprocess
import json
from typing import List, Dict, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
import requests

from .config import Config
from .utils import load_cache, save_cache


class YouTube:
    """YouTube 搜索和字幕提取"""

    def __init__(self):
        self.config = Config

    async def search(self, keyword: str, max_results: int = None, max_duration: int = None) -> List[Dict]:
        """
        搜索 YouTube 视频

        Args:
            keyword: 搜索关键词
            max_results: 最大返回结果数（默认使用配置）
            max_duration: 最大视频时长（秒，默认使用配置）

        Returns:
            视频信息列表
        """
        if max_results is None:
            max_results = self.config.YOUTUBE_INITIAL_RESULTS
        if max_duration is None:
            max_duration = self.config.YOUTUBE_MAX_DURATION

        # 使用 yt-dlp 搜索
        videos = await self._ytdlp_search(keyword, max_results)

        # 过滤时长
        filtered = self._filter_by_duration(videos, max_duration)

        return filtered

    async def _ytdlp_search(self, keyword: str, max_results: int) -> List[Dict]:
        """
        使用 yt-dlp 搜索视频

        Args:
            keyword: 关键词
            max_results: 搜索结果数量

        Returns:
            视频信息列表
        """
        search_query = f"ytsearch{max_results}:{keyword}"

        # 构建命令
        cmd = [
            "yt-dlp",
            search_query,
            "--skip-download",
            "--dump-json",
            "--no-warnings",
            "--ignore-errors",
            "--flat-playlist",  # 只获取基本信息，减少数据量
        ]

        # 添加代理（必须使用）
        proxy_url = self.config.get_proxy_url("search")
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

    def _filter_by_duration(self, videos: List[Dict], max_duration: int) -> List[Dict]:
        """
        根据时长过滤视频

        Args:
            videos: 视频列表
            max_duration: 最大时长（秒）

        Returns:
            过滤后的视频列表
        """
        if not videos:
            return []

        # 过滤掉超过最大时长的视频
        filtered = [
            v for v in videos
            if v.get('duration_seconds', 0) <= max_duration
        ]

        # 如果过滤后有视频，返回所有过滤后的视频
        if filtered:
            return filtered

        # 如果所有视频都超时长，返回时长最短的 1 个
        sorted_by_duration = sorted(
            videos,
            key=lambda v: v.get('duration_seconds', float('inf'))
        )
        return sorted_by_duration[:1]

    async def get_transcript(self, video_id: str, languages: List[str] = None, max_retries: int = 2) -> Dict:
        """
        获取视频字幕（带重试机制）

        Args:
            video_id: 视频 ID
            languages: 字幕语言优先级（默认 ['zh', 'en']）
            max_retries: 最大重试次数（默认 2）

        Returns:
            字幕信息字典
        """
        if languages is None:
            languages = ['zh', 'en']

        # 检查缓存
        cache_data = load_cache(video_id, "youtube")
        if cache_data and cache_data.get("content"):
            return {
                "video_id": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "transcript": cache_data["content"],
                "language": cache_data.get("language", "unknown"),
                "success": True,
                "cached": True
            }

        # 缓存未命中，获取字幕（带重试）
        loop = asyncio.get_event_loop()

        for attempt in range(max_retries + 1):
            transcript, language = await loop.run_in_executor(
                None,
                self._get_transcript_sync,
                video_id,
                languages
            )

            if transcript:
                # 保存到缓存
                save_cache(video_id, "youtube", {
                    "video_id": video_id,
                    "content": transcript,
                    "language": language,
                    "source_type": "youtube"
                })

                return {
                    "video_id": video_id,
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "transcript": transcript,
                    "language": language,
                    "success": True,
                    "cached": False,
                    "retries": attempt
                }

            # 如果失败且还有重试机会，等待后重试
            if attempt < max_retries:
                wait_time = 2 ** (attempt + 1)  # 指数退避：2, 4, 8...
                print(f"    [WAIT] 等待 {wait_time} 秒后重试... (尝试 {attempt + 2}/{max_retries + 1})")
                await asyncio.sleep(wait_time)

        # 所有重试都失败
        return {
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "transcript": "",
            "language": None,
            "success": False,
            "error": "字幕不可用",
            "cached": False,
            "retries": max_retries
        }

    def _get_transcript_sync(self, video_id: str, languages: List[str]) -> Tuple[str, str]:
        """
        获取字幕（同步方法）

        Args:
            video_id: 视频 ID
            languages: 字幕语言优先级

        Returns:
            (字幕文本, 语言代码)
        """
        try:
            # 如果使用代理，创建 ProxyConfig
            proxy_url = self.config.get_proxy_url("extract")

            if proxy_url:
                # 使用 GenericProxyConfig
                proxy_config = GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url
                )
                # 创建 API 实例并传入 proxy_config
                api = YouTubeTranscriptApi(proxy_config=proxy_config)
            else:
                # 不使用代理
                api = YouTubeTranscriptApi()

            # 尝试获取字幕（优先指定语言）
            language_codes = []
            for lang in languages:
                if lang == 'zh':
                    language_codes.extend(['zh-Hans', 'zh-Hant', 'zh'])
                else:
                    language_codes.append(lang)

            try:
                # 获取可用字幕列表
                transcript_list = api.list(video_id)

                # 尝试获取指定语言的字幕
                for lang_code in language_codes:
                    try:
                        transcript = transcript_list.find_transcript([lang_code])
                        fetched = transcript.fetch()
                        text = " ".join([snippet.text for snippet in fetched])
                        return (text, lang_code)
                    except:
                        continue

                # 如果指定语言都失败，获取任何可用字幕
                for transcript in transcript_list:
                    try:
                        fetched = transcript.fetch()
                        text = " ".join([snippet.text for snippet in fetched])
                        return (text, transcript.language_code)
                    except:
                        continue

                return ("", None)

            except Exception as e:
                print(f"    [WARN] 字幕获取失败 ({video_id}): {type(e).__name__}: {str(e)}")
                return ("", None)

        except Exception as e:
            print(f"    [WARN] 字幕获取外层异常 ({video_id}): {type(e).__name__}: {str(e)}")
            return ("", None)

    async def search_and_transcribe(self, keyword: str, num_videos: int = 2, max_duration: int = None) -> Dict:
        """
        搜索关键词并获取视频字幕（组合功能）

        Args:
            keyword: 搜索关键词
            num_videos: 获取字幕的视频数量
            max_duration: 最大视频时长（秒）

        Returns:
            包含视频和字幕的字典
        """
        # 1. 搜索视频
        videos = await self.search(keyword, max_results=num_videos * 2, max_duration=max_duration)

        # 取前 num_videos 个
        videos = videos[:num_videos]

        # 2. 并行获取字幕
        tasks = [self.get_transcript(v['video_id']) for v in videos]
        transcripts = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. 组合结果
        results = []
        for video, transcript_result in zip(videos, transcripts):
            if isinstance(transcript_result, Exception):
                # 获取字幕失败
                results.append({
                    **video,
                    "transcript": "",
                    "language": None,
                    "transcript_available": False
                })
            else:
                # 获取字幕成功
                results.append({
                    **video,
                    "transcript": transcript_result.get("transcript", ""),
                    "language": transcript_result.get("language"),
                    "transcript_available": transcript_result.get("success", False)
                })

        return {
            "keyword": keyword,
            "count": len(results),
            "videos": results
        }
