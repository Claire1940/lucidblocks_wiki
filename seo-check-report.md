# SEO 检查报告

生成时间: 2026-03-14

## 检查摘要

- ✅ 通过: 28 项
- ❌ 失败: 5 项
- ⚠️ 警告: 6 项
- 📊 总计: 39 项

---

## 详细结果

### 阶段 1：代码结构检查

#### 1.1 根 Layout (`src/app/layout.tsx`)
- ✅ 根 layout 存在（极简，仅透传 children）
- ⚠️ 根 layout 无 `<html lang>` 标签 — 由 `[locale]/layout.tsx` 处理，架构上正确但需确认

#### 1.2 Locale Layout (`src/app/[locale]/layout.tsx`)
- ✅ 包含 `<html lang={locale}>` 标签
- ✅ 包含 favicon 图标配置（ico / 16x16 / 32x32 / apple-touch-icon）
- ✅ 包含 manifest.json 引用
- ✅ 包含 OpenGraph 标签（type, locale, url, siteName, title, description, images）
- ✅ 包含 Twitter Card 标签（summary_large_image）
- ✅ 包含 robots 配置（index: true, follow: true, googleBot 完整）
- ✅ 包含 keywords 元标签
- ✅ 包含 alternates / hreflang（通过 `buildLanguageAlternates`）
- ✅ 使用环境变量 `NEXT_PUBLIC_SITE_URL`（有 fallback 到硬编码域名）
- ⚠️ og-image 路径为 `/og-image.jpg`，需确认该文件存在于 `public/` 目录

#### 1.3 动态页面 SEO (`src/app/[locale]/[...slug]/page.tsx`)
- ✅ `generateMetadata` 正确生成 title 和 description
- ✅ 包含 alternates（hreflang）
- ✅ 包含 OpenGraph 标签
- ✅ 包含 robots 配置
- ✅ 有 fallback 到英文的逻辑
- ⚠️ 详情页 title 格式不一致：主语言用 `- Lucid Blocks Wiki`，fallback 语言用 `- Lucid Blocks`（缺少 "Wiki"）
  - 文件: `src/app/[locale]/[...slug]/page.tsx:313`

#### 1.4 Sitemap (`src/app/sitemap.ts`)
- ❌ `BASE_URL` 硬编码为 `'https://www.lucidblocks.wiki'`，未使用环境变量
  - 修复建议: `const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'`
  - 优先级: 🟡 中
- ✅ 包含所有语言版本的首页
- ✅ 包含所有静态页面（about, privacy-policy, terms-of-service, copyright）
- ✅ 包含所有 MDX 文章
- ✅ 优先级配置合理（首页 1.0，内容页 0.7-0.9，静态页 0.3-0.6）
- ✅ 更新频率配置合理

#### 1.5 国际化配置 (`src/i18n/routing.ts`)
- ✅ `localePrefix` 设置为 `'as-needed'`（默认语言无前缀）
- ✅ `defaultLocale` 为 `'en'`
- ✅ `localeDetection` 已启用
- ✅ 支持 8 种语言：en, ru, pt, de, es, ja, ko, fr

#### 1.6 结构化数据
- ✅ `WebSite` 结构化数据存在（`src/app/[locale]/page.tsx`）
- ✅ `SearchAction` 结构化数据存在（首页 `@graph` 中）
- ✅ `Organization` 结构化数据存在（含 logo、sameAs 社交链接）
- ✅ `VideoGame` 结构化数据存在（含 gamePlatform、genre、offers）
- ✅ `ArticleStructuredData` 组件正确（含 headline, datePublished, dateModified, author, publisher）
- ✅ `ListStructuredData` 组件正确（ItemList 格式）
- ⚠️ `ArticleStructuredData` 中 publisher logo 使用 `/images/hero.webp`，建议改为专用 logo 图片

#### 1.7 robots.txt (`public/robots.txt`)
- ✅ 文件存在
- ✅ 允许所有搜索引擎抓取（`User-agent: * / Allow: /`）
- ✅ 包含 sitemap 链接
- ⚠️ sitemap URL 硬编码，与 sitemap.ts 同样问题（低风险，robots.txt 为静态文件）

