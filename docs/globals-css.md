# globals.css 全局样式文件介绍

## 一、应用场景

`globals.css` 是整个项目的全局样式基础文件，在 `src/app/layout.tsx` 中被引入，作用于所有页面和组件。主要应用场景包括：

1. **设计系统基础**：定义整个应用的颜色系统、间距、圆角等设计令牌
2. **深色模式支持**：提供亮色/暗色主题的完整颜色方案
3. **全局动画效果**：滚动揭示动画，提升页面交互体验
4. **浏览器样式重置**：统一不同浏览器的默认样式
5. **自定义滚动条**：美化滚动条外观，与主题保持一致
6. **shadcn/ui 组件基础**：为所有 UI 组件提供统一的样式变量

---

## 二、基础知识

### 2.1 Tailwind CSS 架构

#### **@tailwind 指令**
```css
@tailwind base;       /* 基础样式重置 */
@tailwind components; /* 组件类 */
@tailwind utilities;  /* 工具类 */
```

- **base**：Preflight（Tailwind 的现代化 CSS 重置）
- **components**：可复用的组件样式类
- **utilities**：原子化工具类（如 `flex`、`text-center` 等）

#### **@layer 指令**
用于将自定义样式注入到 Tailwind 的特定层级：
```css
@layer base {
  /* 这里的样式会被注入到 base 层 */
}
```

**优势**：
- 确保样式的正确优先级顺序
- 支持 Tailwind 的 JIT 编译
- 可以使用 `@apply` 指令

### 2.2 CSS 变量 (Custom Properties)

#### **HSL 颜色格式**
项目使用 HSL（色相、饱和度、亮度）格式定义颜色：
```css
--primary: 240 5.9% 10%;
/* 色相: 240° (蓝色)
   饱和度: 5.9%
   亮度: 10% */
```

**为什么不包含 `hsl()` 包装？**
- 方便在 Tailwind 中使用透明度修饰符
- 例如：`bg-primary/50` → `hsl(240 5.9% 10% / 0.5)`

#### **使用方式**
在 CSS 中：
```css
background: hsl(var(--primary));
```

在 Tailwind 中：
```html
<div class="bg-primary text-primary-foreground">
```

### 2.3 shadcn/ui 设计令牌系统

shadcn/ui 使用语义化的颜色命名：

| 变量名 | 用途 | 示例 |
|--------|------|------|
| `--background` | 页面背景色 | 白色/深灰色 |
| `--foreground` | 主要文本色 | 黑色/白色 |
| `--primary` | 主要操作色 | 按钮、链接 |
| `--secondary` | 次要操作色 | 次要按钮 |
| `--muted` | 弱化背景色 | 禁用状态、占位符 |
| `--accent` | 强调色 | 悬停状态、高亮 |
| `--destructive` | 危险操作色 | 删除按钮、错误提示 |
| `--border` | 边框色 | 分割线、卡片边框 |
| `--input` | 输入框边框色 | 表单元素 |
| `--ring` | 焦点环色 | 键盘导航焦点 |

**配对原则**：
- 每个背景色都有对应的前景色（如 `--primary` 和 `--primary-foreground`）
- 确保文本在背景上有足够的对比度（符合 WCAG 标准）

### 2.4 深色模式实现

#### **基于 class 的切换**
```css
:root { /* 亮色主题 */ }
.dark { /* 暗色主题 */ }
```

**工作原理**：
1. 在 `<html>` 或 `<body>` 元素上添加/移除 `.dark` 类
2. CSS 变量自动切换到对应的颜色值
3. 所有使用这些变量的组件自动更新

**优势**：
- 无需 JavaScript 计算样式
- 性能优秀（纯 CSS 实现）
- 支持 SSR（服务端渲染）

---

## 三、代码实现和作用

### 3.1 Tailwind 指令导入 (第 1-3 行)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**作用**：
- 引入 Tailwind CSS 的所有功能
- 必须放在文件最顶部
- 编译时会被替换为实际的 CSS 代码

---

### 3.2 亮色主题颜色系统 (第 5-32 行)

