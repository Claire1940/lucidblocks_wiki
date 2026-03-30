# next.config.mjs 配置文件介绍

## 一、应用场景

`next.config.mjs` 是 Next.js 项目的核心配置文件，定义了整个应用的构建和运行时行为。在本项目中主要用于：

1. **国际化配置**：集成 next-intl 实现多语言支持（中文/英文）
2. **MDX 支持**：启用 Markdown + JSX 混合编写内容页面（攻略、指南等）
3. **图片优化配置**：管理外部图片域名白名单和优化策略
4. **开发环境配置**：允许特定域名访问开发服务器（same-app 预览）
5. **页面扩展名配置**：支持多种文件类型作为页面组件

---

## 二、基础知识

### 2.1 Next.js 配置系统

#### **配置文件格式**
Next.js 支持三种配置文件格式：
- `next.config.js` - CommonJS 格式（传统）
- `next.config.mjs` - ES Module 格式（现代，本项目使用）
- `next.config.ts` - TypeScript 格式

**为什么使用 .mjs？**
- 支持 ES6 `import/export` 语法
- 更好的模块化和树摇优化
- 与现代 JavaScript 生态一致

#### **配置对象结构**
```typescript
const nextConfig: NextConfig = {
  // 各种配置选项
}
```

### 2.2 插件系统（Higher-Order Functions）

Next.js 使用高阶函数模式扩展配置：

```javascript
// 基础配置
const nextConfig = { /* ... */ }

// 应用插件
const withPlugin1 = plugin1(nextConfig)
const withPlugin2 = plugin2(withPlugin1)

// 或链式调用
export default plugin2(plugin1(nextConfig))
```

**工作原理**：
- 每个插件接收配置对象，返回增强后的配置对象
- 插件可以添加 webpack 配置、修改构建行为等
- 执行顺序：从内到外（先 plugin1，后 plugin2）

### 2.3 next-intl（国际化库）

#### **核心概念**
- **Locale**：语言代码（如 `en`、`zh`）
- **Messages**：翻译文件（`en.json`、`zh.json`）
- **Request**：请求级别的国际化配置

#### **工作流程**
1. 用户访问 `/zh/guides` 或 `/en/guides`
2. middleware 检测 locale 参数
3. 加载对应的翻译文件
4. 在组件中通过 `useTranslations()` 获取翻译

### 2.4 MDX（Markdown + JSX）

#### **什么是 MDX？**
MDX 允许在 Markdown 中使用 React 组件：

```mdx
# 攻略标题

这是普通的 Markdown 文本。

<CustomComponent prop="value">
  这是 React 组件
</CustomComponent>

## 下一节

继续使用 Markdown...
```

#### **应用场景**
- 博客文章
- 文档页面
- 游戏攻略（本项目）
- 任何需要富文本 + 交互的内容

#### **处理流程**
1. `.mdx` 文件被编译为 React 组件
2. 支持 remark（Markdown 处理）和 rehype（HTML 处理）插件
3. 可以导入和使用任何 React 组件

### 2.5 Next.js 图片优化

#### **默认行为**
Next.js 的 `<Image>` 组件会自动：
- 按需生成不同尺寸的图片
- 转换为现代格式（WebP、AVIF）
- 懒加载（延迟加载）
- 防止布局偏移（CLS）

#### **外部图片限制**
出于安全考虑，默认只能使用本地图片。要使用外部图片需要：
1. 在 `domains` 或 `remotePatterns` 中配置白名单
2. Next.js 会代理这些图片并进行优化

---

## 三、代码实现和作用

### 3.1 导入依赖 (第 1-2 行)

```javascript
import createMDX from '@next/mdx'
import createNextIntlPlugin from 'next-intl/plugin'
```

**作用**：
- `@next/mdx`：Next.js 官方 MDX 插件，用于处理 `.mdx` 文件
- `next-intl/plugin`：next-intl 的 Next.js 插件，用于集成国际化功能

---

### 3.2 创建 next-intl 插件实例 (第 4 行)

```javascript
const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts')
```

**作用**：
- 创建 next-intl 插件的高阶函数
- 参数 `'./src/i18n/request.ts'` 指向国际化请求配置文件

