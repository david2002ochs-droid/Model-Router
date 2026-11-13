#!/usr/bin/env python3
"""Reproduce public evaluation cost/task computation with cache and per-evaluation fallback rates."""
import gzip,json,re,sqlite3,hashlib,datetime
from pathlib import Path
P=Path(__file__).resolve().parent;c=sqlite3.connect(P/'artificial_analysis.sqlite3',timeout=60)
c.executescript('''CREATE TABLE IF NOT EXISTS evaluation_price_fallbacks(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,raw_json TEXT NOT NULL,PRIMARY KEY(source_url,model_id));
CREATE TABLE IF NOT EXISTS benchmark_cost_estimates(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,model_id TEXT NOT NULL,model_slug TEXT,model_name TEXT,effort TEXT,
 benchmark_slug TEXT NOT NULL,token_field TEXT NOT NULL,task_count REAL NOT NULL,cost_usd_per_task REAL,
 noncache_input_cost_usd_per_task REAL,cache_read_cost_usd_per_task REAL,cache_write_cost_usd_per_task REAL,
 reasoning_cost_usd_per_task REAL,answer_cost_usd_per_task REAL,fallback_applied INTEGER NOT NULL,
 registry_source_sha256 TEXT NOT NULL,formula_source_sha256 TEXT NOT NULL,formula_helper_sha256 TEXT NOT NULL,
 PRIMARY KEY(source_url,model_id,benchmark_slug));''')
helper_url='https://artificialanalysis.ai/_next/static/chunks/49650-4e98dcf773a5b2be.js'
helper_row=c.execute('select sha256 from benchmark_calculation_sources where source_url=? order by retrieved_at_utc desc limit 1',(helper_url,)).fetchone()
if helper_row is None:raise SystemExit('Archivierte Berechnungs-Quelldatei fehlt; kein Kostenimport')
helper_sha=helper_row[0];formula_sha='1e955781826f7a5d8fcca0778c4fe506f1d7cee87b2618b358a277b6b6c97052'
pages=c.execute("select p.url,p.sha256,p.body_gzip from page_archive p join benchmark_time_config t on p.url='https://artificialanalysis.ai/evaluations/'||t.benchmark_slug").fetchall();d=json.JSONDecoder();fallbacks={}
for url,sha,blob in pages:
 html=gzip.decompress(blob).decode('utf8',errors='replace');best={}
 for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
  s=json.loads(m.group(1))
  for z in re.finditer(r'"priceFallbackByModelId"\s*:\s*(?=\{)',s):
   try:o,_=d.raw_decode(s,z.end())
   except ValueError:continue
   if isinstance(o,dict) and len(o)>len(best):best=o
 fallbacks[url]=(sha,best)
with c:
 for url,(sha,objs) in fallbacks.items():
  c.execute('delete from evaluation_price_fallbacks where source_url=?',(url,))
  for mid,obj in objs.items():c.execute('insert into evaluation_price_fallbacks values(?,?,?,?)',(url,sha,mid,json.dumps(obj,ensure_ascii=False)))
def cost_components(tokens,cache_rate,prices):
 need=['input','answer','reasoning']
 if not all(isinstance(tokens.get(k),(int,float)) for k in need):return None
 if not all(isinstance(prices.get(k),(int,float)) for k in ('input','output')):return None
 inp=tokens['input'];cached=tokens.get('cacheableInput')
 if cached is None:noncache,read,write=inp,0,0
 else:
  if not isinstance(cached,(int,float)) or not isinstance(cache_rate,(int,float)) or cached>inp:return None
  read=cached*cache_rate;write=inp-read;noncache=0
 inpprice=prices['input'];outprice=prices['output'];hit=prices.get('cacheHit');writeprice=prices.get('cacheWrite')
 return [noncache*inpprice/1e6,read*(inpprice if hit is None else hit)/1e6,write*(inpprice if writeprice is None else writeprice)/1e6,tokens['reasoning']*outprice/1e6,tokens['answer']*outprice/1e6]
records=[];skips=0
for url,sha,mid,slug,name,effort,raw,bench,tokfield,tasks,regsha in c.execute('''select e.source_url,e.page_sha256,e.model_id,e.model_slug,e.model_name,e.effort,e.model_json,t.benchmark_slug,t.token_field,t.task_count,t.registry_source_sha256
from evaluation_page_models e join benchmark_time_config t on e.source_url='https://artificialanalysis.ai/evaluations/'||t.benchmark_slug''').fetchall():
 o=json.loads(raw);tokens=(o.get('canonicalEvalTokenCounts') or {}).get(tokfield);prices={'input':o.get('price1mInputTokens'),'output':o.get('price1mOutputTokens'),'cacheHit':o.get('cacheHitPrice'),'cacheWrite':o.get('cacheWritePrice')}
 primary=cost_components(tokens or {},o.get('cacheHitRate'),prices)
 if primary is None:skips+=1;continue
 fallback=(fallbacks.get(url,('',{}))[1].get(mid) or {});rate=(fallback.get('rateByEval') or {}).get(bench);applied=0
 if rate is not None:
  other=cost_components(tokens or {},o.get('cacheHitRate'),fallback.get('fallbackPrice') or {})
  if other is None or not all(isinstance(rate.get(k),(int,float)) for k in ('input','reasoning','output')):skips+=1;continue
  rr=[rate['input']]*3+[rate['reasoning'],rate['output']];primary=[a*(1-r)+b*r for a,b,r in zip(primary,other,rr)];applied=1
 parts=[x/tasks for x in primary];records.append((url,sha,mid,slug,name,effort,bench,tokfield,tasks,sum(parts),*parts,applied,regsha,formula_sha,helper_sha))
with c:
 c.execute('delete from benchmark_cost_estimates');c.executemany('insert into benchmark_cost_estimates values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',records)
print('Kostenzeilen:',len(records),'nicht berechenbar:',skips,'Fallback-Modelle:',sum(r[15] for r in records))
