#!/usr/bin/env python3
"""
完整流程编排

自动执行搜集 -> 筛选 -> 提取的完整流程
"""

import subprocess
import argparse
import sys


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_command(cmd: list, description: str) -> bool:
    """
    运行命令

    Args:
        cmd: 命令列表
        description: 描述

    Returns:
        是否成功
    """
    print_header(description)

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✓ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {description} 失败: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Content Pipeline - 完整流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程（手动筛选）
  python3 pipeline.py --json ../keywords.json

  # 完整流程（自动批准）
  python3 pipeline.py --json ../keywords.json --auto-approve

  # 按分类处理
  python3 pipeline.py --json ../keywords.json --category "Equipment System"
        """
    )
    parser.add_argument("--json", required=True, help="关键词 JSON 文件路径")
    parser.add_argument("--category", help="筛选特定分类（可选）")
    parser.add_argument("--auto-approve", action="store_true", help="自动批准（跳过筛选步骤）")
    args = parser.parse_args()

    print("=" * 70)
    print("  Content Pipeline")
    print("=" * 70)
    print(f"关键词文件: {args.json}")
    if args.category:
        print(f"分类: {args.category}")
    if args.auto_approve:
        print("模式: 自动批准")
    print("=" * 70)

    # ============================================================
    # 阶段1：搜集
    # ============================================================
    cmd = ["python3", "collect.py", "--json", args.json]
    if args.category:
        cmd.extend(["--category", args.category])

    if not run_command(cmd, "阶段1：搜集"):
        sys.exit(1)

    # ============================================================
    # 阶段2：筛选
    # ============================================================
    if not args.auto_approve:
        print_header("阶段2：筛选")
        print("请编辑 out/pending_review.json")
        print("设置 'selected': false 排除不需要的条目")
        print("\n按 Enter 继续，或 Ctrl+C 取消...")

        try:
            input()
        except KeyboardInterrupt:
            print("\n⚠️  用户取消")
            sys.exit(0)
    else:
        print_header("阶段2：筛选（跳过）")
        print("使用 --auto-approve，跳过手动筛选")

    # ============================================================
    # 阶段3：提取
    # ============================================================
    cmd = ["python3", "extract.py"]

    if not run_command(cmd, "阶段3：提取"):
        sys.exit(1)

    # ============================================================
    # 完成
    # ============================================================
    print_header("✅ 全部完成")
    print("输出目录: out/extracted/")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        sys.exit(0)
