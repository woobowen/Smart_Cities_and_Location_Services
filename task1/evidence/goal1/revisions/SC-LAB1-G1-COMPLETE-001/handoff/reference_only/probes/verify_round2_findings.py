"""Offline audit probes. Only constructed inputs; no model/network calls.

Run against a checkout using --repo. Default: accompanying verified source snapshot.
No production files or historical result artifacts are changed.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

EXPECTED = {
    'diagnostics.py': '9ff8ea95c016f83f808d7a5f5f2821a19c4eb094',
    'evaluation.py': '206bb5a5b26db10a80cfb6853dce5faf56c569ed',
    'tools.py': '08af4334ddf51059deadce86135c51641cb2733c',
    'io.py': '25ac484dcfcf376d0f8a9e760eec565a7857749a',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1]/'source_snapshot')
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    root=args.repo.resolve()
    versions={}
    for name, expected in EXPECTED.items():
        data=(root/'task1/workflow'/name).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        versions[name]={'git_blob':blob,'expected_at_7e6cd408':expected,'matches_audited_commit':blob==expected,
                        'sha256':hashlib.sha256(data).hexdigest()}
    sys.path.insert(0,str(root))
    ev=importlib.import_module('task1.workflow.evaluation')
    di=importlib.import_module('task1.workflow.diagnostics')
    tools=importlib.import_module('task1.workflow.tools')

    source={'record_id':'fixture:review','indices':[0,1,2,3],
            'timestamps':[0,1,2,3],'xy':[[0,0],[1,0],[2,0],[3,0]]}
    clean=deepcopy(source)
    final={'record_id':source['record_id'],'indices':[0,3],
           'timestamps':[0,3],'xy':[[0,0],[3,0]]}
    parameters={'dt':30,'distance':10,'min_points':3,'min_length':0,
                'direction':35,'dp':1,'time_reliable':True}
    ledger=[{'record_id':source['record_id'],'original_index':i,
             'action':'retained' if i in (0,3) else 'simplified',
             'timestamp':source['timestamps'][i],'xy':deepcopy(source['xy'][i])} for i in range(4)]
    baseline={'status':'VERIFIED','classification':'CONSTRUCTED_FIXTURE',
              'parameters':parameters,'input_hash':'CONSTRUCTED_FIXTURE_NOT_TEACHER_INPUT',
              'records':[{'record_id':source['record_id'],'boundaries':[], 'filtered_segments':[],
                          'processed_segments':[{'segment_index':0,'input':deepcopy(source),
                            'denoise':{'record':clean,'deleted_indices':[]},'output':final}]}],
              'point_actions':ledger,'stage_counts':{'input':4,'segmented':1,'filtered':0,
                            'denoised':0,'simplified':2,'retained':2,'not_processed':0},
              'modified_values':0,'quality_status':'PENDING_RESEARCH_REVIEW'}
    cases={'valid_control':deepcopy(baseline)}
    altered=deepcopy(baseline);altered['records'][0]['processed_segments'][0]['output']['xy'][0][0]=999
    cases['only_final_coordinate_modified']=altered
    shifted=deepcopy(baseline)
    for record in (shifted['records'][0]['processed_segments'][0]['denoise']['record'],
                   shifted['records'][0]['processed_segments'][0]['output']):
        record['xy']=[[x+1000,y+1000] for x,y in record['xy']]
    cases['clean_and_final_shifted_ledger_unchanged']=shifted
    dropped=deepcopy(baseline);dropped['records']=[];dropped['point_actions']=[]
    cases['all_records_and_ledger_dropped_counts_unchanged']=dropped
    counts=deepcopy(baseline);counts['stage_counts'].update(input=999,retained=999)
    cases['stage_counts_modified']=counts
    probes=[]
    for name,candidate in cases.items():
        result=ev.review_baseline(candidate)
        probes.append({'case':name,'expected_for_trusted_complete_review':
                       'VERIFIED' if name=='valid_control' else 'REJECTED',
                       'actual':result,'submitted_stage_counts':candidate['stage_counts']})

    # Former F01: exercise the actual tool boundary with a temporary fixture file.
    fixture={'fixture:a':[[0,0,10],[[0,0],[1,0],[2,0]]],
             'fixture:b':[[0,40],[[0,0],[1,1]]]}
    profile_rows=[di.profile(k,v,'ENGINEERING_TEST') for k,v in fixture.items()]
    inputs={'normal':deepcopy(profile_rows),'legally_reordered':deepcopy(profile_rows[::-1]),
            'duplicate_id':deepcopy(profile_rows+[profile_rows[0]]),
            'missing_id':deepcopy(profile_rows[:1])}
    foreign=deepcopy(profile_rows[0]);foreign['record_id']='fixture:foreign'
    inputs['foreign_id']=deepcopy(profile_rows)+[foreign]
    tool_results=[]
    with tempfile.TemporaryDirectory(prefix='sc-g1-audit2-') as temp:
        path=Path(temp)/'raw.json';path.write_text(json.dumps(fixture))
        policy={'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'semantics_version':'ENGINEERING_TEST','metrics_version':'ENGINEERING_TEST'}
        with patch.object(tools,'DATA',path):
            for name,rows in inputs.items():
                for action in ('verify_profiles','recompute_check'):
                    result=tools.execute_tool(action,list(fixture),policy,rows,classification='ENGINEERING_TEST')
                    tool_results.append({'case':name,'action':action,'status':result['status'],
                                         'result':result['result']})
            result=tools.execute_tool('verify_baseline',list(fixture),policy,
                        classification='ENGINEERING_TEST',previous_baseline=shifted)
            probes.append({'case':'verify_baseline_tool_different_raw_records_and_shifted_candidate',
                           'expected_for_trusted_complete_review':'REJECTED','actual':result})
    missing_time=di.duplicate_details('fixture:missing',[[None,1],[[0,0],[0,0]]])
    out={'audit_target':'7e6cd4082c2cdad2452fa5a1006e99dcfb050d17',
         'at':datetime.now(timezone.utc).isoformat(),'classification':'ENGINEERING_TEST',
         'input_source':'CONSTRUCTED_FIXTURE','live_model_calls':0,'repository_modified':False,
         'source_versions':versions,'baseline_review_probes':probes,
         'previous_F01_regression':tool_results,'previous_missing_timestamp_regression':missing_time,
         'interpretation':'Failed challenge cases show reviewer capability gaps, not corruption of published real pilot data.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'source_exact':all(v['matches_audited_commit'] for v in versions.values()),
          'review_cases':[(p['case'],p['actual']['status']) for p in probes],
          'F01_cases':[(p['case'],p['action'],p['status']) for p in tool_results],
          'missing_time':missing_time,'output':str(args.output)},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
