#!/usr/bin/env python3
"""Incrementally verify gzip bodies against their recorded SHA-256."""
import datetime,gzip,hashlib,sqlite3,sys,zlib
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS archive_integrity_checks(source_url TEXT PRIMARY KEY,page_sha256 TEXT NOT NULL,checked_at_utc TEXT NOT NULL,status TEXT NOT NULL,error TEXT)''')
if len(sys.argv)>1:
 if sys.argv[1:]!=['--full']:raise SystemExit('Nutzung: verify_archive.py [--full]')
 with c:c.execute('delete from archive_integrity_checks')
else:
 # Retry prior failures once per invocation, even if the recorded hash did not change.
 with c:c.execute("update archive_integrity_checks set page_sha256='' where status<>'ok'")
if c.execute('select count(*) from page_archive').fetchone()[0]==0:
 print('Archiv leer; keine Inhalte geprüft',file=sys.stderr);sys.exit(2)
checked=0
while True:
 rows=c.execute('''select p.url,p.sha256,p.body_gzip from page_archive p left join archive_integrity_checks a on a.source_url=p.url where a.page_sha256 is null or a.page_sha256<>p.sha256 limit 20''').fetchall()
 if not rows:break
 checks=[]
 for url,sha,blob in rows:
  try:
   actual=hashlib.sha256(gzip.decompress(blob)).hexdigest()
   status='ok' if actual==sha else 'mismatch';error=None if actual==sha else 'SHA-256 stimmt nicht'
  except (OSError,EOFError,TypeError,zlib.error) as e:status='error';error=str(e)[:500]
  checks.append((url,sha,datetime.datetime.now(datetime.timezone.utc).isoformat(),status,error))
 with c:c.executemany('insert or replace into archive_integrity_checks values(?,?,?,?,?)',checks)
 checked+=len(checks)
failed=c.execute("select count(*) from archive_integrity_checks a join page_archive p on p.url=a.source_url and p.sha256=a.page_sha256 where a.status<>'ok'").fetchone()[0]
print('Archivseiten geprüft:',checked,'aktuell fehlerhaft:',failed)
if failed:sys.exit(1)
