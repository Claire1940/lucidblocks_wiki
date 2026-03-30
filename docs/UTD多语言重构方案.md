# UTD 项目多语言重构方案

**基于 Heartopia 项目的成功实现**

**创建日期**: 2026-01-22

---

## 一、失败原因分析

### 1.1 对比 Heartopia（成功）与 UTD（失败）

| 配置项 | Heartopia（成功） | UTD（失败） | 问题 |
|-------|-----------------|-----------|------|
| **i18n 配置方式** | `defineRouting()` + `createNavigation()` | 手动配置 | ❌ 缺少完整配置 |
| **setRequestLocale** | **不需要调用** | 到处调用但位置错误 | ❌ 错误使用 |
| **根 layout.tsx** | 只返回 `children` | 包含完整 HTML 结构 | ❌ 结构冲突 |
| **localePrefix** | `'as-needed'` 始终一致 | 混乱切换 | ❌ 配置不一致 |
| **翻译文件位置** | `src/messages/` | `src/locales/` | ⚠️ 路径不同（可保持） |
| **Link 组件** | 使用 `@/i18n/navigation` | 使用 `next/link` | ❌ 缺少本地化 |

### 1.2 根本原因

1. **没有使用 `defineRouting()`**：导致 next-intl 无法自动管理 locale 上下文
2. **错误使用 `setRequestLocale`**：在验证逻辑之后调用，且位置不一致
3. **根 layout 结构错误**：根 layout 应该只返回 `children`，HTML 结构应在 `[locale]/layout.tsx` 中
4. **缺少 `createNavigation()`**：导致链接没有自动处理 locale 前缀

### 1.3 关键发现

**Heartopia 项目根本没有调用 `setRequestLocale`！**

通过阅读 Heartopia 的源码发现：
- 使用 `defineRouting()` 后，next-intl 会自动管理 locale 上下文
- 客户端组件可以直接使用 `useTranslations()`
- 服务端组件可以直接使用 `getTranslations()`
- 不需要手动调用 `setRequestLocale`

---

## 二、重构方案

### 2.1 目标文件结构

```
src/
├── i18n/                          # i18n 配置目录（重构）
│   ├── routing.ts                 # 新建：路由配置
│   ├── request.ts                 # 修改：请求配置
│   └── navigation.ts              # 新建：导航工具
│
├── locales/                       # 保持不变
│   ├── en.json
│   └── zh.json
│
├── middleware.ts                  # 修改：使用 routing 配置
│
├── app/
│   ├── layout.tsx                 # 新建：根布局（只返回 children）
│   ├── page.tsx                   # 新建：根页面（重定向）
│   ├── globals.css                # 保持不变
│   ├── ClientBody.tsx             # 保持不变
│   └── [locale]/
│       ├── layout.tsx             # 修改：本地化布局
│       ├── page.tsx               # 保持：首页（客户端组件）
│       ├── not-found.tsx          # 修改：404 页面
│       └── guides/
│           ├── page.tsx           # 修改：攻略列表
│           └── [slug]/
│               └── page.tsx       # 修改：攻略详情
│
└── components/
    ├── Navigation.tsx             # 修改：使用本地化 Link
    └── content/
        ├── NavigationPage.tsx     # 修改：使用本地化 Link
        └── DetailPage.tsx         # 修改：使用本地化 Link
```

---

## 三、具体修改内容

### 3.1 新建 `src/i18n/routing.ts`

```typescript
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  // 支持的语言列表
  locales: ['en', 'zh'],

  // 默认语言
  defaultLocale: 'en',

  // URL 前缀策略：默认语言无前缀
  localePrefix: 'as-needed',

  // 启用自动语言检测
  localeDetection: true
});

// 导出类型
export type Locale = (typeof routing.locales)[number];
```

### 3.2 新建 `src/i18n/navigation.ts`

```typescript
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter } =
  createNavigation(routing);
```

### 3.3 修改 `src/i18n/request.ts`

```typescript
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  // 验证 locale 有效性
  if (!locale || !routing.locales.includes(locale as 'en' | 'zh')) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../locales/${locale}.json`)).default
  };
});
```

### 3.4 删除 `src/i18n/config.ts`

不再需要，配置已合并到 `routing.ts`。

### 3.5 修改 `src/middleware.ts`

```typescript
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: [
    // 匹配所有路径，排除静态资源
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)',
    '/'
  ]
};
```

### 3.6 新建 `src/app/layout.tsx`（根布局）

```typescript
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
```

**关键点**：根布局只返回 `children`，不包含 HTML 结构。

### 3.7 新建 `src/app/page.tsx`（根页面）

```typescript
import { redirect } from 'next/navigation';

export default function RootPage() {
  redirect('/en');
}
```

**说明**：根路径重定向到默认语言。实际上中间件会根据浏览器语言自动重定向。

### 3.8 修改 `src/app/[locale]/layout.tsx`

```typescript
import type { Metadata } from 'next';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';
import { Geist, Geist_Mono } from 'next/font/google';
import Script from 'next/script';
import ClientBody from '../ClientBody';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

