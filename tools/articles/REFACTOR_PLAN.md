# YouTube视频自动嵌入功能 - 重构方案（简化版）

## 目标
在文章自动生成流程中，将YouTube视频列表传给大模型，由大模型根据文章内容智能选择并使用HTML模板嵌入视频。

## 核心设计思路

**将视频嵌入的所有决策权交给大模型：**
- ✅ 在prompt中定义HTML模板
- ✅ 只传视频ID和标题的简单列表
- ✅ 由大模型选择视频并填充模板生成HTML
- ✅ 代码极简，prompt token消耗最少

**优势：**
1. **代码最简** - 无需生成HTML，只需解析CSV
2. **Token最少** - 不传完整HTML，只传必要信息
3. **灵活性高** - 大模型可以根据需要调整HTML格式
4. **维护简单** - 模板在prompt中，易于调整

---

## 架构设计

### 1. 新增模块：youtube_manager.py

**位置**: `tools/articles/modules/youtube_manager.py`

**功能**:
- 读取 `youtube_data.csv` 文件
- 解析所有视频的ID和标题
- 格式化为简单的列表（ID + 标题）
- 过滤VR游戏视频

**核心方法**:
```python
class YouTubeManager:
    def __init__(self, csv_path: str)
    def load_videos(self) -> bool
    def format_videos_list(self) -> str
    def get_stats(self) -> Dict
    def print_stats(self)
```

**数据流**:
```
youtube_data.csv
    ↓ 读取解析
video_id + title
    ↓ 格式化
简单文本列表
    ↓ 传入prompt
GPT-4o
    ↓ 选择 + 填充模板
完整的HTML iframe
```

---

### 2. 修改文件：prompt-template.txt

**位置**: `tools/articles/prompt-template.txt`

**修改内容**: 在内部链接部分之后添加视频嵌入指令和HTML模板

**新增的内容** (在第39行附近):

```text
内部链接（选择 2 个相关的）：
{internal_links}

YouTube视频嵌入（可选）：
如果下面的视频列表中有与本文高度相关的视频，请选择1个嵌入到文章中。

嵌入位置建议：
- 推荐位置：引言段落之后，第一个H2部分之前
- 也可以根据文章内容选择其他合适位置
- 如果没有特别相关的视频，可以不嵌入

HTML模板（请将选择的视频ID和标题填入）：
<div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 2rem 0; border-radius: 0.5rem; overflow: hidden;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    src="https://www.youtube.com/embed/{{VIDEO_ID}}"
    title="{{VIDEO_TITLE}}"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>

可用的YouTube视频列表：
{youtube_videos}

权威外部的具体链接（选择 2 个相关的）：
- https://www.roblox.com/ (Roblox 官方平台)
```

---

### 3. 修改文件：generate-articles.py

**位置**: `tools/articles/generate-articles.py`

#### 修改点1: 导入新模块 (第23行附近)

```python
from excel_parser import ExcelParser
from api_client import APIClient
from file_writer import FileWriter
from internal_links import InternalLinksManager
from youtube_manager import YouTubeManager  # 新增
```

#### 修改点2: 初始化属性 (第41行附近)

```python
class ArticleGenerator:
    def __init__(self, config_path: str = 'tools/articles/config.json', priority_range: tuple = None):
        self.config_path = config_path
        self.priority_range = priority_range
        self.config = None
        self.excel_parser = None
        self.api_client = None
        self.file_writer = None
        self.links_manager = None
        self.youtube_manager = None  # 新增
        self.prompt_template = None
```

#### 修改点3: 初始化YouTube管理器 (第107行附近)

```python
def initialize_modules(self) -> bool:
    try:
        # ... 现有代码 ...

        # Initialize internal links manager
        self.links_manager = InternalLinksManager(
            self.config['internal_links'],
            self.config['site_domain']
        )
        print("✅ Internal links manager initialized")

        # 新增: Initialize YouTube manager
        self.youtube_manager = YouTubeManager(
            self.config['youtube_csv']  # 从config读取CSV路径
        )
        if not self.youtube_manager.load_videos():
            print("⚠️  Warning: Failed to load YouTube videos")
        else:
            print("✅ YouTube manager initialized")

        return True
```

#### 修改点4: 修改build_prompt方法 (第115行附近)

```python
def build_prompt(self, article: Dict) -> str:
    """
    Build prompt for article generation.
    """
    # Select internal links for this article
    internal_links = self.links_manager.select_links_for_article(
        article['url_path'],
        num_links=2
    )
    formatted_links = self.links_manager.format_links_for_prompt(internal_links)

    # 新增: Get YouTube videos list
    youtube_videos = self.youtube_manager.format_videos_list()

    # Get current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Build prompt from template
    prompt = self.prompt_template.format(
        url_path=article['url_path'],
        article_title=article['title'],
        keyword=article['keyword'],
        reference_link=article['reference'] or 'No reference provided',
        internal_links=formatted_links,
        youtube_videos=youtube_videos,  # 新增
        current_date=current_date
    )

    return prompt
```

#### 修改点5: 添加统计输出 (第222行附近)

```python
# Print statistics
print("\n" + "=" * 60)
print("📊 GENERATION COMPLETE")
print("=" * 60)

self.api_client.print_stats()
self.file_writer.print_stats()
self.links_manager.print_stats()
self.youtube_manager.print_stats()  # 新增
```

---

## 实现代码

### youtube_manager.py 完整实现

**文件位置**: `tools/articles/modules/youtube_manager.py`

```python
"""
YouTube Manager Module
Manages YouTube video data for article generation.
Provides simple video list (ID + title) to LLM.
"""
import csv
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class YouTubeManager:
    def __init__(self, csv_path: str):
        """
        Initialize the YouTube manager.

        Args:
            csv_path: Path to youtube_data.csv file
        """
        self.csv_path = csv_path
        self.videos = []
        self.stats = {
            'total_videos': 0,
            'filtered_videos': 0
        }

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.

        Args:
            url: YouTube URL

        Returns:
            Video ID or None
        """
        try:
            parsed = urlparse(url)
            if 'youtube.com' in parsed.netloc:
                return parse_qs(parsed.query).get('v', [None])[0]
            elif 'youtu.be' in parsed.netloc:
                return parsed.path.strip('/')
        except:
            pass
        return None

    def load_videos(self) -> bool:
        """
        Load all videos from CSV file.
        Filters out VR game videos (different from Roblox version).

        Returns:
            bool: True if successful
        """
        try:
            total_count = 0
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    total_count += 1
                    video_id = self.extract_video_id(row['Video URL'])
                    if video_id:
                        title = row['Title']

                        # 过滤VR游戏视频（与Roblox版本不同）
                        if 'VR' in title or 'friendslop' in title.lower():
                            continue

                        self.videos.append({
                            'id': video_id,
                            'title': title
                        })

            self.stats['total_videos'] = total_count
            self.stats['filtered_videos'] = len(self.videos)
            print(f"✅ Loaded {len(self.videos)} YouTube videos (filtered {total_count - len(self.videos)} VR videos)")
            return True

        except Exception as e:
            print(f"❌ Error loading YouTube videos: {str(e)}")
            return False

    def format_videos_list(self) -> str:
        """
        Format video list as simple text for LLM.
        Only includes video ID and title.

        Returns:
            Formatted string containing all videos
        """
        if not self.videos:
            return "（暂无可用的YouTube视频）"

        formatted_lines = []
        for idx, video in enumerate(self.videos, 1):
            formatted_lines.append(f"{idx}. ID: {video['id']} | Title: {video['title']}")

        return "\n".join(formatted_lines)

    def get_stats(self) -> Dict:
        """Get statistics."""
        return self.stats.copy()

    def print_stats(self):
        """Print formatted statistics."""
        stats = self.get_stats()

        print("\n" + "=" * 60)
        print("🎬 YOUTUBE VIDEO STATISTICS")
        print("=" * 60)
        print(f"Total Videos in CSV:  {stats['total_videos']}")
        print(f"Available for LLM:    {stats['filtered_videos']}")
        print("\nℹ️  Videos sent as ID+Title list, LLM fills HTML template")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test the YouTube manager
    manager = YouTubeManager("tools/articles/youtube_data.csv")
    if manager.load_videos():
        print(f"\n✅ Successfully loaded {len(manager.videos)} videos\n")

        # Test formatting
        print("=" * 60)
        print("📝 Formatted video list for LLM:")
        print("=" * 60)
        print(manager.format_videos_list())
        print("=" * 60)
```

