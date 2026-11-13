#!/usr/bin/env python3
"""Export/import the small set of archived formula and mapping sources with SHA-256 checks."""
import base64,hashlib,json,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TABLES=('benchmark_calculation_sources','media_mapping_sources','provider_pricing_mapping_sources','registry_sources')
manifest=ROOT/'source_evidence.json'
if len(sys.argv)==1:sys.argv.append('export')
if len(sys.argv)<2 or sys.argv[1] not in ('export','import'):
 raise SystemExit('Nutzung: source_evidence.py export | import PFAD_ZUR_DATENBANK')
if sys.argv[1]=='export':
 c=sqlite3.connect(ROOT/'artificial_analysis.sqlite3',timeout=60);out={}
 for name in TABLES:
  cols=[r[1] for r in c.execute('pragma table_info('+name+')')]
  rows=[]
  for values in c.execute('select * from '+name):
   obj=dict(zip(cols,values));body=obj.pop('body')
   if hashlib.sha256(body).hexdigest()!=obj['sha256']:raise SystemExit('SHA-256-Abweichung: '+name)
   obj['body_base64']=base64.b64encode(body).decode('ascii');rows.append(obj)
  out[name]=rows
 inventory={name:sorted([(row['sha256'],row['source_url']) for row in rows]) for name,rows in out.items()}
 if any(not rows for rows in out.values()):raise SystemExit('Pflichtbelege fehlen; Export abgebrochen')
 encoded=json.dumps({'format_version':1,'inventory':inventory,'tables':out},ensure_ascii=False,indent=2).encode('utf8')
 manifest.write_bytes(encoded)
 (ROOT/'source_evidence.json.sha256').write_text(hashlib.sha256(encoded).hexdigest()+'\n',encoding='ascii')
 print('Quellartefakte exportiert:',sum(map(len,out.values())))
else:
 if len(sys.argv)!=3:raise SystemExit('Zieldatenbank angeben')
 raw=manifest.read_bytes()
 expected=(ROOT/'source_evidence.json.sha256').read_text(encoding='ascii').strip()
 if hashlib.sha256(raw).hexdigest()!=expected:raise SystemExit('Manifest-SHA-256 stimmt nicht')
 payload=json.loads(raw)
 if not isinstance(payload,dict) or payload.get('format_version')!=1 or set(payload.get('tables',{}))!=set(TABLES) or set(payload.get('inventory',{}))!=set(TABLES):
  raise SystemExit('Manifeststruktur oder Pflichtlisten fehlen')
 data=payload['tables']
 for name in TABLES:
  if not isinstance(data[name],list) or not data[name]:raise SystemExit('Pflichtbelege fehlen: '+name)
  actual=sorted([[r.get('sha256'),r.get('source_url')] for r in data[name]])
  if actual!=sorted(payload['inventory'][name]):raise SystemExit('Beleginventar unvollständig: '+name)
 c=sqlite3.connect(sys.argv[2],timeout=60)
 with c:
  for name in TABLES:
   cols=[r[1] for r in c.execute('pragma table_info('+name+')')]
   if not cols:raise SystemExit('Zieltabelle fehlt: '+name)
   for obj in data.get(name,[]):
    obj=dict(obj);body=base64.b64decode(obj.pop('body_base64'),validate=True)
    if hashlib.sha256(body).hexdigest()!=obj.get('sha256'):raise SystemExit('SHA-256-Abweichung: '+name)
    obj['body']=body
    if set(obj)!=set(cols):raise SystemExit('Unpassende Spalten: '+name)
    c.execute('insert or ignore into '+name+'('+','.join(cols)+') values('+','.join('?' for _ in cols)+')',[obj[k] for k in cols])
    keys=[r[1] for r in c.execute('pragma table_info('+name+')') if r[5]]
    if not keys:raise SystemExit('Kein Primärschlüssel: '+name)
    existing=c.execute('select sha256,body from '+name+' where '+' and '.join(k+'=?' for k in keys),[obj[k] for k in keys]).fetchone()
    if not existing or existing[0]!=obj['sha256'] or existing[1]!=body or hashlib.sha256(existing[1]).hexdigest()!=existing[0]:
     raise SystemExit('Vorhandener Quellbeleg widerspricht Manifest: '+name)
 print('Quellartefakte importiert und vorhandene Inhalte geprüft')
