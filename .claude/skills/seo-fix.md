---
name: seo-fix
description: 根据 SEO 检查报告自动修复发现的问题
trigger: 当用户说"SEO修复"、"seo修复"、"修复SEO"或"/seo-fix"时触发
---

# SEO 自动修复方案

## 概述

这个 skill 根据 `seo-check` 生成的报告，自动修复发现的 SEO 问题。

## 前置条件

- 必须先运行 `/seo-check` 生成检查报告
- 报告文件位置: `seo-check-report.md`

## 修复流程

### 阶段 1：读取检查报告

1. 读取 `seo-check-report.md`
2. 解析失败项和警告项
3. 按优先级排序修复任务

### 阶段 2：执行自动修复

#### 修复 2.1：添加 SearchAction 结构化数据

**条件**: 如果检查报告显示缺少 SearchAction

**操作**:
1. 创建 `src/components/seo/SearchAction.tsx`
2. 在 `src/app/[locale]/layout.tsx` 中引入并使用

**代码模板**:
```typescript
// src/components/seo/SearchAction.tsx
export function SearchAction({ siteUrl }: { siteUrl: string }) {
  const searchAction = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    url: siteUrl,
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${siteUrl}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(searchAction) }}
    />
  )
}
```

#### 修复 2.2：修复 sitemap 域名硬编码

**条件**: 如果检查报告显示 sitemap 使用硬编码域名

**操作**:
1. 读取 `src/app/sitemap.ts`
2. 替换硬编码域名为环境变量

**修复前**:
```typescript
const BASE_URL = 'https://www.burglingnomes.wiki'
```

**修复后**:
```typescript
const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.burglingnomes.wiki'
```

#### 修复 2.3：修复根 Layout

**条件**: 如果检查报告显示根 layout 缺少必要标签

**操作**:
1. 读取 `src/app/layout.tsx`
2. 添加必要的 HTML 结构和 meta 标签

**修复后的结构**:
```typescript
import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://www.burglingnomes.wiki'),
  viewport: 'width=device-width, initial-scale=1',
  charset: 'utf-8',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
```

#### 修复 2.4：添加 robots.txt

**条件**: 如果检查报告显示缺少 robots.txt

**操作**:
1. 创建 `public/robots.txt`

**内容**:
```
User-agent: *
Allow: /

Sitemap: https://www.burglingnomes.wiki/sitemap.xml
```

**注意**: 域名需要替换为实际域名

#### 修复 2.5：替换品牌词硬编码

**条件**: 如果检查报告显示有品牌词硬编码

**操作**:
1. 读取 `需求/automation/game.config.json` 获取游戏名称
2. 在以下文件中替换硬编码的品牌词：
   - `src/app/[locale]/[...slug]/page.tsx`
   - `src/app/sitemap.ts`
   - 其他包含品牌词的文件

**替换规则**:
- 使用配置文件中的 `gameName` 字段
- 或使用环境变量 `NEXT_PUBLIC_SITE_NAME`

#### 修复 2.6：修复 .gitignore

**条件**: 如果检查报告显示 .env 文件未被忽略

**操作**:
1. 读取 `.gitignore`
2. 确保包含以下内容：

```
# 环境变量
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
```

#### 修复 2.7：添加/修复 H1 标签

**条件**: 如果检查报告显示 H1 标签问题

**操作**:
1. 检查 `src/components/content/DetailPage.tsx`
2. 确保使用 `<h1>` 标签显示文章标题
3. 检查 `src/components/content/NavigationPage.tsx`
4. 确保使用 `<h1>` 标签显示页面标题

**修复示例**:
```typescript
// DetailPage.tsx
<h1 className="text-4xl font-bold">{frontmatter.title}</h1>

// NavigationPage.tsx
<h1 className="text-4xl font-bold">{title}</h1>
```

#### 修复 2.8：添加图片 alt 属性

**条件**: 如果检查报告显示图片缺少 alt 属性

**操作**:
1. 使用 grep 查找所有缺少 alt 的图片
2. 为每个图片添加描述性的 alt 文本
3. 装饰性图片使用 `alt=""`

**查找命令**:
```bash
# 查找缺少 alt 的 <img> 标签
grep -r "<img" src/ --include="*.tsx" --include="*.jsx" | grep -v "alt="

# 查找缺少 alt 的 Next.js Image 组件
grep -r "<Image" src/ --include="*.tsx" --include="*.jsx" | grep -v "alt="
```

**修复示例**:
```typescript
// ❌ 错误
<Image src="/logo.png" width={100} height={100} />

// ✅ 正确
<Image src="/logo.png" alt="Burglin' Gnomes Logo" width={100} height={100} />

// ✅ 装饰性图片
<Image src="/decoration.png" alt="" width={100} height={100} />
```

#### 修复 2.9：添加面包屑导航

**条件**: 如果检查报告显示缺少面包屑导航

