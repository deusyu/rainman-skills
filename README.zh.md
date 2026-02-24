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
| [cosmetic-detect](./skills/cosmetic-detect/) | 整容检测 — 上传照片，分析是否有医美/整容痕迹 |
| [car-advisor](./skills/car-advisor/) | 买车顾问 — 实时汽车参数对比、价格查询、车主评价、购车建议 |

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

## cosmetic-detect

上传面部/身体照片，Claude 会系统性地逐区域分析是否存在医美或整容痕迹。

### 功能

- 逐区域分析：眼睛、鼻子、嘴唇、下颌轮廓、额头、面颊、皮肤、颈部、身体
- 跨区域一致性检查（种族特征、年龄、对称性、比例）
- 前后对比照分析模式
- 自然度评分（1-10）及置信度
- 多种族基线参考，提高检测准确性
- 中英双语输出

### 使用示例

在 Claude Code 中上传照片并提问：

```
看看这张照片有没有整过
```
```
帮我鉴定一下，自然度评分多少
```
```
对比这两张照片，有没有做过手术
```
```
Analyze this photo for cosmetic procedures
```

Claude 会输出结构化的分析报告，包含区域发现、跨区域一致性、自然度评分和置信度。

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

## License

[MIT](./LICENSE)
