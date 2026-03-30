#!/usr/bin/env python3
"""测试编码问题"""
import sys
import io

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("测试 emoji 输出:")
print("🔍 搜索")
print("✓ 成功")
print("❌ 失败")
print("📥 下载")
print("🚀 启动")

print("\n编码测试完成!")
