#!/usr/bin/env python3
"""Extract benchmark slug/score field registry from an archived public JS bundle."""
import hashlib,re,sqlite3,sys,urllib.request,datetime
from pathlib import Path
URL='https://artificialanalysis.ai/_next/static/chunks/17016-209a4f52fd2e3e26.js'
try:
 with sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60) as existing:
  saved=existing.execute('select sha256,body from registry_sources where source_url=? order by rowid desc limit 1',(URL,)).fetchone()
except sqlite3.OperationalError:saved=None
if saved:
 if hashlib.sha256(saved[1]).hexdigest()!=saved[0]:raise SystemExit('Archivierte Registry hat falschen SHA-256')
 raw=saved[1]
else:
 with urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as r:raw=r.read()
s=raw.decode();sha=hashlib.sha256(raw).hexdigest();a=s.find('let s="artificial-analysis-intelligence-index"');b=s.find(',$={',a)
if a<0 or b<0:sys.exit('Bekannte Benchmark-Registry nicht gefunden')
variables=dict(re.findall(r'([A-Za-z_$][\w$]*)="([a-z0-9-]+)"',s[a:b]));found=[]
for sym,slug in variables.items():
 m=re.search(r'\['+re.escape(sym)+r'\]:([^,\]]+)',s[b:])
 if not m:continue
 frag=s[b+m.start():b+m.start()+600]
 if frag.startswith('['+sym+']:{'):body=frag
 else:
  ref=re.match(r'\['+re.escape(sym)+r'\]:([\w$]+)',frag)
  if not ref:continue
  x=re.search(r'\b'+re.escape(ref.group(1))+r'=\{',s[b:]);body=s[b+x.start():b+x.start()+600] if x else ''
 z=re.search(r'getScore:(.*?)(?:,getRawCanonicalTokenCount:|,scoreConfig:)',body)
 k=re.search(r'\be\.([\w]+)',z.group(1)) if z else None
 if k:found.append((slug,k.group(1),z.group(0)))
if len(found)<30:sys.exit('Unzureichende Zuordnung, Import abgebrochen')
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.executescript('''CREATE TABLE IF NOT EXISTS registry_sources(sha256 TEXT PRIMARY KEY,source_url TEXT NOT NULL,retrieved_at_utc TEXT NOT NULL,body BLOB NOT NULL);CREATE TABLE IF NOT EXISTS benchmark_registry(evaluation_slug TEXT PRIMARY KEY,score_field TEXT NOT NULL,source_sha256 TEXT NOT NULL,expression TEXT NOT NULL);''')
with c:
 c.execute('insert or ignore into registry_sources values(?,?,?,?)',(sha,URL,datetime.datetime.now(datetime.timezone.utc).isoformat(),raw))
 c.executemany('insert or replace into benchmark_registry values(?,?,?,?)',[(slug,key,sha,expr) for slug,key,expr in found])
print('Benchmark-Feldzuordnungen:',len(found))
