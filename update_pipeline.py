#!/usr/bin/env python3
"""Refresh independent extractions while the associated crawler runs."""
import datetime,os,sqlite3,subprocess,sys,time
from pathlib import Path
p=Path(__file__).resolve().parent;db=p/'artificial_analysis.sqlite3'
if len(sys.argv)!=2:raise SystemExit('Nutzung: update_pipeline.py CRAWLER_PID | --once')
once=sys.argv[1]=='--once';pid=None if once else int(sys.argv[1]);last=0
scripts=('extract_tables.py','extract_provider_leaderboard.py','extract_providers.py','extract_provider_accuracy.py','extract_provider_pages.py','extract_search_api.py','extract_chatbot_plans.py','extract_search_agent_details.py','extract_decision_index.py','extract_harvey_lab_table.py','extract_harvey_costs.py','extract_models.py','extract_evaluations.py','extract_benchmark_time_config.py','extract_benchmark_cost_estimates.py','extract_coding_agents.py','extract_speech_benchmarks.py','extract_speech_agent_host_details.py','extract_speech_agent_arena.py','extract_streaming_speech.py','extract_tts_arena.py','extract_media_arena.py','extract_media_openweights.py','extract_media_leaderboards.py','extract_media_endpoints.py','extract_image_provider_performance.py','extract_video_provider_performance.py','extract_endpoint_prices.py','extract_provider_tiers.py','extract_cache_pricing_table.py','verify_archive.py','export_view_schema.py','source_evidence.py','validate_provider_prices.py','coverage.py')
internal_logs={'extract_tables.py':'table_extraction_log','extract_models.py':'model_extraction_log','extract_evaluations.py':'evaluation_extraction_log','extract_coding_agents.py':'coding_agent_extraction_log','extract_endpoint_prices.py':'provider_endpoint_extraction_log','extract_media_endpoints.py':'media_endpoint_extraction_log'}
with sqlite3.connect(db,timeout=60) as c:
 c.execute('''CREATE TABLE IF NOT EXISTS pipeline_step_runs(id INTEGER PRIMARY KEY,started_at_utc TEXT NOT NULL,script TEXT NOT NULL,exit_code INTEGER,status TEXT NOT NULL,summary TEXT)''')
while True:
 if once:alive=False
 else:
  try:os.kill(pid,0);alive=True
  except ProcessLookupError:alive=False
 with sqlite3.connect(db,timeout=60) as c:n=c.execute("select count(*) from crawl_queue where status='ok'").fetchone()[0]
 if n-last>=100 or not alive:
  failures=0
  for script in scripts:
   started=datetime.datetime.now(datetime.timezone.utc).isoformat()
   try:
    result=subprocess.run([sys.executable,str(p/script)],capture_output=True,text=True,timeout=1200)
    rc=result.returncode;status='ok' if rc==0 else 'error';summary=(result.stdout.strip()+' '+result.stderr.strip())[-1500:]
   except subprocess.TimeoutExpired:
    rc=None;status='timeout';summary='Schritt nach 1200 Sekunden abgebrochen'
   if status=='ok' and script in internal_logs:
    with sqlite3.connect(db,timeout=60) as c:
     unresolved=c.execute('select count(*) from '+internal_logs[script]+' where error is not null').fetchone()[0]
    if unresolved:status='partial';summary+=f' | {unresolved} offene Quellfehler im Extraktionslog'
   if status!='ok':failures+=1
   with sqlite3.connect(db,timeout=60) as c:c.execute('insert into pipeline_step_runs(started_at_utc,script,exit_code,status,summary) values(?,?,?,?,?)',(started,script,rc,status,summary))
   print(script,status,summary[:300],flush=True)
  last=n if failures==0 else max(0,n-90)
  if failures:print('Fehler in',failures,'Schritten; Einzelheiten in pipeline_step_runs.',flush=True)
 if not alive:
  with sqlite3.connect(db,timeout=60) as c:
   pending=c.execute("select count(*) from crawl_queue where status='pending'").fetchone()[0]
  print(('Einmaliger Lauf beendet.' if once else 'Crawler gestoppt; automatische Aktualisierung beendet.'),'Ausstehende Seiten:',pending,'; Fehler und Stoppursache prüfen.',flush=True)
  if failures:raise SystemExit(1)
  break
 time.sleep(30)
