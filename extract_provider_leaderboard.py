#!/usr/bin/env python3
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'))
c.execute('''CREATE TABLE IF NOT EXISTS provider_leaderboard_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider TEXT,model_name TEXT,intelligence_index REAL,cost_per_task_usd REAL,time_per_task_minutes REAL,first_answer_token_seconds REAL,error_rate_percent REAL,context_window TEXT,license TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def n(s):
 try:return float(s.replace('$','').replace('%','').replace(',','').strip())
 except ValueError:return None
N=0
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url='https://artificialanalysis.ai/leaderboards/providers'").fetchall():
 rows=json.loads(raw);idx=next((i for i,r in enumerate(rows) if len(r)==10 and r[0]['text']=='API Provider' and r[1]['text']=='Model'),None)
 if idx is None:continue
 with c:
  c.execute('delete from provider_leaderboard_observations where source_url=? and table_number=?',(url,tn))
  for j,row in enumerate(rows[idx+1:],1):
   v=[x['text'] for x in row]
   if len(v)!=10 or not v[0] or not v[1]:continue
   c.execute('insert into provider_leaderboard_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,tn,j,v[0],v[1],*[n(x) for x in v[2:7]],v[7] or None,v[8] or None,json.dumps(row,ensure_ascii=False)));N+=1
print('Provider-Ranglisten-Zeilen',N)
