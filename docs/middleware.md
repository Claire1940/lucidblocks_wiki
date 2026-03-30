# middleware.ts 中间件文件介绍

## 一、应用场景

`src/middleware.ts` 是 Next.js 的**中间件文件**，在请求到达页面之前执行。在本项目中的作用：

1. **自动语言检测**：根据浏览器语言自动选择合适的语言版本
2. **URL 重定向**：将 `/guides` 自动重定向到 `/en/guides` 或 `/zh/guides`
3. **语言前缀管理**：确保所有 URL 都包含语言前缀
4. **路由拦截**：在请求到达页面组件之前处理国际化逻辑
5. **用户体验优化**：无需手动选择语言，自动跳转到合适的版本

---

## 二、基础知识

### 2.1 Next.js Middleware（中间件）

#### **什么是 Middleware？**
Middleware 是在请求完成之前运行的代码，可以：
- 修改请求和响应
- 重定向到不同的 URL
- 修改请求头和响应头
- 直接返回响应

#### **执行时机**
```
用户请求
  ↓
【Middleware 执行】← 在这里！
  ↓
路由匹配
  ↓
页面组件渲染
  ↓
返回响应
```

#### **Middleware 特点**
- 在服务端运行（Edge Runtime）
- 在所有路由之前执行
- 可以访问请求对象（cookies、headers、URL）
- 不能访问 Node.js API（如 `fs`、`path`）

### 2.2 next-intl Middleware

#### **createMiddleware()**
next-intl 提供的中间件工厂函数，用于：
- 自动检测用户语言偏好
- 重定向到正确的语言版本
- 管理语言前缀

#### **工作流程**
```
1. 用户访问 /guides
2. Middleware 检测浏览器语言
3. 浏览器语言是中文 → 重定向到 /zh/guides
4. 浏览器语言是英文 → 重定向到 /en/guides
5. 浏览器语言是其他 → 重定向到 /en/guides（默认）
```

### 2.3 Middleware Matcher（匹配器）

#### **作用**
定义 middleware 应该在哪些路径上执行。

#### **语法**
```typescript
export const config = {
  matcher: ['/about', '/dashboard/:path*']
}
```

#### **匹配模式**
- `/about`：精确匹配
- `/dashboard/:path*`：匹配 `/dashboard` 及其所有子路径
- `/((?!api).*)` ：正则表达式，排除 `/api` 路径

---

## 三、代码实现和作用

### 3.1 导入依赖 (第 1-2 行)

```typescript
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n/config'
```

**各依赖作用**：

#### **createMiddleware**
- next-intl 提供的中间件工厂函数
- 接收配置对象，返回 middleware 函数
- 处理所有国际化相关的路由逻辑

#### **locales 和 defaultLocale**
从 `src/i18n/config.ts` 导入：
```typescript
// src/i18n/config.ts
export const locales = ['en', 'zh'] as const
export const defaultLocale: Locale = 'en'
```

---

### 3.2 创建 Middleware (第 4-16 行)

```typescript
export default createMiddleware({
	// 支持的语言列表
	locales,

	// 默认语言
	defaultLocale,

	// 语言检测策略
	localeDetection: true,

	// 语言前缀策略：always = 总是显示语言前缀
	localePrefix: 'always'
})
```

#### **3.2.1 locales 配置 (第 6 行)**

```typescript
locales,  // ['en', 'zh']
```

**作用**：
- 定义应用支持的所有语言
- 用于验证 URL 中的语言参数
- 用于语言检测和重定向

**示例**：
```
支持的 URL：
✅ /en/guides
✅ /zh/guides

不支持的 URL：
❌ /fr/guides  → 重定向到 /en/guides
❌ /ja/guides  → 重定向到 /en/guides
```

---

#### **3.2.2 defaultLocale 配置 (第 9 行)**

```typescript
defaultLocale,  // 'en'
```

**作用**：
- 当无法检测用户语言时使用的后备语言
- 当用户访问不带语言前缀的 URL 时的默认语言

