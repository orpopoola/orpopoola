#!/usr/bin/env python3
"""Build the small public relationship index used by theme/project cards."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scalar(front: str, key: str) -> str:
    match = re.search(rf'(?m)^{re.escape(key)}:\s*["\']?([^\n"\']+)', front)
    return match.group(1).strip() if match else ""


def sequence(front: str, key: str) -> list[str]:
    inline = re.search(rf'(?m)^{re.escape(key)}:\s*\[([^]]*)\]', front)
    if inline:
        return [item.strip().strip('"\'') for item in inline.group(1).split(",") if item.strip()]
    block = re.search(rf'(?ms)^{re.escape(key)}:\s*\n((?:\s+-\s+[^\n]+\n?)+)', front)
    return [item.strip().strip('"\'') for item in re.findall(r'(?m)^\s+-\s+(.+)$', block.group(1))] if block else []


def record(path: Path, kind: str) -> dict[str, object] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    front = parts[1]
    if scalar(front, "status") != "published" or scalar(front, "draft").casefold() != "false":
        return None
    return {
        "kind": kind,
        "title": scalar(front, "title"),
        "description": scalar(front, "description"),
        "date": scalar(front, "date"),
        "themes": sequence(front, "categories"),
        "project": scalar(front, "project"),
        "featured": scalar(front, "featured").casefold() == "true",
        "image": scalar(front, "image"),
        "image_alt": scalar(front, "image-alt"),
        "href": path.relative_to(ROOT).with_suffix(".html").as_posix(),
    }


def main() -> int:
    entries = []
    for folder, kind in (("projects", "project"), ("updates", "update")):
        for path in sorted((ROOT / folder).glob("*.qmd")):
            if not path.name.startswith("_") and (item := record(path, kind)):
                entries.append(item)
    entries.sort(key=lambda item: (str(item["date"]), str(item["title"])), reverse=True)
    destination = ROOT / "data/content-index.json"
    destination.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"Indexed {len(entries)} published content records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
