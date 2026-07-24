# share-to-xhs 分享套件

share-to-xhs:把项目里写好的分享包安全发布到小红书的开源 Claude Code 技能。

文案经过两道工序:codex 对抗审查(事实清单硬边界,逐句裁决)→ humanizer-zh(只动文风不动事实,处理后已对照事实清单复核)。

本目录同时是 share-to-xhs 技能的**活体测试样例**:对本目录跑
`python3 skills/share-to-xhs/scripts/share_to_xhs.py scan share` 应得到 `ready`。

## Suggested posting order

1. **01-skill-launch** — 技能首发,唯一章节。

## Formats

- 小红书附图:3:4 竖版,1242×1656 px(平台推荐尺寸)。
- 图为 GPT-Image-2 生成的信息卡(经 baoyu-image-gen 的 codex-cli provider,9:16 生成后居中裁至 3:4)。本技能无网页前端,无实拍素材可抓;卡上文字均来自事实清单,逐图人工核对过错别字。
- X 可复用同组图;正文含仓库链接。

## 素材再生成

各章 `prompts/` 目录存有生成提示词。再生成:

```bash
bun ~/.claude/skills/baoyu-image-gen/scripts/main.ts \
  --provider codex-cli --promptfiles prompts/p1-cover.md --image raw.png --ar 9:16
sips -c 1255 941 raw.png && sips -z 1656 1242 raw.png   # 居中裁 3:4 → 1242×1656
```