**使用场景**：
```
场景 1：用户访问根路径
用户访问: /
→ 重定向到: /en

场景 2：浏览器语言不支持
浏览器语言: fr-FR（法语）
用户访问: /guides
→ 重定向到: /en/guides

场景 3：无法检测浏览器语言
用户访问: /about
→ 重定向到: /en/about
```

---

#### **3.2.3 localeDetection 配置 (第 12 行)**

```typescript
localeDetection: true,
```

**作用**：
- 启用自动语言检测
- 根据浏览器的 `Accept-Language` 头检测用户语言偏好

**检测逻辑**：
```typescript
// 浏览器发送的请求头
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8

// Middleware 解析：
// 1. zh-CN（中文-中国）→ 匹配 'zh' → 重定向到 /zh
// 2. 如果没有 zh，检查 en → 重定向到 /en
// 3. 如果都没有 → 使用 defaultLocale（/en）
```

**示例场景**：

##### **场景 1：中文浏览器**
```
浏览器设置: 中文（简体）
Accept-Language: zh-CN,zh;q=0.9

用户访问: /guides
→ 检测到 zh-CN
→ 匹配 locales 中的 'zh'
→ 重定向到: /zh/guides
```

##### **场景 2：英文浏览器**
```
浏览器设置: English (US)
Accept-Language: en-US,en;q=0.9

用户访问: /guides
→ 检测到 en-US
→ 匹配 locales 中的 'en'
→ 重定向到: /en/guides
```

##### **场景 3：不支持的语言**
```
浏览器设置: 日本語
Accept-Language: ja-JP,ja;q=0.9

用户访问: /guides
→ 检测到 ja-JP
→ locales 中没有 'ja'
→ 使用 defaultLocale
→ 重定向到: /en/guides
```

**禁用语言检测**：
```typescript
localeDetection: false,
```
- 不会自动检测浏览器语言
- 总是使用 defaultLocale
- 用户必须手动切换语言

---

#### **3.2.4 localePrefix 配置 (第 15 行)**

```typescript
localePrefix: 'always'
```

**作用**：
- 控制 URL 中语言前缀的显示策略

**可选值**：

##### **'always'（当前使用）**
```
所有 URL 都必须包含语言前缀

✅ /en/guides
✅ /zh/guides
✅ /en/tools
✅ /zh/tools

❌ /guides  → 重定向到 /en/guides
❌ /tools   → 重定向到 /en/tools
```

**优势**：
- URL 结构清晰明确
- SEO 友好（每种语言有独立 URL）
- 易于分享和收藏

##### **'as-needed'（可选）**
```typescript
localePrefix: 'as-needed'
```

```
默认语言不显示前缀，其他语言显示

✅ /guides        （默认语言 en）
✅ /zh/guides     （非默认语言）
✅ /tools         （默认语言 en）
✅ /zh/tools      （非默认语言）
```

**优势**：
- 默认语言的 URL 更简洁
- 减少重定向

**劣势**：
- URL 结构不一致
- SEO 可能不如 'always' 清晰

##### **'never'（可选）**
```typescript
localePrefix: 'never'
```

```
URL 中不显示语言前缀

✅ /guides
✅ /tools

语言通过 cookie 或 session 管理
```

**适用场景**：
- 单语言应用
- 语言通过子域名区分（如 `en.example.com`、`zh.example.com`）

---

### 3.3 Matcher 配置 (第 18-21 行)

```typescript
export const config = {
	// 匹配所有路径，除了 api、_next、静态文件
	matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
```

#### **作用**
定义 middleware 在哪些路径上执行。

#### **正则表达式解析**

```regex
/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)
```

**分解说明**：

##### **1. 外层结构**
```regex
/(...)/
```
- 匹配整个路径

##### **2. 负向前瞻（Negative Lookahead）**
```regex
(?!api|_next/static|_next/image|favicon.ico|.*\\..*)
```
- `(?!...)` 表示"不匹配以下内容"
- 排除特定路径

##### **3. 排除的路径**

###### **api**
```
排除所有 API 路由
❌ /api/users
❌ /api/posts
```
**原因**：API 路由不需要国际化

