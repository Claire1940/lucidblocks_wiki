深度思考（使用中文和我交流。文档都是中文。严禁未经许可创建各种非必要的文档、测试文件）：
你的目标是搭建一个小游戏站。
阅读下方项目/需求，先编写项目重构文档（包含待办优先级）和SEO优化文档。

游戏词： dragon traveler
新项目： https://github.com/libin257/dragontraveler.com.git https://github.com/new
域名： dragontraveler.com

0、游戏背景
游戏：dragon traveler
官网地址是什么？
深度搜索分析，用大白话讲解游戏背景、玩法逻辑（难点）。
用户痛点（游戏内容相关，不是系统bug 之类。现在是怎么满足，并给出具体链接）、真实需求或感兴趣内容（例如榜单、话题），给出对应英文谷歌搜索关键词，按优先级排序。
如果有code，全网搜集搜索10+个有效code和对应的奖励，不能骗我。
网络搜索并给出合适youtube（4个）、Reddit具体链接（2个）。

多语言
根据热度，分析应该支持哪几门语言（并搜索对应本地化游戏名），按流量排优先级。
先说结论，按优先级排列, 最多3门语言（必须有一个是英语，中文除外）

1、功能设计
基于以上内容，我现在在做游戏内容工具站
我的域名：dragontraveler.com

现在问题：页面只有用户下载这一刚需，但用户点击下载导航后就走了。
请帮我设计首页的功能模块（每部分都要写宣传语）：
（1）数据展示（不超过1个）：游戏内容相关（禁止全球成就完成统计这种和游戏内容无关的展示）
必须是用户经常讨论问题，且数据可以一次性【轻松获取】
api或系统性的一篇文章，不要论坛抓取，表明链接。
如果API获取数据，写清楚：请求url、入参和输出数据json格式。
优势：我可以用大模型进行数据整理，变成用户感兴趣内容。
数据展示一定要炫酷，吸引眼球。
（2）轻量小功能（不超过1个，简单、刚需优先级靠前、高频不是一次性需求）
定义好用户输入（最好是筛选/点击，降低用户成本）、输出、处理逻辑、现在用户的需求是怎么满足的，和数据获取（简单）：外部api或系统性的一篇文章，不要论坛抓取。
不涉及定时调度和部署。
读外部API计算时：为页面不频繁请求浪费时间，要求一次性获取全部数据到本地方案（如存到/public/data/xxx.json）。
如果API获取数据，写清楚请求url、入参和输出数据json格式。
2 个功能里，禁止使用AI。

2、官方照片&背景图&图标&UI
（1）给出官方游戏网站链接
（2）给出适合游戏背景的全站背景图Prompt提示词（PC端、无任何物品，2个备选），营造氛围增强用户沉浸度。要求：背景简单、不会与文字有颜色冲突。一定要和游戏匹配
（3）直接画出适合该游戏站的favicon
（4）定义鼠标滑动时的鼠标箭头位置的特效
（5）给出适合该网站的风格UI json代码，不用出现字体对比度导致的显示问题。
以上：禁止直接给我单独一个图片的URL（很有可能打不开）

 
2、内页
https://trends.google.com/trends/explore?date=now 7-d&q=dragon+traveler
https://sim.3ue.co/#/digitalsuite/acquisition/findkeywords/keyword-generator-tool/999/28d?searchEngine=google&keyword=dragon+traveler&webSource=Total&isWWW=*&tab=phraseMatch
https://sem.3ue.co/analytics/keywordmagic/?q=dragon+traveler&db=us&__gmitm=ayWzA3*l4EVcTpZei43sW*qRvljSdU
https://www.google.com.hk/search?q=dragon+traveler
https://www.youtube.com/results?search_query=dragon+traveler

抽取出本页面所有的关键词和对应的搜索量表格形式给出。
只抽取关键词，不要加附加信息, 不要省略。

