#!/usr/bin/env python3
"""Validate local links, draft safety, required files, and source isolation."""

from __future__ import annotations

import re
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "_quarto.yml", "index.qmd", "research.qmd", "projects.qmd",
    "publications.qmd", "people.qmd", "about.qmd", "CONTENT_TODO.md",
    "HOW_TO_UPDATE.md", "data/pdf-manifest.yml", "data/publications.bib",
)
LINK = re.compile(r"(?<!!)\[[^]]*]\(([^)#]+)(?:#[^)]+)?\)")


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    sources = list((ROOT / "source-materials").rglob("*.pdf"))
    manifest = (ROOT / "data/pdf-manifest.yml").read_text(encoding="utf-8")
    for source in sources:
        relative = source.relative_to(ROOT).as_posix()
        if relative not in manifest:
            errors.append(f"PDF absent from manifest: {relative}")
            continue
        entry = re.search(rf'- source: "{re.escape(relative)}"\s+sha256:\s+([0-9a-f]{{64}})', manifest)
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if not entry or entry.group(1) != actual:
            errors.append(f"PDF hash differs from manifest: {relative}")

    for draft in [*ROOT.glob("projects/*.qmd"), *ROOT.glob("updates/*.qmd")]:
        if draft.name.startswith("_"):
            continue
        text = draft.read_text(encoding="utf-8")
        status = re.search(r"(?m)^status:\s*([^#\n]+)", text)
        is_draft = re.search(r"(?m)^draft:\s*true\s*$", text)
        if status and status.group(1).strip() in {"draft", "review"} and not is_draft:
            errors.append(f"Non-public record lacks draft: true: {draft.relative_to(ROOT)}")
        image = re.search(r"(?m)^image:\s*([^#\n]+)", text)
        image_alt = re.search(r"(?m)^image-alt:\s*([^#\n]+)", text)
        if image and (not image_alt or not image_alt.group(1).strip().strip('"')):
            errors.append(f"Image lacks alt text: {draft.relative_to(ROOT)}")
        if status and status.group(1).strip() == "published" and image_alt and "[IMAGE DESCRIPTION REQUIRED]" in image_alt.group(1):
            errors.append(f"Published image retains alt-text placeholder: {draft.relative_to(ROOT)}")

    checked = [*ROOT.rglob("*.qmd"), *ROOT.glob("*.md")]
    for document in checked:
        text = document.read_text(encoding="utf-8")
        for target in LINK.findall(text):
            if "://" in target or target.startswith(("mailto:", "#")):
                continue
            candidate = (document.parent / target).resolve()
            if not candidate.exists():
                errors.append(f"Broken link in {document.relative_to(ROOT)}: {target}")

    quarto = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    if not re.search(r"(?m)^\s*draft-mode:\s*gone\s*$", quarto):
        errors.append("Quarto must use draft-mode: gone to exclude review content")
    if "source-materials" in re.findall(r"(?m)^\s*-\s+(.+)$", quarto):
        errors.append("Source materials must not be configured as site resources")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Validated {len(checked)} content files and {len(sources)} manifested PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
