## （4）鼠标滑动时“箭头位置特效”（不改系统箭头，只加“跟随光晕 + 轻粒子”）

目标：用户移动鼠标时，在箭头位置出现 **柔和“心动光晕”**，并带一点点“泡泡/闪点尾迹”（符合 Heartopia 的轻松氛围）。

把下面这段放到 Next.js（App Router）里，例如 `components/CursorGlow.tsx`，然后在 `layout.tsx` 引入一次即可。

```tsx
'use client';

import { useEffect, useRef } from 'react';

export default function CursorGlow() {
  const glowRef = useRef<HTMLDivElement | null>(null);
  const dotARef = useRef<HTMLDivElement | null>(null);
  const dotBRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const glow = glowRef.current!;
    const dotA = dotARef.current!;
    const dotB = dotBRef.current!;

    let mx = 0, my = 0;     // mouse
    let gx = 0, gy = 0;     // glow (smoothed)
    let raf = 0;

    const onMove = (e: MouseEvent) => {
      mx = e.clientX;
      my = e.clientY;
    };

    const tick = () => {
      // smooth follow (easing)
      gx += (mx - gx) * 0.18;
      gy += (my - gy) * 0.18;

      // place glow under cursor arrow tip area
      const x = gx;
      const y = gy;

      glow.style.transform = `translate3d(${x - 18}px, ${y - 18}px, 0)`;
      dotA.style.transform = `translate3d(${x + 10}px, ${y + 6}px, 0)`;
      dotB.style.transform = `translate3d(${x - 22}px, ${y + 14}px, 0)`;

      raf = requestAnimationFrame(tick);
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    raf = requestAnimationFrame(tick);

    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      {/* main glow */}
      <div
        ref={glowRef}
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          width: 36,
          height: 36,
          borderRadius: 9999,
          pointerEvents: 'none',
          zIndex: 9999,
          background: 'radial-gradient(circle, rgba(255,111,168,0.55) 0%, rgba(122,92,250,0.18) 45%, rgba(0,0,0,0) 70%)',
          filter: 'blur(0.3px)',
          mixBlendMode: 'screen',
          opacity: 0.95,
          transition: 'opacity 120ms ease',
        }}
      />
      {/* tiny sparkle dots */}
      <div
        ref={dotARef}
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          width: 6,
          height: 6,
          borderRadius: 9999,
          pointerEvents: 'none',
          zIndex: 9999,
          background: 'rgba(255,255,255,0.75)',
          filter: 'blur(0.2px)',
          opacity: 0.65,
        }}
      />
      <div
        ref={dotBRef}
        style={{
          position: 'fixed',
          left: 0,
          top: 0,
          width: 4,
          height: 4,
          borderRadius: 9999,
          pointerEvents: 'none',
          zIndex: 9999,
          background: 'rgba(255,255,255,0.6)',
          opacity: 0.45,
        }}
      />
    </>
  );
}
```

---

## （5）适合 heartopiagame.com 的风格 UI JSON（保证对比度不翻车）

思路：用 **深色耐看底（和备选 B 背景一致）+ 粉色心动主色 + 薰衣草辅色**。正文统一高亮白字，弱文本用偏灰白；按钮/卡片用半透明“玻璃感”，但不走低对比度路线。

