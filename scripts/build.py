#!/usr/bin/env python3
"""Build a dependency-free, crawlable academic site for GitHub Pages."""
from pathlib import Path
from html import escape
import argparse, json, re, shutil
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path,
                    help='Write to this directory instead of docs (useful for isolated checks).')
args=parser.parse_args()
OUT=args.output_dir.resolve() if args.output_dir else ROOT/'docs'
SITE_NAME='Tianxin Research Page'
REPOSITORY='https://github.com/tianxinzh/tianxin-research-page'
PREFIX='/tianxin-research-page'
BASE='https://tianxinzh.github.io'+PREFIX
ROBOTS='index,follow'
VERIFIED='2026-10-05'
PAPERS=json.loads((ROOT/'content/papers.json').read_text())
SCHOLAR='https://scholar.google.com/citations?user=hkDNs4MAAAAJ&hl=en'
AUTHOR={'@type':'Person','name':'Tianxin Zhou','sameAs':[SCHOLAR,'https://github.com/tianxinzh']}
def e(s): return escape(str(s),quote=True)
def write(path,text):
 # Root-relative template links are site-relative, including assets and downloads.
 # Keep fragments/external links unchanged, and apply the project prefix once.
 if str(path).endswith('.html'):
  text=re.sub(r'(\b(?:href|src)=")/(?!/)', lambda m:m.group(1)+PREFIX+'/', text)
 p=OUT/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8')
