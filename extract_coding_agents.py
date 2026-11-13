#!/usr/bin/env python3
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.executescript('''CREATE TABLE IF NOT EXISTS coding_agent_runs(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,run_id TEXT NOT NULL,agent_name TEXT,agent_slug TEXT,model_name TEXT,effort TEXT,run_json TEXT NOT NULL,PRIMARY KEY(source_url,run_id)); CREATE TABLE IF NOT EXISTS coding_agent_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,run_count INTEGER NOT NULL,error TEXT);''')
pages=c.execute("select p.url,p.sha256,p.body_gzip from page_archive p left join coding_agent_extraction_log l on l.source_url=p.url where (p.url like '%/agents/coding-agents/%' or p.url='https://artificialanalysis.ai/agents/coding-agents') and (l.page_sha256 is null or l.page_sha256<>p.sha256)").fetchall();decoder=json.JSONDecoder();count=0
for url,sha,blob in pages:
 try:
  html=gzip.decompress(blob).decode('utf8',errors='replace');best={}
  for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
   payload=json.loads(m.group(1))
   for hit in re.finditer(r'"(?:benchmarkRows|rows)"\s*:\s*(?=\[)',payload):
    try:arr,_=decoder.raw_decode(payload,hit.end())
    except ValueError:continue
    if isinstance(arr,list):
     for obj in arr:
      if isinstance(obj,dict) and obj.get('id') and 'evals' in obj:best[str(obj['id'])]=obj
  with c:
   c.execute('delete from coding_agent_runs where source_url=?',(url,))
   for id,obj in best.items():
    model=obj.get('model') or {};eff=model.get('effort') or {};eff=eff.get('slug') if isinstance(eff,dict) else None
    c.execute('insert into coding_agent_runs values(?,?,?,?,?,?,?,?)',(url,sha,id,obj.get('agentName'),obj.get('agentSlug'),model.get('name'),eff,json.dumps(obj,ensure_ascii=False)))
   c.execute('insert or replace into coding_agent_extraction_log values(?,?,?,NULL)',(url,sha,len(best)))
  count+=len(best)
 except Exception as e:
  with c:c.execute('insert or replace into coding_agent_extraction_log values(?,?,0,?)',(url,sha,str(e)[:500]))
print(len(pages),'Seiten,',count,'Agentenkonfigurationen mit Quellen')