###### **_next/static**
```
排除 Next.js 静态资源
❌ /_next/static/chunks/main.js
❌ /_next/static/css/app.css
```
**原因**：静态资源不需要重定向

###### **_next/image**
```
排除 Next.js 图片优化 API
❌ /_next/image?url=/photo.jpg&w=800
```
**原因**：图片请求不需要国际化

###### **favicon.ico**
```
排除网站图标
❌ /favicon.ico
```
**原因**：图标文件不需要重定向

###### **.*\\..*（任何带扩展名的文件）**
```
排除所有静态文件
❌ /logo.png
❌ /styles.css
❌ /script.js
❌ /document.pdf
```
**原因**：静态文件不需要国际化

##### **4. 匹配的路径**
```regex
.*
```
- 匹配所有其他路径

#### **实际匹配示例**

```
✅ 匹配（会执行 middleware）：
/
/guides
/tools
/about
/zh/guides
/en/tools

❌ 不匹配（不执行 middleware）：
/api/users
/_next/static/chunks/main.js
/_next/image?url=/photo.jpg
/favicon.ico
/logo.png
/styles.css
```

---

## 四、完整执行流程

### 4.1 场景 1：首次访问根路径

```
1. 【用户请求】
   浏览器: 中文（简体）
   Accept-Language: zh-CN,zh;q=0.9
   访问: https://utd-wiki.netlify.app/

2. 【Middleware 执行】
   → matcher 匹配: / ✅
   → localeDetection: true
   → 检测 Accept-Language: zh-CN
   → 匹配 locales 中的 'zh'
   → localePrefix: 'always'
   → 需要添加语言前缀

3. 【重定向】
   → 重定向到: /zh
   → HTTP 307 Temporary Redirect

4. 【第二次请求】
   访问: /zh
   → 渲染 src/app/[locale]/page.tsx
   → 显示中文首页
```

### 4.2 场景 2：访问不带语言前缀的页面

```
1. 【用户请求】
   浏览器: English (US)
   Accept-Language: en-US,en;q=0.9
   访问: /guides

2. 【Middleware 执行】
   → matcher 匹配: /guides ✅
   → 检测 Accept-Language: en-US
   → 匹配 locales 中的 'en'
   → localePrefix: 'always'
   → 需要添加语言前缀

3. 【重定向】
   → 重定向到: /en/guides
   → HTTP 307 Temporary Redirect

4. 【第二次请求】
   访问: /en/guides
   → 渲染 src/app/[locale]/guides/page.tsx
   → 显示英文攻略列表
```

### 4.3 场景 3：直接访问带语言前缀的页面

```
1. 【用户请求】
   访问: /zh/guides/beginner-guide

2. 【Middleware 执行】
   → matcher 匹配: /zh/guides/beginner-guide ✅
   → URL 已包含语言前缀 'zh'
   → 'zh' 在 locales 列表中 ✅
   → 无需重定向

3. 【直接渲染】
   → 渲染 src/app/[locale]/guides/[slug]/page.tsx
   → 显示中文新手攻略
```

### 4.4 场景 4：访问静态资源

```
1. 【用户请求】
   访问: /logo.png

2. 【Matcher 检查】
   → 正则匹配: .*\\..*
   → 匹配到文件扩展名 .png
   → matcher 不匹配 ❌

3. 【跳过 Middleware】
   → Middleware 不执行
   → 直接返回静态文件
```

### 4.5 场景 5：访问 API 路由

```
1. 【用户请求】
   访问: /api/users

2. 【Matcher 检查】
   → 正则匹配: (?!api...)
   → 路径以 /api 开头
   → matcher 不匹配 ❌

3. 【跳过 Middleware】
   → Middleware 不执行
   → 直接路由到 API 处理器
```

---

## 五、与其他文件的关系

### 5.1 文件依赖关系

```
src/i18n/config.ts
  ↓ (导出 locales, defaultLocale)
src/middleware.ts
  ↓ (拦截请求，添加语言前缀)
src/app/[locale]/layout.tsx
  ↓ (接收 locale 参数)
src/app/[locale]/page.tsx
  ↓ (渲染对应语言的页面)
```

