#!/usr/bin/env python
"""
YouTube MCP 服务器启动脚本
确保在正确的工作目录下运行
"""
import os
import sys

# 设置环境变量强制使用 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加当前目录到 Python 路径
sys.path.insert(0, script_dir)

# 导入并运行服务器主函数
if __name__ == "__main__":
    from server import main
    import asyncio

    asyncio.run(main())
