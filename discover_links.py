#!/usr/bin/env python3
"""Queue relevant public HTML links found in archived pages, preserving origin."""
import gzip,re,sqlite3,urllib.parse
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.execute('create table if not exists discovered_links(url TEXT NOT NULL,source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,PRIMARY KEY(url,source_url))')
links={}
for source,sha,blob in c.execute('select url,sha256,body_gzip from page_archive').fetchall():
 html=gzip.decompress(blob).decode('utf8',errors='replace')
 for href in re.findall(r'href="([^"#]+)',html):
  u=urllib.parse.urlsplit(urllib.parse.urljoin('https://artificialanalysis.ai',href));path=u.path.rstrip('/')
  if u.hostname!='artificialanalysis.ai' or not re.match(r'^/(models|providers|evaluations|agents|methodology)/',path) or re.search(r'\.(svg|png|jpg|json|xml|pdf|js|css)$',path,re.I):continue
  url='https://artificialanalysis.ai'+path
  links.setdefault(url,(source,sha))
before=c.execute('select count(*) from crawl_queue').fetchone()[0]
with c:
 c.executemany('insert or ignore into crawl_queue(url) values(?)',[(u,) for u in links])
 c.executemany('insert or ignore into discovered_links values(?,?,?)',[(u,s,h) for u,(s,h) in links.items()])
after=c.execute('select count(*) from crawl_queue').fetchone()[0]
print('Links:',len(links),'neu in Warteschlange:',after-before)
