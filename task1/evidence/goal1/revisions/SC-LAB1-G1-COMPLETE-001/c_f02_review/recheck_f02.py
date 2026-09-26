"""Re-run all original C F02 cases unchanged after the actual repair."""
import importlib.util
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
sys.path.insert(0,str(ROOT))
from task1.workflow.io import read_json,write_json,digest


def main():
    folder=HERE/'round2';folder.mkdir(exist_ok=False)
    spec=importlib.util.spec_from_file_location('c_f02_original',HERE/'probe_f02.py')
    probe=importlib.util.module_from_spec(spec);spec.loader.exec_module(probe)
    probe.HERE=folder
    probe.main()
    result=read_json(folder/'initial_results.json')
    passed=(result['status']=='VERIFIED' and result['source_stable'] and result['trusted_handle_unchanged']
            and result['production_runner_calls']==0 and len(result['cases'])==37)
    report={'classification':'ENGINEERING_TEST','scope':'C2-F02_TRUST_BOUNDARY_NOT_REAL_PILOT_OR_GOAL_ACCEPTANCE',
            'issues':{'C2-F02':{'status':'VERIFIED' if passed else 'REJECTED',
                'checked':[r['case'] for r in result['cases']], 'source_hashes':result['source_hashes_after'],
                'failed':[r for r in result['cases'] if r['expected']!=r['actual']],
                'evidence':'initial_results.json','original_probe_sha256':digest(HERE/'probe_f02.py'),
                'initial_rejection_preserved':'../initial_review.json',
                'reference_reader_evidence':'../registered_reference_check.json',
                'production_runner_calls':result['production_runner_calls'],
                'trusted_handle_unchanged':result['trusted_handle_unchanged'],
                'adaptation':'Only output directory changed; the original 37 cases and expectations are unchanged.'}}}
    write_json(folder/'review_receipt.json',report,exclusive=True)
    print('C2-F02 '+report['issues']['C2-F02']['status']+'; 37 original cases; producer calls 0; source hashes stable='+str(result['source_stable']))


if __name__=='__main__':main()
