#!/usr/bin/env python3
"""Reproduce the GPT G1 review's boundary probes on an explicitly selected repo.

This is an ENGINEERING_TEST. It never calls a model or starts Codex. Temporary
raw records and injected process failures are fixtures, not real task results.
Use before/after fixes; the output is observational, not a project PASS verdict.
"""
import argparse
import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    repo=args.repo.resolve()
    if not (repo/'task1/workflow/tools.py').is_file():
        p.error('Expected the actual repository containing task1/workflow/tools.py')
    if args.output.exists():
        p.error('Output exists; use a new before/after filename to preserve evidence')
    sys.path.insert(0,str(repo))
    d=importlib.import_module('task1.workflow.diagnostics')
    tools=importlib.import_module('task1.workflow.tools')
    prov=importlib.import_module('task1.workflow.provider')
    io=importlib.import_module('task1.workflow.io')
    for mod in (d,tools,prov,io):
        if not Path(mod.__file__).resolve().is_relative_to(repo):
            raise RuntimeError('Wrong module import root')
    try:
        sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    except (OSError,subprocess.CalledProcessError):
        sha='unavailable'
    results={'classification':'ENGINEERING_TEST','network_calls':0,'model_calls':0,
             'review_target':str(repo),'checked_commit':sha,'probes':[]}
    # Never permit the real external process helper to run.
    with patch.object(prov,'run_limited',side_effect=AssertionError('LIVE_DISABLED_IN_REVIEW_PROBE')):
        fixture=[[None,1],[[0,0],[0,0]]]
        try:
            result=d.duplicate_details('fixture',fixture)
            results['probes'].append({'id':'MISSING_TIME_DUPLICATE','returned':result})
        except Exception as exc:
            results['probes'].append({'id':'MISSING_TIME_DUPLICATE','exception':type(exc).__name__,'message':str(exc)})
        with tempfile.TemporaryDirectory(prefix='g1-review-fixture-') as tmp:
            raw={'fixture':[[0,10,20],[[0,0],[1,0],[2,0]]]}
            path=Path(tmp)/'raw.json';io.write_json(path,raw)
            policy={'raw_sha256':io.digest(path),'semantics_version':'fixture','metrics_version':'fixture'}
            good=d.profile('fixture',raw['fixture'],'MOCK_TEST')
            variants={'duplicate':[copy.deepcopy(good),copy.deepcopy(good)],
                      'foreign':[copy.deepcopy(good),{**copy.deepcopy(good),'record_id':'foreign'}],
                      'valid':[copy.deepcopy(good)]}
            for name,rows in variants.items():
                for action in ('verify_profiles','recompute_check'):
                    try:
                        with patch.object(tools,'DATA',path):
                            answer=tools.execute_tool(action,['fixture'],policy,rows,classification='MOCK_TEST')
                        results['probes'].append({'id':name+'_'+action,'status':answer.get('status'),'result':answer})
                    except Exception as exc:
                        results['probes'].append({'id':name+'_'+action,'exception':type(exc).__name__,'message':str(exc)})
        try:
            answer=prov.visible_events('{"type":"item.started","item":null}')
            results['probes'].append({'id':'NULL_ITEM','result':answer})
        except Exception as exc:
            results['probes'].append({'id':'NULL_ITEM','exception':type(exc).__name__,
               'normalized_provider_error':isinstance(exc,prov.ProviderError)})
        errors={'SPAWN_FAILURE':OSError('ENGINEERING_TEST_SPAWN_FAILURE'),
                'TIMEOUT_WITH_PARTIAL_LOG':subprocess.TimeoutExpired('ENGINEERING_TEST',.01,
                    output='{"type":"thread.started","thread_id":"fixture"}\n',stderr='fixture partial stderr')}
        for name,error in errors.items():
            with tempfile.TemporaryDirectory(prefix='g1-provider-fixture-') as tmp:
                provider=prov.CodexProvider();provider.executable='/never-executed-review-fixture'
                with patch.object(prov,'run_limited',side_effect=error):
                    try:
                        provider.call('research','fixture','fixture',['source_evidence'],tmp)
                        result={'id':name,'unexpected_success':True}
                    except Exception as exc:
                        result={'id':name,'exception':type(exc).__name__,
                                'normalized_provider_error':isinstance(exc,prov.ProviderError)}
                result['saved_files']=sorted(x.name for x in Path(tmp).iterdir())
                rp=Path(tmp)/'receipt.json'
                result['receipt']=json.loads(rp.read_text()) if rp.exists() else None
                results['probes'].append(result)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8') as f:
        json.dump(results,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps(results,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
