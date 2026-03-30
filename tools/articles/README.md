# MDX Article Batch Generation Tool

自动批量生成SEO优化的MDX文章的Python工具。

## 功能特性

- 📊 从Excel文件读取文章元数据
- 🎯 支持按优先级筛选生成（1-4级）
- 🤖 使用GPT-4o API并发生成文章
- 📝 生成符合SEO标准的MDX内容
- 🔗 自动添加内部链接和外部权威链接
- ✅ 内容验证和格式检查
- 📈 详细的统计和进度报告
- 🔄 自动重试和错误处理
- 📁 自动添加_init后缀避免覆盖现有文件

## 目录结构

```
tools/articles/
├── config.json              # 配置文件（API密钥、设置等）
├── prompt-template.txt      # GPT-4o 提示词模板
├── 内页.xlsx                # 文章元数据Excel文件
├── generate-articles.py     # 主生成脚本
├── requirements.txt         # Python依赖
├── README.md               # 本文档
├── modules/                # Python模块
│   ├── excel_parser.py     # Excel解析器
│   ├── api_client.py       # API客户端
│   ├── file_writer.py      # 文件写入器
│   └── internal_links.py   # 内链管理器
└── logs/                   # 日志文件目录
    └── failed_articles.log # 失败文章日志
```

## 安装依赖

```bash
# 使用 pip 安装依赖
pip install -r tools/articles/requirements.txt

# 或者单独安装
pip install asyncio aiohttp pandas openpyxl
```

## 配置

### 1. 编辑 config.json

配置文件已包含必要的设置，如需修改：

```json
{
  "api_key": "your-api-key-here",
  "api_base_url": "https://api.apicore.ai/v1/chat/completions",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 4096,
  "concurrent_limit": 100,
  "retry_attempts": 3,
  "retry_delay": 2
}
```

### 2. 准备 Excel 文件

Excel文件 `内页.xlsx` 应包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| Priority | 优先级（1-4，数字越小优先级越高） | 1 |
| URL Path | 文章URL路径 | /codes/pixel-blade-codes/ |
| Article Title | 文章标题 | Pixel Blade Codes: Working Codes |
| Keyword | 主要关键词 | pixel blade codes |
| Reference Link | 参考文章链接 | https://example.com/reference |

**优先级说明：**
- Priority 1：最高优先级（x篇）
- Priority 2：高优先级（x篇）
- Priority 3：中等优先级（x篇）
- Priority 4：低优先级（x篇）

### 3. 自定义提示词模板

编辑 `prompt-template.txt` 以调整文章生成的要求和风格。

## 使用方法

### 基本用法

```bash
# 生成所有文章
python tools/articles/generate-articles.py

# 测试模式（仅生成前3篇）
python tools/articles/generate-articles.py --test

# 覆盖已存在的文件
python tools/articles/generate-articles.py --overwrite

# 自定义批处理大小
python tools/articles/generate-articles.py --batch-size 50
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--batch-size` | 并发API请求数量 | 100 |
| `--overwrite` | 覆盖已存在的MDX文件 | False |
| `--test` | 测试模式，仅处理前2篇文章 | False |
| `--priority` | 优先级范围筛选（格式：1-3） | 无（生成全部） |

### 示例

```bash
# 测试模式：生成2篇文章查看效果
python tools/articles/generate-articles.py --test

# 正式运行：生成所有文章
python tools/articles/generate-articles.py

# 重新生成所有文章（覆盖现有文件）
python tools/articles/generate-articles.py --overwrite

# 使用较小的批处理大小（降低API负载）
python tools/articles/generate-articles.py --batch-size 50

# 🎯 按优先级筛选生成：仅生成优先级1的文章
python tools/articles/generate-articles.py --priority 1-1

# 🎯 生成优先级1-2的文章（共60篇）
python tools/articles/generate-articles.py --priority 1-2

# 🎯 生成优先级1-3的文章（共90篇）
python tools/articles/generate-articles.py --priority 1-3

# 🎯 结合测试模式：测试优先级1的文章（生成2篇）
python tools/articles/generate-articles.py --priority 1-1 --test
```

## 输出

### 文件保存位置

生成的MDX文件会自动保存到对应的内容目录：

```
src/content/
├── codes/           # 代码相关文章
├── guides/          # 指南文章
├── tier-list/       # 排行榜文章
└── info/            # 信息类文章
```

