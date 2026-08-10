#!/usr/bin/env python3
"""Validate local links, draft safety, required files, and source isolation."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_URL = "https://orpopoola.github.io/"
LEGACY_SEGMENT = "orpopoola"
LEGACY_SITE_REFERENCES = (
    f"https://orpopoola.github.io/{LEGACY_SEGMENT}",
    f'"/{LEGACY_SEGMENT}/',
    f"'/{LEGACY_SEGMENT}/",
)
REQUIRED = (
    "_quarto.yml", "index.qmd", "research.qmd", "projects.qmd",
    "publications.qmd", "people.qmd", "about.qmd", "CONTENT_TODO.md",
    "HOW_TO_UPDATE.md", "data/pdf-manifest.yml", "data/publications.bib",
)
LINK = re.compile(r"(?<!!)\[[^]]*]\(([^)#]+)(?:#[^)]+)?\)")


class AssetLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        attribute = "href" if tag in {"a", "link"} else "src" if tag in {"img", "script", "source"} else None
        if attribute and values.get(attribute):
            self.targets.append(values[attribute] or "")


def validate_rendered_site(output: Path) -> list[str]:
    errors: list[str] = []
    if not output.is_dir():
        return [f"Rendered site directory does not exist: {output}"]
    for html in output.rglob("*.html"):
        text = html.read_text(encoding="utf-8", errors="replace")
        for legacy in LEGACY_SITE_REFERENCES:
            if legacy in text:
                errors.append(f"Legacy project-site path in rendered file {html.relative_to(output)}")
        parser = AssetLinkParser()
        parser.feed(text)
        for target in parser.targets:
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean or clean.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
                continue
            candidate = output / clean.lstrip("/") if clean.startswith("/") else html.parent / clean
            if candidate.is_dir():
                candidate /= "index.html"
            if not candidate.exists():
                errors.append(f"Broken rendered link in {html.relative_to(output)}: {target}")
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rendered", type=Path, help="Also validate a rendered Quarto output directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
    site_url = re.search(r'(?m)^\s*site-url:\s*["\']?([^"\'\s]+)', quarto)
    if not site_url or site_url.group(1) != PRODUCTION_URL:
        errors.append(f"Quarto site-url must be exactly {PRODUCTION_URL}")
    if not re.search(r"(?m)^\s*draft-mode:\s*gone\s*$", quarto):
        errors.append("Quarto must use draft-mode: gone to exclude review content")
    if "source-materials" in re.findall(r"(?m)^\s*-\s+(.+)$", quarto):
        errors.append("Source materials must not be configured as site resources")
    for href in re.findall(r"(?m)^\s*href:\s*([^#\n]+)", quarto):
        target = href.strip().strip('"\'')
        if "://" not in target and not (ROOT / target).exists():
            errors.append(f"Broken Quarto navigation link: {target}")

    for document in [*checked, *ROOT.rglob("*.yml"), *ROOT.rglob("*.html"), *ROOT.rglob("*.json"), *ROOT.rglob("*.scss")]:
        if any(part in {".git", "_site", ".ingest"} for part in document.parts):
            continue
        text = document.read_text(encoding="utf-8")
        for legacy in LEGACY_SITE_REFERENCES:
            if legacy in text:
                errors.append(f"Legacy project-site path in {document.relative_to(ROOT)}: {legacy}")

    if args.rendered:
        errors.extend(validate_rendered_site(args.rendered.resolve()))

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Validated {len(checked)} content files and {len(sources)} manifested PDFs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
