#!/usr/bin/env python3
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.execute('''CREATE TABLE IF NOT EXISTS provider_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_slug TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def num(x):
 try:return float(x.replace('$','').replace('%','').replace(',','').strip())
 except (ValueError,AttributeError):return None
count=0
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url like '%/models/%/providers%' ").fetchall():
 rows=json.loads(raw); header=next((i for i,r in enumerate(rows) if r and r[0]['text']=='API Provider' and len(r)>=9),None)
 if header is None:continue
 slug=url.split('/models/',1)[1].split('/providers',1)[0]
 with c:
  c.execute('delete from provider_observations where source_url=? and table_number=?',(url,tn))
  for n,row in enumerate(rows[header+1:],1):
   vals=[x['text'] for x in row]
   if len(vals)!=9 or not vals[0]:continue
   c.execute('insert into provider_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,slug,tn,n,vals[0],num(vals[1]),num(vals[2]),num(vals[3]),num(vals[4]),vals[5] or None,vals[6] or None,vals[7] or None,vals[8] or None,json.dumps(row,ensure_ascii=False)));count+=1
print('Providerzeilen gespeichert:',count)
