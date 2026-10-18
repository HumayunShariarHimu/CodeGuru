#!/usr/bin/env python3
"""Write a sitemap and robots policy for the final static GitHub Pages artifact."""
import json
from pathlib import Path
from urllib.parse import quote

root=Path.cwd().resolve()
site=Path('_site').resolve()
meta=json.loads((root/'pages-metadata.json').read_text(encoding='utf-8'))
base=meta['site_url'].rstrip('/')
urls=[]
for path in sorted(site.rglob('*.html')):
    rel=path.relative_to(site).as_posix()
    if rel=='404.html':
        continue
    if rel=='index.html':
        suffix=''
    elif rel.endswith('/index.html'):
        suffix=rel[:-len('index.html')]
    else:
        suffix=rel
    urls.append(base+'/'+quote(suffix,safe='/._-'))
xml=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in urls:
    xml.append(f'  <url><loc>{url}</loc></url>')
xml.append('</urlset>')
(site/'sitemap.xml').write_text('\n'.join(xml)+'\n',encoding='utf-8')
(site/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n',encoding='utf-8')
print(f'Wrote sitemap for {len(urls)} HTML routes')
