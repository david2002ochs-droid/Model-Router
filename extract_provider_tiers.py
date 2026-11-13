#!/usr/bin/env python3
"""Preserve and cautiously parse publicly displayed provider pricing footnotes."""
import json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS provider_pricing_footnotes(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,endpoint_id TEXT NOT NULL,host_slug TEXT,host_name TEXT,model_slug TEXT,model_name TEXT,footnote_text TEXT NOT NULL,PRIMARY KEY(source_url,endpoint_id))''')
c.execute('''CREATE TABLE IF NOT EXISTS provider_tiered_pricing(source_url TEXT NOT NULL,page_sha256 TEXT NOT NULL,endpoint_id TEXT NOT NULL,host_slug TEXT,model_slug TEXT,tier_number INTEGER NOT NULL,threshold_raw TEXT NOT NULL,input_price_raw TEXT NOT NULL,output_price_raw TEXT NOT NULL,input_price_per_million REAL,output_price_per_million REAL,amount_parse_warning TEXT,footnote_text TEXT NOT NULL,PRIMARY KEY(source_url,endpoint_id,tier_number))''')
pattern=re.compile(r'^\s*-\s*([^:]+):\s*\$([\d.,]+)\s*/\s*\$([\d.,]+)\s+per\s+M\s+tokens\s*$',re.I)
def number(raw):
 if not re.fullmatch(r'\d+(?:\.\d+)?',raw):return None
 try:return float(raw)
 except ValueError:return None
rows=c.execute("select source_url,page_sha256,endpoint_id,host_slug,host_name,model_slug,model_name,raw_json from latest_provider_endpoints where array_kind='rows'").fetchall();foot=[];tiers=[]
for source,sha,eid,host,hostname,model,name,raw in rows:
 o=json.loads(raw);note=o.get('footnotes')
 if not isinstance(note,str) or not note or note.startswith('$'):continue
 foot.append((source,sha,eid,host,hostname,model,name,note));j=0
 for line in note.splitlines():
  m=pattern.fullmatch(line)
  if not m:continue
  threshold,inp,out=m.groups();j+=1;iv,ov=number(inp),number(out);warning='Nicht eindeutig lesbares Zahlenformat; Rohwert prüfen' if iv is None or ov is None else None
  tiers.append((source,sha,eid,host,model,j,threshold.strip(),'$'+inp,'$'+out,iv,ov,warning,note))
with c:
 c.execute('delete from provider_pricing_footnotes');c.execute('delete from provider_tiered_pricing')
 c.executemany('insert into provider_pricing_footnotes values(?,?,?,?,?,?,?,?)',foot)
 c.executemany('insert into provider_tiered_pricing values(?,?,?,?,?,?,?,?,?,?,?,?,?)',tiers)
print('Hinweise:',len(foot),'Preisstaffeln:',len(tiers),'mit parse-Warnung:',sum(x[11] is not None for x in tiers))
