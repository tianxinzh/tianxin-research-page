"""Offline regression checks for the generated GitHub Pages publication.

Run: python scripts/build.py && python -m unittest discover -s tests -v
Uses only Python's standard library. These tests do not replace visual browser QA
or live verification of external research sources and deployment configuration.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
BASE = 'https://searcher.cloud'
PAPERS = json.loads((ROOT / 'content/papers.json').read_text())


class HTML(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.source = path.read_text(encoding='utf-8')
        self.tags = []
        self.ids = []
        self.meta = {}
        self.links = []
        self.jsonld = []
        self.script_type = None
        self.script_data = ''
        self.feed(self.source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'meta':
            key = attrs.get('name', attrs.get('property'))
            self.meta.setdefault(key, []).append(attrs.get('content'))
        if tag in ('a', 'link') and attrs.get('href'):
            self.links.append(attrs['href'])
        if attrs.get('src'):
            self.links.append(attrs['src'])
        if tag == 'script':
            self.script_type = attrs.get('type')
            self.script_data = ''

    def handle_data(self, data):
        if self.script_type:
            self.script_data += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.script_type:
            if self.script_type == 'application/ld+json':
                self.jsonld.append(json.loads(self.script_data))
            self.script_type = None

    def attrs(self, tag):
        return [attrs for name, attrs in self.tags if name == tag]

    @property
    def public_path(self):
        path = '/' + self.path.relative_to(DOCS).as_posix()
        return path[:-10] if path.endswith('index.html') else path


def bib_fields(text):
    """Parse this project's deliberately small, brace-delimited BibTeX subset."""
    match = re.match(r'@(article|misc)\{([A-Za-z0-9_-]+),\s*', text)
    if not match:
        raise ValueError('Unsupported or malformed BibTeX entry')
    fields = {}
    pos = match.end()
    while pos < len(text):
        tail = text[pos:].strip()
        if tail == '}':
            return match.group(1), match.group(2), fields
        field = re.match(r'\s*(\w+)\s*=\s*\{', text[pos:])
        if not field:
            raise ValueError('Malformed BibTeX field')
        key = field.group(1).lower()
        if key in fields:
            raise ValueError('Duplicate BibTeX field')
        pos += field.end()
        start = pos
        depth = 1
        while pos < len(text) and depth:
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
            pos += 1
        if depth:
            raise ValueError('Unbalanced BibTeX braces')
        fields[key] = text[start:pos-1]
        while pos < len(text) and text[pos].isspace():
            pos += 1
        if pos < len(text) and text[pos] == ',':
            pos += 1
    raise ValueError('Missing entry closing brace')


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p: HTML(p) for p in DOCS.rglob('*.html')}

    def test_expected_publication_files(self):
        expected = {
            '.nojekyll', 'CNAME', 'index.html', '404.html', 'robots.txt',
            'sitemap.xml', 'assets/favicon.svg', 'assets/site.js',
            'assets/style.css', 'citations/index.html',
            'citations/publications.bib', 'sources/index.html',
        }
        for paper in PAPERS:
            expected.update({f"papers/{paper['slug']}/index.html",
                             f"citations/{paper['slug']}.bib"})
        actual = {p.relative_to(DOCS).as_posix() for p in DOCS.rglob('*') if p.is_file()}
        self.assertEqual(actual, expected, 'Unexpected/missing public files; review for leaks or stale output')
        self.assertEqual((DOCS / 'CNAME').read_text().strip(), 'searcher.cloud')

    def test_internal_links_and_fragments(self):
        for page in self.pages.values():
            for link in page.links:
                with self.subTest(page=page.public_path, link=link):
                    url = urlsplit(urljoin(BASE + page.public_path, link))
                    if url.scheme not in ('http', 'https') or url.netloc != 'searcher.cloud':
                        continue
                    dest = DOCS / unquote(url.path).lstrip('/')
                    if dest.is_dir():
                        dest = dest / 'index.html'
                    self.assertTrue(dest.is_file(), f'Missing internal link target: {dest}')
                    if url.fragment and dest.suffix == '.html':
                        self.assertIn(unquote(url.fragment), self.pages[dest].ids)

    def test_documents_have_semantic_basics(self):
        for page in self.pages.values():
            with self.subTest(page=page.public_path):
                self.assertTrue(page.source.lower().startswith('<!doctype html>'))
                self.assertEqual(page.attrs('html')[0].get('lang'), 'en')
                self.assertEqual(len(page.attrs('h1')), 1)
                self.assertEqual(len(page.attrs('main')), 1)
                self.assertIn('main', page.ids)
                self.assertIn('width=device-width', page.meta['viewport'][0])
                self.assertEqual(len(page.ids), len(set(page.ids)), 'Duplicate element IDs')
                self.assertTrue(any(a.get('href') == '#main' for a in page.attrs('a')))
                self.assertTrue(all(a.get('aria-label') for a in page.attrs('nav')))
                for img in page.attrs('img'):
                    self.assertIn('alt', img)
                for button in page.attrs('button'):
                    self.assertEqual(button.get('type'), 'button')

    def test_canonical_social_metadata(self):
        for page in self.pages.values():
            with self.subTest(page=page.public_path):
                canonicals = [a['href'] for a in page.attrs('link') if a.get('rel') == 'canonical']
                self.assertEqual(canonicals, [BASE + page.public_path])
                self.assertEqual(page.meta['og:url'], canonicals)
                self.assertTrue(page.meta['description'][0])
                self.assertTrue(page.meta['og:title'][0])
                self.assertTrue(page.meta['twitter:title'][0])
                expected = 'noindex,follow' if page.public_path == '/404.html' else 'index,follow'
                self.assertEqual(page.meta['robots'], [expected])

    def test_sitemap_and_robots(self):
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        xml = ET.parse(DOCS / 'sitemap.xml')
        locations = [n.text for n in xml.findall('s:url/s:loc', ns)]
        expected = [BASE + p.public_path for p in self.pages.values() if p.public_path != '/404.html']
        self.assertCountEqual(locations, expected)
        self.assertEqual(len(locations), len(set(locations)))
        self.assertIn('Sitemap: ' + BASE + '/sitemap.xml', (DOCS / 'robots.txt').read_text())

    def test_paper_citation_metadata(self):
        for paper in PAPERS:
            page = self.pages[DOCS / 'papers' / paper['slug'] / 'index.html']
            with self.subTest(paper=paper['slug']):
                self.assertEqual(page.meta['citation_title'], [paper['title']])
                self.assertEqual(page.meta['citation_author'], paper['authors'])
                self.assertEqual(page.meta['citation_arxiv_id'], [paper['arxiv_id']])
                self.assertEqual(page.meta['citation_pdf_url'], [paper['pdf_url']])
                self.assertEqual(page.meta['citation_publication_date'],
                                 [paper['publication_date'] or str(paper['year'])])
                self.assertNotIn('citation_doi', page.meta)
                self.assertNotIn('citation_author_institution', page.meta)
                if paper['review_url']:
                    self.assertEqual(page.meta['citation_journal_title'], [paper['venue']])
                else:
                    self.assertNotIn('citation_journal_title', page.meta)

    def test_article_jsonld_matches_visible_content(self):
        for paper in PAPERS:
            page = self.pages[DOCS / 'papers' / paper['slug'] / 'index.html']
            with self.subTest(paper=paper['slug']):
                self.assertEqual(len(page.jsonld), 1)
                data = page.jsonld[0]
                self.assertEqual(data['@context'], 'https://schema.org')
                self.assertEqual(data['@type'], 'ScholarlyArticle')
                self.assertEqual(data['name'], paper['title'])
                self.assertEqual(data['headline'], paper['title'])
                self.assertEqual(data['description'], paper['summary'])
                self.assertEqual([a['name'] for a in data['author']], paper['authors'])
                self.assertEqual(data['identifier']['value'], paper['arxiv_id'])
                self.assertEqual(data['url'], BASE + page.public_path)
                self.assertEqual(data.get('datePublished'), paper['publication_date'])
                self.assertIn(paper['paper_url'], data['sameAs'])
                if paper['code_url']:
                    self.assertEqual(data['hasPart']['codeRepository'], paper['code_url'])
                else:
                    self.assertNotIn('hasPart', data)
                self.assertNotIn('affiliation', json.dumps(data))
                self.assertNotIn('doi.org', json.dumps(data))

    def test_bibtex_is_consistent_and_case_protected(self):
        keys = []
        for paper in PAPERS:
            with self.subTest(paper=paper['slug']):
                downloaded = (DOCS / 'citations' / (paper['slug'] + '.bib')).read_text()
                source = (ROOT / 'content' / (paper['slug'] + '.bib')).read_text()
                self.assertEqual(downloaded, paper['bibtex'] + '\n')
                self.assertEqual(source, downloaded)
                kind, key, fields = bib_fields(downloaded)
                keys.append(key)
                self.assertEqual(fields['title'], '{' + paper['title'] + '}')
                self.assertEqual(fields['author'], 'Zhou, Tianxin and Lin, Ruixi')
                self.assertEqual(fields['year'], str(paper['year']))
                self.assertEqual(fields['url'], paper['review_url'] or paper['paper_url'])
                for unsupported in ('doi', 'volume', 'number', 'pages', 'month'):
                    self.assertNotIn(unsupported, fields)
                if paper['review_url']:
                    self.assertEqual(kind, 'article')
                    self.assertEqual(fields['journal'], paper['venue'])
                else:
                    self.assertEqual(kind, 'misc')
                    self.assertEqual(fields['eprint'], paper['arxiv_id'])
        self.assertEqual(len(keys), len(set(keys)))
        expected = '\n\n'.join(p['bibtex'] for p in PAPERS) + '\n'
        self.assertEqual((DOCS / 'citations/publications.bib').read_text(), expected)
        self.assertEqual((ROOT / 'content/publications.bib').read_text(), expected)

    def test_paper_only_citations_are_not_mislabeled_as_software_cff(self):
        # CFF 1.2.0 root type accepts software/dataset, not article.
        self.assertEqual(list(DOCS.rglob('*.cff')), [])
        for page in self.pages.values():
            self.assertNotIn('.cff', page.source)
            self.assertNotIn('Citation File Format', page.source)

    def test_no_private_code_or_unverified_release_links(self):
        for paper in PAPERS:
            page = self.pages[DOCS / 'papers' / paper['slug'] / 'index.html']
            if paper['slug'] in ('juryprobe', 'openregshift'):
                self.assertIsNone(paper['code_url'])
                repo_links = [l for l in page.links if 'github.com/' in l]
                self.assertEqual(repo_links, ['https://github.com/tianxinzh'])
        for path in DOCS.rglob('*'):
            if path.is_file():
                text = path.read_text(encoding='utf-8')
                for pattern in (r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                                r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
                                r'/workspace/', r'/root/', r'localhost', r'127\.0\.0\.1'):
                    self.assertNotRegex(text, pattern, f'Unexpected secret/local detail in {path}')

    def test_static_content_is_not_javascript_dependent(self):
        for paper in PAPERS:
            page = self.pages[DOCS / 'papers' / paper['slug'] / 'index.html']
            self.assertIn(paper['summary'], page.source)
            self.assertIn('Research question', page.source)
            self.assertIn('Scope &amp; limitations', page.source)
            self.assertIn('bib-' + paper['slug'], page.ids)
            button = [a for a in page.attrs('button') if 'data-copy-citation' in a]
            self.assertEqual(len(button), 1)
            self.assertIn('hidden', button[0])
            self.assertTrue(any(a.get('role') == 'status' and a.get('aria-live') == 'polite'
                                for a in page.attrs('p')))
        js = (DOCS / 'assets/site.js').read_text()
        self.assertNotRegex(js, r'\b(?:fetch|eval|XMLHttpRequest)\s*\(')
        self.assertIn('catch', js)
        self.assertIn('Select the citation text or download', js)

    def test_empirical_scope_regressions(self):
        papers = {p['slug']: p for p in PAPERS}
        jury = ' '.join(papers['juryprobe']['contributions'] + papers['juryprobe']['limitations'])
        for detail in ('Number and Entity', '0.402', '0.368', '3.13', '18.13',
                       '34 flagged', 'negative control', '0.004', 'no formal risk guarantee',
                       'all corrupted claims', 'GPT-4o-detectable subsets', '28% of deployment claims'):
            self.assertIn(detail, jury)
        sql = ' '.join(papers['modularsql']['contributions'] + papers['modularsql']['limitations'])
        for detail in ('DeepEye-SQL', 'BIRD-Dev', 'SQLite', '1,532', '65.86%', '67.75%',
                       '72.06%', '$0.0076 total', '120 ms amortized', 'tested only'):
            self.assertIn(detail, sql)
        dynamic = ' '.join(papers['openregshift']['contributions'] + papers['openregshift']['limitations'])
        for detail in ('12 dataset-shift pairs', '16-pair sensitivity', '+0.98', '+0.83',
                       'all 12 runs', '11%', '16%', 'not a finite-sample guarantee',
                       'does not use D_CF5 as an input'):
            self.assertIn(detail, dynamic)

    def test_css_accessibility_safeguards(self):
        css = (DOCS / 'assets/style.css').read_text()
        for feature in (':focus-visible', '.skip:focus', 'prefers-reduced-motion:reduce',
                        '@media(max-width:640px)', 'overflow-wrap:anywhere'):
            self.assertIn(feature, css)
        # WCAG normal-text contrast for the declared text/background palette.
        def luminance(hexcolor):
            rgb = [int(hexcolor[i:i+2], 16) / 255 for i in (0, 2, 4)]
            values = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb]
            return sum(c * weight for c, weight in zip(values, (.2126, .7152, .0722)))
        palette = dict(re.findall(r'--([\w-]+):#([0-9a-f]{6})', css))
        for fg in ('ink', 'muted', 'accent', 'green'):
            for bg in ('paper', 'white', 'soft'):
                light, dark = sorted([luminance(palette[fg]), luminance(palette[bg])], reverse=True)
                self.assertGreaterEqual((light + .05) / (dark + .05), 4.5, f'{fg} on {bg}')

    def test_build_is_reproducible(self):
        def hashes():
            return {p.relative_to(DOCS).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in DOCS.rglob('*') if p.is_file()}
        before = hashes()
        subprocess.run([sys.executable, str(ROOT / 'scripts/build.py')], cwd=ROOT,
                       check=True, stdout=subprocess.PIPE, text=True)
        self.assertEqual(hashes(), before, 'Generated output is stale or build is nondeterministic')


if __name__ == '__main__':
    unittest.main()
