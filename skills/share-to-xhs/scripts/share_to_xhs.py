#!/usr/bin/env python3
"""Normalize share-kit posts and maintain an XHS publication ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
MIME_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
BLOCKING_LEDGER_STATES = {"armed", "submitted", "reviewing", "unknown", "verified"}
ALLOWED_TRANSITIONS = {
    "armed": {"submitted", "cancelled", "failed-before-click"},
    "submitted": {"reviewing", "verified", "unknown", "failed-after-click"},
    "reviewing": {"verified", "unknown", "failed-after-click"},
    "unknown": {"verified", "failed-after-click"},
}


class ShareError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", value.lstrip("\ufeff"))


def read_text(path: Path) -> str:
    try:
        return normalize_text(path.read_bytes().decode("utf-8-sig", errors="strict"))
    except (OSError, UnicodeError) as exc:
        raise ShareError(f"Cannot read UTF-8 Markdown {path}: {exc}") from exc


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def stable_json_hash(value: Any) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(data.encode("utf-8"))


def grapheme_approx(value: str) -> int:
    """Count visible clusters closely enough for preflight; the web counter is final."""
    count = 0
    join_next = False
    for char in normalize_text(value):
        code = ord(char)
        if char == "\u200d":
            join_next = True
            continue
        if unicodedata.combining(char) or 0xFE00 <= code <= 0xFE0F:
            continue
        if join_next:
            join_next = False
            continue
        count += 1
    return count


def utf16_units(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def diagnostic(level: str, code: str, message: str) -> dict[str, str]:
    return {"level": level, "code": code, "message": message}


def heading_sections(text: str, title_pattern: str, level: int = 2) -> list[str]:
    lines = text.splitlines()
    target = re.compile(title_pattern, re.IGNORECASE)
    hits: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if not match or len(match.group(1)) != level or not target.fullmatch(match.group(2)):
            continue
        collected: list[str] = []
        for following in lines[index + 1 :]:
            next_heading = re.match(r"^(#{1,6})\s+", following)
            if next_heading and len(next_heading.group(1)) <= level:
                break
            collected.append(following)
        hits.append("\n".join(collected).strip("\n"))
    return hits


def xhs_fenced_blocks(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[str] = []
    for index, line in enumerate(lines):
        if not re.fullmatch(r"###\s+小红书\s*", line):
            continue
        section: list[str] = []
        for following in lines[index + 1 :]:
            if re.match(r"^#{1,3}\s+", following):
                break
            section.append(following)
        fences: list[str] = []
        cursor = 0
        while cursor < len(section):
            opening = re.fullmatch(r"```\s*([A-Za-z0-9_-]*)\s*", section[cursor])
            if not opening:
                cursor += 1
                continue
            language = opening.group(1).lower()
            end = cursor + 1
            while end < len(section) and not re.fullmatch(r"```\s*", section[end]):
                end += 1
            if end >= len(section):
                raise ShareError("Unclosed fenced block under ### 小红书")
            if language in {"", "text"}:
                fences.append("\n".join(section[cursor + 1 : end]).strip("\n"))
            cursor = end + 1
        if len(fences) != 1:
            raise ShareError(f"Expected one text fence under ### 小红书, found {len(fences)}")
        blocks.append(fences[0])
    return blocks


def extract_backticked_images(value: str) -> list[str]:
    result: list[str] = []
    for candidate in re.findall(r"`([^`]+)`", value):
        candidate = candidate.strip()
        if Path(candidate).suffix.lower() in IMAGE_SUFFIXES:
            result.append(candidate)
    return result


def resolve_image_paths(raw_paths: list[str], chapter: Path, share_root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    images: list[Path] = []
    diagnostics: list[dict[str, str]] = []
    seen: set[Path] = set()
    resolved_root = share_root.resolve()
    for raw_path in raw_paths:
        resolved = (chapter / raw_path).resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            diagnostics.append(diagnostic("error", "IMAGE_OUTSIDE_SHARE_ROOT", f"Image escapes share root: {raw_path}"))
            continue
        if resolved in seen:
            diagnostics.append(diagnostic("error", "DUPLICATE_IMAGE", f"Image is listed more than once: {raw_path}"))
            continue
        seen.add(resolved)
        if not resolved.is_file():
            diagnostics.append(diagnostic("error", "IMAGE_MISSING", f"Image does not exist: {resolved}"))
            continue
        if resolved.stat().st_size <= 0:
            diagnostics.append(diagnostic("error", "IMAGE_EMPTY", f"Image is empty: {resolved}"))
            continue
        images.append(resolved)
    return images, diagnostics


def jpeg_size(path: Path) -> tuple[int, int] | None:
    sof_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    with path.open("rb") as handle:
        if handle.read(2) != b"\xff\xd8":
            return None
        while True:
            byte = handle.read(1)
            if not byte:
                return None
            if byte != b"\xff":
                continue
            marker_byte = handle.read(1)
            while marker_byte == b"\xff":
                marker_byte = handle.read(1)
            if not marker_byte:
                return None
            marker = marker_byte[0]
            if marker in {0xD8, 0xD9}:
                continue
            length_raw = handle.read(2)
            if len(length_raw) != 2:
                return None
            length = int.from_bytes(length_raw, "big")
            if length < 2:
                return None
            if marker in sof_markers:
                data = handle.read(length - 2)
                if len(data) < 5:
                    return None
                return int.from_bytes(data[3:5], "big"), int.from_bytes(data[1:3], "big")
            handle.seek(length - 2, os.SEEK_CUR)


def image_size(path: Path) -> tuple[int | None, int | None]:
    with path.open("rb") as handle:
        header = handle.read(32)
    if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
        return struct.unpack(">II", header[16:24])
    if header.startswith(b"\xff\xd8"):
        size = jpeg_size(path)
        return size if size else (None, None)
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP" and header[12:16] == b"VP8X" and len(header) >= 30:
        width = int.from_bytes(header[24:27], "little") + 1
        height = int.from_bytes(header[27:30], "little") + 1
        return width, height
    return None, None


def image_records(images: list[Path], share_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records: list[dict[str, Any]] = []
    diagnostics: list[dict[str, str]] = []
    for index, path in enumerate(images):
        width, height = image_size(path)
        if width is None or height is None:
            diagnostics.append(diagnostic("warning", "IMAGE_DIMENSIONS_UNKNOWN", f"Could not read image dimensions: {path}"))
        record = {
            "relative_path": path.relative_to(share_root.resolve()).as_posix(),
            "absolute_path": str(path),
            "role": "cover" if index == 0 else "carousel",
            "mime": MIME_BY_SUFFIX[path.suffix.lower()],
            "bytes": path.stat().st_size,
            "width": width,
            "height": height,
            "sha256": sha256_file(path),
        }
        records.append(record)
        if width and height:
            if width > height:
                diagnostics.append(diagnostic("warning", "LANDSCAPE_IMAGE", f"Landscape image will need visual crop review: {path.name} ({width}x{height})"))
            if width < 1080:
                diagnostics.append(diagnostic("warning", "NARROW_IMAGE", f"Image width is below 1080 px: {path.name} ({width}x{height})"))
            if index == 0 and abs((width / height) - 0.75) > 0.08:
                diagnostics.append(diagnostic("warning", "COVER_NOT_3_4", f"Cover is not close to 3:4: {path.name} ({width}x{height})"))
    ratios = {round(record["width"] / record["height"], 2) for record in records if record["width"] and record["height"]}
    if len(ratios) > 1:
        diagnostics.append(diagnostic("warning", "MIXED_ASPECT_RATIOS", "Images use mixed aspect ratios; inspect the Chrome preview carefully"))
    return records, diagnostics


def parse_standard(chapter: Path, share_root: Path, title_override: str | None) -> dict[str, Any]:
    source = chapter / "README.md"
    text = read_text(source)
    blocks = xhs_fenced_blocks(text)
    if not blocks:
        return {"status": "not_xhs_ready", "diagnostics": [diagnostic("warning", "NO_XHS_COPY", "No ### 小红书 block found")]}
    if len(blocks) != 1:
        raise ShareError(f"Expected one ### 小红书 block, found {len(blocks)}")

    block_lines = blocks[0].splitlines()
    nonempty = [index for index, value in enumerate(block_lines) if value.strip()]
    diagnostics: list[dict[str, str]] = []
    if len(nonempty) < 3:
        raise ShareError("XHS block must contain a title, body, and trailing hashtag line")
    title_index = nonempty[0]
    if title_index + 1 >= len(block_lines) or block_lines[title_index + 1].strip():
        diagnostics.append(diagnostic("error", "TITLE_BODY_SEPARATOR", "Title must be followed by a blank line"))
    tag_index = nonempty[-1]
    tag_line = block_lines[tag_index].strip()
    if not re.fullmatch(r"(?:#[^\s#]+(?:\s+|$))+", tag_line):
        diagnostics.append(diagnostic("error", "INVALID_TAG_LINE", "Last non-empty line must contain only #hashtags"))
        tags: list[str] = []
    else:
        tags = re.findall(r"#([^\s#]+)", tag_line)

    source_title = block_lines[title_index].strip()
    title = normalize_text(title_override.strip()) if title_override else source_title
    body = "\n".join(block_lines[title_index + 1 : tag_index]).strip("\n")
    if not body.strip():
        diagnostics.append(diagnostic("error", "BODY_EMPTY", "Body is empty"))

    attach_sections = heading_sections(text, r"Attach", level=2)
    if len(attach_sections) != 1:
        diagnostics.append(diagnostic("error", "ATTACH_SECTION_COUNT", f"Expected one ## Attach section, found {len(attach_sections)}"))
        raw_images: list[str] = []
    else:
        clauses = [part.strip() for part in re.split(r"[；;\n]+", attach_sections[0]) if part.strip()]
        xhs_clauses = [part for part in clauses if re.search(r"小红书\s*[：:]", part)]
        attach_source = "\n".join(re.split(r"小红书\s*[：:]", part, maxsplit=1)[1] for part in xhs_clauses) if xhs_clauses else attach_sections[0]
        raw_images = extract_backticked_images(attach_source)
    images, image_errors = resolve_image_paths(raw_images, chapter, share_root)
    diagnostics.extend(image_errors)
    return build_payload(
        chapter=chapter,
        share_root=share_root,
        schema="share-kit-v1",
        source=source,
        source_text=text,
        title=title,
        title_origin="override" if title_override else "fixed",
        title_options=[source_title],
        selected_title=1 if not title_override else None,
        body=body,
        tags=tags,
        images=images,
        diagnostics=diagnostics,
    )


def parse_rednote(chapter: Path, share_root: Path, title_index: int | None, title_override: str | None) -> dict[str, Any]:
    source = chapter / "note.md"
    text = read_text(source)
    diagnostics: list[dict[str, str]] = []

    title_sections = heading_sections(text, r"标题(?:（选一个）|\(选一个\))?", level=2)
    body_sections = heading_sections(text, r"正文", level=2)
    topic_sections = heading_sections(text, r"话题", level=2)
    carousel_sections = heading_sections(text, r"轮播.*", level=2)
    for label, sections in (("title", title_sections), ("body", body_sections), ("topics", topic_sections), ("carousel", carousel_sections)):
        if len(sections) != 1:
            diagnostics.append(diagnostic("error", "SECTION_COUNT", f"Expected one {label} section, found {len(sections)}"))

    title_options = re.findall(r"^\s*-\s+(.+?)\s*$", title_sections[0], re.MULTILINE) if len(title_sections) == 1 else []
    title_options = [normalize_text(value.strip()) for value in title_options]
    if not title_options:
        diagnostics.append(diagnostic("error", "TITLE_OPTIONS_EMPTY", "No title choices found"))

    selected_title: int | None = None
    if title_override:
        title = normalize_text(title_override.strip())
        title_origin = "override"
    elif title_index is not None:
        if title_index < 1 or title_index > len(title_options):
            diagnostics.append(diagnostic("error", "TITLE_INDEX_RANGE", f"Title index {title_index} is outside 1..{len(title_options)}"))
            title = ""
        else:
            title = title_options[title_index - 1]
            selected_title = title_index
        title_origin = "candidate"
    elif len(title_options) == 1:
        title = title_options[0]
        selected_title = 1
        title_origin = "candidate"
    else:
        title = ""
        title_origin = "candidate"
        diagnostics.append(diagnostic("error", "TITLE_SELECTION_REQUIRED", "Choose a title with --title-index or --title"))

    body = body_sections[0].strip("\n") if len(body_sections) == 1 else ""
    if not body.strip():
        diagnostics.append(diagnostic("error", "BODY_EMPTY", "Body is empty"))

    topic_text = topic_sections[0].strip() if len(topic_sections) == 1 else ""
    if topic_text and not re.fullmatch(r"(?:#[^\s#]+(?:\s+|$))+", " ".join(topic_text.splitlines())):
        diagnostics.append(diagnostic("error", "INVALID_TOPICS", "Topic section must contain only #hashtags"))
    tags = re.findall(r"#([^\s#]+)", topic_text)

    raw_images: list[str] = []
    numbers: list[int] = []
    if len(carousel_sections) == 1:
        for line in carousel_sections[0].splitlines():
            item = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
            if not item:
                continue
            paths = extract_backticked_images(item.group(2))
            if len(paths) != 1:
                diagnostics.append(diagnostic("error", "CAROUSEL_IMAGE_COUNT", f"Carousel line must reference one image: {line.strip()}"))
                continue
            numbers.append(int(item.group(1)))
            raw_images.append(paths[0])
        if numbers != list(range(1, len(numbers) + 1)):
            diagnostics.append(diagnostic("error", "CAROUSEL_SEQUENCE", f"Carousel numbering must be continuous from 1, found {numbers}"))

    cover_match = re.search(r"\*\*封面\*\*\s*[：:]\s*`([^`]+)`", text)
    if cover_match and raw_images and cover_match.group(1).strip() != raw_images[0]:
        diagnostics.append(diagnostic("error", "COVER_ORDER", "The declared cover must be the first carousel image"))

    images, image_errors = resolve_image_paths(raw_images, chapter, share_root)
    diagnostics.extend(image_errors)
    return build_payload(
        chapter=chapter,
        share_root=share_root,
        schema="rednote-v1",
        source=source,
        source_text=text,
        title=title,
        title_origin=title_origin,
        title_options=title_options,
        selected_title=selected_title,
        body=body,
        tags=tags,
        images=images,
        diagnostics=diagnostics,
    )


def build_payload(
    *,
    chapter: Path,
    share_root: Path,
    schema: str,
    source: Path,
    source_text: str,
    title: str,
    title_origin: str,
    title_options: list[str],
    selected_title: int | None,
    body: str,
    tags: list[str],
    images: list[Path],
    diagnostics: list[dict[str, str]],
) -> dict[str, Any]:
    title = normalize_text(title.strip())
    body = normalize_text(body.strip("\n"))
    tags = [normalize_text(tag.strip().lstrip("#")) for tag in tags if tag.strip().lstrip("#")]
    image_data, image_diagnostics = image_records(images, share_root)
    diagnostics.extend(image_diagnostics)

    title_length = grapheme_approx(title) if title else 0
    if not title:
        if not any(item["code"] == "TITLE_SELECTION_REQUIRED" for item in diagnostics):
            diagnostics.append(diagnostic("error", "TITLE_EMPTY", "Title is empty"))
    elif title_length > 20:
        diagnostics.append(diagnostic("error", "TITLE_TOO_LONG", f"Title is {title_length} visible units; XHS limit is 20"))
    elif title_length == 20:
        diagnostics.append(diagnostic("warning", "TITLE_AT_LIMIT", "Title is exactly 20 visible units; verify the web counter"))
    if utf16_units(title) > 20 and title_length <= 20:
        diagnostics.append(diagnostic("warning", "TITLE_UTF16_LONG", "Emoji or surrogate pairs make the title exceed 20 UTF-16 units; verify the web counter"))
    if grapheme_approx(body) > 1000:
        diagnostics.append(diagnostic("error", "BODY_TOO_LONG", f"Body is {grapheme_approx(body)} visible units; configured limit is 1000"))
    if not tags:
        diagnostics.append(diagnostic("error", "TAGS_EMPTY", "At least one topic tag is required"))
    if len(tags) > 10:
        diagnostics.append(diagnostic("error", "TOO_MANY_TAGS", f"Found {len(tags)} tags; configured limit is 10"))
    if not 1 <= len(image_data) <= 18:
        diagnostics.append(diagnostic("error", "IMAGE_COUNT", f"Image count must be 1..18, found {len(image_data)}"))
    if re.search(r"(?:https?://|www\.)", title + "\n" + body, re.IGNORECASE):
        diagnostics.append(diagnostic("error", "URL_IN_COPY", "Title/body contains a URL"))

    source_document = source.resolve().relative_to(share_root.resolve()).as_posix()
    source_hash = stable_json_hash({"source_document": source_document, "markdown": source_text})
    payload_hash = stable_json_hash(
        {
            "title": title,
            "body": body,
            "tags": tags,
            "images": [item["sha256"] for item in image_data],
        }
    ) if title else None
    errors = [item for item in diagnostics if item["level"] == "error"]
    status = "needs_input" if errors and all(item["code"] == "TITLE_SELECTION_REQUIRED" for item in errors) else ("invalid" if errors else "ready")
    root_name = share_root.name
    project_name = share_root.parent.name
    rendered = body + ("\n\n" + " ".join(f"#{tag}" for tag in tags) if tags else "")
    return {
        "version": SCHEMA_VERSION,
        "id": f"{project_name}/{root_name}/{chapter.name}",
        "item_key": chapter.name,
        "schema": schema,
        "source_document": source_document,
        "source_path": str(source.resolve()),
        "share_root": str(share_root.resolve()),
        "title": {
            "value": title or None,
            "origin": title_origin,
            "options": [
                {
                    "index": index + 1,
                    "value": option,
                    "graphemes": grapheme_approx(option),
                    "utf16_units": utf16_units(option),
                    "valid": grapheme_approx(option) <= 20,
                }
                for index, option in enumerate(title_options)
            ],
            "selected_option": selected_title,
            "graphemes": title_length if title else None,
            "utf16_units": utf16_units(title) if title else None,
        },
        "body": body,
        "tags": tags,
        "rendered_content": rendered,
        "images": image_data,
        "source_hash": source_hash,
        "payload_hash": payload_hash,
        "status": status,
        "diagnostics": diagnostics,
        "prepared_at": utc_now(),
    }


def detect_candidate(chapter: Path) -> str | None:
    if (chapter / "note.md").is_file():
        return "rednote-v1"
    if (chapter / "README.md").is_file():
        return "share-kit-v1"
    return None


def posting_order(root: Path) -> list[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return []
    text = read_text(readme)
    return re.findall(r"^\s*\d+\.\s+\*\*([^*]+)\*\*", text, re.MULTILINE)


def discover(path: Path) -> tuple[Path, list[tuple[Path, str]]]:
    path = path.resolve()
    if path.is_file():
        chapter = path.parent
        kind = "rednote-v1" if path.name == "note.md" else "share-kit-v1" if path.name == "README.md" else None
        if not kind:
            raise ShareError("Input file must be README.md or note.md")
        return chapter.parent, [(chapter, kind)]
    if not path.is_dir():
        raise ShareError(f"Path does not exist or is not a directory: {path}")
    direct_kind = detect_candidate(path)
    direct_text = read_text(path / "README.md") if direct_kind == "share-kit-v1" else ""
    if direct_kind == "rednote-v1" or (direct_kind == "share-kit-v1" and re.search(r"^###\s+小红书\s*$", direct_text, re.MULTILINE)):
        return path.parent, [(path, direct_kind)]

    children = [(child, kind) for child in path.iterdir() if child.is_dir() and (kind := detect_candidate(child))]
    order = posting_order(path)
    order_index = {name: index for index, name in enumerate(order)}

    def sort_key(item: tuple[Path, str]) -> tuple[int, int, str]:
        name = item[0].name
        numeric = re.match(r"^(\d+)", name)
        return (order_index.get(name, 10_000), int(numeric.group(1)) if numeric else 10_000, name)

    children.sort(key=sort_key)
    return path, children


def parse_candidate(chapter: Path, kind: str, share_root: Path, title_index: int | None = None, title_override: str | None = None) -> dict[str, Any]:
    if kind == "rednote-v1":
        return parse_rednote(chapter, share_root, title_index, title_override)
    return parse_standard(chapter, share_root, title_override)


def scan(path: Path) -> dict[str, Any]:
    root, candidates = discover(path)
    output: list[dict[str, Any]] = []
    for chapter, kind in candidates:
        try:
            payload = parse_candidate(chapter, kind, root)
            output.append(
                {
                    "item_key": chapter.name,
                    "schema": kind,
                    "source_path": payload.get("source_path", str(chapter)),
                    "status": payload["status"],
                    "title": payload.get("title"),
                    "image_count": len(payload.get("images", [])),
                    "diagnostics": payload.get("diagnostics", []),
                }
            )
        except ShareError as exc:
            output.append(
                {
                    "item_key": chapter.name,
                    "schema": kind,
                    "source_path": str(chapter),
                    "status": "invalid",
                    "title": None,
                    "image_count": 0,
                    "diagnostics": [diagnostic("error", "PARSE_ERROR", str(exc))],
                }
            )
    return {"version": SCHEMA_VERSION, "root": str(root), "candidates": output}


def choose_candidate(path: Path, chapter_name: str | None) -> tuple[Path, Path, str]:
    root, candidates = discover(path)
    if chapter_name:
        matches = [item for item in candidates if item[0].name == chapter_name]
        if not matches:
            raise ShareError(f"Chapter not found: {chapter_name}")
        chapter, kind = matches[0]
        return root, chapter, kind
    if len(candidates) != 1:
        raise ShareError(f"Path contains {len(candidates)} candidates; select one with --chapter")
    chapter, kind = candidates[0]
    return root, chapter, kind


def default_ledger_path(share_root: Path) -> Path:
    return share_root / ".publish" / "xhs-ledger.json"


def read_ledger(path: Path, allow_missing: bool = True) -> dict[str, Any]:
    if not path.exists():
        if allow_missing:
            return {"version": SCHEMA_VERSION, "platform": "xiaohongshu", "attempts": []}
        raise ShareError(f"Ledger does not exist: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShareError(f"Ledger is unreadable; refusing to overwrite {path}: {exc}") from exc
    if value.get("version") != SCHEMA_VERSION or value.get("platform") != "xiaohongshu" or not isinstance(value.get("attempts"), list):
        raise ShareError(f"Ledger schema is invalid; refusing to overwrite {path}")
    return value


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def read_payload(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShareError(f"Cannot read payload {path}: {exc}") from exc
    if payload.get("version") != SCHEMA_VERSION or payload.get("status") != "ready" or not payload.get("payload_hash"):
        raise ShareError("Payload is not a ready share-to-xhs payload")
    return payload


def assert_payload_fresh(payload: dict[str, Any]) -> None:
    share_root = Path(payload["share_root"]).resolve()
    source = Path(payload["source_path"]).resolve()
    source_hash = stable_json_hash({"source_document": payload["source_document"], "markdown": read_text(source)})
    if source_hash != payload["source_hash"]:
        raise ShareError("Source Markdown changed after preparation; prepare again")
    for image in payload["images"]:
        path = Path(image["absolute_path"]).resolve()
        try:
            path.relative_to(share_root)
        except ValueError as exc:
            raise ShareError(f"Payload image escapes share root: {path}") from exc
        if not path.is_file() or sha256_file(path) != image["sha256"]:
            raise ShareError(f"Payload image changed after preparation: {path}")


def ledger_arm(payload_path: Path, account_key: str, backend: str, force: bool, ledger_override: Path | None) -> dict[str, Any]:
    payload = read_payload(payload_path)
    assert_payload_fresh(payload)
    ledger_path = ledger_override or default_ledger_path(Path(payload["share_root"]))
    ledger = read_ledger(ledger_path)
    conflicts = [
        attempt
        for attempt in ledger["attempts"]
        if attempt.get("accountKey") == account_key
        and attempt.get("payloadHash") == payload["payload_hash"]
        and attempt.get("state") in BLOCKING_LEDGER_STATES
    ]
    if conflicts and not force:
        details = ", ".join(f"{item['attemptId']}:{item['state']}" for item in conflicts)
        raise ShareError(f"Same payload is already blocked for this account ({details}); verify before retrying")
    now = utc_now()
    attempt_id = str(uuid.uuid4())
    attempt = {
        "attemptId": attempt_id,
        "itemKey": payload["item_key"],
        "postId": payload["id"],
        "sourceDocument": payload["source_document"],
        "sourceHash": payload["source_hash"],
        "payloadHash": payload["payload_hash"],
        "accountKey": account_key,
        "title": payload["title"]["value"],
        "images": [{"path": item["relative_path"], "sha256": item["sha256"]} for item in payload["images"]],
        "backend": backend,
        "state": "armed",
        "createdAt": now,
        "updatedAt": now,
        "events": [{"state": "armed", "at": now, "detail": "Final preview approved; publish action armed"}],
    }
    ledger["attempts"].append(attempt)
    ledger["updatedAt"] = now
    atomic_write_json(ledger_path, ledger)
    return {"ledger": str(ledger_path), "attempt": attempt}


def ledger_transition(
    payload_path: Path,
    attempt_id: str,
    state: str,
    detail: str | None,
    remote_url: str | None,
    remote_id: str | None,
    ledger_override: Path | None,
) -> dict[str, Any]:
    payload = read_payload(payload_path)
    ledger_path = ledger_override or default_ledger_path(Path(payload["share_root"]))
    ledger = read_ledger(ledger_path, allow_missing=False)
    matches = [item for item in ledger["attempts"] if item.get("attemptId") == attempt_id]
    if len(matches) != 1:
        raise ShareError(f"Attempt ID must match exactly one ledger entry: {attempt_id}")
    attempt = matches[0]
    current = attempt.get("state")
    if state not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ShareError(f"Invalid ledger transition: {current} -> {state}")
    if state in {"reviewing", "verified", "unknown", "failed-after-click", "failed-before-click"} and not detail:
        raise ShareError(f"--detail is required for state {state}")
    now = utc_now()
    event: dict[str, Any] = {"state": state, "at": now}
    if detail:
        event["detail"] = detail
    if remote_url:
        event["remoteUrl"] = remote_url
        attempt["remoteUrl"] = remote_url
    if remote_id:
        event["remoteId"] = remote_id
        attempt["remoteId"] = remote_id
    attempt["events"].append(event)
    attempt["state"] = state
    attempt["updatedAt"] = now
    ledger["updatedAt"] = now
    atomic_write_json(ledger_path, ledger)
    return {"ledger": str(ledger_path), "attempt": attempt}


def emit_json(value: Any, output: Path | None = None) -> None:
    if output:
        atomic_write_json(output, value)
        print(output)
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2))


def print_scan_human(result: dict[str, Any]) -> None:
    print(f"Root: {result['root']}")
    for item in result["candidates"]:
        title = item.get("title") or {}
        value = title.get("value") if isinstance(title, dict) else None
        options = len(title.get("options", [])) if isinstance(title, dict) else 0
        suffix = f" — {value}" if value else f" — {options} title choices" if options else ""
        print(f"{item['item_key']}: {item['status']} ({item['image_count']} images){suffix}")
        for diag in item["diagnostics"]:
            print(f"  {diag['level'].upper()} {diag['code']}: {diag['message']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare share-kit content for safe Xiaohongshu publishing")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Discover XHS-ready share items")
    scan_parser.add_argument("path", type=Path)
    scan_parser.add_argument("--json", action="store_true", help="Print JSON instead of a human summary")

    prepare_parser = subparsers.add_parser("prepare", help="Normalize and validate one share item")
    prepare_parser.add_argument("path", type=Path)
    prepare_parser.add_argument("--chapter")
    title_group = prepare_parser.add_mutually_exclusive_group()
    title_group.add_argument("--title-index", type=int)
    title_group.add_argument("--title")
    prepare_parser.add_argument("--output", type=Path)

    ledger_parser = subparsers.add_parser("ledger", help="Maintain the duplicate-protection ledger")
    ledger_sub = ledger_parser.add_subparsers(dest="ledger_command", required=True)

    arm_parser = ledger_sub.add_parser("arm", help="Record approval immediately before clicking Publish")
    arm_parser.add_argument("--payload", required=True, type=Path)
    arm_parser.add_argument("--account-key", required=True)
    arm_parser.add_argument("--backend", default="chrome")
    arm_parser.add_argument("--ledger", type=Path)
    arm_parser.add_argument("--force", action="store_true")

    transition_parser = ledger_sub.add_parser("transition", help="Advance one publish attempt")
    transition_parser.add_argument("--payload", required=True, type=Path)
    transition_parser.add_argument("--attempt-id", required=True)
    transition_parser.add_argument("--state", required=True, choices=sorted({value for values in ALLOWED_TRANSITIONS.values() for value in values}))
    transition_parser.add_argument("--detail")
    transition_parser.add_argument("--remote-url")
    transition_parser.add_argument("--remote-id")
    transition_parser.add_argument("--ledger", type=Path)

    show_parser = ledger_sub.add_parser("show", help="Print an existing ledger")
    show_parser.add_argument("path", type=Path, help="Share root or ledger JSON path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "scan":
            result = scan(args.path)
            if args.json:
                emit_json(result)
            else:
                print_scan_human(result)
            return 0
        if args.command == "prepare":
            root, chapter, kind = choose_candidate(args.path, args.chapter)
            result = parse_candidate(chapter, kind, root, args.title_index, args.title)
            emit_json(result, args.output)
            return 0 if result["status"] == "ready" else 2
        if args.command == "ledger" and args.ledger_command == "arm":
            emit_json(ledger_arm(args.payload, args.account_key, args.backend, args.force, args.ledger))
            return 0
        if args.command == "ledger" and args.ledger_command == "transition":
            emit_json(
                ledger_transition(
                    args.payload,
                    args.attempt_id,
                    args.state,
                    args.detail,
                    args.remote_url,
                    args.remote_id,
                    args.ledger,
                )
            )
            return 0
        if args.command == "ledger" and args.ledger_command == "show":
            ledger_path = args.path if args.path.suffix == ".json" else default_ledger_path(args.path)
            emit_json(read_ledger(ledger_path, allow_missing=False))
            return 0
        raise ShareError("Unsupported command")
    except ShareError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
