# Tianxin Research Page

A publication-focused research collection for **https://research.searcher.cloud/**. Each paper has a stable landing page with its question, methods, reported findings, limitations, primary sources, code-availability statement, machine-readable citation metadata, and BibTeX downloads.

Repository: https://github.com/tianxinzh/tianxin-research-page

## Build and verify

Requires Python 3.10 or later. Build and tests use only the standard library.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
```

Commit source and generated `docs/` output together. GitHub Pages publishes `main`, `/docs`, using **Settings → Pages → Deploy from a branch**. No Actions credentials, third-party scripts, external fonts, or analytics are required.

The default build reads the custom domain from the tracked `docs/CNAME` file. With `research.searcher.cloud` configured, assets, navigation, and citation downloads are page-relative. The same generated pages work at the domain root or under a project path without rebuilding. Canonical/social metadata, JSON-LD, and sitemap URLs remain absolute and use the configured domain. Builds preserve the domain binding. If `docs/CNAME` is intentionally removed for a separate migration, canonical metadata falls back to the GitHub project URL and `/tianxin-research-page` prefix.

The custom 404 page is the intentional exception: GitHub can serve it at any missing URL depth, so its assets and recovery links use the configured absolute canonical origin. Directory URLs should retain their trailing slash (GitHub Pages redirects directory requests accordingly). No `<base>` element is used.

Normal pages request `index,follow`; the 404 page requests `noindex,follow`. Search indexing and inclusion in AI answers are not guaranteed.

For an isolated build:

```sh
python scripts/build.py --output-dir /tmp/tianxin-research-check
```

To preview the configured custom-domain layout:

```sh
python scripts/build.py --output-dir /tmp/research-preview
python -m http.server 8765 --directory /tmp/research-preview
# Open http://localhost:8765/
```

## Stable paper pages

- `/papers/juryprobe/`
- `/papers/modularsql/`
- `/papers/openregshift/`

The repository was renamed from `tianxinzh.github.io`, preserving its history. GitHub redirects repository links, but [Pages URLs are an exception to repository rename redirects](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository). Avoid recreating the old repository name, which would remove GitHub's repository redirect.

## Custom domain

GitHub Pages is configured for `research.searcher.cloud`, recorded in `docs/CNAME`. The builder reads and preserves that file; do not remove it during routine builds. DNS and GitHub security settings are not modified by the builder. `robots.txt` and `sitemap.xml` are served at the custom-domain root.

Binding a custom domain normally redirects the GitHub Pages address to that domain, so it is not an independent fallback for an expired domain. A future migration requires checking the domain binding, DNS, generated URLs, and live HTTPS together.

## Editing papers

Edit `content/papers.json`, rebuild, and run all tests. Templates are in `scripts/build.py`; styling and progressive enhancement are in `assets/`. The JSON is the source of truth for generated citations. Do not copy extra research notes or deployment reports into `docs/`.

Verify original source records before changing titles, author order, status, dates, quantitative findings, or public-code links. `arxiv_submission_date` describes the first arXiv posting, when verified. `publication_date` is used for citation/datePublished metadata only when appropriate to the cited work; the JuryProbe journal record uses year-only metadata because its exact journal publication date was not independently verified. ModularSQL also uses year-only metadata because its source submission date and identifier month were inconsistent when checked.

The home page is a `CollectionPage`, not a personal profile. Paper pages use `ScholarlyArticle` JSON-LD, ordered author metadata, source links, and downloadable citations. All substantive content is available without JavaScript. JavaScript only enhances citation copying, with a selectable-text/download fallback.

## Research rights and availability

Paper PDFs remain on arXiv and the venue. The site does not redistribute PDFs, private research code, data, or private repository content. OpenRegShift code remains private. JuryProbe public code availability is unverified. ModularSQL links to its verified public repository; this does not claim that reproduction was executed.

No license is assigned here to coauthored research implementations. Public visibility alone does not grant a software reuse license.
