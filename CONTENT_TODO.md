# Content review checklist

Nothing in this checklist should be treated as public fact until a named owner has verified it.

## High Priority

- [ ] Complete or verify the repository rename to `orpopoola/orpopoola.github.io` before deployment; the workflow deliberately rejects the former repository name.
- [ ] Supply or confirm Dr Popoola's current professional title and institutional affiliation.
- [ ] Review every manifest entry before changing any generated record from `draft: true` to public.
- [ ] Confirm whether source PDFs may remain in the production repository; Quarto does not copy them to `_site` under the current configuration.

## PDFs Requiring Review

- [ ] Review all nine PDFs listed in `data/pdf-manifest.yml` using the documented ingestion workflow.
- [ ] Confirm the titles, authorship, publication status, and ownership of each technical paper and report.
- [ ] Determine whether the URLLC/mMTC documents describe one project, a student research activity, publications, or several related records.

## Confidentiality Concerns

- [ ] Review `Application overview - UKRI Funding Service.pdf` for grant, financial, personal, partner, and commercially sensitive information.
- [ ] Review student reports and thesis submissions for personal information, unpublished results, and third-party material.
- [ ] Confirm distribution rights before providing any original PDF as a public download.

## Ambiguous Project Relationships

- [ ] Verify the relationship among the two resource-allocation documents, both Zhuofan Cui documents, and `MSc Report.pdf`.
- [ ] Confirm whether the teleoperation review and mission-critical systems survey relate to active projects or are literature reviews only.

## Missing Dates

- [ ] Supply verified project and activity dates from the research record. Do not use PDF metadata, filenames, or Git dates as substitutes.

## Missing Project Information

- [ ] Confirm challenge, approach, objectives, technical system, experimental platform, outcomes, status, team, partners, and funder for each project.

## Missing Image Descriptions

- [ ] Review candidate embedded images and write descriptions only after their context is known.

## Missing Original Images

- [ ] Supply original experiment, robot, vehicle, laboratory, testbed, and field-trial photographs where PDF extraction quality or rights are insufficient.
- [ ] The MSc/student-report PDFs contain a candidate networked robotic-arm diagram; confirm provenance and request the original if it is approved for use.

## Missing Publication Details

- [ ] Supply an authoritative CV or bibliography with full authors, titles, venues, years, and identifiers.
- [ ] Confirm DOI, paper, code, and dataset URLs before adding them to `data/publications.bib`.

## Missing People Information

- [ ] Verify biography, role, institutional affiliation, education, memberships, leadership, teaching, and service information for Dr Popoola.
- [ ] Add other people only after confirming their relationship to the research programme and obtaining appropriate profile information.

## Missing External Profiles

- [ ] Confirm university profile, Google Scholar, ORCID, LinkedIn, CV, and preferred contact route. GitHub is the only currently verified profile.

## Other Content Decisions

- [ ] Decide whether to activate the optional `/admin/` editor after configuring a secure GitHub OAuth provider.
- [ ] Provide an approved portrait, social preview image, and image descriptions.
- [ ] Confirm whether privacy-conscious analytics are wanted; none are configured.
