#!/usr/bin/env python3
"""Export final SQLite views and validate reconstruction against the current table schema."""
import re, sqlite3
from pathlib import Path
root=Path(__file__).resolve().parent
c=sqlite3.connect(root/'artificial_analysis.sqlite3',timeout=60)
views=c.execute("select name,sql from sqlite_master where type='view' and sql is not null order by name").fetchall()
tables=c.execute("select name,sql from sqlite_master where type='table' and sql is not null and name not like 'sqlite_%' order by name").fetchall()
if not views:raise SystemExit('Keine Views gefunden; Export abgebrochen')
def quote(x):return '"'+x.replace('"','""')+'"'
script='-- Finaler View-Stand; nur auf einer gesicherten, kompatiblen Datenbank installieren.\nBEGIN;\n'
script+=''.join('DROP VIEW IF EXISTS '+quote(name)+';\n' for name,_ in views)
script+=''.join(sql.rstrip(';')+';\n' for _,sql in views)
script+='COMMIT;\n'
# Verify schema on an empty in-memory database, leaving the live database untouched.
test=sqlite3.connect(':memory:')
for name,sql in tables:
 try:test.execute(sql)
 except sqlite3.Error as exc:raise SystemExit('Tabellenschema '+name+': '+str(exc))
try:test.executescript(script)
except sqlite3.Error as exc:raise SystemExit('View-Installation fehlgeschlagen: '+str(exc))
errors=[]
for name,_ in views:
 try:test.execute('SELECT * FROM '+quote(name)+' LIMIT 0')
 except sqlite3.Error as exc:errors.append((name,str(exc)))
if errors:
 for name,error in errors:print(name,error)
 raise SystemExit('View-Prüfung fehlgeschlagen; Export nicht ersetzt')
indexes=c.execute("select sql from sqlite_master where type='index' and sql is not null order by name").fetchall()
bootstrap='-- Leeres, kompatibles Datenbankschema; enthält keine Daten.\nBEGIN;\n'
bootstrap+=''.join(re.sub(r'^CREATE TABLE\s+', 'CREATE TABLE IF NOT EXISTS ', sql, count=1, flags=re.I).rstrip(';')+';\n' for _,sql in tables)
bootstrap+=''.join(re.sub(r'^CREATE (UNIQUE )?INDEX\s+', lambda m: 'CREATE '+(m.group(1) or '')+'INDEX IF NOT EXISTS ', sql, count=1, flags=re.I).rstrip(';')+';\n' for (sql,) in indexes)
bootstrap+=''.join(sql.rstrip(';')+';\n' for _,sql in views)+'COMMIT;\n'
blank=sqlite3.connect(':memory:')
try:
 blank.executescript(bootstrap)
 for name,_ in views:blank.execute('SELECT * FROM '+quote(name)+' LIMIT 0')
except sqlite3.Error as exc:raise SystemExit('Leerer Bootstrap nicht gültig: '+str(exc))
(root/'views_snapshot.sql').write_text(script,encoding='utf8')
(root/'bootstrap_schema.sql').write_text(bootstrap,encoding='utf8')
print(len(views),'Views und',len(tables),'Tabellenschemata geprüft; leerer Bootstrap geprüft')