```css
@layer base {
  :root {
    --background: 0 0% 100%;      /* 纯白色 */
    --foreground: 240 10% 3.9%;   /* 深灰黑色 */
    --primary: 240 5.9% 10%;      /* 深蓝黑色 */
    /* ... 更多颜色变量 */
  }
}
```

**核心颜色解析**：

#### **背景与文本**
- `--background: 0 0% 100%` → 纯白色背景
- `--foreground: 240 10% 3.9%` → 接近黑色的文本

#### **主要操作色**
- `--primary: 240 5.9% 10%` → 深色（接近黑色）
- `--primary-foreground: 0 0% 98%` → 白色文本（用于深色按钮上）

#### **次要操作色**
- `--secondary: 240 4.8% 95.9%` → 浅灰色
- `--secondary-foreground: 240 5.9% 10%` → 深色文本

#### **弱化元素**
- `--muted: 240 4.8% 95.9%` → 浅灰色背景
- `--muted-foreground: 240 3.8% 46.1%` → 中灰色文本（用于次要信息）

#### **强调色**
- `--accent: 240 4.8% 95.9%` → 浅灰色（悬停背景）
- `--accent-foreground: 240 5.9% 10%` → 深色文本

#### **危险操作**
- `--destructive: 0 84.2% 60.2%` → 红色（色相 0° = 红色）
- `--destructive-foreground: 0 0% 98%` → 白色文本

#### **边框与输入**
- `--border: 240 5.9% 90%` → 浅灰色边框
- `--input: 240 5.9% 90%` → 输入框边框（与 border 相同）
- `--ring: 240 5.9% 10%` → 深色焦点环

#### **其他**
- `--radius: 0.5rem` → 全局圆角大小（8px）
- `--chart-1` 到 `--chart-5` → 图表颜色（用于数据可视化）

---

### 3.3 暗色主题颜色系统 (第 34-59 行)

```css
.dark {
  --background: 220 30% 3%;       /* 深蓝黑色 */
  --foreground: 0 0% 98%;         /* 接近白色 */
  --primary: 152 60% 48%;         /* 青绿色 */
  /* ... 更多颜色变量 */
}
```

**核心变化**：

#### **背景与文本反转**
- `--background: 220 30% 3%` → 深蓝黑色（不是纯黑，更柔和）
- `--foreground: 0 0% 98%` → 接近白色的文本

#### **主色调变化**
- `--primary: 152 60% 48%` → **青绿色**（色相 152° = 青绿）
  - 亮色模式是深色，暗色模式是亮色
  - 提供更好的视觉对比
- `--primary-foreground: 0 0% 98%` → 白色文本

#### **卡片与弹出层**
- `--card: 220 25% 8%` → 比背景稍亮的深灰色
- `--popover: 220 25% 8%` → 与卡片相同

#### **次要元素**
- `--secondary: 220 20% 12%` → 深灰色
- `--muted: 220 20% 15%` → 稍亮的深灰色
- `--muted-foreground: 220 10% 60%` → 中灰色文本

#### **强调色**
- `--accent: 152 60% 48%` → 青绿色（与 primary 相同）
- `--ring: 152 60% 48%` → 青绿色焦点环

#### **危险操作**
- `--destructive: 0 62.8% 30.6%` → 深红色（比亮色模式更暗）

**设计理念**：
- 避免纯黑背景（#000000），使用深蓝灰色更护眼
- 主色调从深色变为亮色（青绿色），提供视觉焦点
- 保持足够的对比度，符合无障碍标准

---

### 3.4 全局样式重置 (第 62-69 行)

```css
@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

**作用**：

#### **统一边框色 (第 63-65 行)**
```css
* {
  @apply border-border;
}
```
- 为所有元素设置默认边框颜色
- `border-border` → 使用 `--border` CSS 变量
- 确保边框颜色与主题一致

#### **body 基础样式 (第 66-68 行)**
```css
body {
  @apply bg-background text-foreground;
}
```
- `bg-background` → 使用 `--background` 作为页面背景色
- `text-foreground` → 使用 `--foreground` 作为默认文本色
- 自动适配亮色/暗色主题

---

### 3.5 滚动揭示动画 (第 71-81 行)

```css
.scroll-reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.scroll-reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

