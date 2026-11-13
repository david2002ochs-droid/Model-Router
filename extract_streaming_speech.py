#!/usr/bin/env python3
"""Extract public speech-to-text streaming host/model observations."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS streaming_speech_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,
 name TEXT,host_id TEXT,host_name TEXT,model_id TEXT,model_name TEXT,price_per_1000_minutes REAL,
 aa_wer_streaming_index REAL,aa_agenttalk_streaming_wer REAL,voxpopuli_streaming_wer REAL,
 earnings22_streaming_wer REAL,time_to_final_transcript_seconds REAL,time_to_first_partial_transcript_seconds REAL,
 raw_json TEXT NOT NULL, PRIMARY KEY(source_url,host_model_id))''')
url='https://artificialanalysis.ai/speech-to-text/streaming';row=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if not row:raise SystemExit('Streaming-Seite nicht archiviert')
sha,blob=row;html=gzip.decompress(blob).decode('utf8',errors='replace');decoder=json.JSONDecoder();best=[]
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
 payload=json.loads(m.group(1))
 for hit in re.finditer(r'"hostModels"\s*:\s*(?=\[)',payload):
  try:arr,_=decoder.raw_decode(payload,hit.end())
  except ValueError:continue
  if isinstance(arr,list):
   objs=[o for o in arr if isinstance(o,dict) and o.get('id') and 'aaWerStreamingIndex' in o]
   if len(objs)>len(best):best=objs
if len(best)<5:raise SystemExit('Keine erwartete Streaming-Modellliste gefunden')
with c:
 c.execute('delete from streaming_speech_observations where source_url=?',(url,))
 for obj in best:
  host=obj.get('host') or {};model=obj.get('model') or {}
  c.execute('insert into streaming_speech_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
   url,sha,obj['id'],obj.get('displayName') or obj.get('name'),host.get('id'),host.get('name'),model.get('id'),model.get('name'),
   obj.get('pricePer1kMinutes'),obj.get('aaWerStreamingIndex'),obj.get('aaAgenttalkStreamingWer'),obj.get('voxpopuliStreamingWer'),
   obj.get('earnings22StreamingWer'),obj.get('timeToFinalTranscriptSeconds'),obj.get('timeToFirstPartialTranscriptSeconds'),json.dumps(obj,ensure_ascii=False)))
print('Streaming Host-Modell-Varianten:',len(best))
