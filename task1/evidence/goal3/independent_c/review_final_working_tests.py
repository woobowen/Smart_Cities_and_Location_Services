"""Review recorded full regression evidence and its current source bindings."""
import ast
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[4]
EV=ROOT/'task1/evidence/goal3'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())


def main():
    rp=EV/'full_working_tests_final_receipt.json';reported=read(rp)
    xp=EV/'full_working_tests_final.xml'
    assert reported['status']=='VERIFIED' and sha(xp)==reported['junit_sha256']
    xml=ET.parse(xp);cases=xml.findall('.//testcase');suites=xml.findall('.//testsuite')
    assert all(int(s.get(k))==0 for s in suites for k in ['failures','errors','skipped'])
    assert all(not list(c) for c in cases)
    total=sum(int(s.get('tests')) for s in suites)
    assert len(cases)==reported['test_cases']==469
    assert total==reported['junit_counts']['tests']==479
    assert total-len(cases)==reported['passed_subtests']==10
    sources={**reported['processing_source_hashes'],**reported['auxiliary_source_hashes']}
    frozen=read(EV/'production_freeze.json')
    assert reported['processing_source_hashes']==frozen['processing_source_hashes']
    for name,h in sources.items():assert sha(ROOT/name)==h,name
    test_files={};classes=Counter()
    for case in cases:
        module=case.get('classname');parts=module.split('.')
        while parts and not (ROOT/Path(*parts).with_suffix('.py')).is_file():parts.pop()
        assert parts,('NO_CURRENT_TEST_SOURCE',module)
        path=ROOT/Path(*parts).with_suffix('.py')
        if path not in test_files:
            tree=ast.parse(path.read_text())
            test_files[path]={node.name for node in ast.walk(tree) if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
        assert case.get('name').split('[',1)[0] in test_files[path]
        classes[module]+=1
    boundary=ROOT/reported['additional_actual_independent_challenges']
    assert sha(boundary)==reported['new_information_boundary_test_sha256']
    matching=[c for c in cases if c.get('classname').endswith('test_final_information_boundaries')]
    assert len(matching)==4
    preparation=read(EV/'independent_c/final_acceptance_preparation_post_NB01.json')
    assert preparation['working_tests']['junit_sha256']==sha(xp)
    for p in test_files:sources[str(p.relative_to(ROOT))]=sha(p)
    targets=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [rp,xp,boundary,
        EV/'independent_c/final_information_boundaries_receipt.json']]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':'current_final_working_test_evidence',
        'at':datetime.now(timezone.utc).isoformat(),'targets':targets,'source_hashes':sources,
        'checked_components':['Recorded JUnit file byte hash and every actual testcase node checked; no failure/error/skip',
            '469 ordinary testcase nodes and479 suite total accurately distinguished;10 passed subtests contribute to suite total',
            'Every JUnit case maps to a present actual Python test definition; all current tested processing and auxiliary sources match recorded hashes',
            'Required tamper/scope/reference/freeze/repair/mode/memory/portable boundaries mapped to actual passing tests',
            'Four explicit identifier/final-feedback routing and selection/final-memory rejection challenges included in the current full run'],
        'unchecked_components':['No additional pytest or numerical run by this reviewer; actual recorded regression is reviewed',
            'Tests cannot replace real full Notebook/ZIP execution, report visual review or publication verification'],
        'testcase_nodes':len(cases),'suite_total_including_subtests':total,'passed_subtests':10,
        'classes':dict(classes),'required_topic_coverage':preparation['working_tests']['topic_coverage'],
        'processing_source_file_count':len(reported['processing_source_hashes']),
        'test_source_file_count':len(test_files),'test_counts_are_not_method_experiment_counts':True,
        'new_model_calls':0,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_final_working_tests.py'}
    output=EV/'independent_c/final_working_tests_review.json'
    with output.open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'status':'VERIFIED','testcase_nodes':len(cases),'suite_total':total,'test_files':len(test_files),'sha256':sha(output)}))


if __name__=='__main__':main()
