# 本项目多语言实现完整指南

## 目录

1. [多语言架构概述](#多语言架构概述)
2. [涉及的文件清单](#涉及的文件清单)
3. [实现步骤详解](#实现步骤详解)
4. [构建时的报错现象](#构建时的报错现象)
5. [问题排查和解决](#问题排查和解决)
6. [最佳实践](#最佳实践)

---

## 多语言架构概述

本项目使用 **next-intl** 实现多语言支持，采用 Next.js 15 App Router 架构。

### 核心技术栈

- **框架**: Next.js 15 (App Router)
- **多语言库**: next-intl v4.7.0
- **支持语言**: 英文 (en)、中文 (zh)
- **默认语言**: 英文 (en)
- **URL 策略**: `as-needed` (默认语言无前缀)

### 架构图

```
用户访问
    ↓
middleware.ts (语言检测和路由)
    ↓
[locale]/layout.tsx (加载翻译数据)
    ↓
NextIntlClientProvider (提供翻译 Context)
    ↓
页面组件 (使用翻译)
    ├─ 服务器组件 → getTranslations()
    └─ 客户端组件 → useTranslations()
```

---

## 涉及的文件清单

### 1. 配置文件

#### `src/i18n/config.ts` - 语言配置
```typescript
export const locales = ['en', 'zh'] as const
export type Locale = (typeof locales)[number]

export const defaultLocale: Locale = 'en'

export const localeNames: Record<Locale, string> = {
  en: 'English',
  zh: '中文',
}
```

**作用：**
- 定义支持的语言列表
- 定义默认语言
- 定义语言显示名称

#### `src/i18n/request.ts` - 请求配置
```typescript
import { getRequestConfig } from 'next-intl/server'
import { locales, defaultLocale } from './config'

export default getRequestConfig(async ({ requestLocale }) => {
  // 获取当前请求的语言
  let locale = await requestLocale

  // 确保语言有效
  if (!locale || !locales.includes(locale as any)) {
    locale = defaultLocale
  }

  return {
    locale,
    messages: (await import(`../locales/${locale}.json`)).default,
  }
})
```

**作用：**
- 处理每个请求的语言配置
- 动态加载对应语言的翻译文件
- 验证语言有效性

#### `src/middleware.ts` - 中间件
```typescript
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n/config'

export default createMiddleware({
  locales,
  defaultLocale,
  localeDetection: true,
  localePrefix: 'as-needed'  // 默认语言无前缀
})

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
```

**作用：**
- 拦截所有请求
- 检测用户语言偏好
- 处理 URL 重定向
- 设置语言前缀策略

#### `next.config.mjs` - Next.js 配置
```typescript
import createNextIntlPlugin from 'next-intl/plugin'

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')

const nextConfig = {
  // ... 其他配置
}

export default withNextIntl(nextConfig)
```

**作用：**
- 集成 next-intl 插件
- 指定请求配置文件路径

### 2. 翻译文件

#### `src/locales/en.json` - 英文翻译
```json
{
  "hero": {
    "title": "Universal Tower Defense",
    "description": "The ultimate tower defense experience",
    "badge": "New Update Available"
  },
  "nav": {
    "home": "Home",
    "guides": "Guides"
  },
  "pages": {
    "guides": {
      "title": "Guides",
      "description": "Learn strategies and tips"
    }
  }
}
```

#### `src/locales/zh.json` - 中文翻译
```json
{
  "hero": {
    "title": "通用塔防",
    "description": "终极塔防体验",
    "badge": "新版本可用"
  },
  "nav": {
    "home": "首页",
    "guides": "攻略"
  },
  "pages": {
    "guides": {
      "title": "攻略",
      "description": "学习策略和技巧"
    }
  }
}
```

**作用：**
- 存储所有翻译文本
- 支持嵌套结构
- 保持两种语言的键名一致

### 3. 布局文件

#### `src/app/layout.tsx` - 根布局
```typescript
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Universal Tower Defense',
  description: 'UTD Wiki and Resources',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children  // 不包含 <html> 和 <body>，由 [locale]/layout.tsx 处理
}
```

**作用：**
- 定义全局元数据
- 加载全局样式
- 不包含 HTML 结构（由语言布局处理）

#### `src/app/[locale]/layout.tsx` - 语言布局
```typescript
import { NextIntlClientProvider } from 'next-intl'
import { getMessages } from 'next-intl/server'
import { notFound } from 'next/navigation'
import { locales } from '@/i18n/config'

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }))
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: Promise<{ locale: string }>
}) {
  const { locale } = await params

  // 验证语言是否有效
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // 加载翻译消息
  const messages = await getMessages({ locale })

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
```

**作用：**
- 为每种语言生成静态路由
- 验证语言参数
- 异步加载翻译数据
- 提供翻译 Context 给子组件
- 设置 HTML lang 属性

### 4. 页面组件

#### `src/app/[locale]/page.tsx` - 首页（客户端组件）
```typescript
'use client'

import { useTranslations } from 'next-intl'

export default function HomePage() {
  const t = useTranslations()  // Hook，同步调用

  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.description')}</p>
    </div>
  )
}
```

**作用：**
- 使用 `useTranslations()` Hook
- 客户端渲染，支持交互

#### `src/app/[locale]/guides/page.tsx` - 攻略列表（服务器组件）
```typescript
import { getTranslations } from 'next-intl/server'
import { getAllContent } from '@/lib/content'

export default async function GuidesPage({ params }) {
  const { locale } = await params
  const t = await getTranslations()  // 异步函数

  const guides = await getAllContent('guide', locale)

  return (
    <div>
      <h1>{t('pages.guides.title')}</h1>
      <p>{t('pages.guides.description')}</p>
    </div>
  )
}

export async function generateMetadata({ params }) {
  const { locale } = await params
  const t = await getTranslations()

  return {
    title: t('pages.guides.metaTitle'),
    description: t('pages.guides.metaDescription'),
  }
}

export async function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }]
}
```

**作用：**
- 使用 `getTranslations()` 异步函数
- 服务器渲染，SEO 友好
- 生成静态参数

### 5. 组件文件

#### `src/components/Navigation.tsx` - 导航组件
```typescript
'use client'

import { useTranslations } from 'next-intl'
import Link from 'next/link'

export function Navigation() {
  const t = useTranslations()

  return (
    <nav>
      <Link href="/">{t('nav.home')}</Link>
      <Link href="/guides">{t('nav.guides')}</Link>
    </nav>
  )
}
```

**作用：**
- 客户端组件，使用 Hook
- 提供导航链接

---

## 实现步骤详解

### 步骤 1：安装依赖

```bash
npm install next-intl
```

### 步骤 2：创建配置文件

1. 创建 `src/i18n/config.ts`
2. 创建 `src/i18n/request.ts`
3. 创建 `src/middleware.ts`

### 步骤 3：创建翻译文件

1. 创建 `src/locales/en.json`
2. 创建 `src/locales/zh.json`

### 步骤 4：配置 Next.js

修改 `next.config.mjs`，添加 next-intl 插件。

### 步骤 5：创建布局结构

1. 修改 `src/app/layout.tsx`
2. 创建 `src/app/[locale]/layout.tsx`

### 步骤 6：创建页面

1. 创建 `src/app/[locale]/page.tsx`
2. 创建其他语言页面

### 步骤 7：使用翻译

- 客户端组件：`useTranslations()`
- 服务器组件：`getTranslations()`

---

## 构建时的报错现象

### 错误 1：getTranslations() 使用错误

#### 错误现象
```bash
npm run build

Error occurred prerendering page "/en/guides"
Error:
    at <unknown> (.next/server/chunks/837.js:1:76695)
    at o (.next/server/app/[locale]/guides/page.js:1:8128)
```

#### 原因分析
```typescript
// ❌ 错误代码
import { getTranslations } from 'next-intl/server'

export default async function GuidesPage({ params }) {
  const { locale } = await params
  const language = locale as Language

  // 问题：传递了 locale 参数
  const t = await getTranslations({ locale: language })

  return <div>{t('pages.guides.title')}</div>
}
```

**问题：**
- 在 next-intl v4 中，`getTranslations()` 不接受 `{ locale }` 参数
- 应该直接调用 `getTranslations()`，它会自动从请求上下文获取 locale

#### 解决方案
```typescript
// ✅ 正确代码
import { getTranslations } from 'next-intl/server'

export default async function GuidesPage({ params }) {
  const { locale } = await params

  // 直接调用，不传递参数
  const t = await getTranslations()

  return <div>{t('pages.guides.title')}</div>
}
```

### 错误 2：客户端组件使用异步

#### 错误现象
```bash
Error: async/await is not yet supported in Client Components
Only Server Components and Route Handlers can be async
```

#### 原因分析
```typescript
// ❌ 错误代码
'use client'

import { getTranslations } from 'next-intl/server'

export default async function ClientPage() {
  const t = await getTranslations()  // 错误：客户端组件不能异步
  return <div>{t('title')}</div>
}
```

**问题：**
- 客户端组件不能是 async 函数
- 不能在客户端使用 `getTranslations()`

#### 解决方案
```typescript
// ✅ 正确代码
'use client'

import { useTranslations } from 'next-intl'  // 注意导入路径

export default function ClientPage() {
  const t = useTranslations()  // 使用 Hook，同步调用
  return <div>{t('title')}</div>
}
```

### 错误 3：unstable_setRequestLocale 不存在

#### 错误现象
```bash
Attempted import error: 'unstable_setRequestLocale' is not exported from 'next-intl/server'
```

#### 原因分析
```typescript
// ❌ 错误代码
import { getTranslations, unstable_setRequestLocale } from 'next-intl/server'

export default async function Page({ params }) {
  const { locale } = await params
  unstable_setRequestLocale(locale)  // 错误：v4 中不存在
  const t = await getTranslations()
  return <div>{t('title')}</div>
}
```

**问题：**
- `unstable_setRequestLocale` 在 next-intl v3 中存在
- 在 v4 中已被移除

#### 解决方案
```typescript
// ✅ 正确代码
import { getTranslations } from 'next-intl/server'

export default async function Page({ params }) {
  const { locale } = await params
  // 不需要手动设置 locale，getTranslations() 会自动获取
  const t = await getTranslations()
  return <div>{t('title')}</div>
}
```

### 错误 4：翻译文件路径错误

#### 错误现象
```bash
Error: Cannot find module '../locales/en.json'
```

#### 原因分析
```typescript
// ❌ 错误的文件结构
src/
├── i18n/
│   ├── config.ts
│   └── request.ts
└── translations/  ← 错误：文件夹名称不对
    ├── en.json
    └── zh.json
```

**问题：**
- `request.ts` 中导入路径是 `../locales/${locale}.json`
- 但实际文件夹名称是 `translations`

#### 解决方案
```typescript
// ✅ 正确的文件结构
src/
├── i18n/
│   ├── config.ts
│   └── request.ts
└── locales/  ← 正确：与导入路径匹配
    ├── en.json
    └── zh.json
```

### 错误 5：MDX 文件导入路径错误

#### 错误现象
```bash
Error occurred prerendering page "/en/guides/beginner"
Error: Cannot find module '@/../../content/en/guide/beginner.mdx'
```

#### 原因分析
```typescript
// ❌ 错误代码
const { default: MDXContent, metadata } = await import(
  `@/../../content/${language}/guide/${slug}.mdx`
)
```

**问题：**
- `@/` 指向 `src/` 目录
- `@/../../` 会指向项目根目录的上两级，路径错误

#### 解决方案
```typescript
// ✅ 正确代码
const { default: MDXContent, metadata } = await import(
  `../../../../../content/${language}/guide/${slug}.mdx`
)
```

**路径计算：**
```
当前文件: src/app/[locale]/guides/[slug]/page.tsx
目标文件: content/en/guide/beginner.mdx

相对路径: ../../../../../content/en/guide/beginner.mdx
```

### 错误 6：locale 变量未定义

#### 错误现象
```bash
Type error: Cannot find name 'locale'
```

#### 原因分析
```typescript
// ❌ 错误代码
import { getTranslations, getLocale } from 'next-intl/server'

export async function DetailPage({ frontmatter, content }) {
  const locale = await getLocale()
  const t = await getTranslations({ locale })

  return (
    <Link href={`/${locale}`}>  {/* 使用 locale */}
      {t('common.home')}
    </Link>
  )
}
```

**问题：**
- 删除了 `getLocale()` 调用
- 但代码中还在使用 `locale` 变量

#### 解决方案
```typescript
// ✅ 正确代码
import { getTranslations } from 'next-intl/server'

export async function DetailPage({ frontmatter, content, language }) {
  const t = await getTranslations()

  return (
    <Link href={`/${language}`}>  {/* 使用 props 中的 language */}
      {t('common.home')}
    </Link>
  )
}
```

### 错误 7：webpack 缓存警告

#### 错误现象
```bash
<w> [webpack.cache.PackFileCacheStrategy/webpack.FileSystemInfo]
Parsing of /node_modules/next-intl/dist/esm/production/extractor/format/index.js
for build dependencies failed at 'import(t)'.
Build dependencies behind this expression are ignored and might cause incorrect cache invalidation.
```

#### 原因分析
这是 next-intl 内部使用动态导入导致的 webpack 警告。

#### 解决方案
**这是警告，不是错误，可以忽略。**

如果想消除警告，可以在 `next.config.mjs` 中配置：
```typescript
const nextConfig = {
  webpack: (config) => {
    config.ignoreWarnings = [
      { module: /node_modules\/next-intl/ }
    ]
    return config
  }
}
```

---

## 问题排查和解决

### 排查流程

```
构建失败
    ↓
查看错误信息
    ↓
确定错误类型
    ├─ getTranslations 使用错误 → 检查是否传递了参数
    ├─ 客户端组件异步错误 → 改用 useTranslations()
    ├─ 导入路径错误 → 检查文件路径
    ├─ 变量未定义 → 检查是否删除了变量声明
    └─ 其他错误 → 查看完整错误堆栈
```

### 常见错误速查表

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `async/await is not yet supported in Client Components` | 客户端组件使用了 async | 使用 `useTranslations()` Hook |
| `'unstable_setRequestLocale' is not exported` | 使用了 v3 的 API | 移除该调用，直接用 `getTranslations()` |
| `Cannot find module '../locales/en.json'` | 翻译文件路径错误 | 检查文件夹名称和路径 |
| `Cannot find name 'locale'` | 变量未定义 | 使用 props 中的参数或重新声明 |
| `Error occurred prerendering page` | 预渲染失败 | 检查服务器组件中的异步调用 |

### 调试技巧

#### 1. 检查导入路径
```typescript
// 客户端组件
import { useTranslations } from 'next-intl'  // ✅ 正确

// 服务器组件
import { getTranslations } from 'next-intl/server'  // ✅ 正确
```

#### 2. 检查组件类型
```typescript
// 客户端组件
'use client'  // ← 必须有这个声明
export default function ClientPage() {
  const t = useTranslations()  // ✅ 使用 Hook
}

// 服务器组件
// 没有 'use client' 声明
export default async function ServerPage() {
  const t = await getTranslations()  // ✅ 使用异步函数
}
```

#### 3. 检查 getTranslations 调用
```typescript
// ❌ 错误
const t = await getTranslations({ locale: 'en' })

// ✅ 正确
const t = await getTranslations()
```

#### 4. 启用详细日志
```bash
# 查看详细的构建日志
npm run build -- --debug

# 或者
NODE_OPTIONS='--trace-warnings' npm run build
```

---

## 最佳实践

### 1. 文件组织

```
src/
├── i18n/
│   ├── config.ts          # 语言配置
│   └── request.ts         # 请求配置
├── locales/
│   ├── en.json           # 英文翻译
│   └── zh.json           # 中文翻译
├── middleware.ts         # 中间件
└── app/
    ├── layout.tsx        # 根布局
    └── [locale]/
        ├── layout.tsx    # 语言布局
        └── page.tsx      # 页面
```

### 2. 翻译文件结构

```json
{
  "common": {
    "home": "Home",
    "back": "Back"
  },
  "pages": {
    "home": {
      "title": "Welcome",
      "description": "..."
    },
    "guides": {
      "title": "Guides",
      "description": "..."
    }
  },
  "components": {
    "navigation": {
      "menu": "Menu"
    }
  }
}
```

**原则：**
- 按功能模块组织
- 保持层级清晰
- 避免过深嵌套（最多 3-4 层）

### 3. 组件选择

| 场景 | 组件类型 | 翻译 API |
|------|---------|---------|
| 需要交互 | 客户端组件 | `useTranslations()` |
| 静态内容 | 服务器组件 | `getTranslations()` |
| 需要 SEO | 服务器组件 | `getTranslations()` |
| 需要动画 | 客户端组件 | `useTranslations()` |

### 4. 性能优化

```typescript
// ✅ 好：服务器组件并行加载
export default async function Page() {
  const [t, data1, data2] = await Promise.all([
    getTranslations(),
    fetchData1(),
    fetchData2(),
  ])

  return <div>{t('title')}</div>
}

// ❌ 差：串行加载
export default async function Page() {
  const t = await getTranslations()
  const data1 = await fetchData1()
  const data2 = await fetchData2()

  return <div>{t('title')}</div>
}
```

### 5. 类型安全

```typescript
// 定义翻译类型
interface Translations {
  hero: {
    title: string
    description: string
  }
  nav: {
    home: string
    guides: string
  }
}

// 使用类型
const t = useTranslations() as Translations
```

---

## 总结

### 关键文件

| 文件 | 作用 | 必需 |
|------|------|------|
| `src/i18n/config.ts` | 语言配置 | ✅ |
| `src/i18n/request.ts` | 请求配置 | ✅ |
| `src/middleware.ts` | 路由中间件 | ✅ |
| `src/locales/*.json` | 翻译文件 | ✅ |
| `src/app/[locale]/layout.tsx` | 语言布局 | ✅ |
| `next.config.mjs` | Next.js 配置 | ✅ |

### 常见错误

1. ❌ 在客户端组件使用 `getTranslations()`
2. ❌ 给 `getTranslations()` 传递参数
3. ❌ 使用已废弃的 `unstable_setRequestLocale`
4. ❌ 翻译文件路径错误
5. ❌ MDX 导入路径错误

### 核心原则

- **客户端组件** = `useTranslations()` Hook
- **服务器组件** = `getTranslations()` 异步函数
- **不传递参数** = 自动从上下文获取 locale
- **保持简单** = 遵循框架约定

---

## 参考资料

- [next-intl 官方文档](https://next-intl-docs.vercel.app/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [项目其他文档](./README.md)
