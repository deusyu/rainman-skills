# rainman-skills

English | [中文](README.zh.md)

Claude Code Skills by Rainman.

A monorepo of custom [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skills to help you get things done with natural language.

## Skills

| Skill | Description |
|---|---|
| [nl2ledger](./skills/nl2ledger/) | Natural language bookkeeping — speak and it writes to QianJi CSV |
| [cn-holiday](./skills/cn-holiday/) | Query Chinese public holidays, 调休, and work schedules |
| [exchange-rate](./skills/exchange-rate/) | Currency exchange rate query and conversion (ECB data) |
| [qweather](./skills/qweather/) | Weather query — real-time weather, forecasts, and life indices (QWeather) |
| [car-advisor](./skills/car-advisor/) | Real-time car comparison and purchase advisor with live data |
| [mac-upgrade-advisor](./skills/mac-upgrade-advisor/) | Decide whether a Mac is worth upgrading — by real bottleneck, not chip generation |
| [check-name-clearance](./skills/check-name-clearance/) | Check if a company/product/app name is taken — domains, trademarks, App Store, packages, state LLC |
| [mermaid-link](./skills/mermaid-link/) | Turn Mermaid diagrams in conversations into clickable preview links ([mmd.dyu.sh](https://mmd.dyu.sh)) — no copy-paste |
| [portrait-prompt](./skills/portrait-prompt/) | De-AI-flavor portrait prompts — 8-dimension framework, anti-plastic-skin self-check, per-model adaptation |

## Installation

### Option 1: Claude Code Marketplace (Recommended)

Run in Claude Code:

```
/plugin marketplace add deusyu/rainman-skills
/plugin install nl2ledger@rainman-skills
```

You can enable auto-updates in the Marketplace UI.

### Option 2: npx

```bash
npx skills add deusyu/rainman-skills
```

Follow the prompts to select the Skills you want.

### Option 3: Manual

```bash
git clone https://github.com/deusyu/rainman-skills.git
cp -r rainman-skills/skills/nl2ledger YOUR_PROJECT/.claude/skills/
```

---

## nl2ledger

Natural language bookkeeping — Claude parses amounts, categories, and timestamps from your input and appends structured entries to a [QianJi](https://www.qianji.app/) CSV ledger.

### Features

- Chinese, English, or mixed-language input
- Auto-detects amount, merchant, and category
- Multiple entries in one sentence (comma / pause-mark separated)
- Relative time expressions (yesterday, last Friday, 10am…)
- Preview before writing — no accidental entries

### CSV File

Place your QianJi CSV file in the project root:

- **Export** existing data from the QianJi App, or
- **Create a blank CSV** with only the header row — see [`skills/nl2ledger/sample/QianJi_sample.csv`](./skills/nl2ledger/sample/QianJi_sample.csv) for the format

### Usage

After installation, just type in Claude Code:

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

Claude will parse, show a preview, and write to CSV upon confirmation.

### Customization

- **Category rules**: Edit `references/category_map.md` to add your own merchants and spending habits
- **Recorder name**: Change the default in `category_map.md` (Default Values section) and `scripts/append_entry.py` (`--recorder`)
- **Default account**: Same files, change the `账户1` default

> **Note**: The category rules and special rules (merchant names, tags, etc.) in this repo are example configurations. Customize them to match your own habits.

## cn-holiday

Query Chinese public holidays, 调休 (make-up workdays), and work schedules via the timor.tech API.

### Features

- Check if a date is a workday, weekend, holiday, or make-up workday
- Full-year holiday schedule overview
- Overtime pay multiplier info (1x / 2x / 3x)
- No API key required

### Usage

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

Query real-time and historical exchange rates via the Frankfurter API (ECB data source). Supports 30+ major currencies.

### Features

- Real-time currency conversion
- Historical exchange rate lookup
- Supports Chinese currency names (美元, 人民币, 欧元…)
- No API key required

### Usage

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

Query real-time weather, forecasts, and life indices via [QWeather](https://www.qweather.com/) (和风天气) API.

### Features

- Real-time weather conditions
- Multi-day weather forecast
- Life indices (UV, clothing, car wash, etc.)
- City name lookup (Chinese/English)
- Requires `QWEATHER_API_KEY` and `QWEATHER_API_HOST` environment variables

### Usage

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

Real-time car comparison and purchase advisor. Claude searches live data from official sites, Dongchedi, Autohome, and owner reviews to answer any car-related question.

### Features

- Multi-car parameter comparison with structured tables
- Real-time pricing from official brand websites
- Owner reviews and ratings from Dongchedi, Autohome, Zhihu
- Budget-based car recommendations
- Smart driving (ADAS) capability comparison
- Sales and market data lookup
- No API key required (uses web search)

### Usage

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

Claude will search live data, generate comparison tables, summarize owner feedback, and give purchase recommendations with data sources cited.

## mermaid-link

Turn Mermaid diagrams in conversations into clickable preview links. Instead of copying diagram code out of the chat and pasting it into a renderer, you (or anyone you share the link with) just click — the diagram opens in [MMD Paper](https://mmd.dyu.sh), rendered instantly.

### Features

- Works automatically: when Claude generates a Mermaid diagram, it appends a preview link right after the code block
- Also works on demand: paste any Mermaid code and ask for a link
- Links are self-contained — the diagram is encoded in the URL hash, no account, no server storage
- Private by design: the hash fragment never reaches any server; MMD Paper renders 100% client-side
- UTF-8 / Chinese labels fully supported
- No API key required

### Usage

Once installed, it kicks in on its own — ask Claude for any diagram:

```
画一个用户登录流程的时序图
```

Claude replies with the ```` ```mermaid ```` block plus a link like
`[▶ Open diagram](https://mmd.dyu.sh/#Zmxvd2NoYXJ0...)` — click it and the rendered
diagram opens in the browser, where you can switch themes, zoom, and export SVG/PNG.

Or hand it existing code:

```
把这段 mermaid 变成链接：graph TD; A-->B
```
```
打开这个图 / open this diagram
```

## portrait-prompt

De-AI-flavor portrait prompts. Describe the portrait you want and Claude builds a photorealistic prompt through an 8-dimension framework — persona, fabric, moment, lens, light & skin, background, finishing, negatives — runs a mandatory anti-AI-flavor self-check, then adapts the output to your image model.

### Features

- Targets the root causes of plastic skin / AI flavor / stock-photo cheapness, not the symptoms
- Hard gates per dimension: numeric age, skin micro-texture four-pack (pores / uneven tone / oil sheen / vellus hair), single motivated key light, real focal length + f-stop, imperfection budget
- Structural risk handling: hands, in-scene text & logos, dense repeating grids, crowd faces
- Mandatory self-check before output: mean-face risk, contrast stacking, saturation traps
- Model dialect adaptation: Midjourney / Stable Diffusion / Flux / GPT-Image / Seedream — negative prompts auto-converted to positive statements for models without a negative channel
- No API key required

### Usage

```
给我一个克制老钱风的人像提示词，用在 Midjourney
```
```
体育赛事广播截图风，网球，16:9，Flux 用
```
```
a 50-year-old ceramicist in her studio, photoreal portrait prompt, de-AI
```

## License

[MIT](./LICENSE)
