---
name: seo-check
description: 执行完整的 SEO 检查，包括代码审查、配置验证、结构化数据检查和多语言验证
trigger: 当用户说"SEO检查"、"seo检查"、"检查SEO"或"/seo-check"时触发
---

# SEO 完整检查方案

## 概述

这个 skill 执行全面的 SEO 检查，确保网站符合搜索引擎优化最佳实践。

## 检查阶段

### 阶段 1：代码结构检查

#### 1.1 检查根 Layout
**文件**: `src/app/layout.tsx`

检查项：
- [ ] 是否包含 `<html lang>` 标签
- [ ] 是否包含全局 meta 标签（viewport, charset）
- [ ] 是否包含 SearchAction 结构化数据
- [ ] 是否包含 WebSite 结构化数据（可选）

#### 1.2 检查动态页面 SEO
**文件**: `src/app/[locale]/[...slug]/page.tsx`

检查项：
- [ ] generateMetadata 是否正确生成 title 和 description
- [ ] 是否包含 alternates（hreflang）
- [ ] 是否包含 OpenGraph 标签
- [ ] 是否包含 robots 配置
- [ ] 是否有品牌词硬编码（需要替换）
- [ ] 是否有 fallback 到英文的逻辑

#### 1.3 检查 Sitemap
**文件**: `src/app/sitemap.ts`

检查项：
- [ ] 是否使用环境变量而非硬编码域名
- [ ] 是否包含所有语言版本的首页
- [ ] 是否包含所有静态页面
- [ ] 是否包含所有 MDX 文章
- [ ] 优先级配置是否合理
- [ ] 更新频率配置是否合理

#### 1.4 检查国际化配置
**文件**: `src/i18n/routing.ts`

检查项：
- [ ] localePrefix 是否设置为 'as-needed'
- [ ] defaultLocale 是否为 'en'
- [ ] localeDetection 是否启用

#### 1.5 检查结构化数据组件
**文件**:
- `src/components/seo/SearchAction.tsx`（或在 layout.tsx 中）
- `src/components/content/ArticleStructuredData.tsx`
- `src/components/content/ListStructuredData.tsx`

检查项：
- [ ] SearchAction 是否存在
- [ ] ArticleStructuredData 是否正确
- [ ] ListStructuredData 是否正确

#### 1.6 检查 robots.txt
**文件**: `public/robots.txt`

检查项：
- [ ] 文件是否存在
- [ ] 是否允许搜索引擎抓取
- [ ] 是否包含 sitemap 链接

#### 1.7 检查 H1 标签
**检查范围**: 所有页面组件

检查项：
- [ ] 每个页面是否有且仅有一个 H1 标签
- [ ] H1 是否包含核心关键词
- [ ] H1 是否与 title 相关但不完全相同
- [ ] H1 是否在页面顶部（语义化）
- [ ] DetailPage 组件是否正确使用 H1
- [ ] NavigationPage 组件是否正确使用 H1

#### 1.8 检查图片 alt 属性
**检查范围**: 所有页面和组件

检查项：
- [ ] 所有 `<img>` 标签是否有 alt 属性
- [ ] alt 文本是否描述性（不是空字符串或 "image"）
- [ ] 装饰性图片是否使用 `alt=""`
- [ ] Next.js Image 组件是否有 alt 属性
- [ ] MDX 文件中的图片是否有 alt 属性

#### 1.9 检查面包屑导航
**文件**: `src/components/content/Breadcrumb.tsx` 或相关组件

检查项：
- [ ] 是否有面包屑组件
- [ ] 是否在详情页显示
- [ ] 是否包含 BreadcrumbList 结构化数据（JSON-LD）
- [ ] 链接是否正确（首页 → 分类 → 当前页）
- [ ] 是否有正确的 aria-label

#### 1.10 检查内链完整性
**检查范围**: 所有 MDX 文件和组件

检查项：
- [ ] 是否有孤岛页面（没有任何内链指向）
- [ ] 相关文章链接是否有效
- [ ] 导航链接是否完整
- [ ] 是否有死链（404）
- [ ] 内部链接是否使用相对路径
- [ ] 是否有足够的内链密度（每篇文章至少 2-3 个内链）

### 阶段 2：构建验证

#### 2.1 执行构建测试
```bash
npm run build
```

检查项：
- [ ] 构建是否成功
- [ ] 是否有类型错误
- [ ] 是否有 ESLint 错误

#### 2.2 检查静态生成
```bash
ls -la .next/server/pages/
```

检查项：
- [ ] 是否生成了 .html 文件
- [ ] 首页是否静态生成
- [ ] 静态页面是否生成

### 阶段 3：安全检查

#### 3.1 检查敏感信息
```bash
grep -r "sk-" src/ --exclude-dir=node_modules
grep -r "API_KEY" src/ --exclude-dir=node_modules
grep -r "password" src/ --exclude-dir=node_modules
```

检查项：
- [ ] 代码中是否有 API 密钥硬编码
- [ ] 代码中是否有密码硬编码
- [ ] 代码中是否有其他敏感信息

#### 3.2 检查 .gitignore
```bash
cat .gitignore | grep ".env"
```

