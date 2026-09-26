"""Raw structural inspection only. Does not assign a CRS or repair any data."""
from __future__ import annotations

from collections import Counter
import math


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def profile(record_id, value, classification='CURRENT_RUN_REAL_DATA'):
    result = {'record_id': str(record_id), 'classification': classification,
              'valid_structure': False, 'n_points': 0, 'n_timestamps': 0,
              'invalid_timestamps': 0, 'invalid_coordinates': 0,
              'negative_dt': 0, 'zero_dt': 0, 'positive_dt': 0,
              'same_time_different_position': 0, 'consecutive_duplicate_position': 0,
              'long_gap_gt_30_source_seconds': 0, 'edges_total': 0,
              'dt_computable': 0, 'position_pairs_computable': 0,
              'time_span_raw': None, 'dt_min_raw': None, 'dt_max_raw': None,
              'dt_counts': {}, 'issues': []}
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(x, list) for x in value):
        result['issues'].append('EXPECTED_TWO_ARRAYS')
        return result
    ts, coords = value
    result.update(n_points=len(coords), n_timestamps=len(ts), edges_total=max(0, len(coords)-1))
    result['valid_structure'] = len(ts) == len(coords)
    if len(ts) != len(coords):
        result['issues'].append('ALIGNMENT_MISMATCH')
    good_coords = [isinstance(p, list) and len(p) == 2 and all(finite(x) for x in p) for p in coords]
    result['invalid_timestamps'] = sum(not finite(t) for t in ts)
    result['invalid_coordinates'] = sum(not good for good in good_coords)
    if result['invalid_timestamps']:
        result['issues'].append('NONFINITE_TIME')
    if result['invalid_coordinates']:
        result['issues'].append('NONFINITE_OR_NON2D_COORDINATE')
    counts = Counter()
    for i in range(1, len(ts)):
        if finite(ts[i]) and finite(ts[i-1]):
            dt = ts[i]-ts[i-1]
            counts[str(dt)] += 1
            result['dt_computable'] += 1
            result['negative_dt' if dt < 0 else 'zero_dt' if dt == 0 else 'positive_dt'] += 1
            result['long_gap_gt_30_source_seconds'] += int(dt > 30)
            if dt == 0 and i < len(coords) and good_coords[i] and good_coords[i-1] and coords[i] != coords[i-1]:
                result['same_time_different_position'] += 1
    for i in range(1, len(coords)):
        if good_coords[i] and good_coords[i-1]:
            result['position_pairs_computable'] += 1
            result['consecutive_duplicate_position'] += int(coords[i] == coords[i-1])
    if ts and finite(ts[0]) and finite(ts[-1]):
        result['time_span_raw'] = ts[-1]-ts[0]
    if counts:
        result['dt_min_raw'] = min(float(x) for x in counts)
        result['dt_max_raw'] = max(float(x) for x in counts)
    result['dt_counts'] = dict(counts)
    return result


def aggregate(profiles):
    fields = ['n_points','n_timestamps','invalid_timestamps','invalid_coordinates',
              'negative_dt','zero_dt','positive_dt','same_time_different_position',
              'consecutive_duplicate_position','long_gap_gt_30_source_seconds',
              'edges_total','dt_computable','position_pairs_computable']
    totals = {k: sum(p[k] for p in profiles) for k in fields}
    counts = Counter()
    for p in profiles:
        counts.update(p['dt_counts'])
    return {'n_records':len(profiles), 'valid_structure_records':sum(p['valid_structure'] for p in profiles),
            **totals, 'dt_counts':dict(sorted(counts.items(), key=lambda x:float(x[0]))),
            'point_count_min':min((p['n_points'] for p in profiles), default=None),
            'point_count_max':max((p['n_points'] for p in profiles), default=None),
            'modifications':0, 'physical_distance':{'value':None,'reason':'CRS_AND_DISTANCE_POLICY_UNRESOLVED'}}


def time_boundaries(record_id, value, threshold=30, classification='CURRENT_RUN_REAL_DATA'):
    """Diagnostic partition, not complete time+space segmentation or filtering."""
    p = profile(record_id,value)
    if not p['valid_structure'] or p['invalid_timestamps']:
        return {'record_id':record_id,'status':'BLOCKED','reason':'INVALID_TIMELINE_STRUCTURE'}
    ts, coords = value
    cuts = [{'right_index':i,'left_index':i-1,'dt':ts[i]-ts[i-1],
             'reasons':['NEGATIVE_DT' if ts[i] < ts[i-1] else 'GAP_GT_THRESHOLD']}
            for i in range(1,len(ts)) if ts[i] < ts[i-1] or ts[i]-ts[i-1] > threshold]
    bounds = [0]+[x['right_index'] for x in cuts]+[len(ts)]
    partitions = [list(range(a,b)) for a,b in zip(bounds,bounds[1:]) if a < b]
    return {'record_id':record_id,'status':'EXECUTED','classification':classification,
            'threshold_source_seconds':threshold,'cuts':cuts,'partitions':partitions,
            'n_input':len(coords),'n_accounted':sum(map(len,partitions)),'deleted':0,'modified':0,
            'limitation':'TIME_ONLY; space cuts, length filtering, denoising and DP remain BLOCKED'}


