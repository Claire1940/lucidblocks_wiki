# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个**通用的多语言游戏攻略网站模板**，基于 Next.js 15 构建。模板提供完整的国际化、内容管理、SEO 优化和广告系统。

**模板特性**:
- **前端框架固定** - Next.js、国际化架构、MDX 系统、广告集成等核心代码保持稳定
- **内容完全可变** - 游戏主题、内容类型、支持语言、具体文章根据项目需求调整
- **快速部署新游戏** - 修改配置文件 + 替换内容目录即可适配新游戏项目

**当前实例**: Bizarre Lineage（JOJO 主题 Roblox 游戏），支持 8 种语言

## 重要工作规则

⚠️ **任务执行原则**:
1. **如果给出的任务已经完成，请跳过并进行下一步**
2. **每次只完成要求的任务，项目其余部分未经允许禁止改动/增删**
3. **每次完成任务时，自动进行构建测试（提问讨论类的任务除外）**

## 模块开发规范 🎯

### 必须遵守的三条规则

开发首页模块或任何使用翻译数据的组件时，必须严格遵守以下规则：

#### 1. 先读数据文件，复制字段名

```bash
# 开发前必做：读取数据文件，记录字段名
Read src/locales/en.json

# 直接复制粘贴字段名到代码，不要手写
# ❌ 错误：手写字段名 → 拼写错误 → 运行时崩溃
# ✅ 正确：复制粘贴字段名 → 保证准确
```

**为什么重要**：
- 手写字段名容易拼写错误（如 `featuredCards` 写成 `featureCards`）
- TypeScript 无法检测 JSON 字段名错误
- 运行时才会发现错误，浪费时间

#### 2. 渲染所有字段，不能遗漏

```typescript
// ❌ 错误：只渲染部分字段
function MyModule() {
  const t = useTypedMessages()
  return <h2>{t.myModule.title}</h2>  // 遗漏了 subtitle, cards, links 等
}

// ✅ 正确：检查数据结构，渲染所有字段
function MyModule() {
  const t = useTypedMessages()

  // 开发时先打印数据结构
  console.log('myModule fields:', Object.keys(t.myModule))
  // 输出: ['title', 'subtitle', 'featuredCards', 'sections', 'quickTips', 'sourceLinks']

  return (
    <div>
      <h2>{t.myModule.title}</h2>
      <p>{t.myModule.subtitle}</p>
      {/* 渲染 featuredCards */}
      {/* 渲染 sections */}
      {/* 渲染 quickTips */}
      {/* 渲染 sourceLinks */}
    </div>
  )
}
```

**为什么重要**：
- 数据文件中的内容是精心设计的，遗漏字段会导致内容不完整
- 用户看到的页面会缺少重要信息
- 浪费了翻译工作（翻译了但没显示）

#### 3. 提交前必须浏览器测试

```bash
# 提交前必做：构建并在浏览器中验证
npm run build && npm run dev

# 在浏览器中检查：
# 1. 滚动查看每个模块
# 2. 确认所有内容都显示（不只是标题）
# 3. 检查布局是否正确
# 4. 验证链接是否有效
```

**为什么重要**：
- 代码能编译 ≠ 页面正确显示
- 只看代码很难发现遗漏的字段
- 浏览器测试是发现问题的最后防线

### 一句话总结

**数据有什么字段，代码就渲染什么字段，提交前浏览器看一遍。**

### 检查清单

开发模块时，问自己：

- [ ] 是否已读取 `src/locales/en.json` 并记录字段名？
- [ ] 是否使用复制粘贴而不是手写字段名？
- [ ] 是否使用 `console.log(Object.keys(...))` 检查数据结构？
- [ ] 是否渲染了所有字段（title, subtitle, cards, links 等）？
- [ ] 是否在浏览器中验证了显示效果？
- [ ] 是否滚动查看了整个模块，确认内容完整？

### 常见错误示例

