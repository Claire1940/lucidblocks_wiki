# YouTube MCP 配置指南

## 快速开始

### 1. 安装依赖

```bash
cd tools/youtube_mcp
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，配置代理信息（必须）：

```bash
USE_PROXY=true
TUNNEL_HOST=overseas.tunnel.qg.net
TUNNEL_PORT=16660
TUNNEL_USER=your_username
TUNNEL_PASS=your_password
```

### 3. 添加 MCP 服务器到 Claude Code

**重要：必须使用完整的绝对路径**

```bash
# 错误示例（相对路径会导致工具无法加载）
claude mcp add youtube -- python3 server.py

# 正确示例（使用完整绝对路径）
claude mcp add youtube -- python3 /Users/username/path/to/tools/youtube_mcp/server.py
```

### 4. 验证连接

```bash
claude mcp list
```

应该看到：
```
youtube: python3 /full/path/to/server.py - ✓ Connected
```

### 5. 重启 Claude Code 会话

**关键步骤：** 添加 MCP 后必须重启 Claude Code 会话，工具才会加载到当前环境中。

### 6. 使用 MCP 工具

重启后，可以直接在对话中调用：

- `youtube_search` - 搜索视频
- `youtube_get_transcript` - 获取字幕
- `youtube_search_and_transcribe` - 搜索并获取字幕

## 常见问题

**Q: 为什么工具没有加载？**
A: 确保使用完整绝对路径，并重启 Claude Code 会话。

**Q: 如何移除 MCP 服务器？**
A: `claude mcp remove youtube -s local`
