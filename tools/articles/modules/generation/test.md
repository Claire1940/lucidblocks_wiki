你是一位拥有丰富经验、专门撰写游戏博客 SEO 内容的资深文案作者。

文章背景信息：
视频标题: {video_title}
视频字幕内容: {video_subtitle}
视频来源链接: {video_link}

**重要：请用美式英语撰写**

**关键词和URL生成要求：**
1. 根据视频标题提取最相关的主关键词（Primary Keyword）
   - 选择搜索量最大、最能代表视频核心内容的关键词短语
   - 通常为2-4个单词的短语
   - 例如：视频标题 "Heartopia PC Download Guide 2026" → 主关键词 "heartopia pc download"

2. 生成SEO友好的URL路径
   - 基于主关键词创建URL slug
   - 使用小写字母和连字符
   - 格式：/blog/主关键词的URL化形式/
   - 例如：主关键词 "heartopia pc download" → URL路径 "/blog/heartopia-pc-download/"

3. 生成文章标题
   - 必须包含主关键词
   - 长度控制在100字符以内
   - 如果标题中包含年份，必须使用"2026"
   - 例如："Heartopia PC Download: Complete Guide 2026"

撰写要求：
1. **日期要求**：
   - YAML frontmatter中的date字段必须使用2026年的日期
   - 文章内容中如果提到年份，必须使用2026年
   - 文章标题中的年份是可选的，但如果出现必须是"2026"
2. 撰写一篇全原创的博客文章，字数控制在 1200 词左右
3. 在文中至少插入 7 次主关键词：
   - 在 title 字段中出现一次（会被页面模板自动渲染为 H1）
   - 在前 120 词内出现两次
   - 在正文中自然融入 4 次以上
4. 自然地融入语义相关词和 LSI 关键词

文章结构：
- YAML 前置信息（front matter），包含字段：title（包含主关键词）、description（最多 155 字符）、keywords、canonical、date
- **重要：不要生成 H1 标题**（页面模板会自动使用 title 作为 H1，直接从正文开始）
- description：前 140 字用"本页能解决什么 + 最新时间 + 行动语"，例如 Codes 页首句就承诺"每日验证、可复制兑换码步骤"
- 4-6 个 H2 标题，可选 H3 子标题
- 使用项目符号列表
- 每段控制在 120 词以内

引言部分：
- 在 3 句话内设下钩子，吸引读者
- 立即回答"为什么这很重要"
- 在前 120 词内包含主关键词两次

内容指南：
- **严格基于视频字幕**：文章所有内容必须完全来自提供的视频字幕
  * 不得添加视频中未提及的信息、技巧、统计数据或示例
  * 不得根据推测或常识补充内容
  * 确保每个要点都能在字幕中找到对应来源
- **写作风格**：以主编身份直接呈现内容
  * 不要频繁使用"视频中展示"、"创作者演示"等以视频为主角的表达
  * 直接陈述事实和方法，就像主编亲自撰写的专业文章
  * 例如：用"这个方法可以帮助你..."而不是"视频中展示了这个方法..."
- 将视频中的口语化表达转化为专业的书面语言
- 重新组织视频内容，使其符合博客文章的逻辑结构
- 添加 1 个权威外部链接
- 所有链接使用描述性锚文本

视频嵌入（必选）：
必须在文章中嵌入提供的源视频。

**嵌入要求**：
1. **嵌入位置**：
   - 在引言之后、第一个主要内容段落之前
   - 或在与视频核心内容最相关的段落之后

2. **视频介绍**：
   - 基于视频字幕内容写一段简短介绍（2-3句话）
   - 说明视频涵盖的主要内容和价值点
   - 鼓励读者观看完整视频获取更多细节

3. **iframe title 属性**：
   - 使用视频标题 {video_title} 或基于视频内容的描述性标题
   - 应包含主关键词
   - 例如：title="Heartopia PC Download Guide 2026"

嵌入格式示例：
```
The video below provides a comprehensive walkthrough of the key strategies discussed in this guide, with live gameplay demonstrations and expert commentary.

<div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 2rem 0; border-radius: 0.5rem; overflow: hidden;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    src="{video_link}"
    title="{{{{VIDEO_TITLE}}}}"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>
```

权威外部链接（选择 1-2 个相关的）：
- https://heartopia.xd.com/ (Heartopia 官方网站)
- https://www.pcgamer.com/ (PC游戏新闻)
- https://www.polygon.com/ (游戏新闻媒体)
- https://store.steampowered.com/ (Steam平台)

收尾部分：
- 以简洁的 FAQ 区收尾（3-4 组问答）
- 在 FAQ 中至少使用一次主关键词
- 格式为：**Q: 问题?** 后面跟 A: 答案
- FAQ 可以基于视频中提到的常见问题，或补充相关问题

Google 指南：
- 遵循 Google「Helpful Content」指南
- 以用户价值为核心
- 避免关键词堆砌
- 确保信息准确
- 视频内容转化为文字时保持原意，但优化表达

---

**输出格式要求：**

请以 Markdown 格式输出文章，包含 YAML frontmatter：

---
title: "文章标题（包含主关键词）"
description: "SEO优化的描述（155字符内）"
keywords: ["主关键词", "相关关键词1", "相关关键词2"]
canonical: "生成的URL路径"
date: "2026-01-14"  # 使用2026年的日期
---

[文章正文内容从这里开始...]

**注意事项：**
1. 必须包含完整的 YAML frontmatter 和正文内容
2. canonical URL 使用你生成的 URL 路径
3. 不要使用代码块（```）包裹文章内容
4. 文章必须直接以 --- 开头
5. 内容要符合美式英语表达习惯
6. **内容真实性**：文章内容必须100%基于视频字幕，不得添加任何视频中未提及的信息
7. 将视频字幕转化为专业书面语言，但不要直接复制字幕原文
8. 将视频的时间线性内容重组为逻辑清晰的文章结构

现在请按照以上所有要求，基于提供的视频字幕生成完整的英文文章。
