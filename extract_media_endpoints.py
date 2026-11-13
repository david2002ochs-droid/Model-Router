#!/usr/bin/env python3
"""Extract multimodal hostModels arrays while retaining original objects and units."""
import datetime,gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.executescript('''CREATE TABLE IF NOT EXISTS media_endpoint_records(
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,modality TEXT NOT NULL,endpoint_id TEXT NOT NULL,endpoint_slug TEXT,endpoint_name TEXT,endpoint_classification TEXT,
 provider_id TEXT,provider_slug TEXT,provider_name TEXT,model_id TEXT,model_slug TEXT,model_name TEXT,
 price_per_1000_images_usd REAL,model_quality_elo REAL,model_quality_ci95_low REAL,model_quality_ci95_high REAL,
 median_generation_seconds REAL,p05_generation_seconds REAL,p25_generation_seconds REAL,p75_generation_seconds REAL,p95_generation_seconds REAL,
 is_representative INTEGER,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,endpoint_id));
 CREATE TABLE IF NOT EXISTS media_endpoint_extraction_log(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,record_count INTEGER NOT NULL,extracted_at_utc TEXT NOT NULL,error TEXT);
 CREATE VIEW IF NOT EXISTS media_endpoint_leaves AS SELECT e.source_url,e.page_sha256,e.modality,e.endpoint_id,e.provider_slug,e.model_slug,j.fullkey AS json_path,j.type AS value_type,j.atom AS value FROM media_endpoint_records e,json_tree(e.raw_json) j WHERE j.type IN ('integer','real','text','true','false','null');
 CREATE VIEW IF NOT EXISTS latest_media_endpoints AS SELECT * FROM (
 SELECT e.*,coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
 ROW_NUMBER() OVER (PARTITION BY e.modality,e.endpoint_id ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN p.sha256=e.page_sha256 THEN q.retrieved_at_utc END) DESC,e.source_url) source_rank
 FROM media_endpoint_records e LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=e.source_url AND t.page_sha256=e.page_sha256 LEFT JOIN crawl_queue q ON q.url=e.source_url LEFT JOIN page_archive p ON p.url=e.source_url
) WHERE source_rank=1;''')
for col,typ in [('video_price_usd_per_minute','REAL'),('tts_price_usd_per_million_chars','REAL'),('median_chars_per_second','REAL'),('latency_json','TEXT'),('time_percentiles_consistent','INTEGER'),('text_to_video_elo','REAL'),('image_to_video_elo','REAL')]:
 if col not in {r[1] for r in c.execute('pragma table_info(media_endpoint_records)')}:
  c.execute('alter table media_endpoint_records add column '+col+' '+typ)
pages=c.execute("""SELECT p.url,p.sha256,p.body_gzip FROM page_archive p LEFT JOIN media_endpoint_extraction_log l ON l.source_url=p.url WHERE (p.url LIKE 'https://artificialanalysis.ai/image/providers/%' OR p.url LIKE 'https://artificialanalysis.ai/video/providers/%' OR p.url LIKE 'https://artificialanalysis.ai/text-to-speech/providers/%') AND (l.page_sha256 IS NULL OR l.page_sha256<>p.sha256 OR l.error IS NOT NULL)""").fetchall();d=json.JSONDecoder();pat=re.compile(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)');keys=re.compile(r'"hostModels"\s*:\s*(?=\[)');total=0
for url,sha,blob in pages:
 try:
  html=gzip.decompress(blob).decode('utf8',errors='replace');records={};modality=url.split('/')[3]
  for m in pat.finditer(html):
   s=json.loads(m.group(1))
   for hit in keys.finditer(s):
    try:arr,_=d.raw_decode(s,hit.end())
    except ValueError:continue
    if not isinstance(arr,list):continue
    for o in arr:
     if not isinstance(o,dict) or not o.get('id') or not isinstance(o.get('model'),dict) or not isinstance(o.get('host'),dict):continue
     model=o['model'];host=o['host'];perf=o.get('performance') or {};perf=perf if isinstance(perf,dict) else {}
     def num(v):return v if isinstance(v,(int,float)) and not isinstance(v,bool) else None
     def boolean(v):return int(v) if isinstance(v,bool) else None
     values=(url,sha,modality,str(o['id']),o.get('slug'),o.get('name'),o.get('endpointClassification'),host.get('id'),host.get('slug'),host.get('name'),model.get('id'),model.get('slug'),model.get('name'),num(o.get('pricePer1kImages')),num(model.get('qualityElo')),num(model.get('qualityEloCi95Lower')),num(model.get('qualityEloCi95Upper')),num(perf.get('medianGenerationTimeSeconds')),num(perf.get('percentile05GenerationTimeSeconds')),num(perf.get('quartile25GenerationTimeSeconds')),num(perf.get('quartile75GenerationTimeSeconds')),num(perf.get('percentile95GenerationTimeSeconds')),boolean(o.get('isRepresentative')),json.dumps(o,ensure_ascii=False,separators=(',',':')),
             num(o.get('pricePerMinute')),num(o.get('pricePer1mCharacters')),num(perf.get('medianCharactersPerSecond')),
             json.dumps(o.get('latencyPerformance'),ensure_ascii=False) if isinstance(o.get('latencyPerformance'),dict) else None,
             int(perf['percentile05GenerationTimeSeconds']<=perf['medianGenerationTimeSeconds']<=perf['percentile95GenerationTimeSeconds']) if all(num(perf.get(k)) is not None for k in ('percentile05GenerationTimeSeconds','medianGenerationTimeSeconds','percentile95GenerationTimeSeconds')) else None,
             num(model.get('textToVideoElo')),num(model.get('imageToVideoElo')))
     records[str(o['id'])]=values
  with c:
   c.execute('delete from media_endpoint_records where source_url=?',(url,));c.executemany('insert into media_endpoint_records values('+','.join('?'*31)+')',records.values());c.execute('insert or replace into media_endpoint_extraction_log values(?,?,?,?,NULL)',(url,sha,len(records),datetime.datetime.now(datetime.timezone.utc).isoformat()))
  total+=len(records)
 except Exception as e:
  with c:c.execute('insert or replace into media_endpoint_extraction_log values(?,?,0,?,?)',(url,sha,datetime.datetime.now(datetime.timezone.utc).isoformat(),str(e)[:500]))
print(f'{len(pages)} Medien-Providerseiten, {total} quellenbezogene Endpunkte')
