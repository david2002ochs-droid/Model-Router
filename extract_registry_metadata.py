#!/usr/bin/env python3
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
sha,raw=c.execute('select sha256,body from registry_sources order by rowid desc limit 1').fetchone();s=raw.decode();a=s.find('let s="artificial-analysis-intelligence-index"');b=s.find(',$={',a)
variables=dict(re.findall(r'([A-Za-z_$][\w$]*)="([a-z0-9-]+)"',s[a:b]))
def obj_at(i):
 if i<0 or s[i]!='{':return None
 depth=0;quote=None;esc=False
 for j in range(i,len(s)):
  ch=s[j]
  if quote:
   if esc:esc=False
   elif ch=='\\':esc=True
   elif ch==quote:quote=None
  elif ch in ('"',"'",'`'):quote=ch
  elif ch=='{':depth+=1
  elif ch=='}':
   depth-=1
   if depth==0:return s[i:j+1]
 return None
c.execute('create table if not exists benchmark_registry_metadata(evaluation_slug TEXT PRIMARY KEY,source_sha256 TEXT NOT NULL,task_count REAL,task_weight REAL,score_format TEXT,config_raw TEXT,definition_raw TEXT NOT NULL)')
rows=[]
for sym,slug in variables.items():
 m=re.search(r'\['+re.escape(sym)+r'\]:',s[b:])
 if not m:continue
 pos=b+m.end()
 if s[pos]=='{':body=obj_at(pos)
 else:
  ref=re.match(r'[A-Za-z_$][\w$]*',s[pos:])
  if not ref:continue
  pat=r'(?<![\w$])'+re.escape(ref.group(0))+r'=\{';match=re.search(pat,s[b:])
  body=obj_at(b+match.end()-1) if match else None
 if not body or 'getScore:' not in body:continue
 def number(key):
  v=re.search(r'\b'+key+r':([A-Za-z_$][\w$]*|[0-9.eE+-]+)',body)
  if not v:return None
  val=v.group(1)
  try:return float(val)
  except ValueError:
   match=re.search(r'(?<![\w$])'+re.escape(val)+r'=([0-9.eE+-]+)(?=[,;}])',s[a:])
   try:return float(match.group(1)) if match else None
   except ValueError:return None
 cm=re.search(r'scoreConfig:',body);config=None
 if not cm:
  spread=re.search(r'\.\.\.([A-Za-z_$][\w$]*)',body)
  if spread:
   parent=re.search(r'(?<![\w$])'+re.escape(spread.group(1))+r'=\{',s[b:])
   parent_body=obj_at(b+parent.end()-1) if parent else None
   if parent_body and 'scoreConfig:' in parent_body:
    inherited=re.search(r'scoreConfig:([A-Za-z_$][\w$]*)',parent_body)
    if inherited:
     config_def=re.search(r'(?<![\w$])'+re.escape(inherited.group(1))+r'=\{',s[b:])
     config=obj_at(b+config_def.end()-1) if config_def else None
 if cm:
  pos=cm.end()
  if body[pos:pos+1]=='{':
   # Keep inline definition as source; extracting format does not require parsing JS.
   config=body[pos:pos+200]
  else:
   sym2=re.match(r'[A-Za-z_$][\w$]*',body[pos:])
   if sym2:
    match=re.search(r'(?<![\w$])'+re.escape(sym2.group(0))+r'=\{',s[b:]);config=obj_at(b+match.end()-1) if match else None
 fmt=re.search(r'longFormat:"([^"]+)"',config or '')
 rows.append((slug,sha,number('taskCount'),number('taskWeight'),fmt.group(1) if fmt else None,config,body))
with c:c.executemany('insert or replace into benchmark_registry_metadata values(?,?,?,?,?,?,?)',rows)
print('Metadaten:',len(rows));print(c.execute('select evaluation_slug,task_count,task_weight,score_format from benchmark_registry_metadata where evaluation_slug in (\'gpqa-diamond\',\'aa-briefcase\',\'gdp-pdf\',\'omniscience\')').fetchall())
