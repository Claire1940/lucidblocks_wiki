---
description: SEO 全面检查和配置
trigger: 当用户说"SEO检查"、"seo audit"、"检查SEO"时触发
---

# seo-audit

全面检查和配置网站的 SEO 设置，确保所有元数据、结构化数据、sitemap 等配置正确。

## 执行步骤

### 1. 读取游戏信息
- 读取 `需求/00基础信息.md` 获取：
  - 游戏名称
  - 游戏域名
  - 游戏描述
  - 关键词

### 2. 检查 robots.txt
- 文件：`public/robots.txt`
- 确认：
  - Sitemap URL 使用新游戏域名
  - 爬虫规则正确配置

### 3. 检查 sitemap.ts
- 文件：`src/app/sitemap.ts`
- 确认：
  - 基础 URL 使用新游戏域名
  - 包含所有内容类型的页面
  - 多语言路径正确

### 4. 检查页面元数据
- 文件：`src/app/[locale]/layout.tsx`
  - 根布局的 metadata（title、description、keywords）
  - OpenGraph 配置
  - Twitter Card 配置
  - 使用新游戏名称和描述

- 文件：`src/app/[locale]/page.tsx`
  - 首页 metadata
  - 确保与游戏信息一致

- 文件：`src/app/[locale]/[...slug]/page.tsx`
  - 动态页面 metadata 生成逻辑
  - 从 MDX metadata 正确提取信息

### 5. 检查结构化数据
- 文件：`src/components/content/ArticleStructuredData.tsx`
  - Article schema 配置正确
  - 作者、发布日期、图片等信息完整

- 文件：`src/components/content/ListStructuredData.tsx`
  - ItemList schema 配置正确
  - 列表项信息完整

### 6. 配置首页 JSON-LD
- 文件：`src/app/[locale]/page.tsx`
- 配置 Organization schema：
  - `logo`: 使用 `public/images/hero.webp`
  - `image`: 使用 `public/images/hero.webp`
  - 尺寸要求：
    - logo: 建议 112x112 或更大（正方形）
    - image: 建议 1200x630（用于社交分享）

- 配置 WebSite schema：
  - `url`: 使用新游戏域名
  - `name`: 使用新游戏名称
  - `description`: 使用游戏描述
  - `image`: 使用 `public/images/hero.webp`

### 7. 检查 next.config.mjs
- 文件：`next.config.mjs`
- 确认：
  - 无旧游戏名称引用
  - 配置项正确

### 8. 验证图片配置
- 检查 `public/images/hero.webp` 是否存在
- 确认图片尺寸适合 SEO：
  - 宽度至少 1200px（用于社交分享）
  - 高度至少 630px
  - 文件大小合理（< 500KB）

### 9. 构建测试
- 清理缓存：`rm -rf .next`
- 运行构建：`npm run build`
- 检查构建输出是否有错误或警告
- 验证生成的 sitemap 和 robots.txt

### 10. 运行验证脚本
- 图标验证：`node scripts/validate-icons.js`
- 翻译验证：`npm run validate:translations`（如果存在）
- SEO 检查：`node scripts/check-seo.js`（如果存在）

### 11. 本地测试
- 启动开发服务器：`npm run dev`
- 使用 curl 测试关键 URL：
  ```bash
  curl -I http://localhost:3000
  curl -I http://localhost:3000/sitemap.xml
  curl -I http://localhost:3000/robots.txt
  ```
- 在浏览器中检查：
  - 首页标题和描述
  - 社交分享预览（使用浏览器开发工具）
  - 结构化数据（使用 Google Rich Results Test）

## 检查清单

完成后确认：
- [ ] `robots.txt` 域名正确
- [ ] `sitemap.ts` 域名正确
- [ ] `layout.tsx` metadata 使用新游戏名称
- [ ] `page.tsx` metadata 正确
- [ ] `[...slug]/page.tsx` 动态 metadata 正确
- [ ] `ArticleStructuredData.tsx` 配置正确
- [ ] `ListStructuredData.tsx` 配置正确
- [ ] `next.config.mjs` 无旧游戏名称
- [ ] 首页 Organization schema 配置正确
- [ ] 首页 WebSite schema 配置正确
- [ ] Hero 图片存在且尺寸合适
- [ ] 构建测试通过
- [ ] 验证脚本通过
- [ ] 本地测试通过

## SEO 最佳实践

### Meta Tags
- **Title**: 50-60 字符，包含主关键词
- **Description**: 150-160 字符，吸引点击
- **Keywords**: 5-10 个相关关键词

### OpenGraph
- **og:title**: 与 title 一致或略有变化
- **og:description**: 与 description 一致
- **og:image**: 1200x630px，< 8MB
- **og:type**: website 或 article

### Twitter Card
- **twitter:card**: summary_large_image
- **twitter:title**: 与 og:title 一致
- **twitter:description**: 与 og:description 一致
- **twitter:image**: 与 og:image 一致

### 结构化数据
- 使用 JSON-LD 格式
- 包含 Organization、WebSite、Article 等 schema
- 图片必须可访问（绝对 URL）
- 日期使用 ISO 8601 格式

## 常见问题

### 图片不显示在搜索结果
- 确认图片 URL 是绝对路径（包含域名）
- 确认图片尺寸符合要求（至少 1200x630）
- 确认图片可公开访问（无需登录）
- 使用 Google Rich Results Test 验证

### Sitemap 不更新
- 清理 `.next` 缓存
- 重新构建项目
- 检查 `sitemap.ts` 的动态生成逻辑

### 元数据不生效
- 确认使用 `export const metadata` 而非运行时生成
- 检查是否有多个 metadata 定义冲突
- 清理浏览器缓存

## 测试工具

- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Facebook Sharing Debugger**: https://developers.facebook.com/tools/debug/
- **Twitter Card Validator**: https://cards-dev.twitter.com/validator
- **Schema.org Validator**: https://validator.schema.org/

## 相关 Skills

- 执行前先完成 `/game-rebrand` 和 `/content-reset`
- 发现问题后可重新运行 `/game-rebrand` 修复配置