**`src/i18n/request.ts` 的作用**：
```typescript
// 典型内容
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../locales/${locale}.json`)).default
}));
```

- 定义如何根据 locale 加载翻译文件
- 在服务端渲染时被调用
- 返回当前请求的翻译消息

---

### 3.3 Next.js 配置对象 (第 6-41 行)

#### **3.3.1 TypeScript 类型注释 (第 6 行)**

```javascript
/** @type {import('next').NextConfig} */
```

**作用**：
- JSDoc 类型注释，为 JavaScript 文件提供 TypeScript 类型检查
- 即使不使用 `.ts` 文件，也能获得 IDE 智能提示
- `import('next').NextConfig` 引用 Next.js 的配置类型定义

---

#### **3.3.2 页面扩展名配置 (第 8 行)**

```javascript
pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
```

**作用**：
- 定义哪些文件可以作为 Next.js 页面组件
- 默认值：`['tsx', 'ts', 'jsx', 'js']`
- 添加 `'md'` 和 `'mdx'` 后，可以直接创建 Markdown 页面

**示例**：
```
src/app/guides/
├── page.tsx          ✅ 有效页面
├── tutorial.mdx      ✅ 有效页面（因为配置了 mdx）
└── README.md         ✅ 有效页面（因为配置了 md）
```

**注意事项**：
- 添加 `md` 可能导致意外的页面生成（如 `README.md` 变成路由）
- 建议只在需要时添加，或使用特定目录存放内容文件

---

#### **3.3.3 允许的开发域名 (第 9 行)**

```javascript
allowedDevOrigins: ["*.preview.same-app.com"],
```

**作用**：
- 允许特定域名访问开发服务器（`bun dev`）
- 支持通配符 `*`（匹配任意子域名）

**使用场景**：
- **same-app 预览功能**：在 same-app 平台上预览开发中的应用
- **多设备测试**：在不同设备上访问本地开发服务器
- **团队协作**：允许团队成员访问你的开发环境

**安全性**：
- 仅在开发模式下生效（`NODE_ENV=development`）
- 生产环境不受影响

**示例**：
```
https://abc123.preview.same-app.com → ✅ 允许
https://xyz789.preview.same-app.com → ✅ 允许
https://other-domain.com            → ❌ 拒绝
```

---

#### **3.3.4 图片配置 (第 10-40 行)**

##### **禁用图片优化 (第 11 行)**

```javascript
images: {
  unoptimized: true,
```

**作用**：
- 禁用 Next.js 的自动图片优化
- 图片将以原始格式和尺寸提供

**为什么禁用？**
1. **部署平台限制**：某些平台（如 Netlify）不支持 Next.js 图片优化 API
2. **构建速度**：跳过图片处理，加快构建时间
3. **外部 CDN**：图片已经在 CDN 上优化过（如 Unsplash、same-assets）

**权衡**：
- ✅ 优势：构建快、部署简单、兼容性好
- ❌ 劣势：失去自动 WebP 转换、响应式图片、懒加载等优化

---

##### **允许的图片域名（旧格式）(第 12-17 行)**

```javascript
domains: [
  "source.unsplash.com",
  "images.unsplash.com",
  "ext.same-assets.com",
  "ugc.same-assets.com",
],
```

**作用**：
- 白名单外部图片域名
- 允许 `<Image>` 组件加载这些域名的图片

**域名说明**：
- `source.unsplash.com`：Unsplash 图片 API（随机图片）
- `images.unsplash.com`：Unsplash CDN（特定图片）
- `ext.same-assets.com`：same-app 外部资源 CDN
- `ugc.same-assets.com`：same-app 用户生成内容 CDN

**注意**：
- `domains` 是旧的配置方式（Next.js 12）
- 推荐使用 `remotePatterns`（更灵活、更安全）

---

##### **远程图片模式（新格式）(第 18-39 行)**

```javascript
remotePatterns: [
  {
    protocol: "https",
    hostname: "source.unsplash.com",
    pathname: "/**",
  },
  // ... 其他域名
],
```

**作用**：
- 更精细的外部图片控制
- 可以限制协议、主机名、路径

**配置项说明**：
- `protocol`：只允许 `https`（更安全）
- `hostname`：精确的域名（不支持通配符子域名）
- `pathname`：路径模式（`/**` 表示所有路径）

**高级用法**：
```javascript
{
  protocol: "https",
  hostname: "cdn.example.com",
  pathname: "/images/**",  // 只允许 /images/ 下的图片
}
```

**为什么同时配置 `domains` 和 `remotePatterns`？**
- 向后兼容（旧版 Next.js）
- 某些工具可能只识别 `domains`
- 建议：新项目只使用 `remotePatterns`

---

### 3.4 创建 MDX 插件实例 (第 43-49 行)

```javascript
const withMDX = createMDX({
  options: {
    remarkPlugins: [],
    rehypePlugins: [],
  },
})
```

**作用**：
- 创建 MDX 插件的高阶函数
- 配置 Markdown 和 HTML 处理插件

#### **remarkPlugins（Markdown 处理）**
在 Markdown 转换为 HTML 之前处理：
```javascript
remarkPlugins: [
  remarkGfm,        // GitHub Flavored Markdown（表格、任务列表等）
  remarkMath,       // 数学公式支持
  remarkToc,        // 自动生成目录
]
```

#### **rehypePlugins（HTML 处理）**
在 HTML 生成之后处理：
```javascript
rehypePlugins: [
  rehypeSlug,           // 为标题添加 id
  rehypeAutolinkHeadings, // 标题自动链接
  rehypeHighlight,      // 代码高亮
]
```

**当前配置**：
- 两个数组都为空 `[]`
- 使用 MDX 的默认处理
- 可以根据需要添加插件

---

### 3.5 导出最终配置 (第 51 行)

```javascript
export default withNextIntl(withMDX(nextConfig))
```

**作用**：
- 应用所有插件到基础配置
- 执行顺序：`nextConfig` → `withMDX` → `withNextIntl`

**执行流程**：
1. **基础配置**：`nextConfig`（页面扩展名、图片配置等）
2. **应用 MDX 插件**：`withMDX(nextConfig)`
   - 添加 MDX 文件处理
   - 配置 webpack loader
   - 注册 remark/rehype 插件
3. **应用 next-intl 插件**：`withNextIntl(...)`
   - 添加国际化路由
   - 配置 middleware
   - 注入翻译加载逻辑

**最终配置对象**：
```javascript
{
  // 原始配置
  pageExtensions: [...],
  images: {...},

  // MDX 添加的配置
  webpack: (config) => { /* MDX loader */ },

  // next-intl 添加的配置
  i18n: {...},
  // ... 其他增强
}
```

---

## 四、在项目中的应用

### 4.1 使用外部图片

```tsx
import Image from 'next/image'