// 生成静态参数
export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

// 生成元数据
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;

  return {
    title: 'Universal Tower Defense - Codes, Tier List, Guides & Calculator | UTD Roblox',
    description: 'Complete Universal Tower Defense resource hub! Get the latest working codes, tier lists, DPS calculators, team guides, and wiki for UTD Roblox game.',
    alternates: {
      canonical: locale === 'en' ? '/' : `/${locale}`,
      languages: {
        'en': '/',
        'zh': '/zh',
        'x-default': '/'
      }
    }
  };
}

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;

  // 验证 locale
  if (!routing.locales.includes(locale as 'en' | 'zh')) {
    notFound();
  }

  // 获取翻译消息（不需要 setRequestLocale！）
  const messages = await getMessages();

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
  );
}
```

**关键变化**：
- 移除 `setRequestLocale` 调用
- 使用 `routing.locales` 验证 locale
- HTML 结构在这里定义，而不是根 layout

### 3.9 保持 `src/app/[locale]/page.tsx`（首页）

首页已经是客户端组件，使用 `useTranslations`，无需修改。

### 3.10 修改 `src/app/[locale]/not-found.tsx`

```typescript
'use client';

import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/navigation';

export default function NotFound() {
  const t = useTranslations('common');

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-slate-300 mb-4">
          {t('notFound')}
        </h2>
        <p className="text-slate-400 mb-8">
          {t('notFoundDescription')}
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          {t('backToHome')}
        </Link>
      </div>
    </div>
  );
}
```

**关键变化**：使用 `@/i18n/navigation` 的 `Link` 组件。

### 3.11 修改 `src/app/[locale]/guides/page.tsx`

```typescript
import { getTranslations } from 'next-intl/server';
import { getAllContent, type Language } from '@/lib/content';
import { NavigationPage } from '@/components/content/NavigationPage';
import { routing } from '@/i18n/routing';

interface GuidesPageProps {
  params: Promise<{ locale: string }>;
}

export default async function GuidesPage({ params }: GuidesPageProps) {
  const { locale } = await params;

  // 获取翻译（不需要 setRequestLocale！）
  const t = await getTranslations('pages.guides');

  // 获取所有攻略
  const guides = await getAllContent('guide', locale as Language);

  return (
    <NavigationPage
      title={t('title')}
      description={t('description')}
      items={guides}
      contentType="guides"
      language={locale as Language}
    />
  );
}

// 生成静态参数
export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

// 元数据
export async function generateMetadata({ params }: GuidesPageProps) {
  const { locale } = await params;
  const t = await getTranslations('pages.guides');

  return {
    title: t('metaTitle'),
    description: t('metaDescription'),
    alternates: {
      canonical: locale === 'en' ? '/guides' : `/${locale}/guides`,
      languages: {
        'en': '/guides',
        'zh': '/zh/guides',
        'x-default': '/guides'
      }
    }
  };
}
```

**关键变化**：
- 移除 `setRequestLocale` 调用
- 移除 locale 验证和重定向逻辑（由中间件处理）
- 使用 `routing.locales` 生成静态参数

### 3.12 修改 `src/app/[locale]/guides/[slug]/page.tsx`

```typescript
import { getAllContentSlugs, type Language } from '@/lib/content';
import { DetailPage } from '@/components/content/DetailPage';
import { notFound } from 'next/navigation';
import type { ContentFrontmatter } from '@/lib/content';
import { routing } from '@/i18n/routing';

interface GuidePageProps {
  params: Promise<{ locale: string; slug: string }>;
}

export default async function GuidePage({ params }: GuidePageProps) {
  const { locale, slug } = await params;

  try {
    const { default: MDXContent, metadata } = await import(
      `../../../../../content/${locale}/guide/${slug}.mdx`
    );

    return (
      <DetailPage
        frontmatter={metadata as ContentFrontmatter}
        content={<MDXContent />}
        contentType="guides"
        language={locale as Language}
      />
    );
  } catch (error) {
    notFound();
  }
}

// 生成静态参数
export async function generateStaticParams() {
  const params: { locale: string; slug: string }[] = [];

  for (const locale of routing.locales) {
    const slugs = await getAllContentSlugs('guide', locale as Language);
    params.push(...slugs.map((slug) => ({ locale, slug })));
  }

  return params;
}

// 元数据
export async function generateMetadata({ params }: GuidePageProps) {
  const { locale, slug } = await params;
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://utd-wiki.netlify.app';
  const path = `/guides/${slug}`;

  try {
    const { metadata } = await import(`../../../../../content/${locale}/guide/${slug}.mdx`);

    return {
      title: `${metadata.title} - Universal Tower Defense`,
      description: metadata.description,
      alternates: {
        canonical: locale === 'en' ? path : `/${locale}${path}`,
        languages: {
          'en': path,
          'zh': `/zh${path}`,
          'x-default': path
        }
      },
      openGraph: {
        title: metadata.title,
        description: metadata.description,
        images: metadata.image ? [metadata.image] : [],
        url: `${siteUrl}/${locale}${path}`,
      },
    };
  } catch (error) {
    return {
      title: 'Guide Not Found',
      description: 'The requested guide could not be found.',
    };
  }
}
```

**关键变化**：
- 移除 `setRequestLocale` 调用
- 移除 locale 验证和重定向逻辑
- 使用 `routing.locales` 生成静态参数

### 3.13 修改组件中的 Link 导入

**`src/components/Navigation.tsx`**:
```typescript
// 修改导入
import { Link } from '@/i18n/navigation';

