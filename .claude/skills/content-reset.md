---
name: content-reset
description: 清理旧游戏内容，准备新内容
trigger: 当用户说"清理内容"、"content reset"、"重置内容"或输入 /content-reset 时触发
---

# content-reset

清理旧游戏的内容文件和生成输出，为新游戏内容做准备。

## 执行步骤

### 1. 删除旧内容目录
- 删除 `tools/content_pipeline/out/`（如果存在）
- 删除 `content/`（整个目录）

### 2. 读取语言配置
- 读取 `需求/00基础信息.md` 获取支持的语言列表
- 确认语言列表（加上英语最多8门）

### 3. 更新多语言配置文件
- 文件：`tools/articles/modules/translate/translate_config.json`
  - 更新 `target_languages` 数组
  - 更新 `game_name_localizations` 对象（每种语言的游戏名称翻译）

- 文件：`tools/articles/modules/transpage/transpage_config.json`
  - 更新 `target_languages` 数组
  - 更新 `game_name_localizations` 对象

### 4. 同步路由配置
- 确认 `src/i18n/routing.ts` 的 `locales` 数组与配置文件一致
- 确认 `src/lib/content.ts` 的 `validLanguages` 数组与配置文件一致

### 5. 初始化新内容目录结构（可选）
- 创建 `content/en/` 目录
- 根据 `src/config/navigation.ts` 中定义的内容类型创建子目录
- 为其他语言创建对应目录结构

### 6. 验证配置
- 检查所有配置文件的语言列表是否一致
- 确认目录结构符合项目规范

## 检查清单

完成后确认：
- [ ] `tools/content_pipeline/out/` 已删除
- [ ] `content/` 目录已删除
- [ ] `translate_config.json` 语言配置已更新
- [ ] `transpage_config.json` 语言配置已更新
- [ ] `game_name_localizations` 已配置所有语言
- [ ] `src/i18n/routing.ts` 语言列表一致
- [ ] `src/lib/content.ts` 语言列表一致
- [ ] 新内容目录结构已创建（如果需要）

## 配置文件示例

### translate_config.json
```json
{
  "target_languages": ["es", "pt", "fr", "de", "ja", "ko", "ru"],
  "game_name_localizations": {
    "en": "Game Name",
    "es": "Nombre del Juego",
    "pt": "Nome do Jogo",
    "fr": "Nom du Jeu",
    "de": "Spielname",
    "ja": "ゲーム名",
    "ko": "게임 이름",
    "ru": "Название игры"
  }
}
```

### routing.ts
```typescript
export const routing = defineRouting({
  locales: ['en', 'es', 'pt', 'fr', 'de', 'ja', 'ko', 'ru'],
  defaultLocale: 'en'
})
```

## 注意事项

1. **备份重要内容**：删除前确认是否需要备份旧内容
2. **语言一致性**：所有配置文件的语言列表必须保持一致
3. **游戏名称翻译**：`game_name_localizations` 必须包含所有目标语言
4. **最多8门语言**：包括英语在内，最多支持8门语言

## 后续步骤

内容重置完成后：
1. 使用 Python 工具生成新内容：
   ```bash
   cd tools/articles/modules/generation
   python api_client.py
   ```

2. 翻译内容到其他语言：
   ```bash
   cd tools/articles/modules/translate
   python translator.py
   ```

3. 翻译页面文案：
   ```bash
   cd tools/articles/modules/transpage
   python translate-all-locales.py --overwrite
   ```

## 相关 Skills

- 执行前先运行 `/game-rebrand` 完成基础配置
- 执行后运行 `/seo-audit` 进行最终检查
