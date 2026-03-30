#!/usr/bin/env python3
"""
Enhanced Translation Script with Validation and Retry Logic
Handles translation quality issues automatically
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional


class EnhancedTranslator:
    """Enhanced translator with validation and retry"""

    def __init__(self, config_file: str):
        self.config = self._load_config(config_file)
        self.max_retries = self.config.get('max_retries', 3)
        self.retry_delay = self.config.get('retry_delay', 5)
        self.use_value_extraction = self.config.get('use_value_extraction', False)

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_translation(self, en_file: str, target_file: str, lang_code: str) -> Tuple[bool, List[str]]:
        """Validate translation file"""
        issues = []

        try:
            with open(en_file, 'r', encoding='utf-8') as f:
                en_data = json.load(f)
            with open(target_file, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
        except Exception as e:
            return False, [f"Failed to load files: {str(e)}"]

        # Check 1: Field count
        en_count = self._count_values(en_data)
        target_count = self._count_values(target_data)
        if en_count != target_count:
            issues.append(f"Field count mismatch: EN={en_count}, {lang_code}={target_count}")

        # Check 2: Empty fields
        empty_fields = self._find_empty_fields(target_data)
        if empty_fields:
            issues.append(f"Found {len(empty_fields)} empty fields")

        # Check 3: FAQ structure
        if not self._check_faq_structure(target_data):
            issues.append("FAQ structure corrupted (Q/A mismatch)")

        # Check 4: Table structure
        if not self._check_table_structure(target_data):
            issues.append("Table structure corrupted")

        return len(issues) == 0, issues

    def _count_values(self, obj) -> int:
        """Count total values"""
        count = 0
        if isinstance(obj, dict):
            for v in obj.values():
                count += self._count_values(v)
        elif isinstance(obj, list):
            for item in obj:
                count += self._count_values(item)
        else:
            count += 1
        return count

    def _find_empty_fields(self, obj, path="") -> List[str]:
        """Find empty fields"""
        empty = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                empty.extend(self._find_empty_fields(v, new_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                empty.extend(self._find_empty_fields(item, new_path))
        elif obj == "":
            empty.append(path)
        return empty

    def _check_faq_structure(self, data) -> bool:
        """Check FAQ structure"""
        if 'faq' not in data or 'questions' not in data['faq']:
            return True

        for q in data['faq']['questions']:
            if 'question' not in q or 'answer' not in q:
                return False
            if not q.get('question') or not q.get('answer'):
                return False

        return True

    def _check_table_structure(self, data) -> bool:
        """Check table structure"""
        if 'modules' not in data:
            return True

        for module_data in data['modules'].values():
            if isinstance(module_data, dict) and 'columns' in module_data:
                if not isinstance(module_data.get('columns'), list):
                    return False
                if not isinstance(module_data.get('rows'), list):
                    return False
                if len(module_data['columns']) == 0:
                    return False

        return True

    def translate_with_retry(self, en_file: str, target_lang: str, output_file: str) -> bool:
        """Translate with automatic retry on validation failure"""
        print(f"\n{'='*70}")
        print(f"TRANSLATING: {target_lang.upper()}")
        print(f"{'='*70}")

        for attempt in range(1, self.max_retries + 1):
            print(f"\n[ATTEMPT {attempt}/{self.max_retries}]")

            # Run translation (placeholder - actual implementation depends on your translator)
            success = self._run_translation(en_file, target_lang, output_file)
            if not success:
                print(f"[FAIL] Translation failed")
                continue

            # Validate translation
            is_valid, issues = self.validate_translation(en_file, output_file, target_lang)

            if is_valid:
                print(f"[SUCCESS] Translation validated successfully")
                return True
            else:
                print(f"[FAIL] Validation failed:")
                for issue in issues:
                    print(f"  - {issue}")

                if attempt < self.max_retries:
                    print(f"[RETRY] Waiting {self.retry_delay}s before retry...")
                    time.sleep(self.retry_delay)

        print(f"\n[FAILED] Translation failed after {self.max_retries} attempts")
        return False

    def _run_translation(self, en_file: str, target_lang: str, output_file: str) -> bool:
        """Run actual translation (to be implemented)"""
        # This is a placeholder - implement based on your translator
        print(f"[TRANSLATE] Translating to {target_lang}...")
        return True


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced_translator.py <config_file> [--validate-only]")
        sys.exit(1)

    config_file = sys.argv[1]
    validate_only = "--validate-only" in sys.argv

    translator = EnhancedTranslator(config_file)

    if validate_only:
        # Validate existing translations
        en_file = "src/locales/en.json"
        for lang in ['pt', 'fr', 'th', 'es', 'ru', 'id', 'ja']:
            target_file = f"src/locales/{lang}.json"
            is_valid, issues = translator.validate_translation(en_file, target_file, lang)
            status = "PASS" if is_valid else "FAIL"
            print(f"[{status}] {lang.upper()}")
            if issues:
                for issue in issues:
                    print(f"      {issue}")
    else:
        # Translate with retry
        print("Translation with retry not yet implemented")
        print("Use --validate-only to validate existing translations")


if __name__ == "__main__":
    main()
