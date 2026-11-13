#!/usr/bin/env python3
import datetime, hashlib, json, sqlite3, urllib.request
from html.parser import HTMLParser
from pathlib import Path
BASE='https://artificialanalysis.ai/leaderboards/models'
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(); self.table=0; self.active=False; self.cell=None; self.rows=[]; self.row=[]; self.links=[]
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='table': self.table+=1
  if self.table and t=='tr': self.active=True; self.row=[]; self.links=[]
  if self.active and t in ('th','td'): self.cell=[]
  if self.active and t=='a' and a.get('href'): self.links.append(a['href'])
 def handle_data(self,d):
  if self.cell is not None: self.cell.append(d)
 def handle_endtag(self,t):
  if t in ('th','td') and self.cell is not None: self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
  if t=='tr' and self.active: self.rows.append((self.row,self.links)); self.active=False
  if t=='table': self.table-=1
req=urllib.request.Request(BASE,headers={'User-Agent':'Mozilla/5.0'})
with urllib.request.urlopen(req,timeout=60) as response: raw=response.read()
p=Parser(); p.feed(raw.decode())
headers=next((r for r,_ in p.rows if r and r[0]=='Model' and 'Cost per TaskUSD' in r),None)
if not headers: raise RuntimeError('Spalten verändert; Import abgebrochen')
rows=[(r,l) for r,l in p.rows if len(r)==8 and r[0] not in ('','Model') and r[2] and r[7]]
if len(rows)<10: raise RuntimeError('Zu wenige Zeilen; Import abgebrochen')
db=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'))
db.executescript('''CREATE TABLE IF NOT EXISTS captures(id INTEGER PRIMARY KEY, retrieved_at_utc TEXT NOT NULL, source_url TEXT NOT NULL, sha256 TEXT NOT NULL, headers_json TEXT NOT NULL, row_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS model_observations(capture_id INTEGER NOT NULL REFERENCES captures(id), row_number INTEGER NOT NULL, model_name TEXT NOT NULL, context_window TEXT, creator TEXT, intelligence_index REAL, cost_per_task_usd REAL, time_per_task_minutes REAL, first_answer_token_seconds REAL, raw_cells_json TEXT NOT NULL, links_json TEXT NOT NULL, PRIMARY KEY(capture_id,row_number));''')
def number(s):
 try: return float(s.replace('$','').replace(',','').strip())
 except ValueError: return None
with db:
 cur=db.execute('INSERT INTO captures(retrieved_at_utc,source_url,sha256,headers_json,row_count) VALUES(?,?,?,?,?)',(datetime.datetime.now(datetime.timezone.utc).isoformat(),BASE,hashlib.sha256(raw).hexdigest(),json.dumps(headers),len(rows)))
 for i,(r,links) in enumerate(rows,1):
  db.execute('INSERT INTO model_observations VALUES(?,?,?,?,?,?,?,?,?,?,?)',(cur.lastrowid,i,r[0],r[1] or None,r[2],number(r[3]),number(r[4]),number(r[5]),number(r[6]),json.dumps(r,ensure_ascii=False),json.dumps(links,ensure_ascii=False)))
print('Erfasst:',len(rows),'Zeilen; Snapshot',cur.lastrowid)
