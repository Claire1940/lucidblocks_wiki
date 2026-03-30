# .ts 和 .tsx 文件后缀区别详解

## 一、核心区别

### 1.1 简单总结

| 特性 | .ts | .tsx |
|------|-----|------|
| **全称** | TypeScript | TypeScript + JSX |
| **用途** | 纯 TypeScript 代码 | TypeScript + React 组件 |
| **JSX 语法** | ❌ 不支持 | ✅ 支持 |
| **React 组件** | ❌ 不能写 | ✅ 可以写 |
| **适用场景** | 工具函数、类型定义、配置 | React 组件、页面 |

### 1.2 一句话总结

- **.ts**：纯 TypeScript 文件，**不能**包含 JSX/React 代码
- **.tsx**：TypeScript + JSX 文件，**可以**包含 React 组件

---

## 二、详细对比

### 2.1 .ts 文件（TypeScript）

#### **特点**
- 只能写纯 TypeScript 代码
- 不支持 JSX 语法
- 不能直接返回 React 元素

#### **适用场景**
1. **工具函数**
2. **类型定义**
3. **配置文件**
4. **API 客户端**
5. **数据处理逻辑**
6. **常量定义**

#### **示例代码**

```typescript
// ✅ src/lib/utils.ts - 工具函数
export function formatDate(date: Date): string {
  return date.toLocaleDateString('zh-CN')
}

export function calculateDamage(base: number, multiplier: number): number {
  return base * multiplier
}
```

```typescript
// ✅ src/types/user.ts - 类型定义
export interface User {
  id: string
  name: string
  email: string
}

export type UserRole = 'admin' | 'user' | 'guest'
```

```typescript
// ✅ src/lib/api.ts - API 客户端
export async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`)
  return response.json()
}
```

```typescript
// ✅ src/config/constants.ts - 常量定义
export const API_BASE_URL = 'https://api.example.com'
export const MAX_RETRY_COUNT = 3
export const TIMEOUT_MS = 5000
```

#### **❌ 不能做的事情**

```typescript
// ❌ 错误：.ts 文件不能包含 JSX
export function MyComponent() {
  return <div>Hello</div>  // 语法错误！
}

// ❌ 错误：不能返回 React 元素
export function getButton() {
  return <button>Click</button>  // 语法错误！
}
```

**错误信息**：
```
Cannot use JSX unless the '--jsx' flag is provided.
```

---

### 2.2 .tsx 文件（TypeScript + JSX）

#### **特点**
- 支持 TypeScript 和 JSX 语法
- 可以写 React 组件
- 可以返回 React 元素

#### **适用场景**
1. **React 组件**
2. **页面组件**
3. **布局组件**
4. **包含 JSX 的工具函数**

#### **示例代码**

```tsx
// ✅ src/components/Button.tsx - React 组件
interface ButtonProps {
  label: string
  onClick: () => void
}

export function Button({ label, onClick }: ButtonProps) {
  return <button onClick={onClick}>{label}</button>
}
```

```tsx
// ✅ src/app/page.tsx - 页面组件
export default function HomePage() {
  return (
    <div>
      <h1>欢迎</h1>
      <p>这是主页</p>
    </div>
  )
}
```

```tsx
// ✅ src/components/Layout.tsx - 布局组件
interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="container">
      <header>Header</header>
      <main>{children}</main>
      <footer>Footer</footer>
    </div>
  )
}
```

```tsx
// ✅ src/lib/renderUtils.tsx - 包含 JSX 的工具函数
export function renderErrorMessage(error: string) {
  return <div className="error">{error}</div>
}

export function renderLoadingSpinner() {
  return <div className="spinner">Loading...</div>
}
```

#### **✅ 也可以写纯 TypeScript 代码**

```tsx
// ✅ .tsx 文件也可以包含纯 TypeScript 代码
export function calculateTotal(items: number[]): number {
  return items.reduce((sum, item) => sum + item, 0)
}

