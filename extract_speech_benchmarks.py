#!/usr/bin/env python3
"""Extract visible speech benchmark tables with source hash and raw cells."""
import json,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.executescript('''CREATE TABLE IF NOT EXISTS speech_to_speech_observations(source_url TEXT,source_sha256 TEXT,table_number INTEGER,row_number INTEGER,provider TEXT,model TEXT,speech_to_speech_index REAL,speech_reasoning_pct REAL,conversational_dynamics_pct REAL,agentic_performance_pct REAL,arena_preference_elo REAL,task_success_pct REAL,first_audio_seconds REAL,cost_per_hour_input_audio_usd REAL,input_audio_price_usd_per_hour REAL,output_audio_price_usd_per_hour REAL,raw_cells_json TEXT,PRIMARY KEY(source_url,table_number,row_number));
CREATE TABLE IF NOT EXISTS speech_to_text_observations(source_url TEXT,source_sha256 TEXT,table_number INTEGER,row_number INTEGER,model TEXT,provider TEXT,whisper_version TEXT,word_error_rate_pct REAL,median_speed_factor REAL,price_usd_per_1000_minutes REAL,raw_cells_json TEXT,PRIMARY KEY(source_url,table_number,row_number));''')
def num(s):
 try:return float(s.replace('$','').replace('%','').replace(',','').strip())
 except (ValueError,AttributeError):return None
stats={'speech_to_speech_observations':0,'speech_to_text_observations':0}
for url,sha,tn,raw in c.execute("select url,page_sha256,table_number,rows_json from extracted_tables where url in ('https://artificialanalysis.ai/speech-to-speech','https://artificialanalysis.ai/speech-to-text/non-streaming')").fetchall():
 rows=json.loads(raw)
 for i,row in enumerate(rows):
  h=[v['text'] for v in row]
  if len(h)==12 and h[:3]==['Provider','Model','Speech to Speech Index']:
   table='speech_to_speech_observations';size=12
  elif len(h)==7 and h[:3]==['Model','Provider','Whisper Version'] and 'Word Error Rate' in h[3]:
   table='speech_to_text_observations';size=7
  else:continue
  with c:
   c.execute('delete from '+table+' where source_url=? and table_number=?',(url,tn))
   for j,items in enumerate(rows[i+1:],1):
    v=[x['text'] for x in items]
    if len(v)!=size or not v[0] or not v[1]:continue
    if size==12:values=(url,sha,tn,j,v[0],v[1],*[num(x) for x in v[2:]],json.dumps(items,ensure_ascii=False));marks=','.join('?' for _ in values)
    else:values=(url,sha,tn,j,v[0],v[1],v[2] or None,num(v[3]),num(v[4]),num(v[5]),json.dumps(items,ensure_ascii=False));marks=','.join('?' for _ in values)
    c.execute('insert into '+table+' values('+marks+')',values);stats[table]+=1
  break
print('Zeilen:',stats)
