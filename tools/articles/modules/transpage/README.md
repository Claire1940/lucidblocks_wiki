# 增强版翻译系统使用指南

## 快速开始

### 1. 配置文件说明

编辑 `transpage_config.json`，根据你的项目修改：

```json
{
  // API 配置（必填）
  "api_key": "your-api-key",
  "api_base_url": "https://api.tiu.me/v1",
  "model": "gemini-2.0-flash",

  // 翻译质量配置（推荐值）
  "temperature": 0.1,              // 0.1 = 最稳定，0.3 = 平衡，0.7 = 创意
  "use_value_extraction": false,   // false = 完整JSON模式（防止字段错位）
  "retry_attempts": 8,              // 重试次数
  "retry_delay": 10,                // 重试延迟（秒）

  // 目标语言（根据项目需求修改）
  "languages": ["pt", "fr", "es", "de", "it", "ja", "ko"],
  "default_language": "en",
  "output_dir": "src/locales/",

  // 专有名词保护（根据游戏修改）
  "protected_terms": {
    "game_names": ["Your Game Name"],
    "character_names": ["Hero1", "Hero2"],
    "technical_terms": ["PvP", "PvE", "HP", "XP"]
  },

  // 游戏名称（所有语言保持一致或根据需要本地化）
  "game_names": {
    "en": "Your Game Name",
    "pt": "Your Game Name",
    "fr": "Your Game Name"
  },

  // 语言名称（标准配置，一般不需要修改）
  "lang_names": {
    "pt": "Portuguese (Brazil)",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ru": "Russian",
    "vi": "Vietnamese",
    "th": "Thai"
  }
}
```

### 2. 执行翻译

```bash
# 基础用法：翻译所有配置的语言
python3 translate-messages-enhanced.py --overwrite --report

# 翻译指定语言
python3 translate-messages-enhanced.py --lang pt,fr,es --overwrite --report

# 增量翻译（只翻译变化的部分）
python3 translate-messages-enhanced.py --incremental --report

# 指定分块策略（如果默认失败）
python3 translate-messages-enhanced.py --lang pt --strategy small --overwrite --report
```

### 3. 验证结果

```bash
# JSON 格式验证
for lang in pt fr es de it ja ko; do
  python3 -m json.tool src/locales/$lang.json > /dev/null && echo "✅ $lang" || echo "❌ $lang"
done

# 查看翻译报告
cat temp/translation-reports/*.json

# 检查字段数量
en_fields=$(grep -o '"[^"]*":' src/locales/en.json | wc -l)
for lang in pt fr es de it ja ko; do
  lang_fields=$(grep -o '"[^"]*":' src/locales/$lang.json | wc -l)
  echo "$lang: $lang_fields 字段 (en: $en_fields)"
done
```

## 核心特性

### 1. 智能分块翻译
- 自动分块避免 token 限制
- 自动降级重试（top_level → medium → small → tiny）

### 2. 三重验证
- JSON 格式验证
- 结构完整性验证
- 文件大小验证

### 3. 专有名词保护
- 游戏名称自动保护
- 角色名称自动保护
- 技术术语自动保护

### 4. 详细错误报告
- 保存到 `temp/translation-reports/`
- 包含每个分块的成功/失败状态

## 配置参数说明

### 关键参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| `temperature` | 0.1 | 越低越稳定，防止字段错位 |
| `use_value_extraction` | false | 完整JSON模式，防止字段错位 |
| `retry_attempts` | 8 | 增加重试次数，应对API超时 |
| `retry_delay` | 10 | 重试延迟，避免API限流 |
| `max_tokens` | 32768 | 足够大，避免截断 |
| `timeout` | 1800 | 30分钟超时 |

### 分块策略

| 策略 | 分块大小 | 适用场景 |
|------|---------|---------|
| `top_level` | 按顶层键 | 默认，适合大多数情况 |
| `medium` | 30个键 | 顶层键过大时 |
| `small` | 15个键 | 中等分块失败时 |
| `tiny` | 5个键 | 最后手段 |

## 常见问题

### Q1: API 连接超时
- 增加 `timeout` 到 3600（1小时）
- 分批翻译：`--lang pt` → `--lang fr` → `--lang es`

### Q2: 字段错位
- 确认 `use_value_extraction: false`
- 确认 `temperature: 0.1`

### Q3: 部分模块未翻译
- 查看报告：`cat temp/translation-reports/*.json`
- 使用更小的分块：`--strategy small`

### Q4: FAQ 问答互换
- 降低 `temperature` 到 0.1
- 重新翻译

### Q5: 字段为空
- 增加 `retry_attempts` 到 8
- 检查 API 配置

## 适配新项目

### 步骤 1: 复制文件
```bash
cp -r tools/articles/modules/transpage /path/to/new-project/tools/
```

### 步骤 2: 修改配置
编辑 `transpage_config.json`：
- 修改 `api_key` 和 `api_base_url`
- 修改 `languages` 为目标语言
- 修改 `output_dir` 为输出目录
- 修改 `protected_terms` 为游戏专有名词
- 修改 `game_names` 为游戏名称

### 步骤 3: 执行翻译
```bash
python3 translate-messages-enhanced.py --overwrite --report
```

## 文件说明

- `translate-messages-enhanced.py` - 增强版翻译脚本（主入口）
- `smart_chunk_translator.py` - 智能分块翻译器
- `translator.py` - 翻译核心模块
- `transpage_config.json` - 配置文件
- `prompts/` - 翻译提示词模板

## 质量标准

翻译完成后应满足：
- ✅ JSON 格式有效
- ✅ 字段数量与 en.json 一致
- ✅ 空字段 < 5 个
- ✅ 文件大小在 en.json 的 80%-150% 范围
- ✅ 浏览器测试无问题

## 技术支持

遇到问题查看：
- `需求/04翻译质量解决方案.md`
- `需求/06增强版翻译系统使用指南.md`
