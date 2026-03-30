# SEO Skills 使用指南

## 📋 可用的 Skills

### 1. `/seo-check` - SEO 完整检查

**触发方式**:
- "SEO检查"
- "seo检查"
- "检查SEO"
- "/seo-check"

**功能**: 执行全面的 SEO 检查，生成详细报告

**检查内容**:

#### 阶段 1：代码结构检查
- ✅ 根 Layout（html lang, meta 标签, SearchAction）
- ✅ 动态页面 SEO（metadata, hreflang, OpenGraph）
- ✅ Sitemap 配置
- ✅ 国际化配置
- ✅ 结构化数据组件
- ✅ robots.txt
- ⭐ **H1 标签**（新增）
- ⭐ **图片 alt 属性**（新增）
- ⭐ **面包屑导航**（新增）
- ⭐ **内链完整性**（新增）

#### 阶段 2：构建验证
- ✅ 构建测试
- ✅ 静态生成检查

#### 阶段 3：安全检查
- ✅ 敏感信息检查
- ✅ .gitignore 检查

#### 阶段 4：本地运行验证
- ✅ 首页检查（canonical, hreflang, title, description）
- ✅ 语言重定向
- ✅ 多语言页面
- ✅ 动态页面
- ✅ Sitemap
- ⭐ **移动端响应式**（新增）
- ⭐ **页面性能 (Lighthouse)**（新增）

#### 阶段 5：生成报告
- 检查摘要（通过/失败/警告数量）
- 详细结果（每个检查项的状态）
- 修复建议（按优先级分类）

**输出**: `seo-check-report.md`

---

### 2. `/seo-fix` - SEO 自动修复

**触发方式**:
- "SEO修复"
- "seo修复"
- "修复SEO"
- "/seo-fix"

**前置条件**: 必须先运行 `/seo-check` 生成检查报告

**功能**: 根据检查报告自动修复发现的问题

**修复内容**:

#### 自动修复项
1. ✅ 添加 SearchAction 结构化数据
2. ✅ 修复 sitemap 域名硬编码
3. ✅ 修复根 Layout
4. ✅ 添加 robots.txt
5. ✅ 替换品牌词硬编码
6. ✅ 修复 .gitignore
7. ⭐ **添加/修复 H1 标签**（新增）
8. ⭐ **添加图片 alt 属性**（新增）
9. ⭐ **添加面包屑导航**（新增）
10. ⭐ **修复内链问题**（新增）

#### 验证步骤
- 运行 `npm run build`
- 运行 `npm run typecheck`
- 重新运行 `/seo-check`

**输出**: `seo-fix-report.md`

---

## 🎯 完整工作流程

```bash
# 步骤 1: 执行 SEO 检查
你说: "SEO检查"
# → 生成 seo-check-report.md

# 步骤 2: 查看报告
你说: "查看报告" 或 "打开 seo-check-report.md"
# → 我会读取并解释报告内容

# 步骤 3: 执行自动修复
你说: "SEO修复"
# → 自动修复问题，生成 seo-fix-report.md

# 步骤 4: 验证修复结果
你说: "验证修复" 或 "SEO检查"
# → 重新运行 SEO 检查，确认问题已解决

# 步骤 5: 提交代码
你说: "提交代码"
# → 我会帮你创建 Git commit
```

---

## 📊 检查报告示例

```markdown
# SEO 检查报告

生成时间: 2026-03-13 10:30:00

## 检查摘要

- ✅ 通过: 45 项
- ❌ 失败: 5 项
- ⚠️ 警告: 3 项
- 📊 总计: 53 项

## 详细结果

### 阶段 1：代码结构检查

#### 1.1 根 Layout
- ✅ 包含 <html lang> 标签
- ❌ 缺少 SearchAction 结构化数据
  - 修复建议: 创建 src/components/seo/SearchAction.tsx
  - 优先级: 🔴 高

#### 1.7 H1 标签
- ✅ DetailPage 使用 H1 标签
- ⚠️ H1 标签未包含核心关键词
  - 修复建议: 在 H1 中添加游戏名称
  - 优先级: 🟡 中

#### 1.8 图片 alt 属性
- ❌ 发现 12 个图片缺少 alt 属性
  - 文件: src/components/home/Hero.tsx (3个)
  - 文件: src/components/home/Features.tsx (9个)
  - 修复建议: 为所有图片添加描述性 alt 文本
  - 优先级: 🔴 高

...

## 修复建议

### 🔴 高优先级（必须修复）

1. 添加 SearchAction 结构化数据
2. 为 12 个图片添加 alt 属性
3. 修复 sitemap 域名硬编码

### 🟡 中优先级（建议修复）

1. 优化 H1 标签关键词
2. 添加面包屑导航
3. 修复 3 个内链死链

### 🟢 低优先级（可选优化）

1. 提升 Lighthouse Performance 分数（当前 85，目标 90）
2. 优化移动端触摸目标大小
```

