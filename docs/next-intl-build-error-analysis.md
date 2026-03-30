# Next.js 15 + next-intl v4 构建错误分析报告

**日期**: 2026-01-22
**项目**: Universal Tower Defense Wiki
**问题**: 静态生成阶段预渲染失败

---

## 目录

1. [报错现象](#报错现象)
2. [根本原因分析](#根本原因分析)
3. [当前代码实现](#当前代码实现)
4. [解决方案对比](#解决方案对比)
5. [推荐方案](#推荐方案)
6. [实施步骤](#实施步骤)

---

## 报错现象

### 错误信息

```bash
Error occurred prerendering page "/en"
Error:
    at <unknown> (.next/server/chunks/455.js:1:28391)
    at o (.next/server/chunks/170.js:1:3910) {
  digest: '3242736657'
}
Export encountered an error on /[locale]/page: /en, exiting the build.
```

### 构建阶段

```bash
✓ Compiled successfully in 9.8s
✓ Linting and checking validity of types
✓ Collecting page data
✗ Generating static pages (0/9)  ← 失败在这里
```

### 失败页面

- `/en` - 英文主页
- `/zh` - 中文主页
- 其他页面未能到达构建阶段

---

## 根本原因分析

### 问题 1：主页面是客户端组件 ⚠️

**文件**: `src/app/[locale]/page.tsx`

```typescript
'use client'  // ← 核心问题

import { useTranslations } from 'next-intl'

export default function HomePage() {
  const t = useTranslations() as any
  // ... 大量客户端交互逻辑
}
```

**问题分析**:

1. **客户端组件在静态生成时也需要服务端预渲染**
   - Next.js 15 的 App Router 会在构建时预渲染所有页面
   - 即使是客户端组件，也会先在服务端生成 HTML

2. **`useTranslations()` 在服务端预渲染时的行为**
   - 客户端运行时：从 `NextIntlClientProvider` 的 context 获取 messages
   - 服务端预渲染时：需要从 next-intl 的服务端上下文获取 locale

3. **客户端组件无法调用 `setRequestLocale()`**
   - `setRequestLocale()` 是服务端 API，只能在服务端组件中调用
   - 客户端组件依赖父级 layout 设置的上下文
   - 但在静态生成时，这个上下文传递可能失败

### 问题 2：Layout 中的 setRequestLocale 调用时机 ⚠️

**文件**: `src/app/[locale]/layout.tsx`

```typescript
export default async function LocaleLayout({ children, params }) {
  const { locale } = await params

  // ❌ 问题：在 setRequestLocale 之前有其他逻辑
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // ⚠️ setRequestLocale 应该在 await params 之后立即调用
  setRequestLocale(locale)

  const messages = await getMessages()

  return (
    <html lang={locale}>
      <body>
        <ClientBody>
          <NextIntlClientProvider messages={messages}>
            {children}
          </NextIntlClientProvider>
        </ClientBody>
      </body>
    </html>
  )
}
```

**根据 next-intl v4 文档**:

> `setRequestLocale` must be called at the very top of the component, immediately after awaiting params.

**正确的顺序**:

```typescript
const { locale } = await params
setRequestLocale(locale)  // ← 必须立即调用
// ... 其他逻辑
```

### 问题 3：缺少根 layout.tsx 的影响 ⚠️

**当前结构**:

```
src/app/
  ├── [locale]/
  │   ├── layout.tsx     ← 唯一的 layout
  │   ├── page.tsx
  │   └── guides/
  └── (没有 layout.tsx)
```

**潜在问题**:

1. Next.js 在处理特殊路由时可能出现问题：
   - `/_not-found`
   - `/_error`
   - 其他内部路由

2. 根据 Next.js 文档，虽然 `[locale]/layout.tsx` 可以作为根 layout，但某些边缘情况可能不被正确处理

### 问题 4：not-found 页面也是客户端组件 ⚠️

**文件**: `src/app/[locale]/not-found.tsx`

```typescript
import { useTranslations } from 'next-intl'

export default function NotFound() {
  const t = useTranslations()  // ← 同样的问题
  // ...
}
```

与主页面相同的问题。

---

## 当前代码实现

### 文件结构

| 文件路径 | 组件类型 | next-intl API | setRequestLocale | 状态 |
|---------|---------|--------------|------------------|------|
| `[locale]/layout.tsx` | 服务端 | `getMessages()` | ✅ 已添加 | ⚠️ 位置不对 |
| `[locale]/page.tsx` | **客户端** | `useTranslations()` | ❌ 无法添加 | ❌ 失败 |
| `[locale]/guides/page.tsx` | 服务端 | `getTranslations()` | ✅ 已添加 | ✅ 正确 |
| `[locale]/guides/[slug]/page.tsx` | 服务端 | 无 | ✅ 已添加 | ✅ 正确 |
| `[locale]/not-found.tsx` | **客户端** | `useTranslations()` | ❌ 无法添加 | ⚠️ 潜在问题 |
| `components/content/DetailPage.tsx` | 服务端 | `getTranslations()` | ❌ 未添加 | ⚠️ 依赖父组件 |

### 问题总结

1. **2 个客户端组件**使用 `useTranslations()`，无法调用 `setRequestLocale()`
2. **1 个 layout** 的 `setRequestLocale()` 调用位置不符合规范
3. **1 个可复用组件** 依赖父组件设置上下文

---

## 解决方案对比

### 方案 A：将主页面改为服务端组件 ⭐ 推荐

#### 实现方式

**步骤 1**: 创建服务端包装器

```typescript
// src/app/[locale]/page.tsx
import { setRequestLocale } from 'next-intl/server'
import { HomePageClient } from './HomePageClient'

interface HomePageProps {
  params: Promise<{ locale: string }>
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params

  // 设置 locale 上下文
  setRequestLocale(locale)

  // 渲染客户端组件
  return <HomePageClient />
}

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }]
}
```

**步骤 2**: 将原有逻辑移到客户端组件

```typescript
// src/app/[locale]/HomePageClient.tsx
'use client'

import { useTranslations } from 'next-intl'
// ... 原有的所有导入

export function HomePageClient() {
  const t = useTranslations() as any
  // ... 原有的所有逻辑（完全不变）
}
```

#### 优缺点分析

| 优点 | 缺点 |
|------|------|
| ✅ 符合 next-intl v4 最佳实践 | ❌ 需要拆分文件 |
| ✅ 静态生成正常工作 | ❌ 代码改动较大（但逻辑不变） |
| ✅ 更好的 SEO（服务端渲染） | ❌ 需要同时修改 not-found 页面 |
| ✅ 更好的性能（首屏加载） | |
| ✅ 长期可维护性好 | |
| ✅ 符合 React Server Components 最佳实践 | |

#### 适用场景

- ✅ 需要静态生成的页面
- ✅ 需要 SEO 优化的页面
- ✅ 长期维护的项目

---

### 方案 B：恢复根 layout.tsx + 简化结构

#### 实现方式

**步骤 1**: 恢复根 layout

```typescript
// src/app/layout.tsx
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import Script from 'next/script'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'Universal Tower Defense - Codes, Tier List, Guides & Calculator | UTD Roblox',
  description: '...',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${geistSans.variable} ${geistMono.variable}`}>
      <head>
        <Script crossOrigin="anonymous" src="//unpkg.com/same-runtime/dist/index.global.js" />
      </head>
      <body suppressHydrationWarning className="antialiased">
        {children}
      </body>
    </html>
  )
}
```

**步骤 2**: 简化 locale layout

```typescript
// src/app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl'
import { getMessages, setRequestLocale } from 'next-intl/server'
import { notFound } from 'next/navigation'
import { locales } from '@/i18n/config'
import ClientBody from '../ClientBody'

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

  // 立即设置 locale 上下文
  setRequestLocale(locale)

  // 验证语言是否有效
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // 加载翻译消息
  const messages = await getMessages()

  return (
    <ClientBody>
      <NextIntlClientProvider messages={messages}>
        {children}
      </NextIntlClientProvider>
    </ClientBody>
  )
}
```

#### 优缺点分析

| 优点 | 缺点 |
|------|------|
| ✅ 符合 Next.js 标准结构 | ❌ `<html lang>` 无法动态设置为 locale |
| ✅ 改动相对较小 | ❌ 主页面仍是客户端组件，可能仍有问题 |
| ✅ 更容易理解 | ❌ 不符合 next-intl 推荐的结构 |
| | ❌ 可能需要额外配置 |

#### 适用场景

- ⚠️ 作为临时方案
- ⚠️ 如果方案 A 无法实施

---

### 方案 C：使用 generateStaticParams + 传递翻译数据

#### 实现方式

```typescript
// src/app/[locale]/page.tsx
import { setRequestLocale, getTranslations } from 'next-intl/server'
import { HomePageClient } from './HomePageClient'

export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }]
}

