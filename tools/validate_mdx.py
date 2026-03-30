#!/usr/bin/env python3
"""
MDX 格式验证脚本

用于检查 MDX 文件中的标签匹配问题，包括：
- 未闭合的标签
- 不匹配的开始/结束标签
- 意外的结束标签

支持跳过代码块、注释、导入语句等区域。
"""

import re
import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass


@dataclass
class Tag:
    """标签信息"""
    name: str
    line: int
    column: int
    is_closing: bool
    is_self_closing: bool
    content: str  # 原始标签内容


@dataclass
class ValidationError:
    """验证错误"""
    file_path: str
    error_type: str  # 'unclosed_tag', 'mismatched_tags', 'unexpected_closing_tag', 'improper_self_closing_tag', 'missing_faq', 'excessive_whitespace'
    tag_name: str
    line: int
    column: int
    message: str
    opening_tag: Optional[Tag] = None
    closing_tag: Optional[Tag] = None


class SkipZoneDetector:
    """检测应该跳过解析的区域（代码块、注释、导入等）"""

    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        self.skip_zones: List[Tuple[int, int]] = []  # (start_line, end_line)

    def detect_all_skip_zones(self) -> List[Tuple[int, int]]:
        """检测所有需要跳过的区域"""
        self.skip_zones = []
        self.detect_imports()
        self.detect_exports()
        self.detect_code_blocks()
        self.detect_html_comments()
        return self.skip_zones

    def detect_imports(self):
        """检测导入语句"""
        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') and ' from ' in stripped:
                self.skip_zones.append((i, i))

    def detect_exports(self):
        """检测 export 语句块"""
        in_export = False
        start_line = 0
        brace_depth = 0

        for i, line in enumerate(self.lines, 1):
            stripped = line.strip()

            if not in_export and stripped.startswith('export const '):
                in_export = True
                start_line = i
                brace_depth = 0

            if in_export:
                brace_depth += line.count('{') - line.count('}')
                if brace_depth <= 0 and (';' in line or '}' in line):
                    self.skip_zones.append((start_line, i))
                    in_export = False

    def detect_code_blocks(self):
        """检测代码块（``` 围栏）"""
        in_code_block = False
        start_line = 0

        for i, line in enumerate(self.lines, 1):
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    start_line = i
                else:
                    self.skip_zones.append((start_line, i))
                    in_code_block = False

    def detect_html_comments(self):
        """检测 HTML 注释"""
        comment_pattern = re.compile(r'<!--[\s\S]*?-->', re.MULTILINE)
        for match in comment_pattern.finditer(self.content):
            start_line = self.content[:match.start()].count('\n') + 1
            end_line = self.content[:match.end()].count('\n') + 1
            self.skip_zones.append((start_line, end_line))

    def should_skip_line(self, line_num: int) -> bool:
        """检查某行是否应该跳过"""
        for start, end in self.skip_zones:
            if start <= line_num <= end:
                return True
        return False


