---
description: 将模板适配到新游戏项目
trigger: 当用户说"换游戏"、"rebrand"、"适配新游戏"、"game rebrand"时触发
---

# game-rebrand

将通用游戏模板适配到新游戏项目，包括主题、文案、链接、图标等核心配置。

## 执行步骤

### 1. 读取游戏基础信息
- 读取 `需求/00基础信息.md` 获取：
  - 游戏名称
  - 主题色
  - YouTube 视频 ID
  - 游戏平台和官网链接
  - 社群信息（Discord、Reddit、X、YouTube 等）
  - 支持的语言列表
  - 游戏信息和用户关心的数据

### 2. 更新主题颜色
- 文件：`src/app/globals.css`
- 根据主题色更新 CSS 变量

### 3. 更新 favicon 和 PWA 配置
- 检查 `需求/favicon_io/` 目录
- 复制所有图标文件到 `public/`
- 更新 `public/manifest.json` 的 PWA 信息（name、short_name、icons）

### 4. 转换并更新 Hero 图片
- 读取 `需求/技术/hero.png`
- 转换为 WebP 格式
- 保存到 `public/images/hero.webp`（替换旧文件）

### 5. 更新首页配置
- 文件：`src/app/[locale]/page.tsx`
- 更新 YouTube 视频 ID
- 更新 Hero 区的两个 CTA 按钮链接
- 更新 CTA Section 的两个按钮链接
- 确保所有外部链接指向新游戏

### 6. 更新翻译文件
- 文件：`src/locales/en.json`
- 更新以下部分：
  - `footer.copyright`：版权信息
  - `home.hero`：Hero 大标题（游戏名+wiki）、副标题、统计数据
  - `nav`：导航栏文案
  - `cta`：CTA 按钮文案和描述
  - `footer.social`：社交媒体链接

### 7. 更新法律页面
- 文件：
  - `src/app/[locale]/privacy-policy/page.tsx`
  - `src/app/[locale]/terms-of-service/page.tsx`
  - `src/app/[locale]/copyright/page.tsx`
  - `src/app/[locale]/about/page.tsx`
- 替换游戏名称和更新日期

### 8. 更新导航栏
- 文件：`src/components/Navigation.tsx`
- 更新 Logo 和游戏名称
- 更新 Play 按钮链接到官网

### 9. 更新元数据
- 文件：
  - `src/app/[locale]/layout.tsx`
  - `src/app/[locale]/[...slug]/page.tsx`
  - `src/app/[locale]/page.tsx`
- 更新所有 metadata（title、description、keywords）

### 10. 配置多语言
- 读取语言列表（加上英语最多8门）
- 更新 `src/i18n/routing.ts` 的 `locales` 数组
- 更新 `src/lib/content.ts` 的 `validLanguages` 数组
- 更新 `tools/articles/modules/translate/translate_config.json`
- 更新 `tools/articles/modules/transpage/transpage_config.json`

### 11. 更新 Footer 组件
- 文件：`src/components/Footer.tsx`（如果存在）
- 或 `src/app/[locale]/page.tsx` 的 Footer 部分
- 更新所有社交媒体链接

### 12. 验证和构建测试
- 运行 `npm run build` 验证配置
- 检查是否有构建错误
- 运行图标验证：`node scripts/validate-icons.js`

## 检查清单

完成后确认：
- [ ] 主题颜色已更新
- [ ] favicon 和 manifest.json 已配置
- [ ] Hero 图片已转换并替换
- [ ] YouTube 视频 ID 已更新
- [ ] 所有 CTA 按钮链接正确
- [ ] 所有社交媒体链接正确
- [ ] Footer 版权信息正确
- [ ] 法律页面游戏名称已替换
- [ ] 导航栏配置正确
- [ ] 元数据已更新
- [ ] 多语言配置正确
- [ ] 构建测试通过
- [ ] 无旧游戏名称残留

## 注意事项

1. **阅读需求文档**：每执行一项任务前，先阅读 `需求/03首页导航页.md` 对应部分
2. **原子性提交**：所有相关文件必须在同一个 commit 中
3. **图标验证**：修改 `locales/*.json` 添加图标引用时，必须同时更新 `src/lib/iconRegistry.ts`
4. **搜索残留**：使用 Grep 搜索旧游戏名称，确保全部替换

## 相关 Skills

- 执行完成后运行 `/content-reset` 清理旧内容
- 最后运行 `/seo-audit` 进行 SEO 检查