export default async function HomePage({ params }) {
  const { locale } = await params
  setRequestLocale(locale)

  // 在服务端获取所有需要的翻译
  const t = await getTranslations()

  // 将翻译数据序列化后传递给客户端
  const translations = {
    hero: {
      title: t('hero.title'),
      description: t('hero.description'),
      // ... 所有需要的翻译
    },
    // ...
  }

  return <HomePageClient translations={translations} />
}
```

#### 优缺点分析

| 优点 | 缺点 |
|------|------|
| ✅ 静态生成正常工作 | ❌ 需要手动管理所有翻译键 |
| ✅ 保持客户端组件 | ❌ 代码复杂度大幅增加 |
| | ❌ 容易遗漏翻译键 |
| | ❌ 维护成本高 |
| | ❌ 不符合 next-intl 设计理念 |

#### 适用场景

- ❌ 不推荐使用

---

### 方案 D：禁用静态生成（动态渲染）

#### 实现方式

```typescript
// src/app/[locale]/page.tsx
export const dynamic = 'force-dynamic'  // ← 强制动态渲染

'use client'

import { useTranslations } from 'next-intl'

export default function HomePage() {
  const t = useTranslations() as any
  // ... 保持原有代码不变
}
```

#### 优缺点分析

| 优点 | 缺点 |
|------|------|
| ✅ 最小改动（只加一行） | ❌ 失去静态生成的所有优势 |
| ✅ 立即解决构建问题 | ❌ 性能大幅下降 |
| | ❌ 每次请求都需要服务端渲染 |
| | ❌ 增加服务器负载 |
| | ❌ SEO 可能受影响 |
| | ❌ 不符合项目需求（需要静态生成） |

#### 适用场景

- ⚠️ 仅作为紧急临时方案
- ⚠️ 需要快速上线时
- ❌ 不适合生产环境长期使用

---

## 推荐方案

### 最佳选择：方案 A（将主页面改为服务端组件）

#### 选择理由

1. **符合 next-intl v4 最佳实践**
   - 官方文档推荐的架构
   - 充分利用 React Server Components

2. **保持静态生成优势**
   - 构建时生成 HTML
   - 更快的首屏加载
   - 更好的 SEO

3. **长期可维护性**
   - 清晰的服务端/客户端边界
   - 更容易理解和调试
   - 符合 Next.js 15 的设计理念

4. **性能优势**
   - 减少客户端 JavaScript 体积
   - 更快的 Time to Interactive (TTI)
   - 更好的 Core Web Vitals 指标

#### 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 代码拆分可能引入 bug | 中 | 充分测试，保持逻辑不变 |
| 开发时间增加 | 低 | 逻辑不变，只是文件拆分 |
| 团队需要适应新结构 | 低 | 提供文档和示例 |

---

## 实施步骤

### 阶段 1：修复 Layout（优先级：P0）

**目标**: 确保 `setRequestLocale` 调用位置正确

**文件**: `src/app/[locale]/layout.tsx`

```typescript
export default async function LocaleLayout({ children, params }) {
  const { locale } = await params

  // ✅ 立即调用 setRequestLocale
  setRequestLocale(locale)

  // 验证语言是否有效
  if (!locales.includes(locale as any)) {
    notFound()
  }

  // 加载翻译消息
  const messages = await getMessages()

  return (
    <html lang={locale} className={`dark ${geistSans.variable} ${geistMono.variable}`}>
      <head>
        <Script crossOrigin="anonymous" src="//unpkg.com/same-runtime/dist/index.global.js" />
      </head>
      <body suppressHydrationWarning className="antialiased">
        <ClientBody>
          <NextIntlClientProvider messages={messages}>
            {children}
          </NextIntlClientProvider>
        </ClientBody>
      </body>
    </html>
  )
}
```

**预期结果**: Layout 层面的配置正确

---

### 阶段 2：重构主页面（优先级：P0）

**目标**: 将主页面改为服务端组件包装器

#### 步骤 2.1：创建服务端包装器

**文件**: `src/app/[locale]/page.tsx`

```typescript
import { setRequestLocale } from 'next-intl/server'
import { HomePageClient } from './HomePageClient'