// Unsplash 图片
<Image
  src="https://images.unsplash.com/photo-123456"
  alt="游戏截图"
  width={800}
  height={600}
/>

// same-assets 图片
<Image
  src="https://ext.same-assets.com/game-icon.png"
  alt="游戏图标"
  width={64}
  height={64}
/>
```

### 4.2 创建 MDX 页面

```
src/app/[locale]/guides/beginner/page.mdx
```

```mdx
# 新手攻略

欢迎来到 Universal Tower Defense！

<Alert type="info">
  这是一个自定义 React 组件
</Alert>

## 基础操作

1. 放置塔防单位
2. 升级单位
3. 使用技能

<VideoPlayer src="/videos/tutorial.mp4" />
```

### 4.3 国际化路由

配置生效后，自动支持：
```
/zh/guides          → 中文攻略页面
/en/guides          → 英文攻略页面
/zh/tools           → 中文工具页面
/en/tools           → 英文工具页面
```

---

## 五、配置优化建议

### 5.1 启用图片优化（如果部署平台支持）

```javascript
images: {
  unoptimized: false,  // 启用优化
  formats: ['image/avif', 'image/webp'],  // 现代格式
  deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  remotePatterns: [
    // 保持现有配置
  ],
}
```

### 5.2 添加常用 MDX 插件

```javascript
import remarkGfm from 'remark-gfm'
import rehypeSlug from 'rehype-slug'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'

