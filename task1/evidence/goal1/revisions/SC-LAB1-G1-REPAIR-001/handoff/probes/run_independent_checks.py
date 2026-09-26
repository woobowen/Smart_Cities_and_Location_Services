"""GPT second review; deterministic local audit, not a live Agent experiment.
Source snapshot is copied from the pinned GitHub files and git-blob verified.
No user-repository writes or model/network calls are performed.
"""
from pathlib import Path
import sys, json, hashlib, zipfile, copy, tempfile
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source_snapshot'))
from task1.workflow import diagnostics as d, tools
from task1.workflow.io import write_json,digest

out={'classification':'GPT_SECOND_REVIEW_LOCAL_AUDIT','reviewed_commit':'c2e3ffe2f5af92ee03dac16a2865ec7c42f576e0',
     'model_calls':0,'remote_writes':0,'limitations':['Not a full Git checkout or reproduction of the 108-test suite','Historical model calls were inspected, not repeated'],'probes':[]}
expected={'diagnostics.py':'a70fbe2f74512322e5d19b5541e960f1ba48a5f4','tools.py':'da9a59f939b5e00907a3c2eacfef51545c2d3505','io.py':'25ac484dcfcf376d0f8a9e760eec565a7857749a'}
for name,exp in expected.items():
 b=(ROOT/'source_snapshot/task1/workflow'/name).read_bytes()
 got=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
 assert got==exp,(name,got)
out['verified_source_blobs']=expected

# Independent raw recomputation from an existing teacher ZIP, identical content hash.
want='c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'
found=None
for zpath in sorted(Path('/mnt/data').glob('作业*.zip')):
 with zipfile.ZipFile(zpath) as z:
  for member in z.namelist():
   if member.endswith('/traj_dict.json'):
    b=z.read(member)
    if hashlib.sha256(b).hexdigest()==want:
     found=(zpath,member,b);break
 if found:break
assert found,'Matching raw input not located'
zpath,member,b=found
raw=json.loads(b)
stats=dict(n_records=len(raw),n_points=0,edges=0,zero_dt=0,negative_dt=0,gt30=0,same_time_different_position=0,consecutive_duplicate_position=0)
for rid,(t,p) in raw.items():
 assert len(t)==len(p)
 stats['n_points']+=len(p);stats['edges']+=max(0,len(p)-1)
 for i in range(1,len(p)):
  dt=t[i]-t[i-1]
  stats['zero_dt']+=dt==0;stats['negative_dt']+=dt<0;stats['gt30']+=dt>30
  stats['same_time_different_position']+=dt==0 and p[i]!=p[i-1]
  stats['consecutive_duplicate_position']+=p[i]==p[i-1]
pilot=['0','1','2','246','256','306','352']
pilot_stats=[]
for rid in pilot:
 t,p=raw[rid]
 partitions=(1 if t else 0)+sum(b<a or b-a>30 for a,b in zip(t,t[1:]))
 pilot_stats.append({'record_id':rid,'n_points':len(p),'partitions_time_only':partitions,'zero_dt':sum(b==a for a,b in zip(t,t[1:]))})
out['raw_independent_recount']={'raw_sha256':want,'mounted_zip':zpath.name,'zip_member':member,'stats':stats,'pilot':pilot_stats,
 'pilot_points':sum(r['n_points'] for r in pilot_stats),'pilot_partitions':sum(r['partitions_time_only'] for r in pilot_stats),
 'record_352':{'points':len(raw['352'][0]),'distinct_timestamps':len(set(raw['352'][0])),'span_raw':raw['352'][0][-1]-raw['352'][0][0]}}
# Source code positive check: actual pilot profiles agree with separately counted essentials.
profiles=[d.profile(r,raw[r]) for r in pilot]
review=d.independent_profile_review({r:raw[r] for r in pilot},profiles)
assert review['status']=='VERIFIED'
assert sum(x['n_points'] for x in profiles)==out['raw_independent_recount']['pilot_points']==783
assert sum(len(d.time_boundaries(r,raw[r])['partitions']) for r in pilot)==12
out['probes'].append({'id':'P0-positive-raw-profile','status':'PASS','detail':review})

# P1: duplicate detail must not crash on an aligned record with missing time.
fixture=[[None,1],[[0,0],[0,0]]]
profile=d.profile('fixture',fixture)
try:
 result=d.duplicate_details('fixture',fixture)
 entry={'id':'P1-missing-time-duplicate','observed':'RETURNED','result':result}
except Exception as e:
 entry={'id':'P1-missing-time-duplicate','observed':'UNHANDLED_EXCEPTION','exception':type(e).__name__,'message':str(e)}
entry.update(input_source='CONSTRUCTED_FIXTURE',profile_valid_structure=profile['valid_structure'],profile_invalid_timestamps=profile['invalid_timestamps'])
out['probes'].append(entry)

# P2/P3: the lower-level independent checker rejects coverage defects, but
# the public verify/recompute tool normalizes away duplicate or extra rows.
with tempfile.TemporaryDirectory(prefix='g1-audit-fixture-') as tmp:
 path=Path(tmp)/'raw.json'; r={'fixture':[[0,10,20],[[0,0],[1,0],[2,0]]]};write_json(path,r)
 policy={'raw_sha256':digest(path),'semantics_version':'fixture','metrics_version':'fixture',
         'method':{'processing_status':'APPROVED_FOR_REAL_INPUT','blocking_ids':[]}}
 p=d.profile('fixture',r['fixture'],'MOCK_TEST')
 for label,rows in [('duplicate',[copy.deepcopy(p),copy.deepcopy(p)]),
                    ('extra',[copy.deepcopy(p),{**copy.deepcopy(p),'record_id':'foreign'}])]:
  direct=d.independent_profile_review(r,rows)
  for action in ['verify_profiles','recompute_check']:
   with patch.object(tools,'DATA',path):
    tool=tools.execute_tool(action,['fixture'],policy,rows,classification='MOCK_TEST')
   out['probes'].append({'id':f'P2-{label}-{action}','input_source':'CONSTRUCTED_FIXTURE',
      'submitted_rows':len(rows),'expected_records':1,'direct_checker_status':direct['status'],
      'direct_checker_errors':direct['errors'],'tool_status':tool['status'],'tool_result':tool['result']})
 with patch.object(tools,'DATA',path):
  result=tools.execute_tool('baseline',['fixture'],policy,classification='MOCK_TEST')
 out['probes'].append({'id':'P3-approved-config-baseline-stub','input_source':'CONSTRUCTED_FIXTURE',
      'configured_processing_status':policy['method']['processing_status'],'actual_result':result})

# P4: method does not retrieve sources, it echoes the supplied policy; document this
# as a capability boundary, not a false claim that the historical A fabricated evidence.
policy={'raw_sha256':want,'semantics_version':'fixture','metrics_version':'fixture',
        'semantics':{'fixture_only':'NOT_A_SOURCE'},'method':{'blocking_ids':['U01','U02']},
        'starter_reference':{},'teacher_95m':{}}
with tempfile.TemporaryDirectory(prefix='g1-audit-source-') as tmp:
 path=Path(tmp)/'raw.json';path.write_bytes(b)
 with patch.object(tools,'DATA',path):result=tools.execute_tool('source_evidence',pilot,policy,classification='MOCK_TEST')
 out['probes'].append({'id':'P4-source-evidence-contract-echo','input_source':'EXISTING_RAW_PLUS_CONSTRUCTED_POLICY',
   'returned_fixture_policy_without_source_lookup':result['result']['semantics']==policy['semantics']})

(ROOT/'probes/results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