---

## 文件修改清单

### 新建文件（1个）

1. **`tools/articles/modules/youtube_manager.py`**
   - 完整的YouTubeManager类实现
   - 约100行代码

### 修改文件（2个）

1. **`tools/articles/generate-articles.py`**
   - 5处修改点（已标注具体行号）
   - 总共增加约15行代码

2. **`tools/articles/prompt-template.txt`**
   - 1处修改点（第39行附近）
   - 增加HTML模板定义和视频列表占位符

3. **`tools/articles/config.json`**
   - 新增 `youtube_csv` 配置项
   - 值为 `"tools/articles/youtube_data.csv"`

---

## 测试计划

### 阶段1: 单元测试

```bash
# 测试YouTube管理器
python tools/articles/modules/youtube_manager.py

# 预期输出:
# ✅ Loaded 17 YouTube videos (filtered 4 VR videos)
#
# 📝 Formatted video list for LLM:
# 1. ID: CgKwbYnrtyA | Title: Bring back Food, BECOME RICH...
# 2. ID: HeCL0_26jF4 | Title: DEADLY DELIVERY UPDATE!...
# ... (共17个)
```

### 阶段2: 集成测试

```bash
# 测试模式：生成2篇文章
python tools/articles/generate-articles.py --test

# 检查点:
# 1. ✅ YouTube管理器成功初始化
# 2. ✅ Prompt中包含视频列表和HTML模板
# 3. ✅ 生成的MDX文件包含正确的视频iframe
# 4. ✅ 视频ID和标题正确填充到模板中
```

### 阶段3: 验证生成的文章

检查生成的MDX文件，确保：
- HTML格式正确（与手动嵌入的一致）
- 视频选择合理（与文章内容相关）
- 视频位置合适（通常在引言后）

---

## 示例：传给LLM的内容

### Prompt中的视频部分

```text
YouTube视频嵌入（可选）：
如果下面的视频列表中有与本文高度相关的视频，请选择1个嵌入到文章中。

嵌入位置建议：
- 推荐位置：引言段落之后，第一个H2部分之前
- 也可以根据文章内容选择其他合适位置
- 如果没有特别相关的视频，可以不嵌入

HTML模板（请将选择的视频ID和标题填入）：
<div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 2rem 0; border-radius: 0.5rem; overflow: hidden;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    src="https://www.youtube.com/embed/{{VIDEO_ID}}"
    title="{{VIDEO_TITLE}}"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>

可用的YouTube视频列表：
1. ID: CgKwbYnrtyA | Title: Bring back Food, BECOME RICH.. (Roblox Total Chaos)
2. ID: HeCL0_26jF4 | Title: DEADLY DELIVERY UPDATE! (Codes, Veteran Showcase & MORE) Roblox
3. ID: hwdT4xw_kN0 | Title: Roblox Total Chaos Is SUPER FUN...
4. ID: L093XqyLGrw | Title: DEADLY DELIVERY GUIDE! (Tips & TRICKS) Roblox
5. ID: ZHt6RUZjF3c | Title: ROBLOX Total Chaos is amazing
6. ID: NLseIhDXsRs | Title: ✅ DEADLY DELIVERY CODES ROBLOX – All New Working Codes!
7. ID: mvh_QFTpa1w | Title: Total Chaos - All Entities Showcase - Roblox
8. ID: wUJlb0N_BMg | Title: Total Chaos: Hello, your package has arrived?!
9. ID: tUDwvkDWFRc | Title: ALL NEW CODES in Total Chaos Roblox!
10. ID: q7Db7jvrrUg | Title: Total Chaos Roblox Tips And Guide For Begginers
11. ID: F3c7g92M5F8 | Title: Total Chaos - Release Date Trailer
12. ID: PC_M3W4gPkA | Title: Roblox Total Chaos: Monsters, Clones & Rare Eggs!
13. ID: 5i8mAMTCAr0 | Title: We Became BILLIONAIRES in Roblox Total Chaos!
14. ID: rRW_gEW--dg | Title: *NEW* ALL WORKING CODES FOR DEADLY DELIVERY IN 2025!
15. ID: SiRsywxsUls | Title: 🔴LIVE | Total Chaos NEW Character & Monster
16. ID: A3NG4tyTzsU | Title: Total Chaos - Full Game Playthrough & Ending - Roblox
```