interface HomePageProps {
  params: Promise<{ locale: string }>
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params

  // 设置 locale 上下文
  setRequestLocale(locale)

  // 渲染客户端组件
  return <HomePageClient />
}

// 生成静态参数
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'zh' }]
}
```

#### 步骤 2.2：创建客户端组件

**文件**: `src/app/[locale]/HomePageClient.tsx`

```typescript
'use client'

import { useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import {
  Calculator,
  Gift,
  Trophy,
  BookOpen,
  FileCode,
  Book,
  Users,
  MessageCircle,
  Zap,
  Shield,
  Link2,
  Sparkles,
  ChevronDown,
} from 'lucide-react'
import { useTranslations } from 'next-intl'

export function HomePageClient() {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const t = useTranslations() as any

  useEffect(() => {
    // ... 原有的 useEffect 逻辑
  }, [])

  return (
    <div className="min-h-screen bg-[#06080f]">
      {/* ... 原有的所有 JSX（完全不变） */}
    </div>
  )
}
```

**注意**: 只需要将原有的 `export default function HomePage()` 改为 `export function HomePageClient()`，其他代码完全不变。

---

### 阶段 3：修复 not-found 页面（优先级：P1）

**目标**: 同样将 not-found 改为服务端组件包装器

**文件**: `src/app/[locale]/not-found.tsx`

```typescript
import { setRequestLocale } from 'next-intl/server'
import { NotFoundClient } from './NotFoundClient'

export default async function NotFound() {
  // Note: not-found 页面可能无法访问 params
  // 需要使用其他方式获取 locale
  return <NotFoundClient />
}
```

**或者使用客户端组件但不依赖翻译**:

```typescript
'use client'

import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-slate-300 mb-4">
          Page Not Found
        </h2>
        <p className="text-slate-400 mb-8">
          The page you are looking for does not exist.
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          Back to Home
        </Link>
      </div>
    </div>
  )
}
```

---

### 阶段 4：测试验证（优先级：P0）

#### 4.1 构建测试

```bash
# 清理缓存
rm -rf .next