---

## 🔧 修复报告示例

```markdown
# SEO 修复报告

生成时间: 2026-03-13 10:45:00

## 修复摘要

- ✅ 成功修复: 8 项
- ❌ 修复失败: 0 项
- 📊 总计: 8 项

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

### 2. 添加图片 alt 属性

**状态**: ✅ 成功

**修改文件**:
- src/components/home/Hero.tsx
- src/components/home/Features.tsx

**修改内容**:
- 为 12 个图片添加了描述性 alt 文本
- 装饰性图片使用 alt=""

---

## 验证结果

### 构建测试
```
✅ 构建成功
✅ 类型检查通过
```

### SEO 检查
```
✅ 通过: 50 项
⚠️ 警告: 1 项
❌ 失败: 0 项
```

## 下一步行动

1. ✅ 检查修复后的代码
2. ✅ 本地测试所有修复项
3. ⏳ 提交代码到 Git
4. ⏳ 部署到生产环境
5. ⏳ 使用 Google Search Console 验证
```

---

## 💡 使用技巧

### 1. 定期检查
建议在以下情况运行 SEO 检查：
- 添加新页面后
- 修改重要组件后
- 部署到生产环境前
- 每周定期检查

### 2. 优先级处理
- 🔴 高优先级：立即修复（影响搜索引擎索引）
- 🟡 中优先级：尽快修复（影响用户体验）
- 🟢 低优先级：有时间再优化（锦上添花）

### 3. 自动化集成
可以将 SEO 检查集成到 CI/CD 流程：
```bash
# 在 GitHub Actions 中
- name: SEO Check
  run: |
    # 触发 SEO 检查
    # 如果有高优先级问题，构建失败
```

### 4. 手动检查项
以下项目需要手动检查（skill 无法自动化）：
- Google Search Console 验证
- 实际搜索结果展示
- 用户体验测试
- 竞品分析

---

## 🚨 注意事项

### 安全措施
- ✅ 修复前会备份原文件（添加 `.backup` 后缀）
- ✅ 如果修复失败，会自动回滚
- ✅ 不会删除任何文件
- ✅ 不会修改 Git 历史
- ✅ 不会自动提交代码

### 交互式确认
以下操作会询问用户确认：
- 品牌词替换（需要提供新游戏名称）
- 域名配置（需要提供生产环境域名）
- 危险操作（如修改根 layout）

### 限制
- Lighthouse 检查需要安装 `lighthouse` CLI
- 性能检查在本地环境可能不准确
- 移动端检查需要手动使用浏览器开发者工具

---

## 📚 相关文档

- [CLAUDE.md](../../CLAUDE.md) - 项目开发规范
- [RUNBOOK.md](../../需求/automation/RUNBOOK.md) - 自动化流程
- [SCRIPTS_GUIDE.md](../../需求/automation/SCRIPTS_GUIDE.md) - 本地脚本指南

---

## 🆘 常见问题

### Q: 检查报告在哪里？
A: 在项目根目录，文件名为 `seo-check-report.md`

### Q: 修复失败怎么办？
A: 查看 `seo-fix-report.md` 中的错误信息，或手动修复

### Q: 可以只修复部分问题吗？
A: 可以，在修复过程中会询问你要修复哪些问题

### Q: 检查需要多长时间？
A: 通常 2-5 分钟，取决于项目大小

### Q: 修复会破坏现有代码吗？
A: 不会，修复前会备份，失败会自动回滚

---

## 📝 更新日志

### 2026-03-13
- ✅ 添加 H1 标签检查
- ✅ 添加图片 alt 属性检查
- ✅ 添加面包屑导航检查
- ✅ 添加内链完整性检查
- ✅ 添加移动端响应式检查
- ✅ 添加 Lighthouse 性能检查
- ✅ 添加对应的自动修复功能

### 2026-03-12
- ✅ 创建初始版本
- ✅ 实现基础 SEO 检查
- ✅ 实现自动修复功能
