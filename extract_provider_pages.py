#!/usr/bin/env python3
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.execute('''CREATE TABLE IF NOT EXISTS provider_page_models(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_slug TEXT NOT NULL,model_name TEXT NOT NULL,intelligence_index REAL,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def n(s):
 try:return float(s.replace('$','').replace('%','').replace(',','').strip())
 except ValueError:return None
N=0
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url like 'https://artificialanalysis.ai/providers/%'").fetchall():
 rows=json.loads(raw);idx=next((i for i,r in enumerate(rows) if len(r)==11 and r[0]['text']=='Model' and 'Intelligence Index' in r[1]['text'] and 'Cost per Task' in r[2]['text']),None)
 if idx is None:continue
 slug=url.split('/providers/',1)[1].strip('/')
 with c:
  c.execute('delete from provider_page_models where source_url=? and table_number=?',(url,tn))
  for j,row in enumerate(rows[idx+1:],1):
   v=[x['text'] for x in row]
   if len(v)!=11 or not v[0]:continue
   c.execute('insert into provider_page_models values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,tn,j,slug,v[0],*[n(x) for x in v[1:6]],v[6] or None,v[7] or None,v[8] or None,v[9] or None,json.dumps(row,ensure_ascii=False)));N+=1
print('Provider-Detailzeilen',N)
