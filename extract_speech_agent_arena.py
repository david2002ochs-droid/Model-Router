#!/usr/bin/env python3
"""Extract public Speech-to-Speech Arena outcomes by task slice."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS speech_agent_arena_results(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,result_id TEXT NOT NULL,model_key TEXT,host_model_id TEXT,
 model_name TEXT NOT NULL,creator_id TEXT,creator_name TEXT,slice_key TEXT,elo REAL,elo_ci_low REAL,elo_ci_high REAL,
 appearances INTEGER,task_completion_rate REAL,task_completion_success_count INTEGER,task_completion_failure_count INTEGER,
 source_rank INTEGER,speech_quality_index REAL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,result_id))''')
url='https://artificialanalysis.ai/speech-to-speech/arena';row=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if not row:raise SystemExit('Arena-Seite nicht archiviert')
sha,blob=row;html=gzip.decompress(blob).decode('utf8',errors='replace');d=json.JSONDecoder();found={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
 s=json.loads(m.group(1))
 for hit in re.finditer(r'\{"id":',s):
  try:o,_=d.raw_decode(s,hit.start())
  except ValueError:continue
  if isinstance(o,dict) and o.get('id') and o.get('name') and 'stsQualityIndexV2Components' in o and 'sliceKey' in o:found[o['id']]=o
if len(found)<10:raise SystemExit('Zu wenige erwartete Arena-Ergebnisse; kein Import')
with c:
 c.execute('delete from speech_agent_arena_results where source_url=?',(url,))
 for id,o in found.items():
  c.execute('insert into speech_agent_arena_results values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
   url,sha,id,o.get('modelKey'),o.get('stsHostModelId'),o['name'],o.get('creatorId'),o.get('creatorName'),o.get('sliceKey'),
   o.get('elo'),o.get('lower95ci'),o.get('upper95ci'),o.get('appearances'),o.get('taskCompletionRate'),
   o.get('taskCompletionSuccessCount'),o.get('taskCompletionFailureCount'),o.get('rank'),o.get('stsQualityIndexV2Score'),json.dumps(o,ensure_ascii=False)))
print('Speech-Agent-Arena-Ergebnisse:',len(found))
