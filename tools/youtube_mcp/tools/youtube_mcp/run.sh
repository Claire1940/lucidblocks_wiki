#!/bin/bash
# YouTube MCP 服务器快速启动脚本

echo "🚀 YouTube MCP 服务器"
echo "===================="
echo ""

# 检查依赖
echo "📦 检查依赖..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

if ! command -v yt-dlp &> /dev/null; then
    echo "❌ 错误: 未找到 yt-dlp"
    echo "   请运行: pip3 install yt-dlp"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件"
    exit 1
fi

echo "✅ 依赖检查通过"
echo ""

# 显示菜单
echo "请选择操作:"
echo "1. 运行核心功能测试"
echo "2. 启动 MCP 服务器"
echo "3. 查看配置"
echo "4. 清理缓存"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🧪 运行核心功能测试..."
        echo ""
        python3 test_core.py
        ;;
    2)
        echo ""
        echo "🚀 启动 MCP 服务器..."
        echo ""
        python3 server.py
        ;;
    3)
        echo ""
        echo "⚙️  当前配置:"
        echo ""
        python3 -c "from core.config import Config; Config.print_summary()"
        ;;
    4)
        echo ""
        echo "🗑️  清理缓存..."
        if [ -d cache ]; then
            rm -rf cache
            echo "✅ 缓存已清理"
        else
            echo "ℹ️  缓存目录不存在"
        fi
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac
