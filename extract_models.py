#!/usr/bin/env python3
"""Extract currentModel objects from Next.js server-rendered payloads without changing numeric units."""
import gzip, json, re, sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.executescript('''CREATE TABLE IF NOT EXISTS model_details(source_url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, model_id TEXT, slug TEXT, name TEXT, effort TEXT, model_json TEXT NOT NULL); CREATE TABLE IF NOT EXISTS model_extraction_log(source_url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, object_count INTEGER NOT NULL, error TEXT);''')
query="""SELECT p.url,p.sha256,p.body_gzip FROM page_archive p LEFT JOIN model_extraction_log l ON p.url=l.source_url WHERE p.url LIKE 'https://artificialanalysis.ai/models/%' AND (l.page_sha256 IS NULL OR l.page_sha256<>p.sha256)"""
pages=c.execute(query).fetchall(); dec=json.JSONDecoder(); total=0
for url,sha,blob in pages:
 try:
  html=gzip.decompress(blob).decode('utf-8',errors='replace'); found=[]; initial=[]
  for match in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
   payload=json.loads(match.group(1))
   for hit in re.finditer(r'"currentModel"\s*:\s*(?=\{)',payload):
    try: obj,_=dec.raw_decode(payload,hit.end())
    except ValueError: continue
    if isinstance(obj,dict) and obj.get('id') and obj.get('slug'):found.append(obj)
   for hit in re.finditer(r'"initialModels"\s*:\s*(?=\[)',payload):
    try: arr,_=dec.raw_decode(payload,hit.end())
    except ValueError: continue
    if isinstance(arr,list):initial.extend(x for x in arr if isinstance(x,dict) and x.get('id') and x.get('slug'))
  slug=url.split('?',1)[0].rstrip('/').split('/')[-1]
  obj=next((x for x in found if x['slug']==slug),None)
  if obj is None:
   candidates={str(x['id']):x for x in initial if x['slug']==slug}
   if len(candidates)==1:obj=next(iter(candidates.values()))
  if obj is None and '/models/releases/' in url:
   candidates={str(x['id']):x for x in found if isinstance(x.get('release'),dict) and x['release'].get('slug')==slug}
   if len(candidates)==1:obj=next(iter(candidates.values()))
  with c:
   if obj:
    effort=obj.get('effort');effort=effort.get('slug') if isinstance(effort,dict) else None
    c.execute('INSERT OR REPLACE INTO model_details VALUES(?,?,?,?,?,?,?)',(url,sha,str(obj['id']),obj['slug'],obj.get('name'),effort,json.dumps(obj,ensure_ascii=False)))
    total+=1
   c.execute('INSERT OR REPLACE INTO model_extraction_log VALUES(?,?,?,NULL)',(url,sha,len(found)))
 except Exception as e:
  with c:c.execute('INSERT OR REPLACE INTO model_extraction_log VALUES(?,?,0,?)',(url,sha,str(e)[:500]))
print(f'{len(pages)} Seiten geprüft, {total} Modellobjekte gespeichert')
