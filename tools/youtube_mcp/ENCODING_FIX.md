# YouTube MCP 服务器编码问题修复指南

## 问题描述

在 Windows 系统上运行 YouTube MCP 服务器时，遇到 GBK 编码错误：
```
'gbk' codec can't encode character '\U0001f50d' in position 2: illegal multibyte sequence
```

这是因为代码中使用了 emoji 字符（🔍、✓、❌ 等），而 Windows 默认的 GBK 编码无法处理这些字符。

## 已完成的修复

### 1. 移除所有 emoji 字符

将所有 emoji 替换为纯文本标签：
- 🔍 → `[SEARCH]`
- ✓ → `[OK]`
- ❌ → `[ERROR]`
- 📥 → `[TRANSCRIPT]`
- 🚀 → `[START]`
- ⚠️ → `[WARN]`
- ⏳ → `[WAIT]`

修改的文件：
- `server.py`
- `core/youtube.py`
- `test_core.py`

### 2. 添加环境变量设置

在以下文件中添加了 UTF-8 编码环境变量：
- `server.py` - 设置 `PYTHONIOENCODING='utf-8'`
- `start_server.py` - 设置环境变量
- `run_server.py` - 新建的启动脚本，确保在导入模块前设置环境变量

### 3. 修复 stdio 冲突

移除了与 MCP `stdio_server` 冲突的 `sys.stdout` 重新包装代码。

## 使用方法

### 方案 1：使用 run_server.py（推荐）

在 MCP 配置文件中使用：

```json
{
  "mcpServers": {
    "youtube": {
      "command": "python",
      "args": ["D:\\web\\模板2.0\\tools\\youtube_mcp\\run_server.py"]
    }
  }
}
```

### 方案 2：使用 server.py + 环境变量

```json
{
  "mcpServers": {
    "youtube": {
      "command": "python",
      "args": ["D:\\web\\模板2.0\\tools\\youtube_mcp\\server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
      }
    }
  }
}
```

## 重启步骤

1. 更新 MCP 配置文件（通常在项目根目录的 `.mcp.json` 或 Claude Code 配置中）
2. 完全退出 Claude Code
3. 重新启动 Claude Code
4. 测试 YouTube MCP 搜索功能

## 测试

运行以下命令测试编码是否正常：

```bash
cd D:\web\模板2.0\tools\youtube_mcp
python test_encoding.py
```

应该能看到 emoji 正常输出。

## 验证修复

在 Claude Code 中运行：

```python
mcp__youtube__youtube_search(keyword="Python tutorial", max_results=5)
```

应该能成功返回搜索结果，不再出现编码错误。

## 注意事项

- 所有修复都已完成，代码已更新
- 必须重启 Claude Code 才能加载新代码
- 如果仍有问题，请检查 MCP 配置文件路径是否正确
- 确保使用的是 Python 3.7+ 版本

## 文件清单

修改的文件：
- ✅ `server.py` - 移除 emoji，添加环境变量
- ✅ `core/youtube.py` - 移除 emoji
- ✅ `test_core.py` - 移除 emoji，添加编码设置
- ✅ `start_server.py` - 简化启动逻辑
- ✅ `run_server.py` - 新建的推荐启动脚本

测试文件：
- ✅ `test_encoding.py` - 编码测试脚本
