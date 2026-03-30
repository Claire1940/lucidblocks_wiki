# 首页 React Hooks 应用详解

## 目录

1. [概述](#概述)
2. [使用的 Hooks](#使用的-hooks)
3. [useRef Hook 详解](#useref-hook-详解)
4. [useEffect Hook 详解](#useeffect-hook-详解)
5. [useTranslations Hook 详解](#usetranslations-hook-详解)
6. [完整实现流程](#完整实现流程)
7. [性能优化](#性能优化)
8. [常见问题](#常见问题)

---

## 概述

首页 (`src/app/[locale]/page.tsx`) 是一个营销页面，使用了三个核心 React Hooks 来实现：

1. **useRef** - 存储 IntersectionObserver 实例
2. **useEffect** - 设置滚动动画观察器
3. **useTranslations** - 实现国际化翻译

这些 Hooks 协同工作，创建了一个具有流畅滚动动画和多语言支持的现代化营销页面。

---

## 使用的 Hooks

### 导入声明

```typescript
'use client'

import { useEffect, useRef } from 'react'
import { useTranslations } from 'next-intl'

export default function HomePage() {
  const observerRef = useRef<IntersectionObserver | null>(null)
  const t = useTranslations()

  useEffect(() => {
    // 设置滚动动画
  }, [])

  return (
    // JSX 内容
  )
}
```

---

## useRef Hook 详解

### 基础原理

`useRef` 是一个 React Hook，用于在组件的整个生命周期中保持一个可变的引用值。

**核心特性：**
- 返回一个可变的 ref 对象，其 `.current` 属性被初始化为传入的参数
- 在组件的整个生命周期中保持不变
- 修改 `.current` 属性**不会**触发组件重新渲染
- 常用于存储 DOM 引用或任何需要持久化但不需要触发渲染的值

### 语法

```typescript
const refContainer = useRef<Type>(initialValue)
```

### 在首页中的应用

#### 1. 存储 IntersectionObserver 实例

```typescript
const observerRef = useRef<IntersectionObserver | null>(null)
```

**为什么使用 useRef？**

1. **持久化存储**：IntersectionObserver 实例需要在组件的整个生命周期中保持存在
2. **避免重复创建**：如果使用普通变量，每次渲染都会重新创建
3. **不触发渲染**：修改 observer 不需要重新渲染组件
4. **清理资源**：在组件卸载时需要访问同一个实例来断开连接

#### 2. 类型定义

```typescript
useRef<IntersectionObserver | null>(null)
```

- `IntersectionObserver` - 浏览器 API 类型
- `| null` - 初始值为 null，稍后赋值
- 泛型确保类型安全

#### 3. 使用示例

```typescript
// 创建并存储 observer
observerRef.current = new IntersectionObserver(...)

// 使用 observer
observerRef.current?.observe(element)

// 清理 observer
observerRef.current?.disconnect()
```

### useRef vs useState

| 特性 | useRef | useState |
|------|--------|----------|
| 触发渲染 | ❌ 不触发 | ✅ 触发 |
| 值的访问 | `.current` 属性 | 直接访问 |
| 更新方式 | 直接赋值 | 调用 setter 函数 |
| 使用场景 | DOM 引用、定时器、第三方库实例 | UI 状态、表单数据 |

**为什么不用 useState？**

```typescript
// ❌ 错误做法
const [observer, setObserver] = useState<IntersectionObserver | null>(null)

useEffect(() => {
  setObserver(new IntersectionObserver(...))  // 会触发重新渲染！
}, [])
```

使用 useState 会导致：
1. 不必要的重新渲染
2. 性能下降
3. 可能导致无限循环

---

## useEffect Hook 详解

### 基础原理

`useEffect` 是 React 中处理副作用（side effects）的 Hook。

**副作用包括：**
- 数据获取
- 订阅设置
- DOM 操作
- 定时器
- 日志记录

**执行时机：**
- 组件挂载后（首次渲染后）
- 依赖项变化后
- 组件卸载前（清理函数）

### 语法

```typescript
useEffect(() => {
  // 副作用代码

  return () => {
    // 清理代码（可选）
  }
}, [dependencies])  // 依赖数组
```

### 在首页中的应用

#### 完整代码

```typescript
useEffect(() => {
  // 1. 创建 IntersectionObserver
  observerRef.current = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
        }
      })
    },
    { threshold: 0.1 }
  )

  // 2. 查找所有需要观察的元素
  const elements = document.querySelectorAll('.scroll-reveal')

  // 3. 开始观察每个元素
  elements.forEach((el) => observerRef.current?.observe(el))

  // 4. 清理函数：组件卸载时断开观察器
  return () => observerRef.current?.disconnect()
}, [])  // 空依赖数组 = 只在挂载时执行一次
```

#### 详细解析

##### 1. IntersectionObserver 创建

```typescript
observerRef.current = new IntersectionObserver(
  (entries) => {
    // 回调函数：当元素进入/离开视口时触发
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // 元素进入视口
        entry.target.classList.add('visible')
      }
    })
  },
  { threshold: 0.1 }  // 配置：元素 10% 可见时触发
)
```

**IntersectionObserver 参数：**

1. **回调函数** `(entries) => {...}`
   - `entries`: 被观察元素的数组
   - `entry.isIntersecting`: 元素是否在视口中
   - `entry.target`: 被观察的 DOM 元素

2. **配置对象** `{ threshold: 0.1 }`
   - `threshold`: 触发阈值（0-1）
   - `0.1` = 元素 10% 可见时触发
   - `1.0` = 元素 100% 可见时触发

##### 2. 查找目标元素

```typescript
const elements = document.querySelectorAll('.scroll-reveal')
```

- 查找所有带有 `.scroll-reveal` 类的元素
- 返回 NodeList（类数组对象）
- 这些元素将被添加滚动动画

##### 3. 开始观察

```typescript
elements.forEach((el) => observerRef.current?.observe(el))
```

- 遍历所有元素
- 使用 `?.` 可选链操作符（防止 null 错误）
- 调用 `observe()` 开始观察每个元素

##### 4. 清理函数

```typescript
return () => observerRef.current?.disconnect()
```

**为什么需要清理？**

1. **防止内存泄漏**：observer 持有 DOM 元素的引用
2. **释放资源**：停止监听滚动事件
3. **React 最佳实践**：清理所有副作用

**何时执行？**
- 组件卸载时
- 依赖项变化时（本例中不会，因为依赖数组为空）

##### 5. 依赖数组

```typescript
}, [])  // 空数组
```

**依赖数组的作用：**

| 依赖数组 | 执行时机 | 使用场景 |
|---------|---------|---------|
| `[]` | 仅挂载时执行一次 | 初始化、订阅、一次性设置 |
| `[dep1, dep2]` | 挂载时 + 依赖变化时 | 响应状态变化 |
| 无依赖数组 | 每次渲染后 | ⚠️ 很少使用，可能导致性能问题 |

**本例使用空数组的原因：**
- observer 只需要创建一次
- 不需要响应任何状态变化
- 避免重复创建和销毁

### useEffect 执行流程图

```
组件挂载
    ↓
执行 useEffect 内的代码
    ↓
创建 IntersectionObserver
    ↓
查找 .scroll-reveal 元素
    ↓
开始观察所有元素
    ↓
用户滚动页面
    ↓
元素进入视口 (10% 可见)
    ↓
触发回调函数
    ↓
添加 'visible' 类
    ↓
CSS 动画生效
    ↓
组件卸载
    ↓
执行清理函数
    ↓
断开 observer 连接
```

---

## useTranslations Hook 详解

### 基础原理

`useTranslations` 是 next-intl 库提供的客户端 Hook，用于在 React 组件中访问翻译文本。

**核心功能：**
- 根据当前语言返回对应的翻译文本
- 支持嵌套的翻译键
- 类型安全（TypeScript）
- 自动响应语言切换

### 语法

```typescript
const t = useTranslations()
```

### 在首页中的应用

#### 1. 基本使用

```typescript
const t = useTranslations() as any  // 使用 any 避免类型错误

// 访问翻译文本
<h1>{t.hero.title}</h1>
<p>{t.hero.description}</p>
```

#### 2. 翻译文件结构

**en.json (英文)**
```json
{
  "hero": {
    "title": "Universal Tower Defense",
    "description": "The ultimate tower defense experience",
    "badge": "New Update Available"
  },
  "tools": {
    "title": "Tools &",
    "titleHighlight": "Resources"
  }
}
```

**zh.json (中文)**
```json
{
  "hero": {
    "title": "通用塔防",
    "description": "终极塔防体验",
    "badge": "新版本可用"
  },
  "tools": {
    "title": "工具与",
    "titleHighlight": "资源"
  }
}
```

#### 3. 访问嵌套翻译

```typescript
// 简单访问
{t.hero.title}

// 嵌套访问
{t.tools.dpsCalculator.title}
{t.tools.dpsCalculator.description}

// 数组访问
{t.faq.questions.map((question, index) => (
  <div key={index}>{question}</div>
))}
```

#### 4. 在 JSX 中使用

```typescript
// 文本内容
<h1>{t.hero.title}</h1>

// 按钮文本
<Button>{t.hero.getFreeCodesCTA}</Button>

// 组合使用
<h2>
  {t.tools.title} <span>{t.tools.titleHighlight}</span>
</h2>

// 动态列表
{[
  {
    title: t.tools.dpsCalculator.title,
    description: t.tools.dpsCalculator.description
  },
  {
    title: t.tools.redeemCodes.title,
    description: t.tools.redeemCodes.description
  }
].map((tool, index) => (
  <div key={index}>
    <h3>{tool.title}</h3>
    <p>{tool.description}</p>
  </div>
))}
```

### 服务器组件 vs 客户端组件

| 组件类型 | Hook/函数 | 是否异步 | 使用场景 |
|---------|----------|---------|---------|
| 客户端组件 | `useTranslations()` | ❌ 否 | 交互页面、动画 |
| 服务器组件 | `getTranslations()` | ✅ 是 | 静态页面、SEO |

#### 什么是异步？

**异步（Asynchronous）** 是指操作不会立即完成，需要等待一段时间才能获得结果。

**同步 vs 异步对比：**

```typescript
// 同步操作：立即返回结果
const result = 1 + 1  // 立即得到 2
console.log(result)   // 立即输出

// 异步操作：需要等待
const data = await fetch('/api/data')  // 需要等待网络请求
console.log(data)  // 等待完成后才输出
```

**JavaScript 中的异步操作：**
- 网络请求（fetch, axios）
- 文件读取（fs.readFile）
- 数据库查询
- 定时器（setTimeout）
- Promise 操作

#### 为什么服务器组件需要异步？

**服务器组件中的 `getTranslations()` 是异步的，因为它需要执行以下操作：**

1. **读取翻译文件**
   ```typescript
   // 在服务器端，需要从文件系统读取 JSON 文件
   const messages = await import(`../locales/${locale}.json`)
   ```
   - 文件读取是 I/O 操作，需要时间
   - 必须等待文件读取完成才能继续

2. **确定当前语言**
   ```typescript
   // 需要从请求上下文中获取语言信息
   const locale = await requestLocale
   ```
   - 需要解析 HTTP 请求
   - 可能需要查询数据库或配置

3. **处理翻译逻辑**
   ```typescript
   // 可能需要进行复杂的翻译处理
   const t = await getTranslations({ locale })
   ```
   - 格式化翻译文本
   - 处理插值和复数形式

**服务器组件示例（攻略页）：**
```typescript
import { getTranslations } from 'next-intl/server'

// 注意：组件函数声明为 async
export default async function GuidesPage() {
  // 使用 await 等待翻译加载完成
  const t = await getTranslations()

  // 只有在翻译加载完成后，才能渲染页面
  return <h1>{t('pages.guides.title')}</h1>
}
```

**执行流程：**
```
1. Next.js 调用 GuidesPage 组件
   ↓
2. 执行 getTranslations()
   ↓
3. 读取 locales/en.json 文件（需要时间）
   ↓
4. 解析 JSON 数据
   ↓
5. 返回翻译函数 t
   ↓
6. 渲染 HTML
   ↓
7. 发送给客户端
```

#### 为什么客户端组件不需要异步？

**客户端组件中的 `useTranslations()` 不是异步的，因为：**

1. **翻译数据已经加载**
   ```typescript
   // 在 [locale]/layout.tsx 中，翻译已经加载并传递给客户端
   export default async function LocaleLayout({ children, params }) {
     const { locale } = await params
     const messages = await getMessages({ locale })  // 在这里异步加载

     return (
       <NextIntlClientProvider messages={messages}>
         {children}  {/* 子组件可以同步访问 messages */}
       </NextIntlClientProvider>
     )
   }
   ```

2. **通过 Context 提供**
   ```typescript
   // NextIntlClientProvider 将翻译数据放入 React Context
   // useTranslations() 只是从 Context 中读取，不需要异步
   ```

3. **内存中访问**
   ```typescript
   // 翻译数据已经在浏览器内存中
   const t = useTranslations()  // 直接从内存读取，无需等待
   ```

**客户端组件示例（首页）：**
```typescript
'use client'

import { useTranslations } from 'next-intl'

// 注意：组件函数不是 async
export default function HomePage() {
  // 不需要 await，立即返回
  const t = useTranslations()

  // 可以立即使用翻译
  return <h1>{t.hero.title}</h1>
}
```

**执行流程：**
```
1. 父组件 LocaleLayout 已经加载翻译数据
   ↓
2. 通过 NextIntlClientProvider 提供给子组件
   ↓
3. HomePage 组件渲染
   ↓
4. useTranslations() 从 Context 读取（同步，立即完成）
   ↓
5. 返回翻译函数 t
   ↓
6. 渲染 UI
```

#### 详细对比

| 特性 | 服务器组件 `getTranslations()` | 客户端组件 `useTranslations()` |
|------|-------------------------------|-------------------------------|
| **是否异步** | ✅ 是（async/await） | ❌ 否（同步） |
| **函数签名** | `async function` | 普通函数 |
| **调用方式** | `await getTranslations()` | `useTranslations()` |
| **数据来源** | 文件系统（需要读取） | React Context（已加载） |
| **执行位置** | 服务器端 | 浏览器端 |
| **执行时机** | 构建时/请求时 | 渲染时 |
| **性能影响** | 可能较慢（I/O 操作） | 快速（内存访问） |

#### 代码对比示例

**服务器组件（异步）：**
```typescript
import { getTranslations } from 'next-intl/server'

// ✅ 必须声明为 async
export default async function ServerPage() {
  // ✅ 必须使用 await
  const t = await getTranslations()

  return (
    <div>
      <h1>{t('title')}</h1>
      {/* 可以直接调用 t() */}
    </div>
  )
}
```

**客户端组件（同步）：**
```typescript
'use client'

import { useTranslations } from 'next-intl'

// ✅ 不能声明为 async（React Hooks 规则）
export default function ClientPage() {
  // ✅ 不需要 await
  const t = useTranslations()

  return (
    <div>
      <h1>{t('title')}</h1>
      {/* 可以直接使用 t */}
    </div>
  )
}
```

#### 常见错误

**❌ 错误 1：在客户端组件中使用 async/await**
```typescript
'use client'

// ❌ 错误：客户端组件不能是 async 函数
export default async function ClientPage() {
  const t = await useTranslations()  // ❌ useTranslations 不是异步的
  return <div>{t('title')}</div>
}

// 错误信息：
// Error: async/await is not yet supported in Client Components
```

**❌ 错误 2：在服务器组件中忘记 await**
```typescript
import { getTranslations } from 'next-intl/server'

export default async function ServerPage() {
  const t = getTranslations()  // ❌ 忘记 await
  return <div>{t('title')}</div>  // ❌ t 是 Promise，不是函数
}

// 错误信息：
// Error: t is not a function
```

**✅ 正确做法：**
```typescript
// 服务器组件
export default async function ServerPage() {
  const t = await getTranslations()  // ✅ 使用 await
  return <div>{t('title')}</div>
}

// 客户端组件
'use client'
export default function ClientPage() {
  const t = useTranslations()  // ✅ 不使用 await
  return <div>{t('title')}</div>
}
```

#### 为什么这样设计？

**服务器组件使用异步的优势：**

1. **灵活的数据加载**
   - 可以从文件系统、数据库、API 等多种来源加载翻译
   - 支持动态翻译和实时更新

2. **更好的 SEO**
   - 翻译在服务器端完成，HTML 中包含完整的翻译文本
   - 搜索引擎可以索引所有语言版本

3. **减少客户端包体积**
   - 只发送当前语言的翻译
   - 不需要在客户端加载所有语言

**客户端组件使用同步的优势：**

1. **符合 React Hooks 规则**
   - Hooks 必须在组件顶层同步调用
   - 不能在条件语句、循环或异步函数中调用

2. **更快的渲染**
   - 翻译数据已经在内存中
   - 无需等待异步操作

3. **更好的用户体验**
   - 语言切换即时响应
   - 无需重新加载页面

#### 实际应用场景

**使用服务器组件（异步）的场景：**
- 静态页面（攻略、文档）
- SEO 重要的页面
- 不需要客户端交互的页面
- 需要从数据库加载翻译的页面

**使用客户端组件（同步）的场景：**
- 需要交互的页面（首页、表单）
- 需要动画效果的页面
- 需要使用浏览器 API 的页面
- 需要实时响应用户操作的页面

#### 总结

| 问题 | 答案 |
|------|------|
| 什么是异步？ | 操作需要等待一段时间才能完成，使用 async/await |
| 为什么服务器组件需要异步？ | 需要从文件系统读取翻译文件，I/O 操作需要时间 |
| 为什么客户端组件不需要异步？ | 翻译数据已经通过 Context 提供，直接从内存读取 |
| 如何选择？ | 需要交互/动画用客户端组件，需要 SEO 用服务器组件 |

---

## 为什么 useTranslations 是 Hook 而 getTranslations 不是？

### 什么是 React Hook？

**React Hook** 是 React 提供的特殊函数，用于在函数组件中"钩入" React 特性。

**Hook 的特征：**
1. 函数名以 `use` 开头（命名约定）
2. 只能在函数组件或自定义 Hook 中调用
3. 必须在组件顶层调用（不能在条件、循环、嵌套函数中）
4. 可以访问 React 内部状态和生命周期

**常见的 React Hooks：**
```typescript
useState()      // 状态管理
useEffect()     // 副作用处理
useContext()    // 访问 Context
useRef()        // 引用存储
useMemo()       // 记忆化计算
useCallback()   // 记忆化函数
```

### useTranslations 为什么是 Hook？

**`useTranslations()` 是一个 React Hook，因为它需要：**

#### 1. 访问 React Context

```typescript
// next-intl 内部实现（简化版）
export function useTranslations() {
  // 使用 useContext 访问翻译数据
  const messages = useContext(IntlContext)

  // 返回翻译函数
  return (key: string) => messages[key]
}
```

**为什么需要 Context？**
- 翻译数据需要在组件树中共享
- 避免通过 props 层层传递
- 支持语言切换时自动更新所有组件

#### 2. 响应状态变化

```typescript
// 当用户切换语言时
<LanguageSwitcher onChange={(locale) => {
  // 更新 Context 中的语言
  setLocale(locale)

  // 所有使用 useTranslations() 的组件自动重新渲染
  // 显示新语言的文本
}} />
```

**Hook 的优势：**
- 自动订阅 Context 变化
- 语言切换时自动重新渲染
- 无需手动管理订阅

#### 3. 遵循 React 规则

```typescript
'use client'

export default function HomePage() {
  // ✅ 在组件顶层调用 Hook
  const t = useTranslations()

  // ✅ 可以在渲染中使用
  return <h1>{t('title')}</h1>
}
```

**Hook 规则：**
- 必须在函数组件中调用
- 必须在顶层调用（不能在条件语句中）
- 可以访问组件的渲染上下文

#### 4. 完整的内部实现示例

```typescript
// next-intl 的简化实现
import { useContext } from 'react'

// 1. 创建 Context
const IntlContext = createContext<{
  locale: string
  messages: Record<string, any>
}>({
  locale: 'en',
  messages: {}
})

// 2. Provider 组件
export function NextIntlClientProvider({ locale, messages, children }) {
  return (
    <IntlContext.Provider value={{ locale, messages }}>
      {children}
    </IntlContext.Provider>
  )
}

// 3. useTranslations Hook
export function useTranslations() {
  // 使用 useContext Hook 访问翻译数据
  const { messages } = useContext(IntlContext)

  // 返回翻译函数
  return (key: string) => {
    const keys = key.split('.')
    let value = messages

    for (const k of keys) {
      value = value[k]
    }

    return value
  }
}
```

### getTranslations 为什么不是 Hook？

**`getTranslations()` 不是 Hook，因为它：**

#### 1. 在服务器端运行

```typescript
// 服务器组件中
export default async function ServerPage() {
  // 在服务器端调用，不在 React 组件渲染过程中
  const t = await getTranslations()

  return <h1>{t('title')}</h1>
}
```

**服务器端特点：**
- 没有 React Context（Context 是客户端概念）
- 没有组件状态
- 没有重新渲染
- 每次请求都是全新的执行

#### 2. 不需要访问 React 状态

```typescript
// next-intl 服务器端实现（简化版）
export async function getTranslations() {
  // 直接从文件系统读取
  const locale = await getLocale()
  const messages = await import(`../locales/${locale}.json`)

  // 返回翻译函数
  return (key: string) => messages[key]
}
```

**不需要 Hook 的原因：**
- 直接读取文件，不需要 Context
- 不需要响应状态变化
- 不需要订阅更新

#### 3. 是普通的异步函数

```typescript
// getTranslations 就是一个普通的 async 函数
async function getTranslations() {
  // 执行异步操作
  const data = await loadData()
  return data
}

// 不是 Hook，不需要遵循 Hook 规则
// 可以在任何地方调用（只要在 async 函数中）
```

#### 4. 执行时机不同

```typescript
// 服务器组件：构建时/请求时执行
export default async function ServerPage() {
  // 这段代码在服务器上执行一次
  const t = await getTranslations()

  // 生成 HTML 发送给客户端
  return <h1>{t('title')}</h1>
}

// 客户端组件：每次渲染时执行
'use client'
export default function ClientPage() {
  // 这段代码在浏览器中每次渲染时执行
  const t = useTranslations()

  // 可能会多次渲染（状态变化、props 变化等）
  return <h1>{t('title')}</h1>
}
```

### 详细对比

| 特性 | `useTranslations()` (Hook) | `getTranslations()` (函数) |
|------|---------------------------|---------------------------|
| **类型** | React Hook | 普通异步函数 |
| **命名** | 以 `use` 开头 | 以 `get` 开头 |
| **运行环境** | 客户端（浏览器） | 服务器端 |
| **是否异步** | ❌ 否（同步） | ✅ 是（async/await） |
| **数据来源** | React Context | 文件系统/数据库 |
| **调用位置** | 组件顶层 | async 函数中任何位置 |
| **调用限制** | 必须遵循 Hook 规则 | 无特殊限制 |
| **状态订阅** | ✅ 自动订阅 Context | ❌ 不需要订阅 |
| **重新渲染** | ✅ 响应状态变化 | ❌ 每次请求重新执行 |
| **使用场景** | 需要交互的客户端组件 | 静态的服务器组件 |

### 为什么需要两个不同的 API？

#### 客户端需要 Hook 的原因

```typescript
'use client'

export default function LanguageSwitcher() {
  const [locale, setLocale] = useState('en')
  const t = useTranslations()  // Hook，自动响应语言变化

  return (
    <div>
      <h1>{t('title')}</h1>  {/* 语言切换时自动更新 */}

      <button onClick={() => setLocale('zh')}>
        切换到中文
      </button>
    </div>
  )
}
```

**Hook 的优势：**
1. 自动响应语言切换
2. 无需手动重新加载翻译
3. 所有组件同步更新
4. 更好的用户体验

#### 服务器端不能使用 Hook 的原因

```typescript
// ❌ 错误：服务器组件不能使用 Hook
export default async function ServerPage() {
  const t = useTranslations()  // ❌ 错误！服务器端没有 React Context
  return <h1>{t('title')}</h1>
}

// ✅ 正确：使用异步函数
export default async function ServerPage() {
  const t = await getTranslations()  // ✅ 正确！直接读取文件
  return <h1>{t('title')}</h1>
}
```

**服务器端的限制：**
1. 没有 React Context
2. 没有组件状态
3. 没有重新渲染机制
4. 每次请求都是独立的

### 实际应用示例

#### 示例 1：客户端交互页面

```typescript
'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'

export default function ContactForm() {
  const t = useTranslations()  // Hook，访问 Context
  const [name, setName] = useState('')

  return (
    <form>
      <label>{t('form.name')}</label>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder={t('form.namePlaceholder')}
      />
      <button>{t('form.submit')}</button>
    </form>
  )
}
```

**为什么用 Hook？**
- 需要表单交互（useState）
- 需要事件处理器（onChange）
- 需要动态更新 UI
- 翻译文本需要响应语言切换

#### 示例 2：服务器端静态页面

```typescript
import { getTranslations } from 'next-intl/server'

export default async function AboutPage() {
  const t = await getTranslations()  // 异步函数，读取文件

  return (
    <div>
      <h1>{t('about.title')}</h1>
      <p>{t('about.description')}</p>

      {/* 静态内容，不需要交互 */}
      <ul>
        <li>{t('about.feature1')}</li>
        <li>{t('about.feature2')}</li>
        <li>{t('about.feature3')}</li>
      </ul>
    </div>
  )
}
```

**为什么用异步函数？**
- 纯静态内容，无交互
- 需要 SEO 优化
- 在服务器端渲染
- 不需要响应状态变化

### 常见错误和解决方案

#### 错误 1：在服务器组件中使用 Hook

```typescript
// ❌ 错误
export default async function ServerPage() {
  const t = useTranslations()  // 错误：服务器组件不能使用 Hook
  return <h1>{t('title')}</h1>
}

// ✅ 解决方案 1：使用 getTranslations
export default async function ServerPage() {
  const t = await getTranslations()
  return <h1>{t('title')}</h1>
}

// ✅ 解决方案 2：改为客户端组件
'use client'
export default function ClientPage() {
  const t = useTranslations()
  return <h1>{t('title')}</h1>
}
```

#### 错误 2：在客户端组件中使用 getTranslations

```typescript
'use client'

// ❌ 错误
export default async function ClientPage() {
  const t = await getTranslations()  // 错误：客户端组件不能是 async
  return <h1>{t('title')}</h1>
}

// ✅ 解决方案：使用 useTranslations
'use client'
export default function ClientPage() {
  const t = useTranslations()
  return <h1>{t('title')}</h1>
}
```

#### 错误 3：在条件语句中使用 Hook

```typescript
'use client'

// ❌ 错误
export default function ConditionalPage({ showTitle }) {
  if (showTitle) {
    const t = useTranslations()  // 错误：Hook 不能在条件语句中
    return <h1>{t('title')}</h1>
  }
  return null
}

// ✅ 解决方案：在顶层调用 Hook
'use client'
export default function ConditionalPage({ showTitle }) {
  const t = useTranslations()  // 在顶层调用

  if (showTitle) {
    return <h1>{t('title')}</h1>
  }
  return null
}
```

### 总结

| 问题 | 答案 |
|------|------|
| 什么是 Hook？ | 以 `use` 开头的特殊函数，用于访问 React 特性 |
| useTranslations 为什么是 Hook？ | 需要访问 React Context，响应状态变化 |
| getTranslations 为什么不是 Hook？ | 在服务器端运行，直接读取文件，不需要 React 特性 |
| 如何选择？ | 客户端组件用 Hook，服务器组件用异步函数 |
| 能混用吗？ | ❌ 不能，必须根据组件类型选择对应的 API |

**核心原则：**
- **客户端组件** = `useTranslations()` (Hook) = 访问 Context = 响应变化
- **服务器组件** = `getTranslations()` (函数) = 读取文件 = 静态渲染

---

## 完整实现流程

### 1. 组件初始化

```typescript
export default function HomePage() {
  // 步骤 1: 创建 ref 存储 observer
  const observerRef = useRef<IntersectionObserver | null>(null)

  // 步骤 2: 获取翻译函数
  const t = useTranslations()

  // 步骤 3: 设置副作用
  useEffect(() => {
    // ... 观察器设置
  }, [])

  // 步骤 4: 渲染 UI
  return (
    // ... JSX
  )
}
```

### 2. 滚动动画设置

```typescript
useEffect(() => {
  // 步骤 1: 创建观察器
  observerRef.current = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible')
        }
      })
    },
    { threshold: 0.1 }
  )

  // 步骤 2: 查找目标元素
  const elements = document.querySelectorAll('.scroll-reveal')

  // 步骤 3: 开始观察
  elements.forEach((el) => observerRef.current?.observe(el))

  // 步骤 4: 返回清理函数
  return () => observerRef.current?.disconnect()
}, [])
```

### 3. CSS 动画配置

```css
/* globals.css */

/* 初始状态：隐藏 */
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s ease-out;
}

/* 可见状态：显示 */
.scroll-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### 4. HTML 标记

```typescript
// 需要动画的元素添加 .scroll-reveal 类
<div className="scroll-reveal">
  <h1>{t.hero.title}</h1>
</div>

<div className="scroll-reveal">
  <p>{t.hero.description}</p>
</div>
```

### 5. 完整执行流程

```
1. 组件挂载
   ↓
2. 创建 observerRef (useRef)
   ↓
3. 获取翻译函数 (useTranslations)
   ↓
4. 渲染初始 UI（所有 .scroll-reveal 元素不可见）
   ↓
5. 执行 useEffect
   ↓
6. 创建 IntersectionObserver
   ↓
7. 查找所有 .scroll-reveal 元素
   ↓
8. 开始观察这些元素
   ↓
9. 用户滚动页面
   ↓
10. 元素进入视口（10% 可见）
    ↓
11. 触发 observer 回调
    ↓
12. 添加 'visible' 类
    ↓
13. CSS 过渡动画生效
    ↓
14. 元素淡入并上移
    ↓
15. 用户切换语言
    ↓
16. 组件重新渲染
    ↓
17. useTranslations 返回新语言的文本
    ↓
18. UI 更新为新语言
    ↓
19. 用户离开页面
    ↓
20. 组件卸载
    ↓
21. 执行清理函数
    ↓
22. 断开 observer 连接
```

---

## 性能优化

### 1. 使用 useRef 避免重复创建

```typescript
// ✅ 正确：使用 useRef
const observerRef = useRef<IntersectionObserver | null>(null)

useEffect(() => {
  observerRef.current = new IntersectionObserver(...)
}, [])

// ❌ 错误：每次渲染都创建新实例
useEffect(() => {
  const observer = new IntersectionObserver(...)
})  // 没有依赖数组！
```

### 2. 空依赖数组

```typescript
// ✅ 正确：只执行一次
useEffect(() => {
  // 设置代码
  return () => {
    // 清理代码
  }
}, [])  // 空数组

// ❌ 错误：每次渲染都执行
useEffect(() => {
  // 设置代码
})  // 没有依赖数组
```

### 3. 清理函数

```typescript
// ✅ 正确：清理资源
useEffect(() => {
  const observer = new IntersectionObserver(...)

  return () => {
    observer.disconnect()  // 清理
  }
}, [])

// ❌ 错误：没有清理
useEffect(() => {
  const observer = new IntersectionObserver(...)
  // 没有返回清理函数！
}, [])
```

### 4. 可选链操作符

```typescript
// ✅ 正确：防止 null 错误
observerRef.current?.observe(el)
observerRef.current?.disconnect()

// ❌ 错误：可能抛出错误
observerRef.current.observe(el)  // 如果为 null 会报错
```

### 5. 批量操作

```typescript
// ✅ 正确：一次性查找所有元素
const elements = document.querySelectorAll('.scroll-reveal')
elements.forEach((el) => observer.observe(el))

// ❌ 错误：多次查询 DOM
document.querySelectorAll('.scroll-reveal')[0]
document.querySelectorAll('.scroll-reveal')[1]
// ...
```

---

## 常见问题

### Q1: 为什么动画只触发一次？

**A:** 当前实现中，元素进入视口后添加 `visible` 类，但不会移除。如果需要重复动画：

```typescript
observerRef.current = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
      } else {
        entry.target.classList.remove('visible')  // 离开视口时移除
      }
    })
  },
  { threshold: 0.1 }
)
```

### Q2: 如何调整动画触发时机？

**A:** 修改 `threshold` 值：

```typescript
{ threshold: 0.1 }   // 10% 可见时触发（当前）
{ threshold: 0.5 }   // 50% 可见时触发
{ threshold: 1.0 }   // 100% 可见时触发
```

### Q3: 为什么使用 `as any` 类型断言？

**A:** 这是临时解决方案，避免 TypeScript 类型错误。更好的做法是定义类型：

```typescript
// 定义翻译类型
interface Translations {
  hero: {
    title: string
    description: string
    // ...
  }
  // ...
}

// 使用类型
const t = useTranslations() as Translations
```

### Q4: useEffect 的清理函数何时执行？

**A:** 清理函数在以下情况执行：
1. 组件卸载时
2. 依赖项变化，重新执行 effect 之前
3. 本例中只在卸载时执行（因为依赖数组为空）

### Q5: 可以在 useEffect 中使用 async/await 吗？

**A:** 不能直接使用，但可以这样：

```typescript
// ❌ 错误
useEffect(async () => {
  await fetchData()
}, [])

// ✅ 正确
useEffect(() => {
  const fetchData = async () => {
    const data = await fetch(...)
  }
  fetchData()
}, [])
```

### Q6: 如何调试 IntersectionObserver？

**A:** 添加日志：

```typescript
observerRef.current = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      console.log('Element:', entry.target)
      console.log('Is intersecting:', entry.isIntersecting)
      console.log('Intersection ratio:', entry.intersectionRatio)

      if (entry.isIntersecting) {
        entry.target.classList.add('visible')
      }
    })
  },
  { threshold: 0.1 }
)
```

### Q7: 为什么不用 useState 存储 observer？

**A:** 因为：
1. observer 变化不需要触发重新渲染
2. useState 会导致不必要的性能开销
3. useRef 更适合存储实例引用

### Q8: 如何支持多个动画效果？

**A:** 使用不同的类名：

```typescript
// HTML
<div className="scroll-reveal-fade">淡入</div>
<div className="scroll-reveal-slide">滑入</div>

// CSS
.scroll-reveal-fade.visible {
  opacity: 1;
}

.scroll-reveal-slide.visible {
  transform: translateX(0);
}

// JavaScript
const fadeElements = document.querySelectorAll('.scroll-reveal-fade')
const slideElements = document.querySelectorAll('.scroll-reveal-slide')

fadeElements.forEach((el) => observer.observe(el))
slideElements.forEach((el) => observer.observe(el))
```

---

## 总结

首页使用的三个 Hooks 各司其职：

1. **useRef**
   - 存储 IntersectionObserver 实例
   - 避免重复创建
   - 不触发重新渲染

2. **useEffect**
   - 设置滚动动画观察器
   - 只在挂载时执行一次
   - 卸载时清理资源

3. **useTranslations**
   - 提供多语言支持
   - 自动响应语言切换
   - 类型安全的翻译访问

这三个 Hooks 的组合创建了一个高性能、可维护、国际化的营销页面。

## 参考资料

- [React Hooks 官方文档](https://react.dev/reference/react)
- [IntersectionObserver API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)
- [next-intl 文档](https://next-intl-docs.vercel.app/)
