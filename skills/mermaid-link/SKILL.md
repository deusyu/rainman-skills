---
name: mermaid-link
description: >
  把 Mermaid 图表变成可点击的预览链接（mmd.dyu.sh），省去从对话里复制粘贴代码。
  Turn Mermaid diagrams into clickable preview links — no copy-paste.
  触发: 当你在回复中输出了 Mermaid 图表 / ```mermaid 代码块时，主动在其后附上预览链接；
  或用户说 "打开这个图", "预览这个图", "mermaid 链接", "在浏览器里看这个图",
  "open this diagram", "mermaid link", "preview mermaid"。
---

# mermaid-link — Open Mermaid diagrams via link

[MMD Paper](https://mmd.dyu.sh) is a local-first Mermaid scratchpad that accepts the
diagram source in the URL hash. This skill turns any Mermaid code into a
ready-to-click preview link, so nobody has to copy diagram code out of a chat and
paste it somewhere to see it.

## URL format

```
https://mmd.dyu.sh/#<base64(utf8(mermaid source))>
```

- Standard base64 and base64url both work; padding and line wrapping are tolerated.
- Privacy: the hash fragment is never sent to any server, and MMD Paper renders
  100% client-side — the diagram never leaves the browser.

## Workflow

1. Take the Mermaid source. Prefer just the diagram code; full Markdown containing a
   ```` ```mermaid ```` block also works (MMD Paper extracts the first block).
2. Encode it. Write the code to a temp file first — this sidesteps shell-quoting
   pitfalls with quotes, backticks, and `$` in diagram text:

   ```bash
   cat > "${TMPDIR:-/tmp}/diagram.mmd" <<'MMD'
   flowchart TD
     A[Start] --> B{Ship?}
   MMD
   echo "https://mmd.dyu.sh/#$(base64 < "${TMPDIR:-/tmp}/diagram.mmd" | tr -d '\n')"
   ```

   `tr -d '\n'` matters: GNU `base64` wraps output at 76 columns.
3. Put the link right after the diagram, as a Markdown link:

   ```markdown
   [▶ Open diagram](https://mmd.dyu.sh/#Zmxvd2NoYXJ0IFREOyBBLS0+Qg==)
   ```

## Behavior

- When you generate a Mermaid diagram in a reply, append the preview link right
  after the code block — don't wait to be asked.
- Multiple diagrams → one link per diagram.
- UTF-8 labels (Chinese etc.) are fully supported — base64 encodes the UTF-8 bytes.
- Long diagrams produce long URLs. Always wrap them in Markdown link syntax so chat
  UIs don't mangle them; browsers handle URLs far larger than any realistic diagram.
- Do not try to compute base64 "in your head" — always run the shell command.
