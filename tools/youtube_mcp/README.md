# YouTube MCP 服务器

一个基于 MCP (Model Context Protocol) 的 YouTube 搜索和字幕获取服务器，可以被 Claude 等 AI 助手调用。

## 功能特性

- ✅ **YouTube 搜索**：根据关键词搜索视频，返回视频链接和元数据
- ✅ **字幕获取**：获取 YouTube 视频的字幕（支持多语言）
- ✅ **组合功能**：搜索关键词并直接获取前 N 个视频的字幕
- ✅ **代理支持**：支持青果隧道等代理服务（必须使用代理）
- ✅ **缓存机制**：自动缓存字幕，避免重复请求
- ✅ **并行处理**：使用 asyncio 并行处理，提高效率

## 安装

### 1. 安装依赖

```bash
cd tools/youtube_mcp
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，配置代理信息：

```bash
# 代理配置（必须）
USE_PROXY=true
TUNNEL_HOST=overseas.tunnel.qg.net
TUNNEL_PORT=17407
TUNNEL_USER=your_username
TUNNEL_PASS=your_password

# 代理格式：tagged（青果隧道普通模式打标记）
TUNNEL_PROXY_FORMAT=tagged
TUNNEL_CHANNEL_PREFIX=channel
TUNNEL_TTL=10

# YouTube 配置
YOUTUBE_INITIAL_RESULTS=5
YOUTUBE_MAX_DURATION=3600
YOUTUBE_RETRIES=3
YOUTUBE_TIMEOUT=180

# 缓存配置
CACHE_DIR=cache
```

## 使用方式

### 方式 1：在 Claude Desktop 中使用（推荐）

1. 编辑 Claude Desktop 配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加 MCP 服务器配置：

```json
{
  "mcpServers": {
    "youtube": {
      "command": "python3",
      "args": ["/path/to/tools/youtube_mcp/server.py"]
    }
  }
}
```

3. 重启 Claude Desktop

4. 在 Claude 中使用：

```
用户: 搜索 "Python tutorial" 相关的 YouTube 视频

Claude: [调用 youtube_search 工具]

用户: 获取这个视频的字幕：https://youtube.com/watch?v=abc123

Claude: [调用 youtube_get_transcript 工具]

用户: 搜索 "机器学习入门" 并获取前 2 个视频的字幕

Claude: [调用 youtube_search_and_transcribe 工具]
```

### 方式 2：命令行测试

使用 MCP Inspector 测试服务器：

```bash
npx @modelcontextprotocol/inspector python3 server.py
```

## MCP Tools 说明

### 1. youtube_search

搜索 YouTube 视频，返回视频链接和元数据。

**输入参数**：
- `keyword` (string, required): 搜索关键词
- `max_results` (number, optional): 返回结果数量（默认 5）
- `max_duration` (number, optional): 最大视频时长（秒，默认 3600）

**输出示例**：
```json
{
  "keyword": "Python tutorial",
  "count": 5,
  "videos": [
    {
      "title": "Python Tutorial for Beginners",
      "url": "https://youtube.com/watch?v=abc123",
      "video_id": "abc123",
      "channel": "Programming with Mosh",
      "duration": "6:14:07",
      "duration_seconds": 22447,
      "view_count": 12345678
    }
  ]
}
```

### 2. youtube_get_transcript

获取 YouTube 视频字幕（带自动重试机制）。

**输入参数**：
- `url` (string, required): YouTube 视频 URL 或 video_id
- `languages` (array, optional): 字幕语言优先级（默认 ['zh', 'en']）

**输出示例**：
```json
{
  "video_id": "abc123",
  "url": "https://youtube.com/watch?v=abc123",
  "transcript": "Hello everyone, welcome to this tutorial...",
  "language": "en",
  "success": true,
  "cached": false,
  "retries": 0
}
```

**重试机制**：
- 如果首次获取失败，会自动重试最多 2 次
- 使用指数退避策略（等待 2秒、4秒）
- 每次重试会使用新的代理 IP（TTL=10秒自动轮换）
- 大幅提高成功率（从 66% 提升到接近 100%）

### 3. youtube_search_and_transcribe

搜索关键词并获取前 N 个视频的字幕（组合功能）。

**输入参数**：
- `keyword` (string, required): 搜索关键词
- `num_videos` (number, optional): 获取字幕的视频数量（默认 2）
- `max_duration` (number, optional): 最大视频时长（秒，默认 3600）

**输出示例**：
```json
{
  "keyword": "机器学习入门",
  "count": 2,
  "videos": [
    {
      "title": "机器学习入门教程",
      "url": "https://youtube.com/watch?v=abc123",
      "video_id": "abc123",
      "channel": "AI学习",
      "duration": "45:30",
      "transcript": "大家好，今天我们来学习机器学习...",
      "language": "zh",
      "transcript_available": true
    }
  ]
}
```

## 缓存机制

字幕会自动缓存在 `cache/youtube/` 目录下，文件名格式为 `{video_id}.json`。

缓存命中时会在输出中标记 `"cached": true`，避免重复请求。

清理缓存：
```bash
rm -rf cache/youtube/*
```

## 代理配置说明

本服务器**必须使用代理**才能访问 YouTube。支持两种代理格式：

### 1. 简单格式（simple）
```bash
TUNNEL_PROXY_FORMAT=simple
```
代理 URL 格式：`http://user:pass@host:port`

### 2. 青果隧道打标记格式（tagged）
```bash
TUNNEL_PROXY_FORMAT=tagged
TUNNEL_CHANNEL_PREFIX=channel
TUNNEL_TTL=10
```
代理 URL 格式：`http://user:pass:channel-{stage}:{ttl}@host:port`

其中 `{stage}` 会根据操作类型自动设置：
- `search` - YouTube 搜索阶段
- `extract` - 字幕获取阶段

## 故障排除

### 1. 搜索失败

**问题**：搜索时报错 "未找到任何视频"

**解决方案**：
- 检查代理配置是否正确
- 检查 `yt-dlp` 是否已安装：`yt-dlp --version`
- 尝试手动测试代理：`curl --proxy "http://user:pass@host:port" https://www.youtube.com`

### 2. 字幕获取失败

**问题**：字幕获取失败，返回 "字幕不可用"

**原因**：
- 视频没有字幕
- 视频字幕被禁用
- 代理连接失败

**解决方案**：
- 确认视频确实有字幕（在 YouTube 网页上查看）
- 检查代理配置
- 尝试其他视频

### 3. 代理连接超时

**问题**：操作超时

**解决方案**：
- 检查代理服务器是否可用
- 增加超时时间：修改 `.env` 中的 `YOUTUBE_TIMEOUT`
- 检查网络连接

## 技术架构

```
tools/youtube_mcp/
├── server.py              # MCP 服务器主入口
├── core/
│   ├── __init__.py       # 模块初始化
│   ├── config.py         # 配置管理
│   ├── youtube.py        # YouTube 搜索和字幕提取
│   └── utils.py          # 工具函数
├── requirements.txt       # 依赖列表
├── .env                   # 环境变量配置
└── README.md             # 本文档
```

## 依赖项

- **mcp**: Model Context Protocol SDK
- **yt-dlp**: YouTube 视频下载和搜索工具
- **youtube-transcript-api**: YouTube 字幕获取库
- **requests**: HTTP 请求库
- **python-dotenv**: 环境变量管理

## 许可证

MIT License
