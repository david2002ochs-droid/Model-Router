#!/usr/bin/env python3
"""Preserve model records exposed by evaluation-page payloads."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.executescript('''CREATE TABLE IF NOT EXISTS evaluation_page_models(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,model_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id)); CREATE TABLE IF NOT EXISTS evaluation_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,model_count INTEGER NOT NULL,error TEXT);''')
pages=c.execute("SELECT p.url,p.sha256,p.body_gzip FROM page_archive p LEFT JOIN evaluation_extraction_log l ON p.url=l.source_url WHERE p.url LIKE '%/evaluations/%' AND (l.page_sha256 IS NULL OR l.page_sha256<>p.sha256)").fetchall(); decoder=json.JSONDecoder();count=0
for url,sha,blob in pages:
 try:
  html=gzip.decompress(blob).decode('utf8',errors='replace');models={}
  for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
   payload=json.loads(m.group(1))
   for hit in re.finditer(r'"initialModels"\s*:\s*(?=\[)',payload):
    try: arr,_=decoder.raw_decode(payload,hit.end())
    except ValueError: continue
    if isinstance(arr,list):
     for obj in arr:
      if isinstance(obj,dict) and obj.get('id'):models[str(obj['id'])]=obj
  with c:
   c.execute('delete from evaluation_page_models where source_url=?',(url,))
   for id,obj in models.items():
    effort=obj.get('effort');effort=effort.get('slug') if isinstance(effort,dict) else effort if isinstance(effort,str) else None
    c.execute('insert into evaluation_page_models values(?,?,?,?,?,?,?)',(url,sha,id,obj.get('slug'),obj.get('name'),effort,json.dumps(obj,ensure_ascii=False)))
   c.execute('insert or replace into evaluation_extraction_log values(?,?,?,NULL)',(url,sha,len(models)))
  count+=len(models)
 except Exception as e:
  with c:c.execute('insert or replace into evaluation_extraction_log values(?,?,0,?)',(url,sha,str(e)[:500]))
print(f'{len(pages)} Seiten, {count} Modell-Datensätze')
