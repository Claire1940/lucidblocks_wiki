#!/usr/bin/env python3
"""
Article Generation Script
Main script to generate MDX articles using GPT-4o API.

Usage:
    python generate-articles.py [--batch-size 100] [--overwrite] [--test] [--category "Class"]
"""

import asyncio
import json
import os
import sys
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Modules are now in the same directory
from keyword_parser import KeywordParser
from merged_content_parser import MergedContentParser
from api_client import APIClient
from file_writer import FileWriter

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class ArticleGenerator:
    def __init__(self, config_path: str = 'config.json', category_filter: str = None):
        """
        Initialize the article generator.

        Args:
            config_path: Path to configuration file
            category_filter: Optional category name to filter keywords
        """
        self.config_path = config_path
        self.category_filter = category_filter
        self.config = None
        self.keyword_parser = None
        self.merged_content_parser = None
        self.api_client = None
        self.file_writer = None
        self.prompt_template = None

    def load_config(self) -> bool:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"✅ Configuration loaded from {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading configuration: {str(e)}")
            return False

    def load_prompt_template(self) -> bool:
        """Load prompt template from file."""
        try:
            template_path = 'prompt-template.txt'
            with open(template_path, 'r', encoding='utf-8') as f:
                self.prompt_template = f.read()
            print(f"✅ Prompt template loaded")
            return True
        except Exception as e:
            print(f"❌ Error loading prompt template: {str(e)}")
            return False

    def initialize_modules(self) -> bool:
        """Initialize all modules."""
        try:
            # Initialize keyword parser
            self.keyword_parser = KeywordParser(self.config['keywords_file'])
            print("✅ Keyword parser initialized")

            # Print keyword statistics
            all_categories = self.keyword_parser.get_all_categories()
            print(f"   Found {len(all_categories)} categories")
            if self.category_filter:
                keyword_count = self.keyword_parser.get_keyword_count(self.category_filter)
                print(f"   Filtering by category: {self.category_filter} ({keyword_count} keywords)")
            else:
                total_keywords = self.keyword_parser.get_keyword_count()
                print(f"   Total keywords: {total_keywords}")

            # Initialize merged content parser
            self.merged_content_parser = MergedContentParser(self.config['merged_dir'])
            print("✅ Merged content parser initialized")

            # Initialize API client
            self.api_client = APIClient(self.config)
            print("✅ API client initialized")

            # Initialize file writer
            self.file_writer = FileWriter(
                self.config['output_dir']
            )
            print("✅ File writer initialized")

            return True

        except Exception as e:
            print(f"❌ Error initializing modules: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def build_prompt(self, article: Dict, merged_data: Dict) -> str:
        """
        Build prompt for article generation.

        Args:
            article: {keyword, category, merged_data_path}
            merged_data: Complete merged JSON content

        Returns:
            Complete prompt string
        """
        # Format merged data as JSON string
        merged_json = self.merged_content_parser.format_for_prompt(merged_data)

        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Build prompt from template
        prompt = self.prompt_template.format(
            merged_data=merged_json,
            current_date=current_date
        )

        return prompt

    async def generate_all_articles(
        self,
        batch_size: int = 100,
        overwrite: bool = False,
        test_mode: bool = False
    ):
        """
        Generate all articles from keywords.json and merged/*.json.

        Args:
            batch_size: Number of concurrent API requests
            overwrite: Whether to overwrite existing files
            test_mode: If True, only process first 2 articles
        """
        print("\n" + "=" * 60)
        print("🚀 STARTING ARTICLE GENERATION")
        print("=" * 60 + "\n")

        # Step 1: Get keywords from keyword_parser
        keywords = self.keyword_parser.get_keywords_by_category(self.category_filter)

        if test_mode:
            keywords = keywords[:2]
            print(f"🧪 TEST MODE: Processing only {len(keywords)} keywords\n")

        print(f"📝 Total keywords to process: {len(keywords)}\n")

        # Step 2: Load merged content for each keyword
        print("📂 Loading merged content...")
        articles_to_generate = []
        skipped_count = 0

        for kw in keywords:
            merged_data = self.merged_content_parser.load_merged_content(kw['keyword'])

            if merged_data is None:
                logger.warning(f"Skipping '{kw['keyword']}': merged file not found")
                skipped_count += 1
                continue

            # Get source summary
            summary = self.merged_content_parser.get_source_summary(merged_data)
            logger.info(f"✓ {kw['keyword']}: {summary['total_sources']} sources ({summary['youtube_count']} videos, {summary['web_count']} web)")

            articles_to_generate.append({
                'keyword': kw['keyword'],
                'category': kw['category'],
                'merged_data': merged_data
            })

        if skipped_count > 0:
            print(f"\n⚠️  Skipped {skipped_count} keywords (no merged data)\n")

        if not articles_to_generate:
            print("❌ No articles to generate (all keywords lack merged data)\n")
            return

        print(f"\n✅ Loaded {len(articles_to_generate)} articles with merged data\n")

        # NEW: Filter out existing files if not overwriting
        if not overwrite:
            print("🔍 Checking for existing files...")
            articles_before = len(articles_to_generate)
            articles_to_generate = [
                article for article in articles_to_generate
                if not self.file_writer.check_file_exists(article, locale='en')
            ]
            existing_count = articles_before - len(articles_to_generate)
            if existing_count > 0:
                print(f"⏭️  Skipped {existing_count} articles (files already exist)\n")

            if not articles_to_generate:
                print("ℹ️  All articles already exist. Use --overwrite to regenerate.\n")
                return

        print(f"📝 {len(articles_to_generate)} articles need to be generated\n")

        # Step 3: Build prompts for all articles
        print("🔨 Building prompts...")
        prompts = []
        for article in articles_to_generate:
            prompt = self.build_prompt(article, article['merged_data'])
            prompts.append((prompt, article))

        print(f"✅ Built {len(prompts)} prompts\n")

        # Step 4: Generate articles via API
        print("🤖 Generating articles via GPT-4o API...")
        print(f"   Batch size: {batch_size}")
        print(f"   Concurrent limit: {self.config['concurrent_limit']}")
        print(f"   Max tokens: {self.config['max_tokens']}\n")

        results = await self.api_client.generate_articles_batch(
            prompts,
            batch_size=batch_size
        )

        # Step 5: Save articles
        print("\n💾 Saving generated articles...")

        saved_count = 0
        failed_count = 0

        for article_info, content in results:
            if content:
                # Save English article
                success = self.file_writer.save_article(
                    content,
                    article_info,  # Now only contains keyword, category
                    overwrite=overwrite,
                    locale='en'
                )
                if success:
                    saved_count += 1
                else:
                    failed_count += 1
            else:
                self.file_writer.save_failed_article(
                    article_info,
                    "API generation failed"
                )
                failed_count += 1

        # Step 6: Print statistics
        print("\n" + "=" * 60)
        print("📊 GENERATION COMPLETE")
        print("=" * 60)

        self.api_client.print_stats()
        self.file_writer.print_stats()

        # Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        print(f"Total Keywords:       {len(keywords)}")
        print(f"Successfully Saved:   {saved_count} ✅")
        print(f"Failed:               {failed_count} ❌")
        print(f"Skipped (no data):    {skipped_count} ⏭️")
        if len(articles_to_generate) > 0:
            print(f"Success Rate:         {round(saved_count / len(articles_to_generate) * 100, 2)}%")
        print("=" * 60 + "\n")

        if failed_count > 0:
            print(f"ℹ️  Failed articles logged to: tools/articles/logs/failed_articles.log\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate MDX articles using GPT-4o API')
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Number of concurrent API requests (default: 100)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing MDX files'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: only process first 2 keywords'
    )
    parser.add_argument(
        '--category',
        type=str,
        help='Filter by category (e.g., "Class", "Equipment", "Quest")'
    )

    args = parser.parse_args()

    # Create generator with category filter
    generator = ArticleGenerator(category_filter=args.category)

    # Load configuration and initialize
    if not generator.load_config():
        sys.exit(1)

    if not generator.load_prompt_template():
        sys.exit(1)

    if not generator.initialize_modules():
        sys.exit(1)

    # Generate articles
    try:
        asyncio.run(generator.generate_all_articles(
            batch_size=args.batch_size,
            overwrite=args.overwrite,
            test_mode=args.test
        ))
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
