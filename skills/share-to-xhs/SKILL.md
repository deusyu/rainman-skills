---
name: share-to-xhs
description: Publish already-prepared Xiaohongshu (小红书/RED/XHS) posts from project share directories through the user's Chrome session, with deterministic parsing, linting, ordered local-image upload, real-page preview, explicit publish control, post-publication verification, and duplicate protection. Use when asked to scan or publish a `share/` or `share-rednote/` package, turn a share-kit chapter into an XHS draft, post an existing title/body/tags/images bundle, or verify that an XHS web post went live. Supports the standard `### 小红书` + `## Attach` README format and the `note.md` rednote format. Do not use it to invent missing XHS copy.
---

# Share to Xiaohongshu

Publish finished share-kit content without rewriting it. Parse locally first, then use the user's existing Chrome session for the visible creator-page workflow.

## Required resources

- Run `scripts/share_to_xhs.py` for discovery, normalization, validation, hashes, and receipts.
- Read `references/share-schemas.md` only when a source package fails parsing or a new schema must be added.
- Read `references/chrome-publishing.md` completely before the first browser action in a task.

## Core rules

1. Require an explicit project, `share` directory, or chapter path. Never scan the entire home directory or workspace by default.
2. Treat the prepared Markdown as source content. Do not rewrite, shorten, reorder images, add emoji, or change tags without showing the change to the user.
3. Publish only candidates reported as `ready`. Treat parser errors as blocking and warnings as review items.
4. Use the current runtime's supported Chrome-control capability, not a headless browser, so the user can reuse their login and inspect the real XHS rendering. If controllable Chrome is unavailable, stop and state that dependency instead of silently switching browsers.
5. Never inspect or export cookies, local storage, passwords, or browser profiles.
6. Never infer success from clicking Publish. Verify the resulting post in the creator content list or the public note page.
7. Never retry a publish click when the result is uncertain. Record `unknown` and investigate first; an automatic retry can create a duplicate.
8. Never publish multiple posts under one blanket confirmation. Prepare a queue, then handle one post at a time.
9. Require action-time confirmation while the completed creator-page preview is visible. Earlier permission to create the Skill or begin the workflow is not the final click confirmation.

## Workflow

### 1. Discover candidates

From this skill directory, run:

```bash
python3 scripts/share_to_xhs.py scan /absolute/path/to/project/share --json
```

The scanner recognizes:

- Standard share-kit chapters containing `### 小红书` and `## Attach` in `README.md`.
- Rednote chapters containing title choices, body, topics, and carousel order in `note.md`.

Respect the root README's numbered posting order when present. Report candidates without XHS content as `not_xhs_ready`; never repurpose X or 朋友圈 copy.

### 2. Select and prepare one post

For a standard chapter:

```bash
python3 scripts/share_to_xhs.py prepare /absolute/path/to/project/share \
  --chapter 01-launch \
  --output /tmp/xhs-payload.json
```

For a rednote chapter with several titles, select the user's chosen 1-based title index:

```bash
python3 scripts/share_to_xhs.py prepare /absolute/path/to/project/share-rednote \
  --chapter 01-ice-age \
  --title-index 1 \
  --output /tmp/xhs-payload.json
```

Do not silently choose among multiple title candidates. The preparation command blocks titles over 20 Unicode code points, URLs, missing assets, more than 10 tags, more than 18 images, and content over 1,000 Unicode code points. It warns about landscape or unusually small images.

If the current revision has a blocking attempt for the same account, stop unless the user explicitly requests a repost or verification resolves the old attempt.

### 3. Preview the normalized payload

Show the user at least:

- Source and post ID.
- Exact title and title length.
- Exact body.
- Tags.
- Image paths in upload order, including dimensions.
- Every warning.

This normalized preview authorizes filling the form, not clicking Publish. Obtain clear action-time confirmation after the completed Chrome preview is visible.

### 4. Fill and review in Chrome

Follow `references/chrome-publishing.md`:

1. Open the official Xiaohongshu creator site in the user's Chrome session.
2. If a QR-code login page appears, take a screenshot, give it to the user, and wait for them to finish login in Chrome.
3. Select image-and-text publishing.
4. Upload the normalized absolute image paths in their listed order.
5. Fill the exact title, body, and topics.
6. Inspect the rendered page and image order. Capture a screenshot before the irreversible action.
7. Resolve any platform-side validation error without silently changing content.

### 5. Arm, publish, and verify

After action-time authorization, first create a conservative duplicate-protection attempt:

```bash
python3 scripts/share_to_xhs.py ledger arm \
  --payload /tmp/xhs-payload.json \
  --account-key 'xhs:visible-account-alias' \
  --backend chrome
```

Keep the returned `attemptId`. Then:

1. Click Publish once.
2. Immediately transition the attempt to `submitted`, even before the site finishes responding:

   ```bash
   python3 scripts/share_to_xhs.py ledger transition \
     --payload /tmp/xhs-payload.json \
     --attempt-id ATTEMPT_ID \
     --state submitted
   ```

3. Wait for an explicit success state or navigation.
4. Open creator content management and locate the post by exact title.
5. Prefer opening the resulting note and verifying its title, image count, body, and topics.
6. Capture the remote note URL or ID when visible.

Classify the result:

- `reviewing`: located in content management with an exact title/cover/time match, but XHS still shows 审核中.
- `verified`: shown as 已发布 in content management or opened as a remote note and matched.
- `unknown`: the click may have succeeded, but no authoritative post record could be matched.
- `failed-after-click`: XHS showed a definite failure and a content-list check found no matching post.

### 6. Finalize the receipt

If XHS shows 审核中, transition to `reviewing` with the matched title, cover, and timestamp in `--detail`. After XHS shows 已发布 or the public note opens, transition to `verified`:

```bash
python3 scripts/share_to_xhs.py ledger transition \
  --payload /tmp/xhs-payload.json \
  --attempt-id ATTEMPT_ID \
  --state verified \
  --remote-url 'https://www.xiaohongshu.com/explore/...' \
  --detail 'Matched exact title and image count in creator content management'
```

Use `--state unknown --detail '...'` when evidence is incomplete. Never report `reviewing` as publicly live. The commands write `share/.publish/xhs-ledger.json` (or the rednote equivalent) atomically. The ledger stores hashes and audit events, not credentials or full post bodies. Do not edit the source README to mark publication.

## Cancellation and recovery

- Before Publish: leave the filled page open or save a draft when the user asks. If already armed, transition to `cancelled`.
- Login required: show the QR screenshot and pause. Resume in the same Chrome tab after the user confirms login.
- Browser disconnected: reconnect to Chrome and re-inspect the page before acting.
- Unknown publish result: transition to `unknown`, search content management by exact title, and do not click Publish again.
- Source changed after preparation: rerun `prepare`; never publish a stale payload.
- Repost requested: require explicit acknowledgement that the same revision was previously published, then use `--force` when arming the new attempt.