export interface Product {
  id: string
  name: string
  price: number
}
```

**重要**：`.tsx` 文件可以包含纯 TypeScript 代码，但 `.ts` 文件不能包含 JSX。

---

## 三、在本项目中的应用

### 3.1 .ts 文件示例

#### **src/lib/content.ts**
```typescript
// 纯工具函数，不涉及 React
export async function getAllContentSlugs(
  contentType: ContentType,
  language: Language
): Promise<string[]> {
  const contentDir = path.join(process.cwd(), 'content', language, contentType)

  if (!fs.existsSync(contentDir)) {
    return []
  }

  const files = fs.readdirSync(contentDir).filter(f => f.endsWith('.mdx'))
  return files.map(file => file.replace('.mdx', ''))
}
```

**为什么用 .ts？**
- 只有数据处理逻辑
- 不需要渲染 UI
- 不包含 JSX

#### **src/i18n/config.ts**
```typescript
// 配置文件，纯数据定义
export const locales = ['en', 'zh'] as const
export type Locale = (typeof locales)[number]

export const defaultLocale: Locale = 'en'

export const localeNames: Record<Locale, string> = {
  en: 'English',
  zh: '中文',
}
```

**为什么用 .ts？**
- 只定义常量和类型
- 不涉及 React 组件

#### **src/lib/utils.ts**
```typescript
// 工具函数，不涉及 UI
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**为什么用 .ts？**
- 纯函数，处理字符串
- 不返回 React 元素

---

### 3.2 .tsx 文件示例

#### **src/components/ui/button.tsx**
```tsx
// React 组件，包含 JSX
import * as React from "react"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)

export { Button }
```

**为什么用 .tsx？**
- 定义 React 组件
- 返回 JSX 元素

#### **src/app/[locale]/page.tsx**
```tsx
// 页面组件，包含 JSX
import { useTranslations } from 'next-intl'

export default function HomePage() {
  const t = useTranslations()

  return (
    <div>
      <h1>{t('hero.title')}</h1>
      <p>{t('hero.description')}</p>
    </div>
  )
}
```

**为什么用 .tsx？**
- Next.js 页面组件
- 返回 JSX

#### **src/components/Navigation.tsx**
```tsx
// 导航组件，包含 JSX
export function Navigation() {
  return (
    <nav className="flex items-center gap-4">
      <a href="/">Home</a>
      <a href="/guides">Guides</a>
      <a href="/tools">Tools</a>
    </nav>
  )
}
```

**为什么用 .tsx？**
- React 组件
- 包含 JSX 结构

---

## 四、如何选择？

### 4.1 决策流程图

```
开始
  ↓
是否需要写 React 组件？
  ↓
  是 → 使用 .tsx
  ↓
  否 → 是否需要返回 JSX？
        ↓
        是 → 使用 .tsx
        ↓
        否 → 使用 .ts
```

### 4.2 快速判断规则

#### **使用 .tsx 的情况**
- ✅ 文件包含 `<div>`、`<button>` 等 JSX 标签
- ✅ 文件定义 React 组件（函数组件或类组件）
- ✅ 文件返回 `React.ReactNode` 或 `JSX.Element`
- ✅ 文件使用 React Hooks（`useState`、`useEffect` 等）
- ✅ Next.js 页面文件（`page.tsx`、`layout.tsx`）

#### **使用 .ts 的情况**
- ✅ 纯工具函数（数据处理、计算、格式化）
- ✅ 类型定义（`interface`、`type`、`enum`）
- ✅ 配置文件（常量、设置）
- ✅ API 客户端（fetch、axios 封装）
- ✅ 数据模型（class、数据结构）
- ✅ 中间件（Next.js middleware）

---

## 五、常见误区

### 5.1 误区 1：所有 TypeScript 文件都用 .tsx

**❌ 错误做法**：
```tsx
// src/lib/utils.tsx - 不需要 JSX，但用了 .tsx
export function add(a: number, b: number): number {
  return a + b
}
```

**✅ 正确做法**：
```typescript
// src/lib/utils.ts - 纯函数，使用 .ts
export function add(a: number, b: number): number {
  return a + b
}
```

**原因**：
- `.tsx` 文件编译时会启用 JSX 转换
- 增加不必要的编译开销
- 语义不清晰

---

### 5.2 误区 2：React 项目中所有文件都用 .tsx

**❌ 错误做法**：
```
src/
├── components/
│   ├── Button.tsx          ✅ 正确（React 组件）
│   └── utils.tsx           ❌ 错误（纯函数）
├── lib/
│   ├── api.tsx             ❌ 错误（API 客户端）
│   └── constants.tsx       ❌ 错误（常量定义）
└── types/
    └── user.tsx            ❌ 错误（类型定义）
```

**✅ 正确做法**：
```
src/
├── components/
│   ├── Button.tsx          ✅ React 组件
│   └── utils.ts            ✅ 纯函数
├── lib/
│   ├── api.ts              ✅ API 客户端
│   └── constants.ts        ✅ 常量定义
└── types/
    └── user.ts             ✅ 类型定义
```

