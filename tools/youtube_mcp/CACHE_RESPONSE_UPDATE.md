# YouTube MCP 缓存响应更新

## 更新日期
2025-02-08

## 更新概述
修改 YouTube MCP 服务，使其返回缓存文件路径而非完整字幕内容，以避免上下文溢出问题。

## 问题背景
之前的实现会在响应中返回完整的字幕内容，当字幕很长时（例如 50KB+），会导致：
- 上下文窗口溢出
- 响应体积过大
- 不必要的数据传输

## 解决方案
将数据存储与数据检索分离：
1. 字幕获取后自动保存到缓存文件：`cache/youtube/{video_id}.json`
2. API 响应只返回文件路径和元数据
3. Claude 可以使用 Read 工具按需读取缓存文件

## 修改内容

### 1. 新增函数：`format_transcript_response()`
**位置**: `server.py` (第 125-164 行)

**功能**: 将字幕结果格式化为包含缓存文件路径的响应

**输入**:
```python
{
  "success": True,
  "video_id": "dQw4w9WgXcQ",
  "transcript": "完整字幕内容...",  # 可能有几千字符
  "language": "en",
  "cached": False
}
```

**输出**:
```python
{
  "success": True,
  "video_id": "dQw4w9WgXcQ",
  "cache_file": "cache/youtube/dQw4w9WgXcQ.json",
  "transcript_length": 2089,
  "language": "en",
  "cached": False,
  "message": "Transcript saved to cache/youtube/dQw4w9WgXcQ.json. Use Read tool to access content."
}
```

### 2. 更新函数：`handle_youtube_get_transcript()`
**位置**: `server.py` (第 192-223 行)

**修改**:
- 调用 `format_transcript_response()` 格式化响应
- 更新日志输出，显示缓存文件路径和字符数
- 响应中不再包含完整字幕内容

### 3. 更新函数：`handle_youtube_search_and_transcribe()`
**位置**: `server.py` (第 226-275 行)

**修改**:
- 遍历每个视频结果，移除 `transcript` 字段
- 添加 `cache_file`、`transcript_length`、`language` 字段
- 在响应中添加使用提示消息

### 4. 更新工具描述
**位置**: `server.py` (第 58 和 78 行)

**修改**:
- `youtube_get_transcript`: 描述更新为"获取 YouTube 视频字幕并保存到缓存文件，返回文件路径而非完整内容"
- `youtube_search_and_transcribe`: 描述更新为"搜索关键词并获取前 N 个视频的字幕，保存到缓存文件并返回文件路径"

## 响应对比

### 修改前
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "transcript": "We're no strangers to love You know the rules... [2000+ 字符]",
  "language": "en",
  "cached": false
}
```
**响应大小**: ~4.6 KB

### 修改后
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "cache_file": "cache/youtube/dQw4w9WgXcQ.json",
  "transcript_length": 2089,
  "language": "en",
  "cached": false,
  "message": "Transcript saved to cache/youtube/dQw4w9WgXcQ.json. Use Read tool to access content."
}
```
**响应大小**: ~307 字节

**大小减少**: 93% ✅

## 缓存文件格式

缓存文件保存在 `cache/youtube/{video_id}.json`，格式如下：

```json
{
  "video_id": "dQw4w9WgXcQ",
  "content": "完整字幕内容...",
  "language": "en",
  "source_type": "youtube",
  "cached_at": "2025-02-08T21:14:08.324474"
}
```

## 使用方式

### 1. 获取单个视频字幕
```python
# 调用 MCP 工具
response = youtube_get_transcript(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# 响应示例
{
  "success": true,
  "cache_file": "cache/youtube/dQw4w9WgXcQ.json",
  "transcript_length": 2089,
  "language": "en"
}

# 读取完整字幕
transcript_data = Read(file_path="cache/youtube/dQw4w9WgXcQ.json")
full_transcript = transcript_data["content"]
```

### 2. 搜索并获取多个视频字幕
```python
# 调用 MCP 工具
response = youtube_search_and_transcribe(keyword="Python tutorial", num_videos=3)

# 响应示例
{
  "keyword": "Python tutorial",
  "count": 3,
  "videos": [
    {
      "title": "Python Tutorial for Beginners",
      "video_id": "abc123",
      "cache_file": "cache/youtube/abc123.json",
      "transcript_length": 5234,
      "transcript_available": true
    },
    ...
  ],
  "message": "Transcripts saved to cache files. Use Read tool to access content."
}

# 按需读取特定视频的字幕
transcript_data = Read(file_path="cache/youtube/abc123.json")
```

## 测试结果

运行 `test_cache_response.py` 的测试结果：

✅ **测试 1**: `format_transcript_response()` 成功场景
- 响应大小从 4651 字节减少到 307 字节
- 响应包含 `cache_file` 而非完整 `transcript`

✅ **测试 2**: `format_transcript_response()` 失败场景
- 错误响应格式正确
- 包含错误信息和提示消息

✅ **测试 3**: 真实字幕获取
- 字幕成功保存到缓存文件
- 缓存文件包含完整字幕内容
- 响应只包含元数据和文件路径

## 优势

1. **避免上下文溢出**: 响应大小减少 93%，从 KB 级别降至字节级别
2. **按需加载**: Claude 可以选择性地读取需要的字幕
3. **更好的架构**: 数据存储与检索分离
4. **缓存复用**: 缓存文件可以跨会话重复使用
5. **向后兼容**: 缓存机制保持不变，只是响应格式改变

## 注意事项

1. **缓存目录**: 确保 `cache/youtube/` 目录存在且可写
2. **文件路径**: 响应中的 `cache_file` 路径是相对于 MCP 服务器工作目录的
3. **读取权限**: Claude 需要有读取缓存文件的权限
4. **缓存清理**: 长期运行可能需要定期清理旧的缓存文件

## 相关文件

- `server.py`: 主要修改文件
- `core/youtube.py`: 缓存逻辑（未修改）
- `core/utils.py`: 缓存工具函数（未修改）
- `test_cache_response.py`: 测试脚本

## 版本信息

- **修改前版本**: 返回完整字幕内容
- **修改后版本**: 返回缓存文件路径
- **兼容性**: 完全向后兼容，缓存机制不变
