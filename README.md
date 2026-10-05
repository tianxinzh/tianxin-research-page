# Tianxin Zhou · Research

Static academic website for **https://searcher.cloud**. Includes public-paper summaries, original source links, explicit limitations, and BibTeX downloads for JuryProbe, ModularSQL, and the OpenRegShift paper.

## Build and check

Requires Python 3.10 or later. The site build has no third-party dependencies.

```sh
python scripts/build.py
python -m unittest discover -s tests -v
python -m http.server 8765 --directory docs
```

The generated `docs/` directory is the complete website. Content remains readable without JavaScript; JavaScript only enhances citation copying. Fonts and assets are served locally, with no analytics or third-party tracking scripts.

## GitHub Pages

Publish the `main` branch, `/docs` folder in **Settings → Pages → Deploy from a branch**. The custom domain is `searcher.cloud`; `docs/CNAME` records that domain. Configure the custom domain in GitHub before directing DNS to Pages. Verify the domain with the GitHub-provided TXT record when available, and enable HTTPS after its certificate is issued.

Canonical URLs always use `https://searcher.cloud`. Keep paper paths stable:

- `/papers/juryprobe/`
- `/papers/modularsql/`
- `/papers/openregshift/`

## Editing content

Edit `content/papers.json`, rebuild, run tests, and commit both the source and generated `docs/` output. HTML templates are in `scripts/build.py`; styling and optional progressive enhancement are in `assets/`.

Before changing paper metadata, check the original source record. Use ordered authors, distinguish accepted papers from preprints, and avoid unsupported DOI, affiliation, quantitative, or generalization claims. Keep source-check dates current when the content is actually rechecked.

## Publication and rights

Paper PDFs remain on arXiv and the publication venue. This site does not redistribute PDFs, private research code, private data, or private repository content. OpenRegShift code remains private. The site assigns no software license to coauthored research implementations. Public visibility is not itself a reuse license.

The site improves human readability and machine-readable metadata. Search indexing, generative-search visibility, and citation impact are not guaranteed.