---

### 5.3 误区 3：.tsx 文件不能包含纯 TypeScript 代码

**✅ 实际上可以**：
```tsx
// src/components/Button.tsx
// 可以同时包含 React 组件和纯函数

// 纯函数
export function calculateButtonWidth(text: string): number {
  return text.length * 10
}

// React 组件
export function Button({ label }: { label: string }) {
  const width = calculateButtonWidth(label)
  return <button style={{ width }}>{label}</button>
}
```

**但建议分离**：
```typescript
// src/lib/buttonUtils.ts - 纯函数
export function calculateButtonWidth(text: string): number {
  return text.length * 10
}
```

```tsx
// src/components/Button.tsx - React 组件
import { calculateButtonWidth } from '@/lib/buttonUtils'

export function Button({ label }: { label: string }) {
  const width = calculateButtonWidth(label)
  return <button style={{ width }}>{label}</button>
}
```

**原因**：
- 更好的关注点分离
- 纯函数更容易测试
- 提高代码复用性

---

## 六、编译器行为差异

### 6.1 TypeScript 编译器配置

在 `tsconfig.json` 中：

```json
{
  "compilerOptions": {
    "jsx": "preserve",  // 或 "react-jsx"、"react"
    // ...
  }
}
```

**jsx 选项说明**：
- `"preserve"`：保留 JSX，由其他工具处理（如 Babel、Next.js）
- `"react"`：转换为 `React.createElement()`
- `"react-jsx"`：转换为新的 JSX 转换（React 17+）

### 6.2 编译过程

#### **.ts 文件编译**
```typescript
// 输入：src/lib/utils.ts
export function add(a: number, b: number): number {
  return a + b
}

// 输出：dist/lib/utils.js
export function add(a, b) {
  return a + b
}
```

**过程**：
1. 移除类型注解
2. 转换为 JavaScript
3. 不涉及 JSX 转换

#### **.tsx 文件编译**
```tsx
// 输入：src/components/Button.tsx
export function Button({ label }: { label: string }) {
  return <button>{label}</button>
}

// 输出：dist/components/Button.js (jsx: "react")
import React from 'react'
export function Button({ label }) {
  return React.createElement('button', null, label)
}

// 或输出 (jsx: "react-jsx")
import { jsx as _jsx } from 'react/jsx-runtime'
export function Button({ label }) {
  return _jsx('button', { children: label })
}
```

**过程**：
1. 移除类型注解
2. 转换 JSX 为函数调用
3. 生成 JavaScript

---

## 七、性能影响

### 7.1 编译性能

| 文件类型 | 编译步骤 | 性能 |
|---------|---------|------|
| .ts | 类型检查 + 转译 | 快 ⚡ |
| .tsx | 类型检查 + JSX 转换 + 转译 | 稍慢 🐢 |

**建议**：
- 不需要 JSX 的文件使用 `.ts`
- 减少不必要的 JSX 转换开销

### 7.2 包大小

```tsx
// ❌ 不必要的 .tsx
// src/lib/constants.tsx
export const API_URL = 'https://api.example.com'
```

```typescript
// ✅ 使用 .ts
// src/lib/constants.ts
export const API_URL = 'https://api.example.com'
```

**影响**：
- `.tsx` 文件可能引入额外的 JSX 运行时代码
- 虽然影响很小，但积少成多

---

## 八、IDE 支持差异

### 8.1 语法高亮

- **.ts**：TypeScript 语法高亮
- **.tsx**：TypeScript + JSX 语法高亮

### 8.2 自动补全

#### **.ts 文件**
```typescript
// 只提示 TypeScript API
const str = "hello"
str.  // 提示：toUpperCase, toLowerCase, split, ...
```

#### **.tsx 文件**
```tsx
// 提示 TypeScript + React API
<div   // 提示：className, style, onClick, ...
```

### 8.3 错误提示

#### **.ts 文件**
```typescript
// ❌ 立即报错
const element = <div>Hello</div>
// Error: Cannot use JSX unless the '--jsx' flag is provided.
```

#### **.tsx 文件**
```tsx
// ✅ 正常工作
const element = <div>Hello</div>
```

---

## 九、最佳实践

### 9.1 文件命名规范

