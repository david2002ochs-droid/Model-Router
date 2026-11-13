#!/usr/bin/env python3
"""Preserve visible open-weights Arena ranking rows without inferring model IDs."""
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS media_arena_openweights_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 media_type TEXT NOT NULL,arena_task TEXT NOT NULL,rank INTEGER,rank_range TEXT,model_name TEXT NOT NULL,
 elo_displayed REAL,ci_lower_displayed REAL,ci_upper_displayed REAL,sample_count INTEGER,released TEXT,
 price_text TEXT,price_usd_per_1000_images REAL,price_usd_per_video_minute REAL,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number))''')
total=0
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where (url like '%/image/leaderboard/%/open-weights' or url like '%/video/leaderboard/%/open-weights') and table_number=0").fetchall():
 rows=json.loads(raw)
 if not rows or [x['text'] for x in rows[0]][:5]!=['','Range','Model','Elo','Samples']:continue
 media='image' if '/image/' in url else 'video';task=url.split('/leaderboard/',1)[1].split('/open-weights',1)[0];n=0
 with c:
  c.execute('delete from media_arena_openweights_observations where source_url=? and table_number=?',(url,tn))
  for i,row in enumerate(rows[1:],1):
   v=[x['text'] for x in row]
   if len(v)!=7 or not v[2]:continue
   elo=re.fullmatch(r'([0-9]+)(?:±([0-9]+)95% interval ([0-9]+) to ([0-9]+))?',v[3]);anchor=re.fullmatch(r'([0-9]+)AnchorFixed at 1000 as the reference point for this board.s Elo scale\.',v[3]);price=re.fullmatch(r'\$([0-9]+(?:\.[0-9]+)?)\s*/(1k imgs|min)',v[6])
   c.execute('insert into media_arena_openweights_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
    url,sha,tn,i,media,task,int(v[0]) if v[0].isdigit() else None,v[1] or None,v[2],float(elo[1]) if elo else (float(anchor[1]) if anchor else None),
    float(elo[3]) if elo and elo[3] else None,float(elo[4]) if elo and elo[4] else None,int(v[4].replace(',','')) if v[4].replace(',','').isdigit() else None,
    v[5] or None,v[6] or None,float(price[1]) if price and price[2]=='1k imgs' else None,float(price[1]) if price and price[2]=='min' else None,json.dumps(row,ensure_ascii=False)))
   n+=1
 print(url,n);total+=n
print('Open-Weights-Zeilen',total)
