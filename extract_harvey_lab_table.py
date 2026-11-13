#!/usr/bin/env python3
"""Preserve visible Harvey LAB-AA benchmark results and displayed cost/task."""
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS harvey_lab_table_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,table_number INTEGER NOT NULL,row_number INTEGER NOT NULL,
 display_rank INTEGER,creator_name TEXT,model_name TEXT NOT NULL,hallucination_gated_all_pass_pct REAL,
 criterion_pass_pct REAL,material_hallucinations_per_task REAL,displayed_cost_usd_per_task REAL,release_date_text TEXT,
 raw_cells_json TEXT NOT NULL,PRIMARY KEY(source_url,table_number,row_number))''')
url='https://artificialanalysis.ai/evaluations/harvey-lab-aa';row=c.execute('select page_sha256,table_number,rows_json from extracted_tables where url=? and table_number=0',(url,)).fetchone()
if not row:raise SystemExit('Rangliste nicht archiviert und extrahiert')
sha,tn,raw=row;rows=json.loads(raw);head=[x['text'] for x in rows[0]]
if head!=['','Creator','Name','Hallucination-Gated All-Pass Rate','Criterion Pass Rate','Material Hallucinations per Task','Cost per Task','Release Date']:raise SystemExit('Tabellenstruktur geändert; kein Import')
def num(s):
 if not re.fullmatch(r'\$?-?\d+(?:\.\d+)?%?',s.strip()):return None
 return float(s.strip().lstrip('$').rstrip('%'))
n=0
with c:
 c.execute('delete from harvey_lab_table_observations where source_url=? and table_number=?',(url,tn))
 for i,r in enumerate(rows[1:],1):
  v=[x['text'] for x in r]
  if len(v)!=8 or not v[2]:continue
  c.execute('insert into harvey_lab_table_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?)',(url,sha,tn,i,int(v[0]) if v[0].isdigit() else None,v[1] or None,v[2],num(v[3]),num(v[4]),num(v[5]),num(v[6]),v[7] or None,json.dumps(r,ensure_ascii=False)));n+=1
print('Harvey LAB-AA Tabellenzeilen:',n)