// 使用方式不变，Link 会自动处理 locale 前缀
<Link href="/guides">Guides</Link>
```

**`src/components/content/NavigationPage.tsx`**:
```typescript
import { Link } from '@/i18n/navigation';
// ... 其他代码保持不变
```

**`src/components/content/DetailPage.tsx`**:
```typescript
import { Link } from '@/i18n/navigation';
// ... 其他代码保持不变
```

---

## 四、修改文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/i18n/routing.ts` | **新建** | 定义路由配置 |
| `src/i18n/navigation.ts` | **新建** | 创建本地化导航组件 |
| `src/i18n/request.ts` | **修改** | 使用 routing 配置 |
| `src/i18n/config.ts` | **删除** | 合并到 routing.ts |
| `src/middleware.ts` | **修改** | 使用 routing 配置 |
| `src/app/layout.tsx` | **新建** | 根布局（只返回 children） |
| `src/app/page.tsx` | **新建** | 根页面（重定向） |
| `src/app/[locale]/layout.tsx` | **修改** | 移除 setRequestLocale，使用 routing |
| `src/app/[locale]/not-found.tsx` | **修改** | 使用本地化 Link |
| `src/app/[locale]/guides/page.tsx` | **修改** | 移除 setRequestLocale |
| `src/app/[locale]/guides/[slug]/page.tsx` | **修改** | 移除 setRequestLocale |
| `src/components/Navigation.tsx` | **修改** | 使用本地化 Link |
| `src/components/content/NavigationPage.tsx` | **修改** | 使用本地化 Link |
| `src/components/content/DetailPage.tsx` | **修改** | 使用本地化 Link |

---

## 五、验证步骤

### 5.1 清理并重新构建

```bash
rm -rf .next
npm run build
```

### 5.2 预期结果

```bash
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Collecting page data
✓ Generating static pages (X/X)
✓ Finalizing page optimization

Route (app)                              Size
┌ ○ /                                    ...
├ ○ /[locale]                            ...
├ ○ /[locale]/guides                     ...
└ ○ /[locale]/guides/[slug]              ...
```

### 5.3 测试路由

| URL | 预期行为 |
|-----|---------|
| `/` | 重定向到 `/` (英文) 或 `/zh` (根据浏览器语言) |
| `/guides` | 英文攻略列表（无前缀） |
| `/zh` | 中文首页 |
| `/zh/guides` | 中文攻略列表 |
| `/guides/beginner` | 英文攻略详情 |
| `/zh/guides/beginner` | 中文攻略详情 |

### 5.4 测试语言切换

- 在英文页面切换到中文 → URL 变为 `/zh/...`
- 在中文页面切换到英文 → URL 变为 `/...`（无前缀）

---

## 六、关键教训

### 6.1 使用完整的 next-intl 配置

```
defineRouting()     → 定义路由规则
createNavigation()  → 创建本地化导航
createMiddleware()  → 处理请求
```

### 6.2 不需要手动调用 `setRequestLocale`

使用 `defineRouting` 后，next-intl 自动管理上下文：
- 客户端组件：直接使用 `useTranslations()`
- 服务端组件：直接使用 `getTranslations()`
- Layout：只需调用 `getMessages()`

### 6.3 根 layout 应该简单

```typescript
// src/app/layout.tsx
export default function RootLayout({ children }) {
  return children;  // 只返回 children！
}
```

HTML 结构（`<html>`, `<body>`）应该在 `[locale]/layout.tsx` 中定义。

### 6.4 使用本地化 Link 组件

```typescript
// ❌ 错误
import Link from 'next/link';

// ✅ 正确
import { Link } from '@/i18n/navigation';
```

本地化 Link 会自动处理 locale 前缀。

### 6.5 localePrefix: 'as-needed' 的行为

| 语言 | URL 示例 |
|------|---------|
| 英语（默认） | `/guides` |
| 中文 | `/zh/guides` |

默认语言无前缀，其他语言有前缀。

---

## 七、参考资源

- [Heartopia 项目实现](/Users/libin91/Documents/GameProjects/0113Heartopia/)
- [多语言实现技术文档](./多语言实现技术文档.md)
- [next-intl 官方文档](https://next-intl-docs.vercel.app/)
- [Next.js App Router 国际化](https://nextjs.org/docs/app/building-your-application/routing/internationalization)

---

## 八、变更历史

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-01-22 | 1.0 | 初始版本，基于 Heartopia 成功实现 |
