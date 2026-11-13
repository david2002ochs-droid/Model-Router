#!/usr/bin/env python3
"""Extract visible HTML tables from archived pages, preserving cells and links."""
import gzip, hashlib, json, sqlite3
from html.parser import HTMLParser
from pathlib import Path
class Tables(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True); self.depth=0; self.tables=[]; self.rows=[]; self.row=None; self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':
   self.depth+=1
   if self.depth==1: self.rows=[]
  if self.depth==1 and t=='tr': self.row=[]
  if self.depth==1 and self.row is not None and t in ('td','th'): self.cell={'text':[], 'links':[], 'header':t=='th'}
  if self.cell is not None and t=='a' and dict(a).get('href'): self.cell['links'].append(dict(a)['href'])
 def handle_data(self,d):
  if self.cell is not None: self.cell['text'].append(d)
 def handle_endtag(self,t):
  if self.depth==1 and t in ('td','th') and self.cell is not None:
   self.cell['text']=' '.join(''.join(self.cell['text']).split()); self.row.append(self.cell); self.cell=None
  if self.depth==1 and t=='tr' and self.row is not None:
   if self.row:self.rows.append(self.row)
   self.row=None
  if t=='table' and self.depth:
   if self.depth==1 and self.rows:self.tables.append(self.rows)
   self.depth-=1
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
c.executescript('''CREATE TABLE IF NOT EXISTS extracted_tables(url TEXT NOT NULL, page_sha256 TEXT NOT NULL, table_number INTEGER NOT NULL, rows_json TEXT NOT NULL, PRIMARY KEY(url,table_number)); CREATE TABLE IF NOT EXISTS table_extraction_log(url TEXT PRIMARY KEY, page_sha256 TEXT NOT NULL, table_count INTEGER NOT NULL, error TEXT);''')
pages=c.execute('SELECT p.url,p.sha256,p.body_gzip FROM page_archive p LEFT JOIN table_extraction_log l ON p.url=l.url WHERE l.page_sha256 IS NULL OR l.page_sha256<>p.sha256').fetchall()
tables=0
for url,sha,blob in pages:
 try:
  p=Tables(); p.feed(gzip.decompress(blob).decode('utf-8',errors='replace'))
  with c:
   c.execute('DELETE FROM extracted_tables WHERE url=?',(url,))
   c.executemany('INSERT INTO extracted_tables VALUES(?,?,?,?)',[(url,sha,i,json.dumps(t,ensure_ascii=False)) for i,t in enumerate(p.tables)])
   c.execute('INSERT OR REPLACE INTO table_extraction_log VALUES(?,?,?,NULL)',(url,sha,len(p.tables)))
  tables+=len(p.tables)
 except Exception as e:
  with c:c.execute('INSERT OR REPLACE INTO table_extraction_log VALUES(?,?,0,?)',(url,sha,str(e)[:500]))
print(f'{len(pages)} Seiten verarbeitet; {tables} Tabellen extrahiert')