### LLM生成的示例（Codes文章）

对于 `/codes/deadly-delivery-codes/` 文章，LLM可能会：

1. **分析文章内容**：关于游戏代码
2. **选择视频**：ID: NLseIhDXsRs 或 tUDwvkDWFRc（关于codes的视频）
3. **填充模板**：
```html
<div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 2rem 0; border-radius: 0.5rem; overflow: hidden;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
    src="https://www.youtube.com/embed/NLseIhDXsRs"
    title="✅ DEADLY DELIVERY CODES ROBLOX – All New Working Codes!"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen
  ></iframe>
</div>
```

---

## 优势分析

### 与之前方案的对比

| 特性 | 代码匹配方案 | 预生成HTML方案 | **当前方案** ⭐ |
|------|------------|--------------|--------------|
| 代码复杂度 | 高（匹配算法） | 中（生成HTML） | **极低（只解析）** |
| Prompt Token | 低 | 高（完整HTML） | **最低（仅ID+标题）** |
| 灵活性 | 低（规则固定） | 中 | **最高（LLM决策）** |
| 维护成本 | 高（维护规则） | 中 | **最低** |
| LLM自主性 | 无 | 选择视频 | **完全自主** |

### 核心优势

1. ✅ **代码最简**: 只需解析CSV，无需匹配算法或HTML生成
2. ✅ **Token最少**: 传递最精简的信息（ID + 标题）
3. ✅ **完全灵活**: LLM可以根据需要调整HTML（虽然有模板）
4. ✅ **易于维护**: 模板在prompt中，修改无需改代码
5. ✅ **智能决策**: LLM理解视频标题语义，选择更准确

### Token消耗对比

假设每篇文章：

- **预生成HTML方案**: ~2000 tokens (17个完整iframe)
- **当前方案**: ~500 tokens (17个ID+标题行)
- **节省**: 约75%的prompt tokens

对于100篇文章：
- 节省tokens: ~150,000
- 节省成本: 显著降低API费用

---

## 回滚方案

如果需要禁用视频嵌入功能：

### 方案A: 修改prompt（推荐）

在 `prompt-template.txt` 中删除或注释掉视频部分：
```diff
- YouTube视频嵌入（可选）：
- ... (整个视频部分)
- {youtube_videos}
```

### 方案B: 传递空列表

在 `generate-articles.py` 中：
```python
# youtube_videos = self.youtube_manager.format_videos_list()
youtube_videos = "（本文不嵌入视频）"
```

### 方案C: 不初始化管理器

注释掉YouTubeManager的初始化：
```python
# self.youtube_manager = YouTubeManager(...)
# ...
youtube_videos = ""
```

---

## 总结

### 核心思路
**"最简代码 + LLM智能填充"** 策略：
- 代码只负责数据提取和格式化
- HTML模板定义在prompt中
- LLM负责选择和填充

### 工作流程
```
CSV文件
  ↓ 解析
Video ID + Title
  ↓ 格式化为列表
Prompt (含HTML模板)
  ↓ 传给LLM
GPT-4o 智能选择
  ↓ 填充模板
完整HTML iframe
  ↓ 生成
MDX文章
```

### 执行步骤

1. ✅ **创建** `youtube_manager.py` (~100行)
2. ✅ **修改** `prompt-template.txt` (添加模板和占位符)
3. ✅ **修改** `generate-articles.py` (5处小改动)
4. ✅ **测试** 单元测试和集成测试
5. ✅ **验证** 生成的文章质量
6. ✅ **上线** 批量生成

### 关键指标

- **代码量**: ~100行新增代码
- **修改文件**: 3个文件
- **Token节省**: ~75%
- **维护成本**: 极低
- **实现难度**: 简单

这是三个方案中**最优雅、最简洁**的解决方案！
