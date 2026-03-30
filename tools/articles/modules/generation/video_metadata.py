"""
YouTube 视频元数据管理器
功能：
1. 从 CSV 获取基础数据
2. 提取视频 ID
3. 转换时长和日期格式
4. 缓存结果，避免重复处理

注意：使用 title 作为 description，无需调用 YouTube API

使用方式：
# 一次性预处理（获取所有视频元数据）
python -m tools.articles.fetch_video_metadata

# 文章生成时使用缓存数据
manager = VideoMetadataManager(config)
metadata = manager.get_cached_metadata(video_id)
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import csv


class VideoMetadataManager:
    """视频元数据管理器"""

    def __init__(self, config: dict):
        """
        初始化视频元数据管理器

        Args:
            config: 配置字典，包含：
                - youtube_csv: CSV 文件路径
                - video_metadata_cache: 缓存文件路径（JSON）
        """
        self.csv_path = config.get('youtube_csv', 'tools/articles/youtube_data.csv')
        self.cache_path = config.get('video_metadata_cache', 'tools/articles/video_metadata_cache.json')
        self.cache: Dict[str, dict] = {}

        # 加载已有缓存
        self._load_cache()

    def _load_cache(self):
        """加载缓存文件"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"✅ 已加载缓存: {len(self.cache)} 个视频")
            except Exception as e:
                print(f"⚠️  加载缓存失败: {e}")
                self.cache = {}
        else:
            print("📝 缓存文件不存在，将创建新缓存")
            self.cache = {}

    def _save_cache(self):
        """保存缓存到文件"""
        try:
            # 只有当目录路径不为空时才创建目录
            dir_path = os.path.dirname(self.cache_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            print(f"✅ 缓存已保存: {len(self.cache)} 个视频")
        except Exception as e:
            print(f"❌ 保存缓存失败: {e}")

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        从 YouTube URL 提取视频 ID

        Args:
            url: YouTube URL

        Returns:
            视频 ID 或 None
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\s]+)',
            r'youtube\.com\/embed\/([^&\s]+)',
            r'youtube\.com\/v\/([^&\s]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def minutes_to_iso8601(self, minutes_str: str) -> str:
        """
        将分钟数转换为 ISO 8601 时长格式

        Args:
            minutes_str: 分钟数字符串，如 "8.59"

        Returns:
            ISO 8601 格式，如 "PT8M35S"
        """
        try:
            total_seconds = int(float(minutes_str) * 60)
            mins = total_seconds // 60
            secs = total_seconds % 60

            return f"PT{mins}M{secs}S"
        except:
            return "PT0S"

    def parse_relative_date(self, relative_date: str) -> str:
        """
        解析相对日期为 ISO 8601 日期格式

        Args:
            relative_date: 相对日期，如 "4天前", "1个月前"

        Returns:
            ISO 8601 日期，如 "2024-11-21"
        """
        now = datetime.now()

        # 匹配模式
        patterns = [
            (r'(\d+)\s*天前', 'days'),
            (r'(\d+)\s*小时前', 'hours'),
            (r'(\d+)\s*周前', 'weeks'),
            (r'(\d+)\s*个月前', 'months'),
            (r'(\d+)\s*年前', 'years'),
        ]

        for pattern, unit in patterns:
            match = re.search(pattern, relative_date)
            if match:
                value = int(match.group(1))

                if unit == 'days':
                    date = now - timedelta(days=value)
                elif unit == 'hours':
                    date = now  # 小于1天，算今天
                elif unit == 'weeks':
                    date = now - timedelta(weeks=value)
                elif unit == 'months':
                    date = now - timedelta(days=value * 30)  # 近似
                elif unit == 'years':
                    date = now - timedelta(days=value * 365)  # 近似
                else:
                    date = now

                return date.strftime('%Y-%m-%d')

        # 如果包含 "直播时间"，返回当前日期
        if '直播' in relative_date:
            return now.strftime('%Y-%m-%d')

        # 默认返回当前日期
        return now.strftime('%Y-%m-%d')

    def load_csv_data(self) -> List[dict]:
        """
        从 CSV 加载视频数据

        Returns:
            视频数据列表
        """
        videos = []

        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    videos.append(row)

            print(f"✅ 从 CSV 加载了 {len(videos)} 个视频")
            return videos
        except Exception as e:
            print(f"❌ 读取 CSV 失败: {e}")
            return []

    def fetch_all_metadata(self, limit: Optional[int] = None):
        """
        一次性获取所有视频的元数据（预处理步骤）

        注意：使用 CSV 数据，title 作为 description，无需调用 API

        Args:
            limit: 限制处理数量（用于测试），None 表示处理全部
        """
        print("\n🚀 开始批量处理视频元数据...\n")

        # 加载 CSV 数据
        csv_videos = self.load_csv_data()

        if limit:
            csv_videos = csv_videos[:limit]
            print(f"⚠️  测试模式：只处理前 {limit} 个视频\n")

        success_count = 0
        skip_count = 0

        for idx, row in enumerate(csv_videos, 1):
            video_url = row.get('Video URL', '')
            title = row.get('Title', '').replace('"', '')
            duration_minutes = row.get('Video Duration', '')
            relative_date = row.get('Date the video uploaded', '')

            # 提取视频 ID
            video_id = self.extract_video_id(video_url)

            if not video_id:
                print(f"[{idx}/{len(csv_videos)}] ⚠️  跳过（无法提取 ID）: {title[:50]}...")
                skip_count += 1
                continue

            # 检查缓存
            if video_id in self.cache:
                print(f"[{idx}/{len(csv_videos)}] ✓ 已缓存: {video_id}")
                skip_count += 1
                continue

            # 跳过 SHORTS 视频（时长为 "SHORTS"）
            if duration_minutes == "SHORTS":
                print(f"[{idx}/{len(csv_videos)}] ⚠️  跳过（Shorts 视频）: {video_id}")
                skip_count += 1
                continue

            print(f"[{idx}/{len(csv_videos)}] 🔄 处理中: {video_id} - {title[:50]}...")

            # 转换格式
            duration_iso = self.minutes_to_iso8601(duration_minutes)
            upload_date = self.parse_relative_date(relative_date)

            # 构建元数据（使用 title 作为 description）
            metadata = {
                'enabled': True,
                'youtubeId': video_id,
                'title': title,
                'description': title,  # 使用标题作为描述
                'duration': duration_iso,
                'uploadDate': upload_date
            }

            # 保存到缓存
            self.cache[video_id] = metadata
            success_count += 1

            print(f"[{idx}/{len(csv_videos)}] ✅ 成功: {video_id}")

            # 每处理 10 个视频保存一次缓存（防止中断丢失数据）
            if success_count % 10 == 0:
                self._save_cache()

        # 最终保存
        self._save_cache()

        print("\n" + "="*60)
        print("📊 批量处理完成")
        print("="*60)
        print(f"   总计: {len(csv_videos)} 个视频")
        print(f"   ✅ 成功: {success_count}")
        print(f"   ⏭️  跳过: {skip_count}")
        print(f"   💾 缓存大小: {len(self.cache)} 个视频")
        print("="*60 + "\n")

    def get_cached_metadata(self, video_id: str) -> Optional[dict]:
        """
        从缓存获取视频元数据（文章生成时使用）

        Args:
            video_id: YouTube 视频 ID

        Returns:
            视频元数据字典，或 None
        """
        return self.cache.get(video_id)

    def get_all_cached_metadata(self) -> Dict[str, dict]:
        """
        获取所有缓存的元数据

        Returns:
            所有视频元数据字典
        """
        return self.cache


if __name__ == '__main__':
    """
    独立运行此脚本，生成视频元数据缓存
    """
    # 加载配置
    config = {
        'youtube_csv': 'youtube_data.csv',
        'video_metadata_cache': 'video_metadata_cache.json'
    }

    manager = VideoMetadataManager(config)

    # 批量处理所有视频
    manager.fetch_all_metadata()

    print("✅ 视频元数据缓存生成完成！")
