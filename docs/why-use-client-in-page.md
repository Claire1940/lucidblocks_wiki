# 为什么 `src/app/[locale]/page.tsx` 需要使用 `'use client'`

## 概述

在 Next.js 15 的 App Router 中，组件默认是**服务器组件**（Server Components）。但是 `src/app/[locale]/page.tsx` 必须声明为**客户端组件**（Client Component），通过在文件顶部添加 `'use client'` 指令来实现。

## 服务器组件 vs 客户端组件

### 服务器组件（Server Components）
- 在服务器端渲染
- 可以直接访问数据库、文件系统等后端资源
- 不能使用浏览器 API
- 不能使用 React Hooks（useState, useEffect 等）
- 不能添加事件处理器（onClick, onChange 等）
- 包体积更小，性能更好

### 客户端组件（Client Components）
- 在浏览器中渲染
- 可以使用 React Hooks
- 可以使用浏览器 API
- 可以添加交互功能
- 需要下载到客户端，包体积更大

## `page.tsx` 为什么必须是客户端组件

让我们看看 `src/app/[locale]/page.tsx` 中使用的功能：

### 1. React Hooks

```typescript
import { useEffect, useRef } from 'react'
import { useTranslations } from 'next-intl'

export default function HomePage() {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const t = useTranslations()

  useEffect(() => {
    // 创建观察器
    observerRef.current = new IntersectionObserver(...)
  }, [])
}
```

**使用的 Hooks：**
- `useRef` - 存储 IntersectionObserver 实例
- `useEffect` - 设置和清理观察器
- `useTranslations` - next-intl 的客户端 hook

**为什么需要客户端：** 所有 React Hooks 只能在客户端组件中使用。

### 2. 浏览器 API

```typescript
useEffect(() => {
  observerRef.current = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('scroll-reveal-visible')
        }
      })
    },
    { threshold: 0.1 }
  )

  // 观察所有带有 scroll-reveal 类的元素
  const elements = document.querySelectorAll('.scroll-reveal')
  elements.forEach((el) => observerRef.current?.observe(el))
}, [])
```

**使用的浏览器 API：**
- `IntersectionObserver` - 监听元素进入视口
- `document.querySelectorAll` - 查询 DOM 元素
- `classList.add` - 操作 DOM 类名

**为什么需要客户端：** 这些 API 只存在于浏览器环境中，服务器端没有 DOM。

### 3. 交互功能

```typescript
<Button
  onClick={() => window.location.href = '#features'}
  className="..."
>
  {t('hero.cta')}
</Button>
```

**交互功能：**
- `onClick` 事件处理器
- 按钮点击、表单提交等用户交互
- 动画和过渡效果

**为什么需要客户端：** 事件处理器需要在客户端执行。

### 4. 滚动揭示动画

页面使用了 Intersection Observer 实现滚动揭示动画：

```typescript
// 当元素进入视口时添加动画类
if (entry.isIntersecting) {
  entry.target.classList.add('scroll-reveal-visible')
}
```

配合 CSS：

```css
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

.scroll-reveal-visible {
  opacity: 1;
  transform: translateY(0);
}
```

**为什么需要客户端：** 动画需要在用户滚动时实时响应，这是纯客户端行为。

## 如果不使用 `'use client'` 会发生什么？

如果移除 `'use client'` 指令，会遇到以下错误：

```
Error: useEffect only works in Client Components
Error: useRef only works in Client Components
Error: IntersectionObserver is not defined
Error: document is not defined
```

## 最佳实践

### ✅ 正确做法

```typescript
'use client'  // 在文件顶部声明

import { useEffect, useRef } from 'react'
import { useTranslations } from 'next-intl'

export default function HomePage() {
  // 可以使用所有客户端功能
}
```

### ❌ 错误做法

```typescript
// 没有 'use client' 声明

import { useEffect, useRef } from 'react'  // ❌ 会报错

export default function HomePage() {
  useEffect(() => {  // ❌ 会报错
    // ...
  })
}
```

## 性能考虑

虽然客户端组件需要下载到浏览器，但这是必要的权衡：

### 优点
- 提供丰富的交互体验
- 实现复杂的动画效果
- 响应用户操作

### 优化策略
1. **代码分割**：Next.js 自动进行代码分割
2. **懒加载**：使用 `dynamic()` 延迟加载重型组件
3. **服务器组件优先**：尽可能使用服务器组件，只在必要时使用客户端组件

## 混合使用服务器组件和客户端组件

在同一个应用中，你可以混合使用：

```
src/app/[locale]/
├── layout.tsx              # 服务器组件（加载翻译消息）
├── page.tsx                # 客户端组件（交互和动画）
└── guides/
    ├── page.tsx            # 服务器组件（列表页，无交互）
    └── [slug]/
        └── page.tsx        # 服务器组件（详情页，静态内容）
```

**规则：**
- 服务器组件可以导入客户端组件
- 客户端组件**不能**导入服务器组件（但可以通过 children 传递）

## next-intl 的特殊情况

### 服务器组件中使用翻译

```typescript
// guides/page.tsx - 服务器组件
import { getTranslations } from 'next-intl/server'

export default async function GuidesPage() {
  const t = await getTranslations()  // 异步函数

  return <div>{t('pages.guides.title')}</div>
}
```

### 客户端组件中使用翻译

```typescript
// page.tsx - 客户端组件
'use client'

import { useTranslations } from 'next-intl'

export default function HomePage() {
  const t = useTranslations()  // Hook，非异步

  return <div>{t('hero.title')}</div>
}
```

**关键区别：**
- 服务器组件：使用 `getTranslations()` - 异步函数
- 客户端组件：使用 `useTranslations()` - React Hook

## 总结

`src/app/[locale]/page.tsx` 必须使用 `'use client'` 因为它：

1. ✅ 使用 React Hooks（useEffect, useRef, useTranslations）
2. ✅ 使用浏览器 API（IntersectionObserver, document）
3. ✅ 需要事件处理器（onClick 等）
4. ✅ 实现滚动动画和交互效果

这是一个**营销首页**，需要丰富的交互和动画来吸引用户，因此客户端组件是正确的选择。

对于其他页面（如攻略列表、详情页），如果不需要交互，应该优先使用服务器组件以获得更好的性能。

## 参考资料

- [Next.js Server Components](https://nextjs.org/docs/app/building-your-application/rendering/server-components)
- [Next.js Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [next-intl Usage](https://next-intl-docs.vercel.app/docs/usage)
