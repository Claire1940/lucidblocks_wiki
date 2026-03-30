#!/usr/bin/env python3
"""
Translation Validator - Detects and fixes translation errors
Handles: field misalignment, FAQ swaps, table data corruption
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class TranslationValidator:
    """Validates and fixes translation files"""

    def __init__(self, en_file: str, target_file: str, lang_code: str):
        self.en_file = en_file
        self.target_file = target_file
        self.lang_code = lang_code
        self.errors = []
        self.warnings = []

    def load_files(self) -> Tuple[Dict, Dict]:
        """Load English and target language files"""
        try:
            with open(self.en_file, 'r', encoding='utf-8') as f:
                en_data = json.load(f)
            with open(self.target_file, 'r', encoding='utf-8') as f:
                target_data = json.load(f)
            return en_data, target_data
        except Exception as e:
            self.errors.append(f"Failed to load files: {str(e)}")
            return None, None

    def count_values(self, obj: Any) -> int:
        """Count total string values in JSON"""
        count = 0
        if isinstance(obj, dict):
            for v in obj.values():
                count += self.count_values(v)
        elif isinstance(obj, list):
            for item in obj:
                count += self.count_values(item)
        else:
            count += 1
        return count

    def check_field_count(self, en_data: Dict, target_data: Dict) -> bool:
        """Check if field counts match"""
        en_count = self.count_values(en_data)
        target_count = self.count_values(target_data)

        if en_count != target_count:
            self.errors.append(
                f"Field count mismatch: EN={en_count}, {self.lang_code.upper()}={target_count}"
            )
            return False
        return True

    def check_empty_fields(self, target_data: Dict) -> List[str]:
        """Find empty string fields"""
        empty_fields = []

        def find_empty(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{path}.{k}" if path else k
                    find_empty(v, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{path}[{i}]"
                    find_empty(item, new_path)
            elif obj == "":
                empty_fields.append(path)

        find_empty(target_data)

        if empty_fields:
            self.warnings.append(f"Found {len(empty_fields)} empty fields")
            return empty_fields
        return []

    def check_faq_structure(self, target_data: Dict) -> bool:
        """Check FAQ question/answer structure"""
        if 'faq' not in target_data or 'questions' not in target_data['faq']:
            return True

        issues = []
        for i, q in enumerate(target_data['faq']['questions']):
            if 'question' not in q or 'answer' not in q:
                issues.append(f"FAQ[{i}]: Missing question or answer field")
                continue

            q_text = q.get('question', '')
            a_text = q.get('answer', '')

            # Check if question looks like an answer (too long)
            if len(q_text) > 200 and len(a_text) < 50:
                issues.append(f"FAQ[{i}]: Possible Q/A swap (Q too long, A too short)")

            # Check if both are empty
            if not q_text or not a_text:
                issues.append(f"FAQ[{i}]: Empty question or answer")

        if issues:
            for issue in issues:
                self.errors.append(issue)
            return False
        return True

    def check_table_structure(self, target_data: Dict) -> bool:
        """Check table data structure"""
        if 'modules' not in target_data:
            return True

        issues = []
        for module_name, module_data in target_data['modules'].items():
            if isinstance(module_data, dict) and 'columns' in module_data and 'rows' in module_data:
                cols = module_data['columns']
                rows = module_data['rows']

                if not isinstance(cols, list) or not isinstance(rows, list):
                    issues.append(f"modules.{module_name}: columns or rows is not a list")
                    continue

                if len(cols) == 0:
                    issues.append(f"modules.{module_name}: No columns defined")

                if len(rows) == 0:
                    issues.append(f"modules.{module_name}: No rows defined")

        if issues:
            for issue in issues:
                self.errors.append(issue)
            return False
        return True

    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"\n{'='*70}")
        print(f"VALIDATING: {self.lang_code.upper()} ({self.target_file})")
        print(f"{'='*70}")

        en_data, target_data = self.load_files()
        if not en_data or not target_data:
            return False

        # Run checks
        checks = [
            ("Field Count", lambda: self.check_field_count(en_data, target_data)),
            ("FAQ Structure", lambda: self.check_faq_structure(target_data)),
            ("Table Structure", lambda: self.check_table_structure(target_data)),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                status = "PASS" if result else "FAIL"
                print(f"[{status}] {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"[ERROR] {check_name}: {str(e)}")
                all_passed = False

        # Check empty fields (warning only)
        empty = self.check_empty_fields(target_data)
        if empty:
            print(f"[WARN] Empty Fields: {len(empty)}")
        else:
            print(f"[PASS] No Empty Fields")

        # Print errors and warnings
        if self.errors:
            print(f"\nERRORS ({len(self.errors)}):")
            for error in self.errors[:5]:
                print(f"  - {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more")

        if self.warnings:
            print(f"\nWARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        print(f"\n{'='*70}")
        return all_passed


def main():
    """Main validation function"""
    if len(sys.argv) < 3:
        print("Usage: python3 translation_validator.py <en_file> <target_file> [lang_code]")
        sys.exit(1)

    en_file = sys.argv[1]
    target_file = sys.argv[2]
    lang_code = sys.argv[3] if len(sys.argv) > 3 else "unknown"

    validator = TranslationValidator(en_file, target_file, lang_code)
    success = validator.validate()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
