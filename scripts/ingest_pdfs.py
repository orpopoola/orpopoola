#!/usr/bin/env python3
"""Create a review report for source PDFs without publishing their content.

The script uses Poppler tools when available. It writes temporary extraction
artefacts under .ingest/ (ignored by Git), records hashes for traceability, and
flags safety terms. A human must curate any project/update and approve publication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SAFETY_TERMS = (
    "confidential", "private", "internal", "draft", "nda",
    "not for distribution", "proprietary", "commercial in confidence",
    "unpublished", "embargoed",
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def pdf_info(path: Path) -> dict[str, str]:
    if not shutil.which("pdfinfo"):
        return {}
    result = run(["pdfinfo", str(path)])
    if result.returncode:
        return {"error": result.stderr.strip()}
    return {
        key.strip().lower().replace(" ", "_"): value.strip()
        for line in result.stdout.splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }


def extract_text(path: Path, destination: Path) -> tuple[str, str | None]:
    if not shutil.which("pdftotext"):
        return "", "pdftotext is unavailable; install Poppler and run again"
    result = run(["pdftotext", "-layout", str(path), str(destination)])
    if result.returncode:
        return "", result.stderr.strip() or "pdftotext failed"
    return destination.read_text(encoding="utf-8", errors="replace"), None


def safety_flags(text: str) -> list[str]:
    lowered = text.casefold()
    return [term for term in SAFETY_TERMS if re.search(rf"\b{re.escape(term)}\b", lowered)]


def inspect_pdf(path: Path, output: Path) -> dict[str, object]:
    stem = re.sub(r"[^a-z0-9]+", "-", path.stem.casefold()).strip("-")[:80]
    text_path = output / f"{stem}.txt"
    text, error = extract_text(path, text_path)
    record: dict[str, object] = {
        "source": path.as_posix(),
        "sha256": digest(path),
        "metadata": pdf_info(path),
        "text_characters": len(text),
        "safety_flags": safety_flags(text),
        "publication_status": "draft",
        "human_review_required": True,
    }
    if error:
        record["extraction_warning"] = error
    if text and not text.strip():
        record["ocr_required"] = True
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("source-materials"))
    parser.add_argument("--output", type=Path, default=Path(".ingest"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdfs = sorted(args.source.rglob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found under {args.source}")
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "notice": "Review artefact only. Nothing in this report is approved for publication.",
        "documents": [inspect_pdf(pdf, args.output) for pdf in pdfs],
    }
    report_path = args.output / "pdf-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Inspected {len(pdfs)} PDFs; review {report_path}")
    warnings = sum("extraction_warning" in item for item in report["documents"])
    if warnings:
        print(f"Warning: {warnings} documents need Poppler text extraction", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
