#!/usr/bin/env python3
"""Extract source-hosted speech benchmark scores and per-task costs."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS speech_agent_host_details(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,host_model_name TEXT,host_model_slug TEXT,
 host_id TEXT,host_name TEXT,model_id TEXT,model_name TEXT,model_slug TEXT,
 speech_index REAL,big_bench_audio_score_raw REAL,conversational_dynamics_score_raw REAL,tau3_voice_score_raw REAL,
 first_audio_seconds REAL,big_bench_audio_average_cost_per_task_usd REAL,big_bench_audio_cost_per_input_hour_usd REAL,
 input_audio_price_usd_per_hour REAL,output_audio_price_usd_per_hour REAL,tau3_voice_mean_audio_duration_seconds REAL,
 source_series_json TEXT NOT NULL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,host_model_id))''')
url='https://artificialanalysis.ai/speech-to-speech';row=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if not row:raise SystemExit('Speech-to-speech-Seite nicht archiviert')
sha,blob=row;html=gzip.decompress(blob).decode('utf8',errors='replace');d=json.JSONDecoder();found={};series={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
 s=json.loads(m.group(1))
 for hit in re.finditer(r'"([A-Za-z]+HostModels)"\s*:\s*(?=\[)',s):
  try:a,_=d.raw_decode(s,hit.end())
  except ValueError:continue
  if not isinstance(a,list):continue
  for o in a:
   if not isinstance(o,dict) or not o.get('id') or not isinstance(o.get('model'),dict) or not isinstance(o.get('host'),dict) or 'averageCostPerTask' not in o:continue
   id=str(o['id'])
   if id in found and o!=found[id]:raise SystemExit('Widersprüchliche Daten für Host-Modell '+id+'; kein Import')
   found[id]=o;series.setdefault(id,set()).add(hit.group(1))
if len(found)<10:raise SystemExit('Zu wenige erwartete Host-Modelle; kein Import')
with c:
 c.execute('delete from speech_agent_host_details where source_url=?',(url,))
 for id,o in found.items():
  host=o['host'];model=o['model']
  c.execute('insert into speech_agent_host_details values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
   url,sha,id,o.get('name'),o.get('slug'),host.get('id'),host.get('name'),model.get('id'),model.get('name'),model.get('slug'),
   o.get('stsQualityIndex'),o.get('bbaScore'),o.get('fdbScore'),o.get('tauVoiceAggScore'),o.get('timeToFirstAudioSeconds'),
   o.get('averageCostPerTask'),o.get('costPerHourOfInputAudio'),o.get('pricePerHourInput'),o.get('pricePerHourOutput'),o.get('tauVoiceMeanAudioDurationSeconds'),
   json.dumps(sorted(series[id])),json.dumps(o,ensure_ascii=False)))
print('Speech-Host-Modelle:',len(found))
