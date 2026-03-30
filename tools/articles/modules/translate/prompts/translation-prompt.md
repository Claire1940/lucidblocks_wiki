将以下 MDX 内容从英文翻译成 $language_name。

## ⚠️ 关键规则 - 必须严格遵守：

**规则 1：保留所有 import 语句**
- 原始内容以 import 语句开头，如 `import { Map, Swords } from 'lucide-react'`
- 你必须在翻译开头保持所有这些 import 行的原样
- 不要跳过、修改或翻译任何 import 语句

**规则 2：⛔️ 绝对不要添加代码块标记（```）**
- ⚠️ 这是最常见的错误，必须避免！
- 在 import 语句前不要添加 ```
- 在 metadata export 语句前后不要添加 ```
- 在 MDX 内容中不要添加 ```
- ❌ 错误示例：
  ```
  ```
  import { Map } from 'lucide-react'
  ```
  这是错误的！不要这样做！
  ```
- ✅ 正确示例：
  ```
  import { Map } from 'lucide-react'

  export const metadata = { ... }

  <Section>内容</Section>
  ```
  直接输出，不要有任何 ``` 标记

**规则 3：只翻译文本内容**
- 保持所有代码、组件名称和技术元素不变

翻译规则：
1. 将所有文本内容自然流畅地翻译成 $language_name
2. 保持所有 Markdown 格式不变（标题 ##、列表 -、加粗 **、链接 [] 等）
3. 保持所有 HTML 标签不变（如 <iframe>、<div> 等）
4. 保持所有 URL 不变
5. 保持所有 YouTube 视频 ID 不变
6. 保持相同的文章结构和长度
7. **不要翻译 MDX 组件标签及其属性** - 保持所有组件名称、props 和属性名称为英文：
   - 组件名称：<Section>、<Callout>、<Card>、<CardGrid>、<Checklist>、<FAQ>、<Steps>、<Step>、<YouTubeEmbed>
   - Prop 名称：icon、title、type、id、items、num、videoId、cols、question、answer
   - 图标名称：Map、Swords、Trophy、Target、Shield、Sparkles
   - 只翻译这些组件内部的文本内容
   - 示例：<Section icon={{Map}} title="Chapter Title"> → title 的值应该被翻译，但 "Section"、"icon"、"Map" 保持英文

## 关键：MDX/JSX 标签格式规则

**重要：开始标签和闭合标签必须在独立的行上**

1. **永远不要在内容行末尾放置闭合标签**
   - ❌ 错误：`| Table | Content </Section>`（标签在表格行中）
   - ❌ 错误：`<Section>Content</Section>`（全部在同一行）
   - ✅ 正确：
     ```
     <Section icon={{Map}} title="Title">
     Content here
     </Section>
     ```

2. **⚠️ 表格专用规则（极其重要）：**
   - 表格必须以正确的行闭合结束：`|`
   - **表格后必须添加空行**
   - **在空行后的独立行上放置 </Section> 标签**
   - 这是最常见的错误！必须严格遵守！
   - ❌ 错误示例：
     ```
     | Column1 | Column2 </Section>          ← 错误！标签在表格行末尾
     ```
     或者
     ```
     | Column1 | Column2 |                   ← 表格最后一行
                                               ← 缺少空行和闭合标签！文件结束了！
     ```
   - ✅ 正确示例：
     ```
     | Column1 | Column2 |                   ← 表格最后一行

     </Section>                               ← 必须在独立的行上
     ```

3. **标签完整性检查清单 - 输出前验证：**
   - ✓ 每个 `<Section>` 都有匹配的 `</Section>` 在独立的行上
   - ✓ 每个 `<Callout>` 都有匹配的 `</Callout>` 在独立的行上
   - ✓ 每个 `<Card>` 都有匹配的 `</Card>` 在独立的行上
   - ✓ 没有闭合标签被附加到表格行或其他内容行
   - ✓ 表格单元格使用 markdown 语法（`**bold**`）而不是 HTML（`<strong>bold</strong>`）
   - ✓ 所有开始标签和闭合标签都在独立的行上

FRONTMATTER 翻译要求：
**关键：使用 JavaScript export 格式，不是 YAML frontmatter**
- 输出格式：`export const metadata = { ... }`
- **必须翻译的字段：**
  - title：翻译成 $language_name
  - description：翻译成 $language_name
  - keywords：翻译成 $language_name（作为单个字符串）
  - category：翻译成 $language_name（例如："Guide" → "Guía" (ES), "指南" (ZH)）
  - author：翻译成 $language_name（例如："Wiki Team" → "Equipo de Wiki" (ES)）
- **保持不变的字段：**
  - date：保持不变
  - image：保持不变（URL 不翻译）
  - ⚠️ canonical：不要添加或修改，如果原文没有则不添加，如果原文有则保持原样
- 游戏名称：引用游戏时使用 "$game_name"
- 不要使用 YAML frontmatter（--- 格式）

正确输出格式示例（西班牙语）：
```
import { Map, Swords, Trophy } from 'lucide-react'
import { Callout } from '@/components/mdx/Callout'

export const metadata = {
  title: "Entrenamiento Cooperativo: Domina las Mejores Estadísticas",
  description: "Desbloquea mejoras masivas de CP en Solo Leveling: Arise",
  category: "Guía",
  author: "Equipo de Wiki de Solo Leveling: Arise",
  date: "2026-01-25",
  image: "https://example.com/image.png",
  keywords: "entrenamiento, cooperativo, estadísticas"
}

<Callout type="info" title="快速指南">
翻译的内容在这里...
</Callout>
```

错误输出（不要这样做）：
```
export const metadata = {
  title: "翻译后的标题"
}
```  ← 不要添加这个闭合代码块标记！

<Callout type="info">
```

目标语言：$language_name ($lang_code)
游戏名称（$language_name）：$game_name

原始英文内容：

$content

## ⚠️ 关键输出指令 - 严格遵守：

**输出格式要求：**
1. ⛔️ 第一行直接开始 import 语句 - 不要添加任何 ``` 标记
2. 复制所有 import 语句（完全一致）
3. 空一行
4. 输出 metadata export 语句（带翻译的字段）
5. 空一行
6. 直接输出 MDX 内容 - 不要添加 ``` 标记
7. 不要添加任何解释或注释
8. 不要在开头、中间或结尾添加 ``` 或 ```mdx 标记

**❌ 绝对禁止的错误输出：**
```
```                           ← 不要这样开头！
import { Map } from '...'
```                           ← 不要这样结尾！
<Section>内容</Section>
```

**✅ 正确的输出格式：**
import { Map } from '...'     ← 直接开始，无 ``` 标记

export const metadata = { ... }

<Section>内容</Section>        ← 直接结束，无 ``` 标记
