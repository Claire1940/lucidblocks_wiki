#!/usr/bin/env python3
"""
MDX Article Translation Script (Single Language per Call)
Translates English MDX articles to multiple languages with high concurrency.

Usage:
    python translate-articles.py [--test] [--overwrite] [--lang es,pt,ru]
"""

import asyncio
import json
import os
import sys
import argparse
import aiohttp
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add the translate module directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Import from same module directory
from translator import MDXTranslator


class ArticleTranslationManager:
    """Manager for batch translating MDX articles"""

    def __init__(self, config_path: str = None):
        """
        Initialize translation manager

        Args:
            config_path: Path to configuration file (defaults to same directory)
        """
        if config_path is None:
            # Config is in the same directory as this script
            script_dir = os.path.dirname(__file__)
            config_path = os.path.join(script_dir, 'translate_config.json')

        self.config_path = config_path
        self.config = None
        self.translator = None
        self.base_dir = None

    def load_config(self) -> bool:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"[OK] Configuration loaded from {self.config_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error loading configuration: {str(e)}")
            return False

    def initialize(self) -> bool:
        """Initialize translator"""
        try:
            self.translator = MDXTranslator(self.config)
            self.base_dir = self.config.get('output_dir', 'src/content/')
            print("[OK] Translator initialized")
            return True
        except Exception as e:
            print(f"[ERROR] Error initializing translator: {str(e)}")
            return False

    def find_english_articles(self) -> List[Path]:
        """
        Find all English MDX articles

        Returns:
            List of Path objects for English articles
        """
        en_dir = Path(self.base_dir) / 'en'

        if not en_dir.exists():
            print(f"[ERROR] English articles directory not found: {en_dir}")
            return []

        # Find all .mdx files recursively
        articles = list(en_dir.glob('**/*.mdx'))

        print(f"[OK] Found {len(articles)} English articles")
        return articles

    def _save_failed_translations(self, failed_translations: List[Dict]):
        """
        Save failed translations to log files

        Args:
            failed_translations: List of failed translation records
        """
        if not failed_translations:
            return

        # Get the project root directory (go up from tools/articles/modules/translate/)
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent.parent
        logs_dir = project_root / 'tools' / 'articles' / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Save to JSON file (overwrite mode - only contains latest failed translations)
        json_file = logs_dir / 'failed_translations.json'
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(failed_translations, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVE] Failed translations saved to: {json_file}")
        except Exception as e:
            print(f"\n[WARN] Failed to save JSON log: {str(e)}")

        # Save to text log file (append mode - keeps history)
        log_file = logs_dir / 'failed_translations.log'
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Translation Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"{'='*80}\n\n")

                for item in failed_translations:
                    f.write(f"[{item['timestamp']}] {item['article']} ({item['language_name']})\n")
                    f.write(f"  Language: {item['language'].upper()}\n")
                    f.write(f"  Article: {item['article_name']}\n")
                    f.write(f"  Error: {item['error']}\n")
                    f.write(f"{'-'*80}\n")

            print(f"[SAVE] Failed translations log appended to: {log_file}")
        except Exception as e:
            print(f"[WARN] Failed to save text log: {str(e)}")

    async def translate_all_articles(
        self,
        target_langs: List[str],
        test_mode: bool = False,
        overwrite: bool = False
    ):
        """
        Translate all English articles to target languages
        Strategy: Configurable batch size for optimal performance

        Args:
            target_langs: List of target language codes
            test_mode: If True, only process first 2 articles
            overwrite: Whether to overwrite existing files
        """
        # Single language translation mode (always)
        print(f"\n[MODE] Single language translation mode")
        await self._translate_single_mode(target_langs, test_mode, overwrite)

    async def _translate_single_mode(
        self,
        target_langs: List[str],
        test_mode: bool = False,
        overwrite: bool = False
    ):
        """
        Single language translation mode (current implementation)
        Strategy: One API call per (article × language) for maximum concurrency
        """
        print("\n" + "=" * 60)
        print("[START] ARTICLE TRANSLATION (SINGLE LANGUAGE)")
        print("=" * 60 + "\n")

        print(f"[TARGET] Target languages: {', '.join(target_langs)}")

        # Find English articles
        articles = self.find_english_articles()

        if not articles:
            print("[ERROR] No English articles found")
            return

        if test_mode:
            articles = articles[:1]
            print(f"[TEST] TEST MODE: Processing only {len(articles)} articles\n")

        print(f"[INFO] Total articles to translate: {len(articles)}")
        print(f"[INFO] Maximum API calls: {len(articles) * len(target_langs)}\n")

        # 使用默认 ClientSession（参考 api_client.py 的成功实现）
        async with aiohttp.ClientSession() as session:
            # Build translation tasks (article × language)
            all_tasks = []

            print("[BUILD] Building translation tasks...")
            for article_path in articles:
                # Read English article
                try:
                    with open(article_path, 'r', encoding='utf-8') as f:
                        en_content = f.read()
                except Exception as e:
                    print(f"[ERROR] Error reading {article_path}: {str(e)}")
                    continue

                # Get relative path
                en_dir = Path(self.base_dir) / 'en'
                relative_path = article_path.relative_to(en_dir)
                article_name = relative_path.stem

                # Create task for each language
                for lang in target_langs:
                    output_path = Path(self.base_dir) / lang / relative_path

                    # Skip if exists and not overwrite
                    if output_path.exists() and not overwrite:
                        print(f"  [SKIP] Skipping {relative_path} [{lang.upper()}] (already exists)")
                        continue

                    # Create translation task (translate and save immediately)
                    task_info = {
                        'article_path': article_path,
                        'relative_path': relative_path,
                        'lang': lang,
                        'output_path': output_path,
                        'article_name': article_name,
                        'task': self.translator.translate_and_save(
                            en_content,
                            lang,
                            output_path,
                            session,
                            article_name
                        )
                    }
                    all_tasks.append(task_info)

            if not all_tasks:
                print("[OK] All articles already translated!")
                return

            print(f"[OK] Built {len(all_tasks)} translation tasks\n")

            # Get batch configuration
            batch_size = self.config.get('batch_size', 10)
            batch_delay = self.config.get('batch_delay', 2)
            total_batches = (len(all_tasks) + batch_size - 1) // batch_size

            # Execute tasks in batches
            print(f"[EXEC] Executing {len(all_tasks)} translation tasks in {total_batches} batches (batch_size={batch_size})...\n")
            print("   每个任务会在翻译完成后立即保存文件\n")

            results = []

            # Process each batch sequentially
            for i in range(0, len(all_tasks), batch_size):
                batch = all_tasks[i:i + batch_size]
                batch_num = i // batch_size + 1

                print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} tasks)...")

                # Execute batch in parallel
                batch_results = await asyncio.gather(
                    *[t['task'] for t in batch],
                    return_exceptions=True
                )
                results.extend(batch_results)

                # Progress update
                completed = i + len(batch)
                print(f"✅ Completed {completed}/{len(all_tasks)} tasks")

                # Delay between batches (except after last batch)
                if i + batch_size < len(all_tasks):
                    print(f"⏳ Waiting {batch_delay}s before next batch...")
                    await asyncio.sleep(batch_delay)

            # Collect statistics and failed translations
            print("\n[STATS] Collecting statistics...\n")
            stats = {
                'total': len(all_tasks),
                'success': 0,
                'failed': 0
            }

            failed_translations = []

            for task_info, result in zip(all_tasks, results):
                relative_path = task_info['relative_path']
                lang = task_info['lang']
                article_name = task_info['article_name']

                # Check if task succeeded (result is True) or failed
                if result is True:
                    stats['success'] += 1
                elif isinstance(result, Exception):
                    error_msg = f"{type(result).__name__}: {str(result)}"
                    print(f"  [ERROR] [{lang.upper()}] {relative_path} - Exception: {type(result).__name__}")
                    stats['failed'] += 1

                    # Record failed translation
                    failed_translations.append({
                        'article': str(relative_path),
                        'article_name': article_name,
                        'language': lang,
                        'language_name': self.translator.lang_names.get(lang, lang),
                        'error': error_msg,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                else:
                    # result is False
                    stats['failed'] += 1

                    # Record failed translation
                    failed_translations.append({
                        'article': str(relative_path),
                        'article_name': article_name,
                        'language': lang,
                        'language_name': self.translator.lang_names.get(lang, lang),
                        'error': 'Translation failed',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

            # Save failed translations to log files
            if failed_translations:
                self._save_failed_translations(failed_translations)

        # Print summary
        print("\n" + "=" * 60)
        print("[STATS] TRANSLATION COMPLETE")
        print("=" * 60)
        print(f"Total tasks:      {stats['total']}")
        print(f"[OK] Successful:      {stats['success']}")
        print(f"[FAIL] Failed:        {stats['failed']}")
        if stats['total'] > 0:
            print(f"Success rate:     {stats['success'] / stats['total'] * 100:.1f}%")
        print("=" * 60 + "\n")


def main():
    """Main function"""
    # Force unbuffered output
    import sys
    sys.stdout.reconfigure(line_buffering=True)

    print("[DEBUG] Starting...", flush=True)

    parser = argparse.ArgumentParser(description='Translate MDX articles to multiple languages')
    parser.add_argument('--test', action='store_true', help='Test mode (process only 2 articles)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing translations')
    parser.add_argument('--lang', type=str, default=None, help='Target languages (comma-separated, e.g., es,pt,ru)')

    args = parser.parse_args()
    print(f"[DEBUG] Args: test={args.test}", flush=True)

    # Initialize manager
    manager = ArticleTranslationManager()

    if not manager.load_config():
        sys.exit(1)

    if not manager.initialize():
        sys.exit(1)

    # Determine target languages
    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
    else:
        target_langs = manager.config.get('languages', ['es', 'pt', 'ru'])

    print(f"[LANG] Target languages: {', '.join(target_langs)}")

    # Run translation
    asyncio.run(manager.translate_all_articles(
        target_langs=target_langs,
        test_mode=args.test,
        overwrite=args.overwrite
    ))


if __name__ == '__main__':
    main()
