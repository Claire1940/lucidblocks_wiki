#!/usr/bin/env python3
"""
Retry failed translations from failed_translations.json
Translates only the missing articles for each language.

Usage:
    python retry-failed.py [--test] [--lang es,pt,ru]
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


class FailedTranslationRetry:
    """Manager for retrying failed translations"""

    def __init__(self, config_path: str = None):
        """Initialize retry manager"""
        if config_path is None:
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
            print(f"[FAIL] Error loading configuration: {str(e)}")
            return False

    def initialize(self) -> bool:
        """Initialize translator"""
        try:
            self.translator = MDXTranslator(self.config)
            self.base_dir = self.config.get('output_dir', 'src/content/')
            print("[OK] Translator initialized")
            return True
        except Exception as e:
            print(f"[FAIL] Error initializing translator: {str(e)}")
            return False

    def load_failed_translations(self) -> List[Dict]:
        """Load failed translations from JSON file"""
        # Get the project root directory
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent.parent
        failed_file = project_root / 'tools' / 'articles' / 'logs' / 'failed_translations.json'

        if not failed_file.exists():
            print(f"[FAIL] Failed translations file not found: {failed_file}")
            return []

        try:
            with open(failed_file, 'r', encoding='utf-8') as f:
                failed = json.load(f)
            print(f"[OK] Loaded {len(failed)} failed translations from {failed_file}")
            return failed
        except Exception as e:
            print(f"[FAIL] Error loading failed translations: {str(e)}")
            return []

    async def retry_failed_translations(
        self,
        target_langs: List[str] = None,
        test_mode: bool = False
    ):
        """
        Retry translating failed articles

        Args:
            target_langs: List of target language codes (None = all)
            test_mode: If True, only process first 10 failed translations
        """
        print("\n" + "=" * 60)
        print("[RETRY] RETRYING FAILED TRANSLATIONS")
        print("=" * 60 + "\n")

        # Load failed translations
        all_failed_translations = self.load_failed_translations()

        if not all_failed_translations:
            print("[FAIL] No failed translations to retry")
            return

        # Filter by language if specified
        if target_langs:
            filtered_failed = [
                item for item in all_failed_translations
                if item['language'] in target_langs
            ]
            print(f"[TARGET] Filtered to {len(filtered_failed)} translations for languages: {', '.join(target_langs)}")
        else:
            filtered_failed = all_failed_translations

        if not filtered_failed:
            print("[FAIL] No failed translations found for specified languages")
            return

        # Test mode - limit to first 10, but keep reference to unprocessed
        if test_mode:
            failed_translations = filtered_failed[:10]
            unprocessed_translations = all_failed_translations[10:]  # Keep unprocessed for later
            print(f"[TEST] TEST MODE: Processing only {len(failed_translations)} translations\n")
        else:
            failed_translations = filtered_failed
            unprocessed_translations = []

        # Group by language for summary
        lang_counts = {}
        for item in failed_translations:
            lang = item['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        print(f"[INFO] Total failed translations to retry: {len(failed_translations)}")
        print(f"[STATS] By language:")
        for lang in sorted(lang_counts.keys()):
            print(f"   [{lang.upper()}] {lang_counts[lang]} articles")
        print()

        # Build translation tasks
        async with aiohttp.ClientSession() as session:
            all_tasks = []

            print("[BUILD] Building retry tasks...")

            for item in failed_translations:
                article_path_str = item['article']
                lang = item['language']
                article_name = item['article_name']

                # Build paths
                en_dir = Path(self.base_dir) / 'en'
                en_article_path = en_dir / article_path_str

                # Check if English article exists
                if not en_article_path.exists():
                    print(f"  [WARN] Skipping {article_path_str} [{lang.upper()}] - English source not found")
                    continue

                # Read English content
                try:
                    with open(en_article_path, 'r', encoding='utf-8') as f:
                        en_content = f.read()
                except Exception as e:
                    print(f"  [FAIL] Error reading {en_article_path}: {str(e)}")
                    continue

                # Output path
                output_path = Path(self.base_dir) / lang / article_path_str

                # Create translation task
                task_info = {
                    'article_path': en_article_path,
                    'relative_path': Path(article_path_str),
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
                print("[FAIL] No valid tasks to retry!")
                return

            print(f"[OK] Built {len(all_tasks)} retry tasks\n")

            # Execute all tasks in parallel
            print(f"[EXEC] Executing {len(all_tasks)} translation tasks in parallel...\n")
            print("   每个任务会在翻译完成后立即保存文件\n")

            results = await asyncio.gather(*[t['task'] for t in all_tasks], return_exceptions=True)

            # Collect statistics and still-failed translations
            print("\n[STATS] Collecting statistics...\n")
            stats = {
                'total': len(all_tasks),
                'success': 0,
                'failed': 0
            }

            still_failed = []

            for task_info, result in zip(all_tasks, results):
                relative_path = task_info['relative_path']
                lang = task_info['lang']
                article_name = task_info['article_name']

                # Check if task succeeded (result is True) or failed
                if result is True:
                    stats['success'] += 1
                elif isinstance(result, Exception):
                    error_msg = f"{type(result).__name__}: {str(result)}"
                    print(f"  [FAIL] [{lang.upper()}] {relative_path} - Exception: {type(result).__name__}")
                    stats['failed'] += 1

                    # Record still-failed translation
                    still_failed.append({
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

                    # Record still-failed translation
                    still_failed.append({
                        'article': str(relative_path),
                        'article_name': article_name,
                        'language': lang,
                        'language_name': self.translator.lang_names.get(lang, lang),
                        'error': 'Translation failed',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

            # Update failed_translations.json
            # In test mode, merge still-failed with unprocessed translations
            all_remaining_failed = still_failed + unprocessed_translations

            if all_remaining_failed:
                self._update_failed_translations(all_remaining_failed)
                if test_mode and unprocessed_translations:
                    print(f"\n[SAVE] Saved {len(still_failed)} still-failed + {len(unprocessed_translations)} unprocessed = {len(all_remaining_failed)} total")
            else:
                # All succeeded and no unprocessed - clear the failed translations file
                self._clear_failed_translations()

        # Print summary
        print("\n" + "=" * 60)
        print("[STATS] RETRY COMPLETE")
        print("=" * 60)
        print(f"Total retry tasks:  {stats['total']}")
        print(f"[OK] Successful:      {stats['success']}")
        print(f"[FAIL] Still failed:    {stats['failed']}")
        if stats['total'] > 0:
            print(f"Success rate:       {stats['success'] / stats['total'] * 100:.1f}%")
        print("=" * 60 + "\n")

    def _update_failed_translations(self, still_failed: List[Dict]):
        """Update failed_translations.json with still-failed items"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent.parent
        failed_file = project_root / 'tools' / 'articles' / 'logs' / 'failed_translations.json'

        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump(still_failed, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVE] Updated failed_translations.json with {len(still_failed)} still-failed translations")
        except Exception as e:
            print(f"\n[WARN] Failed to update failed_translations.json: {str(e)}")

    def _clear_failed_translations(self):
        """Clear failed_translations.json (all retries succeeded)"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent.parent.parent
        failed_file = project_root / 'tools' / 'articles' / 'logs' / 'failed_translations.json'

        try:
            with open(failed_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print(f"\n[OK] All translations succeeded! Cleared failed_translations.json")
        except Exception as e:
            print(f"\n[WARN] Failed to clear failed_translations.json: {str(e)}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Retry failed translations')
    parser.add_argument('--test', action='store_true', help='Test mode (process only 10 failed translations)')
    parser.add_argument('--lang', type=str, default=None, help='Target languages (comma-separated, e.g., es,pt,ru)')

    args = parser.parse_args()

    # Initialize manager
    manager = FailedTranslationRetry()

    if not manager.load_config():
        sys.exit(1)

    if not manager.initialize():
        sys.exit(1)

    # Determine target languages
    target_langs = None
    if args.lang:
        target_langs = [lang.strip() for lang in args.lang.split(',')]
        print(f"[LANG] Target languages: {', '.join(target_langs)}")

    # Run retry
    asyncio.run(manager.retry_failed_translations(
        target_langs=target_langs,
        test_mode=args.test
    ))


if __name__ == '__main__':
    main()
