"""
File Writer Module
Handles saving generated MDX articles to the correct directories.
"""
import os
import re
import json
import logging
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class FileWriter:
    def __init__(self, output_dir: str):
        """
        Initialize the file writer.

        Args:
            output_dir: Base output directory (e.g., 'src/content/')
        """
        self.output_dir = output_dir
        self.stats = {
            'saved': 0,
            'saved_with_warnings': 0,
            'skipped': 0,
            'errors': 0
        }

    def check_file_exists(self, article_info: Dict, locale: str = 'en') -> bool:
        """
        Check if article file already exists.

        Args:
            article_info: Dictionary with article metadata (keyword, category)
            locale: Language code (e.g., 'en', 'vi', 'zh')

        Returns:
            bool: True if file exists, False otherwise
        """
        keyword = article_info.get('keyword', '')
        category = article_info.get('category', '').lower().replace(' ', '-')
        filename = keyword.replace(' ', '-') + '.mdx'
        dir_path = os.path.join(self.output_dir, locale, category)
        file_path = os.path.join(dir_path, filename)
        return os.path.exists(file_path)

    def extract_category_and_filename(self, content: str = None, url_path: str = None, locale: str = 'en') -> tuple:
        """
        Extract category and filename from url_path.

        Args:
            content: MDX content (not used, kept for compatibility)
            url_path: URL path like '/codes/pixel-blade-codes/'
            locale: Language code (e.g., 'en', 'vi', 'zh')

        Returns:
            Tuple of (category, filename, locale)
        """
        if not url_path:
            raise ValueError("No URL path provided")

        # Remove leading and trailing slashes
        path = url_path.strip('/')

        # Split into parts
        parts = path.split('/')

        if len(parts) >= 2:
            category = parts[0]
            filename = parts[1] + '.mdx'
        elif len(parts) == 1:
            # If only one part, use it as both category and filename
            category = parts[0]
            filename = parts[0] + '.mdx'
        else:
            raise ValueError(f"Invalid URL path: {url_path}")

        return category, filename, locale

    def _extract_canonical_from_content(self, content: str) -> Optional[str]:
        """
        Extract canonical URL from MDX content metadata.

        Args:
            content: MDX content

        Returns:
            Canonical URL path or None
        """
        try:
            # Match canonical field in metadata
            # Pattern: canonical: "/category/slug/" or canonical: '/category/slug/'
            pattern = r'canonical:\s*["\']([^"\']+)["\']'
            match = re.search(pattern, content)

            if match:
                return match.group(1)

            return None
        except Exception as e:
            logger.warning(f"Failed to extract canonical from content: {e}")
            return None

    def validate_mdx_content(self, content: str) -> tuple:
        """
        Validate MDX content structure.

        Args:
            content: The MDX content to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validation disabled - accept all content
        return True, ""

    def _format_validation_warning(self, error_msg: str) -> str:
        """
        Format validation error into a user-friendly warning message.

        Args:
            error_msg: Original error message from validation

        Returns:
            Formatted warning string
        """
        # Keep the error message concise for console output
        return error_msg.replace("Missing", "missing").replace("Invalid", "invalid")

    def _clean_mdx_content(self, content: str) -> str:
        """
        Clean up MDX content by removing code block markers if present.

        Args:
            content: Raw MDX content from LLM

        Returns:
            Cleaned MDX content
        """
        # Remove opening ```mdx or ``` marker
        if content.startswith('```mdx'):
            content = content[6:].lstrip('\n')
        elif content.startswith('```'):
            content = content[3:].lstrip('\n')

        # Remove closing ``` marker
        if content.rstrip().endswith('```'):
            content = content.rstrip()[:-3].rstrip()

        return content

    def save_article(
        self,
        content: str,
        article_info: Dict,
        overwrite: bool = False,
        locale: str = 'en'
    ) -> bool:
        """
        Save article to the appropriate directory with multi-language support.

        Args:
            content: The MDX content to save
            article_info: Dictionary with article metadata (keyword, category)
            overwrite: Whether to overwrite existing files
            locale: Language code (e.g., 'en', 'vi', 'zh')

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Step 0: Clean up content (remove code block markers if present)
            content = self._clean_mdx_content(content)

            # Step 1: Validate content (store result, don't exit early)
            is_valid, error_msg = self.validate_mdx_content(content)

            # Step 2: Extract category and filename from article_info
            keyword = article_info.get('keyword', '')
            category = article_info.get('category', '').lower().replace(' ', '-')
            filename = keyword.replace(' ', '-') + '.mdx'

            # Step 3: Create full directory path with locale: content/{locale}/{category}/
            dir_path = os.path.join(self.output_dir, locale, category)
            os.makedirs(dir_path, exist_ok=True)

            # Step 4: Create full file path
            file_path = os.path.join(dir_path, filename)

            # Step 5: Check if file exists
            if os.path.exists(file_path) and not overwrite:
                print(f"⏭️  Skipping {locale}/{category}/{filename} (already exists)")
                self.stats['skipped'] += 1
                return False

            # Step 6: Write file (ALWAYS, regardless of validation status)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Step 7: Update stats and output based on validation result
            if is_valid:
                print(f"✅ Saved: {locale}/{category}/{filename}")
                self.stats['saved'] += 1
            else:
                # File written despite validation issues
                warning_msg = self._format_validation_warning(error_msg)
                print(f"⚠️ Saved with warnings: {locale}/{category}/{filename}")
                print(f"   {warning_msg}")
                self.stats['saved_with_warnings'] += 1

                # Log to failed_articles for tracking (as warning, not error)
                self.save_failed_article(
                    article_info,
                    error_msg=f"VALIDATION_WARNING: {error_msg}",
                    written_with_warnings=True
                )

            return True

        except Exception as e:
            print(f"❌ Error saving {article_info.get('keyword', article_info.get('title', 'Unknown'))} [{locale}]: {str(e)}")
            self.stats['errors'] += 1
            return False

    def _get_log_dir(self) -> str:
        """Get the log directory path."""
        # Use working directory as project root
        project_root = os.getcwd()
        log_dir = os.path.join(project_root, 'tools', 'articles', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _get_failed_json_path(self) -> str:
        """Get the path to failed_articles.json file."""
        return os.path.join(self._get_log_dir(), 'failed_articles.json')

    def save_failed_article(
        self,
        article_info: Dict,
        error_msg: str = "API generation failed",
        written_with_warnings: bool = False
    ):
        """
        Log failed article generation in both text and JSON format.

        Args:
            article_info: Dictionary with article metadata
            error_msg: Error message
            written_with_warnings: True if content was written despite validation issues
        """
        log_dir = self._get_log_dir()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get keyword for logging (support both old and new format)
        keyword = article_info.get('keyword', 'Unknown')
        title = article_info.get('title', keyword)
        url_path = article_info.get('url_path', f"/{article_info.get('category', 'unknown')}/{keyword.replace(' ', '-')}/")

        # Save to text log (human readable)
        log_file = os.path.join(log_dir, 'failed_articles.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {url_path} - {title}\n")
            f.write(f"  Reason: {error_msg}\n")
            f.write(f"  Keyword: {keyword}\n")
            f.write("-" * 80 + "\n")

        # Save to JSON log (machine readable for retry)
        json_file = self._get_failed_json_path()

        # Load existing failed articles
        failed_list = []
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    failed_list = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                failed_list = []

        # Check if article already exists in failed list (by url_path)
        existing_urls = {item.get('url_path', item.get('keyword', '')) for item in failed_list}
        if url_path not in existing_urls and keyword not in existing_urls:
            # Add new failed article
            failed_entry = {
                'keyword': keyword,
                'url_path': url_path,
                'title': title,
                'category': article_info.get('category', 'unknown'),
                'error': error_msg,
                'timestamp': timestamp,
                'retry_count': 0,
                'written_with_warnings': written_with_warnings
            }
            failed_list.append(failed_entry)

            # Save updated list
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(failed_list, f, ensure_ascii=False, indent=2)

    def get_failed_articles(self) -> List[Dict]:
        """
        Get list of failed articles from JSON log.

        Returns:
            List of failed article dictionaries
        """
        json_file = self._get_failed_json_path()

        if not os.path.exists(json_file):
            return []

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def remove_from_failed_list(self, url_path: str):
        """
        Remove an article from the failed list after successful retry.

        Args:
            url_path: URL path of the article to remove
        """
        json_file = self._get_failed_json_path()

        if not os.path.exists(json_file):
            return

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                failed_list = json.load(f)

            # Remove article with matching url_path
            failed_list = [item for item in failed_list if item['url_path'] != url_path]

            # Save updated list
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(failed_list, f, ensure_ascii=False, indent=2)
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    def clear_failed_articles(self):
        """Clear all failed articles from the JSON log."""
        json_file = self._get_failed_json_path()
        log_file = os.path.join(self._get_log_dir(), 'failed_articles.log')

        # Clear JSON file
        if os.path.exists(json_file):
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Archive text log with timestamp
        if os.path.exists(log_file):
            archive_name = f"failed_articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            archive_path = os.path.join(self._get_log_dir(), archive_name)
            os.rename(log_file, archive_path)
            print(f"📁 Archived old log to: {archive_name}")

    def get_stats(self) -> Dict:
        """
        Get file writing statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()
        total = stats['saved'] + stats['saved_with_warnings'] + stats['skipped'] + stats['errors']

        print("\n" + "=" * 60)
        print("📁 FILE WRITING STATISTICS")
        print("=" * 60)
        print(f"Total Processed:      {total}")
        print(f"Successfully Saved:   {stats['saved']} ✅")
        print(f"Saved with Warnings:  {stats['saved_with_warnings']} ⚠️")
        print(f"Skipped (exists):     {stats['skipped']} ⏭️")
        print(f"Errors:               {stats['errors']} ❌")

        if total > 0:
            total_written = stats['saved'] + stats['saved_with_warnings']
            success_rate = round(total_written / total * 100, 2)
            print(f"Write Success Rate:   {success_rate}%")

        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the file writer
    writer = FileWriter("src/content/", "https://pixelbladegame.org")

    # Test article
    test_content = """---
title: "Test Article"
description: "This is a test article for validation"
keywords: ["test", "article"]
canonical: "https://pixelbladegame.org/codes/test-article/"
date: "2025-11-20"
---

# Test Article

This is a test article body.

## Section 1

Content here.

## Section 2

More content.

## Section 3

Even more content.

## Section 4

Final content.
"""

    test_info = {
        'url_path': '/codes/test-article/',
        'title': 'Test Article',
        'keyword': 'test'
    }

    # Test validation
    is_valid, error = writer.validate_mdx_content(test_content)
    print(f"Validation: {'✅ Valid' if is_valid else f'❌ Invalid - {error}'}")

    # Test extraction
    category, filename = writer.extract_category_and_filename(test_info['url_path'])
    print(f"Category: {category}, Filename: {filename}")
