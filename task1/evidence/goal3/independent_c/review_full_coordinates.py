"""C audit of completed coordinate outputs: full scope plus independent sensitivity sample.

Full mathematical S/D/P recomputation is deliberately not claimed. Independent
sensitivity covers frozen random/category records and every reported difference
or stage-extreme record, while all points, raw edges and stage denominators are checked.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import pyproj

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from task1.evidence.goal2.c_contract.independent_numeric import directions, finite_distance, allowance

EV=ROOT/'task1/evidence/goal3'
OUT=EV/'independent_c'


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def key(row):
    return (row['kind'],row['record_id'],row['config_id'],row['stage_position'],
            row['input_segment_id'],tuple(row['input_indices']),row.get('original_index'),
            row.get('left_index'),row.get('right_index'),tuple(row.get('segment_indices',[])))


def distance(point,start,end):
    # Own binary64 implementation for the alternate algorithm's deterministic tie domain.
    x,y=point; a,b=start; dx,dy=end[0]-a,end[1]-b
    length=math.hypot(dx,dy)
    u=min(1.,max(0.,((x-a)*dx+(y-b)*dy)/(length*length))) if length else 0.
    return math.hypot(x-a-u*dx,y-b-u*dy)


def alternate_dp(points,ids,tolerance):
    if len(ids)<=2 or tolerance==0:return list(ids)
    errors=[distance(points[i],points[ids[0]],points[ids[-1]]) for i in ids[1:-1]]
    maximum=max(errors)
    if maximum<=tolerance:return [ids[0],ids[-1]]
    pivot=errors.index(maximum)+1
    return alternate_dp(points,ids[:pivot+1],tolerance)[:-1]+alternate_dp(points,ids[pivot:],tolerance)


def stage_counts(trace):
    c=Counter()
    for stage in trace['stages']:
        if stage['name']=='S':
            c['S_distance_edges']+=sum(max(0,len(s['indices'])-1) for s in stage['input'])
            c['S_actual_segments_length']+=sum(len(op['segments']) for op in stage['operations'])
        elif stage['name']=='D':
            c['D_windows']+=sum(len(s['indices']) for s in stage['input'])
            c['D_undefined_windows']+=sum(v['reason'] is not None for op in stage['operations'] for v in op['decisions'])
        else:
            c['P_complete_input_points']+=sum(len(s['indices']) for s in stage['input'])
            c['P_immediate_output_points']+=sum(len(s['indices']) for s in stage['output'])
            c['P_segments']+=len(stage['input'])
    return c


def sensitivity(trace,cfg,raw,alt,geod):
    """Separate C implementation; does not import B's sensitivity helper."""
    rid=trace['record_id'];p=trace['parameters'];enu=trace['source_record']['xy'];times,ll=raw
    events=[]
    def emit(kind,stage,segment,**fields):
        events.append({'kind':kind,'record_id':rid,'config_id':cfg,'stage_position':stage['position'],
            'input_segment_id':segment['segment_id'],'input_indices':segment['indices'],**fields})
    for stage in trace['stages']:
        for j,(segment,op) in enumerate(zip(stage['input'],stage['operations'])):
            ids=segment['indices']
            if stage['name']=='S':
                for a,b in zip(ids,ids[1:]):
                    values=[math.dist(enu[a],enu[b]),math.dist(alt[a],alt[b]),geod.inv(*ll[a],*ll[b])[2]]
                    if len({v>p['distance'] for v in values})>1:
                        emit('S_DISTANCE_THRESHOLD',stage,segment,left_index=a,right_index=b)
                for part in op['segments']:
                    group=part['indices']
                    values=[math.fsum(math.dist(xy[a],xy[b]) for a,b in zip(group,group[1:])) for xy in (enu,alt)]
                    values.append(math.fsum(geod.inv(*ll[a],*ll[b])[2] for a,b in zip(group,group[1:])))
                    if len({v<p['min_length'] for v in values})>1:
                        emit('S_LENGTH_THRESHOLD',stage,segment,segment_indices=group)
            elif stage['name']=='D':
                e,a=directions(enu,ids,p['direction']),directions(alt,ids,p['direction'])
                for en,ae in zip(e,a):
                    if (en['reason'],en['candidate'])!=(ae['reason'],ae['candidate']):
                        emit('D_DIRECTION_THRESHOLD_OR_UNDEFINED',stage,segment,original_index=en['index'])
            else:
                kept=stage['output'][j]['indices'];position={i:k for k,i in enumerate(ids)}
                eps_e=allowance([enu[i] for i in ids],p['dp']);eps_a=allowance([alt[i] for i in ids],p['dp'])
                # Decimal on every actual omitted interval point, endpoints are exactly zero.
                for left,right in zip(kept,kept[1:]):
                    for i in ids[position[left]+1:position[right]]:
                        e=finite_distance(enu[i],enu[left],enu[right]);a=finite_distance(alt[i],alt[left],alt[right])
                        if (e>p['dp'])!=(a>p['dp']) or (e>p['dp']+eps_e)!=(a>p['dp']+eps_a):
                            emit('P_FIXED_OUTPUT_INTERVAL_THRESHOLD',stage,segment,original_index=i,left_index=left,right_index=right)
                if alternate_dp(alt,ids,p['dp'])!=kept:
                    emit('P_KEEP_SET_SENSITIVITY',stage,segment)
    return events


