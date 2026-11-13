#!/usr/bin/env python3
"""Extract source-matched overall and category Elo rows from image/video Arena pages."""
import gzip,json,re,sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=60)
c.execute('''CREATE TABLE IF NOT EXISTS media_arena_observations(
 source_url TEXT NOT NULL,source_sha256 TEXT NOT NULL,media_type TEXT NOT NULL,arena_task TEXT NOT NULL,
 category_slug TEXT NOT NULL,model_id TEXT NOT NULL,model_name TEXT NOT NULL,creator_id TEXT,creator_name TEXT,
 elo REAL,confidence_lower REAL,confidence_upper REAL,sample_count INTEGER,release_date TEXT,
 price_usd_per_1000_images REAL,price_usd_per_video_minute REAL,open_weights_url TEXT,raw_json TEXT NOT NULL,
 PRIMARY KEY(source_url,category_slug,model_id))''')
dec=json.JSONDecoder();total=0
pages=c.execute("select p.url,p.sha256,p.body_gzip,t.rows_json from page_archive p join extracted_tables t on p.url=t.url where (p.url like '%/image/leaderboard/%' or p.url like '%/video/leaderboard/%') and p.url not like '%/open-weights' and t.table_number=0").fetchall()
for url,sha,blob,table_raw in pages:
 try:
  table=json.loads(table_raw); header=[x['text'] for x in table[0]]
  if header[:5]!=['','Range','Model','Elo','Samples']:continue
  names={r[2]['text'] for r in table[1:] if len(r)>2 and r[2]['text']};html=gzip.decompress(blob).decode('utf8',errors='replace');candidates=[]
  for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:\\.|[^"\\])*")\]\)',html):
   s=json.loads(m.group(1));prefix=re.match(r'^[0-9a-f]+:',s)
   if not prefix:continue
   try:a,_=dec.raw_decode(s,prefix.end())
   except ValueError:continue
   if not isinstance(a,list) or not a or not isinstance(a[0],list) or len(a[0])!=2 or a[0][0] is not None or not isinstance(a[0][1],list):continue
   vals=[o.get('values',{}) for o in a[0][1] if isinstance(o,dict)]
   found={v.get('name') for v in vals if isinstance(v,dict) and v.get('id') and 'elo' in v}
   if found==names:candidates.append(a)
  if len(candidates)!=1:
   print('übersprungen: kein eindeutiges passendes Dataset',url,len(candidates));continue
  categories=candidates[0];media='image' if '/image/' in url else 'video';task=url.split('/leaderboard/',1)[1]
  n=0
  with c:
   c.execute('delete from media_arena_observations where source_url=?',(url,))
   for group in categories:
    if not isinstance(group,list) or len(group)!=2 or not isinstance(group[1],list):continue
    cat=group[0] if isinstance(group[0],str) else '__overall__'
    for obj in group[1]:
     if not isinstance(obj,dict):continue
     v=obj.get('values');
     if not isinstance(v,dict) or not v.get('id') or not v.get('name') or 'elo' not in v:continue
     creator=v.get('creator') or {}
     c.execute('insert or replace into media_arena_observations values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
      url,sha,media,task,cat,v['id'],v['name'],creator.get('id'),creator.get('name'),v.get('elo'),v.get('ciLower'),v.get('ciUpper'),v.get('appearances'),v.get('releaseDate'),v.get('pricePer1kImages'),v.get('pricePerMinute'),v.get('openWeightsUrl'),json.dumps(obj,ensure_ascii=False)))
     n+=1
  print(url,'kategorien',len(categories),'werte',n);total+=n
 except (ValueError,TypeError,KeyError) as e:print('übersprungen',url,str(e))
print('Gesamt:',total)
