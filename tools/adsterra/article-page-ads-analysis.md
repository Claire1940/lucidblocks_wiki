# 文章页广告放置分析文档

## 概述
本文档详细分析 StarRupture 网站文章页面的广告放置策略，重点关注侧边栏广告的固定实现方式。

---

## 一、广告位布局总览

文章页共有 **5 个广告位**，分布在不同区域：

| 广告位 | 位置 | 组件 | 尺寸 | 设备 |
|--------|------|------|------|------|
| 广告位 1 | 页面顶部 | `NativeAdBanner` | 自适应 | 全部 |
| 广告位 2 | 文章结束后 | `ResponsiveAdBanner` | 响应式 | 全部 |
| 广告位 3 | 侧边栏顶部 | `AdBanner` (banner-160x600) | 160×600 | 仅桌面 |
| 广告位 4 | 文章底部 | `Banner320x50` | 320×50 | 全部 |
| 广告位 5 | 侧边栏下方 | `Banner160x300` | 160×300 | 仅桌面 |

---

## 二、页面布局结构

### 2.1 整体布局
文件位置：`src/app/[locale]/[...slug]/page.tsx:190-316`

```jsx
<div className="container mx-auto py-12 px-4">
  <div className="max-w-7xl mx-auto">
    {/* 广告位 1: 页面顶部 */}
    <div className="mb-8 flex justify-center">
      <NativeAdBanner />
    </div>

    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* 主内容区域 (8列) */}
      <article className="lg:col-span-8">
        {/* 面包屑导航 */}
        {/* 文章头部 */}
        {/* 文章内容 */}
        {/* Newsletter CTA */}
        {/* 广告位 2 */}
        {/* 广告位 4 */}
      </article>

      {/* 侧边栏 (4列) */}
      <aside className="lg:col-span-4">
        {/* 相关文章 */}
        {/* 工具链接 */}
        {/* 广告位 3 - 固定定位 */}
        {/* 广告位 5 */}
      </aside>
    </div>
  </div>
</div>
```

### 2.2 响应式网格系统
- 使用 **Tailwind CSS Grid** 布局
- 桌面端（lg+）：`grid-cols-12`，主内容占 8 列，侧边栏占 4 列
- 移动端：`grid-cols-1`，单列布局（侧边栏广告不显示）

---

## 三、侧边栏广告固定实现 ⭐

### 3.1 固定定位的核心代码
文件位置：`src/app/[locale]/[...slug]/page.tsx:288-312`

```jsx
<aside className="lg:col-span-4">
  <div className="hidden lg:block space-y-6">
    {/* 相关文章组件 */}
    <RelatedArticles category={slug[0]} currentSlug={slug.join('/')} locale={locale} />

    {/* Export Heatmap CTA */}
    <Link href="/tools/export-heatmap" className="...">
      {/* ... */}
    </Link>

    {/* 广告位 3: 侧边栏 - 160x600 横幅广告 (仅桌面) */}
    <div className="flex justify-center sticky top-4">
      <AdBanner type="banner-160x600" />
    </div>

    {/* 广告位 5: 侧边栏 - 160x300 横幅广告 (仅桌面) */}
    <div className="flex justify-center mt-6">
      <Banner160x300 />
    </div>
  </div>
</aside>
```

### 3.2 固定定位的关键技术点

#### **1. CSS Sticky 定位**
```jsx
<div className="flex justify-center sticky top-4">
```

- **`sticky`**: CSS 粘性定位，滚动时广告会"粘"在视口
- **`top-4`**: 距离顶部 `1rem`（16px），防止广告贴边
- **`flex justify-center`**: 广告在容器内水平居中

#### **2. 工作原理**
1. **初始状态**：广告随页面正常滚动
2. **触发粘性**：当滚动到距离顶部 `1rem` 时
3. **固定位置**：广告保持在视口顶部 `1rem` 处
4. **边界限制**：父容器 `<aside>` 滚动完后，广告随父容器离开视口

#### **3. 仅桌面端显示**
```jsx
<div className="hidden lg:block space-y-6">
```
- **`hidden`**: 默认隐藏（移动端）
- **`lg:block`**: 大屏幕（≥1024px）显示
- **`space-y-6`**: 子元素垂直间距 `1.5rem`

---

## 四、广告组件详细分析

### 4.1 广告位 1: NativeAdBanner（原生横幅）
**文件位置**：`src/components/ads/NativeAdBanner.tsx`

**特点**：
- 使用 Adsterra 动态脚本加载
- 自适应容器宽度
- 自动检测设备并生成适配广告

**实现方式**：
```tsx
useEffect(() => {
  const script = document.createElement('script');
  script.src = 'https://pl28441008.effectivegatecpm.com/...';
  script.async = true;
  containerRef.current?.appendChild(script);
}, []);
```

---

### 4.2 广告位 2: ResponsiveAdBanner（响应式横幅）
**文件位置**：`src/components/ads/ResponsiveAdBanner.tsx`

**响应式规则**：
```tsx
const updateSize = () => {
  const width = window.innerWidth;
  if (width < 768) {
    setAdSize({ width: 300, height: 250 }); // 移动端
  } else if (width < 1024) {
    setAdSize({ width: 468, height: 60 });  // 平板
  } else {
    setAdSize({ width: 728, height: 90 });  // 桌面
  }
};
```

