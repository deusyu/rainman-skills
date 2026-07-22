# rainman-skills

[English](README.md) | 中文

Claude Code Skills by Rainman.

这是一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skills 的 monorepo，收录实用的自定义 Skill，帮助你用自然语言高效完成各种任务。

## Skills

| Skill | 简介 |
|---|---|
| [nl2ledger](./skills/nl2ledger/) | 自然语言记账 — 说一句话，自动解析并写入钱迹 CSV |
| [cn-holiday](./skills/cn-holiday/) | 中国节假日/调休查询 — 查某天是工作日还是休息日 |
| [exchange-rate](./skills/exchange-rate/) | 汇率换算 — 查询实时汇率、历史汇率（数据源：ECB） |
| [qweather](./skills/qweather/) | 天气查询 — 实时天气、预报、生活指数（数据源：和风天气） |
| [car-advisor](./skills/car-advisor/) | 买车顾问 — 实时汽车参数对比、价格查询、车主评价、购车建议 |
| [mac-upgrade-advisor](./skills/mac-upgrade-advisor/) | 判断 Mac 是否值得换新 —— 按真实瓶颈而非芯片代数决策 |
| [check-name-clearance](./skills/check-name-clearance/) | 名称查重 — 查公司/产品/App 名是否被占用：域名、商标、App Store、包名、各州 LLC |
| [mermaid-link](./skills/mermaid-link/) | Mermaid 秒开链接 — 对话里生成的 Mermaid 图一键在 [mmd.dyu.sh](https://mmd.dyu.sh) 打开，免复制粘贴 |
| [portrait-prompt](./skills/portrait-prompt/) | 去AI味人像提示词 — 8 维框架 + 反塑料皮肤自检 + 按模型方言适配 |
| [share-to-xhs](./skills/share-to-xhs/) | 通过 Chrome 把现成 `share/` 套件发布到小红书，带预览、验证和防重复记录 |

## 安装

### 方式一：Claude Code Marketplace（推荐）

在 Claude Code 中运行：

```
/plugin marketplace add deusyu/rainman-skills
/plugin install nl2ledger@rainman-skills
```

安装后可在 Marketplace 界面开启自动更新。

### 方式二：npx

```bash
npx skills add deusyu/rainman-skills
```

按提示选择要安装的 Skill 即可。

### 方式三：手动安装

```bash
git clone https://github.com/deusyu/rainman-skills.git
cp -r rainman-skills/skills/nl2ledger YOUR_PROJECT/.claude/skills/
```

---

## nl2ledger

用自然语言记账，Claude 自动解析金额、分类、时间，生成符合[钱迹](https://www.qianji.app/)格式的 CSV 条目。

### 功能

- 支持中文、英文、中英混合输入
- 自动识别金额、商户、分类
- 一句话记多笔（逗号/顿号分隔）
- 支持相对时间表达（昨天、上周五、上午10点……）
- 写入前预览确认，不会误操作

### CSV 文件

在项目根目录放置你的钱迹 CSV 文件：

- **从钱迹 App 导出**已有数据，或
- **创建空白 CSV**（只需表头行），表头格式参考 [`skills/nl2ledger/sample/QianJi_sample.csv`](./skills/nl2ledger/sample/QianJi_sample.csv)

### 使用示例

安装后，在 Claude Code 中直接用自然语言记账：

```
午饭麦当劳25块
```
```
咖啡18，打车32
```
```
昨天晚饭西贝89
```
```
lunch 35, coffee 18
```

Claude 会自动识别并显示预览，确认后写入 CSV。

### 自定义

- **分类规则**：编辑 `references/category_map.md`，添加你常去的商户和消费习惯
- **记账者名称**：在 `category_map.md` 的 Default Values 部分和 `scripts/append_entry.py` 的 `--recorder` 默认值中修改
- **默认账户**：同上，修改 `账户1` 的默认值

> **提示**：仓库中的分类规则和特殊规则（如商户名、标签等）是示例配置，请根据自己的消费习惯修改。

## cn-holiday

通过 timor.tech API 查询中国节假日、调休补班、工作日安排。

### 功能

- 查询某天是工作日、周末、节假日还是调休补班
- 全年假期安排一览
- 加班工资倍率查询（1倍 / 2倍 / 3倍）
- 无需 API Key

### 使用示例

```
今天上班吗
```
```
春节放几天
```
```
国庆节放假安排
```
```
下个工作日是哪天
```

## exchange-rate

通过 Frankfurter API（数据源：欧洲央行 ECB）查询实时和历史汇率，支持 30+ 主要货币。

### 功能

- 实时货币换算
- 历史汇率查询
- 支持中文货币名称（美元、人民币、欧元……）
- 无需 API Key

### 使用示例

```
100美元换人民币
```
```
500 EUR to JPY
```
```
今天英镑汇率多少
```

## qweather

通过[和风天气](https://www.qweather.com/) API 查询实时天气、预报和生活指数。

### 功能

- 实时天气状况
- 多日天气预报
- 生活指数（紫外线、穿衣、洗车等）
- 城市名称查询（中英文）
- 需要设置 `QWEATHER_API_KEY` 和 `QWEATHER_API_HOST` 环境变量

### 使用示例

```
北京今天天气怎么样
```
```
明天需要带伞吗
```
```
上海未来三天天气预报
```

## car-advisor

实时汽车问答与对比分析系统。Claude 会从官网、懂车帝、汽车之家、真实车主评价等渠道实时检索数据，回答任何买车相关问题。

### 功能

- 多车型参数横向对比，输出结构化表格
- 实时价格查询（从品牌官网获取最新售价）
- 真实车主评价汇总（懂车帝、汽车之家、知乎）
- 按预算推荐车型
- 智驾能力对比（NOA、激光雷达、算力等）
- 销量/市场数据查询
- 无需 API Key（基于 Web 搜索）

### 使用示例

```
小米SU7和Model 3哪个好
```
```
问界M9多少钱
```
```
20-30万预算推荐什么新能源SUV
```
```
Model Y 焕新版有座椅通风吗
```
```
2024年最畅销新能源车排名
```

Claude 会实时搜索数据，生成参数对比表，汇总车主评价，并给出附带数据来源的购买建议。

## mermaid-link

把对话中生成的 Mermaid 图变成可点击的预览链接。不用再从聊天里复制图表代码、粘贴到渲染器——你（以及任何拿到链接的人）点一下，图就在 [MMD Paper](https://mmd.dyu.sh) 里渲染出来。

### 功能

- 自动生效：Claude 生成 Mermaid 图表时，自动在代码块后附上预览链接
- 也可按需使用：贴一段 Mermaid 代码，让它给你链接
- 链接自包含 —— 图表内容编码在 URL hash 里，无账号、无服务端存储
- 隐私友好：hash 片段不会发送到任何服务器，MMD Paper 纯浏览器端渲染
- 完整支持 UTF-8 / 中文标签
- 无需 API Key

### 使用示例

装好后自动生效，直接让 Claude 画图即可：

```
画一个用户登录流程的时序图
```

Claude 会在 ```` ```mermaid ```` 代码块后附上形如
`[▶ Open diagram](https://mmd.dyu.sh/#Zmxvd2NoYXJ0...)` 的链接——点开就是渲染好的图，
可以切换主题、缩放、导出 SVG/PNG。

也可以把现成的代码丢给它：

```
把这段 mermaid 变成链接：graph TD; A-->B
```
```
打开这个图
```

## portrait-prompt

去AI味人像提示词。描述你想要的人像，Claude 按 8 维框架——主体人设、服装材质、表情瞬间、镜头构图、光线皮肤、背景氛围、画质处理、负面词——构建摄影级提示词，强制跑一遍反AI味自检，再按目标模型方言适配输出。

### 功能

- 针对塑料感 / AI味 / 廉价感的根源（统计均值回归）下手，而非表面堆词
- 每维硬门槛：具体数字年龄、皮肤微观四件套（毛孔/肤色不均/油光/绒毛）、唯一有动机的主光、真实焦段+光圈数值、缺陷预算
- 结构性风险处理：手部、画面内文字与 logo、密集网格物、人群面孔
- 输出前强制自检：均值脸风险、对比堆叠、饱和度陷阱
- 模型方言适配：Midjourney / Stable Diffusion / Flux / GPT-Image / 即梦 —— 无负面通道的模型自动把负面词转为正向陈述
- 无需 API Key

### 使用示例

```
给我一个克制老钱风的人像提示词，用在 Midjourney
```
```
体育赛事广播截图风，网球，16:9，Flux 用
```
```
一个 50 岁陶艺家在工作室的肖像，去AI味
```

## share-to-xhs

把项目 `share/` 或 `share-rednote/` 目录里已经完成的小红书文案和有序图片发布出去。Skill 会确定性解析内容、检查平台限制、在用户真实 Chrome 的创作中心填表、停在发布前做最终目视确认，发布后再到内容管理验证，并写入基于哈希的回执防止重复发布。

### 功能

- 支持标准 `### 小红书` + `## Attach` share-kit 章节
- 支持带标题候选和轮播顺序的 `note.md` 套件
- 保留原始文案与图片顺序，不会擅自把 X/朋友圈文案改成小红书稿
- 支持扫码登录截图交接、真实创作页预览和点击前确认
- 严格验证发布结果，并原子写入 `.publish/xhs-ledger.json`
- 本地解析器只依赖 Python 标准库

### 运行要求

自动发布需要当前运行时能够控制用户的 Chrome 会话。在 Codex 中需安装并启用 Chrome 控制插件/扩展；如果没有可控 Chrome，Skill 只能生成标准化 payload，不得静默切换到其他浏览器。

### 使用示例

```text
使用 $share-to-xhs 把 nice-talk/share/01-launch 发布到小红书。
```

```text
扫描这个项目的 share 目录，告诉我哪些小红书内容可以直接发。
```

## License

[MIT](./LICENSE)