```typescript
// ❌ 错误 1：手写字段名拼写错误
const cards = t.tools.featureCards  // 应该是 featuredCards

// ❌ 错误 2：只渲染标题，遗漏其他字段
return <h2>{t.tools.title}</h2>  // 遗漏了 subtitle, cards, sections 等

// ❌ 错误 3：没有检查数据结构
// 不知道 tools 模块有哪些字段，凭感觉写代码

// ❌ 错误 4：没有浏览器测试
// 代码能编译就提交，没有在浏览器中验证显示效果
```

### 正确流程示例

```typescript
// ✅ 步骤 1：读取数据文件
// Read src/locales/en.json
// 找到 tools 模块，记录字段：title, subtitle, featuredCards, sections, quickTips, sourceLinks

// ✅ 步骤 2：复制字段名到代码
function ToolsSection() {
  const t = useTypedMessages()

  // ✅ 步骤 3：检查数据结构
  console.log('tools fields:', Object.keys(t.tools))

  // ✅ 步骤 4：渲染所有字段
  return (
    <section>
      <h2>{t.tools.title}</h2>
      <p>{t.tools.subtitle}</p>

      {/* featuredCards */}
      {t.tools.featuredCards?.map(card => (
        <Card key={card.title} {...card} />
      ))}

      {/* sections */}
      {t.tools.sections?.map(section => (
        <Section key={section.title} {...section} />
      ))}

      {/* quickTips */}
      {t.tools.quickTips && <QuickTips items={t.tools.quickTips} />}

      {/* sourceLinks */}
      {t.tools.sourceLinks && <SourceLinks links={t.tools.sourceLinks} />}
    </section>
  )
}

// ✅ 步骤 5：浏览器测试
// npm run build && npm run dev
// 在浏览器中滚动查看，确认所有内容都显示
```

## Development Commands

```bash
# 开发服务器（监听所有网络接口）
npm run dev

# 生产构建
npm run build

# 启动生产服务器
npm start

# 类型检查和 Lint
npm run lint

# 仅类型检查
npm run typecheck

# 代码格式化（使用 Biome）
npm run format

# 清理缓存（解决构建缓存损坏问题）
npm run clean              # 清理 .next 和 node_modules/.cache
npm run clean:all          # 清理 .next 和整个 node_modules
npm run rebuild            # 清理缓存后重新构建

# MDX 内容验证
npm run validate              # 基础验证
npm run validate:json         # JSON 格式输出
npm run validate:strict       # 严格模式
```

### 常见问题排查

**构建失败或出现奇怪错误**：
```bash
# 1. 清理缓存
npm run clean

# 2. 重新构建
npm run build

# 如果还是失败，清理所有依赖
npm run clean:all
npm install
npm run build
```

## Template Architecture

### 核心技术栈（固定）
- **框架**: Next.js 15 (App Router)
- **国际化**: next-intl（支持任意语言扩展）
- **内容**: MDX（@next/mdx + next-mdx-remote）
- **样式**: Tailwind CSS + shadcn/ui
- **类型**: TypeScript（严格模式）
- **广告**: 5 种广告格式集成
- **SEO**: 自动 sitemap、结构化数据、meta tags

### 目录结构