### 5.2 配置文件

#### **src/i18n/config.ts**
```typescript
export const locales = ['en', 'zh'] as const
export type Locale = (typeof locales)[number]
export const defaultLocale: Locale = 'en'
```
- 定义支持的语言
- Middleware 使用这些配置

#### **next.config.mjs**
```javascript
const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')
export default withNextIntl(nextConfig)
```
- 集成 next-intl 插件
- 启用国际化功能

#### **src/i18n/request.ts**
```typescript
export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../locales/${locale}.json`)).default
}))
```
- 配置翻译文件加载
- Middleware 重定向后，这里加载对应的翻译

---

## 六、调试和测试

### 6.1 查看 Middleware 日志

```typescript
// src/middleware.ts
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n/config'
import { NextRequest, NextResponse } from 'next/server'

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localeDetection: true,
  localePrefix: 'always'
})

export default function middleware(request: NextRequest) {
  console.log('🔍 Middleware 执行')
  console.log('📍 请求路径:', request.nextUrl.pathname)
  console.log('🌐 Accept-Language:', request.headers.get('accept-language'))

  const response = intlMiddleware(request)

  if (response.status === 307) {
    console.log('↪️  重定向到:', response.headers.get('location'))
  }

  return response
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'],
}
```

### 6.2 测试不同浏览器语言

#### **Chrome 浏览器**
```
1. 打开 Chrome 设置
2. 搜索"语言"
3. 添加语言并设置优先级
4. 重启浏览器
5. 访问网站，观察重定向
```

#### **使用 curl 测试**
```bash
# 测试中文
curl -H "Accept-Language: zh-CN" http://localhost:3000/guides
# 应该重定向到 /zh/guides

# 测试英文
curl -H "Accept-Language: en-US" http://localhost:3000/guides
# 应该重定向到 /en/guides

# 测试不支持的语言
curl -H "Accept-Language: ja-JP" http://localhost:3000/guides
# 应该重定向到 /en/guides（默认语言）
```

#### **使用浏览器开发者工具**
```
1. 打开开发者工具（F12）
2. 切换到 Network 标签
3. 访问 /guides
4. 查看请求：
   - Status: 307 Temporary Redirect
   - Location: /zh/guides 或 /en/guides
```

---

## 七、常见问题

### 7.1 重定向循环

**问题**：页面不断重定向

**原因**：
- matcher 配置错误，匹配了已经有语言前缀的路径
- localePrefix 配置与实际路由不匹配

**解决**：
```typescript
// ❌ 错误：会匹配所有路径，包括 /en/guides
matcher: ['/*']

// ✅ 正确：排除已有语言前缀的路径
matcher: ['/((?!api|_next|en|zh).*)']
```

### 7.2 静态资源被重定向

**问题**：图片、CSS 等静态文件返回 HTML

**原因**：
- matcher 匹配了静态文件路径

**解决**：
```typescript
// 确保排除所有静态文件
matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)']
//                                                          ^^^^^^^^
//                                                          排除带扩展名的文件
```

### 7.3 API 路由被重定向

**问题**：API 请求返回 307 重定向

**原因**：
- matcher 匹配了 API 路径

**解决**：
```typescript
// 确保排除 /api 路径
matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)']
//                ^^^
//                排除 API 路由
```

### 7.4 语言检测不准确

**问题**：总是重定向到英文，即使浏览器是中文

**排查**：
1. 检查 `localeDetection` 是否为 `true`
2. 检查浏览器的 `Accept-Language` 头
3. 检查 `locales` 配置是否包含对应语言

**解决**：
```typescript
// 确保启用语言检测
localeDetection: true,