（0）
基于tools/demand/关键词.md，新建一个关键词分类文档：tools/demand/关键词分类.md
对【所有关键词】分类（<=8组，核心主词和非本游戏相关词过滤掉，不要在分类里），核心主词和非本游戏词过滤掉。
同义词要合并（合并后的关键词必须是搜索量最大、大众习惯搜索那个）。
并给出同义词合并后，还有多少，即还能做多少"一个词一个内页"的精品内容。 
分类1：xxx
关键词1
关键词2
…
严禁缺少任何一个关键词（核心主词和非本游戏词除外）。
注意事项：xxx游戏 reddit等这类，也属于这个游戏，不能过滤。
关键词优化：
1、不允许存在非英文（需翻译成英文）
2、可修改某单词拼写错误，但禁止扩写
3、游戏词统一，然后去重：例如dragon traveler xxx，游戏名统一成dragon traveler xxx。
除此之外，禁止做其他修改。
注意事项：
Mutually Exclusive（相互独立）：一个分类下,不能出现同义关键词（例如只是单复数区别）
Collectively Exhaustive（完全穷尽）：一个分类下所有有效关键词要覆盖这个分类可能的所有需求，且具备一定逻辑关系（顺序或包含）

（1）
基于上述关键词分类文档：tools/demand/关键词分类.md
按照分类肯关键词顺序，按照一词一内页原则（需要干掉游戏主词和其他游戏的关键词），为游戏站生成 精品内页SEO内容矩阵。
最后给我一个文件名为内页的JSON（含优先级（1/2/…，每级30篇左右的文章），放到位置tools/articles/modules/generation/内页.json。
每个内页面（只针对上述一个关键词），对应可参考的优秀文章内容具体链接（而不是一个网站）。
设计关键词、页面URL结构、目录结构（一/二/三级树状结构）、文章标题。
字段分别是：优先级、关键词（要和给你的关键词名称完全一致）、关键词搜索量、URL路径（采用///两级结构）、文章标题、5列），必须是全英文。
文章标题注意事项：必须大于于60个字符小于120字符，且包含关键词且吸引人点击,必须3个字以上，可体现出文章目标和内容，把利益点、时效、数量一目了然，最终显著提升同位次 CTR。
文章标题严禁全部使用某种模板（严谨直接编程生成）。
表头字段命名必须是： Priority、Keyword、Search Volume、URL Path、Article Title关键词只针对标准关键词（排除非括号内的同义关键词）。
[
  {
    "Priority": 1,
    "Keyword": "starrupture gameplay",
    "Search Volume": "8917",
    "URL Path": "/community/gameplay",
    "Article Title": "StarRupture Gameplay 2025: First 60 Minutes of Brutal Survival, Base Building and Combat Revealed"
  },
  {
    "Priority": 1,
    "Keyword": "starrupture trailer",
    "Search Volume": "3166",
    "URL Path": "/community/trailer",
    "Article Title": "Watch All StarRupture Trailers: Official Launch Trailer, Gameplay Previews and Developer Showcases"
 }
]

3、首页SEO全英文文案
为新游戏重新编写首页SEO全英文文案（先阅读旧游戏的历史文档并参照格式）：tools/demand/首页SEO全英文文案.md
基于信息：
tools/demand/0_需求.md（域名、游戏名2）
tools/demand/游戏介绍.md
tools/demand/功能需求.md
tools/demand/多语言.md
tools/articles/modules/generation/内页.json
编写首页SEO 全英文文案（不是你的回答全英文，附内链、meta 标题/描述/关键词信息，页面自顶向下：导航、hero、导航、功能、社媒）
（1）hero区域：3s内给用户快速下钩子，增加了解网站欲望。
大标题必须是游戏名（为了SEO）。
给用户一种我真诚提供价值感觉：要有宣传语，例如 xxx 分钟。
不要虚假宣传，附上按钮对应上述具体url（工具页/tools/xxx，不是内页）。
（2）信息/下载导航区（内链）：吸引用户点击
基于内页.Excel具体链接：写出每个链接的标题、宣传语（吸引人点击）。必须是6个，禁止多或少。
（3）FAQ：多次体现游戏词，提升Seo关键词密度，不需要每条都携带内链。
（4）首页其余部分文案
点击按钮，要附上具体内页url。
导航栏链接：设置为一级目录文章列表页（和你提供给我的 url 一致），不是文章内页。
网络搜索并给出合适youtube（4个）、Reddit具体链接（2个）

