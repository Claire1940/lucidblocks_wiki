# [locale]/guides/[slug]/page.tsx 动态攻略页面介绍

## 一、应用场景

`src/app/[locale]/guides/[slug]/page.tsx` 是一个**双层动态路由页面**，用于展示游戏攻略的详细内容。在本项目中的作用：

1. **多语言攻略展示**：支持 `/en/guides/beginner-guide` 和 `/zh/guides/beginner-guide`
2. **MDX 内容渲染**：从 `content/` 目录加载 MDX 文件并渲染
3. **静态生成优化**：构建时预生成所有攻略页面
4. **SEO 优化**：自动生成元数据、Open Graph 标签、多语言链接
5. **错误处理**：处理无效语言、不存在的攻略等情况
6. **动态导入**：按需加载 MDX 内容，提升性能

---

## 二、基础知识

### 2.1 Next.js 嵌套动态路由

#### **双层动态段**
```
src/app/[locale]/guides/[slug]/page.tsx
```

**路由匹配**：
- `/en/guides/beginner-guide` → `{ locale: "en", slug: "beginner-guide" }`
- `/zh/guides/advanced-tips` → `{ locale: "zh", slug: "advanced-tips" }`
- `/en/guides/tower-placement` → `{ locale: "en", slug: "tower-placement" }`

**文件系统映射**：
```
content/
├── en/
│   └── guide/
│       ├── beginner-guide.mdx
│       ├── advanced-tips.mdx
│       └── tower-placement.mdx
└── zh/
    └── guide/
        ├── beginner-guide.mdx
        ├── advanced-tips.mdx
        └── tower-placement.mdx
```

### 2.2 MDX 动态导入

#### **动态 import()**
```typescript
const { default: MDXContent, metadata } = await import(
  `../../../../../content/${language}/guide/${slug}.mdx`
)
```

**工作原理**：
1. 使用模板字符串构建文件路径
2. `await import()` 异步加载模块
3. 返回 MDX 组件（`default`）和元数据（`metadata`）

**优势**：
- 按需加载，减少初始包大小
- 支持代码分割（Code Splitting）
- 可以在运行时决定加载哪个文件

#### **MDX 导出**
```mdx
---
title: "新手攻略"
description: "适合新手的完整指南"
date: "2024-01-20"
---

export const metadata = {
  title: "新手攻略",
  description: "适合新手的完整指南",
  date: "2024-01-20"
}

# 新手攻略内容

这里是攻略正文...
```

- `default` 导出：MDX 编译后的 React 组件
- `metadata` 导出：frontmatter 数据

### 2.3 Next.js 渲染模式

#### **dynamic 配置**
```typescript
export const dynamic = 'force-dynamic'
```

**渲染模式**：
- `'auto'`（默认）：自动选择静态或动态
- `'force-static'`：强制静态生成（SSG）
- `'force-dynamic'`：强制动态渲染（SSR）
- `'error'`：如果页面是动态的则报错

**本项目使用 `'force-dynamic'` 的原因**：
- 注释说明："临时禁用静态生成以获取更详细的错误信息"
- 开发阶段便于调试
- 生产环境建议改为 `'force-static'` 或移除此配置

### 2.4 Next.js 元数据生成

#### **generateMetadata()**
```typescript
export async function generateMetadata({ params }) {
  // 返回元数据对象
  return {
    title: "...",
    description: "...",
    openGraph: {...},
    alternates: {...}
  }
}
```

**作用**：
- 动态生成页面的 `<head>` 标签
- 支持 SEO 优化
- 自动处理 Open Graph、Twitter Cards 等

**元数据类型**：
- `title`：页面标题
- `description`：页面描述
- `openGraph`：社交媒体分享卡片
- `alternates`：多语言链接和规范链接

---

## 三、代码实现和作用

### 3.1 导入依赖 (第 1-9 行)

```typescript
import {
	getAllContentSlugs,
	isValidLanguage,
	getDefaultLanguage,
	type Language,
} from '@/lib/content'
import { DetailPage } from '@/components/content/DetailPage'
import { redirect, notFound } from 'next/navigation'
import type { ContentFrontmatter } from '@/lib/content'
```

**各依赖作用**：

#### **@/lib/content 工具函数**
- `getAllContentSlugs()`：获取所有攻略的 slug 列表
- `isValidLanguage()`：验证语言参数是否有效
- `getDefaultLanguage()`：获取默认语言（'en'）
- `Language` 类型：`'en' | 'zh'`

