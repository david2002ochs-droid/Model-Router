#!/usr/bin/env python3
"""Extract provider tables with the extra Endpoint Accuracy Index column."""
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS provider_accuracy_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_slug TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,cost_per_task_usd REAL,time_per_task_minutes REAL,endpoint_accuracy_index_percent REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,function_calling TEXT,json_mode TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def n(x):
 try:return float(x.replace('$','').replace('%','').replace(',','').strip())
 except (ValueError,AttributeError):return None
N=0
for u,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url like '%/models/%/providers%'").fetchall():
 rows=json.loads(raw);idx=next((i for i,r in enumerate(rows) if len(r)==10 and r[0]['text']=='API Provider' and r[3]['text']=='Endpoint Accuracy Index'),None)
 if idx is None:continue
 slug=u.split('/models/',1)[1].split('/providers',1)[0]
 with c:
  c.execute('delete from provider_accuracy_observations where source_url=? and table_number=?',(u,tn))
  for i,row in enumerate(rows[idx+1:],1):
   v=[x['text'] for x in row]
   if len(v)!=10 or not v[0]:continue
   c.execute('insert into provider_accuracy_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(u,sha,slug,tn,i,v[0],n(v[1]),n(v[2]),n(v[3]),n(v[4]),n(v[5]),v[6] or None,v[7] or None,v[8] or None,v[9] or None,json.dumps(row,ensure_ascii=False)));N+=1
print('Zusätzliche Provider-Zeilen mit Accuracy:',N)
