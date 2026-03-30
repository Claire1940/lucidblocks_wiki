# 文章生成模块

使用 GPT-4o API 自动生成英文 SEO 文章的工具。

## 📋 功能特点

- ✅ 批量生成英文文章（基于 Excel 数据）
- ✅ 支持 YouTube 视频嵌入和元数据
- ✅ 智能内部链接选择
- ✅ 优先级筛选
- ✅ 失败重试机制
- ✅ 并发 API 调用（最高 1000 并发）

## 📁 文件结构

```
modules/generation/
├── config.json                    # 配置文件
├── prompt-template.txt            # 提示词模板
├── 内页.xlsx                      # 文章元数据
├── youtube_data.csv               # YouTube 视频数据
├── video_metadata_cache.json      # 视频元数据缓存
├── generate-articles.py           # 主生成脚本
├── api_client.py                  # API 客户端
├── excel_parser.py                # Excel 解析器
├── file_writer.py                 # 文件写入器
├── internal_links.py              # 内部链接管理
├── youtube_manager.py             # YouTube 管理器
└── video_metadata.py              # 视频元数据管理器
```

## 🚀 使用步骤

### 1. 预处理：生成 YouTube 视频元数据缓存

在生成文章之前，先运行此步骤生成视频元数据缓存：

```bash
cd tools/articles/modules/generation
python3 video_metadata.py
```

这将：
- 从 `youtube_data.csv` 读取所有视频数据
- 提取视频 ID、标题、时长、上传日期
- 生成 `video_metadata_cache.json` 缓存文件

### 2. 测试模式：生成 2 篇文章

```bash
python3 generate-articles.py --test
```

- 只生成前 2 篇文章
- 用于快速测试配置是否正确

### 3. 按优先级生成

生成优先级为 1 的文章：
```bash
python3 generate-articles.py --priority 1-1
```

生成优先级为 1-2 的文章：
```bash
python3 generate-articles.py --priority 1-2
```

### 4. 生成所有文章

```bash
python3 generate-articles.py
```

### 5. 覆盖已存在的文件

```bash
python3 generate-articles.py --overwrite
```

### 6. 重试失败的文章

```bash
python3 generate-articles.py --retry-failed
```

### 7. 清空失败列表

```bash
python3 generate-articles.py --clear-failed
```

## ⚙️ 配置说明

编辑 `config.json` 文件：

```json
{
  "api_key": "your-api-key",
  "api_base_url": "https://api.apicore.ai/v1/chat/completions",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4096,
  "concurrent_limit": 1000,
  "batch_size": 100,
  "excel_file": "内页.xlsx",
  "youtube_csv": "youtube_data.csv",
  "video_metadata_cache": "video_metadata_cache.json",
  "video_feature_enabled": true,
  "output_dir": "../../../../src/content/",
  "site_domain": "https://osrssailing.org",
  "internal_links": { ... },
  "external_authorities": [ ... ]
}
```

## 📊 输出结构

生成的文章将保存到：

```
src/content/en/{category}/{article-name}.mdx
```

示例：
```
src/content/en/guides/1-99-sailing-osrs.mdx
src/content/en/activities/osrs-sailing-boats.mdx
src/content/en/updates/osrs-sailing-release-date.mdx
```

## 📝 MDX 格式

```mdx
---
title: "Article Title with Keyword"
description: "SEO-optimized description (max 155 chars)"
keywords: ["main keyword", "related keyword"]
canonical: "/guides/article-path/"
date: "2025-12-05"
video:
  enabled: true
  youtubeId: "VIDEO_ID"
  title: "Video Title"
  description: "Video Description"
  duration: "PT8M35S"
  uploadDate: "2025-11-20"
---

[Article content here...]
```

## 🔧 常用命令参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--test` | 测试模式，只生成 2 篇 | `--test` |
| `--priority` | 按优先级筛选 | `--priority 1-2` |
| `--batch-size` | 并发批次大小 | `--batch-size 50` |
| `--overwrite` | 覆盖已存在的文件 | `--overwrite` |
| `--retry-failed` | 重试失败的文章 | `--retry-failed` |
| `--clear-failed` | 清空失败列表 | `--clear-failed` |

## 📋 Excel 数据格式

`内页.xlsx` 需包含以下列：

| 列名 | 说明 | 必需 |
|------|------|------|
| URL Path | 文章路径 | ✅ |
| Article Title | 文章标题 | ✅ |
| Keyword | 主关键词 | ✅ |
| Reference Link | 参考链接 | ❌ |
| Priority | 优先级（1-5） | ❌ |

## 🎯 最佳实践

1. **首次使用**：
   ```bash
   # 1. 生成视频元数据
   python3 video_metadata.py

   # 2. 测试生成
   python3 generate-articles.py --test

   # 3. 按优先级生成
   python3 generate-articles.py --priority 1-1
   ```

2. **批量生成**：
   ```bash
   # 生成优先级 1
   python3 generate-articles.py --priority 1-1

   # 生成优先级 2
   python3 generate-articles.py --priority 2-2

   # 生成所有剩余文章
   python3 generate-articles.py
   ```

3. **错误处理**：
   ```bash
   # 查看失败日志
   cat ../../../logs/failed_articles.log

   # 重试失败的文章
   python3 generate-articles.py --retry-failed
   ```

## 🐛 故障排查

### 问题 1：API 调用失败
```bash
❌ API error 429: Rate limit exceeded
```
**解决方案**：降低 `batch_size` 或 `concurrent_limit`

### 问题 2：文件已存在
```bash
⚠️  Skipping en/guides/article.mdx (already exists)
```
**解决方案**：使用 `--overwrite` 参数

### 问题 3：缺少视频元数据
```bash
⚠️  Video VIDEO_ID not found in cache
```
**解决方案**：重新运行 `python3 video_metadata.py`

## 📝 日志文件

- 失败文章日志：`tools/articles/logs/failed_articles.log`
- 包含失败原因、时间戳和文章信息

## 🔄 工作流程

```
1. video_metadata.py
   ↓ (生成缓存)
2. generate-articles.py --test
   ↓ (测试)
3. generate-articles.py --priority 1-1
   ↓ (按优先级生成)
4. generate-articles.py
   ↓ (生成所有)
5. generate-articles.py --retry-failed
   ↓ (重试失败)

输出: src/content/en/**/*.mdx
```

## ⚡ 性能

- **并发限制**：1000 个并发请求
- **批次大小**：100 篇/批次
- **生成速度**：约 10-15 秒/篇
- **预计时间**：100 篇文章约 15-25 分钟

## 📦 依赖

```bash
pip3 install pandas aiohttp openpyxl
```

## 🎓 后续步骤

文章生成后，使用翻译模块进行多语言翻译：
```bash
cd ../translate
python3 translate-articles.py
```
