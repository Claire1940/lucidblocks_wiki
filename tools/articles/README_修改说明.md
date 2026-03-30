# 文章生成功能修改说明

## 修改内容
修改了文章生成功能,使得即使文章格式不符合要求,也会写入 `src/content`,但会显示警告。

## 主要变化

### 1. 新的行为
- **之前:** 验证失败 → 文章不保存
- **现在:** 验证失败 → 文章仍然保存 + 显示警告

### 2. 输出消息
- ✅ `Saved: en/xxx/xxx.mdx` - 格式正确的文章
- ⚠️ `Saved with warnings: en/xxx/xxx.mdx` - 有格式问题但仍保存的文章
- ⏭️ `Skipping: en/xxx/xxx.mdx` - 文件已存在,跳过
- ❌ `Error saving: en/xxx/xxx.mdx` - 写入失败 (I/O 错误)

### 3. 统计报告
```
Total Processed:      100
Successfully Saved:   92 ✅      # 格式完全正确的文章
Saved with Warnings:  5 ⚠️       # 有问题但仍保存的文章
Skipped (exists):     2 ⏭️       # 跳过的文章
Errors:               1 ❌       # 真正的错误
Write Success Rate:   97%        # (92+5)/100 = 97%
```

### 4. 日志记录
有格式问题的文章会记录到 `tools/articles/logs/failed_articles.json`:
```json
{
  "url_path": "/xxx/xxx/",
  "title": "Article Title",
  "error": "VALIDATION_WARNING: Missing required fields: description:",
  "written_with_warnings": true
}
```

## 使用方法

### 正常使用
无需改变任何使用方式,文章生成时自动应用新机制。

### 查看有警告的文章
```bash
# 查看所有带警告的文章
jq '.[] | select(.written_with_warnings == true)' tools/articles/logs/failed_articles.json
```

### Windows 环境运行 python -X utf8 xxx.py
如果遇到编码错误,使用 UTF-8 模式:
```bash
python -X utf8 generate-articles.py
```

## 验证规则 (未改变)
仍然检查以下内容:
- ✓ YAML front matter 必须存在
- ✓ 必需字段: title, description, keywords, canonical, date
- ✓ 不允许 H1 标题 (会与页面标题重复)

**区别:** 即使不符合规则,文章也会保存,只是会显示警告。

## 测试
运行测试脚本验证功能:
```bash
cd tools/articles
python -X utf8 test_validation_warning.py
```

## 修改的文件
- `tools/articles/modules/generation/file_writer.py` - 核心逻辑修改
- `tools/articles/test_validation_warning.py` - 测试脚本 (新增)
- `tools/articles/MODIFICATIONS.md` - 详细修改文档 (新增)

## 向后兼容性
✅ 完全兼容,无需修改现有代码或配置