**工作原理**：

1. **初始状态** (`.scroll-reveal`)：
   - `opacity: 0` → 完全透明
   - `transform: translateY(30px)` → 向下偏移 30px
   - `transition` → 定义动画过渡效果

2. **可见状态** (`.scroll-reveal.visible`)：
   - `opacity: 1` → 完全不透明
   - `transform: translateY(0)` → 回到原位

3. **触发方式**（在 JavaScript 中）：
   ```typescript
   // 使用 Intersection Observer API
   const observer = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
       if (entry.isIntersecting) {
         entry.target.classList.add('visible');
       }
     });
   });

   document.querySelectorAll('.scroll-reveal').forEach(el => {
     observer.observe(el);
   });
   ```

**应用场景**：
- 页面各个部分（Hero、Features、Tools 等）
- 卡片列表
- 统计数据
- 任何需要"渐入"效果的元素

**动画参数**：
- `0.6s` → 动画持续时间
- `ease-out` → 缓动函数（开始快，结束慢）
- `30px` → 偏移距离（可根据需要调整）

---

### 3.6 自定义滚动条样式 (第 83-99 行)

```css
::-webkit-scrollbar {
  width: 10px;
}

::-webkit-scrollbar-track {
  background: hsl(var(--background));
}

::-webkit-scrollbar-thumb {
  background: hsl(var(--muted));
  border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground));
}
```

**各部分作用**：

#### **滚动条宽度 (第 84-86 行)**
```css
::-webkit-scrollbar {
  width: 10px;
}
```
- 设置垂直滚动条宽度为 10px
- 默认浏览器滚动条通常为 15-17px

#### **滚动条轨道 (第 88-90 行)**
```css
::-webkit-scrollbar-track {
  background: hsl(var(--background));
}
```
- 轨道背景色与页面背景色相同
- 实现无缝融合效果

#### **滚动条滑块 (第 92-95 行)**
```css
::-webkit-scrollbar-thumb {
  background: hsl(var(--muted));
  border-radius: 5px;
}
```
- 使用 `--muted` 颜色（弱化的灰色）
- 圆角 5px，更现代的外观

#### **滑块悬停状态 (第 97-99 行)**
```css
::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--muted-foreground));
}
```
- 悬停时颜色加深（使用 `--muted-foreground`）
- 提供视觉反馈

**兼容性说明**：
- `::-webkit-scrollbar` 仅支持 Chromium 内核浏览器（Chrome、Edge、Opera）
- Firefox 使用 `scrollbar-width` 和 `scrollbar-color` 属性
- Safari 完全支持

**如需跨浏览器支持，可添加**：
```css
* {
  scrollbar-width: thin;
  scrollbar-color: hsl(var(--muted)) hsl(var(--background));
}
```

---

## 四、在项目中的应用

### 4.1 在组件中使用颜色变量

```tsx
// 使用 Tailwind 类
<div className="bg-primary text-primary-foreground">
  主要按钮
</div>

// 使用透明度修饰符
<div className="bg-primary/50">
  半透明背景
</div>

// 在自定义 CSS 中使用
<div style={{ background: 'hsl(var(--accent))' }}>
  自定义样式
</div>
```

### 4.2 深色模式切换

```tsx
// 在 layout.tsx 或顶层组件中
const [theme, setTheme] = useState('light');

useEffect(() => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}, [theme]);
```

### 4.3 滚动揭示动画

```tsx
// 在 page.tsx 中
useEffect(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.scroll-reveal').forEach((el) => {
    observer.observe(el);
  });

  return () => observer.disconnect();
}, []);

// 在 JSX 中使用
<section className="scroll-reveal">
  <h2>这个部分会在滚动时渐入</h2>
</section>
```

---

## 五、设计优势

1. **主题一致性**：所有组件使用统一的颜色系统
2. **深色模式支持**：一次定义，自动适配两种主题
3. **易于维护**：修改 CSS 变量即可更新整个应用的配色
4. **性能优秀**：纯 CSS 实现，无 JavaScript 运行时开销
5. **无障碍性**：颜色对比度符合 WCAG 标准
6. **灵活性**：支持透明度修饰符、颜色混合等高级功能
7. **现代化体验**：滚动动画、自定义滚动条提升用户体验

