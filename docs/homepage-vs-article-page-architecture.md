# 首页 vs 文章页：架构选型详解

## 目录

1. [概述](#概述)
2. [首页架构分析](#首页架构分析)
3. [文章页架构分析](#文章页架构分析)
4. [选型对比](#选型对比)
5. [为什么不能反过来？](#为什么不能反过来)
6. [性能影响](#性能影响)
7. [最佳实践建议](#最佳实践建议)

---

## 概述

在我们的项目中，首页和文章页采用了不同的架构方案：

| 页面类型 | 组件类型 | 翻译 API | 原因 |
|---------|---------|---------|------|
| **首页** | 客户端组件 (`'use client'`) | `useTranslations()` Hook | 需要交互和动画 |
| **文章页** | 服务器组件 (默认) | `getTranslations()` 异步函数 | 静态内容，需要 SEO |

**核心问题：为什么不能都用同一种方案？**

答案：因为它们的**业务需求**和**技术要求**完全不同。

---

## 首页架构分析

### 首页代码结构

```typescript
// src/app/[locale]/page.tsx
'use client'  // ← 关键：声明为客户端组件

import { useEffect, useRef } from 'react'
import { useTranslations } from 'next-intl'

export default function HomePage() {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const t = useTranslations()  // ← 使用 Hook

  useEffect(() => {
    // 设置滚动动画
    observerRef.current = new IntersectionObserver(...)
  }, [])

  return (
    <div>
      <h1>{t.hero.title}</h1>
      {/* 大量交互元素 */}
    </div>
  )
}
```

### 为什么首页必须是客户端组件？

#### 1. 需要滚动动画

```typescript
useEffect(() => {
  // 创建 IntersectionObserver 监听滚动
  observerRef.current = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')  // 添加动画类
        }
      })
    },
    { threshold: 0.1 }
  )

  // 观察所有需要动画的元素
  const elements = document.querySelectorAll('.scroll-reveal')
  elements.forEach((el) => observerRef.current?.observe(el))
}, [])
```

**为什么需要客户端？**
- `IntersectionObserver` 是浏览器 API，服务器端不存在
- `document.querySelectorAll` 需要访问 DOM，服务器端没有 DOM
- 动画需要实时响应用户滚动，必须在浏览器中执行

**如果改为服务器组件会怎样？**
```typescript
// ❌ 错误：服务器组件不能使用浏览器 API
export default async function HomePage() {
  useEffect(() => {  // ❌ 错误：服务器组件不能使用 useEffect
    const observer = new IntersectionObserver(...)  // ❌ 错误：服务器端没有这个 API
  }, [])
}

// 错误信息：
// Error: useEffect only works in Client Components
// Error: IntersectionObserver is not defined
```

#### 2. 需要用户交互

```typescript
// 首页有大量交互元素
<Button onClick={() => handleClick()}>
  {t.hero.getFreeCodesCTA}
</Button>

<form onSubmit={handleSubmit}>
  <input onChange={handleChange} />
</form>
```

**为什么需要客户端？**
- `onClick`、`onSubmit`、`onChange` 等事件处理器只能在客户端工作
- 用户交互需要 JavaScript 在浏览器中执行
- 服务器组件生成的是静态 HTML，没有交互能力

#### 3. 需要 React Hooks

```typescript
const observerRef = useRef<IntersectionObserver | null>(null)  // 存储实例
const [isOpen, setIsOpen] = useState(false)  // 状态管理
const t = useTranslations()  // 翻译 Hook

useEffect(() => {
  // 副作用处理
}, [])
```

**为什么需要客户端？**
- 所有 React Hooks 只能在客户端组件中使用
- 服务器组件不支持 `useState`、`useEffect`、`useRef` 等
- `useTranslations()` 本身就是一个 Hook

#### 4. 需要动态更新

```typescript
// 用户切换语言时，首页需要立即更新
<LanguageSwitcher onChange={(locale) => {
  setLocale(locale)  // 更新状态
  // 所有使用 useTranslations() 的文本自动更新
}} />
```

**为什么需要客户端？**
- 语言切换需要重新渲染组件
- `useTranslations()` Hook 自动订阅 Context 变化
- 服务器组件无法响应客户端状态变化

### 首页的业务需求

| 需求 | 是否需要客户端 | 原因 |
|------|---------------|------|
| 滚动动画 | ✅ 必须 | 需要 IntersectionObserver |
| 按钮点击 | ✅ 必须 | 需要事件处理器 |
| 表单交互 | ✅ 必须 | 需要状态管理 |
| 语言切换 | ✅ 必须 | 需要动态更新 |
| 动态效果 | ✅ 必须 | 需要 JavaScript |
| SEO 优化 | ❌ 次要 | 首页主要是营销，SEO 不是最优先 |

**结论：首页必须是客户端组件，因此必须使用 `useTranslations()` Hook。**

---

## 文章页架构分析

### 文章页代码结构

```typescript
// src/app/[locale]/guides/page.tsx
// 注意：没有 'use client' 声明，默认是服务器组件

import { getTranslations } from 'next-intl/server'
import { getAllContent } from '@/lib/content'

export default async function GuidesPage({ params }) {
  const { locale } = await params

  // 使用异步函数获取翻译
  const t = await getTranslations()

  // 获取所有攻略文章
  const guides = await getAllContent('guide', locale)

  return (
    <div>
      <h1>{t('pages.guides.title')}</h1>
      <ul>
        {guides.map(guide => (
          <li key={guide.slug}>{guide.title}</li>
        ))}
      </ul>
    </div>
  )
}
```

### 为什么文章页应该是服务器组件？

#### 1. 主要是静态内容

```typescript
// 文章页的内容
<article>
  <h1>{metadata.title}</h1>
  <p>{metadata.description}</p>

  {/* MDX 渲染的文章内容 */}
  <MDXContent />

  {/* 静态的导航链接 */}
  <Link href="/guides">返回列表</Link>
</article>
```

**为什么适合服务器组件？**
- 文章内容是静态的，不需要交互
- 不需要 JavaScript 就能显示完整内容
- 用户主要是阅读，不需要复杂的客户端逻辑

**如果改为客户端组件会怎样？**
```typescript
'use client'

// ❌ 问题 1：增加包体积
// 所有文章内容都需要下载到客户端
// 用户需要等待 JavaScript 加载才能看到内容

// ❌ 问题 2：SEO 变差
// 搜索引擎可能无法正确索引内容
// 初始 HTML 中可能没有完整的文章内容

// ❌ 问题 3：性能下降
// 首次内容绘制 (FCP) 变慢
// 用户体验变差
```

#### 2. 需要 SEO 优化

```typescript
// 文章页需要良好的 SEO
export async function generateMetadata({ params }) {
  const { locale, slug } = await params
  const t = await getTranslations()

  return {
    title: `${metadata.title} - Universal Tower Defense`,
    description: metadata.description,
    openGraph: {
      title: metadata.title,
      description: metadata.description,
      images: [metadata.image],
    },
  }
}
```

**为什么需要服务器组件？**
- 服务器组件生成完整的 HTML，搜索引擎可以直接索引
- 元数据在服务器端生成，SEO 效果更好
- 不依赖 JavaScript，爬虫可以轻松抓取内容

**客户端组件的 SEO 问题：**
```typescript
'use client'

// ❌ SEO 问题
export default function ArticlePage() {
  const [content, setContent] = useState(null)

  useEffect(() => {
    // 内容在客户端加载
    loadContent().then(setContent)
  }, [])

  // 初始 HTML 中没有内容
  // 搜索引擎可能看不到文章内容
  return <div>{content}</div>
}
```

#### 3. 可以使用异步数据加载

```typescript
export default async function ArticlePage({ params }) {
  const { locale, slug } = await params

  // 可以并行加载多个数据源
  const [t, article, relatedArticles] = await Promise.all([
    getTranslations(),
    getArticle(slug),
    getRelatedArticles(slug),
  ])

  return (
    <div>
      <h1>{article.title}</h1>
      <article>{article.content}</article>

      <aside>
        <h2>{t('related.title')}</h2>
        {relatedArticles.map(item => (
          <Link key={item.slug} href={item.slug}>
            {item.title}
          </Link>
        ))}
      </aside>
    </div>
  )
}
```

**为什么适合服务器组件？**
- 可以直接使用 `async/await` 加载数据
- 数据在服务器端准备好，直接渲染成 HTML
- 用户看到的是完整的页面，无需等待客户端加载

**客户端组件的数据加载问题：**
```typescript
'use client'

export default function ArticlePage() {
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // ❌ 问题：用户需要等待数据加载
    loadArticle().then(data => {
      setArticle(data)
      setLoading(false)
    })
  }, [])

  // ❌ 问题：初始渲染显示加载状态
  if (loading) return <div>Loading...</div>

  return <div>{article.content}</div>
}
```

#### 4. 更好的性能

```typescript
// 服务器组件的性能优势

// 1. 零 JavaScript 包体积
// 文章内容不需要下载 JavaScript 就能显示

// 2. 更快的首次内容绘制 (FCP)
// HTML 中包含完整内容，立即可见

// 3. 更小的客户端包
// 不需要下载 React、翻译库等

// 4. 更好的缓存
// 静态 HTML 可以被 CDN 缓存
```

### 文章页的业务需求

| 需求 | 是否需要客户端 | 原因 |
|------|---------------|------|
| 显示文章内容 | ❌ 不需要 | 静态内容，服务器渲染即可 |
| SEO 优化 | ❌ 不需要 | 服务器组件 SEO 更好 |
| 快速加载 | ❌ 不需要 | 服务器组件性能更好 |
| 文章列表 | ❌ 不需要 | 静态列表，无需交互 |
| 导航链接 | ❌ 不需要 | 普通链接，无需 JavaScript |
| 滚动动画 | ❌ 不需要 | 文章页不需要花哨的动画 |
| 表单交互 | ❌ 不需要 | 文章页主要是阅读 |

**结论：文章页应该是服务器组件，因此应该使用 `getTranslations()` 异步函数。**

---

## 选型对比

### 技术对比

| 特性 | 首页（客户端组件） | 文章页（服务器组件） |
|------|------------------|-------------------|
| **组件声明** | `'use client'` | 无声明（默认） |
| **翻译 API** | `useTranslations()` Hook | `getTranslations()` 异步函数 |
| **是否异步** | ❌ 否 | ✅ 是 |
| **React Hooks** | ✅ 可以使用 | ❌ 不能使用 |
| **浏览器 API** | ✅ 可以使用 | ❌ 不能使用 |
| **事件处理器** | ✅ 可以使用 | ❌ 不能使用 |
| **JavaScript 包** | 较大（需要下载） | 零（不需要 JS） |
| **首次加载** | 较慢（需要 JS） | 快速（纯 HTML） |
| **SEO** | 一般 | 优秀 |
| **交互能力** | 强大 | 无 |

### 业务需求对比

| 需求 | 首页 | 文章页 |
|------|------|--------|
| **主要目的** | 营销、吸引用户 | 提供信息、教育用户 |
| **用户行为** | 浏览、点击、交互 | 阅读、学习 |
| **内容类型** | 动态、交互式 | 静态、文本为主 |
| **更新频率** | 较低（设计变化） | 较高（新文章） |
| **SEO 重要性** | 中等 | 非常重要 |
| **性能要求** | 流畅的动画 | 快速加载 |
| **用户期望** | 视觉吸引力 | 内容质量 |

### 用户体验对比

#### 首页用户体验

```
用户访问首页
    ↓
看到加载动画（可接受，因为有视觉反馈）
    ↓
JavaScript 加载完成
    ↓
页面开始动画（滚动揭示效果）
    ↓
用户滚动页面
    ↓
元素逐个淡入（吸引注意力）
    ↓
用户点击按钮
    ↓
立即响应（良好的交互体验）
```

**用户期望：**
- 视觉吸引力 ✅
- 流畅的动画 ✅
- 即时的交互响应 ✅

#### 文章页用户体验

```
用户访问文章页
    ↓
立即看到完整内容（无需等待 JavaScript）
    ↓
开始阅读文章
    ↓
滚动浏览内容
    ↓
点击链接跳转到其他文章
    ↓
快速加载（服务器渲染）
```

**用户期望：**
- 快速看到内容 ✅
- 无需等待加载 ✅
- 流畅的阅读体验 ✅

---

## 为什么不能反过来？

### 场景 1：如果首页改为服务器组件

```typescript
// ❌ 错误：首页改为服务器组件
import { getTranslations } from 'next-intl/server'

export default async function HomePage() {
  const t = await getTranslations()

  // ❌ 问题 1：不能使用 useEffect
  useEffect(() => {
    // 错误：服务器组件不支持 useEffect
  }, [])

  // ❌ 问题 2：不能使用 IntersectionObserver
  const observer = new IntersectionObserver(...)  // 错误：服务器端没有这个 API

  // ❌ 问题 3：不能使用事件处理器
  return (
    <Button onClick={() => handleClick()}>  {/* 错误：服务器组件不支持 onClick */}
      {t('hero.cta')}
    </Button>
  )
}
```

**结果：**
- ❌ 无法实现滚动动画
- ❌ 无法实现按钮交互
- ❌ 无法实现语言切换
- ❌ 首页变成静态页面，失去吸引力

**结论：首页必须是客户端组件。**

### 场景 2：如果文章页改为客户端组件

```typescript
'use client'

import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'

export default function ArticlePage({ params }) {
  const t = useTranslations()
  const [article, setArticle] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 在客户端加载文章
    loadArticle(params.slug).then(data => {
      setArticle(data)
      setLoading(false)
    })
  }, [params.slug])

  if (loading) return <div>Loading...</div>

  return (
    <article>
      <h1>{article.title}</h1>
      <div>{article.content}</div>
    </article>
  )
}
```

**问题：**

1. **SEO 变差**
   ```html
   <!-- 初始 HTML（搜索引擎看到的） -->
   <div>Loading...</div>

   <!-- 搜索引擎可能看不到文章内容 -->
   ```

2. **性能下降**
   ```
   用户访问文章页
       ↓
   看到 "Loading..." （体验差）
       ↓
   等待 JavaScript 下载（慢）
       ↓
   等待 React 初始化（慢）
       ↓
   等待文章数据加载（慢）
       ↓
   终于看到内容（用户可能已经离开）
   ```

3. **包体积增加**
   ```
   服务器组件：0 KB JavaScript
   客户端组件：~100 KB JavaScript（React + 翻译库 + 文章内容）
   ```

4. **缓存效率降低**
   ```
   服务器组件：CDN 可以缓存完整的 HTML
   客户端组件：只能缓存 JavaScript，每次都需要客户端渲染
   ```

**结论：文章页应该是服务器组件。**

---

## 性能影响

### 首页性能指标

| 指标 | 客户端组件 | 服务器组件（假设） |
|------|-----------|------------------|
| **FCP (首次内容绘制)** | ~1.5s | ~0.8s ✅ |
| **LCP (最大内容绘制)** | ~2.5s | ~1.2s ✅ |
| **TTI (可交互时间)** | ~2.0s | ∞ (无交互) ❌ |
| **JavaScript 包大小** | ~150 KB | 0 KB ✅ |
| **动画流畅度** | 60 FPS ✅ | 无动画 ❌ |
| **交互响应** | 即时 ✅ | 无交互 ❌ |

**结论：首页需要交互，客户端组件是正确选择。**

### 文章页性能指标

| 指标 | 服务器组件 | 客户端组件（假设） |
|------|-----------|------------------|
| **FCP (首次内容绘制)** | ~0.5s ✅ | ~1.8s |
| **LCP (最大内容绘制)** | ~0.8s ✅ | ~2.5s |
| **TTI (可交互时间)** | ~0.5s ✅ | ~2.5s |
| **JavaScript 包大小** | 0 KB ✅ | ~120 KB |
| **SEO 得分** | 100/100 ✅ | 70/100 |
| **缓存效率** | 高 ✅ | 低 |

**结论：文章页主要是内容展示，服务器组件是正确选择。**

---

## 最佳实践建议

### 如何判断应该使用哪种组件？

#### 使用客户端组件的场景

✅ **需要使用以下任何一项时：**
- React Hooks（useState, useEffect, useRef 等）
- 浏览器 API（IntersectionObserver, localStorage 等）
- 事件处理器（onClick, onChange 等）
- 动画和过渡效果
- 实时响应用户操作
- 第三方客户端库（图表、地图等）

**示例页面：**
- 首页（营销页面）
- 表单页面
- 仪表板
- 交互式工具（计算器、编辑器等）
- 实时聊天

#### 使用服务器组件的场景

✅ **满足以下条件时：**
- 主要是静态内容展示
- 需要良好的 SEO
- 需要快速的首次加载
- 不需要客户端交互
- 需要访问后端资源（数据库、文件系统）

**示例页面：**
- 博客文章
- 文档页面
- 产品列表
- 关于我们
- 静态内容页

### 混合使用策略

```typescript
// 服务器组件（外层）
export default async function ArticlePage() {
  const article = await getArticle()

  return (
    <div>
      {/* 静态内容：服务器渲染 */}
      <h1>{article.title}</h1>
      <article>{article.content}</article>

      {/* 交互组件：客户端渲染 */}
      <CommentSection articleId={article.id} />
      <LikeButton articleId={article.id} />
    </div>
  )
}

// 客户端组件（内层）
'use client'
function CommentSection({ articleId }) {
  const [comments, setComments] = useState([])

  return (
    <div>
      {/* 交互式评论功能 */}
    </div>
  )
}
```

**优势：**
- 主要内容快速加载（服务器渲染）
- 交互功能正常工作（客户端渲染）
- 最佳的性能和用户体验

### 决策流程图

```
开始
  ↓
需要交互吗？
  ├─ 是 → 需要动画吗？
  │        ├─ 是 → 客户端组件 + useTranslations()
  │        └─ 否 → 需要表单吗？
  │                 ├─ 是 → 客户端组件 + useTranslations()
  │                 └─ 否 → 需要实时更新吗？
  │                          ├─ 是 → 客户端组件 + useTranslations()
  │                          └─ 否 → 考虑服务器组件
  │
  └─ 否 → 需要 SEO 吗？
           ├─ 是 → 服务器组件 + getTranslations()
           └─ 否 → 内容是静态的吗？
                    ├─ 是 → 服务器组件 + getTranslations()
                    └─ 否 → 客户端组件 + useTranslations()
```

---

## 总结

### 首页选型总结

**为什么使用客户端组件 + useTranslations()？**

| 原因 | 说明 |
|------|------|
| ✅ 需要滚动动画 | IntersectionObserver 只在浏览器中可用 |
| ✅ 需要用户交互 | 按钮点击、表单提交等需要事件处理器 |
| ✅ 需要 React Hooks | useEffect、useRef 等只能在客户端组件中使用 |
| ✅ 需要动态更新 | 语言切换需要重新渲染 |
| ✅ 营销页面特性 | 视觉吸引力比 SEO 更重要 |

### 文章页选型总结

**为什么使用服务器组件 + getTranslations()？**

| 原因 | 说明 |
|------|------|
| ✅ 主要是静态内容 | 文章内容不需要交互 |
| ✅ 需要 SEO 优化 | 搜索引擎需要索引文章内容 |
| ✅ 需要快速加载 | 用户期望立即看到内容 |
| ✅ 零 JavaScript | 不需要下载 JS 就能阅读 |
| ✅ 更好的缓存 | CDN 可以缓存完整的 HTML |

### 核心原则

**根据页面的主要功能选择架构：**

- **交互为主** → 客户端组件 + `useTranslations()` Hook
- **内容为主** → 服务器组件 + `getTranslations()` 异步函数

**不要为了统一而统一，要根据实际需求选择最合适的方案。**

---

## 参考资料

- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Next.js Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [React Hooks](https://react.dev/reference/react)
