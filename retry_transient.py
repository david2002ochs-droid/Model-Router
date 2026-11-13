#!/usr/bin/env python3
"""Requeue at most two transient HTTP/network errors, without retrying 403/429 or 404."""
import sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('create table if not exists retry_attempts(url text primary key, retry_count integer not null default 0, last_error text)')
c.execute('BEGIN IMMEDIATE')
rows=c.execute("""select q.url,q.error from crawl_queue q left join retry_attempts r on q.url=r.url where q.status='error' and (q.http_status is null or q.http_status in (500,502,503,504)) and coalesce(r.retry_count,0)<2""").fetchall()
with c:
 for url,error in rows:
  c.execute('insert into retry_attempts(url,retry_count,last_error) values(?,1,?) on conflict(url) do update set retry_count=retry_count+1,last_error=excluded.last_error',(url,error))
  c.execute("update crawl_queue set status='pending',error=NULL where url=?",(url,))
print('Temporäre Fehler erneut eingereiht:',len(rows))