```
src/
├── app/                      # Next.js App Router（框架层，不变）
│   ├── [locale]/            # 国际化路由
│   │   ├── [...slug]/       # 动态内容路由（处理所有 MDX 页面）
│   │   └── page.tsx         # 首页
│   ├── layout.tsx           # 根布局
│   └── sitemap.ts           # 动态 sitemap 生成
├── components/              # UI 组件（框架层，不变）
│   ├── ads/                 # 广告组件（5种格式）
│   ├── content/             # 内容渲染组件
│   │   ├── DetailPage.tsx   # 文章详情页模板
│   │   ├── NavigationPage.tsx # 导航列表页模板
│   │   └── MDXWrapper.tsx   # MDX 渲染包装器
│   └── home/                # 首页模块组件
├── config/                  # 配置层（可变）
│   └── navigation.ts        # ⚙️ 内容类型配置（根据游戏修改）
├── i18n/                    # 国际化系统（框架层，不变）
│   ├── routing.ts           # ⚙️ 语言配置（根据需求修改）
│   └── request.ts           # 翻译加载逻辑（深度合并 fallback）
├── lib/                     # 工具库（框架层，不变）
│   └── content.ts           # MDX 内容加载逻辑
└── locales/                 # 翻译文件（内容层，可变）
    ├── en.json              # 📝 英文翻译（基准语言）
    ├── pt.json              # 📝 葡萄牙语
    ├── fr.json              # 📝 法语
    └── ...                  # 📝 其他语言

content/                      # MDX 内容文件（内容层，完全可变）
├── en/                      # 英文内容（基准语言）
│   ├── {type1}/             # 📝 内容类型 1（根据游戏定义）
│   ├── {type2}/             # 📝 内容类型 2
│   └── ...
└── {locale}/                # 其他语言（结构同 en）

tools/                        # Python 工具集（辅助层，可选使用）
├── articles/                # AI 文章生成工具
│   ├── modules/
│   │   ├── generation/      # GPT-4o 批量生成
│   │   ├── translate/       # 多语言翻译
│   │   └── transpage/       # 页面翻译
│   └── logs/                # 生成日志
├── content_pipeline/        # 内容采集管道
│   ├── collect.py           # 从 YouTube/Web 采集
│   ├── extract.py           # 提取关键词
│   └── core/                # 核心模块
└── validate_mdx.py          # MDX 验证工具
```

**图例**:
- 框架层（不变）: 核心代码，跨项目复用
- 配置层（可变）: ⚙️ 根据游戏调整
- 内容层（可变）: 📝 完全替换

## Adapting Template for New Game

### 步骤 1: 修改内容类型配置

编辑 `src/config/navigation.ts`，定义新游戏的内容类型：

```typescript
export const NAVIGATION_CONFIG: NavigationItem[] = [
  { key: 'guides', path: '/guides', icon: BookOpen, isContentType: true },
  { key: 'characters', path: '/characters', icon: Users, isContentType: true },
  { key: 'items', path: '/items', icon: Package, isContentType: true },
  // ... 根据新游戏添加/删除类型
]
```

**影响范围**: 导航菜单、路由、内容加载、sitemap 生成

### 步骤 2: 配置支持语言

编辑 `src/i18n/routing.ts`，调整支持的语言：

```typescript
export const routing = defineRouting({
  locales: ['en', 'es', 'pt', 'fr'], // 根据目标市场调整
  defaultLocale: 'en'
})
```

### 步骤 3: 更新翻译文件

1. 编辑 `src/locales/en.json`（基准语言）：
```json
{
  "nav": {
    "guides": "Guides",
    "characters": "Characters",
    "items": "Items"
  },
  "home": {
    "title": "New Game Wiki",
    "description": "..."
  }
}
```

2. 使用 Python 工具翻译其他语言：
```bash
cd tools/articles/modules/transpage
python translate-all-locales.py --overwrite
```

**说明**：
- 自动从 `src/i18n/routing.ts` 读取目标语言列表
- 翻译所有非英文语言到 `src/locales/` 目录
- 使用 `--overwrite` 覆盖已有翻译文件

### 步骤 4: 替换内容目录

1. 清空 `content/` 目录
2. 创建新的内容结构：
```
content/
├── en/
│   ├── guides/
│   │   └── beginner.mdx
│   ├── characters/
│   │   └── hero-name.mdx
│   └── items/
│       └── item-name.mdx
└── {locale}/  # 其他语言
```

3. 使用 Python 工具生成内容（可选）：
```bash
cd tools/articles/modules/generation
python api_client.py
```

### 步骤 5: 更新首页内容

编辑 `src/app/[locale]/page.tsx` 和 `src/components/home/` 中的组件，调整首页展示内容。

### 步骤 6: 验证和部署

