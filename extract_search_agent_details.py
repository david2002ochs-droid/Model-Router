#!/usr/bin/env python3
"""Extract public Search Index configuration-level statistics, preserving source data."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS search_agent_details(
 source_url TEXT NOT NULL, source_sha256 TEXT NOT NULL, configuration_id TEXT NOT NULL,
 provider_key TEXT, provider_name TEXT,provider_family_slug TEXT, provider_variant TEXT,
 answer_model_slug TEXT, answer_model_name TEXT,
 quality_index_raw REAL, browsecomp_accuracy_raw REAL, deepsearchqa_f1_raw REAL, omniscience_accuracy_raw REAL, baseline_lift_raw REAL,
 average_task_seconds REAL, search_time_per_task_seconds REAL, candidate_model_time_seconds_derived REAL,search_query_latency_seconds REAL,
 candidate_model_cost_usd_per_task REAL, search_api_cost_usd_per_task REAL, cost_usd_per_search_query REAL,
 search_queries_per_task REAL,input_tokens_per_task REAL, reasoning_tokens_per_task REAL,answer_tokens_per_task REAL,
 benchmark_count INTEGER, latest_measured_at TEXT,raw_json TEXT NOT NULL, PRIMARY KEY(source_url,configuration_id))''')
url='https://artificialanalysis.ai/agents/search-api';row=c.execute('select sha256,body_gzip from page_archive where url=?',(url,)).fetchone()
if row is None:raise SystemExit('Search-API-Seite nicht archiviert')
sha,blob=row;html=gzip.decompress(blob).decode('utf8',errors='replace');d=json.JSONDecoder();found={}
for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
 s=json.loads(m.group(1))
 for hit in re.finditer(r'\{"id":',s):
  try:o,_=d.raw_decode(s,hit.start())
  except ValueError:continue
  if isinstance(o,dict) and o.get('id') and o.get('providerKey') and 'candidateModelCostPerTaskUsd' in o and 'searchQueriesPerTask' in o:found[o['id']]=o
if len(found)<5:raise SystemExit('Zu wenige erwartete Suchkonfigurationen; keine Daten ersetzt')
with c:
 c.execute('delete from search_agent_details where source_url=?',(url,))
 for id,o in found.items():
  c.execute('insert into search_agent_details values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
   url,sha,id,o.get('providerKey'),o.get('providerName'),o.get('providerFamilySlug'),o.get('providerVariant'),o.get('answerModelSlug'),o.get('answerModelName'),
   o.get('aaSearchQualityIndex'),o.get('browsecompAccuracy'),o.get('deepsearchqaAvgF1'),o.get('omniscienceAccuracy'),o.get('qualityIndexLiftVsModelOnly'),
   o.get('avgLatencyS'),o.get('searchTimePerTaskS'),o.get('candidateModelLatencyS'),o.get('searchQueryLatencyS'),
   o.get('candidateModelCostPerTaskUsd'),o.get('searchApiCostPerTaskUsd'),o.get('costPerSearchQueryUsd'),
   o.get('searchQueriesPerTask'),o.get('inputTokensPerTask'),o.get('reasoningTokensPerTask'),o.get('answerTokensPerTask'),o.get('benchmarkCount'),o.get('latestMeasuredAt'),json.dumps(o,ensure_ascii=False)))
print('Such-Agenten-Konfigurationen:',len(found))
