#!/usr/bin/env python3
"""Extract the public provider cache pricing table, retaining row-spanned provider labels."""
import json,sqlite3
from pathlib import Path
URL='https://artificialanalysis.ai/models/caching'
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS cache_pricing_source_rows(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_group_raw TEXT NOT NULL,provider_links_json TEXT NOT NULL,model_name TEXT NOT NULL,input_usd_per_million REAL,cache_write_usd_per_million REAL,cache_hit_usd_per_million REAL,cache_storage_raw TEXT,output_usd_per_million REAL,auto_enabled_raw TEXT,min_tokens_raw TEXT,cache_ttl_raw TEXT,notes_raw TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def num(s):
 try:return float(s.replace('$','').replace(',','').strip())
 except (ValueError,AttributeError):return None
n=0
for u,sha,tn,raw in c.execute('select url,page_sha256,table_number,rows_json from extracted_tables where url=?',(URL,)).fetchall():
 a=json.loads(raw)
 if not a or [x['text'] for x in a[0]]!=['Provider','Model','Input (standard)','Cache write','Cache hit','Cache storage','Output (standard)','Auto-Enabled','Min tokens','Cache TTL','Notes']:continue
 group=None;links=[];buf=[]
 for i,row in enumerate(a[1:],1):
  v=[x['text'] for x in row]
  if len(v)==11:group=v.pop(0);links=row[0].get('links',[])
  elif len(v)!=10:raise RuntimeError('Unexpected cache table row length at row '+str(i))
  if not group:raise RuntimeError('Missing provider group at row '+str(i))
  if not v[0]:continue
  buf.append((u,sha,tn,i,group,json.dumps(links,ensure_ascii=False),v[0],num(v[1]),num(v[2]),num(v[3]),v[4] or None,num(v[5]),v[6] or None,v[7] or None,v[8] or None,v[9] or None,json.dumps(row,ensure_ascii=False)))
 with c:
  c.execute('delete from cache_pricing_source_rows where source_url=? and table_number=?',(u,tn));c.executemany('insert into cache_pricing_source_rows values('+','.join('?'*17)+')',buf)
 n+=len(buf)
print('Cache-Preiszeilen:',n)
