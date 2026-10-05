# Tianxin Research Page

A publication-focused research collection for **https://tianxinzh.github.io/tianxin-research-page/**. Each paper has a stable landing page with its question, methods, reported findings, limitations, primary sources, code-availability statement, machine-readable citation metadata, and BibTeX downloads.

Repository: https://github.com/tianxinzh/tianxin-research-page

## Build and verify

Requires Python 3.10 or later. Build and tests use only the standard library.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
```

Commit source and generated `docs/` output together. GitHub Pages publishes `main`, `/docs`, using **Settings → Pages → Deploy from a branch**. No Actions credentials, third-party scripts, external fonts, or analytics are required.

The default build uses the GitHub project URL as the primary, indexable canonical. HTML, navigation, assets, citation downloads, social metadata, JSON-LD, and sitemap URLs all include `/tianxin-research-page`. Normal pages request `index,follow`; the 404 page requests `noindex,follow`. Search indexing and inclusion in AI answers are not guaranteed.

For an isolated build:

```sh
python scripts/build.py --output-dir /tmp/tianxin-research-check
```

To preview with the real project path, build into a directory of that name and serve its parent:

```sh
python scripts/build.py --output-dir /tmp/research-preview/tianxin-research-page
python -m http.server 8765 --directory /tmp/research-preview
# Open http://localhost:8765/tianxin-research-page/
```

## Stable paper pages

- `/tianxin-research-page/papers/juryprobe/`
- `/tianxin-research-page/papers/modularsql/`
- `/tianxin-research-page/papers/openregshift/`

The repository was renamed from `tianxinzh.github.io`, preserving its history. GitHub redirects repository links, but [Pages URLs are an exception to repository rename redirects](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository). Use the project URL above; do not assume the former root site or its paper paths redirect. Avoid recreating the old repository name, which would remove GitHub's repository redirect.

## Custom domains

This site does not depend on a separately registered domain. No custom domain is configured, and builds remove a stale `docs/CNAME`. DNS is not modified by the builder.

A future custom-domain change requires a separate, approved migration, ownership/DNS verification, changes to the URL configuration, and live HTTPS checks. Binding a custom domain to GitHub Pages normally redirects the GitHub Pages address to that domain, so it is not an independent fallback for an expired domain. Keep the current configuration for a domain-renewal-independent address.

The included `robots.txt` records the project sitemap, but crawlers request robots.txt at the host root; a project-directory copy cannot set host-wide rules. The indexability controls on each HTML page and the canonical sitemap are the operative site-level metadata. Submit the project sitemap to a verified search-console property if one is configured separately.

## Editing papers

Edit `content/papers.json`, rebuild, and run all tests. Templates are in `scripts/build.py`; styling and progressive enhancement are in `assets/`. The JSON is the source of truth for generated citations. Do not copy extra research notes or deployment reports into `docs/`.

Verify original source records before changing titles, author order, status, dates, quantitative findings, or public-code links. `arxiv_submission_date` describes the first arXiv posting, when verified. `publication_date` is used for citation/datePublished metadata only when appropriate to the cited work; the JuryProbe journal record uses year-only metadata because its exact journal publication date was not independently verified. ModularSQL also uses year-only metadata because its source submission date and identifier month were inconsistent when checked.

The home page is a `CollectionPage`, not a personal profile. Paper pages use `ScholarlyArticle` JSON-LD, ordered author metadata, source links, and downloadable citations. All substantive content is available without JavaScript. JavaScript only enhances citation copying, with a selectable-text/download fallback.

## Research rights and availability

Paper PDFs remain on arXiv and the venue. The site does not redistribute PDFs, private research code, data, or private repository content. OpenRegShift code remains private. JuryProbe public code availability is unverified. ModularSQL links to its verified public repository; this does not claim that reproduction was executed.

No license is assigned here to coauthored research implementations. Public visibility alone does not grant a software reuse license.