---

## 六、自定义与扩展

### 6.1 修改主色调

在 `:root` 和 `.dark` 中修改 `--primary` 变量：

```css
:root {
  --primary: 220 90% 56%;  /* 改为蓝色 */
}

.dark {
  --primary: 220 90% 56%;  /* 保持一致或使用不同色调 */
}
```

### 6.2 添加新的颜色变量

```css
:root {
  --success: 142 76% 36%;  /* 绿色 */
  --success-foreground: 0 0% 98%;
  --warning: 38 92% 50%;   /* 橙色 */
  --warning-foreground: 0 0% 98%;
}
```

然后在 `tailwind.config.ts` 中注册：

```typescript
theme: {
  extend: {
    colors: {
      success: 'hsl(var(--success))',
      'success-foreground': 'hsl(var(--success-foreground))',
      warning: 'hsl(var(--warning))',
      'warning-foreground': 'hsl(var(--warning-foreground))',
    }
  }
}
```

### 6.3 调整动画参数

```css
.scroll-reveal {
  opacity: 0;
  transform: translateY(50px);  /* 增加偏移距离 */
  transition: opacity 1s ease-out, transform 1s ease-out;  /* 延长动画时间 */
}
```

### 6.4 添加更多动画效果

```css
/* 从左侧滑入 */
.slide-in-left {
  opacity: 0;
  transform: translateX(-50px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.slide-in-left.visible {
  opacity: 1;
  transform: translateX(0);
}

/* 缩放渐入 */
.scale-in {
  opacity: 0;
  transform: scale(0.9);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.scale-in.visible {
  opacity: 1;
  transform: scale(1);
}
```

---

## 七、注意事项

1. **不要直接使用硬编码颜色**：
   ```tsx
   ❌ <div className="bg-blue-500">
   ✅ <div className="bg-primary">
   ```

2. **保持颜色对比度**：
   - 文本与背景的对比度至少为 4.5:1（WCAG AA 标准）
   - 使用工具检查：https://webaim.org/resources/contrastchecker/

3. **测试深色模式**：
   - 确保所有颜色在两种主题下都清晰可见
   - 特别注意边框、阴影等细节

4. **滚动动画性能**：
   - 使用 `transform` 和 `opacity`（GPU 加速）
   - 避免使用 `left`、`top` 等触发重排的属性

5. **滚动条样式兼容性**：
   - 在 Firefox 中测试滚动条外观
   - 考虑添加 `scrollbar-width` 和 `scrollbar-color` 作为后备

6. **CSS 变量命名**：
   - 遵循 shadcn/ui 的命名约定
   - 使用语义化名称（如 `--primary`），而非描述性名称（如 `--blue`）

7. **避免过度动画**：
   - 尊重用户的 `prefers-reduced-motion` 设置
   - 可添加：
     ```css
     @media (prefers-reduced-motion: reduce) {
       .scroll-reveal {
         transition: none;
       }
     }
     ```

---

## 八、相关文件

- **tailwind.config.ts**：Tailwind 配置，注册 CSS 变量为 Tailwind 类
- **src/app/layout.tsx**：引入 globals.css 的地方
- **src/components/ui/*.tsx**：使用这些颜色变量的 UI 组件
- **src/app/page.tsx**：使用滚动揭示动画的主页面

---

## 九、调试技巧

### 9.1 查看当前颜色值

在浏览器开发者工具中：
```javascript
// 获取 CSS 变量值
getComputedStyle(document.documentElement)
  .getPropertyValue('--primary')
// 输出: "240 5.9% 10%"
```

### 9.2 动态修改颜色

```javascript
// 临时修改主色调
document.documentElement.style.setProperty('--primary', '220 90% 56%');
```

### 9.3 测试深色模式

```javascript
// 切换深色模式
document.documentElement.classList.toggle('dark');
```

### 9.4 调试滚动动画

```javascript
// 手动触发动画
document.querySelectorAll('.scroll-reveal').forEach(el => {
  el.classList.add('visible');
});
```
