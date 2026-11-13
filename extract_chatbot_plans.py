#!/usr/bin/env python3
"""Extract clearly labelled chatbot subscription plans, never price per API task."""
import gzip,json,re,sqlite3
from pathlib import Path
URL='https://artificialanalysis.ai/agents/chatbots'
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS chatbot_plan_observations(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,plan_id TEXT NOT NULL,plan_name TEXT NOT NULL,creator_name TEXT,product_slug TEXT,tier TEXT,monthly_price_usd REAL,monthly_price_notes TEXT,model_slug TEXT,model_name TEXT,model_notes TEXT,intelligence_index REAL,feature_score REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,plan_id))''')
row=c.execute('select sha256,body_gzip from page_archive where url=?',(URL,)).fetchone()
if not row:raise SystemExit('Chatbot-Liste fehlt im Archiv')
sha,blob=row;h=gzip.decompress(blob).decode('utf8',errors='replace');decoder=json.JSONDecoder();best={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',h):
 s=json.loads(m.group(1))
 for x in re.finditer(r'"chatbots"\s*:\s*(?=\[)',s):
  try:arr,_=decoder.raw_decode(s,x.end())
  except ValueError:continue
  if not isinstance(arr,list):continue
  for o in arr:
   if isinstance(o,dict) and o.get('id') and o.get('name') and 'priceMonthly' in o:best[str(o['id'])]=o
if len(best)<5:raise SystemExit('Keine belastbare Abonnementliste; Import abgebrochen')
def num(v):return v if isinstance(v,(int,float)) and not isinstance(v,bool) else None
with c:
 c.execute('delete from chatbot_plan_observations where source_url=?',(URL,))
 for id,o in best.items():c.execute('insert into chatbot_plan_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(URL,sha,id,o['name'],o.get('creatorName'),o.get('slug'),o.get('tier'),num(o.get('priceMonthly')),o.get('priceMonthlyNotes'),o.get('modelSlug'),o.get('modelName'),o.get('modelNotes'),num(o.get('intelligenceIndex')),num(o.get('featuresScore')),json.dumps(o,ensure_ascii=False,separators=(',',':'))))
print('Chatbot-Abonnements:',len(best))
