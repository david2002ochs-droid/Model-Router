#!/usr/bin/env python3
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.execute('''CREATE TABLE IF NOT EXISTS search_api_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,provider_variant TEXT NOT NULL,search_index REAL,baseline_lift REAL,deepsearchqa_f1 REAL,browsecomp_accuracy REAL,omniscience_accuracy REAL,search_cost_usd_per_1000 REAL,model_cost_usd_per_1000 REAL,time_per_task_seconds REAL,website TEXT,raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
def n(s):
 try:return float(s.replace('$','').replace(',','').replace('s','').strip())
 except ValueError:return None
N=0
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url like '%/agents/search-api%'").fetchall():
 rows=json.loads(raw);i=next((i for i,r in enumerate(rows) if len(r)==10 and r[0]['text']=='Provider' and 'Search Index' in r[1]['text'] and 'DeepSearchQA' in r[3]['text']),None)
 if i is None:continue
 with c:
  c.execute('delete from search_api_observations where source_url=? and table_number=?',(url,tn))
  for j,row in enumerate(rows[i+1:],1):
   v=[x['text'] for x in row]
   if len(v)!=10 or not v[0]:continue
   c.execute('insert into search_api_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,tn,j,v[0],*[n(x) for x in v[1:9]],v[9] or None,json.dumps(row,ensure_ascii=False)));N+=1
print('Search-API-Zeilen',N)
