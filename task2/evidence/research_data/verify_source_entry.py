"""Exercise public-clone fallback in a temporary isolated directory."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'task2/src'))
import dispatch_data as d


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    repo=d.ROOT
    teacher=repo/'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_NYC.csv'
    original_hash=sha(teacher)
    baseline=d.load_data()
    before={'trips':len(baseline.trips),'partitions':{k:v['rows'] for k,v in baseline.audit['split'].items()}}
    with tempfile.TemporaryDirectory(prefix='sc_dispatch_source_entry_') as directory:
        isolated=Path(directory)
        fallback=isolated/'task2/teacher_materials/author_original/public_conversion'
        fallback.mkdir(parents=True)
        for city in ['NYC','TKY']:
            name=f'dataset_TSMC2014_{city}.csv'
            shutil.copyfile(repo/'task2/teacher_materials/author_fetch_reproduction'/name,fallback/name)
        try:
            d.ROOT=isolated
            public=d.load_data()
            assert public.audit['source_identity']=='AUTHOR_RECONSTRUCTED'
            assert public.audit['teacher_byte_identity'] is False
            assert len(public.trips)==25550
            assert {k:v['rows'] for k,v in public.audit['split'].items()}==before['partitions']
            identity=['origin_source_row','destination_source_row','date','minute']
            assert public.trips[identity].equals(baseline.trips[identity])
            fallback_result={'source_identity':public.audit['source_identity'],'teacher_byte_identity':False,
                'resolved_path':public.audit['path'],'sha256':public.audit['sha256'],
                'all_trip_source_pairs_dates_minutes_equal':True,'partition_counts_equal':True}
            target=isolated/'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_NYC.csv'
            target.parent.mkdir(parents=True)
            shutil.copyfile(teacher,target)
            assert d.source_path()==target
            preferred=d.load_data()
            assert preferred.audit['source_identity']=='TEACHER_PROVIDED' and preferred.audit['teacher_byte_identity']
        finally:
            d.ROOT=repo
    assert sha(teacher)==original_hash
    result={'status':'PASS','reviewer':'/root/research_data','baseline':before,'fallback':fallback_result,
            'teacher_priority_checked':True,'original_teacher_sha256_unchanged':original_hash,
            'data_code_sha256':sha(repo/'task2/src/dispatch_data.py'),
            'scope':'identity/path only; filtering, temporal split, geometry and current teacher input remain unchanged; active RL CSV inputs untouched'}
    (Path(__file__).parent/'source_entry_regression.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