#### **DetailPage 组件**
- 通用的详情页面组件
- 接收 frontmatter、content、contentType 等参数
- 负责渲染页面布局和内容

#### **Next.js 导航函数**
- `redirect()`：重定向到其他页面
- `notFound()`：触发 404 页面

#### **ContentFrontmatter 类型**
```typescript
interface ContentFrontmatter {
  title: string
  description: string
  category?: string
  image?: string
  date?: string
  author?: string
}
```

---

### 3.2 渲染模式配置 (第 11-12 行)

```typescript
// 临时禁用静态生成以获取更详细的错误信息
export const dynamic = 'force-dynamic'
```

**作用**：
- 强制使用服务端渲染（SSR）
- 每次请求都重新生成页面

**开发 vs 生产**：
```typescript
// 开发阶段（当前）
export const dynamic = 'force-dynamic'  // 便于调试

// 生产环境（建议）
// 移除此行，使用默认的静态生成
```

**性能影响**：
- SSR：每次请求都需要服务器处理
- SSG：构建时生成，访问时直接返回 HTML

---

### 3.3 类型定义 (第 14-19 行)

```typescript
interface GuidePageProps {
	params: Promise<{
		locale: string
		slug: string
	}>
}
```

**作用**：
- 定义页面组件的 props 类型
- `params` 包含两个动态路由参数

**参数说明**：
- `locale`：语言代码（从 URL 的 `[locale]` 段提取）
- `slug`：攻略标识符（从 URL 的 `[slug]` 段提取）

**示例**：
```
URL: /zh/guides/beginner-guide
→ params = { locale: "zh", slug: "beginner-guide" }
```

---

### 3.4 页面组件 (第 21-47 行)

#### **3.4.1 函数签名和参数提取 (第 21-22 行)**

```typescript
export default async function GuidePage({ params }: GuidePageProps) {
	const { locale, slug } = await params
```

**关键点**：
- `async function`：异步服务器组件
- `await params`：Next.js 15 的 Promise 参数
- 解构提取 `locale` 和 `slug`

---

#### **3.4.2 语言验证和类型转换 (第 24 行)**

```typescript
const language: Language = isValidLanguage(locale) ? (locale as Language) : getDefaultLanguage()
```

**逻辑分解**：
```typescript
// 如果 locale 是有效语言（'en' 或 'zh'）
if (isValidLanguage(locale)) {
  language = locale as Language  // 类型断言
} else {
  language = getDefaultLanguage()  // 使用默认语言 'en'
}
```

**为什么需要类型断言？**
- `locale` 类型是 `string`（来自 URL）
- `Language` 类型是 `'en' | 'zh'`（字面量类型）
- 需要断言告诉 TypeScript：这个 string 确实是 Language

---

#### **3.4.3 无效语言重定向 (第 26-28 行)**

```typescript
if (!isValidLanguage(locale)) {
	redirect(`/${getDefaultLanguage()}/guides/${slug}`)
}
```

**作用**：
- 如果用户访问不支持的语言，重定向到默认语言

**示例**：
```
用户访问: /fr/guides/beginner-guide
→ locale = "fr"
→ isValidLanguage("fr") = false
→ redirect("/en/guides/beginner-guide")
```

**用户体验**：
- 不会显示 404 页面
- 自动跳转到英文版本
- 保留原始的 slug

---

#### **3.4.4 MDX 内容加载 (第 30-43 行)**

```typescript
try {
	// 一次导入，同时获取内容组件和元数据
	const { default: MDXContent, metadata } = await import(
		`../../../../../content/${language}/guide/${slug}.mdx`
	)

	return (
		<DetailPage
			frontmatter={metadata as ContentFrontmatter}
			content={<MDXContent />}
			contentType="guides"
			language={language}
		/>
	)
} catch (error) {
	notFound()
}
```

**执行流程**：

##### **1. 动态导入 MDX 文件**
```typescript
const { default: MDXContent, metadata } = await import(
  `../../../../../content/${language}/guide/${slug}.mdx`
)
```

**路径构建**：
```typescript
// 示例：locale = "zh", slug = "beginner-guide"
`../../../../../content/zh/guide/beginner-guide.mdx`

// 相对路径解析：
// 当前文件：src/app/[locale]/guides/[slug]/page.tsx
// 目标文件：content/zh/guide/beginner-guide.mdx
// 需要向上 6 级：../ × 6
```