def check_stage_extreme(name,witness,trace,raw,alt,geod):
    """Recalculate the reported actual-stage witness, without assuming global maximality."""
    xy=trace['source_record']['xy'];ll=raw[1]
    stage=next(s for s in trace['stages'] if s['position']==witness['stage_position'])
    if name.startswith('S_max_abs_'):
        assert stage['name']=='S'
        if 'length' in name:
            ids=witness['segment_indices']
            assert any(p['indices']==ids for op in stage['operations'] for p in op['segments'])
            e=math.fsum(math.dist(xy[a],xy[b]) for a,b in zip(ids,ids[1:]))
            g=math.fsum(geod.inv(*ll[a],*ll[b])[2] for a,b in zip(ids,ids[1:]))
            value=abs(e-g)
        else:
            a,b=witness['left_index'],witness['right_index']
            assert any((a,b) in list(zip(p['indices'],p['indices'][1:])) for p in stage['input'])
            e=math.dist(xy[a],xy[b])
            other=math.dist(alt[a],alt[b]) if 'aeqd' in name else geod.inv(*ll[a],*ll[b])[2]
            value=abs(e-other)
    elif name=='D_max_abs_aeqd_angle_change_degrees':
        assert stage['name']=='D';index=witness['original_index']
        segment=next(p for p in stage['input'] if index in p['indices'])
        e=next(v for v in directions(xy,segment['indices'],trace['parameters']['direction']) if v['index']==index)
        a=next(v for v in directions(alt,segment['indices'],trace['parameters']['direction']) if v['index']==index)
        assert e['reason'] is a['reason'] is None
        value=max(abs(x-y) for x,y in zip(e['deltas'],a['deltas']))
    elif name in {'P_max_aeqd_error_of_actual_output_m','P_max_abs_aeqd_error_change_m'}:
        assert stage['name']=='P';index=witness['original_index']
        position=next(j for j,p in enumerate(stage['input']) if index in p['indices'])
        kept=stage['output'][position]['indices']
        if index in kept:
            e=a=0.
        else:
            left,right=next((l,r) for l,r in zip(kept,kept[1:]) if l<index<r)
            e=finite_distance(xy[index],xy[left],xy[right]);a=finite_distance(alt[index],alt[left],alt[right])
        value=a if name=='P_max_aeqd_error_of_actual_output_m' else abs(e-a)
    else:
        raise AssertionError(('UNRECOGNIZED_STAGE_EXTREMUM',name))
    assert math.isclose(value,witness['value'],rel_tol=1e-9,abs_tol=1e-8),(name,value,witness['value'])
    return {'name':name,'record_id':trace['record_id'],'config_id':witness['config_id'],
            'reported_value':witness['value'],'independent_value':value,'scope':'actual witness; global completeness relies on reviewed B full enumeration'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);parser.add_argument('coordinates',type=Path)
    parser.add_argument('--development-smoke',action='store_true');args=parser.parse_args()
    folder=args.run.resolve();mp=folder/'manifest.json';m=read(mp)
    result_path=args.coordinates.resolve()/'coordinate_checks.json';result=read(result_path)
    log_path=result_path.parent/'threshold_differences.jsonl.gz'
    assert m['status']=='MACHINE_VERIFIED_PENDING_C', 'NO_RUNNING_OR_PARTIAL_SCOPE_REVIEW'
    cp=ROOT/'task1/config/goal3/contract.json';contract=read(cp);model=contract['model']
    raw_path=ROOT/contract['raw_path'];assert sha(raw_path)==contract['raw_sha256'];raw=read(raw_path)
    assert result['source_sha256']==sha(ROOT/'task1/goal3/coordinates.py')
    for name,h in result['source_bindings'].items():assert sha(ROOT/name)==h,name
    assert result['threshold_differences_sha256']==sha(log_path)
    if args.development_smoke:
        assert m['partition']=='G3_DEVELOPMENT'
        expected_ids=m['input_ids'][:8];sample=set(expected_ids)
        fixture=result_path.parent/'engineering_scope_fixture_manifest.json'
        assert result['input_manifest_sha256']==sha(fixture)
        assert read(fixture)['input_ids']==expected_ids
    else:
        assert m['partition']=='FULL_PRODUCTION'
        frozen=read(EV/'production_freeze.json')
        assert m['input_ids']==frozen['input_ids'] and set(m['input_ids'])==set(raw)
        assert result['input_manifest_sha256']==sha(mp)
        prior=read(OUT/(m['run_id']+'_receipt.json'));categories=read(OUT/(m['run_id']+'_categories_receipt.json'))
        assert prior['status']==categories['status']=='VERIFIED'
        assert prior['targets'][0]['sha256']==categories['targets'][0]['sha256']==sha(mp)
        sample=set(categories['random_records'])
        for cat in categories['categories'].values():sample.update(cat['selected_records'])
        expected_ids=m['input_ids']
    assert result['input_record_count']==len(expected_ids)
    assert result['run_id']==m['run_id'] and result['partition']==m['partition']
    assert [r['record_id'] for r in result['per_record']]==expected_ids
    assert result['implementation_status']=='VERIFIED' and not result['implementation_failures']
    assert result['source_crs']=='UNVERIFIED' and not result['source_datum_proven'] and not result['ground_truth_accuracy_claim']
    reported=defaultdict(list)
    with gzip.open(log_path,'rt') as handle:
        for line in handle:
            row=json.loads(line);reported[row['record_id']].append(row)
    assert set(reported)<=set(expected_ids)
    assert Counter(r['kind'] for rows in reported.values() for r in rows)==Counter(result['difference_counts'])
    sample.update(reported)
    sample.update(v['record_id'] for v in result['extrema'].values())
    assert sample<=set(expected_ids)
    a,rf=model['semi_major_m'],model['inverse_flattening'];lon0,lat0=model['origin_lon_degrees'],model['origin_lat_degrees']
    proj=pyproj.Transformer.from_pipeline(f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad +step +proj=cart +a={a} +rf={rf} +step +proj=topocentric +a={a} +rf={rf} +lon_0={lon0} +lat_0={lat0} +h_0=0')
    aeqd=pyproj.Proj(proj='aeqd',a=a,rf=rf,lon_0=lon0,lat_0=lat0,units='m');geod=pyproj.Geod(a=a,rf=rf)
    counts=Counter();seen=[];point_max=radius_max=raw_abs_max=raw_rel_max=0.;independent_events=[];sample_traces=0;stage_extremes=[]
    per_record={r['record_id']:r for r in result['per_record']};targets=[]
    for shard in m['shards']:
        if not set(shard['input_ids'])&set(expected_ids):continue
        path=folder/shard['path'];assert sha(path)==shard['sha256'];targets.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
        shard_seen=[]
        with gzip.open(path,'rt') as handle:
            for line in handle:
                row=json.loads(line);rid=row['record_id'];shard_seen.append(rid)
                if rid not in per_record:continue
                seen.append(rid);times,ll=raw[rid];ll=np.asarray(ll,float)
                trace=next(iter(row['traces'].values()));xy=np.asarray(trace['source_record']['xy'],float)
                e,n,_=proj.transform(ll[:,0],ll[:,1],np.zeros(len(ll)),errcheck=True)
                residual=np.hypot(xy[:,0]-e,xy[:,1]-n);radius=np.hypot(*xy.T)
                er=float(residual.max());rad=float(radius.max())
                assert er<=model['coordinate_crosscheck_absolute_tolerance_m'] and rad<=model['domain_max_radius_m']
                point_max=max(point_max,er);radius_max=max(radius_max,rad)
                _,_,gd=geod.inv(ll[:-1,0],ll[:-1,1],ll[1:,0],ll[1:,1]);gd=np.asarray(gd)
                difference=np.abs(np.linalg.norm(np.diff(xy,axis=0),axis=1)-gd)
                abs_max=float(difference.max()) if len(difference) else None
                if abs_max is not None:raw_abs_max=max(raw_abs_max,abs_max)
                if np.any(gd>0):raw_rel_max=max(raw_rel_max,float((difference[gd>0]/gd[gd>0]).max()))
                r=per_record[rid]
                assert r['points']==len(times) and r['actual_traces_checked']==len(row['traces'])
                assert abs(r['coordinate_error_max_work_m']-er)<1e-12
                assert (r['raw_adjacent_geod_difference_max_work_m'] is None if abs_max is None else abs(r['raw_adjacent_geod_difference_max_work_m']-abs_max)<1e-10)
                counts.update(records_checked=1,points_checked=len(times),raw_adjacent_edges=max(0,len(times)-1),unique_actual_traces_checked=len(row['traces']))
                alt=None
                if rid in sample:
                    ax,ay=aeqd(ll[:,0],ll[:,1],errcheck=True);alt=np.column_stack((ax,ay)).tolist()
                for cfg,t in row['traces'].items():
                    counts.update(stage_counts(t))
                    if alt is not None:
                        independent_events.extend(sensitivity(t,cfg,raw[rid],alt,geod));sample_traces+=1
                        for name,witness in result['extrema'].items():
                            if name.startswith(('S_','D_','P_')) and witness['record_id']==rid and witness['config_id']==cfg:
                                stage_extremes.append(check_stage_extreme(name,witness,t,raw[rid],alt,geod))
                if len(seen)%500==0:print(json.dumps({'coordinate_C_records':len(seen),'independent_sensitivity_traces':sample_traces}),flush=True)
        assert shard_seen==shard['input_ids']
    assert seen==expected_ids and counts==Counter(result['counts'])
    assert {r['name'] for r in stage_extremes}=={name for name in result['extrema'] if name.startswith(('S_','D_','P_'))}
    actual_keys=Counter(key(r) for r in independent_events)
    reported_keys=Counter(key(r) for rid,rows in reported.items() if rid in sample for r in rows)
    assert actual_keys==reported_keys,{'extra_independent':list((actual_keys-reported_keys).elements())[:10], 'extra_reported':list((reported_keys-actual_keys).elements())[:10]}
    for name,value in [('PROJ_implementation_error_work_m',point_max),('max_ENU_radius_work_m',radius_max),
        ('raw_adjacent_geod_absolute_difference_work_m',raw_abs_max),('raw_adjacent_geod_relative_difference',raw_rel_max)]:
        assert math.isclose(result['extrema'][name]['value'],value,rel_tol=1e-12,abs_tol=1e-12),name
    source_paths=[mp,result_path,log_path,cp,ROOT/'task1/goal3/coordinates.py',ROOT/'task1/scripts/goal2_coordinate_sensitivity.py']
    targets+=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in source_paths]
    receipt={'role_context':'/root/c_protocol','status':'VERIFIED','target_id':m['run_id']+':coordinate_outputs',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,'source_hashes':result['source_bindings'],
        'classification':'8_RECORD_EXPOSED_DEVELOPMENT_ENGINEERING_SMOKE_NOT_FULL' if args.development_smoke else 'FULL_SCOPE_WITH_EXPLICIT_INDEPENDENT_SENSITIVITY_SAMPLE',
        'checked_components':['Exact raw/input/record/shard/output/log/source hashes and ordered complete scope',
            'Every selected original point independently checked against PROJ; all rawadjacentGeod distances and complete perrecord extrema reduced',
            'All actual Sedge/length,Dwindow/undefined andPinput/output/segment counts independently enumerated',
            'Difference log fullaggregation; independently reconstructed allS/D/P sensitivity events for predeclaredrandom/category plus everyreported difference/extreme record',
            'Sensitivity checker does not import production coordinates or inherited B inspect_trace helper; Decimal finiteinterval math and own DP/direction path',
            'Every reported S/D/P extremum witness independently recalculated; all-record global maximality remains B full-enumeration claim',
            'Fixed actualstageinputs sensitivity, not full alternate-coordinate endtoend reprocessing; datum/groundtruth claims remainfalse'],
        'unchecked_components':['Independent sensitivity recomputation for every nonsampled record','Independent proof of complete B difference enumeration beyond inspected sample; source/control flow and full denominators reviewed',
            'Source datum, absolute physical positioning accuracy or noise truth'],
        'counts':dict(counts),'independent_sensitivity_record_ids':sorted(sample),
        'independent_sensitivity_trace_checks':sample_traces,'difference_counts':result['difference_counts'],
        'independent_stage_extreme_witness_checks':stage_extremes,
        'PROJ_max_error_work_m':point_max,'errors':[],
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_c/review_full_coordinates.py '+str(args.run)+' '+str(args.coordinates)+(' --development-smoke' if args.development_smoke else ''),
        'checker_sha256':sha(Path(__file__))}
    suffix='_coordinates_independent_smoke_receipt.json' if args.development_smoke else '_coordinates_receipt.json'
    output=OUT/(m['run_id']+suffix)
    with output.open('x') as handle:json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
    print(json.dumps({'status':'VERIFIED','classification':receipt['classification'],'records':len(seen),'points':counts['points_checked'],
        'independent_sensitivity_records':len(sample),'independent_sensitivity_traces':sample_traces,'receipt_sha256':sha(output)}))


if __name__=='__main__':
    main()
