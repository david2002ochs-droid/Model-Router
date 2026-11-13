#!/usr/bin/env python3
"""Extract per-provider endpoint prices and performance from archived page payloads.

Source arrays are kept separate: hostModels (detail) and rows (display table).
Missing and unpublished values remain NULL. Raw JSON and page hash retained.
"""
import datetime,gzip,json,re,sqlite3
from pathlib import Path
P=Path(__file__).resolve().parent
c=sqlite3.connect(P/'artificial_analysis.sqlite3',timeout=60)
c.executescript('''CREATE TABLE IF NOT EXISTS provider_endpoint_records (
 source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,array_kind TEXT NOT NULL,endpoint_id TEXT NOT NULL,
 endpoint_slug TEXT,host_id TEXT,host_slug TEXT,host_name TEXT,model_id TEXT,model_slug TEXT,model_name TEXT,
 price_1m_input_usd REAL,price_1m_output_usd REAL,cache_hit_usd_per_1m REAL,cache_write_usd_per_1m REAL,
 cost_per_task_usd REAL,index_time_per_task_seconds REAL,output_tokens_per_second REAL,
 first_answer_token_seconds REAL,first_token_seconds REAL,error_rate_fraction REAL,context_window_tokens INTEGER,
 function_calling INTEGER,json_mode INTEGER,raw_json TEXT NOT NULL,
 PRIMARY KEY(source_url,array_kind,endpoint_id));
CREATE TABLE IF NOT EXISTS provider_endpoint_extraction_log (
 source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,record_count INTEGER NOT NULL,extracted_at_utc TEXT NOT NULL,error TEXT);
CREATE VIEW IF NOT EXISTS latest_provider_endpoints AS
SELECT * FROM (SELECT p.*,coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END) retrieved_at_utc,
ROW_NUMBER() OVER (PARTITION BY p.endpoint_id,p.array_kind ORDER BY coalesce(t.retrieved_at_utc,CASE WHEN a.sha256=p.page_sha256 THEN q.retrieved_at_utc END) DESC,p.source_url) AS source_rank
FROM provider_endpoint_records p LEFT JOIN (SELECT source_url,page_sha256,max(retrieved_at_utc) retrieved_at_utc FROM page_capture_events GROUP BY source_url,page_sha256) t ON t.source_url=p.source_url AND t.page_sha256=p.page_sha256 LEFT JOIN crawl_queue q ON q.url=p.source_url LEFT JOIN page_archive a ON a.url=p.source_url) WHERE source_rank=1;
''')
pages=c.execute("""SELECT p.url,p.sha256,p.body_gzip FROM page_archive p
 LEFT JOIN provider_endpoint_extraction_log l ON l.source_url=p.url
 WHERE (p.url LIKE 'https://artificialanalysis.ai/providers/%' OR p.url LIKE 'https://artificialanalysis.ai/models/%/providers%')
 AND (l.page_sha256 IS NULL OR l.page_sha256<>p.sha256 OR l.error IS NOT NULL)""").fetchall()
pat=re.compile(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)')
keys=re.compile(r'"(hostModels|rows)"\s*:\s*(?=\[)');decoder=json.JSONDecoder(); total=0
for url,sha,blob in pages:
 try:
  raw=gzip.decompress(blob).decode('utf8',errors='replace');records={}
  host_from_url=url.split('/providers/',1)[1].split('/',1)[0] if '/providers/' in url and '/models/' not in url else None
  for match in pat.finditer(raw):
   payload=json.loads(match.group(1))
   for hit in keys.finditer(payload):
    try: arr,_=decoder.raw_decode(payload,hit.end())
    except ValueError:continue
    if not isinstance(arr,list):continue
    for o in arr:
     if not isinstance(o,dict) or not o.get('id') or not isinstance(o.get('pricing'),dict):continue
     model=o.get('model');host=o.get('host') or {}
     if not isinstance(model,dict) or not model.get('slug'):continue
     if not isinstance(host,dict):host={}
     if not (host.get('slug') or o.get('hostId') or host_from_url):continue
     pricing=o['pricing'];perf=o.get('performance') or o.get('headline') or {};features=o.get('features') or {}
     if not isinstance(perf,dict):perf={}
     if not isinstance(features,dict):features={}
     cost=o.get('intelligenceIndexCostPerTask');cost=cost.get('total') if isinstance(cost,dict) else pricing.get('costPerTask')
     def boolean(v):return int(v) if isinstance(v,bool) else None
     def numeric(v):return v if isinstance(v,(int,float)) and not isinstance(v,bool) else None
     record=(url,sha,hit.group(1),str(o['id']),o.get('slug'),o.get('hostId'),host.get('slug') or host_from_url,host.get('name'),
             model.get('id'),model.get('slug'),model.get('name') or o.get('label'),
             numeric(pricing.get('price1mInputTokens')),numeric(pricing.get('price1mOutputTokens')),numeric(pricing.get('cacheHitPrice')),numeric(pricing.get('cacheWritePrice')),
             numeric(cost),numeric(o.get('intelligenceIndexTimePerTask',perf.get('intelligenceIndexTimePerTask'))),numeric(perf.get('outputSpeed')),numeric(perf.get('timeToFirstAnswerToken')),
             numeric(perf.get('timeToFirstToken')),numeric(perf.get('endpointErrorRate')),numeric(o.get('contextWindowTokens',features.get('contextWindowTokens'))),
             boolean(o.get('functionCalling',features.get('functionCalling'))),boolean(o.get('jsonMode',features.get('jsonMode'))),json.dumps(o,ensure_ascii=False,separators=(',',':')))
     records[(hit.group(1),str(o['id']))]=record
  with c:
   c.execute('DELETE FROM provider_endpoint_records WHERE source_url=?',(url,))
   c.executemany('INSERT INTO provider_endpoint_records VALUES('+','.join('?'*25)+')',records.values())
   c.execute('INSERT OR REPLACE INTO provider_endpoint_extraction_log VALUES(?,?,?,?,NULL)',(url,sha,len(records),datetime.datetime.now(datetime.timezone.utc).isoformat()))
  total+=len(records)
 except Exception as e:
  with c:c.execute('INSERT OR REPLACE INTO provider_endpoint_extraction_log VALUES(?,?,?,?,?)',(url,sha,0,datetime.datetime.now(datetime.timezone.utc).isoformat(),str(e)[:500]))
print(f'{len(pages)} Seiten geprüft; {total} quellenbezogene Endpunktobjekte gespeichert')