def ul(items): return '<ul>'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>'
def link(href,label,cls=''): return f'<a href="{e(href)}"'+(f' class="{e(cls)}"' if cls else '')+'>'+label+'</a>'
def page(title,desc,path,body,schema=None,meta='',section=''):
 nav=''.join(f'<a href="{href}"'+(' aria-current="page"' if section==name else '')+(' class="nav-sources"' if name=='Sources' else '')+f'>{name}</a>' for href,name in [('/#publications','Papers'),('/citations/','Citations'),('/sources/','Sources')])
 schema_json=json.dumps(schema or {'@context':'https://schema.org','@type':'WebPage','name':title,'url':BASE+path},ensure_ascii=False).replace('</','<\\/')
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE+path}"><meta name="robots" content="{ROBOTS}"><meta name="theme-color" content="#f6f3ed">
<meta property="og:type" content="{'article' if path.startswith('/papers/') else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE+path}"><meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="stylesheet" href="/assets/style.css">{meta}
<script type="application/ld+json">{schema_json}</script>
<script src="/assets/site.js" defer></script></head><body>
<a class="skip" href="#main">Skip to content</a><div class="wrap"><header class="masthead"><a class="wordmark" href="/" aria-label="Tianxin Research Page home">{SITE_NAME}</a><nav class="nav" aria-label="Main navigation">{nav}</nav></header>
<main id="main">{body}</main><footer class="footer"><div>{SITE_NAME}<br>Publications, methods &amp; evidence</div><div><a href="{REPOSITORY}">Site repository</a><a href="/citations/">Citations</a><a href="/sources/">Sources &amp; notes</a></div></footer></div></body></html>'''
def citebox(p):
 s=p['slug']
 return f'''<div class="citation-box"><header><span>BIBTEX · {e(p['short_name'])}</span><button type="button" data-copy-citation="bib-{s}" hidden>Copy citation</button></header><pre id="bib-{s}">{e(p['bibtex'])}</pre><p class="toast" role="status" aria-live="polite"></p></div><p class="small"><a href="/citations/{s}.bib" download>Download BibTeX</a></p>'''
def paper_card(p):
 name=p['short_name']; tag=' <span class="tag">TMLR 2026</span>' if p['slug']=='juryprobe' else '<span>PREPRINT · 2026</span>'
 actions=link('/papers/'+p['slug']+'/','Read summary <span aria-hidden="true">→</span>')+link(p['review_url'] or p['paper_url'],'Published paper' if p['review_url'] else 'arXiv paper')
 if p['code_url']: actions+=link(p['code_url'],'Public code')
 return f'''<article class="paper-card"><div class="paper-meta"><div class="paper-name">{e(name)}</div>{tag}</div><div><h3><a href="/papers/{p['slug']}/">{e(p['title'])}</a></h3><p>{e(p['summary'])}</p><p class="authors">{e(' · '.join(p['authors']))}</p></div><div class="paper-actions">{actions}</div></article>'''
OUT.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
hero='''<section class="hero" aria-labelledby="collection-title"><div><p class="eyebrow">Tianxin Research Page · Publication collection</p><h1 id="collection-title">Research papers.<br>Methods &amp;<br>evidence.</h1><p class="intro">When do machine-learning systems fail, and when does a targeted intervention help?</p><p class="small">Three papers on factuality evaluation, text-to-SQL, and regression under distribution shift. Read the findings, inspect their limits, and follow the original evidence.</p><div class="links"><a href="#publications">Explore the papers <span class="arrow" aria-hidden="true">→</span></a><a href="/citations/">Download citations <span class="arrow" aria-hidden="true">→</span></a></div></div><aside class="research-map" aria-label="Research topics"><p class="eyebrow">Explore by research question</p><div class="map-row"><span class="map-no">01</span><div><h2><a href="/papers/juryprobe/">Evaluate consensus</a></h2><p>When do agreeing factuality judges share the same mistakes?</p></div></div><div class="map-row"><span class="map-no">02</span><div><h2><a href="/papers/modularsql/">Inspect execution</a></h2><p>Which SQL errors disappear when duplicate rows are ignored?</p></div></div><div class="map-row"><span class="map-no">03</span><div><h2><a href="/papers/openregshift/">Adapt selectively</a></h2><p>When does regional reweighting help under distribution shift?</p></div></div></aside></section>'''
home=hero+'<section class="section" id="publications"><div class="section-top"><div><p class="eyebrow">Paper index · 2026</p><h2>Publications</h2></div><p class="section-note">Methods, findings, and limits.<br>Links to the original work.</p></div>'+''.join(paper_card(p) for p in PAPERS)+'</section>'+'''<section class="section" id="collection"><div class="about-grid"><div><p class="eyebrow">Read. Inspect. Reproduce.</p><h2>Follow the<br>evidence.</h2></div><div><p>Each paper page brings together the research question, method, reported results, limitations, and citation metadata. Author credits follow the original publication records.</p><p>Read the original paper for complete experimental details. Public code is linked where its release is verified; code availability is stated separately for every paper.</p><div class="links"><a href="/citations/">Citation library <span aria-hidden="true">→</span></a><a href="/sources/">Sources &amp; verification <span aria-hidden="true">→</span></a></div></div></div></section>'''
collection={'@context':'https://schema.org','@type':'CollectionPage','@id':BASE+'/#collection','name':SITE_NAME,'url':BASE+'/','description':'Research papers on factuality evaluation, text-to-SQL, and regression under distribution shift.','mainEntity':{'@type':'ItemList','numberOfItems':len(PAPERS),'itemListElement':[{'@type':'ListItem','position':i+1,'url':BASE+'/papers/'+p['slug']+'/','name':p['title']} for i,p in enumerate(PAPERS)]}}
write('index.html',page(SITE_NAME+' | Machine Learning Papers','Research papers on factuality evaluation, text-to-SQL execution, and regression under distribution shift. Methods, findings, limitations, public resources, and citations.','/',home,collection,section='Papers'))
paths=['/','/citations/','/sources/']
for p in PAPERS:
 s=p['slug']; path='/papers/'+s+'/'
 paths.append(path)
 authors=[dict(AUTHOR) if a=='Tianxin Zhou' else {'@type':'Person','name':a} for a in p['authors']]
 schema={'@context':'https://schema.org','@type':'ScholarlyArticle','@id':BASE+path+'#article','url':BASE+path,'name':p['title'],'headline':p['title'],'author':authors,'description':p['summary'],'inLanguage':'en','identifier':{'@type':'PropertyValue','propertyID':'arXiv','value':p['arxiv_id']},'sameAs':[p['paper_url']]+([p['review_url']] if p['review_url'] else []),'isAccessibleForFree':True}
 if p['publication_date']: schema['datePublished']=p['publication_date']
 if p['review_url']: schema['isPartOf']={'@type':'Periodical','name':p['venue']}
 if p['code_url']: schema['hasPart']={'@type':'SoftwareSourceCode','codeRepository':p['code_url'],'name':p['short_name']}
 meta='\n'+''.join(f'<meta name="{n}" content="{e(v)}">\n' for n,v in [('citation_title',p['title']),*[("citation_author",a) for a in p['authors']],('citation_publication_date',p['publication_date'] or str(p['year'])),('citation_pdf_url',p['pdf_url']),('citation_arxiv_id',p['arxiv_id']),('citation_abstract_html_url',BASE+path)]+([('citation_journal_title',p['venue'])] if p['review_url'] else []))
 publicnote='Public research implementation.' if p['code_url'] else ('Code is not publicly released.' if s=='openregshift' else 'A public code release could not be verified on 5 October 2026.')
 resources=link(p['review_url'],'TMLR / OpenReview →') if p['review_url'] else ''
 resources+=link(p['paper_url'],'arXiv record →')+link(p['pdf_url'],'Paper PDF on arXiv →')+link(p['html_url'],'Full-text HTML on arXiv →')
 if p['code_url']: resources+=link(p['code_url'],'Public code on GitHub →')
 sources=''.join('<li>'+link(url,e('arXiv record' if '/abs/' in url else 'Full-text paper' if '/html/' in url else 'arXiv citation export' if '/bibtex/' in url else 'Public implementation'))+'</li>' for url in p['sources'])
 statusnote='<p class="small">TMLR status is stated in the arXiv journal reference. The linked OpenReview record provides the venue page.</p>' if s=='juryprobe' else ''
 body=f'''<header class="page-head paper-head"><a class="back" href="/#publications">← All papers</a><p class="eyebrow">{e(p['short_name'])} · Research paper</p><h1>{e(p['title'])}</h1><p class="authors">{e(' · '.join(p['authors']))}</p><div class="publication-meta"><span class="tag">{e(p['status'])}</span><span>arXiv:{e(p['arxiv_id'])}</span></div></header><div class="paper-layout"><article class="paper-body"><h2>Research question</h2><p class="lead">{e(p['summary'])}</p><h2>Method &amp; reported findings</h2>{ul(p['contributions'])}<section class="limits"><h2>Scope &amp; limitations</h2>{ul(p['limitations'])}</section><h2 id="citation">Cite this paper</h2>{citebox(p)}{statusnote}<h2 id="sources">Original sources</h2><ul class="source-list">{sources}</ul><p class="provenance">Source records checked 5 October 2026. This page is an editorial summary of the linked public paper. Results apply to the experimental conditions reported there; see the full text for definitions and complete evidence.</p></article><aside class="sidebar"><section class="sidebar-block"><h2>Read the work</h2>{resources}</section><section class="sidebar-block"><h2>Code availability</h2><p>{e(publicnote)}</p></section><section class="sidebar-block"><h2>On this page</h2><a href="#citation">Citation &amp; downloads</a><a href="#sources">Original sources</a><a href="/citations/">All paper citations</a></section></aside></div>'''
 write('papers/'+s+'/index.html',page(p['title']+' | '+SITE_NAME,p['summary'],path,body,schema,meta,section='Papers'))
 write('citations/'+s+'.bib',p['bibtex']+'\n')
write('citations/publications.bib','\n\n'.join(p['bibtex'] for p in PAPERS)+'\n')
citations='''<header class="page-head"><p class="eyebrow">Reference library</p><h1 style="font-size:clamp(3rem,7vw,5rem)">Cite the research.</h1><p class="intro">Verified paper titles, ordered authors, and direct links to the original work.</p><a href="/citations/publications.bib" download>Download all three citations (.bib)</a></header>'''+''.join(f'<article class="citation-item"><p class="eyebrow">{e(p["status"])}</p><h2><a href="/papers/{p["slug"]}/">{e(p["title"])}</a></h2><p>{e(" · ".join(p["authors"]))}</p>{citebox(p)}</article>' for p in PAPERS)+'<p class="provenance">Citations are assembled from the linked public source records. No unverified DOI, issue, volume, or page range has been added. Prefer a venue’s current citation export if the publication metadata changes.</p>'
write('citations/index.html',page('Paper Citations | '+SITE_NAME,'Download BibTeX metadata for JuryProbe, ModularSQL, and the OpenRegShift research paper.','/citations/',citations,{'@context':'https://schema.org','@type':'CollectionPage','name':SITE_NAME+' citations','url':BASE+'/citations/','isPartOf':{'@type':'CollectionPage','@id':BASE+'/#collection'}},section='Citations'))
sources='''<header class="page-head"><p class="eyebrow">Source transparency</p><h1 style="font-size:clamp(3rem,7vw,5rem)">Sources &amp; notes</h1><p class="intro">Short summaries, with the original evidence one click away.</p></header><article class="wide-text"><h2>How these pages are written</h2><p>Paper titles, author order, identifiers, and publication status are taken from the linked public research records. Summaries describe the papers’ questions and methods in concise language. Numerical findings are attributed to the experiments in the original papers, rather than presented as general guarantees.</p><p>The research listed here is by Tianxin Zhou and Ruixi Lin. This is a selected collection of three papers, not a claim to be a complete publication list.</p><h2>Publication records</h2><ul><li><a href="https://arxiv.org/abs/2608.20607">JuryProbe</a>: the arXiv journal reference states acceptance at Transactions on Machine Learning Research in 2026. The paper links its <a href="https://openreview.net/forum?id=dgBczhxcZY">OpenReview record</a>. The venue page could not be independently read during this check.</li><li><a href="https://arxiv.org/abs/2609.29573">ModularSQL</a>: displayed as an arXiv preprint. Only the year is displayed because the source record’s submission date and identifier month were inconsistent when checked.</li><li><a href="https://arxiv.org/abs/2608.18330">When Does Dynamic Ensembling Pay Off?</a>: displayed as an arXiv preprint, under the project label OpenRegShift.</li></ul><h2>Code and full text</h2><p>ModularSQL links to its verified public repository. A public JuryProbe code release could not be verified. OpenRegShift code is not publicly released. No private code, data, or repository content is hosted here.</p><p>Full-text links go to the original arXiv and venue pages. This site does not redistribute the papers’ PDF files. It does not assign a license to the papers or their research implementations.</p><h2>Citation metadata</h2><p>The citation library supplies BibTeX records. Entries use verified titles, author order, year, and public identifiers. The JuryProbe entry uses the TMLR venue record. Unverified DOI, issue, volume, and pagination fields are omitted.</p><h2>Last checked</h2><p>5 October 2026. Source pages and code availability can change after this date.</p></article>'''
write('sources/index.html',page('Sources & Verification Notes | '+SITE_NAME,'Source records, publication status, code availability, and citation metadata notes for the selected research collection.','/sources/',sources,{'@context':'https://schema.org','@type':'WebPage','name':'Sources and verification notes','url':BASE+'/sources/'},section='Sources'))
write('404.html',page('Page Not Found | '+SITE_NAME,'Find the research papers and citation library.','/404.html','<section class="not-found"><p class="eyebrow">404 · Page not found</p><h1>Back to the research.</h1><p>This address does not match a page in the collection.</p><a href="/">Visit the paper index →</a></section>').replace('content="index,follow"','content="noindex,follow"'))
write('robots.txt','User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n')
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{BASE+p}</loc><lastmod>{VERIFIED}</lastmod></url>\n' for p in paths)+'</urlset>\n')
write('.nojekyll','')
# Never carry a custom-domain binding into the independent GitHub Pages build.
(OUT/'CNAME').unlink(missing_ok=True)
print(f"Built {len(paths)} indexable pages in {OUT}; canonical={BASE}")
