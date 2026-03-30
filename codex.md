## 项目概述

这是一个基于 Next.js 15 的 Roblox 游戏资源中心网站，为 "Anime Paradox" 游戏提供工具、攻略和社区资源。项目使用 App Router、TypeScript、Tailwind CSS 和 shadcn/ui 组件库。

## 重要工作规则

⚠️ **任务执行原则**:
1. **如果给出的任务已经完成，请跳过并进行下一步**
2. **每次只完成要求的任务，项目其余部分未经允许禁止改动/增删**
3. **每次完成任务时，自动进行构建测试（提问讨论类的任务除外）**

## 常用命令

### 开发

```bash
bun dev                    # 启动开发服务器 (使用 Turbopack，监听 0.0.0.0)
bun run build              # 构建生产版本
bun start                  # 启动生产服务器
```

### 代码质量

```bash
bun run lint               # 运行 TypeScript 类型检查和 ESLint
bunx tsc --noEmit          # 仅运行 TypeScript 类型检查
bun run format             # 使用 Biome 格式化代码
bunx biome check --write   # 运行 Biome 检查并自动修复
```

### shadcn/ui 组件

```bash
bunx shadcn@latest add <component-name>   # 添加新的 shadcn/ui 组件
```

## 代码架构

### 目录结构

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 根布局 (服务器组件) - 字体加载、元数据、same-runtime 集成
│   ├── page.tsx           # 主页面 (客户端组件) - 完整的营销页面
│   ├── ClientBody.tsx     # 客户端包装 - 提供 LanguageProvider
│   └── globals.css        # 全局样式 - Tailwind + CSS 变量 + 自定义动画
├── components/ui/         # shadcn/ui 组件库
├── contexts/              # React Context 状态管理
│   └── LanguageContext.tsx  # 多语言上下文（支持 7 种语言）
├── lib/                   # 工具函数
│   └── utils.ts          # cn() 函数 - 合并 Tailwind 类名
└── locales/              # 国际化翻译文件
    ├── en.json           # 英文翻译（主翻译文件/源文件）
    └── [其他语言].json   # 基于 en.json 翻译的其他 7 种语言（不包含中文）
```

### 关键架构决策

#### 1. 服务器组件 vs 客户端组件

- **layout.tsx**: 服务器组件 - 处理元数据、字体加载、静态配置
- **page.tsx**: 客户端组件 (`'use client'`) - 需要交互、状态管理和浏览器 API
- **ClientBody.tsx**: 客户端包装 - 解决水合问题，提供 Context

#### 2. 状态管理

使用 React Context API 进行轻量级状态管理：

- **LanguageContext**: 管理多语言切换（支持 7 种语言）
- 使用 localStorage 持久化语言选择
- 自动检测浏览器语言 (navigator.language)

使用方式：

```typescript
const { language, setLanguage, t } = useLanguage();
```

#### 3. 国际化 (i18n)

- 翻译文件位于 `src/locales/`
- **en.json** 是主翻译文件（源文件），所有新内容首先添加到这里
- 其他语言文件基于 en.json 进行翻译
- 通过 LanguageContext 提供翻译对象 `t`
- 所有文本内容都应通过 `t.section.key` 访问
- **重要**: 项目不包含中文翻译（zh.json）

#### 4. 样式系统

- **Tailwind CSS**: 主要样式框架
- **CSS 变量**: 使用 HSL 格式定义颜色系统 (在 globals.css 中)
- **深色模式**: 基于 class 的切换 (`.dark` 类)
- **shadcn/ui**: 使用 "new-york" 风格，基础颜色为 zinc
- **动画**: 使用 tailwindcss-animate 插件和自定义 scroll-reveal 动画

#### 5. 图片处理

- Next.js 图片优化已禁用 (`unoptimized: true`)
- 允许的外部图片域名：
  - source.unsplash.com
  - images.unsplash.com
  - ext.same-assets.com
  - ugc.same-assets.com

#### 6. same-runtime 集成

- 自定义 JSX 运行时，在 tsconfig.json 中配置
- 全局脚本在 layout.tsx 中加载
- 不要修改 `jsxImportSource` 配置

#### 7. 图标系统

项目使用集中式图标注册表管理所有动态图标：

**核心文件**：

- `src/lib/iconRegistry.ts` - 图标注册表（单一来源）
- `src/components/ui/DynamicIcon.tsx` - 动态图标组件
- `scripts/validate-icons.js` - 构建时验证脚本

**添加新图标**：

1. 在 `src/lib/iconRegistry.ts` 中注册图标：
   ```typescript
   export const iconRegistry: Record<string, LucideIcon> = {
     NewIcon: LucideIcons.NewIcon,
     // ...
   };
   ```
2. 在翻译文件（`en.json`）中使用相同的名称：
   ```json
   {
     "icon": "NewIcon"
   }
   ```
3. 运行 `bun run validate:icons` 验证

**使用图标**：

```typescript
import { DynamicIcon } from '@/components/ui/DynamicIcon'

