#!/usr/bin/env python3
import sqlite3
from pathlib import Path
c=sqlite3.connect(Path(__file__).with_name('artificial_analysis.sqlite3'),timeout=30)
print('SQLite:',c.execute('pragma quick_check').fetchone()[0])
rows=c.execute('''select d.name,json_extract(d.model_json,'$.intelligenceIndexTimePerTask'),o.time_per_task_minutes,json_extract(d.model_json,'$.intelligenceIndexCostPerTask.cost.total'),o.cost_per_task_usd from model_details d join model_observations o on lower(json_extract(d.model_json,'$.shortName'))=lower(o.model_name) where o.time_per_task_minutes is not null and json_extract(d.model_json,'$.intelligenceIndexTimePerTask') is not null and o.cost_per_task_usd is not null''').fetchall()
print('Vergleich Detailobjekte/Rangliste:',len(rows))
print('Zeit innerhalb 0,11 Minuten:',sum(abs(t/60-m)<=.11 for _,t,m,_,_ in rows))
print('Kosten innerhalb 0,011 USD:',sum(abs(a-b)<=.011 for _,_,_,a,b in rows if a is not None))
print('Abweichungen können durch unterschiedliche Abrufzeitpunkte oder Rundung entstehen.')
comp=c.execute('''select count(*),sum(case when abs(j.value-k.value)>1e-7 then 1 else 0 end) from model_details d join embedded_latest_models e on d.model_id=e.model_id,json_each(d.model_json) j,json_each(e.model_json) k where j.key=k.key and j.type in ('integer','real') and k.type in ('integer','real')''').fetchone()
print('Gleichnamige numerische Felder in Detailseiten/Snapshot:',comp[0],'; Abweichungen:',comp[1] or 0)
dupe=c.execute('select count(*) from (select model_id,evaluation_slug,count(*) n from latest_combined_benchmark_scores group by model_id,evaluation_slug having n>1)').fetchone()[0]
print('Doppelte Modell-/Benchmarkpaare in jüngster Sicht:',dupe)
if c.execute("select 1 from sqlite_master where name='benchmark_cost_estimates'").fetchone():
 rows=c.execute('''select a.model_id,a.benchmark_slug,max(case when abs(a.cost_usd_per_task-b.cost_per_task)>0.0000001 then 1 else 0 end) differs from benchmark_cost_estimates a join embedded_benchmark_results b on a.model_id=b.model_id and a.benchmark_slug=b.evaluation_slug where a.cost_usd_per_task is not null and b.cost_per_task is not null group by a.model_id,a.benchmark_slug''').fetchall()
 print('Kostenabgleich: eindeutige Modell-/Benchmarkpaare:',len(rows),'; Abweichungen:',sum(x[2] for x in rows))