```bash
# 验证 MDX 文件
npm run validate

# 类型检查
npm run typecheck

# 本地测试
npm run dev

# 生产构建
npm run build
```

## Key Architecture Patterns

### 1. 内容类型系统（单一配置源）

所有内容类型在 `src/config/navigation.ts` 中统一定义：
- 导航菜单自动生成
- 路由自动配置
- 内容加载自动处理
- Sitemap 自动包含

**修改内容类型时只需更新此文件**，无需修改多处代码。

### 2. 国际化架构（深度 Fallback）

- **翻译 Fallback**: 所有语言深度合并英文翻译（`src/i18n/request.ts`）
- **内容 Fallback**: MDX 文件缺失时自动回退到英文版本（`src/lib/content.ts`）
- **零错误**: 翻译或内容缺失不会导致页面报错

### 3. MDX 内容加载（动态导入）

- 使用 `import()` 动态加载 MDX（支持 metadata 导出）
- 支持递归目录结构（如 `guides/pvp/advanced.mdx`）
- 自动按日期排序
- 支持嵌套分类

### 4. 广告系统（5 种格式）

位置：`src/components/ads/`

- `AdBanner`: 横幅广告（页面顶部/底部）
- `NativeBannerAd`: 原生横幅（内容中）
- `IframeBannerAd`: iframe 横幅（灵活嵌入）
- `SidebarAd`: 侧边栏广告（桌面端）
- `SocialBarAd`: 社交栏广告（移动端）

**集成位置**:
- 首页: `src/app/[locale]/page.tsx`
- 详情页: `src/components/content/DetailPage.tsx`

### 5. SEO 优化（自动化）

- **Meta Tags**: 从 MDX metadata 自动生成
- **Sitemap**: `src/app/sitemap.ts` 动态生成所有页面
- **结构化数据**: `ArticleStructuredData.tsx` 自动添加 JSON-LD
- **多语言 SEO**: 自动生成 hreflang 标签

## Content Management

### MDX 文件格式（标准）

```mdx
export const metadata = {
  title: "文章标题",
  description: "155 字符以内的描述",
  category: "类别",
  date: "2025-01-20",
  lastModified: "2025-01-21",
  image: "/images/cover.jpg",
  themeColor: "1e40af",  // 可选：自定义主题色
}

## 标题（H2）

内容...

### 子标题（H3）

更多内容...
```

**重要规则**:
- ✅ 使用 `export const metadata` 而非 YAML frontmatter
- ✅ 必须包含 `title` 和 `description`
- ❌ 不要使用 H1（页面模板自动使用 `title` 作为 H1）
- ✅ 支持 Markdown 和 React 组件混合

### 内容组织建议

```
content/en/{type}/
├── category1/
│   ├── article1.mdx
│   └── article2.mdx
├── category2/
│   └── article3.mdx
└── standalone.mdx
```

- 支持任意深度的目录嵌套
- URL 自动生成：`/{locale}/{type}/category1/article1`
- 分类可选，单篇文章可直接放在类型根目录

## Python Tools (Optional)

### 文章生成工具

```bash
# 生成英文文章
cd tools/articles/modules/generation
python api_client.py

# 翻译到其他语言
cd tools/articles/modules/translate
python translator.py

# 翻译页面内容（locales/*.json）
cd tools/articles/modules/transpage
python translate-all-locales.py --overwrite

# 或使用原脚本（手动指定语言）
python translate-messages-enhanced.py --lang es,pt,ja,ru,de,fr,tr --overwrite
```

**推荐使用 `translate-all-locales.py`**：
- 自动从 `src/i18n/routing.ts` 读取语言列表
- 避免手动输入错误
- 确保与项目配置一致

**配置文件**:
- `tools/articles/modules/generation/config.json`: API 配置
- `tools/articles/modules/translate/translate_config.json`: 翻译配置
- `tools/articles/modules/transpage/transpage_config.json`: 页面翻译配置

### 内容采集管道

