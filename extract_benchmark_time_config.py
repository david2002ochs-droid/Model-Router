#!/usr/bin/env python3
"""Extract simple benchmark token-count accessors used by archived application code."""
import re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS benchmark_time_config(
 benchmark_slug TEXT PRIMARY KEY,token_field TEXT NOT NULL,task_count REAL NOT NULL,has_tool_time INTEGER NOT NULL,
 registry_source_sha256 TEXT NOT NULL,source_definition TEXT NOT NULL)''')
rows=[]
for slug,count,sha,body in c.execute('select evaluation_slug,task_count,source_sha256,definition_raw from benchmark_registry_metadata'):
 m=re.search(r'getRawCanonicalTokenCount:\w+=>\w+\.([\w]+)',body)
 if m and count and count>0:rows.append((slug,m.group(1),count,int('getToolMsPerTask:' in body),sha,body))
if len(rows)<25:raise SystemExit('Zu wenige gültige Konfigurationen; kein Import')
with c:
 c.execute('delete from benchmark_time_config');c.executemany('insert into benchmark_time_config values(?,?,?,?,?,?)',rows)
print('Benchmark-Zeitkonfigurationen:',len(rows))