**导入结果**：
- `MDXContent`：React 组件（渲染 MDX 内容）
- `metadata`：frontmatter 对象

##### **2. 渲染 DetailPage 组件**
```typescript
<DetailPage
  frontmatter={metadata as ContentFrontmatter}
  content={<MDXContent />}
  contentType="guides"
  language={language}
/>
```

**props 说明**：
- `frontmatter`：元数据（标题、描述、日期等）
- `content`：MDX 组件实例（实际内容）
- `contentType`：内容类型（用于面包屑、导航等）
- `language`：当前语言

##### **3. 错误处理**
```typescript
catch (error) {
  notFound()
}
```

**触发条件**：
- MDX 文件不存在
- 文件路径错误
- MDX 编译错误

**用户体验**：
```
用户访问: /zh/guides/non-existent
→ 尝试导入 content/zh/guide/non-existent.mdx
→ 文件不存在，抛出错误
→ catch 捕获错误
→ 调用 notFound()
→ 显示 404 页面
```

---

### 3.5 静态参数生成 (第 49-60 行)

```typescript
export async function generateStaticParams() {
	const languages: Language[] = ['en', 'zh']
	const params: { locale: string; slug: string }[] = []

	for (const lang of languages) {
		const slugs = await getAllContentSlugs('guide', lang)
		params.push(...slugs.map((slug) => ({ locale: lang, slug })))
	}

	return params
}
```

**作用**：
- 告诉 Next.js 在构建时生成哪些页面
- 遍历所有语言和 slug 组合

**执行流程**：

##### **1. 定义语言列表**
```typescript
const languages: Language[] = ['en', 'zh']
```

##### **2. 遍历每种语言**
```typescript
for (const lang of languages) {
  const slugs = await getAllContentSlugs('guide', lang)
  // ...
}
```

**getAllContentSlugs() 的作用**：
```typescript
// 读取 content/en/guide/ 目录
// 返回所有 .mdx 文件的文件名（不含扩展名）
// 例如：['beginner-guide', 'advanced-tips', 'tower-placement']
```

##### **3. 生成参数组合**
```typescript
params.push(...slugs.map((slug) => ({ locale: lang, slug })))
```

**示例**：
```typescript
// 假设有以下文件：
// content/en/guide/beginner-guide.mdx
// content/en/guide/advanced-tips.mdx
// content/zh/guide/beginner-guide.mdx
// content/zh/guide/advanced-tips.mdx

// 生成的 params：
[
  { locale: 'en', slug: 'beginner-guide' },
  { locale: 'en', slug: 'advanced-tips' },
  { locale: 'zh', slug: 'beginner-guide' },
  { locale: 'zh', slug: 'advanced-tips' },
]
```

##### **4. 构建时行为**
```bash
bun run build

# Next.js 为每个参数组合生成静态页面
○ /en/guides/beginner-guide
○ /en/guides/advanced-tips
○ /zh/guides/beginner-guide
○ /zh/guides/advanced-tips
```

---

### 3.6 元数据生成 (第 62-98 行)

```typescript
export async function generateMetadata({ params }: GuidePageProps) {
	const { locale, slug } = await params

	const language: Language = isValidLanguage(locale) ? (locale as Language) : getDefaultLanguage()

	// 获取网站域名（从环境变量或使用默认值）
	const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://utd-wiki.netlify.app'
	const path = `/guides/${slug}`

	try {
		const { metadata } = await import(`../../../../../content/${language}/guide/${slug}.mdx`)

		return {
			title: `${metadata.title} - Universal Tower Defense`,
			description: metadata.description,
			alternates: {
				canonical: `${siteUrl}/${language}${path}`,
				languages: {
					en: `${siteUrl}/en${path}`,
					zh: `${siteUrl}/zh${path}`,
				},
			},
			openGraph: {
				title: metadata.title,
				description: metadata.description,
				images: metadata.image ? [metadata.image] : [],
				url: `${siteUrl}/${language}${path}`,
			},
		}
	} catch (error) {
		return {
			title: 'Guide Not Found',
			description: 'The requested guide could not be found.',
		}
	}
}
```

**执行流程**：

#### **3.6.1 提取参数和验证语言 (第 63-66 行)**
```typescript
const { locale, slug } = await params
const language: Language = isValidLanguage(locale) ? (locale as Language) : getDefaultLanguage()
```

