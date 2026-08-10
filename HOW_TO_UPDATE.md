# Add research from a PDF

1. Add the original PDF to `source-materials/presentations/` (or create a clearly named source subfolder).
2. Run `python scripts/ingest_pdfs.py --source source-materials/presentations`.
3. Review the report in `.ingest/` and the manifest changes; extraction never publishes content.
4. Create or review the generated draft under `projects/` or `updates/`.
5. Check the title and description against the source.
6. Review candidate images, their rights, quality, relevance, and context.
7. Confirm the research themes and any project association.
8. Write accurate alt text. If context is insufficient, use `[IMAGE DESCRIPTION REQUIRED]` and update `CONTENT_TODO.md`.
9. Confirm dates from the document content—not PDF metadata, filenames, or Git history.
10. After human approval, change `status: review` to `status: published` and `draft: true` to `draft: false`.
11. Commit or merge the reviewed change. GitHub Actions renders and deploys the website.

## Manual fallback

- Copy `projects/_template.qmd` or `updates/_template.qmd`.
- Rename it with a short lowercase slug such as `multi-robot-field-trial.qmd`.
- Complete only fields supported by evidence and retain the internal `source` metadata.
- Leave missing optional sections out rather than publishing empty headings.
- Preview with `quarto preview`; validate with `python scripts/validate_site.py`.

## Publications, people, and biography

- Add verified BibTeX to `data/publications.bib`.
- Add verified people records to `data/people.yml` and write approved profile copy in `people.qmd`.
- Update `about.qmd` only from a verified CV or owner-approved biography.

## If something is wrong

Correct the source QMD/YAML/BibTeX file, add the reason or unresolved question to `CONTENT_TODO.md`, preview, then commit. Never edit generated `_site/` files.