**加载方式**：
- 使用 iframe 加载 `/ads/banner-responsive.html`
- 监听窗口 resize 事件动态调整尺寸

---

### 4.3 广告位 3: AdBanner（160×600 侧边栏广告）
**文件位置**：`src/components/ads/AdBanner.tsx`

**配置**：
```tsx
const AD_CONFIGS = {
  'banner-160x600': { width: 160, height: 600 }
};
```

**关键样式**：
```tsx
<iframe
  src="/ads/banner-160x600.html"
  width={160}
  height={600}
  style={{
    border: 'none',
    maxWidth: '100%',
    display: 'block'
  }}
  scrolling="no"
/>
```

**固定实现**：
- 父容器使用 `sticky top-4` 实现粘性定位
- 600px 高度适合长篇文章侧边栏

---

### 4.4 广告位 4: Banner320x50（文章底部横幅）
**文件位置**：`src/components/ads/Banner320x50.tsx`

**特点**：
- 320×50 尺寸，适合移动端和桌面端
- 放置在文章底部，不干扰阅读
- iframe 加载方式

---

### 4.5 广告位 5: Banner160x300（侧边栏次要广告）
**文件位置**：`src/components/ads/Banner160x300.tsx`

**特点**：
- 160×300 尺寸，比主侧边栏广告短
- **不使用 sticky 定位**，正常流式布局
- 与广告位 3 配合，增加侧边栏广告密度

---

## 五、懒加载优化（LazyAdBanner）

**文件位置**：`src/components/ads/LazyAdBanner.tsx`

虽然当前文章页没有使用，但项目包含懒加载组件：

```tsx
useEffect(() => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect();
      }
    },
    { rootMargin: '200px' } // 提前 200px 开始加载
  );
}, []);
```

**优势**：
- 仅在广告进入视口时加载
- 减少初始页面加载时间
- 提升性能和用户体验

---

## 六、广告加载方式对比

| 方式 | 使用组件 | 优点 | 缺点 |
|------|----------|------|------|
| **iframe 加载** | AdBanner, Banner320x50, Banner160x300, ResponsiveAdBanner | 隔离性好，不影响主页面 | 可能有延迟 |
| **脚本动态注入** | NativeAdBanner | 灵活，自适应强 | 可能阻塞渲染 |
| **懒加载** | LazyAdBanner | 性能优化 | 实现复杂度高 |

---

## 七、关键技术总结

### 7.1 侧边栏广告固定的实现要点
1. **CSS Sticky 定位**：`sticky top-4` 实现滚动固定
2. **响应式隐藏**：`hidden lg:block` 仅桌面端显示
3. **Grid 布局**：`lg:col-span-4` 确保侧边栏宽度
4. **垂直间距**：`space-y-6` 保持广告与内容的间距

### 7.2 为什么只有广告位 3 固定？
- **广告位 3**（160×600）：高度大，适合长时间停留在视口
- **广告位 5**（160×300）：高度较小，固定意义不大，且避免过度粘性

### 7.3 性能优化建议
- ✅ 考虑使用 `LazyAdBanner` 替换主内容广告
- ✅ 添加广告加载失败的占位符
- ✅ 监控广告加载性能指标

---

## 八、广告位设计最佳实践

### 8.1 当前设计的优点
- ✅ 侧边栏固定广告提升可见度
- ✅ 响应式设计适配多设备
- ✅ 广告位分散，不影响阅读体验
- ✅ 仅桌面端显示侧边栏广告，移动端体验更好

### 8.2 潜在改进方向
- 🔄 可以考虑为广告位 5 也添加 sticky，但设置不同的 `top` 值
- 🔄 添加广告可见性追踪（viewability tracking）
- 🔄 使用 Intersection Observer 优化广告加载时机

---

## 九、代码文件清单

| 文件 | 功能 |
|------|------|
| `src/app/[locale]/[...slug]/page.tsx` | 文章页主模板，定义所有广告位 |
| `src/components/ads/NativeAdBanner.tsx` | 原生横幅广告（动态脚本） |
| `src/components/ads/ResponsiveAdBanner.tsx` | 响应式横幅广告 |
| `src/components/ads/AdBanner.tsx` | 通用广告组件（支持多种尺寸） |
| `src/components/ads/Banner320x50.tsx` | 320×50 横幅广告 |
| `src/components/ads/Banner160x300.tsx` | 160×300 侧边栏广告 |
| `src/components/ads/LazyAdBanner.tsx` | 懒加载广告组件（备用） |

---

## 十、常见问题 FAQ

**Q1: 为什么侧边栏广告在移动端不显示？**
A: 使用 `hidden lg:block`，避免移动端侧边栏占用空间，改善用户体验。

**Q2: sticky 定位在什么浏览器上支持？**
A: 现代浏览器（Chrome 56+, Safari 13+, Firefox 59+）均支持，覆盖率 >95%。

**Q3: 如何调整固定广告距离顶部的距离？**
A: 修改 `top-4` 为其他值（如 `top-8` = 2rem, `top-0` = 0px）。

**Q4: 如果想让两个侧边栏广告都固定怎么办？**
A: 为广告位 5 的容器也添加 `sticky`，并设置不同的 `top` 值（如 `top-[640px]`，确保在广告位 3 下方）。

---

**文档创建日期**: 2026-01-17
**分析版本**: StarRupture v1.0