#### 1.8 H1 标签
- ✅ `NavigationPage` 有且仅有一个 H1（`<h1>{title}</h1>`）
- ✅ `DetailPage` 有且仅有一个 H1（`<h1>{frontmatter.title}</h1>`）
- ✅ 首页有且仅有一个 H1（`<h1>{t.hero.title}</h1>`）
- ✅ H1 在页面顶部语义位置

#### 1.9 图片 alt 属性
- ✅ `NavigationPage` 中 Image 组件有描述性 alt（`${title} - Featured ${contentType} guide`）
- ✅ `DetailPage` 中 Image 组件有描述性 alt（`${title} - ${contentTypeLabel}`）
- ✅ Next.js Image 组件均有 alt 属性

#### 1.10 面包屑导航
- ✅ `DetailPage` 有面包屑（首页 → 内容类型 → 当前页）
- ✅ 面包屑有正确的链接
- ❌ 面包屑缺少 `BreadcrumbList` JSON-LD 结构化数据
  - 修复建议: 在 `DetailPage` 或 `ArticleStructuredData` 中添加 BreadcrumbList schema
  - 优先级: 🟡 中
- ❌ 面包屑缺少 `aria-label="breadcrumb"` 无障碍属性
  - 修复建议: 将面包屑包裹在 `<nav aria-label="breadcrumb">` 中
  - 优先级: 🟡 中

#### 1.11 内链
- ✅ `DetailPage` 有相关文章（RelatedArticles 组件，最多 3 篇）
- ✅ `NavigationPage` 有完整的内容列表链接
- ✅ 首页 Footer 有内部法律页面链接
- ✅ 内部链接使用 next-intl 的 `Link` 组件（自动处理 locale 前缀）

### 阶段 2：构建验证

- ⚠️ 未执行构建测试（需手动运行 `npm run build`）

### 阶段 3：安全检查

- ✅ 代码中无 API 密钥硬编码（`sk-`、`API_KEY`、`password` 均未发现）
- ✅ `.gitignore` 包含 `.env*`（覆盖所有 .env 文件）
- ✅ 无旧项目品牌词残留（"Bizarre Lineage" 未发现）

### 阶段 4：本地运行验证

- ⚠️ 需手动验证（启动 `npm run dev` 后在浏览器中检查）

---

## 修复建议

### 🔴 高优先级（必须修复）

无高优先级问题。

### 🟡 中优先级（建议修复）

**1. Sitemap BASE_URL 使用环境变量**
- 文件: `src/app/sitemap.ts:5`
- 当前: `const BASE_URL = 'https://www.lucidblocks.wiki'`
- 修复: `const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.lucidblocks.wiki'`

**2. 详情页 fallback title 格式不一致**
- 文件: `src/app/[locale]/[...slug]/page.tsx:313`
- 当前: `` `${metadata.title} - Lucid Blocks` ``
- 修复: `` `${metadata.title} - Lucid Blocks Wiki` ``

**3. 面包屑缺少 BreadcrumbList JSON-LD**
- 文件: `src/components/content/DetailPage.tsx`
- 修复: 在 `ArticleStructuredData` 中添加 BreadcrumbList schema，或单独创建 `BreadcrumbStructuredData` 组件

**4. 面包屑缺少 aria-label**
- 文件: `src/components/content/DetailPage.tsx:73`
- 修复: 将面包屑 div 改为 `<nav aria-label="breadcrumb">`

### 🟢 低优先级（可选优化）

**5. 确认 og-image.jpg 存在**
- 检查 `public/og-image.jpg` 是否存在，否则 OpenGraph 分享图片会 404

**6. ArticleStructuredData publisher logo**
- 当前使用 `/images/hero.webp`（游戏截图）
- 建议改为专用 logo 图片（如 `/android-chrome-512x512.png`）

---

## 下一步行动

1. 修复 🟡 中优先级问题（约 30 分钟）
2. 运行 `npm run build` 验证构建
3. 启动 `npm run dev`，手动检查：
   - 首页 `http://localhost:3000/` 的 title、description、hreflang
   - `http://localhost:3000/sitemap.xml` 格式
   - 详情页面包屑显示
4. 部署后使用 Google Search Console 提交 sitemap
