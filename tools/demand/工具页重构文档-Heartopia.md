# Heartopia 工具页重构文档

## 目标

创建两个独立工具页并在首页复刻功能模块：
1. Code Finder（兑换码筛选器）
2. Official Update Radar（官方更新雷达）

---

## 数据需求

### 1. heartopia-codes.json

**数据源**:
- 主要：https://heartopia.gg/codes
- 交叉验证：https://www.pcgamesn.com/heartopia/codes

**JSON 格式**:
```json
{
  "fetchedAt": "2026-01-13T00:00:00Z",
  "primarySource": "https://heartopia.gg/codes",
  "codes": [
    {
      "code": "dcthx4u",
      "rewards": [{"item": "Wishing Star", "qty": 10}],
      "expiresAt": "2026-06-30",
      "category": "Discord 300K",
      "sources": ["heartopia.gg", "pcgamesn"],
      "sourceUrls": ["https://heartopia.gg/codes", "https://www.pcgamesn.com/heartopia/codes"],
      "verified": true
    }
  ]
}
```

### 2. heartopia-news.json

**数据源**:
- Steam News API: `https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=4025700&count=50&maxlength=300&format=json`

**JSON 格式**:
```json
{
  "appnews": {
    "appid": 4025700,
    "newsitems": [
      {
        "gid": "512979846355223182",
        "title": "Update Title",
        "url": "https://store.steampowered.com/news/...",
        "is_external_url": false,
        "author": "",
        "contents": "Update content...",
        "feedlabel": "Community Announcements",
        "date": 1736740800,
        "feedname": "steam_community_announcements"
      }
    ],
    "count": 50
  }
}
```

---

## 工具页设计

### Tool 1: Code Finder (/tools/code-finder)

**功能**:
- 展示所有活跃兑换码
- 按奖励类型筛选（Moonlight Crystals, Wishing Stars, Repair Kits, Gold, Materials）
- 按到期时间排序
- 一键复制功能
- 显示验证状态

**UI 组件**:
- 筛选器（Filter Bar）
- 代码卡片网格（Code Cards Grid）
- 复制按钮（Copy Button）
- 到期提醒标签（Expiry Badge）

### Tool 2: Official Update Radar (/tools/update-radar)

**功能**:
- 展示最近 Steam 更新/公告
- 按类型筛选（Maintenance, Event, Reward, Update）
- 时间轴显示
- 关键词标签
- 更新统计

**UI 组件**:
- 统计卡片（Stats Cards）
- 更新时间轴（Timeline）
- 关键词标签云（Keyword Tags）
- 最新公告卡片（Latest Update Card）

---

## 多语言支持

所有文案在 `src/messages/en.json` 中管理：

```json
{
  "codeFinder": {
    "title": "Code Finder",
    "subtitle": "Find active Heartopia codes",
    "description": "Browse all active codes with reward filters and expiration dates.",
    "filterByReward": "Filter by Reward",
    "allRewards": "All Rewards",
    "copyCode": "Copy Code",
    "copied": "Copied!",
    "expiresOn": "Expires on",
    "neverExpires": "Never expires",
    "verified": "Verified",
    "codesFound": "codes found",
    "searchPlaceholder": "Search codes or rewards..."
  },
  "updateRadar": {
    "title": "Official Update Radar",
    "subtitle": "Track game updates in real-time",
    "description": "See latest updates, events, and announcements from Steam.",
    "daysSinceUpdate": "Days Since Update",
    "updatesLast30Days": "Updates (30 Days)",
    "latestUpdate": "Latest Update",
    "readMore": "Read More",
    "viewOnSteam": "View on Steam",
    "filterByType": "Filter by Type",
    "allUpdates": "All Updates",
    "maintenance": "Maintenance",
    "event": "Event",
    "reward": "Reward",
    "update": "Update"
  }
}
```

---

## 首页复刻功能模块

在首页 `/tools` section 之后添加：

### Code Finder Preview Section
- 显示最新 6 个兑换码
- 带有 "View All Codes" 按钮跳转到完整工具页
- 使用相同的 heartopia-codes.json 数据

---

## 实施步骤

1. ✅ 阅读功能需求.md
2. ⏳ 网络搜索并创建数据 JSON 文件
3. ⏳ 删除历史工具页
4. ⏳ 创建 Code Finder 工具页
5. ⏳ 创建 Update Radar 工具页
6. ⏳ 更新 src/messages/en.json
7. ⏳ 在首页复刻 Code Finder 功能
8. ⏳ 测试工具页
9. ⏳ 测试首页功能模块

---

## 删除的历史页面

需要删除的 Pathologic 3 工具页：
- `/tools/patch-pulse/`
- `/tools/update-tracker/`
- `/tools/export-heatmap/`
- `/tools/dp-calculator/`
