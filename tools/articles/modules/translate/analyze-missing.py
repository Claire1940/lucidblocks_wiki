#!/usr/bin/env python3
"""
Analyze missing translations and create failed_translations.json
"""

import json
from pathlib import Path
from datetime import datetime

# Languages to check
LANGUAGES = ['ar', 'de', 'es', 'fr', 'ja', 'ko', 'pt', 'ru', 'th', 'tr', 'vi', 'zh']

LANG_NAMES = {
    'ar': 'Arabic',
    'de': 'German',
    'es': 'Spanish',
    'fr': 'French',
    'ja': 'Japanese',
    'ko': 'Korean',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'th': 'Thai',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'zh': 'Chinese'
}

def main():
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent.parent.parent
    content_dir = project_root / 'src' / 'content'

    # Find all English articles
    en_dir = content_dir / 'en'
    en_articles = list(en_dir.glob('**/*.mdx'))

    print(f"[INFO] Found {len(en_articles)} English articles\n")

    # Get relative paths
    en_relative_paths = set()
    for article in en_articles:
        rel_path = article.relative_to(en_dir)
        en_relative_paths.add(rel_path)

    # Check each language
    failed_translations = []

    for lang in LANGUAGES:
        lang_dir = content_dir / lang

        if not lang_dir.exists():
            print(f"[WARN] [{lang.upper()}] Directory not found")
            continue

        # Find translated articles
        translated = set()
        for article in lang_dir.glob('**/*.mdx'):
            rel_path = article.relative_to(lang_dir)
            translated.add(rel_path)

        # Find missing articles
        missing = en_relative_paths - translated

        print(f"[{lang.upper()}] {len(translated)}/{len(en_articles)} - Missing: {len(missing)}")

        # Add to failed translations
        for rel_path in sorted(missing):
            article_name = rel_path.stem
            failed_translations.append({
                'article': str(rel_path),
                'article_name': article_name,
                'language': lang,
                'language_name': LANG_NAMES[lang],
                'error': 'Translation not found',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

    # Save to JSON
    output_file = project_root / 'tools' / 'articles' / 'logs' / 'failed_translations.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(failed_translations, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVE] Saved {len(failed_translations)} failed translations to:")
    print(f"   {output_file}")

    # Print summary by language
    print("\n[STATS] Summary:")
    lang_counts = {}
    for item in failed_translations:
        lang = item['language']
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    for lang in sorted(lang_counts.keys()):
        print(f"   [{lang.upper()}] {lang_counts[lang]} missing articles")

if __name__ == '__main__':
    main()
