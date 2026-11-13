#!/usr/bin/env python3
"""Preserve visible image, video and speech arena leaderboards and exact units."""
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS media_leaderboard_observations(
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 modality TEXT NOT NULL,benchmark_slug TEXT NOT NULL,open_weights_filter INTEGER NOT NULL,rank INTEGER,rank_range TEXT,
 model_name TEXT NOT NULL,model_links_json TEXT NOT NULL,elo REAL,elo_ci95_low REAL,elo_ci95_high REAL,elo_raw TEXT,
 samples INTEGER,arena_voices TEXT,released TEXT,price_usd REAL,price_unit TEXT,price_raw TEXT,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number))''')
rows=c.execute("""select url,page_sha256,table_number,rows_json from extracted_tables
where (url like 'https://artificialanalysis.ai/image/leaderboard/%' or url like 'https://artificialanalysis.ai/video/leaderboard/%' or url like 'https://artificialanalysis.ai/text-to-speech/leaderboard/%')""").fetchall();N=0
for url,sha,tn,raw in rows:
 data=json.loads(raw); headers=[x['text'] for x in data[0]] if data else []
 if 'Model' not in headers or 'Elo' not in headers or 'Samples' not in headers:continue
 def col(name):return headers.index(name) if name in headers else None
 pi=next((i for i,h in enumerate(headers) if h.startswith('Pricing')),None)
 parts=url.split('/');modality=parts[3];benchmark=parts[5];openweights=int('open-weights' in parts[6:])
 with c:
  c.execute('delete from media_leaderboard_observations where source_url=? and table_number=?',(url,tn))
  for i,r in enumerate(data[1:],1):
   vals=[x['text'] for x in r]
   def val(index):return vals[index] if index is not None and index<len(vals) else ''
   model=val(col('Model'))
   if not model:continue
   elotext=val(col('Elo'));e=re.match(r'^\s*(-?\d+(?:\.\d+)?)',elotext);ci=re.search(r'95%\s*interval\s*(-?\d+(?:\.\d+)?)\s*to\s*(-?\d+(?:\.\d+)?)',elotext,re.I)
   price=val(pi);m=re.search(r'\$\s*([\d,]+(?:\.\d+)?)\s*/\s*(.+)',price)
   sample=val(col('Samples')).replace(',','');rank=val(0).replace(',','')
   c.execute('insert into media_leaderboard_observations values('+','.join('?'*22)+')',(url,sha,tn,i,modality,benchmark,openweights,int(rank) if rank.isdigit() else None,val(col('Range')) or None,model,json.dumps(r[col('Model')].get('links',[]),ensure_ascii=False),float(e.group(1)) if e else None,float(ci.group(1)) if ci else None,float(ci.group(2)) if ci else None,elotext or None,int(sample) if sample.isdigit() else None,val(col('Arena Voices')) or None,val(col('Released')) or None,float(m.group(1).replace(',','')) if m else None,m.group(2).strip() if m else None,price or None,json.dumps(r,ensure_ascii=False)))
   N+=1
print('Medien-Ranglisten-Zeilen:',N)
