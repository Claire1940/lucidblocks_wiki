#!/usr/bin/env python3
"""
Enhanced Translation Validator - 增强版翻译验证器
添加更多质量检查
"""

import json
from typing import Tuple, Optional, List, Dict, Any


class EnhancedTranslationValidator:
    """增强版翻译验证器"""

    @staticmethod
    def validate_json_format(content: str) -> Tuple[bool, Optional[str]]:
        """验证 JSON 格式"""
        try:
            json.loads(content)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"JSON 格式错误: {str(e)}"

    @staticmethod
    def validate_structure(original: dict, translated: dict) -> Tuple[bool, Optional[str]]:
        """验证结构完整性"""
        def get_keys_recursive(obj, prefix=''):
            keys = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key_path = f"{prefix}.{k}" if prefix else k
                    keys.append(key_path)
                    keys.extend(get_keys_recursive(v, key_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    keys.extend(get_keys_recursive(item, f"{prefix}[{i}]"))
            return keys

        original_keys = set(get_keys_recursive(original))
        translated_keys = set(get_keys_recursive(translated))

        if original_keys != translated_keys:
            missing = original_keys - translated_keys
            extra = translated_keys - original_keys
            error_msg = []
            if missing:
                error_msg.append(f"缺失键: {list(missing)[:5]}")
            if extra:
                error_msg.append(f"多余键: {list(extra)[:5]}")
            return False, "; ".join(error_msg)

        return True, None

    @staticmethod
    def validate_size(original: dict, translated: dict) -> Tuple[bool, Optional[str]]:
        """验证文件大小合理性（±50%）"""
        original_str = json.dumps(original, ensure_ascii=False)
        translated_str = json.dumps(translated, ensure_ascii=False)

        original_size = len(original_str)
        translated_size = len(translated_str)

        ratio = translated_size / original_size

        if ratio < 0.5 or ratio > 1.5:
            return False, f"大小异常: 原始 {original_size} 字符, 翻译后 {translated_size} 字符 (比例 {ratio:.2f})"

        return True, None

    @staticmethod
    def validate_no_empty_values(data: dict, path: str = "") -> Tuple[bool, Optional[List[str]]]:
        """
        检查空值

        Args:
            data: 要检查的数据
            path: 当前路径（用于递归）

        Returns:
            (是否通过, 空字段列表)
        """
        empty_fields = []

        def check_recursive(obj: Any, current_path: str):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    check_recursive(value, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    check_recursive(item, new_path)
            elif isinstance(obj, str):
                if obj.strip() == "":
                    empty_fields.append(current_path)
            elif obj is None:
                empty_fields.append(current_path)

        check_recursive(data, path)

        if empty_fields:
            return False, empty_fields
        return True, None

    @staticmethod
    def validate_protected_terms(
        original: dict,
        translated: dict,
        protected_terms: List[str]
    ) -> Tuple[bool, Optional[List[str]]]:
        """
        检查专有名词是否被错误翻译

        Args:
            original: 原始数据
            translated: 翻译后的数据
            protected_terms: 需要保护的专有名词列表

        Returns:
            (是否通过, 违规列表)
        """
        original_str = json.dumps(original, ensure_ascii=False)
        translated_str = json.dumps(translated, ensure_ascii=False)

        violations = []

        for term in protected_terms:
            # 检查原文中有，但译文中没有的情况
            original_count = original_str.count(term)
            translated_count = translated_str.count(term)

            if original_count > 0 and translated_count == 0:
                violations.append(f"{term} (原文出现 {original_count} 次，译文中消失)")
            elif original_count > 0 and translated_count < original_count * 0.8:
                # 允许一些差异，但如果减少超过 20% 就警告
                violations.append(f"{term} (原文 {original_count} 次，译文仅 {translated_count} 次)")

        if violations:
            return False, violations
        return True, None

    @staticmethod
    def validate_faq_structure(data: dict) -> Tuple[bool, Optional[List[str]]]:
        """
        检查 FAQ 结构是否正确

        Args:
            data: 要检查的数据

        Returns:
            (是否通过, 错误列表)
        """
        if 'faq' not in data:
            return True, None

        errors = []
        faq = data['faq']

        # 检查必需字段
        required_fields = ['title', 'titleHighlight', 'subtitle', 'questions']
        for field in required_fields:
            if field not in faq:
                errors.append(f"FAQ 缺少必需字段: {field}")

        # 检查 questions 数组
        if 'questions' in faq:
            questions = faq['questions']

            if not isinstance(questions, list):
                errors.append("FAQ questions 应该是数组")
            else:
                for i, q in enumerate(questions):
                    if not isinstance(q, dict):
                        errors.append(f"FAQ 问题 #{i+1} 应该是对象")
                        continue

                    question = q.get('question', '')
                    answer = q.get('answer', '')

                    # 检查是否为空
                    if not question or not answer:
                        errors.append(f"FAQ #{i+1} 问题或答案为空")
                        continue

                    # 启发式检查：问题应该以 ? 或 ？ 结尾
                    if not (question.endswith('?') or question.endswith('？')):
                        errors.append(f"FAQ #{i+1} 问题格式异常（不以问号结尾）: {question[:50]}...")

                    # 答案不应该以 ? 或 ？ 结尾（可能是问答互换）
                    if answer.endswith('?') or answer.endswith('？'):
                        errors.append(f"FAQ #{i+1} 答案格式异常（以问号结尾，可能与问题互换）: {answer[:50]}...")

                    # 检查长度合理性：问题通常比答案短
                    if len(question) > len(answer) * 1.5:
                        errors.append(f"FAQ #{i+1} 问题比答案长很多（可能互换）: Q={len(question)} A={len(answer)}")

        if errors:
            return False, errors
        return True, None

    @staticmethod
    def validate_all(
        original: dict,
        translated: dict,
        protected_terms: List[str] = None
    ) -> Dict[str, Any]:
        """
        执行所有验证

        Args:
            original: 原始数据
            translated: 翻译后的数据
            protected_terms: 需要保护的专有名词列表

        Returns:
            验证结果字典
        """
        results = {
            'passed': True,
            'checks': {}
        }

        # 1. 结构检查
        valid, error = EnhancedTranslationValidator.validate_structure(original, translated)
        results['checks']['structure'] = {
            'passed': valid,
            'error': error
        }
        if not valid:
            results['passed'] = False

        # 2. 大小检查
        valid, error = EnhancedTranslationValidator.validate_size(original, translated)
        results['checks']['size'] = {
            'passed': valid,
            'error': error
        }
        if not valid:
            results['passed'] = False

        # 3. 空值检查
        valid, empty_fields = EnhancedTranslationValidator.validate_no_empty_values(translated)
        results['checks']['empty_values'] = {
            'passed': valid,
            'empty_fields': empty_fields or [],
            'count': len(empty_fields) if empty_fields else 0
        }
        if not valid:
            results['passed'] = False

        # 4. 专有名词检查
        if protected_terms:
            valid, violations = EnhancedTranslationValidator.validate_protected_terms(
                original, translated, protected_terms
            )
            results['checks']['protected_terms'] = {
                'passed': valid,
                'violations': violations or [],
                'count': len(violations) if violations else 0
            }
            if not valid:
                results['passed'] = False

        # 5. FAQ 结构检查
        valid, errors = EnhancedTranslationValidator.validate_faq_structure(translated)
        results['checks']['faq_structure'] = {
            'passed': valid,
            'errors': errors or [],
            'count': len(errors) if errors else 0
        }
        if not valid:
            results['passed'] = False

        return results


def test_validator():
    """测试验证器"""
    print("=== 测试 EnhancedTranslationValidator ===\n")

    # 测试数据
    original = {
        "common": {
            "home": "Home",
            "more": "More"
        },
        "faq": {
            "title": "Frequently Asked",
            "titleHighlight": "Questions",
            "subtitle": "Everything you need to know",
            "questions": [
                {
                    "question": "What is WWE 2K26?",
                    "answer": "WWE 2K26 is a wrestling game."
                }
            ]
        }
    }

    # 测试 1: 正常翻译
    print("测试 1: 正常翻译")
    translated_good = {
        "common": {
            "home": "Inicio",
            "more": "Más"
        },
        "faq": {
            "title": "Preguntas",
            "titleHighlight": "Frecuentes",
            "subtitle": "Todo lo que necesitas saber",
            "questions": [
                {
                    "question": "¿Qué es WWE 2K26?",
                    "answer": "WWE 2K26 es un juego de lucha libre."
                }
            ]
        }
    }

    results = EnhancedTranslationValidator.validate_all(
        original, translated_good, protected_terms=['WWE 2K26']
    )
    print(f"  通过: {results['passed']}")
    print(f"  结果: {json.dumps(results, indent=2, ensure_ascii=False)}")
    print()

    # 测试 2: FAQ 问答互换
    print("测试 2: FAQ 问答互换")
    translated_bad_faq = {
        "common": {
            "home": "Inicio",
            "more": "Más"
        },
        "faq": {
            "title": "Preguntas",
            "titleHighlight": "Frecuentes",
            "subtitle": "Todo lo que necesitas saber",
            "questions": [
                {
                    "question": "WWE 2K26 es un juego de lucha libre.",  # 答案变成了问题
                    "answer": "¿Qué es WWE 2K26?"  # 问题变成了答案
                }
            ]
        }
    }

    results = EnhancedTranslationValidator.validate_all(
        original, translated_bad_faq, protected_terms=['WWE 2K26']
    )
    print(f"  通过: {results['passed']}")
    print(f"  FAQ 检查: {results['checks']['faq_structure']}")
    print()

    # 测试 3: 空值
    print("测试 3: 空值检查")
    translated_empty = {
        "common": {
            "home": "",  # 空值
            "more": "Más"
        },
        "faq": {
            "title": "Preguntas",
            "titleHighlight": "Frecuentes",
            "subtitle": "Todo lo que necesitas saber",
            "questions": []
        }
    }

    results = EnhancedTranslationValidator.validate_all(
        original, translated_empty, protected_terms=['WWE 2K26']
    )
    print(f"  通过: {results['passed']}")
    print(f"  空值检查: {results['checks']['empty_values']}")
    print()

    # 测试 4: 专有名词被翻译
    print("测试 4: 专有名词被翻译")
    translated_bad_terms = {
        "common": {
            "home": "Inicio",
            "more": "Más"
        },
        "faq": {
            "title": "Preguntas",
            "titleHighlight": "Frecuentes",
            "subtitle": "Todo lo que necesitas saber",
            "questions": [
                {
                    "question": "¿Qué es WWE 2K26?",
                    "answer": "Lucha Libre 2K26 es un juego."  # WWE 被翻译了
                }
            ]
        }
    }

    results = EnhancedTranslationValidator.validate_all(
        original, translated_bad_terms, protected_terms=['WWE 2K26']
    )
    print(f"  通过: {results['passed']}")
    print(f"  专有名词检查: {results['checks']['protected_terms']}")
    print()


if __name__ == "__main__":
    test_validator()
