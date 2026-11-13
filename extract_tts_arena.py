#!/usr/bin/env python3
"""Normalize public text-to-speech Arena leaderboards."""
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS tts_arena_observations(
 source_url TEXT NOT NULL, source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 arena_variant TEXT NOT NULL,rank INTEGER,rank_range TEXT,model_name TEXT NOT NULL,elo REAL,elo_interval_low REAL,elo_interval_high REAL,
 sample_count INTEGER,arena_voices TEXT,released TEXT,price_usd_per_million_characters REAL,price_text TEXT,raw_cells_json TEXT NOT NULL,
 PRIMARY KEY(source_url,table_number,row_number))''')
N=0
for url,sha,tn,raw in c.execute("""select url,page_sha256,table_number,rows_json from extracted_tables
 where url in ('https://artificialanalysis.ai/text-to-speech/leaderboard/controlled-voice',
               'https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice')""").fetchall():
 rows=json.loads(raw)
 if not rows:continue
 headers=[x['text'] for x in rows[0]]
 variant=url.rsplit('/',1)[-1]
 if headers[:5]!=['','Range','Model','Elo','Samples'] or len(headers)!=(7 if variant=='controlled-voice' else 8):continue
 with c:
  c.execute('delete from tts_arena_observations where source_url=? and table_number=?',(url,tn))
  for i,row in enumerate(rows[1:],1):
   v=[x['text'] for x in row]
   if len(v)!=len(headers) or not v[2]:continue
   elo=re.fullmatch(r'([0-9]+)(?:±([0-9]+)95% interval ([0-9]+) to ([0-9]+))?',v[3])
   anchor=re.fullmatch(r'([0-9]+)AnchorFixed at 1000 as the reference point for this board.s Elo scale\.',v[3])
   pr=re.fullmatch(r'\$([0-9]+(?:\.[0-9]+)?)\s*/1M chars',v[-1])
   c.execute('insert into tts_arena_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
    url,sha,tn,i,variant,int(v[0]) if v[0].isdigit() else None,v[1] or None,v[2],float(elo[1]) if elo else (float(anchor[1]) if anchor else None),
    float(elo[3]) if elo and elo[3] else None,float(elo[4]) if elo and elo[4] else None,
    int(v[4].replace(',','')) if v[4].replace(',','').isdigit() else None,
    v[5] if variant=='provider-voice' else None,v[-2] or None,float(pr[1]) if pr else None,v[-1] or None,json.dumps(row,ensure_ascii=False)))
   N+=1
print('TTS-Arena-Zeilen:',N)
