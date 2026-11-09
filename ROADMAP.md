# ROADMAP — qtan-tran.github.io

## Done

- v2 design ("modern academic", owner feedback: v1 was too minimal/boring):
  stronger typographic hierarchy (kicker, gradient hairlines on h1/h2),
  sticky translucent header with backdrop blur, hero with profile chips
  (Email, ORCID, Google Scholar), project and repository cards with hover
  lift + gradient top bar, pills/tags, teaching list as cards,
  prefers-reduced-motion support. Still no JS, no external dependencies.
- Course description for "Introduction to Open Science" (Winter 2026–27,
  block seminar, 16–17 & 23–24 October) fed into the course page,
  including the three literature items (2 DOIs verified HTTP 200).
- Structure agreed: static self-contained HTML/CSS, no build step, no JS,
  no external dependencies; shared `style.css`; system fonts; dark mode via
  `prefers-color-scheme`; print styles; semantic HTML.
- Homepage (`index.html`) with sections: About me (bio, education,
  fellowships and awards, fieldwork), Research projects (ROARA, POEM),
  Publications (19 items in 7 groups, rendered from `publications.bib`
  data), Repositories (oa-explorer, graecum-vn), Teaching teaser.
- `publications.bib` as canonical machine-readable publication source
  (BibTeX; keys referenced from the HTML via `data-key`).
- Teaching overview (`teaching/index.html`, newest to oldest) plus one
  placeholder page per course (10 courses, standard template, description
  sections ready to be filled).
- QA script `qa/check_site.py` (tag balance, internal links and anchors,
  bib ↔ HTML cross-check, mojibake scan, optional online link check).
- `.nojekyll` so GitHub Pages serves the files as-is.

## Next

- Fill in course descriptions for the remaining nine courses
  (owner will feed the descriptions; template = the Open Science page).
- Owner decision (2026-11-09): drop "Invited talks" section; keep
  "Conference presentations" on the site.
- Syllabus link for Summer 2020 ("Platform society and infrastructures of
  everyday life") replaced with the Notion page
  `https://tantran.notion.site/56-104-Platform-society-Syllabus-f842451ef0bb4a59a549b35006d5a433`
  (dead tiny.cc link removed).
- Profiles added (verified against Bielefeld PUB): ORCID
  `0000-0003-3533-5858`, Google Scholar `Lev6PMwAAAAJ`.
- Author correction in STI 2025 proceedings entry (owner-confirmed):
  "Leigh-Ann, B." → "Butler, L.-A.".
- Add new repository/dataset entries to the Repositories section as they
  go public (structure ready; e.g. the ROARA corpus repository
  `oa-os-policy-collections` when published).
- Update "Last updated" lines whenever content changes.

## Maintenance notes

- After every content change: run `python3 qa/check_site.py . --online`,
  then push to `main` (deploys automatically, CDN cache ~5 min).
- Entry keys in `publications.bib` are stable identifiers; never rename an
  existing key, only add new ones.
- Course page URLs are permanent; never rename or move a published course
  page.
