"""
Internal Links Module
Manages internal links and provides smart link selection for articles.
1. 智能选择内部链接
为每篇文章自动选择最相关的内部链接，优先选择同类别的文章。

举例：
- 如果正在生成 /codes/pixel-blade-codes/ 文章
- 系统会优先选择其他 codes 类别的文章链接
- 如果同类别链接不够，才会从其他类别选择

2. 避免自链接
自动过滤掉文章自己的URL，防止文章链接到自己。

3. 格式化链接
将链接格式化成适合插入提示词的格式：
  - [Pixel Blade 
  Codes](https://pixelbladegame.org/codes/pixel-blade-codes/)
  - [How To Get 
  Wishes](https://pixelbladegame.org/guides/how-to-get-wishes/)
"""
from typing import Dict, List
import random


class InternalLinksManager:
    def __init__(self, links_config: Dict[str, List[str]], site_domain: str):
        """
        Initialize the internal links manager.

        Args:
            links_config: Dictionary mapping categories to lists of internal links
            site_domain: Site domain URL
        """
        self.links_config = links_config
        self.site_domain = site_domain

    def get_category_from_url(self, url_path: str) -> str:
        """
        Extract category from URL path.

        Args:
            url_path: URL path like '/codes/pixel-blade-codes/'

        Returns:
            Category name (e.g., 'codes')
        """
        path = url_path.strip('/')
        parts = path.split('/')
        return parts[0] if parts else 'info'

    def select_links_for_article(
        self,
        url_path: str,
        num_links: int = 2,
        prefer_same_category: bool = True
    ) -> List[str]:
        """
        Select internal links for an article.

        Args:
            url_path: URL path of the current article
            num_links: Number of links to select
            prefer_same_category: Whether to prefer links from the same category

        Returns:
            List of selected internal link paths
        """
        category = self.get_category_from_url(url_path)
        selected = []

        # Get all available links except the current article
        all_links = []
        for cat, links in self.links_config.items():
            for link in links:
                if link != url_path:  # Don't link to self
                    all_links.append((cat, link))

        # If prefer same category, try to get links from same category first
        if prefer_same_category and category in self.links_config:
            same_category_links = [
                link for link in self.links_config[category]
                if link != url_path
            ]

            if len(same_category_links) >= num_links:
                # We have enough links in the same category
                selected = random.sample(same_category_links, num_links)
            elif same_category_links:
                # Use all same-category links and supplement with others
                selected.extend(same_category_links)
                remaining = num_links - len(selected)

                # Get links from other categories
                other_links = [
                    link for cat, link in all_links
                    if cat != category and link not in selected
                ]

                if other_links:
                    selected.extend(random.sample(
                        other_links,
                        min(remaining, len(other_links))
                    ))

        # If we still don't have enough links, randomly select from all
        if len(selected) < num_links:
            available = [link for cat, link in all_links if link not in selected]
            if available:
                needed = min(num_links - len(selected), len(available))
                selected.extend(random.sample(available, needed))

        return selected[:num_links]

    def format_links_for_prompt(self, links: List[str]) -> str:
        """
        Format internal links for inclusion in the prompt.

        Args:
            links: List of internal link paths

        Returns:
            Formatted string of links
        """
        formatted = []
        for link in links:
            full_url = f"{self.site_domain}{link}"
            # Create a descriptive title from the URL
            title = link.strip('/').split('/')[-1].replace('-', ' ').title()
            formatted.append(f"- [{title}]({full_url})")

        return '\n'.join(formatted)

    def get_all_links_by_category(self, category: str) -> List[str]:
        """
        Get all links for a specific category.

        Args:
            category: Category name

        Returns:
            List of links in that category
        """
        return self.links_config.get(category, [])

    def get_link_stats(self) -> Dict:
        """
        Get statistics about available links.

        Returns:
            Dictionary with link statistics
        """
        stats = {
            'total_links': 0,
            'by_category': {}
        }

        for category, links in self.links_config.items():
            stats['by_category'][category] = len(links)
            stats['total_links'] += len(links)

        return stats

    def print_stats(self):
        """Print formatted link statistics."""
        stats = self.get_link_stats()

        print("\n" + "=" * 60)
        print("🔗 INTERNAL LINKS STATISTICS")
        print("=" * 60)
        print(f"Total Links Available: {stats['total_links']}")
        print("\nBy Category:")
        for category, count in stats['by_category'].items():
            print(f"  {category:15s}: {count} links")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the internal links manager
    import json

    with open('tools/articles/config.json', 'r') as f:
        config = json.load(f)

    manager = InternalLinksManager(
        config['internal_links'],
        config['site_domain']
    )

    # Print stats
    manager.print_stats()

    # Test link selection for different categories
    test_urls = [
        '/codes/new-pixel-blade-codes/',
        '/guides/how-to-level-up-fast/',
        '/tier-list/best-weapons/',
        '/info/game-updates/'
    ]

    print("📝 Testing link selection:\n")
    for url in test_urls:
        category = manager.get_category_from_url(url)
        links = manager.select_links_for_article(url, num_links=2)

        print(f"Article: {url}")
        print(f"Category: {category}")
        print(f"Selected links: {len(links)}")
        print(manager.format_links_for_prompt(links))
        print("-" * 60 + "\n")
