# qtan-tran.github.io — personal academic website

Source for the personal website of Quoc-Tan Tran:
<https://qtan-tran.github.io/>

This is a GitHub Pages **user page**: the site is served from the `main`
branch of this repository at the domain root. Project pages such as
<https://qtan-tran.github.io/graecum-vn/> live in their own repositories and
are untouched by changes here.

## Design principles

- **Static, self-contained HTML + CSS.** No build step, no JavaScript, no
  external dependencies (no CDN, no web fonts, no analytics). The page should
  still render correctly in ten years.
- One shared stylesheet (`style.css`), system font stack, semantic HTML
  (`header/nav/main/section/article`), responsive, print-friendly, dark mode
  via `prefers-color-scheme`.
- `.nojekyll` keeps GitHub Pages from running Jekyll: everything is served as
  plain files.

## Repository structure

    index.html                  Homepage: About, Research, Publications,
                                Repositories, Teaching teaser
    style.css                   Shared stylesheet (light + dark + print)
    publications.bib            Canonical machine-readable publication data
    teaching/index.html         Teaching overview (newest to oldest)
    teaching/<slug>/index.html  One page per course (description goes here)
    qa/check_site.py            QA checks (tags, links, bib consistency)
    README.md                   This file
    ROADMAP.md                  What is done / what comes next

## How to update

### Publications (source of truth: `publications.bib`)

1. Add or correct the entry in `publications.bib` (BibTeX; exchangeable with
   Zotero and journals). Keep the entry key stable once published.
2. Update the rendered list in `index.html`: add or edit the `<li>` inside the
   matching group (`Books`, `Edited volumes`, `Journal articles`, `Book
   chapters`, `Proceedings`, `Posters`, `Professional and community writing`),
   always setting `data-key` to the exact BibTeX key.
3. Run the QA script (below). It fails if a bib entry is missing from the
   rendered list or an unknown `data-key` appears.

### Teaching

1. Create `teaching/<slug>/index.html` by copying an existing course page
   (keep the same template).
2. Add the course to the list in `teaching/index.html` at the top (newest
   first).
3. Course descriptions are added directly on the course page in the
   `Course description` section (replace the `placeholder-note` paragraph).

### Repositories (tools and datasets)

Add a new `<li>` block to the `Repositories` list in `index.html`, following
the existing two entries (`oa-explorer`, `graecum-vn`). Keep descriptions short
and verify every link with the QA script before pushing.

## QA before every push

    python3 qa/check_site.py .          # offline checks
    python3 qa/check_site.py . --online # + external link / DOI verification

The script checks:

1. HTML tag balance (every opened tag closed, void elements respected),
2. internal links and `#anchors` resolve to existing files and ids,
3. `publications.bib` and the rendered list agree (both directions),
4. suspicious characters (mojibake, replacement chars, stray control chars,
   markdown leakage),
5. with `--online`: HTTP status of every external link.

Some publishers (Taylor & Francis, Medium) block automated requests with
403; the script lists those hosts explicitly so they are reported as
"bot-blocked, check manually" instead of failures.

## Deployment

Push to `main`; GitHub Pages deploys automatically. The CDN cache for
`main` is about 5 minutes. Verify with:

    curl -s -o /dev/null -w "%{http_code}" https://qtan-tran.github.io/

## Conventions

- UTF-8 everywhere; en dashes (–) in page ranges and terms, no smart-quote
  tricks in source beyond real Unicode characters.
- Relative links only (`index.html`, `teaching/index.html`), so the site also
  works when opened from a local checkout.
- Contact: quoc-tan.tran@uni-bielefeld.de