#### **3.6.2 构建 URL (第 68-70 行)**
```typescript
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://utd-wiki.netlify.app'
const path = `/guides/${slug}`
```

**环境变量**：
- 优先使用 `NEXT_PUBLIC_SITE_URL`（生产环境）
- 后备使用默认值（开发环境）

#### **3.6.3 加载元数据 (第 72-73 行)**
```typescript
const { metadata } = await import(`../../../../../content/${language}/guide/${slug}.mdx`)
```

**注意**：
- 只导入 `metadata`，不导入 `default`（MDX 组件）
- 减少不必要的代码加载

#### **3.6.4 返回元数据对象 (第 75-91 行)**

##### **页面标题和描述**
```typescript
title: `${metadata.title} - Universal Tower Defense`,
description: metadata.description,
```

**渲染结果**：
```html
<title>新手攻略 - Universal Tower Defense</title>
<meta name="description" content="适合新手的完整指南" />
```

##### **多语言链接（alternates）**
```typescript
alternates: {
  canonical: `${siteUrl}/${language}${path}`,
  languages: {
    en: `${siteUrl}/en${path}`,
    zh: `${siteUrl}/zh${path}`,
  },
},
```

**渲染结果**：
```html
<link rel="canonical" href="https://utd-wiki.netlify.app/zh/guides/beginner-guide" />
<link rel="alternate" hreflang="en" href="https://utd-wiki.netlify.app/en/guides/beginner-guide" />
<link rel="alternate" hreflang="zh" href="https://utd-wiki.netlify.app/zh/guides/beginner-guide" />
```

**SEO 作用**：
- `canonical`：告诉搜索引擎这是规范 URL
- `alternate`：告诉搜索引擎有其他语言版本
- 避免重复内容惩罚

##### **Open Graph 标签**
```typescript
openGraph: {
  title: metadata.title,
  description: metadata.description,
  images: metadata.image ? [metadata.image] : [],
  url: `${siteUrl}/${language}${path}`,
},
```

**渲染结果**：
```html
<meta property="og:title" content="新手攻略" />
<meta property="og:description" content="适合新手的完整指南" />
<meta property="og:image" content="https://example.com/image.jpg" />
<meta property="og:url" content="https://utd-wiki.netlify.app/zh/guides/beginner-guide" />
```

**作用**：
- 社交媒体分享时显示的卡片
- 支持 Facebook、Twitter、Discord 等平台

#### **3.6.5 错误处理 (第 92-97 行)**
```typescript
catch (error) {
  return {
    title: 'Guide Not Found',
    description: 'The requested guide could not be found.',
  }
}
```

**触发条件**：
- MDX 文件不存在
- metadata 导出缺失

---

## 四、完整执行流程

### 4.1 用户访问 `/zh/guides/beginner-guide`

```
1. 【路由匹配】
   URL: /zh/guides/beginner-guide
   → 匹配 src/app/[locale]/guides/[slug]/page.tsx
   → params = { locale: "zh", slug: "beginner-guide" }

2. 【生成元数据】
   → generateMetadata() 执行
   → 导入 content/zh/guide/beginner-guide.mdx 的 metadata
   → 返回 title、description、openGraph 等
   → Next.js 生成 <head> 标签

3. 【渲染页面】
   → GuidePage() 执行
   → 验证语言：isValidLanguage("zh") = true
   → 导入 MDX：content/zh/guide/beginner-guide.mdx
   → 获取 MDXContent 组件和 metadata
   → 渲染 <DetailPage> 组件

4. 【返回 HTML】
   → 服务端渲染完成
   → 返回完整的 HTML 页面
   → 包含元数据、内容、样式
```

### 4.2 用户访问 `/fr/guides/beginner-guide`（无效语言）

```
1. 【路由匹配】
   URL: /fr/guides/beginner-guide
   → params = { locale: "fr", slug: "beginner-guide" }

2. 【语言验证】
   → isValidLanguage("fr") = false
   → redirect("/en/guides/beginner-guide")

3. 【重定向】
   → 浏览器跳转到 /en/guides/beginner-guide
   → 显示英文版本的攻略
```

### 4.3 用户访问 `/zh/guides/non-existent`（不存在的攻略）