class TagExtractor:
    """提取 MDX 文件中的所有标签"""

    # HTML5 void elements（必须使用自闭合格式）
    VOID_ELEMENTS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
        'input', 'link', 'meta', 'source', 'track', 'wbr'
    }

    # 自闭合标签（不需要结束标签，包括 HTML void elements 和自定义组件）
    SELF_CLOSING_TAGS = {
        'img', 'br', 'hr', 'input', 'meta', 'link',
        'area', 'base', 'col', 'embed', 'source', 'track', 'wbr',
        'Checklist', 'YouTubeEmbed', 'FAQ'
    }

    def __init__(self, content: str, skip_detector: SkipZoneDetector, file_path: str = ""):
        self.content = content
        self.lines = content.split('\n')
        self.skip_detector = skip_detector
        self.file_path = file_path
        self.tags: List[Tag] = []
        self.errors: List[ValidationError] = []

    def extract_all_tags(self) -> List[Tag]:
        """提取所有标签"""
        self.tags = []

        i = 0
        while i < len(self.lines):
            line_num = i + 1
            line = self.lines[i]

            # 跳过应该忽略的行
            if self.skip_detector.should_skip_line(line_num):
                i += 1
                continue

            # 处理这一行中的所有标签
            self._extract_tags_from_line(line, line_num)
            i += 1

        return self.tags

    def _extract_tags_from_line(self, line: str, line_num: int):
        """从单行中提取标签"""
        # 首先检查不正确的自闭合标签格式
        self._check_improper_self_closing(line, line_num)

        # 跳过内联代码
        line = self._remove_inline_code(line)

        # 匹配所有标签
        # 自闭合标签: <Component />
        self_closing_pattern = r'<(\w+)(?:\s+[^>]*)?\s*/>'
        # 结束标签: </Component>
        closing_pattern = r'</(\w+)>'
        # 开始标签: <Component> 或 <Component prop="value">
        opening_pattern = r'<(\w+)(?:\s+[^>]*)?>'

        # 首先匹配自闭合标签
        for match in re.finditer(self_closing_pattern, line):
            tag_name = match.group(1)
            column = match.start() + 1
            self.tags.append(Tag(
                name=tag_name,
                line=line_num,
                column=column,
                is_closing=False,
                is_self_closing=True,
                content=match.group(0)
            ))

        # 移除已匹配的自闭合标签
        line = re.sub(self_closing_pattern, '', line)

        # 匹配结束标签
        for match in re.finditer(closing_pattern, line):
            tag_name = match.group(1)
            column = match.start() + 1
            self.tags.append(Tag(
                name=tag_name,
                line=line_num,
                column=column,
                is_closing=True,
                is_self_closing=False,
                content=match.group(0)
            ))

        # 匹配开始标签
        for match in re.finditer(opening_pattern, line):
            tag_name = match.group(1)
            # 跳过结束标签（已经匹配过了）
            if match.group(0).startswith('</'):
                continue
            # 跳过自闭合标签
            if match.group(0).endswith('/>'):
                continue

            column = match.start() + 1

            # 检查是否是自闭合标签类型
            is_self_closing = tag_name in self.SELF_CLOSING_TAGS

            self.tags.append(Tag(
                name=tag_name,
                line=line_num,
                column=column,
                is_closing=False,
                is_self_closing=is_self_closing,
                content=match.group(0)
            ))

    def _remove_inline_code(self, line: str) -> str:
        """移除行内代码（` ` 包裹的内容）"""
        # 简单处理：移除所有 ` ` 之间的内容
        return re.sub(r'`[^`]*`', '', line)

    def _check_improper_self_closing(self, line: str, line_num: int):
        """检测应该自闭合但格式不正确的标签"""
        # 先移除内联代码
        clean_line = self._remove_inline_code(line)

        # 匹配不带斜杠的 void element 标签
        # 格式: <tag> 或 <tag attr="value"> 但不是 <tag /> 或 <tag attr="value" />
        void_tags_pattern = '|'.join(self.VOID_ELEMENTS)
        pattern = rf'<({void_tags_pattern})(?:\s+[^>]*?)?\s*>(?!\s*/)'

        for match in re.finditer(pattern, clean_line, re.IGNORECASE):
            tag_name = match.group(1)
            # 计算原始行中的列位置
            column = match.start() + 1
            matched_text = match.group(0)

            # 检查是否确实不是自闭合格式
            if not matched_text.rstrip().endswith('/>'):
                self.errors.append(ValidationError(
                    file_path=self.file_path,
                    error_type='improper_self_closing_tag',
                    tag_name=tag_name,
                    line=line_num,
                    column=column,
                    message=f"Self-closing tag <{tag_name}> should use <{tag_name} /> format, not <{tag_name}>"
                ))


