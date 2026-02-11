# rainman-skills

Claude Code Skills by Rainman.

A monorepo of custom [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skills to help you get things done with natural language.

[中文说明](#中文说明)

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

---

# 中文说明

Claude Code Skills by Rainman.

这是一个 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Skills 的 monorepo，收录实用的自定义 Skill，帮助你用自然语言高效完成各种任务。

## Skills

| Skill | 简介 |
|---|---|
| [nl2ledger](./skills/nl2ledger/) | 自然语言记账 — 说一句话，自动解析并写入钱迹 CSV |

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

## License

[MIT](./LICENSE)
