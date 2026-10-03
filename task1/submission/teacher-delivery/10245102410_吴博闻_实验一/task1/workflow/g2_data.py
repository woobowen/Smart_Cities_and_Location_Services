"""Goal 2 descriptive record split and conditional coordinates, without cleaning."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import math
import numpy as np

from .io import DATA, ROOT, digest, object_hash, read_json, write_json, now
from .coordinates import conditional_contract, working_xy

PILOT = ['0', '1', '2', '246', '256', '306', '352']
EXPECTED_RAW = 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'


def raw_data():
    if digest(DATA) != EXPECTED_RAW:
        raise ValueError('RAW_HASH_MISMATCH')
    return read_json(DATA)


def model():
    value = deepcopy(conditional_contract()['analysis_model'])
    # Same mathematical mapping as G1. A/C review registers the larger input
    # guard separately; it is not an assertion of source datum or ground accuracy.
    value['domain_max_radius_m'] = 200000.0
    return value


def adapt(record_id, raw_record):
    times, coordinates = raw_record
    if len(times) != len(coordinates):
        raise ValueError('RAW_ALIGNMENT_MISMATCH')
    return {'record_id':str(record_id), 'indices':list(range(len(times))),
            'timestamps':deepcopy(times), 'xy':working_xy(coordinates, model())}


def describe(record_id, raw_record):
    r = adapt(record_id, raw_record)
    xy = np.asarray(r['xy'], dtype=float)
    t = np.asarray(r['timestamps'], dtype=float)
    delta = np.diff(t)
    distances = np.hypot(*np.diff(xy, axis=0).T)
    directions_valid = distances > 0
    return {'record_id':str(record_id), 'n_points':len(t),
            'span_work_m':float(np.hypot(*np.ptp(xy, axis=0))),
            'duration_seconds':float(t[-1]-t[0]),
            'path_length_work_m':float(distances.sum()),
            'max_radius_work_m':float(np.hypot(*xy.T).max()),
            'zero_dt_edges':int((delta == 0).sum()),
            'negative_dt_edges':int((delta < 0).sum()),
            'median_positive_dt':None if not np.any(delta>0) else float(np.median(delta[delta>0])),
            'dt_over_30_edges':int((delta > 30).sum()),
            'distance_over_400_edges':int((distances > 400).sum()),
            'raw_break_edges':int(((delta>30)|(delta<0)|(distances>400)).sum()),
            'adjacent_duplicate_edges':sum(a == b for a,b in zip(raw_record[1], raw_record[1][1:])),
            'direction_unavailable_edges':int((~directions_valid).sum()),
            'speed_unavailable_edges':int((delta <= 0).sum()),
            'time_flag':bool(np.any((delta <= 0) | (delta > 30))),
            'duplicate_flag':any(a == b for a,b in zip(raw_record[1], raw_record[1][1:])),
            'record_content_sha256':object_hash(raw_record)}


def rank(record_id, purpose):
    return hashlib.sha256(('42|'+purpose+'|'+str(record_id)).encode()).hexdigest()


def balanced_take(available, count, strata, purpose):
    """Equal descriptive-stratum allocation with deterministic shortage fill.

    Exact duplicate groups are checked before this function: current raw has none.
    A future dataset with duplicates must use an explicitly reviewed grouped rule.
    """
    buckets = defaultdict(list)
    for rid in available:
        buckets[strata[rid]].append(rid)
    for s in buckets:
        buckets[s].sort(key=lambda rid:(rank(rid,purpose),rid))
    names = sorted(buckets)
    if sum(map(len,buckets.values())) < count:
        raise ValueError('INSUFFICIENT_RECORDS')
    quota = {s:count//len(names)+(i<count%len(names)) for i,s in enumerate(names)}
    selected=[];shortfalls={}
    for s in names:
        take=min(quota[s],len(buckets[s]));selected.extend(buckets[s][:take])
        buckets[s]=buckets[s][take:]
        if take<quota[s]:shortfalls[s]=quota[s]-take
    while len(selected)<count:
        for s in names:
            if buckets[s]:selected.append(buckets[s].pop(0))
            if len(selected)==count:break
    return selected, {'nominal_quota':quota,'shortfalls':shortfalls,
                      'realized':dict(Counter(strata[x] for x in selected))}


def make_split(output_dir):
    output_dir.mkdir(parents=True,exist_ok=True)
    if (output_dir/'split_manifest.json').exists():
        raise ValueError('SPLIT_ALREADY_FROZEN')
    raw=raw_data(); cards={rid:describe(rid,r) for rid,r in raw.items()}
    groups=defaultdict(list)
    for rid,c in cards.items():groups[c['record_content_sha256']].append(rid)
    duplicates=[v for v in groups.values() if len(v)>1]
    if duplicates:
        write_json(output_dir/'duplicate_groups.json',duplicates)
        raise ValueError('GROUPED_REALLOCATION_REQUIRES_REVIEW; no records selected')
    q=np.quantile([c['span_work_m'] for c in cards.values()],[1/3,2/3],method='linear')
    strata={}
    for rid,c in cards.items():
        level='LOW' if c['span_work_m']<=q[0] else ('MID' if c['span_work_m']<=q[1] else 'HIGH')
        strata[rid]=f'{level}_T{int(c["time_flag"])}_D{int(c["duplicate_flag"])}'
        c['stratum']=strata[rid]
        c['exposure']='EXPOSED_G1_PILOT' if rid in PILOT else 'PRIOR_FULL_READONLY_INVENTORY; other historical method exposure not proven absent'
    available=set(raw)-set(PILOT);splits={'PILOT_REGRESSION':PILOT};allocation={}
    for name,count in [('DEMO_MEMORY',60),('DEVELOPMENT',120),('G2_EVAL',120)]:
        ids,info=balanced_take(available,count,strata,name)
        splits[name]=ids;allocation[name]=info;available-=set(ids)
    splits['G3_RESERVED']=sorted(available,key=lambda x:(rank(x,'reserved'),x))
    subsets={}
    for name in ('DEVELOPMENT','G2_EVAL'):
        ids,info=balanced_take(splits[name],24,strata,name+'_LLM')
        subsets[name]=ids;allocation[name+'_LLM']=info
    write_json(output_dir/'raw_diagnostics.json',cards)
    result={'goal_id':'SC-LAB1-G2-EXPERIMENTS-001','frozen_at':now(),
            'classification':'FULL_RAW_READONLY_DESCRIPTIVE_INVENTORY; not a cleaning run',
            'raw_sha256':EXPECTED_RAW,'raw_records':len(raw),'raw_points':sum(c['n_points'] for c in cards.values()),
            'seed':42,'algorithm':'sha256(42|purpose|record_id), equal extant strata, sorted-stratum round-robin shortage fill',
            'grouping':'complete raw record canonical SHA256; no exact duplicate groups found; no independently verified higher entity',
            'quantiles':q.tolist(),'stratum_definition':'ENU bbox diagonal tertiles x any(dt<=0 or dt>30) x adjacent exact coordinate duplicate',
            'population_strata':dict(Counter(strata.values())),
            'sample_weighting':'stratified record means, not population means',
            'splits':splits,'llm_subsets':subsets,'allocation':allocation,
            'diagnostics_sha256':digest(output_dir/'raw_diagnostics.json'),
            'source_sha256':digest(__file__),'source_crs':'UNVERIFIED'}
    write_json(output_dir/'split_manifest.json',result,exclusive=True)
    return result