```bash
# 采集 YouTube 视频和网页内容
python tools/content_pipeline/collect.py

# 提取关键词
python tools/content_pipeline/extract.py

# 完整管道
python tools/content_pipeline/pipeline.py
```

### MDX 验证

```bash
# 验证所有 MDX 文件
python tools/validate_mdx.py

# 严格模式（检查图片、链接等）
python tools/validate_mdx.py --strict

# JSON 输出（用于 CI）
python tools/validate_mdx.py --format json
```

## Common Workflows

### 添加新的内容类型

1. 修改 `src/config/navigation.ts`
2. 在 `src/locales/en.json` 添加翻译键（`nav.{key}`）
3. 创建 `content/en/{type}/` 目录
4. 添加 MDX 文件
5. 运行 `npm run dev` 验证

### 添加新语言

1. 修改 `src/i18n/routing.ts` 添加语言代码
2. 创建 `src/locales/{locale}.json`
3. 创建 `content/{locale}/` 目录
4. 使用翻译工具或手动翻译内容

### 修改首页布局

编辑 `src/app/[locale]/page.tsx` 和 `src/components/home/` 中的模块组件。首页采用模块化设计，可自由组合。

### 调整广告位置

广告组件已集成到页面模板中：
- 首页: `src/app/[locale]/page.tsx`
- 详情页: `src/components/content/DetailPage.tsx`
- 导航页: `src/components/content/NavigationPage.tsx`

直接在模板中调整组件位置即可。

## Important Notes

### 不要修改的部分（框架层）

- `src/app/` 路由结构
- `src/lib/content.ts` 内容加载逻辑
- `src/i18n/request.ts` 国际化逻辑
- `src/components/content/` 渲染组件
- `src/components/ads/` 广告组件

### 需要修改的部分（配置/内容层）

- `src/config/navigation.ts` - 内容类型
- `src/i18n/routing.ts` - 支持语言
- `src/locales/*.json` - 翻译文件
- `content/` - 所有 MDX 内容
- `src/app/[locale]/page.tsx` - 首页内容
- `src/components/home/` - 首页模块

### 常见问题

**MDX 文件不显示**:
- 检查 `metadata` 导出格式
- 确认文件路径与内容类型匹配
- 运行 `npm run validate` 检查语法

**翻译缺失**:
- 英文翻译会自动 fallback，不会报错
- 检查 `src/locales/en.json` 是否包含对应的键

**类型错误**:
- 运行 `npm run typecheck` 检查
- 确保 `src/config/navigation.ts` 中的类型定义正确

**Python 工具报错**:
- 检查 `.env` 文件中的 API 密钥
- 确认 Python 依赖已安装（`pip install -r requirements.txt`）
- 查看 `tools/articles/logs/` 中的错误日志

## Deployment

项目配置为 Docker standalone 模式（`next.config.mjs` 中 `output: 'standalone'`）：

```bash
# 构建
npm run build

# 启动
npm start
```

生成的 `.next/standalone` 目录包含完整的生产环境文件。

## Template Philosophy

这个模板的设计哲学是**分离关注点**：

- **框架层**（Next.js、国际化、MDX）提供稳定的技术基础
- **配置层**（navigation.ts、routing.ts）提供灵活的定制点
- **内容层**（MDX 文件、翻译）完全独立，可快速替换

这种设计使得同一套代码可以支持不同游戏项目，只需修改配置和内容，无需重写框架代码。

## Git 提交检查清单 ⚠️

### 核心原则：原子性提交

**每次提交都应该是一个可独立部署的完整单元**，不能包含"半成品"代码。

```
❌ 错误做法：
Commit 1: 修改 en.json（添加图标引用）
Commit 2: 修改 iconRegistry.ts（注册图标）
         ↑ CI 在这里失败，因为 Commit 1 已经引用了不存在的图标

✅ 正确做法：
Commit 1: en.json + iconRegistry.ts + page.tsx（所有相关文件一起提交）
         ↑ 代码始终保持完整状态
```

### 文件依赖关系（必须同时提交）

