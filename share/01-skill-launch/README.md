# 01 · share-to-xhs 首发

一句定位:把写好的分享包安全发布到小红书——不重写内容,防重复发布,发后可验证。

## Assets

- `cover.png` — 钩子卡:机械手指悬停在上锁的「发布」按钮上(1242×1656,3:4)
- `02-flow.png` — 五步发布流程卡(1242×1656,3:4)
- `03-safety.png` — 安全设计四要点卡(1242×1656,3:4)
- `prompts/` — 三张卡的生成提示词(再生成方法见根 README)

## Post-ready copy

### 小红书

```text
复制粘贴发帖太烦,我让AI代劳了

文案和图都做好了,复制粘贴发帖这一步反而最烦。
想让 AI 直接替我发,又怕两件事:它乱改我的文案,或者手抖发重复。
所以我写了个开源的 Claude Code 技能,叫 share-to-xhs。
它只发我写好的东西。不重写,不加 emoji,不动图片顺序,想改哪一处都得先问我。
保险一共三道。
发前:本地先校验一遍,标题超 20 字、正文夹链接,直接拦下,图片不是 3:4 竖版也会提醒。填好页面我看一眼,点头才许发。
点击:发布键只按一次。结果不确定就停下来查,不自动重试。
发后:去创作者中心核对,审核中不算发成功。同一篇再发一次?会被本地账本拦住。
它用的是我自己登录的 Chrome,不用无头浏览器,全程看得见,不读 Cookie,扫码登录还是我自己扫。
MIT 开源,GitHub 搜 deusyu/rainman-skills,Claude Code 里就能装。
如果是你,会把发帖这步交给 AI 吗?

#ClaudeCode #AI工具 #开源 #效率工具 #小红书运营
```

### X-中文

```text
让 AI 替你发小红书,最怕两件事:改你的文案,或者重复发帖。

我写了个开源 Claude Code 技能 share-to-xhs,发布拆成三段,每段一道保险:

1/ 发前:只发你写好的 share/ 包,原样发,不重写。本地先校验:标题 20 字上限、正文禁链接、图片 3:4 提醒。填好的页面你过目后才发
2/ 点击:发布键只按一次,结果不确定就停下查,不自动重试
3/ 发后:去创作者中心核对;同一篇内容再发,会被本地账本拦住

用你自己登录的 Chrome,不用无头浏览器,不读 Cookie,全程可见。

github.com/deusyu/rainman-skills
```

### X-EN

```text
Letting an AI post to social media for you has two failure modes: it rewrites your copy, or it double-posts.

I built share-to-xhs, an open-source Claude Code skill that publishes prepared content to Xiaohongshu (RED) with a safeguard at each stage:

1/ Before: publishes your prepared share/ package without rewriting it; local checks catch over-length titles and URLs in the body, and flag non-3:4 images — then you review the filled page
2/ At the click: the publish button is pressed exactly once; if the result is unclear it stops and investigates instead of retrying
3/ After: it verifies the post in the creator console, and a local ledger blocks re-publishing the same content to the same account

Runs in your own logged-in Chrome — no headless browser, no cookie reading, everything visible.

MIT licensed: github.com/deusyu/rainman-skills
```

## Attach

X:`cover.png` 单图即可;小红书:`cover.png` 为主、`02-flow.png`、`03-safety.png` 为辅。
