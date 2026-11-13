#!/usr/bin/env python3
import gzip,json,re,sqlite3,sys
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.execute('''CREATE TABLE IF NOT EXISTS embedded_model_snapshots(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,model_json TEXT NOT NULL,PRIMARY KEY(source_url,page_sha256,model_id))''')
url=sys.argv[1] if len(sys.argv)>1 else 'https://artificialanalysis.ai/models/claude-fable-5-1-high'
row=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if row is None:sys.exit('Seite ist nicht im Archiv')
sha,blob=row;html=gzip.decompress(blob).decode('utf8',errors='replace');decoder=json.JSONDecoder();best=[]
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
 payload=json.loads(m.group(1))
 for hit in re.finditer(r'"models"\s*:\s*(?=\[)',payload):
  try: arr,_=decoder.raw_decode(payload,hit.end())
  except ValueError:continue
  if isinstance(arr,list):
   objs=[o for o in arr if isinstance(o,dict) and o.get('id') and o.get('slug') and 'intelligenceIndexEvaluations' in o]
   if len(objs)>len(best):best=objs
if len(best)<10:sys.exit('Keine ausreichend große Modellliste gefunden')
with c:
 for obj in best:
  effort=obj.get('effort');effort=effort.get('slug') if isinstance(effort,dict) else None
  c.execute('insert or replace into embedded_model_snapshots values(?,?,?,?,?,?,?)',(url,sha,str(obj['id']),obj['slug'],obj.get('name'),effort,json.dumps(obj,ensure_ascii=False)))
print('Modelle:',len(best),'mit Index-Evaluierungen:',sum(bool(o.get('intelligenceIndexEvaluations')) for o in best))