检查项：
- [ ] .env.local 是否在 .gitignore 中
- [ ] .env 是否在 .gitignore 中

### 阶段 4：本地运行验证

#### 4.1 启动开发服务器
```bash
npm run dev
```

#### 4.2 检查首页
访问 `http://localhost:3000/`

检查项：
- [ ] 页面是否正常显示
- [ ] 是否显示英文内容
- [ ] 查看页面源代码是否包含 `<link rel="canonical">`
- [ ] 查看页面源代码是否包含 `<link rel="alternate" hreflang>`
- [ ] 查看页面源代码是否包含 SearchAction JSON-LD
- [ ] title 是否正确
- [ ] description 是否正确

#### 4.3 检查语言重定向
访问 `http://localhost:3000/en`

检查项：
- [ ] 是否自动重定向到 `/`（301 或 308）

#### 4.4 检查其他语言
访问 `http://localhost:3000/pt`, `/fr`, `/es` 等

检查项：
- [ ] 页面是否正常显示
- [ ] 是否显示对应语言的内容
- [ ] 语言切换按钮是否正常工作

#### 4.5 检查动态页面
访问任意内容页面（如 `/codes/latest-codes`）

检查项：
- [ ] 页面是否正常显示
- [ ] title 是否与首页不同
- [ ] description 是否与首页不同
- [ ] 是否包含 ArticleStructuredData

#### 4.6 检查 Sitemap
访问 `http://localhost:3000/sitemap.xml`

检查项：
- [ ] sitemap 是否正常生成
- [ ] 是否包含所有语言版本的页面
- [ ] 是否包含 alternates（多语言链接）
- [ ] URL 格式是否正确

#### 4.7 检查移动端响应式
**检查方式**: 使用浏览器开发者工具（F12 → 设备模拟）

检查项：
- [ ] 在移动端视口下是否正常显示（375px, 414px）
- [ ] 文字是否可读（字体大小 >= 16px）
- [ ] 按钮是否可点击（触摸目标 >= 48px）
- [ ] 是否有横向滚动条
- [ ] 图片是否响应式（不溢出）
- [ ] 导航菜单在移动端是否可用
- [ ] 表格在移动端是否可滚动

#### 4.8 检查页面性能
**工具**: Lighthouse CLI（如果已安装）

检查项：
- [ ] Performance 分数 >= 90
- [ ] Accessibility 分数 >= 90
- [ ] Best Practices 分数 >= 90
- [ ] SEO 分数 >= 90
- [ ] First Contentful Paint (FCP) < 1.8s
- [ ] Largest Contentful Paint (LCP) < 2.5s
- [ ] Cumulative Layout Shift (CLS) < 0.1
- [ ] Total Blocking Time (TBT) < 200ms

**注意**: 如果未安装 Lighthouse CLI，此项检查会跳过，并在报告中标记为"需要手动检查"

### 阶段 5：生成检查报告

生成一个 Markdown 格式的检查报告，包含：

1. **检查摘要**
   - 总检查项数量
   - 通过项数量
   - 失败项数量
   - 警告项数量

2. **详细结果**
   - 每个阶段的检查结果
   - 失败项的详细说明
   - 修复建议

3. **优先级建议**
   - 🔴 高优先级（必须修复）
   - 🟡 中优先级（建议修复）
   - 🟢 低优先级（可选优化）

## 输出格式

```markdown
# SEO 检查报告

生成时间: YYYY-MM-DD HH:mm:ss

## 检查摘要

- ✅ 通过: X 项
- ❌ 失败: X 项
- ⚠️ 警告: X 项
- 📊 总计: X 项

## 详细结果

### 阶段 1：代码结构检查

#### 1.1 根 Layout
- ✅ 包含 <html lang> 标签
- ❌ 缺少 SearchAction 结构化数据
  - 修复建议: 创建 src/components/seo/SearchAction.tsx
  - 优先级: 🔴 高

...

### 阶段 2：构建验证

...

### 阶段 3：安全检查

...

### 阶段 4：本地运行验证

...

## 修复建议

### 🔴 高优先级（必须修复）

1. 添加 SearchAction 结构化数据
   - 文件: src/components/seo/SearchAction.tsx
   - 原因: 提升搜索结果中的站内搜索框显示

2. 修复 sitemap 域名硬编码
   - 文件: src/app/sitemap.ts
   - 原因: 部署到不同环境时需要动态域名

### 🟡 中优先级（建议修复）

...

### 🟢 低优先级（可选优化）

...

## 下一步行动

1. 修复所有 🔴 高优先级问题
2. 重新运行 SEO 检查
3. 修复 🟡 中优先级问题
4. 部署到生产环境
5. 使用 Google Search Console 验证
```

## 执行流程

1. 读取所有需要检查的文件
2. 执行代码结构检查
3. 执行构建验证
4. 执行安全检查
5. 启动开发服务器（如果未运行）
6. 执行本地运行验证
7. 生成检查报告
8. 输出报告到控制台和文件（`seo-check-report.md`）

## 注意事项

- 检查过程中不会修改任何文件
- 只读取和验证现有代码
- 生成的报告保存在项目根目录
- 如果发现问题，提供详细的修复建议
- 不会自动修复问题，需要用户确认后再执行修复