```
locales/*.json (使用图标)
    ↓ 必须同时提交
src/lib/iconRegistry.ts (注册图标)

src/config/navigation.ts (定义导航项)
    ↓ 必须同时提交
locales/en.json (nav.* 翻译键)

src/app/[locale]/page.tsx (使用组件)
    ↓ 必须同时提交
src/components/home/* (组件实现)

需求/automation/game.config.json (配置文件)
    ↓ 必须同时提交
所有使用该配置的代码文件
```

### 提交前强制检查清单

**每次提交前必须执行以下步骤**：

```bash
# 1. 检查所有修改的文件
git status
git diff

# 2. 识别依赖关系（问自己）
# - 修改了 locales/*.json 添加图标？→ iconRegistry.ts 必须一起提交
# - 修改了 page.tsx 使用新组件？→ 组件文件必须一起提交
# - 修改了配置文件？→ 使用该配置的代码必须一起提交

# 3. 运行所有验证（必做！）
npm run build                      # 构建测试
node scripts/validate-icons.js     # 图标验证（关键！）
npm run typecheck                  # 类型检查

# 4. 确认暂存区包含所有相关文件
git diff --cached
# 检查：是否所有依赖文件都已暂存？

# 5. 提交
git commit -m "feat: 完整的功能描述"
```

### 关键认知

- ❌ **本地构建通过 ≠ CI 构建通过**（CI 环境更干净、更严格）
- ✅ **相关文件必须在同一个 commit 中**，不能分开提交
- ✅ **CI 失败要立即修复**，不累积问题
- ✅ **提交前必须运行验证脚本**，特别是 `validate-icons.js`

### 图标系统特别说明

项目使用 `scripts/validate-icons.js` 在构建时自动验证：
1. 检查 `src/lib/iconRegistry.ts` 中注册的图标
2. 检查 `locales/*.json` 中使用的图标
3. 如果有缺失 → 退出码 1 → 构建失败

**强制规则**：
- 修改 `locales/*.json` 添加图标引用时，必须同时更新 `src/lib/iconRegistry.ts`
- 两个文件必须在同一个 commit 中
- 提交前必须手动运行 `node scripts/validate-icons.js`

### Claude Code 工作流程

作为 AI 助手，在每次修改代码后应该：

1. **识别依赖关系** - 检查修改的文件是否相互依赖
2. **确保完整性** - 所有相关文件都已修改
3. **运行验证** - 执行构建和验证脚本
4. **检查暂存区** - 确认所有相关文件都已暂存
5. **原子性提交** - 一次提交包含所有相关变更

## 类型安全最佳实践 🛡️

### 核心问题：TypeScript 的"谎言"

**问题**：TypeScript 只在编译时检查，运行时数据可能不符合类型定义。

```typescript
// ❌ 错误做法
const t = useMessages() as any  // 完全放弃类型检查

return (
  <div>
    {t.tools.cards.map((card: any) => (  // 💥 如果 cards 是 undefined 会崩溃
      <div>{card.title}</div>
    ))}
  </div>
)
```

### 三层架构解决方案

```
┌─────────────────────────────────────┐
│  数据层（JSON）- 字段可选            │  ← 反映真实的 JSON 结构
├─────────────────────────────────────┤
│  适配层（验证和转换）                │  ← 检查数据，提供默认值
├─────────────────────────────────────┤
│  组件层（使用数据）- 字段必需        │  ← 保持纯粹，不处理 undefined
└─────────────────────────────────────┘
```

### 1. 使用类型安全的 Hook

```typescript
// ✅ 正确做法
import { useTypedMessages, useSafeArray, useHasData } from '@/hooks/useTypedMessages'

function MyComponent() {
  const t = useTypedMessages()  // 类型安全
  const cards = useSafeArray(t.tools.cards)  // 安全获取，返回空数组而不是崩溃
  const hasCards = useHasData(t.tools.cards)  // 检查是否有数据

  if (!hasCards) {
    return <EmptyState />  // 优雅降级
  }

  return <CardList cards={cards} />  // 传递时保证数据有效
}
```