【vscode】CC命令
Set-ExecutionPolicy -Scope Process Bypass
claude --dangerously-skip-permissions

1
现在需要将项目重构，模版站变成另一个游戏站。
游戏词: dragon traveler
新项目: git@github.com:libin257/dragontraveler.com.git
参考tools\git连接.md，添加远程仓库（使用 SSH 格式，不是 HTTPS）
域名: dragontraveler.com

删除旧的 origin 远程 git remote remove 当前项目（但不会影响 GitHub上的实际仓库）
关于 git 仓库迁移，您希望如何处理？ → 重新初始化 git 仓库
移除当前git本地工作区

完成后，提交远程代码（严禁修改代码文件）

– 同步工作
https://github.com/new
https://analytics.google.com/analytics/web/#/a366071507p510942946/admin/property/create
https://clarity.microsoft.com/projects
https://favicon.io/favicon-converter
https://www.youtube.com/results?search_query=dragon+traveler

2、修改首页修改首页面,请先列出todo list,然后开始执行。
前置说明：
保持当前多语言项目架构不变
第一步只完成英语版本（后续批量补充其他语言）
禁止修改任何页面现有前端设计和UI风格
所有文案必须在 src/messages/en.json 中管理
参考文档：tools/demand/首页SEO全英文文案.md
![alt text](image.png)
具体要求：
更新首页所有文案内容（按照首页SEO全英文文案.md）
清除旧导航项，只保留新游戏的导航栏
确保导航栏所有文案在 src/messages/en.json
确保首页所有文案在 src/messages/en.json

执行流程：
编写首页重构文档（包含 Todolist）
查看参考文档后依次执行
启动项目
使用 curl 测试首页
确认通过后，保持项目运行

完成检查清单：
首页文案已更新（参考首页SEO全英文文案.md）
导航栏已清除旧项目内容，只保留新游戏导航
所有首页文案在 src/messages/en.json
所有导航栏文案在 src/messages/en.json
curl 测试首页通过
前端设计和UI风格未改变
前置说明：
保持当前多语言项目架构不变
第一步只完成英语版本（后续批量补充其他语言）
禁止修改任何页面现有前端设计和UI风格
所有文案必须在 src/messages/en.json 中管理
参考文档：tools/demand/首页SEO全英文文案.md
![alt text](image.png)
具体要求：
更新首页所有文案内容（按照首页SEO全英文文案.md）
清除旧导航项，只保留新游戏的导航栏
确保导航栏所有文案在 src/messages/en.json
确保首页所有文案在 src/messages/en.json

执行流程：
编写首页重构文档（包含 Todolist）
查看参考文档后依次执行
启动项目
使用 curl 测试首页
确认通过后，保持项目运行

完成检查清单：
首页文案已更新（参考首页SEO全英文文案.md）
导航栏已清除旧项目内容，只保留新游戏导航
所有首页文案在 src/messages/en.json
所有导航栏文案在 src/messages/en.json
curl 测试首页通过
前端设计和UI风格未改变

3、创建工具页面,请先列出todo list,然后开始执行。
前置说明：
保持当前多语言项目架构不变
第一步只完成英语版本（后续批量补充其他语言）
禁止修改任何页面现有前端设计和UI风格
所有文案必须在 src/messages/en.json 中管理
参考文档：tools/demand/功能需求.md、tools/demand/游戏介绍.md

具体要求：
1 网络搜索数据
阅读 功能需求.md 中列出的所有 API/文章数据需求
网络搜索获取真实、完整的数据
严格按照要求生成完整的数据 JSON 文件

2 创建独立工具页
删除历史工具页
创建新的独立工具页（必须支持多语言）
页面文案在 src/messages/en.json
至少一个工具页放在首页 tool section 之后