const withMDX = createMDX({
  options: {
    remarkPlugins: [remarkGfm],  // 支持表格、任务列表
    rehypePlugins: [
      rehypeSlug,                 // 标题 ID
      rehypeAutolinkHeadings,     // 标题锚点
    ],
  },
})
```

### 5.3 移除冗余的 `domains` 配置

```javascript
images: {
  unoptimized: true,
  // 删除 domains，只保留 remotePatterns
  remotePatterns: [
    // ... 现有配置
  ],
}
```

### 5.4 限制 MDX 页面扩展名

```javascript
pageExtensions: ['js', 'jsx', 'mdx', 'ts', 'tsx'],
// 移除 'md'，避免 README.md 等文件变成路由
```

### 5.5 添加性能优化配置

```javascript
const nextConfig = {
  // ... 现有配置

  // 启用 SWC 压缩（更快）
  swcMinify: true,

  // 严格模式
  reactStrictMode: true,

  // 生产环境移除 console
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // 实验性功能
  experimental: {
    optimizeCss: true,  // CSS 优化
  },
}
```

---

## 六、常见问题

### 6.1 图片加载失败

**问题**：`Image with src "https://example.com/image.jpg" is not configured`

**解决**：
1. 检查域名是否在 `remotePatterns` 中
2. 确保 `protocol` 和 `hostname` 完全匹配
3. 检查 `pathname` 模式是否覆盖图片路径

### 6.2 MDX 文件不被识别

**问题**：`.mdx` 文件不能作为页面

**解决**：
1. 确保 `pageExtensions` 包含 `'mdx'`
2. 检查 `@next/mdx` 是否正确安装
3. 确认 `withMDX` 插件已应用

### 6.3 国际化路由不工作

**问题**：访问 `/zh/page` 返回 404

**解决**：
1. 检查 `src/i18n/request.ts` 是否存在
2. 确认 `src/middleware.ts` 已配置
3. 验证 `withNextIntl` 插件已应用

### 6.4 开发服务器跨域问题

**问题**：在 same-app 预览时出现 CORS 错误

**解决**：
1. 确认 `allowedDevOrigins` 包含正确的域名模式
2. 检查是否在开发模式下运行（`bun dev`）
3. 验证域名是否匹配通配符模式

---

## 七、相关文件

- **src/i18n/request.ts**：国际化请求配置
- **src/middleware.ts**：路由中间件（处理 locale 检测）
- **src/locales/*.json**：翻译文件
- **tailwind.config.ts**：Tailwind CSS 配置（可能引用 Next.js 配置）
- **package.json**：依赖版本管理

---

## 八、插件执行顺序可视化

```
┌─────────────────────────────────────────────┐
│           nextConfig (基础配置)              │
│  - pageExtensions                           │
│  - allowedDevOrigins                        │
│  - images                                   │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         withMDX(nextConfig)                 │
│  + MDX 文件处理                              │
│  + webpack loader 配置                       │
│  + remark/rehype 插件                        │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      withNextIntl(withMDX(nextConfig))      │
│  + 国际化路由                                │
│  + middleware 集成                           │
│  + 翻译加载逻辑                              │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         【最终导出的配置】
```

---

## 九、注意事项

1. **插件顺序很重要**：
   - 先应用的插件可能被后应用的插件覆盖
   - 通常：基础功能 → 内容处理 → 路由/国际化

2. **图片优化与部署平台**：
   - Vercel：完全支持图片优化
   - Netlify：需要 `unoptimized: true` 或使用 `@netlify/plugin-nextjs`
   - 静态导出：必须 `unoptimized: true`

3. **MDX 性能影响**：
   - 每个 `.mdx` 文件都会被编译为 React 组件
   - 大量 MDX 文件会增加构建时间
   - 考虑使用内容管理系统（CMS）存储大量内容

4. **开发域名安全**：
   - `allowedDevOrigins` 仅在开发模式生效
   - 不要在生产环境依赖此配置

5. **类型安全**：
   - 使用 JSDoc 注释获得类型检查
   - 或将文件重命名为 `next.config.ts` 获得完整 TypeScript 支持

6. **配置缓存**：
   - 修改配置后需要重启开发服务器
   - 某些配置（如 webpack）可能需要清除 `.next` 缓存

---

## 十、调试技巧

### 10.1 查看最终配置

```javascript
// 在 next.config.mjs 中添加
const finalConfig = withNextIntl(withMDX(nextConfig))
console.log('Final Next.js config:', JSON.stringify(finalConfig, null, 2))
export default finalConfig
```

### 10.2 测试图片域名

```bash
# 在浏览器控制台
const img = new Image()
img.src = 'https://images.unsplash.com/photo-123456'
img.onload = () => console.log('✅ 图片加载成功')
img.onerror = () => console.log('❌ 图片加载失败')
```

### 10.3 验证 MDX 编译

```bash
# 构建项目并查看输出
bun run build

# 查找 .mdx 文件的编译结果
ls -la .next/server/app/**/page.js
```

### 10.4 检查国际化配置

```javascript
// 在页面组件中
import { useLocale } from 'next-intl'

export default function Page() {
  const locale = useLocale()
  console.log('当前语言:', locale)
  return <div>Locale: {locale}</div>
}
```
