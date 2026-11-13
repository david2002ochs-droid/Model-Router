#!/usr/bin/env python3
import datetime, hashlib, json, os, sqlite3, sys, urllib.error, urllib.request
from pathlib import Path
key=os.environ.get('ARTIFICIAL_ANALYSIS_API_KEY')
if not key: sys.exit('ARTIFICIAL_ANALYSIS_API_KEY fehlt. Siehe README.md.')
base='https://artificialanalysis.ai/api/v2'
paths=sys.argv[1:] or ['/language/models']
if any(not p.startswith('/') or p.startswith('//') for p in paths): sys.exit('Nur relative API-Pfade verwenden.')
db=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'))
db.execute('CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY, retrieved_at_utc TEXT NOT NULL, endpoint TEXT NOT NULL, status INTEGER NOT NULL, sha256 TEXT NOT NULL, response_json TEXT NOT NULL)')
for path in paths:
 req=urllib.request.Request(base+path,headers={'x-api-key':key,'Accept':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=60) as r: raw=r.read(); status=r.status
  obj=json.loads(raw)
  with db: db.execute('INSERT INTO snapshots(retrieved_at_utc,endpoint,status,sha256,response_json) VALUES(?,?,?,?,?)',(datetime.datetime.now(datetime.timezone.utc).isoformat(),path,status,hashlib.sha256(raw).hexdigest(),json.dumps(obj,ensure_ascii=False)))
  print(path, 'gespeichert')
 except (urllib.error.HTTPError, urllib.error.URLError, ValueError) as e: print(path, 'fehlgeschlagen:',e, file=sys.stderr)
