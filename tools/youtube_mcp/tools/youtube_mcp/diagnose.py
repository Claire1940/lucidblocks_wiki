#!/usr/bin/env python3
"""
YouTube MCP 服务器诊断脚本
"""

import sys
import os

print("=" * 70)
print("YouTube MCP 服务器诊断")
print("=" * 70)
print()

# 1. 检查 Python 环境
print("1. Python 环境")
print("-" * 70)
print(f"   Python 路径: {sys.executable}")
print(f"   Python 版本: {sys.version.split()[0]}")
print()

# 2. 检查依赖
print("2. 依赖检查")
print("-" * 70)

dependencies = [
    "mcp",
    "youtube_transcript_api",
    "requests",
    "dotenv"
]

all_ok = True
for dep in dependencies:
    try:
        __import__(dep.replace("-", "_"))
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - 未安装")
        all_ok = False

print()

# 3. 检查文件
print("3. 文件检查")
print("-" * 70)

files = [
    "server.py",
    "core/__init__.py",
    "core/config.py",
    "core/youtube.py",
    "core/utils.py",
    ".env"
]

for file in files:
    if os.path.exists(file):
        print(f"   ✅ {file}")
    else:
        print(f"   ❌ {file} - 不存在")
        all_ok = False

print()

# 4. 检查配置
print("4. 配置检查")
print("-" * 70)

try:
    from core.config import Config
    print(f"   ✅ 配置加载成功")
    print(f"   - 使用代理: {Config.USE_PROXY}")
    print(f"   - 代理服务器: {Config.TUNNEL_HOST}:{Config.TUNNEL_PORT}")
    print(f"   - 缓存目录: {Config.CACHE_DIR}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    all_ok = False

print()

# 5. 测试 MCP 服务器
print("5. MCP 服务器测试")
print("-" * 70)

try:
    from mcp.server import Server
    app = Server("youtube-mcp")
    print(f"   ✅ MCP 服务器创建成功")
except Exception as e:
    print(f"   ❌ MCP 服务器创建失败: {e}")
    all_ok = False

print()

# 6. Claude Desktop 配置
print("6. Claude Desktop 配置")
print("-" * 70)

config_path = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
if os.path.exists(config_path):
    print(f"   ✅ 配置文件存在")
    print(f"   路径: {config_path}")

    import json
    with open(config_path) as f:
        config = json.load(f)

    if "youtube" in config.get("mcpServers", {}):
        print(f"   ✅ YouTube MCP 已配置")
        youtube_config = config["mcpServers"]["youtube"]
        print(f"   - 命令: {youtube_config.get('command')}")
        print(f"   - 参数: {youtube_config.get('args')}")
    else:
        print(f"   ❌ YouTube MCP 未配置")
        all_ok = False
else:
    print(f"   ❌ 配置文件不存在")
    all_ok = False

print()
print("=" * 70)

if all_ok:
    print("✅ 所有检查通过！")
    print()
    print("如果 Claude Desktop 仍然无法加载 YouTube MCP，请：")
    print("1. 完全退出 Claude Desktop (Cmd+Q)")
    print("2. 重新打开 Claude Desktop")
    print("3. 查看 Claude Desktop 的日志（如果有）")
else:
    print("❌ 发现问题，请修复上述错误后重试")

print("=" * 70)