```
1. 【路由匹配】
   URL: /zh/guides/non-existent
   → params = { locale: "zh", slug: "non-existent" }

2. 【尝试加载 MDX】
   → 导入 content/zh/guide/non-existent.mdx
   → 文件不存在，抛出错误

3. 【错误处理】
   → catch 捕获错误
   → 调用 notFound()
   → 显示 404 页面
```

---

## 五、在项目中的应用

### 5.1 创建新攻略

**步骤**：
1. 创建 MDX 文件：
   ```
   content/zh/guide/my-new-guide.mdx
   content/en/guide/my-new-guide.mdx
   ```

2. 编写内容：
   ```mdx
   ---
   title: "我的新攻略"
   description: "这是一个新攻略"
   date: "2024-01-22"
   author: "作者名"
   image: "/images/guide-cover.jpg"
   ---

   export const metadata = {
     title: "我的新攻略",
     description: "这是一个新攻略",
     date: "2024-01-22",
     author: "作者名",
     image: "/images/guide-cover.jpg"
   }

   # 我的新攻略

   这里是攻略内容...
   ```

3. 重新构建：
   ```bash
   bun run build
   ```

4. 访问页面：
   ```
   /zh/guides/my-new-guide
   /en/guides/my-new-guide
   ```

### 5.2 在 MDX 中使用 React 组件

```mdx
---
title: "高级攻略"
---

export const metadata = { ... }

# 高级攻略

<Alert type="warning">
  这是一个高级技巧，请谨慎使用！
</Alert>

## 伤害计算

<DamageCalculator />

## 视频教程

<VideoPlayer src="/videos/advanced.mp4" />
```

---

## 六、设计优势

1. **双层动态路由**：支持多语言和多攻略
2. **静态生成**：构建时预生成所有页面，极快的加载速度
3. **SEO 优化**：完整的元数据、多语言链接、Open Graph 标签
4. **错误处理**：优雅处理无效语言和不存在的攻略
5. **类型安全**：TypeScript 确保参数类型正确
6. **按需加载**：动态导入 MDX，减少初始包大小
7. **灵活扩展**：易于添加新攻略和新语言

---

## 七、常见问题

### 7.1 相对路径太长

**问题**：`../../../../../content/` 太难维护

**解决**：使用路径别名
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@content/*": ["./content/*"]
    }
  }
}

// 使用
await import(`@content/${language}/guide/${slug}.mdx`)
```

### 7.2 构建时间过长

**问题**：攻略很多时，构建很慢

**优化**：
1. 使用增量静态生成（ISR）
2. 限制 `generateStaticParams()` 返回的数量
3. 考虑按需生成（On-Demand ISR）

### 7.3 MDX 编译错误

**问题**：MDX 文件语法错误导致构建失败

**排查**：
1. 检查 frontmatter 格式
2. 确保 `export const metadata` 存在
3. 验证 MDX 语法（使用 MDX 编辑器）

---

## 八、最佳实践

### 8.1 统一 frontmatter 结构

```mdx
---
title: "攻略标题"
description: "攻略描述"
date: "2024-01-22"
author: "作者名"
category: "新手"
image: "/images/cover.jpg"
---

export const metadata = {
  title: "攻略标题",
  description: "攻略描述",
  date: "2024-01-22",
  author: "作者名",
  category: "新手",
  image: "/images/cover.jpg"
}
```

### 8.2 使用环境变量

```bash
# .env.local
NEXT_PUBLIC_SITE_URL=https://your-domain.com
```

### 8.3 添加错误日志

```typescript
catch (error) {
  console.error(`Failed to load guide: ${language}/${slug}`, error)
  notFound()
}
```

---

## 九、注意事项

1. **frontmatter 和 metadata 必须一致**：避免数据不同步
2. **slug 必须唯一**：同一语言下不能有重复的 slug
3. **图片路径使用绝对路径**：`/images/...` 而非 `./images/...`
4. **测试所有语言版本**：确保每种语言的攻略都存在
5. **生产环境移除 `force-dynamic`**：使用静态生成提升性能
6. **处理特殊字符**：slug 中避免使用空格、特殊符号

---

## 十、相关文件

- **src/lib/content.ts**：内容管理工具函数
- **src/components/content/DetailPage.tsx**：详情页面组件
- **content/[lang]/guide/*.mdx**：攻略 MDX 文件
- **src/app/[locale]/layout.tsx**：国际化布局
- **src/middleware.ts**：语言检测中间件
