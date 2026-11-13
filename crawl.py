#!/usr/bin/env python3
"""Resumable public sitemap archive, one request at a time."""
import datetime, gzip, hashlib, sqlite3, subprocess, sys, time, urllib.request, urllib.error, xml.etree.ElementTree as ET
from pathlib import Path
DB=Path(__file__).with_name('artificial_analysis.sqlite3')
db=sqlite3.connect(DB, timeout=60)
db.execute("PRAGMA busy_timeout=60000")
db.executescript('''CREATE TABLE IF NOT EXISTS crawl_queue(url TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'pending', http_status INTEGER, retrieved_at_utc TEXT, error TEXT); CREATE TABLE IF NOT EXISTS page_archive(url TEXT PRIMARY KEY REFERENCES crawl_queue(url), sha256 TEXT NOT NULL, content_type TEXT, body_gzip BLOB NOT NULL);''')
db.execute('CREATE TABLE IF NOT EXISTS page_capture_events(id INTEGER PRIMARY KEY,source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,final_url TEXT,content_type TEXT)')
headers={'User-Agent':'Mozilla/5.0 (compatible; research archive)'}
with urllib.request.urlopen(urllib.request.Request('https://artificialanalysis.ai/sitemap.xml',headers=headers),timeout=45) as r: sitemap=r.read()
root=ET.fromstring(sitemap)
urls=[x.text for x in root.iter() if x.tag.endswith('loc') and x.text and x.text.startswith('https://artificialanalysis.ai/')]
with db: db.executemany('INSERT OR IGNORE INTO crawl_queue(url) VALUES(?)',[(u,) for u in urls])
print('Warteschlange:',len(urls),flush=True)
while True:
 row=db.execute("SELECT url FROM crawl_queue WHERE status='pending' ORDER BY CASE WHEN url LIKE '%/evaluations/%' THEN 0 WHEN url LIKE '%/methodology/%' THEN 1 WHEN url LIKE '%/agents/%' THEN 1 WHEN url LIKE '%/models/%' AND url NOT LIKE '%/providers%' AND url NOT LIKE '%/comparisons/%' THEN 2 WHEN url LIKE '%/models/%/providers%' THEN 3 WHEN url LIKE '%/providers/%' THEN 4 WHEN url LIKE '%/comparisons/%' THEN 6 ELSE 5 END, rowid LIMIT 1").fetchone()
 if row is None:
  for script in ('discover_links.py','retry_transient.py'):
   result=subprocess.run([sys.executable,str(DB.parent/script)],check=False)
   if result.returncode:
    raise RuntimeError(f'{script} fehlgeschlagen; Abdeckung nicht vollständig geprüft')
  row=db.execute("SELECT url FROM crawl_queue WHERE status='pending' LIMIT 1").fetchone()
  if row is None:
   print('Keine ausstehenden Seiten nach Linksuche und Wiederholungen.',flush=True);break
  continue
 url=row[0];now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:
   raw=r.read();code=r.status;ctype=r.headers.get('Content-Type','');final_url=r.geturl()
 except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError) as e:
  code=getattr(e,'code',None)
  with db:db.execute("UPDATE crawl_queue SET status='error',http_status=?,retrieved_at_utc=?,error=? WHERE url=?",(code,now,str(e)[:500],url))
  print(url,code,str(e),flush=True)
  if code in (403,429):print('Zugriff begrenzt; gestoppt:',code,flush=True);break
 else:
  with db:
   db.execute('INSERT OR REPLACE INTO page_archive VALUES(?,?,?,?)',(url,hashlib.sha256(raw).hexdigest(),ctype,gzip.compress(raw)))
   db.execute('INSERT INTO page_capture_events(source_url,page_sha256,retrieved_at_utc,final_url,content_type) VALUES(?,?,?,?,?)',(url,hashlib.sha256(raw).hexdigest(),now,final_url,ctype))
   db.execute("UPDATE crawl_queue SET status='ok',http_status=?,retrieved_at_utc=?,error=NULL WHERE url=?",(code,now,url))
  print(url,code,flush=True)
 time.sleep(0.5)
