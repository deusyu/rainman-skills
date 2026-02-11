# rainman-skills

English | [中文](README.zh.md)

Claude Code Skills by Rainman.

A monorepo of custom [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skills to help you get things done with natural language.

## Skills

| Skill | Description |
|---|---|
| [nl2ledger](./skills/nl2ledger/) | Natural language bookkeeping — speak and it writes to QianJi CSV |

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

## License

[MIT](./LICENSE)