3 在首页复刻功能模块
将工具页的功能复制到首页
替代首页原有功能模块
使用相同的数据 JSON
执行流程：
(1) 编写工具页重构文档（包含 Todolist）
(2) 网络搜索并创建完整数据 JSON
(3) 查看参考文档后依次执行
(4) 启动项目（如未运行）
(5) 使用 curl 测试工具页
(6) 使用 curl 测试首页的功能模块
(7) 确认通过后，保持项目运行

完成检查清单：
已阅读功能需求.md所有API/数据需求
已网络搜索并创建完整数据 JSON 文件
已删除历史工具页
已创建独立工具页（多语言支持）
工具页文案在 src/messages/en.json
首页已复刻工具功能模块
首页功能模块使用数据 JSON
curl 测试工具页通过
curl 测试首页功能模块通过
前端设计和UI风格未改变

最后检查网页/tools：
检查工具页多语言文案问题，有问题则修复src\messages\en.json

4、-- 和7并行执行
（1）删除src/messages/除英文以外其他语言，其他文件禁止改动多语言配置
（2）阅读tools/articles/内页.json，参考历史文章列表页样式，src/app/下，为目录创建列表页。
过程中禁止创建任何一篇文章页（.mdx）,我后面会批量创建。列表页所有文章必须列表排列,不能九宫格排列。
（3）移除所有历史项目（不属于内页.json）src/app下文章列表页。
（4）首页导航栏数量和内容，要和这些目录（内页.json和工具页+tools）保持一致（不多不少），并指向正确列表页或工具页url。
5、
（1）阅读tools/图片优化方案.md、tools/性能优化重构方案.md，
使用WebP方式，将tools/demand/hero.png、backend.png这两个图片分别放hero区右侧图、全站背景图（将历史项目public\images旧图先删除）
禁止修改tools/任何文件。
（2）阅读tools/demand/UI.md，设置全局鼠标(删除旧的鼠标样式svg)和网站颜色，优化视觉体验。不用出现字体对比度导致显示问题两个数据。
（3）检查icon.png：copy the following link tags and paste them into the head of your HTML.
完成后，清除缓存，并重新启动项目（同一个端口）
6、
（1）阅读项目，检查是否还有旧游戏词没被替换，尤其是src/messages/en.json和Footer.tsx，要删除旧项目部分（文章内容页不需要检查）
（2）检查首页所有url链接都指向正确内链，有内容返回（除文章页暂时没有内容，但要存在正确内链地址）
（4）去掉网站所有**除AdSense以外**广告，如果没有，不需要改动
（5）根项目下（尤其是页脚、版权、隐私、服务条款、Lighthouse等页面）检索旧游戏词，并全部替代成新游戏词而不是删除页面，除了文章页
禁止改动tools/下的所有文件、禁止修改任何多语言配置
<!------------------------------------------------------------------------------------------------->
7、文章页
-0、初始化. 请先列出todo list,然后开始执行
（1）根据项目游戏词、域名（tools\demand\0_需求.md）、内链（tools/articles/modules/generation/内页.json的url），修改tools/articles/modules/generation/config.json的site_domain、internal_links、external_authorities等选项.
（2）根据tools/demand/多语言.md里语言（加上英语最多3门），修改
tools/articles/modules/translate/translate_config.json里多语言配置（包括game name localizations）
（3）删除旧的tools\articles\modules\generation\video_metadata_cache.json，运行tools/articles/modules/generation/video_metadata.py处理tools/articles/modules/generation/youtube_data.csv，生成 youtube 元数据json.
(4) 删除src/content所有内容（目录和文件）
<!-- 
安装所需包：tools\articles\modules\generation\requirements.txt
使用国内镜像源：pip install 包名 -i https://pypi.tuna.tsinghua.edu.cn/simple -->
<!---- 修改生成文章功能：大模型生成的文章后，不符合位置格式，仍然要写入src/content，但要输出警告 -->