class TagValidator:
    """验证标签匹配"""

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.tag_stack: List[Tag] = []

    def validate_file(self, file_path: str, tags: List[Tag]) -> List[ValidationError]:
        """验证文件中的所有标签"""
        self.errors = []
        self.tag_stack = []

        for tag in tags:
            if tag.is_self_closing:
                # 自闭合标签，不需要处理
                continue
            elif tag.is_closing:
                # 结束标签，需要匹配开始标签
                self._handle_closing_tag(file_path, tag)
            else:
                # 开始标签，入栈
                self.tag_stack.append(tag)

        # 检查栈中是否还有未闭合的标签
        self._check_unclosed_tags(file_path)

        # 检查是否包含 FAQ 组件
        self._check_faq_presence(file_path, tags)

        # 检查是否有多余空格
        self._check_excessive_whitespace(file_path)

        return self.errors

    def _handle_closing_tag(self, file_path: str, closing_tag: Tag):
        """处理结束标签"""
        if not self.tag_stack:
            # 栈为空，出现了意外的结束标签
            self.errors.append(ValidationError(
                file_path=file_path,
                error_type='unexpected_closing_tag',
                tag_name=closing_tag.name,
                line=closing_tag.line,
                column=closing_tag.column,
                message=f"Unexpected closing tag </{closing_tag.name}>",
                closing_tag=closing_tag
            ))
            return

        opening_tag = self.tag_stack[-1]

        if opening_tag.name != closing_tag.name:
            # 标签不匹配
            self.errors.append(ValidationError(
                file_path=file_path,
                error_type='mismatched_tags',
                tag_name=opening_tag.name,
                line=opening_tag.line,
                column=opening_tag.column,
                message=f"Mismatched tags: <{opening_tag.name}> (line {opening_tag.line}) and </{closing_tag.name}> (line {closing_tag.line})",
                opening_tag=opening_tag,
                closing_tag=closing_tag
            ))
            # 移除开始标签（尝试继续验证）
            self.tag_stack.pop()
        else:
            # 匹配成功，出栈
            self.tag_stack.pop()

    def _check_unclosed_tags(self, file_path: str):
        """检查未闭合的标签"""
        for tag in self.tag_stack:
            self.errors.append(ValidationError(
                file_path=file_path,
                error_type='unclosed_tag',
                tag_name=tag.name,
                line=tag.line,
                column=tag.column,
                message=f"Expected a closing tag for <{tag.name}> ({tag.line}:{tag.column})",
                opening_tag=tag
            ))

    def _check_faq_presence(self, file_path: str, tags: List[Tag]):
        """检查文章是否包含 FAQ 组件"""
        # 读取文件内容并检查是否包含 "FAQ items" 字符串
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            has_faq = 'FAQ items' in content
        except Exception:
            has_faq = False

        if not has_faq:
            self.errors.append(ValidationError(
                file_path=file_path,
                error_type='missing_faq',
                tag_name='FAQ',
                line=0,
                column=0,
                message="缺少 FAQ 组件"
            ))

    def _check_excessive_whitespace(self, file_path: str):
        """检测文件中的多余空格、超长表格分隔线和重复表格分隔线"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            prev_is_separator = False
            prev_line_num = 0

            for i, line in enumerate(lines):
                line_length = len(line)
                is_separator = self._is_table_separator(line)

                # 检测超长行（超过 1000 字符）
                if line_length > 1000:
                    # 检查多余空格
                    if '  ' in line:  # 至少2个连续空格
                        # 计算可以节省的空格数
                        cleaned_line = re.sub(r' {2,}', ' ', line)
                        saved_chars = line_length - len(cleaned_line)

                        self.errors.append(ValidationError(
                            file_path=file_path,
                            error_type='excessive_whitespace',
                            tag_name='',
                            line=i + 1,
                            column=0,
                            message=f"行包含大量多余空格 (当前: {line_length:,} 字符, 可优化为: {len(cleaned_line):,} 字符, 节省: {saved_chars:,} 字符)"
                        ))

                    # 检查超长表格分隔线
                    elif is_separator:
                        # 估算合理长度（假设每列平均 10 个字符）
                        estimated_normal_length = 100
                        saved_chars = line_length - estimated_normal_length
                        saved_tokens = int(saved_chars * 0.25)

                        self.errors.append(ValidationError(
                            file_path=file_path,
                            error_type='excessive_whitespace',
                            tag_name='',
                            line=i + 1,
                            column=0,
                            message=f"表格分隔线异常长 (当前: {line_length:,} 字符, 预计可优化为: ~{estimated_normal_length} 字符, 节省: ~{saved_chars:,} 字符, ~{saved_tokens:,} tokens)"
                        ))

                # 检测重复的表格分隔线（新增）
                if is_separator and prev_is_separator:
                    self.errors.append(ValidationError(
                        file_path=file_path,
                        error_type='duplicate_table_separator',
                        tag_name='',
                        line=i + 1,
                        column=0,
                        message=f"检测到重复的表格分隔线（第 {prev_line_num} 行和第 {i+1} 行都是分隔线，应删除第 {i+1} 行）"
                    ))

                # 更新状态
                if is_separator:
                    prev_is_separator = True
                    prev_line_num = i + 1
                else:
                    prev_is_separator = False

        except Exception as e:
            # 静默处理文件读取错误
            pass

    def _is_table_separator(self, line: str) -> bool:
        """检测是否是表格分隔线"""
        stripped = line.strip()
        if not stripped.startswith('|') or not stripped.endswith('|'):
            return False
        content = stripped[1:-1]
        return all(c in '-| ' for c in content) and '-' in content


class ErrorReporter:
    """错误报告生成器"""

    def __init__(self, format_type: str = 'text'):
        self.format_type = format_type
        self.all_errors: List[ValidationError] = []
        self.validated_files: Set[str] = set()

    def add_file_errors(self, file_path: str, errors: List[ValidationError]):
        """添加文件的错误"""
        self.validated_files.add(file_path)
        self.all_errors.extend(errors)

    def print_report(self):
        """打印报告"""
        if self.format_type == 'json':
            self._print_json_report()
        else:
            self._print_text_report()

    def _print_text_report(self):
        """打印文本格式报告"""
        print("\n" + "=" * 58)
        print("MDX 格式验证报告")
        print("=" * 58 + "\n")

        # 按文件分组错误
        files_with_errors = {}
        for error in self.all_errors:
            if error.file_path not in files_with_errors:
                files_with_errors[error.file_path] = []
            files_with_errors[error.file_path].append(error)

        # 打印每个文件的错误
        for file_path in sorted(self.validated_files):
            if file_path in files_with_errors:
                print(f"✗ {file_path}")
                for error in files_with_errors[file_path]:
                    self._print_error(error)
                print()
            else:
                print(f"✓ {file_path}")

        # 打印统计信息
        print("-" * 58)
        print("统计信息:")
        print(f"  扫描文件: {len(self.validated_files)}")
        print(f"  通过验证: {len(self.validated_files) - len(files_with_errors)}")
        print(f"  错误文件: {len(files_with_errors)}")
        print(f"  总错误数: {len(self.all_errors)}")

        # 错误分类
        if self.all_errors:
            print("\n错误分类:")
            error_types = {}
            for error in self.all_errors:
                error_types[error.error_type] = error_types.get(error.error_type, 0) + 1

            type_names = {
                'unclosed_tag': '未闭合标签',
                'mismatched_tags': '标签不匹配',
                'unexpected_closing_tag': '意外的结束标签',
                'improper_self_closing_tag': '不正确的自闭合标签',
                'missing_faq': '缺少FAQ组件',
                'excessive_whitespace': '多余空格',
                'duplicate_table_separator': '重复表格分隔线'
            }

            for error_type, count in error_types.items():
                print(f"  - {type_names.get(error_type, error_type)}: {count}")

        print("=" * 58)

    def _print_error(self, error: ValidationError):
        """打印单个错误"""
        if error.error_type == 'unclosed_tag':
            print(f"  错误: 未闭合的标签 <{error.tag_name}>")
            print(f"  开始位置: 第 {error.line} 行, 第 {error.column} 列")
            print(f"  预期: 在文件末尾前找到 </{error.tag_name}>")

        elif error.error_type == 'mismatched_tags':
            print(f"  错误: 标签不匹配")
            print(f"  开始标签: <{error.opening_tag.name}> (第 {error.opening_tag.line} 行)")
            print(f"  结束标签: </{error.closing_tag.name}> (第 {error.closing_tag.line} 行)")
            print(f"  预期: </{error.opening_tag.name}>")

        elif error.error_type == 'unexpected_closing_tag':
            print(f"  错误: 意外的结束标签 </{error.tag_name}>")
            print(f"  位置: 第 {error.line} 行, 第 {error.column} 列")
            print(f"  说明: 没有找到对应的开始标签")

        elif error.error_type == 'improper_self_closing_tag':
            print(f"  错误: 不正确的自闭合标签 <{error.tag_name}>")
            print(f"  位置: 第 {error.line} 行, 第 {error.column} 列")
            print(f"  说明: 自闭合标签应使用 <{error.tag_name} /> 格式，而不是 <{error.tag_name}>")

        elif error.error_type == 'missing_faq':
            print(f"  错误: 缺少 FAQ 组件")
            print(f"  说明: 每篇文章都应该包含 <FAQ /> 组件")

        elif error.error_type == 'excessive_whitespace':
            print(f"  错误: {error.message}")
            print(f"  位置: 第 {error.line} 行")
            print(f"  建议: 运行 'python3 tools/clean_spaces.py {error.file_path}' 清理多余空格")

    def _print_json_report(self):
        """打印 JSON 格式报告"""
        # 错误分类统计
        error_breakdown = {}
        for error in self.all_errors:
            error_breakdown[error.error_type] = error_breakdown.get(error.error_type, 0) + 1

        files_with_errors = len(set(e.file_path for e in self.all_errors))

        report = {
            "summary": {
                "total_files": len(self.validated_files),
                "files_with_errors": files_with_errors,
                "total_errors": len(self.all_errors),
                "error_breakdown": error_breakdown
            },
            "errors": [
                {
                    "file": error.file_path,
                    "type": error.error_type,
                    "tag": error.tag_name,
                    "line": error.line,
                    "column": error.column,
                    "message": error.message
                }
                for error in self.all_errors
            ]
        }

        print(json.dumps(report, indent=2, ensure_ascii=False))

    def get_exit_code(self) -> int:
        """获取退出码"""
        return 1 if self.all_errors else 0


def find_mdx_files(path: str, exclude_patterns: List[str] = None) -> List[str]:
    """递归查找 MDX 文件"""
    mdx_files = []
    path_obj = Path(path)

    if path_obj.is_file():
        if path_obj.suffix == '.mdx':
            return [str(path_obj)]
        return []

    for mdx_file in path_obj.rglob('*.mdx'):
        file_path = str(mdx_file)

        # 检查排除模式
        if exclude_patterns:
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern in file_path:
                    should_exclude = True
                    break
            if should_exclude:
                continue

        mdx_files.append(file_path)

    return sorted(mdx_files)


def validate_mdx_file(file_path: str, verbose: bool = False) -> List[ValidationError]:
    """验证单个 MDX 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        if verbose:
            print(f"警告: 无法读取文件 {file_path}: {e}", file=sys.stderr)
        return []

    # 检测跳过区域
    skip_detector = SkipZoneDetector(content)
    skip_detector.detect_all_skip_zones()

    if verbose:
        print(f"处理文件: {file_path}")
        print(f"  跳过区域: {len(skip_detector.skip_zones)}")

    # 提取标签
    tag_extractor = TagExtractor(content, skip_detector, file_path)
    tags = tag_extractor.extract_all_tags()

    if verbose:
        print(f"  提取标签: {len(tags)}")

    # 验证标签
    validator = TagValidator()
    errors = validator.validate_file(file_path, tags)

    # 合并 TagExtractor 的错误（格式错误）和 TagValidator 的错误（匹配错误）
    all_errors = tag_extractor.errors + errors

    if verbose and all_errors:
        print(f"  发现错误: {len(all_errors)}")

    return all_errors


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='验证 MDX 文件中的标签匹配问题',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'path',
        nargs='?',
        default='content/',
        help='要扫描的 MDX 文件或目录路径（默认: content/）'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json'],
        default='text',
        help='输出格式（默认: text）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细信息'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='静默模式（仅显示错误）'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='严格模式（发现错误时退出码为 1）'
    )

    parser.add_argument(
        '--exclude',
        help='排除的路径模式（逗号分隔）'
    )

    args = parser.parse_args()

    # 解析排除模式
    exclude_patterns = []
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(',')]

    # 查找 MDX 文件
    mdx_files = find_mdx_files(args.path, exclude_patterns)

    if not mdx_files:
        print(f"未找到 MDX 文件: {args.path}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"找到 {len(mdx_files)} 个 MDX 文件\n")

    # 创建错误报告器
    reporter = ErrorReporter(format_type=args.format)

    # 验证所有文件
    for file_path in mdx_files:
        errors = validate_mdx_file(file_path, verbose=args.verbose)
        reporter.add_file_errors(file_path, errors)

    # 打印报告
    if not args.quiet or reporter.all_errors:
        reporter.print_report()

    # 返回退出码
    if args.strict:
        return reporter.get_exit_code()

    return 0


if __name__ == '__main__':
    sys.exit(main())
