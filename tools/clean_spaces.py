#!/usr/bin/env python3
"""清理 MDX 文件中的多余空格和超长表格分隔线"""

import re
import sys
from pathlib import Path


def is_table_separator(line: str) -> bool:
    """检测是否是表格分隔线"""
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return False

    # 移除首尾的 |，检查中间是否全是 - 和 |
    content = stripped[1:-1]
    return all(c in '-| ' for c in content) and '-' in content


def get_table_header_structure(lines: list, separator_index: int) -> tuple:
    """获取表头结构，返回 (列数, 列宽列表)"""
    if separator_index == 0:
        return None, None

    header_line = lines[separator_index - 1].strip()
    if not header_line.startswith('|') or not header_line.endswith('|'):
        return None, None

    # 分割列
    columns = [col.strip() for col in header_line.split('|')[1:-1]]
    column_count = len(columns)

    # 计算每列的合理宽度（至少3个字符用于 ---）
    column_widths = [max(len(col), 3) for col in columns]

    return column_count, column_widths


def generate_table_separator(column_widths: list) -> str:
    """生成合理长度的表格分隔线"""
    separators = ['|']
    for width in column_widths:
        separators.append('-' * width)
        separators.append('|')
    return ''.join(separators) + '\n'


def clean_file(filepath):
    """清理单个文件"""
    print(f"\n处理文件: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ✗ 读取文件失败: {e}")
        return False, 0, 0

    modified = False
    total_saved_bytes = 0
    total_saved_tokens = 0

    for i, line in enumerate(lines):
        line_length = len(line)

        # 检测 1: 多余空格（现有功能）
        if line_length > 1000 and '  ' in line:
            new_line = re.sub(r' {2,}', ' ', line)
            if len(new_line) != line_length:
                saved = line_length - len(new_line)
                saved_tokens = int(saved * 0.25)
                print(f"  第 {i+1} 行 [多余空格]: {line_length:,} -> {len(new_line):,} 字符 (节省 {saved:,} 字符)")
                lines[i] = new_line
                modified = True
                total_saved_bytes += saved
                total_saved_tokens += saved_tokens

        # 检测 2: 超长表格分隔线（新功能）
        elif line_length > 1000 and is_table_separator(line):
            column_count, column_widths = get_table_header_structure(lines, i)

            if column_widths:
                new_line = generate_table_separator(column_widths)
                saved = line_length - len(new_line)
                saved_tokens = int(saved * 0.25)

                print(f"  第 {i+1} 行 [表格分隔线]: {line_length:,} -> {len(new_line):,} 字符")
                print(f"    节省空间: {saved:,} 字符 ({saved/1024:.1f} KB)")
                print(f"    节省 tokens: ~{saved_tokens:,} tokens")

                lines[i] = new_line
                modified = True
                total_saved_bytes += saved
                total_saved_tokens += saved_tokens

    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"  ✓ 已保存: {filepath}")
            return True, total_saved_bytes, total_saved_tokens
        except Exception as e:
            print(f"  ✗ 保存文件失败: {e}")
            return False, 0, 0
    else:
        print(f"  ✓ 无需修改")
        return False, 0, 0


def main():
    if len(sys.argv) < 2:
        print("用法: python3 tools/clean_spaces.py <file_or_directory>")
        print("\n示例:")
        print("  python3 tools/clean_spaces.py content/en/resources/anime-paradox-passives.mdx")
        print("  python3 tools/clean_spaces.py content/")
        sys.exit(1)

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"错误: 路径不存在: {path}")
        sys.exit(1)

    print("=" * 60)
    print("MDX 文件多余空格和表格分隔线清理工具")
    print("=" * 60)

    files_processed = 0
    files_modified = 0
    total_saved_bytes = 0
    total_saved_tokens = 0

    if path.is_file():
        if path.suffix == '.mdx':
            files_processed = 1
            modified, saved_bytes, saved_tokens = clean_file(path)
            if modified:
                files_modified = 1
                total_saved_bytes += saved_bytes
                total_saved_tokens += saved_tokens
        else:
            print(f"错误: 不是 MDX 文件: {path}")
            sys.exit(1)
    elif path.is_dir():
        mdx_files = list(path.rglob('*.mdx'))
        if not mdx_files:
            print(f"错误: 目录中没有找到 MDX 文件: {path}")
            sys.exit(1)

        print(f"\n找到 {len(mdx_files)} 个 MDX 文件\n")

        for mdx_file in sorted(mdx_files):
            files_processed += 1
            modified, saved_bytes, saved_tokens = clean_file(mdx_file)
            if modified:
                files_modified += 1
                total_saved_bytes += saved_bytes
                total_saved_tokens += saved_tokens
    else:
        print(f"错误: 无效的路径: {path}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("清理完成")
    print("=" * 60)
    print(f"处理文件: {files_processed}")
    print(f"修改文件: {files_modified}")
    print(f"未修改文件: {files_processed - files_modified}")

    if total_saved_bytes > 0:
        print(f"\n节省统计:")
        print(f"  总空间: {total_saved_bytes:,} 字节 ({total_saved_bytes/1024:.1f} KB)")
        print(f"  总 tokens: ~{total_saved_tokens:,} tokens")

    print("=" * 60)


if __name__ == '__main__':
    main()