// 确保 locales 包含所有支持的语言
locales: ['en', 'zh'],  // 不要遗漏
```

---

## 八、性能优化

### 8.1 Middleware 性能

**特点**：
- 运行在 Edge Runtime（边缘计算）
- 非常快速（通常 < 10ms）
- 不会显著影响页面加载速度

**优化建议**：
1. 保持 middleware 逻辑简单
2. 避免复杂的计算
3. 不要在 middleware 中进行数据库查询

### 8.2 减少重定向

**策略 1：使用 cookie 记住用户语言**
```typescript
// next-intl 自动处理
// 用户首次访问后，语言偏好存储在 cookie 中
// 后续访问直接使用 cookie，减少语言检测
```

**策略 2：引导用户直接访问带语言前缀的 URL**
```html
<!-- 在其他网站分享时，使用完整 URL -->
<a href="https://utd-wiki.netlify.app/zh/guides">
  查看攻略
</a>
```

---

## 九、最佳实践

### 9.1 语言前缀策略选择

**推荐使用 `'always'`**：
```typescript
localePrefix: 'always'
```

**理由**：
- ✅ URL 结构清晰一致
- ✅ SEO 友好（每种语言独立 URL）
- ✅ 易于分享和收藏
- ✅ 避免混淆

### 9.2 Matcher 配置

**推荐模式**：
```typescript
matcher: [
  // 匹配所有路径
  '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'
]
```

**不推荐**：
```typescript
// ❌ 太宽泛，可能匹配不该匹配的路径
matcher: ['/*']

// ❌ 太具体，需要手动维护每个路径
matcher: ['/guides', '/tools', '/about']
```

### 9.3 语言检测

**推荐启用**：
```typescript
localeDetection: true
```

**理由**：
- 提升用户体验
- 自动适配用户语言
- 减少手动选择的步骤

---

## 十、扩展功能

### 10.1 添加语言切换 Cookie

```typescript
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n/config'
import { NextRequest } from 'next/server'

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localeDetection: true,
  localePrefix: 'always'
})

export default function middleware(request: NextRequest) {
  const response = intlMiddleware(request)

  // 从 URL 中提取语言
  const locale = request.nextUrl.pathname.split('/')[1]

  // 如果是有效语言，设置 cookie
  if (locales.includes(locale as any)) {
    response.cookies.set('NEXT_LOCALE', locale, {
      maxAge: 60 * 60 * 24 * 365, // 1 年
      path: '/'
    })
  }

  return response
}
```

### 10.2 添加自定义重定向逻辑

```typescript
import createMiddleware from 'next-intl/middleware'
import { locales, defaultLocale } from './i18n/config'
import { NextRequest, NextResponse } from 'next/server'

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localeDetection: true,
  localePrefix: 'always'
})

export default function middleware(request: NextRequest) {
  // 自定义逻辑：将旧路径重定向到新路径
  if (request.nextUrl.pathname === '/old-guides') {
    return NextResponse.redirect(new URL('/en/guides', request.url))
  }

  // 执行 next-intl middleware
  return intlMiddleware(request)
}
```

---

## 十一、总结

### 11.1 核心功能

1. **自动语言检测**：根据浏览器语言自动选择
2. **URL 重定向**：确保所有 URL 包含语言前缀
3. **路径过滤**：排除 API、静态资源等不需要国际化的路径

### 11.2 关键配置

| 配置项 | 值 | 作用 |
|--------|-----|------|
| `locales` | `['en', 'zh']` | 支持的语言列表 |
| `defaultLocale` | `'en'` | 默认语言 |
| `localeDetection` | `true` | 启用自动语言检测 |
| `localePrefix` | `'always'` | 总是显示语言前缀 |
| `matcher` | 正则表达式 | 定义执行范围 |

### 11.3 执行流程

```
用户请求
  ↓
Matcher 检查（是否需要执行？）
  ↓
语言检测（浏览器语言是什么？）
  ↓
URL 检查（是否已有语言前缀？）
  ↓
重定向（如需要）或放行
  ↓
页面渲染
```

---

## 十二、相关资源

- **next-intl Middleware 文档**：https://next-intl-docs.vercel.app/docs/routing/middleware
- **Next.js Middleware 文档**：https://nextjs.org/docs/app/building-your-application/routing/middleware
- **Edge Runtime**：https://nextjs.org/docs/app/api-reference/edge
