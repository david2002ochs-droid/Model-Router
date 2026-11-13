#!/usr/bin/env python3
"""Copy archival input tables into an empty bootstrapped database, without touching the source."""
import gzip,hashlib,sqlite3,sys,zlib
from pathlib import Path
from urllib.parse import quote
TABLES=('crawl_queue','page_archive','page_capture_events','captures','model_observations','discovered_links','retry_attempts','embedded_model_snapshots')
if len(sys.argv)!=3:raise SystemExit('Nutzung: restore_archive.py QUELL-DB LEERE-ZIEL-DB')
src=Path(sys.argv[1]).resolve();dst=Path(sys.argv[2]).resolve()
if src==dst or not src.is_file() or not dst.is_file():raise SystemExit('Zwei unterschiedliche vorhandene Datenbankdateien angeben')
c=sqlite3.connect(dst,timeout=60,uri=True)
c.execute('attach database ? as origin',('file:'+quote(str(src))+'?mode=ro',))
c.execute('BEGIN')  # Keep source reads and copy in the same consistent transaction.
def columns(schema,table):return [x[1:6] for x in c.execute('pragma '+schema+'.table_info('+table+')')]
for table in TABLES:
 if not columns('main',table) or columns('main',table)!=columns('origin',table):raise SystemExit('Tabelle fehlt oder Schema abweichend: '+table)
 if c.execute('select count(*) from main.'+table).fetchone()[0]:raise SystemExit('Zieltabelle ist nicht leer: '+table)
checked=0
for url,sha,blob in c.execute('select url,sha256,body_gzip from origin.page_archive'):
 try:actual=hashlib.sha256(gzip.decompress(blob)).hexdigest()
 except (OSError,EOFError,zlib.error) as exc:raise SystemExit('Archiv nicht entpackbar: '+url+' ('+str(exc)+')')
 if actual!=sha:raise SystemExit('Archiv-Hash stimmt nicht: '+url)
 checked+=1
print('Archivseiten mit SHA-256 geprüft:',checked)
with c:
 for table in TABLES:
  c.execute('insert into main.'+table+' select * from origin.'+table)
  print(table,c.execute('select count(*) from main.'+table).fetchone()[0])
print('Archivquellen kopiert; abgeleitete Beobachtungen müssen anschließend neu extrahiert werden.')