```json
{
  "brand": {
    "name": "HeartopiaGame",
    "tagline": "Cozy tools, clean guides, and quick rewards for Heartopia."
  },
  "theme": {
    "mode": "dark",
    "background": {
      "type": "gradient",
      "value": "linear-gradient(135deg, #0B132B 0%, #171A3D 40%, #2A1B4A 70%, #2B2438 100%)"
    },
    "colors": {
      "textPrimary": "#F5F7FF",
      "textSecondary": "#C9D1F2",
      "muted": "#8C95BF",
      "card": "rgba(255,255,255,0.06)",
      "cardBorder": "rgba(255,255,255,0.10)",
      "brandPink": "#FF6FA8",
      "brandLavender": "#7A5CFA",
      "brandCyan": "#6EC9FF",
      "success": "#3EE08F",
      "warning": "#FFC14A",
      "danger": "#FF5A6B",
      "focusRing": "rgba(110,201,255,0.55)"
    },
    "typography": {
      "fontFamily": "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
      "h1": { "size": 40, "weight": 800, "lineHeight": 1.15, "color": "#F5F7FF" },
      "h2": { "size": 28, "weight": 750, "lineHeight": 1.2, "color": "#F5F7FF" },
      "body": { "size": 16, "weight": 450, "lineHeight": 1.6, "color": "#C9D1F2" },
      "small": { "size": 13, "weight": 450, "lineHeight": 1.5, "color": "#8C95BF" }
    },
    "radius": { "card": 20, "button": 16, "pill": 999 },
    "shadow": {
      "card": "0 10px 30px rgba(0,0,0,0.35)",
      "glowPink": "0 0 24px rgba(255,111,168,0.28)",
      "glowLavender": "0 0 28px rgba(122,92,250,0.24)"
    }
  },
  "layout": {
    "maxWidth": 1120,
    "gutter": 20,
    "sections": [
      {
        "id": "hero",
        "type": "hero",
        "headline": "Heartopia",
        "subheadline": "Download fast, redeem rewards, and track official updates — all in one cozy hub.",
        "primaryCta": { "label": "Download", "href": "/download" },
        "secondaryCta": { "label": "Redeem Codes", "href": "#codes" },
        "badges": ["Official links inside", "No clutter", "Readable at night"]
      },
      {
        "id": "download",
        "type": "ctaCard",
        "title": "One-click Download Portal",
        "copy": "Choose your platform and jump into Heartopia Town in seconds.",
        "buttons": [
          { "label": "PC / Steam", "href": "/download#pc" },
          { "label": "Android", "href": "/download#android" },
          { "label": "iOS", "href": "/download#ios" }
        ]
      },
      {
        "id": "updates",
        "type": "featureCard",
        "title": "Official Update Radar",
        "copy": "See the latest announcements, events, and important changes at a glance.",
        "ui": { "variant": "timeline+chips", "accent": "brandCyan", "icon": "radar" }
      },
      {
        "id": "codes",
        "type": "toolCard",
        "title": "Code Finder",
        "copy": "Filter rewards you actually want (Crystals / Stars / Gold) and copy in one tap.",
        "ui": { "variant": "filters+list", "accent": "brandPink", "icon": "ticket" }
      },
      {
        "id": "official-media",
        "type": "linkGrid",
        "title": "Official Media & Screenshots",
        "copy": "Browse official pages for screenshots, news, and verified info — no shady reuploads.",
        "links": [
          { "label": "Official Website", "href": "https://heartopia.xd.com/us/" },
          { "label": "Official News", "href": "https://heartopia.xd.com/us/news" },
          { "label": "Steam Store", "href": "https://store.steampowered.com/app/4025700/Heartopia/" },
          { "label": "Google Play", "href": "https://play.google.com/store/apps/details?id=com.xd.xdtglobal.gp" }
        ]
      },
      {
        "id": "faq",
        "type": "faq",
        "title": "FAQ",
        "copy": "Quick answers for the most common Heartopia questions — faster than scrolling chat logs.",
        "items": [
          { "q": "Where do I redeem codes?", "a": "Open the in-game menu/settings and find the Redeem Code entry, then claim rewards from your mailbox." },
          { "q": "Which platform should I start on?", "a": "Pick the platform you’ll play daily. Your goal is consistency — cozy games reward routine." }
        ]
      }
    ]
  }
}
```

---

### 最后补一句“落地建议”（不增加新需求）

首页把“下载”按钮做成 **新标签打开**，并在下载按钮旁边放一句：**“下载后先来领兑换码/看官方更新（不浪费 1 分钟）”**，用锚点直达你站内的 Codes & Updates 区块——这就是把“下载即流失”变成“下载后顺手多点两下”的关键。

如果你希望我把这个 UI JSON 直接转成你 Next.js 的组件结构（`sections.map` 渲染 + Tailwind 变量），我可以按你现在的目录结构给你一份可直接粘贴的实现。

[1]: https://heartopia.xd.com/us/?utm_source=chatgpt.com "Heartopia | A Relaxing Slow-life Simulation"
[2]: https://heartopia.xd.com/us/news?utm_source=chatgpt.com "News"
[3]: https://store.steampowered.com/app/4025700/Heartopia/?utm_source=chatgpt.com "Heartopia on Steam"
[4]: https://play.google.com/store/apps/details?hl=en_US&id=com.xd.xdtglobal.gp&utm_source=chatgpt.com "Heartopia - Apps on Google Play"
[5]: https://x.com/MyHeartopia?lang=en&utm_source=chatgpt.com "Heartopia (@MyHeartopia) / Posts / X"
[6]: https://www.gamespress.com/Chill-Vibes-and-a-Cosy-Small-Town-Life-First-Look-At-He-XD-Network-Inc?utm_source=chatgpt.com "\"Chill Vibes and a Cosy Small Town Life: First Look At ..."
