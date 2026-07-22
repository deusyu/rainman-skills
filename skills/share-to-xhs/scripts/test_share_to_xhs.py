#!/usr/bin/env python3

import json
import struct
import tempfile
import unittest
from pathlib import Path

from share_to_xhs import ShareError, ledger_arm, ledger_transition, parse_candidate, scan


def fake_png(path: Path, width: int = 1080, height: int = 1440, marker: bytes = b"") -> None:
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", width, height) + marker)


class ShareToXhsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_standard(self) -> tuple[Path, Path]:
        share = self.root / "project" / "share"
        chapter = share / "01-launch"
        chapter.mkdir(parents=True)
        share.joinpath("README.md").write_text("# Share\n\n1. **01-launch** — first\n", encoding="utf-8")
        chapter.joinpath("README.md").write_text(
            """# Launch

## Assets
- `x-only.png`

## Post-ready copy

### 小红书

```text
这是一个合规标题

第一段

第二段

#AI #学习方法
```

## Attach

X：`x-only.png`；小红书：`cover.png` 为主、`detail.png` 为辅。
""",
            encoding="utf-8",
        )
        fake_png(chapter / "x-only.png", marker=b"x")
        fake_png(chapter / "cover.png", marker=b"cover")
        fake_png(chapter / "detail.png", 1600, 900, marker=b"detail")
        return share, chapter

    def test_standard_schema_and_platform_attach_order(self) -> None:
        share, chapter = self.make_standard()
        payload = parse_candidate(chapter, "share-kit-v1", share)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["title"]["value"], "这是一个合规标题")
        self.assertEqual(payload["tags"], ["AI", "学习方法"])
        self.assertEqual([item["relative_path"] for item in payload["images"]], ["01-launch/cover.png", "01-launch/detail.png"])
        self.assertTrue(any(item["code"] == "LANDSCAPE_IMAGE" for item in payload["diagnostics"]))

    def test_scan_respects_root_and_finds_candidate(self) -> None:
        share, _ = self.make_standard()
        result = scan(share)
        self.assertEqual([item["item_key"] for item in result["candidates"]], ["01-launch"])
        self.assertEqual(result["candidates"][0]["status"], "ready")

    def test_long_title_is_invalid(self) -> None:
        share, chapter = self.make_standard()
        payload = parse_candidate(chapter, "share-kit-v1", share, title_override="一" * 21)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(any(item["code"] == "TITLE_TOO_LONG" for item in payload["diagnostics"]))

    def test_rednote_requires_title_and_preserves_carousel(self) -> None:
        share = self.root / "project" / "share-rednote"
        chapter = share / "01-topic"
        chapter.mkdir(parents=True)
        chapter.joinpath("note.md").write_text(
            """# Note

**封面**: `cover.jpg`

## 标题（选一个）
- 第一候选
- 第二候选

## 正文
正文内容

## 话题
#地理 #冷知识

## 轮播（按序发 2 张）
1. `cover.jpg` — cover
2. `detail.jpg` — detail
""",
            encoding="utf-8",
        )
        fake_png(chapter / "cover.jpg", marker=b"cover")
        fake_png(chapter / "detail.jpg", marker=b"detail")
        pending = parse_candidate(chapter, "rednote-v1", share)
        self.assertEqual(pending["status"], "needs_input")
        ready = parse_candidate(chapter, "rednote-v1", share, title_index=2)
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(ready["title"]["value"], "第二候选")
        self.assertEqual([item["relative_path"] for item in ready["images"]], ["01-topic/cover.jpg", "01-topic/detail.jpg"])

    def test_image_cannot_escape_share_root(self) -> None:
        share, chapter = self.make_standard()
        outside = self.root / "outside.png"
        fake_png(outside)
        readme = chapter / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("`cover.png` 为主、`detail.png`", "`../../../outside.png` 为主、`detail.png`"), encoding="utf-8")
        payload = parse_candidate(chapter, "share-kit-v1", share)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(any(item["code"] == "IMAGE_OUTSIDE_SHARE_ROOT" for item in payload["diagnostics"]))

    def test_ledger_blocks_duplicate_and_tracks_verified(self) -> None:
        share, chapter = self.make_standard()
        payload = parse_candidate(chapter, "share-kit-v1", share)
        payload_path = self.root / "payload.json"
        payload_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        armed = ledger_arm(payload_path, "xhs:test", "chrome", False, None)
        attempt_id = armed["attempt"]["attemptId"]
        with self.assertRaises(ShareError):
            ledger_arm(payload_path, "xhs:test", "chrome", False, None)
        submitted = ledger_transition(payload_path, attempt_id, "submitted", "Publish clicked once", None, None, None)
        self.assertEqual(submitted["attempt"]["state"], "submitted")
        reviewing = ledger_transition(payload_path, attempt_id, "reviewing", "Matched exact title with reviewing status", None, None, None)
        self.assertEqual(reviewing["attempt"]["state"], "reviewing")
        verified = ledger_transition(payload_path, attempt_id, "verified", "Matched exact title in published content list", "https://example.test/note", "note-1", None)
        self.assertEqual(verified["attempt"]["state"], "verified")


if __name__ == "__main__":
    unittest.main()
