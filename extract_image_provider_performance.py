#!/usr/bin/env python3
"""Extract hosted image-model pricing and generation-time distributions."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS image_host_model_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,host_model_id TEXT NOT NULL,host_model_name TEXT,host_model_slug TEXT,
 host_id TEXT,host_name TEXT,host_slug TEXT,model_id TEXT,model_name TEXT,model_slug TEXT,creator_id TEXT,creator_name TEXT,
 price_usd_per_1000_images REAL,endpoint_classification TEXT,quality_elo REAL,quality_elo_ci_low REAL,quality_elo_ci_high REAL,
 median_generation_seconds REAL,p05_generation_seconds REAL,p25_generation_seconds REAL,p75_generation_seconds REAL,p95_generation_seconds REAL,
 raw_json TEXT NOT NULL,PRIMARY KEY(source_url,host_model_id))''')
dec=json.JSONDecoder();total=0
for url,sha,blob in c.execute("select url,sha256,body_gzip from page_archive where url like '%/image/providers/%'").fetchall():
 html=gzip.decompress(blob).decode('utf8',errors='replace');best={}
 for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
  payload=json.loads(m.group(1))
  for hit in re.finditer(r'"hostModels"\s*:\s*(?=\[)',payload):
   try:arr,_=dec.raw_decode(payload,hit.end())
   except ValueError:continue
   if not isinstance(arr,list):continue
   objs={str(o['id']):o for o in arr if isinstance(o,dict) and o.get('id') and 'pricePer1kImages' in o and isinstance(o.get('model'),dict) and isinstance(o.get('host'),dict)}
   if len(objs)>len(best):best=objs
 if not best:print('keine Host-Modellliste',url);continue
 with c:
  c.execute('delete from image_host_model_observations where source_url=?',(url,))
  for id,o in best.items():
   host=o['host'];model=o['model'];creator=model.get('creator') or {};perf=o.get('performance') or {}
   c.execute('insert into image_host_model_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
    url,sha,id,o.get('name'),o.get('slug'),host.get('id'),host.get('name'),host.get('slug'),model.get('id'),model.get('name'),model.get('slug'),creator.get('id'),creator.get('name'),
    o.get('pricePer1kImages'),o.get('endpointClassification'),model.get('qualityElo'),model.get('qualityEloCi95Lower'),model.get('qualityEloCi95Upper'),
    perf.get('medianGenerationTimeSeconds'),perf.get('percentile05GenerationTimeSeconds'),perf.get('quartile25GenerationTimeSeconds'),perf.get('quartile75GenerationTimeSeconds'),perf.get('percentile95GenerationTimeSeconds'),json.dumps(o,ensure_ascii=False)))
 total+=len(best);print(url,len(best))
print('Host-Modellquellzeilen',total)
