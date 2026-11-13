#!/usr/bin/env python3
"""Extract public Decision Index contestants and dataset-specific cost/latency."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.executescript('''CREATE TABLE IF NOT EXISTS decision_index_contestants(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,contestant_slug TEXT NOT NULL,contestant_name TEXT,contestant_kind TEXT,
 host_name TEXT,creator_name TEXT,index_score REAL,accuracy_index_score REAL,cost_usd_per_task REAL,median_time_ms_per_task REAL,
 brier REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,contestant_slug));
CREATE TABLE IF NOT EXISTS decision_dataset_results(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,contestant_slug TEXT NOT NULL,contestant_name TEXT,
 contestant_kind TEXT,host_name TEXT,creator_name TEXT,dataset_slug TEXT NOT NULL,cost_usd_per_task REAL,
 median_time_ms_per_task REAL,brier REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,contestant_slug,dataset_slug));''')
url='https://artificialanalysis.ai/evaluations/artificial-analysis-decision-index';r=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if not r:raise SystemExit('Decision-Index-Seite fehlt')
sha,blob=r;h=gzip.decompress(blob).decode('utf8',errors='replace');d=json.JSONDecoder();best={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',h):
 s=json.loads(m.group(1))
 for hit in re.finditer(r'"contestants"\s*:\s*(?=\[)',s):
  try:arr,_=d.raw_decode(s,hit.end())
  except ValueError:continue
  if not isinstance(arr,list):continue
  objs={str(o['slug']):o for o in arr if isinstance(o,dict) and o.get('slug') and isinstance(o.get('byDataset'),dict) and 'costPerTaskUsd' in o}
  if len(objs)>len(best):best=objs
if len(best)<5:raise SystemExit('Erwartete Decision-Konfigurationen fehlen; nichts ersetzt')
count=0
with c:
 c.execute('delete from decision_dataset_results where source_url=?',(url,));c.execute('delete from decision_index_contestants where source_url=?',(url,))
 for slug,o in best.items():
  c.execute('insert into decision_index_contestants values(?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,slug,o.get('name'),o.get('kind'),o.get('hostName'),o.get('creatorName'),o.get('indexScore'),o.get('accuracyIndexScore'),o.get('costPerTaskUsd'),o.get('timePerTaskMs'),o.get('brier'),json.dumps(o,ensure_ascii=False)))
  for ds,v in o['byDataset'].items():
   if not isinstance(v,dict):continue
   c.execute('insert into decision_dataset_results values(?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,slug,o.get('name'),o.get('kind'),o.get('hostName'),o.get('creatorName'),ds,v.get('costPerTaskUsd'),v.get('timePerTaskMs'),v.get('brier'),json.dumps(v,ensure_ascii=False)));count+=1
print('Decision-Konfigurationen:',len(best),'Datensatzzeilen:',count)