# 运行构建
npm run build
```

**预期结果**:
```bash
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (9/9)
✓ Finalizing page optimization

Route (app)                              Size     First Load JS
┌ ○ /[locale]                            ...      ...
├ ○ /[locale]/guides                     ...      ...
└ ○ /[locale]/guides/[slug]              ...      ...

○  (Static)  prerendered as static content
```

#### 4.2 功能测试

**路由测试**:
- [ ] 访问 `/` → 自动重定向到 `/en` 或 `/zh`
- [ ] 访问 `/en` → 显示英文首页
- [ ] 访问 `/zh` → 显示中文首页
- [ ] 访问 `/en/guides` → 显示英文攻略列表
- [ ] 访问 `/zh/guides` → 显示中文攻略列表
- [ ] 访问 `/en/guides/beginner` → 显示英文攻略详情
- [ ] 访问 `/zh/guides/beginner` → 显示中文攻略详情

**语言切换测试**:
- [ ] 在英文页面点击语言切换按钮 → 切换到中文
- [ ] 在中文页面点击语言切换按钮 → 切换到英文
- [ ] 切换后 URL 正确更新
- [ ] 切换后页面内容正确翻译

**交互功能测试**:
- [ ] 滚动揭示动画正常工作
- [ ] 按钮点击正常
- [ ] 导航链接正常
- [ ] 图片加载正常

#### 4.3 性能测试

使用 Lighthouse 测试：
- [ ] Performance > 90
- [ ] Accessibility > 90
- [ ] Best Practices > 90
- [ ] SEO > 90

---

## 附录

### A. next-intl v4 关键 API

#### 服务端 API

```typescript
import { getTranslations, getMessages, setRequestLocale } from 'next-intl/server'

// 设置 locale 上下文（必须在组件最顶部调用）
setRequestLocale(locale)

// 获取翻译函数
const t = await getTranslations()

// 获取所有翻译消息
const messages = await getMessages()
```

#### 客户端 API

```typescript
import { useTranslations, useLocale } from 'next-intl'

// 获取翻译函数
const t = useTranslations()

// 获取当前 locale
const locale = useLocale()
```

### B. 常见错误和解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `MISSING_MESSAGE` | 翻译键不存在 | 在 `en.json` 和 `zh.json` 中添加对应的键 |
| `Error occurred prerendering page` | 客户端组件使用 `useTranslations()` | 改为服务端组件或使用服务端包装器 |
| `setRequestLocale is not a function` | 导入路径错误 | 使用 `next-intl/server` 而不是 `next-intl` |
| `locale is undefined` | 未调用 `setRequestLocale` | 在组件顶部调用 `setRequestLocale(locale)` |

### C. 参考资料

- [next-intl v4 官方文档](https://next-intl-docs.vercel.app/)
- [Next.js 15 App Router 文档](https://nextjs.org/docs/app)
- [React Server Components 文档](https://react.dev/reference/rsc/server-components)
- [Next.js 静态生成文档](https://nextjs.org/docs/app/building-your-application/rendering/server-components#static-rendering-default)

---

## 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|---------|------|
| 2026-01-22 | 1.0 | 初始版本 | Claude |

---

**文档状态**: ✅ 已完成
**下一步行动**: 实施方案 A - 将主页面改为服务端组件
