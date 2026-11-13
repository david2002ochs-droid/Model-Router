#!/usr/bin/env python3
"""Extract the Harvey-LAB-AA benchmark's explicitly labelled cost-per-task array."""
import datetime,gzip,json,re,sqlite3
from pathlib import Path
URL='https://artificialanalysis.ai/evaluations/harvey-lab-aa'
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS harvey_exact_task_costs(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_name TEXT,creator_name TEXT,gated_all_pass_fraction REAL,criterion_pass_fraction REAL,material_hallucinations_per_task REAL,cost_per_task_usd REAL,release_date TEXT,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id))''')
row=c.execute('select sha256,body_gzip from page_archive where url=?',(URL,)).fetchone()
if not row:raise SystemExit('Harvey-LAB-AA-Seite ist nicht archiviert')
sha,blob=row;h=gzip.decompress(blob).decode('utf8',errors='replace');dec=json.JSONDecoder();data={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',h):
 s=json.loads(m.group(1))
 for x in re.finditer(r'"models"\s*:\s*(?=\[)',s):
  try:arr,_=dec.raw_decode(s,x.end())
  except ValueError:continue
  if not isinstance(arr,list):continue
  for o in arr:
   if not isinstance(o,dict) or not o.get('id') or not all(k in o for k in ('gatedAllPass','criterionPassRate','materialHallucinationsPerTask','costPerTask')):continue
   data[str(o['id'])]=o
if len(data)<3:raise SystemExit('Erwartete Harvey-Ergebnisliste fehlt; keine Änderungen')
def num(x):return x if isinstance(x,(int,float)) and not isinstance(x,bool) else None
with c:
 c.execute('delete from harvey_exact_task_costs where source_url=?',(URL,))
 for id,o in data.items():
  creator=o.get('creator');creator=creator if isinstance(creator,dict) else {}
  c.execute('insert into harvey_exact_task_costs values(?,?,?,?,?,?,?,?,?,?,?)',(URL,sha,id,o.get('name'),creator.get('name'),num(o.get('gatedAllPass')),num(o.get('criterionPassRate')),num(o.get('materialHallucinationsPerTask')),num(o.get('costPerTask')),o.get('releaseDate'),json.dumps(o,ensure_ascii=False,separators=(',',':'))))
print('Modelle:',len(data),'mit Kosten:',sum(num(o.get('costPerTask')) is not None for o in data.values()))
