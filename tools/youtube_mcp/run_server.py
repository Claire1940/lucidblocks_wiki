#!/usr/bin/env python3
"""
YouTube MCP 服务器运行脚本
在导入任何模块前设置环境变量
"""
import os
import sys

# 必须在导入任何其他模块之前设置
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
sys.path.insert(0, script_dir)

# 现在导入并运行服务器
if __name__ == "__main__":
    import asyncio
    from server import main
    asyncio.run(main())
