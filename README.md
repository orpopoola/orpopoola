# Your Website

This repository contains the research website for **Ola Popoola**. When the repository is connected to GitHub Pages, the public address is <https://orpopoola.github.io>.

You do not need to write HTML to keep the site current. Projects and short Research Updates are ordinary QMD (Markdown) files. Publications are BibTeX records. Original research PDFs stay in `source-materials/` and are used to prepare reviewable drafts; they are **not** copied to the public website.

The publication safeguard is simple:

1. material extracted from a PDF starts as `status: draft` or `status: review`;
2. draft records include `draft: true` and are omitted by Quarto;
3. a person checks facts, dates, relationships, images, rights, and confidentiality;
4. only an approved record is changed to `status: published` and `draft: false`;
5. merging to `main` triggers the GitHub Pages deployment.

Open [`CONTENT_TODO.md`](CONTENT_TODO.md) first. It records information that is missing, ambiguous, personal, unpublished, or potentially sensitive.

## Add Research from a PDF

1. Put the unmodified PDF in `source-materials/presentations/` or an appropriate subfolder of `source-materials/`.
2. Run:

   ```bash
   python scripts/ingest_pdfs.py --source source-materials
   ```

3. Inspect `.ingest/pdf-report.json`. The `.ingest/` directory is temporary and is not committed.
4. Review the extracted text and any safety flags. If normal extraction fails, use OCR only for that document.
5. Decide whether the source describes a stable Project, a specific Research Update, a publication, or nothing suitable for the public site.
6. Copy the appropriate template and retain `source`/`sources` provenance.
7. Review title, summary, date, themes, project relationships, and images against the PDF.
8. Record uncertainty or missing information in `CONTENT_TODO.md`.
9. Keep the item as a draft until the owner approves it.
10. Preview, validate, commit, and merge. Deployment then runs automatically.

The ingestion utility does not call an AI service and never publishes. It uses `pdfinfo` and `pdftotext` from Poppler when installed, calculates a SHA-256 hash, looks for explicit safety terms, and writes a local review report. This deliberately keeps a human between extraction and publication.

## Add a Project

1. Copy `projects/_template.qmd` to `projects/short-project-name.qmd`.
2. Complete only fields supported by reviewed evidence.
3. Use one or more of the four exact theme names in `categories`.
4. Add internal PDF provenance under `source` or `sources`.
5. Omit unsupported optional sections instead of leaving empty headings.
6. Set `featured: true` only after approval.
7. Keep `draft: true` until publication is approved.

Project pages follow **Challenge → Approach → System and experiments → Outcomes** where evidence supports those sections.

## Add a Research Update

1. Copy `updates/_template.qmd` to `updates/short-update-name.qmd`.
2. Write a concise evidence-led description—approximately 100 words is usually enough.
3. Use the activity date stated in the source. Never substitute the filename, PDF metadata, upload date, or Git date.
4. Set `project` only when the relationship is explicit.
5. Add an approved research image and accurate alt text where available.
6. Keep `draft: true` until publication is approved.

Published updates appear automatically in the Research Activity listing and can be associated with themes through categories. Project/theme automation is metadata-driven; do not copy the same update into multiple pages.

## Add a Publication

Add a complete, verified record to `data/publications.bib`. Use an authoritative CV, publisher record, DOI record, or confirmed author bibliography. Do not turn a partial slide reference into a complete citation. Add paper, DOI, code, or dataset links only when verified.

## Update Biography

Edit `about.qmd` after checking the wording against an owner-approved biography or CV. Do not infer job title, institution, education, memberships, awards, or contact details.

## Add a Person

Add verified structured information to `data/people.yml`, then add approved public copy to `people.qmd`. A name appearing in a PDF does not by itself establish team membership or collaboration.

## Fix Incorrect Content

1. Find the QMD, YAML, or BibTeX source—not `_site/`.
2. Correct the claim against the authoritative source.
3. Update provenance and `CONTENT_TODO.md` if the change exposes an unresolved conflict.
4. Run validation and preview before committing.

## Deployment

`.github/workflows/publish.yml` validates, renders, checks that PDFs were not copied to `_site`, and deploys the result through GitHub Pages whenever `main` changes.

One GitHub setting remains manual: in **Repository settings → Pages → Build and deployment → Source**, select **GitHub Actions**. Confirm the production repository is named `orpopoola.github.io`; the repository originally inspected by Codex identified itself as `orpopoola/orpopoola`.

No analytics or custom domain is configured. A future custom domain can be added through GitHub Pages without changing internal site links.

## Troubleshooting

- **Quarto is missing:** install it from <https://quarto.org/docs/get-started/> and rerun `quarto check`.
- **PDF text is empty:** confirm Poppler is installed; if the PDF is image-only, OCR that file and review the result manually.
- **A draft appears publicly:** set both `status: draft` (or `review`) and `draft: true`, then run `python scripts/validate_site.py`.
- **An image is unclear:** remove it from public content, add `[IMAGE DESCRIPTION REQUIRED]`, and request the original in `CONTENT_TODO.md`.
- **Deployment fails:** open the failed GitHub Actions run, fix the first validation/render error, and rerun it.

For a short checklist, use [`HOW_TO_UPDATE.md`](HOW_TO_UPDATE.md).

# Developer Documentation

## Local setup

Requirements:

- Quarto;
- Python 3.10 or later;
- Poppler (`pdfinfo` and `pdftotext`) for PDF ingestion.

```bash
quarto check
python scripts/validate_site.py
python scripts/build_content_index.py
quarto preview
```

The site uses only Quarto, Bootstrap, QMD/YAML/BibTeX, restrained SCSS, and a negligible progressive-enhancement script. There is no Node build or database.

## Rendering

```bash
quarto render
python scripts/validate_site.py
```

Generated output is written to `_site/` and ignored by Git. Source PDFs are not listed as Quarto resources and the deployment workflow rejects any rendered PDF.

## Architecture

- `_quarto.yml` — navigation, search, SEO, theme, output, and global settings.
- `index.qmd` and top-level QMD files — primary information architecture.
- `research/` — the four theme pages.
- `projects/` and `updates/` — metadata-driven public records plus reusable templates.
- `data/` — themes, people, publications, and PDF provenance manifest.
- `source-materials/` — preserved internal source documents; never a public resource by default.
- `styles/custom.scss` — responsive visual system and accessibility states.
- `scripts/ingest_pdfs.py` — cautious local PDF inspection.
- `scripts/validate_site.py` — links, manifest coverage, draft safety, and source-isolation checks.
- `scripts/build_content_index.py` — published project/update relationships used by homepage, theme, and project cards.
- `.github/workflows/publish.yml` — GitHub Pages build and deployment.

## Content states

`draft` and `review` records must have `draft: true`. `published` records use `draft: false`. Human review—not ingestion—is the publication gate.

## Administration

There is no `/admin/` CMS in this version. Adding one safely requires an owner-selected GitHub OAuth provider and operational credentials; committing an interface before authentication exists would be misleading. GitHub's editor and ordinary local editing remain fully supported.

## Licence

Repository code is covered by [`LICENSE`](LICENSE). Source PDFs and extracted media may carry separate rights and must not be assumed to inherit the software licence.
