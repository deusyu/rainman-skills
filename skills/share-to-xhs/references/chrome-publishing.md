# Chrome publishing and verification

Use the installed Chrome-control capability and the user's existing Chrome session. In Codex, load and follow `chrome:control-chrome` completely before acting. Do not substitute standalone Playwright, a headless profile, CDP scripts, or cookie extraction. If the runtime exposes no controllable Chrome, stop and explain the missing dependency.

Before each click, fill, or upload, take a fresh semantic/DOM snapshot. Use a locator only when it is visibly correct and unique; verify `count() == 1` when ambiguity is possible. Never use a positional shortcut such as `first()` or `nth()` merely to bypass ambiguity. After each action, verify the cheapest authoritative result: field value, uploaded-thumbnail count, route change, or success state.

## Login

1. Navigate to the official Xiaohongshu creator site: `https://creator.xiaohongshu.com/`.
2. Inspect the visible page before interacting.
3. If XHS shows QR login, take a clear screenshot containing the full QR code and login instructions.
4. Send the screenshot to the user and explicitly ask them to scan it and finish login in Chrome.
5. Wait for the user to say login is complete, then inspect the same tab again.
6. Check the visible account name when available. If account identity is ambiguous, ask before publishing.

Do not read cookies, local storage, passwords, browser profiles, or session files.

## Fill-only stage

1. Enter image-and-text note publishing, not video publishing.
2. Upload every absolute local image path in payload order.
3. Wait for all thumbnails and upload indicators to finish.
4. Verify thumbnail count and order against the payload. Do not drag-reorder unless the source order was wrong and the user approves the correction.
5. Fill the exact title.
6. Fill the exact body.
7. Add the exact topics. Prefer the site's topic selector when it is available; otherwise append the normalized `#topic` tokens exactly once in the supported editor field.
8. Leave optional commercial, location, collection, visibility, originality, and scheduling controls at their current/default values unless the user supplied values.
9. Inspect visible validation counters and errors.
10. Take a screenshot of the completed creator page before publishing.

Do not hard-code selectors in the skill. Inspect the current accessibility/DOM state because XHS changes its creator UI.

## Irreversible action

Click Publish only when:

- The user has just confirmed while the fully filled creator-page preview is visible.
- All uploads finished.
- Title, body, topics, image count, and image order match the payload.
- No blocking validation or account ambiguity remains.

Click once. If the response is slow or ambiguous, wait and inspect; never click a second time merely because no immediate success banner appeared.

## Verification

A toast alone is weak evidence. Require a matching creator content-management entry, plus at least one of a success message or navigation away from the publish route. Prefer these authoritative states, strongest first:

1. Opened remote note page with matching title, body/topics, and image count.
2. Creator content-management entry with matching exact title, timestamp, and image count/status.
3. Explicit success route plus a matching newly created content entry.

Capture the note URL or ID when possible. If the exact entry is present but marked 审核中, classify it as `reviewing`, not publicly live. If only a transient success message appears and no content entry can be matched, classify the outcome as `unknown`.

If publishing definitely fails, search the content list once before retrying. A network/UI error can occur after the server accepted the post.