### 2. 使用 Zod 进行运行时验证

项目已集成 Zod schema 验证：

```bash
# 验证所有翻译文件
npm run validate:translations

# 在构建时自动运行
npm run build  # 会自动验证翻译
```

**验证脚本位置**：
- Schema 定义：`src/lib/translationSchema.ts`
- 验证脚本：`scripts/validate-translations.js`

### 3. 组件开发规范

#### A. 数据层接口（反映 JSON 结构）

```typescript
// src/types/translations.ts
export interface ToolsModule {
  title: string
  subtitle: string
  cards?: IconCard[]  // 可选，因为 JSON 可能没有
}
```

#### B. 组件层接口（要求数据存在）

```typescript
// 组件要求数据必须存在
interface CardListProps {
  cards: IconCard[]  // 必需！
}

function CardList({ cards }: CardListProps) {
  // 不需要检查 undefined，因为适配层已经保证了
  return (
    <div>
      {cards.map(card => (
        <Card key={card.title} {...card} />
      ))}
    </div>
  )
}
```

#### C. 适配层（验证和转换）

```typescript
// 在页面或容器组件中做适配
function ToolsSection() {
  const t = useTypedMessages()
  const cards = useSafeArray(t.tools.cards)

  if (cards.length === 0) {
    return <EmptyState />
  }

  // 传递给组件时，保证数据有效
  return <CardList cards={cards} />
}
```

### 4. 使用判别联合类型

当需要处理多种数据结构时，使用判别联合而不是"万能接口"：

```typescript
// ❌ 错误：万能接口（字段膨胀）
interface Card {
  title?: string      // Build 卡片用
  name?: string       // Companion 卡片用
  stats?: object      // Build 卡片用
  roleTags?: string[] // Companion 卡片用
}

// ✅ 正确：判别联合类型
type BuildCard = {
  type: 'build'
  title: string
  stats: Record<string, number>
}

type CompanionCard = {
  type: 'companion'
  name: string
  roleTags: string[]
}

type Card = BuildCard | CompanionCard

// 使用类型守卫
function renderCard(card: Card) {
  if (card.type === 'build') {
    // TypeScript 知道这里只能是 BuildCard
    return <div>{card.title}</div>  // ✅ 有 title
  }

  if (card.type === 'companion') {
    // TypeScript 知道这里只能是 CompanionCard
    return <div>{card.name}</div>  // ✅ 有 name
  }
}
```

### 5. 防御性编程检查清单

在编写组件时，问自己：

- [ ] 是否使用了 `as any`？（应该避免）
- [ ] 是否直接调用 `.map()` 而没有检查数组存在？
- [ ] 是否访问了深层嵌套的属性而没有可选链？
- [ ] 是否为可选字段提供了默认值？
- [ ] 是否有空状态 UI？
- [ ] 是否使用了类型守卫来区分不同的数据结构？

### 6. 验证流程

```bash
# 开发时
npm run dev  # 自动验证图标

# 提交前
git add .
git commit  # pre-commit hook 会自动验证

# 构建时
npm run build  # 验证图标 + 验证翻译 + 构建
```

### 7. 示例文件

参考这些文件了解完整的实现：

- **类型定义**：`src/types/translations.ts`
- **Schema 验证**：`src/lib/translationSchema.ts`
- **类型安全 Hook**：`src/hooks/useTypedMessages.ts`
- **示例组件**：`src/components/home/ToolsSection.example.tsx`
- **验证脚本**：`scripts/validate-translations.js`

### 8. 关键原则

1. **不要信任 TypeScript** - 类型正确 ≠ 运行时正确
2. **在边界处验证** - 数据进入系统时立即验证（Zod）
3. **分离关注点** - 数据层、适配层、组件层各司其职
4. **优雅降级** - 显示空状态而不是崩溃
5. **类型和运行时双重保护** - TypeScript 类型 + Zod 验证