<DynamicIcon name="Download" className="w-6 h-6" />
```

**验证图标**：

```bash
bun run validate:icons  # 手动验证
bun dev                 # 开发时自动验证
bun run build           # 构建前自动验证
```

**重要**：

- 图标名称是代码标识符，必须保持英文，不应被翻译
- 验证脚本只检查 `en.json`，其他语言文件的图标名称应与英文保持一致
- 缺失的图标会自动回退到 `HelpCircle`
- 开发环境下会在控制台显示警告

### 路径别名

在 TypeScript 中使用以下别名：

```typescript
@/components  → src/components
@/lib         → src/lib
@/ui          → src/components/ui
@/hooks       → src/hooks
```

### 添加新的 shadcn/ui 组件

1. 运行 `bunx shadcn@latest add <component-name>`
2. 组件会自动添加到 `src/components/ui/`
3. 组件使用 CVA (class-variance-authority) 管理样式变体
4. 所有组件都集成了 Tailwind CSS 和 CSS 变量系统

### 页面结构 (page.tsx)

主页面包含以下部分（按顺序）：

1. **导航栏**: 固定顶部，包含语言切换按钮（支持 7 种语言，不包含中文）
2. **Hero 部分**: 标题、描述、CTA 按钮、统计数据
3. **游戏特性**: 图片 + 描述展示
4. **工具与资源**: 8 个工具卡片网格
5. **"什么是 Anime Paradox"**: 3 个特性卡片
6. **顶级单位**: 4 个单位卡片
7. **稀有度系统**: 6 个等级展示
8. **FAQ**: 可展开的问题列表
9. **CTA 部分**: 行动号召
10. **页脚**: 4 列导航 + 版权信息

所有部分都使用 Intersection Observer 实现滚动揭示动画。

### 代码风格

- 使用 Biome 进行代码格式化
- ESLint 配置禁用了部分规则：
  - `@typescript-eslint/no-unused-vars`
  - `react/no-unescaped-entities`
  - `@next/next/no-img-element`
  - `jsx-a11y/alt-text`
- TypeScript 严格模式已启用
- 使用 Bun 作为包管理器和运行时

### 部署

- 部署平台: Netlify
- 构建命令: `bun run build`
- 发布目录: `.next`
- 配置文件: `netlify.toml`
- 跳过 Netlify Next.js 插件，使用 `@netlify/plugin-nextjs`

## 开发注意事项

1. **添加新文本内容**:
   - 首先更新 `src/locales/en.json`（主翻译文件）
   - 其他语言文件会基于 en.json 进行翻译
   - **不要创建或更新 zh.json**（项目不包含中文翻译）
2. **添加新页面**: 在 `src/app/` 下创建新目录和 `page.tsx`
3. **修改样式主题**: 编辑 `src/app/globals.css` 中的 CSS 变量
4. **添加新图片域名**: 更新 `next.config.js` 中的 `domains` 和 `remotePatterns`
5. **客户端交互**: 需要使用 `'use client'` 指令的场景：
   - 使用 React Hooks (useState, useEffect 等)
   - 访问浏览器 API (localStorage, navigator 等)
   - 事件处理器 (onClick, onChange 等)
   - 使用 Context (useContext, useLanguage 等)

## 多语言翻译工作流

### 翻译脚本选择

**优先使用增强版脚本**（推荐）：

```bash
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang [语言代码]
```

**原脚本**（仅在增强版不可用时使用）：

```bash
python3 tools/articles/modules/transpage/translate-messages.py --overwrite
```

### 何时使用增强版脚本

**必须使用增强版**的场景：

- en.json 文件较大（>5000 字符）
- 之前遇到过 token 限制错误
- 需要翻译多个语言
- 需要增量翻译（只翻译变化部分）

**增强版的优势**：

- ✅ 自动分块，避免 token 限制（8,192 tokens）
- ✅ 自动验证 JSON 格式和结构完整性
- ✅ 专有名词自动保护（游戏名、角色名）
- ✅ 智能降级重试（大块失败自动尝试小块）
- ✅ 详细错误报告

### 翻译工作流程

**重要**：当用户要求"翻译多语言文件"或"翻译 src/locales/"时，必须执行以下步骤：

#### 步骤 1：自动获取目标语言列表

**使用辅助脚本**（推荐）：

```bash
# 获取逗号分隔的语言列表
LANGS=$(node tools/articles/modules/transpage/get-target-languages.js --format comma)
echo "目标语言: $LANGS"

