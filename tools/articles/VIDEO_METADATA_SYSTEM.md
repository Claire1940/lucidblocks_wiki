# 视频元数据系统使用指南

## 概述

该系统实现了YouTube视频元数据的一次性预处理和缓存机制，避免在每次生成文章时重复调用YouTube API。

## 架构设计

```
一次性预处理（手动执行）:
├── fetch_video_metadata.py
│   ├── 读取 youtube_data.csv
│   ├── 提取视频 ID
│   ├── 调用 YouTube API 获取描述
│   ├── 转换时长格式（8.59 → PT8M35S）
│   ├── 转换相对日期（4天前 → 2024-11-21）
│   └── 保存到 video_metadata_cache.json
│
后续文章生成（自动使用缓存）:
└── generate-articles.py
    ├── 读取 video_metadata_cache.json
    ├── 生成文章内容（LLM）
    ├── 保存文章
    ├── 从文章内容提取视频 ID
    ├── 从缓存查找对应元数据
    └── 注入 video frontmatter
```

## 文件说明

### 核心文件

1. **`modules/video_metadata.py`** - 视频元数据管理器类
   - `VideoMetadataManager` 类
   - 负责加载CSV、调用API、格式转换、缓存管理

2. **`fetch_video_metadata.py`** - 预处理脚本
   - 一次性执行，生成缓存文件
   - 支持 `--limit` 参数用于测试

3. **`video_metadata_cache.json`** - 缓存文件（自动生成）
   - 存储所有视频的完整元数据
   - 格式：`{video_id: {metadata...}}`

4. **`config.json`** - 配置文件
   ```json
   {
     "youtube_api_key": "YOUR_API_KEY_HERE",
     "video_metadata_cache": "tools/articles/video_metadata_cache.json",
     "video_feature_enabled": true
   }
   ```

## 使用流程

### 第一步：配置 YouTube API Key

1. 打开 `tools/articles/config.json`
2. 填写 `youtube_api_key` 字段：
   ```json
   "youtube_api_key": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX"
   ```
3. 获取API Key：https://console.cloud.google.com/apis/credentials

### 第二步：预处理视频元数据（仅执行一次）

```bash
# 完整处理所有视频
python tools/articles/fetch_video_metadata.py

# 测试模式（只处理前5个视频）
python tools/articles/fetch_video_metadata.py --limit 5
```

**输出示例：**
```
============================================================
🎬 YouTube 视频元数据预处理工具
============================================================

📋 配置信息:
   CSV 文件: tools/articles/youtube_data.csv
   缓存文件: tools/articles/video_metadata_cache.json
   API Key: ✅ 已配置

🚀 开始批量获取视频元数据...

✅ 从 CSV 加载了 100 个视频

[1/100] 🔄 处理中: L093XqyLGrw - DEADLY DELIVERY GUIDE!...
[1/100] ✅ 成功: L093XqyLGrw
[2/100] ✓ 已缓存: XYZ123...
...

============================================================
📊 批量处理完成
============================================================
   总计: 100 个视频
   ✅ 成功: 85
   ⚠️  部分成功: 10
   ⏭️  跳过: 5
   💾 缓存大小: 95 个视频
============================================================

✅ 预处理完成！

缓存文件已保存到: tools/articles/video_metadata_cache.json
现在可以运行文章生成脚本，将自动使用缓存数据。
```

**生成的缓存文件示例：**
```json
{
  "L093XqyLGrw": {
    "enabled": true,
    "youtubeId": "L093XqyLGrw",
    "title": "DEADLY DELIVERY GUIDE! (Tips & TRICKS) Roblox",
    "description": "Master Total Chaos with tips and tricks...",
    "duration": "PT8M59S",
    "uploadDate": "2024-12-15"
  },
  "ABC123XYZ": {
    "enabled": true,
    "youtubeId": "ABC123XYZ",
    "title": "Another Video Title",
    "description": "Video description here...",
    "duration": "PT15M30S",
    "uploadDate": "2024-12-10"
  }
}
```

### 第三步：正常生成文章（自动使用缓存）

```bash
# 正常运行文章生成脚本
python tools/articles/generate-articles.py --test

# 视频元数据会自动注入到包含视频的文章中
```

**文章生成时的输出：**
```
✅ Saved: en/guides/gameplay.mdx
      ✅ Video metadata added: L093XqyLGrw
✅ Saved: vi/guides/gameplay.mdx
      ✅ Video metadata added: L093XqyLGrw
```

**生成的 MDX 文件示例：**
```yaml
---
title: "Total Chaos Gameplay Guide"
description: "Complete gameplay guide..."
keywords: ["deadly delivery", "gameplay"]
canonical: "https://totalchaos.info/guides/gameplay/"
date: "2024-11-25"
video:
  enabled: true
  youtubeId: "L093XqyLGrw"
  title: "DEADLY DELIVERY GUIDE! (Tips & TRICKS) Roblox"
  description: "Master Total Chaos with tips and tricks..."
  duration: "PT8M59S"
  uploadDate: "2024-12-15"
---

Article content here...

<iframe src="https://www.youtube.com/embed/L093XqyLGrw"></iframe>
```

## 工作原理

### 1. 预处理阶段（`fetch_video_metadata.py`）

