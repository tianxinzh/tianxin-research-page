# Tianxin Zhou · Research

Static academic website with public-paper summaries, original source links, explicit limitations, and BibTeX downloads for JuryProbe, ModularSQL, and the OpenRegShift paper.

**Current deployment:** https://tianxinzh.github.io/ is the working public preview. The intended custom domain, `searcher.cloud`, is not bound by the default build. Domain ownership verification and the website DNS cutover must be completed separately.

## Default preview build

Requires Python 3.10 or later. The build and tests use only Python's standard library.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python -m http.server 8765 --directory docs
```

The default build:

- Uses `https://tianxinzh.github.io` for canonical, social, citation-page, JSON-LD, and sitemap URLs.
- Sets HTML pages to `noindex,follow` while the site is a temporary preview. The pages remain publicly readable. This is an indexing request, not an access control.
- Does **not** create `docs/CNAME`. If a previous custom-domain build left that generated file in the output directory, the default build removes it.

The generated `docs/` directory is the complete website. Content remains readable without JavaScript; JavaScript only enhances citation copying. Fonts and assets are served locally, with no analytics or third-party tracking scripts.

## GitHub Pages and custom-domain cutover

The current publishing source is the `main` branch, `/docs` folder, using **Settings → Pages → Deploy from a branch**. Keep that source unchanged.

Only as an explicit, approved custom-domain cutover step, build with:

```sh
python scripts/build.py --custom-domain
python -m unittest discover -s tests -v
```

This flag writes `docs/CNAME` containing `searcher.cloud`, changes every site-owned absolute URL to `https://searcher.cloud`, and enables indexing for the normal HTML pages. The 404 page stays `noindex,follow`. Continue using this flag for subsequent production builds once the custom domain is active; a default preview build would remove the generated binding file.

The flag only creates files. It does not prove DNS ownership, edit DNS, configure GitHub's Pages settings, issue a certificate, or establish that the custom domain is live. Complete the GitHub TXT ownership check, configure the repository's custom domain before pointing DNS at Pages, preserve unrelated DNS records, and verify the live domain and certificate before announcing the custom-domain launch. Commit the generated output only in coordination with that cutover. Do not use the production build merely to refresh the preview.

An isolated output directory is available for checks:

```sh
python scripts/build.py --custom-domain --output-dir /tmp/research-site-production-check
```

The tests exercise preview → custom-domain → preview in a temporary directory, including removal of a stale CNAME and consistency of the URL/indexing metadata. They do not contact or modify GitHub or DNS.

Keep paper paths stable across the hostname change:

- `/papers/juryprobe/`
- `/papers/modularsql/`
- `/papers/openregshift/`

## Editing content

Edit `content/papers.json`, rebuild in the intended mode, run tests, and commit both the source and generated `docs/` output. `content/papers.json` is the citation source of truth; the builder creates the downloadable `.bib` files from it. HTML templates are in `scripts/build.py`; styling and optional progressive enhancement are in `assets/`.

Before changing paper metadata, check the original source record. Use ordered authors, distinguish accepted papers from preprints, and avoid unsupported DOI, affiliation, quantitative, or generalization claims. Keep source-check dates current when the content is actually rechecked.

## Publication and rights

Paper PDFs remain on arXiv and the publication venue. This site does not redistribute PDFs, private research code, private data, or private repository content. OpenRegShift code remains private. The site assigns no software license to coauthored research implementations. Public visibility is not itself a reuse license.

The site improves human readability and machine-readable metadata. Search indexing, generative-search visibility, and citation impact are not guaranteed.