– 1、生成文章
阅读tools/articles/modules/generation/README.md, 加上–test生成2篇，测试生成
python3 tools/articles/modules/generation/generate-articles.py --test
如果都执行成功了，再去调用函数生成所有文章。如果有一个失败，都要禁止执行后续所有文章。
有问题的文章会记录到 `tools/articles/logs/failed_articles.json`，有格式问题手动修改，没有返回阅读tools\articles\modules\generation\内页.json手动生成。
python3 tools/articles/modules/generation/generate-articles.py
失败文章你直接写（基于内页Excel），禁止写脚本生成。

<!--– 查询网络，验证所有工具页和文章页的codes有效性，并进行更新 -->

– 2、翻译 文章
生成测试翻译文章：
python3 tools/articles/modules/translate/translate-articles.py --test --overwrite
如果都执行成功了，翻译剩余所有的文章：
python3 tools/articles/modules/translate/translate-articles.py --overwrite

<!---------------------------------------------------------->
– 3、翻译src/messages/下对应的json文件
python3 tools/articles/modules/transpage/translate-messages.py --overwrite

– 4、调整多语言
检查所有文件，是否存在历史多语言缩写（（如vi, zh, th等），干掉并替换。
根据tools/articles/modules/translate/translate_config.json里的多语言选项，和网站所有相关多语言配置，必须修改以下所有文件，禁止遗漏：
修改网站右上角筛选框里的对应展示语言（采用平铺列举法）
核心配置文件（5个）：
src/i18n/routing.ts

修改 locales 数组（如：[‘en’, ‘de’, ‘pt’]）
更新注释说明对应语言 src/lib/content.ts

修改第180行左右的语言列表检查，确保内容扫描器正确识别语言目录
src/app/[locale]/[…slug]/page.tsx

修改 generateStaticParams 中的 locales 数组
更新 generateMetadata 中的 alternates.languages 对象
src/i18n/request.ts

更新 locale 类型断言（如：‘en’ | ‘de’ | ‘pt’）
src/app/[locale]/layout.tsx

更新 localeMap 对象（语言到locale代码的映射）
更新 alternates.languages 对象
更新 locale 类型断言
SEO元数据文件（6个）：
src/app/[locale]/guides/page.tsx - alternates.languages
src/app/[locale]/maps/page.tsx - alternates.languages
src/app/[locale]/activities/page.tsx - alternates.languages
src/app/[locale]/items/page.tsx - alternates.languages
src/app/[locale]/meta/page.tsx - alternates.languages
src/app/[locale]/updates/page.tsx - alternates.languages

其他需要检查的文件：
src/middleware.ts - 检查路由匹配模式（通常已正确配置）
src/messages/*.json - 确保对应语言的翻译文件存在
src/content/* - 确保对应语言的内容目录存在

注意事项：
1）文章页点击相关文章，避免在路径拼接2个多语言缩写（如es/es/）
2）文章详情页的cta要是本游戏的工具

验证方法：
修改完成后运行：
rm -rf .next && npm run build
检查构建输出中的语言路径数量是否正确（N个内容路径 × 语言数量）

– 坑
Google好像强制刷新不了页面，终端清除缓存没用

8、测试
（1）重启本地服务器（同个端口），使用curl命令进行所有页面（文章页除外）本地url链接测试
（2）提交代码到远程仓库。我要部署到 vercel上，请检查是否能正常构建。
要求：必须上一步curl 命令测试所有 url 通过才可以。
执行检查代码问题：
npm run typecheck && npm run lint && vercel build
提交最终代码到GitHub。
（3）为这个游戏站首页生成4条基本信息（不生成其他，要求英文）
标题、URL、描述、锚文本

–
因为 Vercel 已经配置了重定向到 www，我们应该让代码也统一使用 www：
修改 metadataBase 为 www 版本
metadataBase: new URL(‘https://www.universaltowerdefense.net’) // 添加 www
需要检查的文件清单：
src/app/[locale]/layout.tsx:71 - metadataBase
src/app/robots.ts - robots.txt 中的 baseUrl


1、调整promot提示词：视频放在偏开头位置
2、爬取所有视频的信息，以后展示这个

广告怎么优化，一键开启一键关闭？
脚本也放到变量里