```
✅ 推荐的文件结构
src/
├── components/
│   ├── Button.tsx           # React 组件
│   ├── Card.tsx             # React 组件
│   └── Layout.tsx           # React 组件
├── lib/
│   ├── utils.ts             # 工具函数
│   ├── api.ts               # API 客户端
│   └── validation.ts        # 验证逻辑
├── types/
│   ├── user.ts              # 类型定义
│   └── product.ts           # 类型定义
├── hooks/
│   └── useAuth.ts           # 自定义 Hook（不返回 JSX）
└── config/
    └── constants.ts         # 配置常量
```

### 9.2 何时可以混用

```tsx
// ✅ 可以接受：组件文件中包含辅助函数
// src/components/UserCard.tsx

// 辅助函数（纯 TypeScript）
function formatUserName(firstName: string, lastName: string): string {
  return `${firstName} ${lastName}`
}

// React 组件（JSX）
export function UserCard({ user }: { user: User }) {
  const fullName = formatUserName(user.firstName, user.lastName)
  return <div>{fullName}</div>
}
```

**原则**：
- 如果辅助函数只在这个组件中使用 → 可以放在同一文件
- 如果辅助函数会被多个组件使用 → 应该提取到 `.ts` 文件

### 9.3 重构建议

**场景**：一个 `.tsx` 文件变得很大

```tsx
// ❌ 不好：所有代码都在一个 .tsx 文件
// src/components/Dashboard.tsx (500 行)

// 数据处理函数
function processData(data: any[]) { ... }
function filterData(data: any[]) { ... }
function sortData(data: any[]) { ... }

// 类型定义
interface DashboardData { ... }
interface ChartConfig { ... }

// React 组件
export function Dashboard() {
  // 200 行组件代码
}
```

**✅ 重构后**：

```typescript
// src/lib/dashboardUtils.ts - 数据处理
export function processData(data: any[]) { ... }
export function filterData(data: any[]) { ... }
export function sortData(data: any[]) { ... }
```

```typescript
// src/types/dashboard.ts - 类型定义
export interface DashboardData { ... }
export interface ChartConfig { ... }
```

```tsx
// src/components/Dashboard.tsx - React 组件
import { processData, filterData, sortData } from '@/lib/dashboardUtils'
import type { DashboardData, ChartConfig } from '@/types/dashboard'

export function Dashboard() {
  // 只包含组件逻辑
}
```

---

## 十、总结

### 10.1 核心原则

> **如果文件包含 JSX，使用 .tsx；否则使用 .ts**

### 10.2 快速检查清单

**使用 .tsx 的信号**：
- [ ] 文件中有 `<` 和 `>` 标签
- [ ] 定义了 React 组件
- [ ] 返回 `JSX.Element`
- [ ] 使用了 React Hooks

**使用 .ts 的信号**：
- [ ] 只有函数和类型定义
- [ ] 不涉及 UI 渲染
- [ ] 纯数据处理逻辑
- [ ] 配置和常量

### 10.3 记忆口诀

```
有 JSX 用 .tsx
无 JSX 用 .ts
不确定？看代码里有没有 <标签>
```

---

## 十一、实战练习

### 练习 1：判断文件类型

```typescript
// 文件 A
export function calculateTotal(items: number[]): number {
  return items.reduce((sum, item) => sum + item, 0)
}
```
**答案**：`.ts`（纯函数，无 JSX）

---

```typescript
// 文件 B
export function ErrorMessage({ message }: { message: string }) {
  return <div className="error">{message}</div>
}
```
**答案**：`.tsx`（包含 JSX）

---

```typescript
// 文件 C
export interface User {
  id: string
  name: string
}

export type UserRole = 'admin' | 'user'
```
**答案**：`.ts`（只有类型定义）

---

```typescript
// 文件 D
import { useState } from 'react'

export function useCounter() {
  const [count, setCount] = useState(0)
  return { count, increment: () => setCount(count + 1) }
}
```
**答案**：`.ts`（自定义 Hook，不返回 JSX）

---

```typescript
// 文件 E
export const API_CONFIG = {
  baseURL: 'https://api.example.com',
  timeout: 5000,
}
```
**答案**：`.ts`（配置对象）

---

## 十二、相关资源

- **TypeScript 官方文档**：https://www.typescriptlang.org/docs/handbook/jsx.html
- **React TypeScript Cheatsheet**：https://react-typescript-cheatsheet.netlify.app/
- **Next.js TypeScript**：https://nextjs.org/docs/app/building-your-application/configuring/typescript