# 示例输出：es,pt,ja,ru,de,fr,tr
```

**手动方法**（备用）：

```bash
# 方法 1：从配置文件读取
cat tools/articles/modules/transpage/transpage_config.json | grep -A 10 '"languages"'

# 方法 2：扫描现有文件
ls src/locales/*.json | grep -v en.json | sed 's/.*\///;s/\.json//' | paste -sd ','
```

**重要**：

- 辅助脚本会优先从配置文件读取 `languages` 字段
- 如果配置文件没有，会自动扫描 `src/locales/` 目录
- 排除 `en.json`（源文件）和 `zh.json`（项目不包含中文）

#### 步骤 2：执行翻译

**场景 A：完整翻译所有语言**（用户说"翻译多语言文件"）

```bash
# 使用从配置读取的语言列表
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang [从配置读取的语言列表] --report

# 示例（假设配置中有 7 种语言）：
# python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang es,pt,ja,ru,de,fr,tr --report
```

**场景 B：增量翻译**（用户说"更新翻译"或"增量翻译"）

```bash
# 1. 备份当前 en.json
cp src/locales/en.json src/locales/en.json.backup

# 2. 用户修改 en.json

# 3. 只翻译变化部分（使用从配置读取的语言列表）
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang [语言列表] --incremental
```

**场景 C：翻译指定语言**（用户明确指定语言，如"翻译 vi 和 th"）

```bash
# 只翻译用户指定的语言
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi,th --report
```

**场景 D：修复翻译问题**（用户说"修复 vi 翻译"）

```bash
# 重新翻译单个语言，使用更小的分块策略
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi --overwrite --strategy small
```

#### 步骤 3：自动验证每个翻译的语言

对于每个翻译的语言文件，执行以下验证：

```bash
# 1. JSON 格式验证
python3 -m json.tool src/locales/[语言代码].json > /dev/null && echo "✓ [语言代码] Valid" || echo "✗ [语言代码] Invalid"

# 2. 文件大小检查（应该与 en.json 接近，±50% 范围内）
ls -lh src/locales/en.json src/locales/[语言代码].json
```

#### 步骤 4：生成验证报告

汇总所有语言的验证结果，报告给用户：

```
翻译完成：
✓ es - 有效 (12,345 字符)
✓ pt - 有效 (12,123 字符)
✗ ja - JSON 格式错误
✓ ru - 有效 (13,456 字符)
...

失败的语言：
- ja: JSON 格式错误，建议重新翻译
```

### 翻译后自动验证

**必须执行的验证步骤**：

1. **JSON 格式验证**：

```bash
python3 -m json.tool src/locales/[语言代码].json > /dev/null && echo "✓ Valid" || echo "✗ Invalid"
```

2. **结构完整性检查**：

```bash
# 比较键数量
python3 -c "import json; en=json.load(open('src/locales/en.json')); lang=json.load(open('src/locales/vi.json')); print(f'EN: {len(str(en))} chars, VI: {len(str(lang))} chars, Ratio: {len(str(lang))/len(str(en)):.2f}')"
```

3. **常见问题检查**：
   - 字段错位（如 hero.title 变成 "切换语言"）
   - FAQ 问答互换
   - 表格数据混乱
   - 字段值为空

### 问题诊断和解决

**如果翻译失败或出现问题**：

1. **查看错误类型**：
   - Token 限制错误 → 增强版脚本会自动处理
   - JSON 格式错误 → 增强版脚本会自动验证和重试
   - 字段错位 → 增强版脚本的结构验证会捕获

2. **参考文档**：
   - `需求/06增强版翻译系统使用指南.md` - 完整使用指南
   - `需求/04翻译质量解决方案.md` - 问题分析和手动修复方案

3. **降级策略**：
   - 如果增强版脚本失败，会自动尝试更小的分块
   - 如果所有策略都失败，查看 `temp/translation-reports/` 中的详细报告

### 专有名词配置

**配置文件**：`tools/articles/modules/transpage/transpage_config.json`

```json
{
  "protected_terms": {
    "game_names": ["Burglin' Gnomes"],
    "character_names": [],
    "technical_terms": ["PvP", "PvE", "HP", "XP", "DPS"]
  }
}
```

**添加新的专有名词**：

- 编辑 `protected_terms` 配置
- 重新运行翻译脚本

### 翻译命令速查

```bash
# 翻译单个语言
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi

# 翻译多个语言
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi,th,es

# 强制覆盖已有翻译
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi --overwrite

# 增量翻译（只翻译变化部分）
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi --incremental

# 生成详细报告
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi --report

# 指定分块策略
python3 tools/articles/modules/transpage/translate-messages-enhanced.py --lang vi --strategy small
```