```python
# 从 CSV 读取视频数据
csv_videos = load_csv_data()

for video in csv_videos:
    # 1. 提取视频 ID
    video_id = extract_video_id(video_url)

    # 2. 调用 YouTube API 获取描述
    api_data = fetch_youtube_api(video_id)

    # 3. 格式转换
    duration = minutes_to_iso8601("8.59")  # → "PT8M35S"
    upload_date = parse_relative_date("4天前")  # → "2024-11-21"

    # 4. 保存到缓存
    cache[video_id] = {
        "enabled": True,
        "youtubeId": video_id,
        "title": title,
        "description": api_data['description'],
        "duration": duration,
        "uploadDate": upload_date
    }

# 5. 写入 JSON 文件
save_cache_to_json()
```

### 2. 文章生成阶段（`generate-articles.py`）

```python
# 初始化时加载缓存
video_metadata_manager = VideoMetadataManager(config)
# 从 video_metadata_cache.json 读取所有数据到内存

# 生成并保存文章后
file_writer.save_article(content, article_info)

# 后处理：注入视频元数据
video_id = extract_youtube_id_from_content(content)  # 从 iframe 提取
video_metadata = video_metadata_manager.get_cached_metadata(video_id)
updated_content = inject_video_metadata_to_frontmatter(content, video_metadata)
save_updated_file(updated_content)
```

## 配置选项

### config.json 配置项

```json
{
  "youtube_api_key": "",          // YouTube Data API v3 密钥（必填）
  "youtube_csv": "tools/articles/youtube_data.csv",  // CSV 数据源
  "video_metadata_cache": "tools/articles/video_metadata_cache.json",  // 缓存文件路径
  "video_feature_enabled": true   // 是否启用视频功能（true/false）
}
```

### 启用/禁用视频功能

```json
// 启用（默认）
"video_feature_enabled": true

// 禁用（文章生成时不添加 video frontmatter）
"video_feature_enabled": false
```

## 增量更新

如果 CSV 文件中添加了新视频：

```bash
# 再次运行预处理脚本
python tools/articles/fetch_video_metadata.py

# 已缓存的视频会被跳过，只处理新视频
```

**输出示例：**
```
[1/110] ✓ 已缓存: L093XqyLGrw (跳过)
[2/110] ✓ 已缓存: ABC123XYZ (跳过)
...
[101/110] 🔄 处理中: NEW_VIDEO_ID - New Video Title...
[101/110] ✅ 成功: NEW_VIDEO_ID
```

## 格式转换说明

### 1. 时长格式转换

CSV 格式 → ISO 8601 格式

| CSV 中的值 | 转换后 | 说明 |
|-----------|--------|------|
| `8.59` | `PT8M35S` | 8分35秒 |
| `15.30` | `PT15M18S` | 15分18秒 |
| `1.05` | `PT1M3S` | 1分3秒 |
| `SHORTS` | 跳过 | Shorts视频不处理 |

### 2. 日期格式转换

CSV 格式 → ISO 8601 日期

| CSV 中的值 | 转换后 | 说明 |
|-----------|--------|------|
| `4天前` | `2024-11-21` | 当前日期减4天 |
| `1个月前` | `2024-10-25` | 当前日期减1个月 |
| `2周前` | `2024-11-11` | 当前日期减2周 |
| `直播时间：2天前` | `2024-11-23` | 提取数字转换 |

注：API 返回的日期更准确，优先使用 API 数据。

## 常见问题

### Q1: API Key 配额不够怎么办？

A: YouTube Data API 免费配额为每天 10,000 units，一次视频查询消耗 1 unit。如果视频过多，可以：
- 使用 `--limit` 参数分批处理
- 申请更高配额
- 等待第二天配额重置

### Q2: 某些视频获取失败怎么办？

A: 脚本会自动降级处理：
- 使用 CSV 中的时长和日期数据
- 使用标题作为描述
- 仍然会保存到缓存中
- 文章生成不受影响

### Q3: 如何验证缓存文件是否正确？

```bash
# 检查缓存文件内容
cat tools/articles/video_metadata_cache.json | jq '.'

# 检查特定视频
cat tools/articles/video_metadata_cache.json | jq '.L093XqyLGrw'
```

### Q4: 文章已生成，如何为旧文章添加视频元数据？

```bash
# 重新生成并覆盖
python tools/articles/generate-articles.py --overwrite

# 或手动编辑 MDX 文件添加 video frontmatter
```

## 技术细节

### 依赖库

```python
import requests  # HTTP 请求
import csv       # CSV 解析
import json      # JSON 处理
import re        # 正则表达式（提取视频ID）
from datetime import datetime, timedelta  # 日期处理
```

### VideoMetadataManager 主要方法

```python
class VideoMetadataManager:
    def __init__(config: dict)
    def load_csv_data() -> List[dict]
    def extract_video_id(url: str) -> Optional[str]
    def minutes_to_iso8601(minutes_str: str) -> str
    def parse_relative_date(relative_date: str) -> str
    def fetch_youtube_api(video_id: str) -> Optional[dict]
    def fetch_all_metadata(limit: Optional[int] = None)
    def get_cached_metadata(video_id: str) -> Optional[dict]
    def get_all_cached_metadata() -> Dict[str, dict]
```

## 性能优化

- ✅ 缓存机制：避免重复 API 调用
- ✅ 批量保存：每处理 10 个视频保存一次（防止中断丢失数据）
- ✅ 增量更新：已缓存视频跳过
- ✅ 内存加载：缓存文件一次性加载到内存，快速查询

## 下一步

1. 运行预处理脚本生成缓存
2. 测试文章生成流程
3. 验证 MDX 文件中的 video frontmatter
4. 检查前端页面是否正确显示 VideoObject Schema

---

**维护者**: 开发团队
**最后更新**: 2025-11-25
