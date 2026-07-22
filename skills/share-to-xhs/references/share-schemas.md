# Supported share schemas

## Standard share-kit README

Expected chapter layout:

```text
share/
├── README.md
└── 01-launch/
    ├── README.md
    └── image.png
```

The chapter `README.md` must contain a fenced block after a `### 小红书` heading:

```text
Title on the first non-empty line

Body paragraphs

#topic-one #topic-two
```

Parsing rules:

- First non-empty line becomes `title`.
- Contiguous trailing lines beginning with `#` become `tags`.
- Lines between them become `content`, preserving paragraph breaks.
- `## Attach` supplies image order.
- If an Attach line has a `小红书：` branch, only that branch is parsed.
- Backticked or plain relative PNG/JPEG/WEBP paths are resolved from the chapter directory.
- A root `Suggested posting order` numbered list using bold chapter names overrides lexical directory order.

## Rednote note.md

Expected chapter layout:

```text
share-rednote/
└── 01-topic/
    ├── note.md
    ├── cover.jpg
    └── 02-detail.jpg
```

Expected sections:

```markdown
## 标题（选一个）
- First title
- Second title

## 正文
Body

## 话题
#topic-one #topic-two

## 轮播（已生成,按序发 2 张）
1. `cover.jpg`
2. `02-detail.jpg`
```

The caller must provide `--title-index` when more than one title exists. Carousel numbering is authoritative image order.

## Unsupported or ambiguous input

Mark a chapter `not_xhs_ready` when it has no supported XHS section. Do not convert another platform's copy automatically.

Block and ask for correction when:

- The title/body boundary cannot be determined.
- Multiple titles exist without a selection.
- Attach contains no resolvable image.
- A listed asset is absent.
- Source content violates a hard XHS limit.

When a project's Markdown differs, update the deterministic parser and its tests instead of adding one-off interpretation instructions to the agent workflow.