### 日志文件

失败的文章会记录到：
```
tools/articles/logs/failed_articles.log
```

## 文章格式

生成的MDX文章包含：

### YAML Front Matter
```yaml
---
title: "文章标题"
description: "155字符以内的描述"
keywords: ["主关键词", "相关词1", "相关词2"]
canonical: "https://pixelbladegame.org/category/article-name/"
date: "2025-11-20"
---
```

### 内容结构
- ✅ 无 H1 标题（页面模板自动使用 title 作为 H1）
- ✅ 4-6个H2标题
- ✅ 可选的H3子标题
- ✅ 项目符号列表
- ✅ 每段少于120词
- ✅ 2个内部链接
- ✅ 2个权威外部链接
- ✅ FAQ部分（3-4个问答）

## 性能统计

脚本运行后会显示详细统计：

### API调用统计
- 总请求数
- 成功/失败数量
- 成功率
- 总Token消耗
- 执行时间
- 每秒请求数

### 文件写入统计
- 总处理文章数
- 成功保存数量
- 跳过数量（已存在）
- 错误数量

### 内链统计
- 可用内链总数
- 各类别内链数量

## 优先级筛选使用建议

### 什么时候使用优先级筛选？

1. **分阶段生成**：先生成高优先级文章，验证质量后再生成其他
2. **API配额管理**：当API有使用限制时，优先生成重要内容
3. **快速上线**：先发布最重要的文章，逐步补充其他内容
4. **测试验证**：测试新的提示词或配置时，只生成少量高优先级文章

### 推荐工作流程

```bash
# 阶段1：生成并测试优先级1（最重要的30篇）
python tools/articles/generate-articles.py --priority 1-1 --test  # 先测试2篇
python tools/articles/generate-articles.py --priority 1-1         # 全部生成

# 阶段2：检查质量后，生成优先级2
python tools/articles/generate-articles.py --priority 2-2

# 阶段3：生成剩余文章
python tools/articles/generate-articles.py --priority 3-4
```

### 优先级分布统计

脚本运行时会自动显示：
```
============================================================
📊 PRIORITY STATISTICS
============================================================
Total Articles:       120

Priority Distribution:
  Priority  1:      30 articles
  Priority  2:      30 articles
  Priority  3:      30 articles
  Priority  4:      30 articles

🎯 Filter Applied:    Priority 1-2
Filtered Articles:    60
============================================================
```

## 故障排除

### 常见问题

#### 1. API请求失败
```
❌ API error 401: Unauthorized
```
**解决方案**: 检查 `config.json` 中的 `api_key` 是否正确。

#### 2. Excel文件读取错误
```
❌ Error: Excel file not found
```
**解决方案**: 确保 `内页.xlsx` 文件存在于 `tools/articles/` 目录。

#### 3. 缺少Python依赖
```
ModuleNotFoundError: No module named 'aiohttp'
```
**解决方案**: 运行 `pip install -r tools/articles/requirements.txt`

#### 4. 速率限制
```
⚠️ Rate limited, waiting...
```
**解决方案**: 脚本会自动重试。如果频繁出现，可降低 `--batch-size`。

### 测试模块

可以单独测试各个模块：

```bash
# 测试Excel解析器
python tools/articles/modules/excel_parser.py

# 测试API客户端
python tools/articles/modules/api_client.py

# 测试文件写入器
python tools/articles/modules/file_writer.py

# 测试内链管理器
python tools/articles/modules/internal_links.py
```

## 最佳实践

1. **首次使用**：先运行 `--test` 模式检查效果
2. **大批量生成**：使用默认 `batch-size 100` 以提高效率
3. **API限流**：如遇限流，降低 `batch-size` 或增加 `retry_delay`
4. **内容验证**：生成后检查几篇文章确保质量
5. **备份**：生成前备份现有文章（或使用 `--overwrite` 时特别注意）

## 技术细节

### 并发处理
- 使用 `aiohttp` 实现异步HTTP请求
- 支持批量并发（默认100个请求/批）
- 自动管理连接池和超时

### 错误处理
- 自动重试失败的请求（默认3次）
- 指数退避策略
- 详细的错误日志

### 内容质量控制
- YAML front matter验证
- 标题层级检查（H1, H2数量）
- 关键词密度监控
- 内外链数量验证

## 许可证

本工具仅供内部使用。

## 支持

如有问题或建议，请联系开发团队。
