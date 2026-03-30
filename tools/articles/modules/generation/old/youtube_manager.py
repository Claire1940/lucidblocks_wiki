"""
YouTube Manager Module
Manages YouTube video data for article generation.
Provides simple video list (ID + title) to LLM.
"""
import csv
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class YouTubeManager:
    def __init__(self, csv_path: str):
        """
        Initialize the YouTube manager.

        Args:
            csv_path: Path to youtube_data.csv file
        """
        self.csv_path = csv_path
        self.videos = []
        self.stats = {
            'total_videos': 0,
            'filtered_videos': 0
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            Video ID or None
        """
        try:
            parsed = urlparse(url)
            if 'youtube.com' in parsed.netloc:
                return parse_qs(parsed.query).get('v', [None])[0]
            elif 'youtu.be' in parsed.netloc:
                return parsed.path.strip('/')
        except:
            pass
        return None

    def load_videos(self) -> bool:
        """
        Load all videos from CSV file.
        Filters out VR game videos (different from Roblox version).

        Returns:
            bool: True if successful
        """
        try:
            total_count = 0
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_count += 1
                    video_id = self.extract_video_id(row['Video URL'])
                    if video_id:
                        title = row['Title']

                        # 过滤VR游戏视频（与Roblox版本不同）
                        if 'VR' in title or 'friendslop' in title.lower():
                            continue

                        self.videos.append({
                            'id': video_id,
                            'title': title
                        })

            self.stats['total_videos'] = total_count
            self.stats['filtered_videos'] = len(self.videos)
            print(f"✅ Loaded {len(self.videos)} YouTube videos (filtered {total_count - len(self.videos)} VR videos)")
            return True

        except Exception as e:
            print(f"❌ Error loading YouTube videos: {str(e)}")
            return False

    def format_videos_list(self) -> str:
        """
        Format video list as simple text for LLM.
        Only includes video ID and title.

        Returns:
            Formatted string containing all videos
        """
        if not self.videos:
            return "（暂无可用的YouTube视频）"

        formatted_lines = []
        for idx, video in enumerate(self.videos, 1):
            formatted_lines.append(f"{idx}. ID: {video['id']} | Title: {video['title']}")

        return "\n".join(formatted_lines)

    def get_stats(self) -> Dict:
        """Get statistics."""
        return self.stats.copy()

    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("🎬 YOUTUBE VIDEO STATISTICS")
        print("=" * 60)
        print(f"Total Videos in CSV:  {stats['total_videos']}")
        print(f"Available for LLM:    {stats['filtered_videos']}")
        print("\nℹ️  Videos sent as ID+Title list, LLM fills HTML template")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the YouTube manager
    manager = YouTubeManager("tools/articles/youtube_data.csv")
    if manager.load_videos():
        print(f"\n✅ Successfully loaded {len(manager.videos)} videos\n")

        # Test formatting
        print("=" * 60)
        print("📝 Formatted video list for LLM:")
        print("=" * 60)
        print(manager.format_videos_list())
        print("=" * 60)