**操作**:
1. 创建 `src/components/content/Breadcrumb.tsx`
2. 在 `DetailPage.tsx` 中引入并使用
3. 添加 BreadcrumbList 结构化数据

**代码模板**:
```typescript
// src/components/content/Breadcrumb.tsx
import Link from 'next/link'

interface BreadcrumbItem {
  label: string
  href: string
}

export function Breadcrumb({ items }: { items: BreadcrumbItem[] }) {
  const breadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      item: item.href,
    })),
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbSchema) }}
      />
      <nav aria-label="Breadcrumb" className="mb-4">
        <ol className="flex items-center space-x-2 text-sm">
          {items.map((item, index) => (
            <li key={item.href} className="flex items-center">
              {index > 0 && <span className="mx-2">/</span>}
              {index === items.length - 1 ? (
                <span className="text-gray-500">{item.label}</span>
              ) : (
                <Link href={item.href} className="hover:underline">
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
      </nav>
    </>
  )
}
```

#### 修复 2.10：修复内链问题

**条件**: 如果检查报告显示有孤岛页面或死链

**操作**:
1. 分析所有页面的内链关系
2. 为孤岛页面添加内链
3. 修复死链（404）
4. 在相关文章中添加内链

**检查命令**:
```bash
# 查找所有内部链接
grep -r "href=" content/ --include="*.mdx"

# 检查链接是否有效（需要服务器运行）
# 使用工具如 broken-link-checker
```

**修复建议**:
- 在首页添加指向重要页面的链接
- 在文章底部添加"相关文章"模块
- 在导航菜单中包含所有主要分类
- 在文章内容中自然地添加内链

### 阶段 3：验证修复结果

修复完成后，自动执行以下验证：

1. 运行 `npm run build` 确保构建成功
2. 运行 `npm run typecheck` 确保类型正确
3. 重新运行 `/seo-check` 验证修复效果

### 阶段 4：生成修复报告

生成一个 Markdown 格式的修复报告，包含：

1. **修复摘要**
   - 修复项数量
   - 成功修复数量
   - 失败修复数量

2. **详细修复记录**
   - 每个修复项的详细说明
   - 修改的文件列表
   - 修改前后的对比

3. **验证结果**
   - 构建是否成功
   - 类型检查是否通过
   - SEO 检查是否通过

## 输出格式

```markdown
# SEO 修复报告

生成时间: YYYY-MM-DD HH:mm:ss

## 修复摘要

- ✅ 成功修复: X 项
- ❌ 修复失败: X 项
- 📊 总计: X 项

## 详细修复记录

### 1. 添加 SearchAction 结构化数据

**状态**: ✅ 成功

**修改文件**:
- 创建: src/components/seo/SearchAction.tsx
- 修改: src/app/[locale]/layout.tsx

**修改内容**:
```diff
+ import { SearchAction } from '@/components/seo/SearchAction'
+
+ <SearchAction siteUrl={siteUrl} />
```

---

### 2. 修复 sitemap 域名硬编码

**状态**: ✅ 成功

**修改文件**:
- src/app/sitemap.ts

**修改内容**:
```diff
- const BASE_URL = 'https://www.burglingnomes.wiki'
+ const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://www.burglingnomes.wiki'
```

---

## 验证结果

### 构建测试
```
✅ 构建成功
✅ 类型检查通过
```

### SEO 检查
```
✅ 通过: 25 项
⚠️ 警告: 2 项
❌ 失败: 0 项
```

## 下一步行动

1. 检查修复后的代码
2. 本地测试所有修复项
3. 提交代码到 Git
4. 部署到生产环境
5. 使用 Google Search Console 验证
```

## 执行流程

1. 读取 SEO 检查报告
2. 解析失败项和警告项
3. 按优先级执行修复
4. 验证修复结果
5. 生成修复报告
6. 输出报告到控制台和文件（`seo-fix-report.md`）

## 注意事项

- 修复前会备份原文件（添加 `.backup` 后缀）
- 如果修复失败，会自动回滚
- 修复完成后会自动运行验证
- 生成的报告保存在项目根目录
- 修复过程中会显示详细的进度信息

## 安全措施

- 不会删除任何文件
- 不会修改 Git 历史
- 不会自动提交代码
- 所有修改都可以通过 Git 回滚
- 修复前会询问用户确认

## 交互式修复

如果检测到以下情况，会询问用户：

1. **品牌词替换**: 询问新的游戏名称
2. **域名配置**: 询问生产环境域名
3. **危险操作**: 询问是否继续（如修改根 layout）

## 使用示例

```bash
# 1. 先运行 SEO 检查
/seo-check

# 2. 查看检查报告
cat seo-check-report.md

# 3. 执行自动修复
/seo-fix

# 4. 查看修复报告
cat seo-fix-report.md

# 5. 验证修复结果
npm run build
npm run dev
```
