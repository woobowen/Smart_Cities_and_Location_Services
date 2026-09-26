"""Current read-only structural verification of cases already named in starter materials."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
p=ROOT/'task1/作业/作业/traj_dict.json'; before=hashlib.sha256(p.read_bytes()).hexdigest();data=json.loads(p.read_text())
ids=['0','246','256','306','352','209']; rows=[]
for vid in ids:
 value=data.get(vid)
 if value is None:
  rows.append({'record_id':vid,'present':False}); continue
 ts,ps=value[:2];dt=[b-a for a,b in zip(ts,ts[1:])]
 rows.append({'record_id':vid,'present':True,'point_count':len(ps),'time_count':len(ts),'unique_timestamps':len(set(ts)),'raw_span':ts[-1]-ts[0] if ts else None,'raw_dt_min':min(dt) if dt else None,'raw_dt_max':max(dt) if dt else None,'zero_dt_count':sum(t==0 for t in dt),'negative_dt_count':sum(t<0 for t in dt),'adjacent_equal_position_count':sum(a==b for a,b in zip(ps,ps[1:]))})
after=hashlib.sha256(p.read_bytes()).hexdigest();assert before==after
out={'classification':'CURRENT_RUN_READ_ONLY_STRUCTURE_CHECK','purpose':'check historical named-case structural claims; no metric-distance inference','command':'python3 task1/evidence/goal1/materials/check_historical_cases.py','input_path':p.relative_to(ROOT).as_posix(),'input_sha256':before,'input_sha256_after':after,'input_unchanged':True,'case_ids_previously_exposed_in_starter':ids,'results':rows}
Path(__file__).with_name('historical_case_structure_check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':'EXECUTED','classification':out['classification'],'cases':len(rows),'input_unchanged':True},ensure_ascii=False))