def duplicate_details(record_id, value):
    p = profile(record_id,value)
    if not p['valid_structure']:
        return {'record_id':record_id,'status':'BLOCKED','reason':'INVALID_STRUCTURE'}
    ts,coords=value
    events=[]
    for i in range(1,len(ts)):
        tags=[]
        if coords[i] == coords[i-1]:
            tags.append('REPEATED_POSITION_NOT_AUTOMATIC_NOISE')
        if ts[i] == ts[i-1]:
            tags.append('ZERO_DT_SPEED_UNAVAILABLE')
            if coords[i] != coords[i-1]:
                tags.append('SAME_TIME_DIFFERENT_POSITION')
        if tags:
            events.append({'left_index':i-1,'right_index':i,'dt_raw':ts[i]-ts[i-1], 'reasons':tags})
    return {'record_id':record_id,'events':events,'modified':0,'deleted':0,'status':'EXECUTED'}


def independent_profile_review(raw, rows):
    """Second implementation, direct counts, not a call to profile/aggregate."""
    errors=[]
    if len(rows)!=len(raw) or len({p.get('record_id') for p in rows})!=len(rows):
        errors.append('RECORD_COVERAGE')
    for row in rows:
        rid=row.get('record_id')
        if rid not in raw:
            errors.append(f'UNKNOWN_RECORD:{rid}');continue
        value=raw[rid]
        if not isinstance(value,list) or len(value)!=2 or not all(isinstance(x,list) for x in value):
            if row.get('valid_structure') is not False:
                errors.append(f'STRUCTURE:{rid}')
            continue
        t,c=value
        coordinate_valid=[isinstance(p,list) and len(p)==2 and all(finite(v) for v in p) for p in c]
        expected={'n_points':len(c),'n_timestamps':len(t),'valid_structure':len(t)==len(c),
                  'negative_dt':0,'zero_dt':0,'positive_dt':0,'dt_computable':0,
                  'same_time_different_position':0,'consecutive_duplicate_position':0,
                  'long_gap_gt_30_source_seconds':0,'edges_total':max(len(c)-1,0),
                  'invalid_timestamps':sum(not finite(v) for v in t),
                  'invalid_coordinates':len(c)-sum(coordinate_valid),
                  'position_pairs_computable':sum(a and b for a,b in zip(coordinate_valid,coordinate_valid[1:])),
                  'time_span_raw':t[-1]-t[0] if t and finite(t[0]) and finite(t[-1]) else None,
                  'dt_counts':{}}
        deltas=[]
        for j,(a,b) in enumerate(zip(t,t[1:]),1):
            if not(finite(a) and finite(b)):continue
            expected['dt_computable']+=1
            delta=b-a;deltas.append(delta)
            key=str(delta);expected['dt_counts'][key]=expected['dt_counts'].get(key,0)+1
            expected['zero_dt']+=int(a==b);expected['negative_dt']+=int(b<a);expected['positive_dt']+=int(b>a)
            expected['long_gap_gt_30_source_seconds']+=int(b-a>30)
            if j < len(c) and a==b and c[j]!=c[j-1] and all(isinstance(x,list) and len(x)==2 and all(finite(v) for v in x) for x in c[j-1:j+1]):
                expected['same_time_different_position']+=1
        expected['consecutive_duplicate_position']=sum(a==b for a,b in zip(c,c[1:]) if all(isinstance(x,list) and len(x)==2 and all(finite(v) for v in x) for x in [a,b]))
        expected['dt_min_raw']=float(min(deltas)) if deltas else None
        expected['dt_max_raw']=float(max(deltas)) if deltas else None
        expected['issues']=(['ALIGNMENT_MISMATCH'] if len(t)!=len(c) else [])
        if expected['invalid_timestamps']:expected['issues'].append('NONFINITE_TIME')
        if expected['invalid_coordinates']:expected['issues'].append('NONFINITE_OR_NON2D_COORDINATE')
        for k,v in expected.items():
            if row.get(k)!=v:errors.append(f'{rid}:{k}')
    return {'status':'VERIFIED' if not errors else 'REJECTED','errors':errors,'records_checked':len(rows),
            'claim':'Structural counts only; no physical accuracy or cleaning quality claim'}
