"""
JSON Parser Module
Reads article data from JSON file and validates the structure.
"""
import json
from typing import List, Dict
import os


class JsonParser:
    def __init__(self, json_file_path: str, priority_range: tuple = None):
        """
        Initialize the JSON parser.

        Args:
            json_file_path: Path to the JSON file
            priority_range: Optional tuple (min_priority, max_priority) to filter articles
        """
        self.json_file_path = json_file_path
        self.priority_range = priority_range
        self.data = None
        self.original_data = None  # Store original data before filtering

    def load_data(self) -> bool:
        """
        Load and validate JSON file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.json_file_path):
                print(f"❌ Error: JSON file not found at {self.json_file_path}")
                return False

            # Read JSON file
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                self.original_data = json.load(f)

            self.data = self.original_data.copy()

            # Validate required fields
            required_fields = ['URL Path', 'Article Title', 'Keyword']
            if self.data:
                first_item = self.data[0]
                missing_fields = [field for field in required_fields if field not in first_item]

                if missing_fields:
                    print(f"❌ Error: Missing required fields: {', '.join(missing_fields)}")
                    return False

            # Apply priority filter if specified
            if self.priority_range:
                min_priority, max_priority = self.priority_range
                original_count = len(self.data)
                self.data = [
                    item for item in self.data
                    if 'Priority' in item and min_priority <= item['Priority'] <= max_priority
                ]
                filtered_count = len(self.data)
                print(f"✅ Successfully loaded {original_count} articles from JSON")
                print(f"🎯 Filtered to {filtered_count} articles (Priority {min_priority}-{max_priority})")
            else:
                print(f"✅ Successfully loaded {len(self.data)} articles from JSON")

            return True

        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error loading JSON file: {str(e)}")
            return False

    def get_articles(self) -> List[Dict[str, str]]:
        """
        Get all articles as a list of dictionaries.

        Returns:
            List of article dictionaries with keys: url_path, title, keyword, reference, row_number
        """
        if self.data is None:
            print("❌ Error: Data not loaded. Call load_data() first.")
            return []

        articles = []
        for index, item in enumerate(self.data):
            # Skip items with missing essential data
            if not item.get('URL Path') or not item.get('Article Title') or not item.get('Keyword'):
                print(f"⚠️  Warning: Skipping item {index + 1} due to missing data")
                continue

            article = {
                'row_number': index + 1,
                'url_path': str(item['URL Path']).strip(),
                'title': str(item['Article Title']).strip(),
                'keyword': str(item['Keyword']).strip(),
                'reference': str(item.get('Reference Link', '')).strip()
            }
            articles.append(article)

        return articles

    def filter_by_failed_list(self, failed_articles: List[Dict]) -> List[Dict]:
        """
        Filter articles based on a list of failed articles.

        Args:
            failed_articles: List of failed article dictionaries (from file_writer)

        Returns:
            List of article dictionaries that match the failed list
        """
        if not failed_articles:
            return []

        # Build a set of failed URL paths for fast lookup
        failed_urls = {item['url_path'] for item in failed_articles}

        # Get all articles and filter
        all_articles = self.get_articles()
        filtered = [
            article for article in all_articles
            if article['url_path'] in failed_urls
        ]

        return filtered

    def get_article_count(self) -> int:
        """
        Get total number of valid articles.

        Returns:
            int: Number of articles
        """
        return len(self.get_articles())

    def validate_url_paths(self) -> List[str]:
        """
        Validate URL paths and return any issues.

        Returns:
            List of validation error messages
        """
        errors = []
        articles = self.get_articles()

        for idx, article in enumerate(articles):
            url_path = article['url_path']

            # Check if URL path starts with /
            if not url_path.startswith('/'):
                errors.append(f"Item {idx + 1}: URL path should start with '/' - got '{url_path}'")

            # Check if URL path ends with /
            if not url_path.endswith('/'):
                errors.append(f"Item {idx + 1}: URL path should end with '/' - got '{url_path}'")

        return errors

    def get_priority_stats(self) -> Dict:
        """
        Get priority distribution statistics.

        Returns:
            Dictionary with priority statistics
        """
        if self.original_data is None:
            return {}

        # Count priorities
        priority_counts = {}
        for item in self.original_data:
            priority = item.get('Priority', 'Unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        stats = {
            'total': len(self.original_data),
            'distribution': dict(sorted(priority_counts.items())),
            'filtered_count': len(self.data) if self.data is not None else 0
        }
        return stats

    def print_priority_stats(self):
        """Print formatted priority statistics."""
        stats = self.get_priority_stats()

        if not stats:
            print("⚠️  No priority information available")
            return

        print("\n" + "=" * 60)
        print("📊 PRIORITY STATISTICS")
        print("=" * 60)
        print(f"Total Articles:       {stats['total']}")
        print(f"\nPriority Distribution:")
        for priority, count in sorted(stats['distribution'].items()):
            print(f"  Priority {priority}:      {count} articles")

        if self.priority_range:
            min_p, max_p = self.priority_range
            print(f"\n🎯 Filter Applied:    Priority {min_p}-{max_p}")
            print(f"Filtered Articles:    {stats['filtered_count']}")

        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the parser without filter
    print("=== Test 1: Load all articles ===")
    parser = JsonParser("内页.json")
    if parser.load_data():
        parser.print_priority_stats()
        articles = parser.get_articles()
        print(f"📊 Total articles: {len(articles)}\n")

    # Test with priority filter
    print("\n=== Test 2: Load Priority 1-2 articles ===")
    parser_filtered = JsonParser("内页.json", priority_range=(1, 2))
    if parser_filtered.load_data():
        parser_filtered.print_priority_stats()
        articles = parser_filtered.get_articles()
        print(f"📊 Filtered articles: {len(articles)}\n")
