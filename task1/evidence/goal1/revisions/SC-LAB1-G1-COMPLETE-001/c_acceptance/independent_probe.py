"""C's read-only raw/contract/actual-output audit; no workflow imports.

Only this script's own directory receives output. Decimal residuals are an
independent finite-segment implementation, and recursive DP checks actual
retained indices in addition to a tolerance certificate.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile
import xml.etree.ElementTree as ET

import pyproj

ROOT = Path(__file__).resolve().parents[6]
OUT = Path(__file__).resolve().parent
REV = OUT.parent
IDS = ['0', '1', '2', '246', '256', '306', '352']
RAW = ROOT / 'task1/作业/作业/traj_dict.json'
RAW_HASH = 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3'
EPS = sys.float_info.epsilon


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def obj(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def same(left, right):
    return obj(left) == obj(right)


def distance(point, start, end):
    with localcontext() as ctx:
        ctx.prec = 55
        p, a, b = [tuple(Decimal(v) for v in q) for q in (point, start, end)]
        v = (b[0]-a[0], b[1]-a[1]); w = (p[0]-a[0], p[1]-a[1])
        square = v[0]*v[0]+v[1]*v[1]
        t = max(Decimal(0), min(Decimal(1), (v[0]*w[0]+v[1]*w[1])/square)) if square else Decimal(0)
        return float(((w[0]-t*v[0])**2 + (w[1]-t*v[1])**2).sqrt())


def recurse_dp(xy, indices, tolerance):
    if len(indices) <= 2 or tolerance == 0:
        return indices
    errors = [distance(xy[i], xy[indices[0]], xy[indices[-1]]) for i in indices[1:-1]]
    biggest = max(errors)
    if biggest <= tolerance:
        return [indices[0], indices[-1]]
    pos = errors.index(biggest)+1
    return recurse_dp(xy, indices[:pos+1], tolerance)[:-1]+recurse_dp(xy, indices[pos:], tolerance)


def circular(a, b):
    delta = abs(a-b)
    return min(delta, 360-delta)


def headings(xy, ids):
    return [None if xy[i] == xy[j] else math.degrees(math.atan2(xy[j][0]-xy[i][0], xy[j][1]-xy[i][1])) % 360
            for i, j in zip(ids, ids[1:])]


def direction_rows(xy, ids):
    h = headings(xy, ids); rows=[]
    for pos, i in enumerate(ids):
        reason = ('ENDPOINT' if pos in (0, len(ids)-1) else
                  'MISSING_FOLLOWING_OUTGOING_EDGE' if pos+1 >= len(h) else
                  'UNCOMPUTABLE_DIRECTION_IN_WINDOW' if None in h[pos-1:pos+2] else None)
        differences = None if reason else [circular(h[pos], h[pos-1]), circular(h[pos], h[pos+1])]
        rows.append({'index':i,'reason':reason,'differences':differences,
                     'candidate':None if reason else all(d>35 for d in differences)})
    return rows


def allowance(xy):
    return 64*EPS*max(1, 5, max(abs(v) for p in xy for v in p),
                     *(max(p[k] for p in xy)-min(p[k] for p in xy) for k in (0,1)))


def main(run_id):
    checks=[]; errors=[]
    def check(name, condition, detail=None):
        checks.append({'check':name,'passed':bool(condition),'detail':detail})
        if not condition: errors.append({'check':name,'detail':detail})
    contract=read(ROOT/'task1/config/conditional_planar.json')
    policy=read(ROOT/'task1/config/goal1.json')
    all_raw=read(RAW);raw={i:all_raw[i] for i in IDS}
    path=REV/'runs'/run_id/'baseline.json'; baseline=read(path)
    check('raw_hash', sha(RAW)==RAW_HASH)
    check('fixed_scope', baseline['record_ids']==IDS and len(baseline['records'])==7)
    check('fixed_input_count', sum(len(v[1]) for v in raw.values())==783)
    check('conditional_claims', contract['source_crs']=='UNVERIFIED' and contract['analysis_model']['source_epsg'] is None
          and baseline['classification']=='CURRENT_RUN_CONDITIONAL_ANALYSIS')
    check('candidate_contract_exact',same(baseline['contract'],contract))
    check('fixed_parameters',same(baseline['parameters'], {'dt':30,'distance':400,'min_points':5,'min_length':65,
                                                        'direction':35,'dp':5,'time_reliable':True}))
    authorization=contract['approval_source']
    check('authorization_hash',sha(ROOT/authorization['path'])==authorization['sha256'])
    decision=read(ROOT/authorization['path'])
    check('user_supplement_hash',sha(ROOT/decision['D1']['source'])==decision['D1']['sha256'])
    check('D2_explicit_authorization',decision['D2']['status']=='USER_APPROVED' and
          decision['D2']['method']=='single_pass_simultaneous_keep_undefined')
    sources=read(REV/'a_scope/source_audit.json')
    for source in sources['source_checks']:
        check('teacher_bytes:'+source['path'],sha(ROOT/source['path'])==source['sha256'])
    for source in sources['targeted_excerpts']:
        if 'member' not in source: continue
        with zipfile.ZipFile(ROOT/source['path']) as z:
            xml=ET.fromstring(z.read(source['member']))
        # Office Math keeps equations in m:t, alongside ordinary DrawingML a:t.
        text='\n'.join(node.text or '' for node in xml.iter() if node.tag.rsplit('}',1)[-1]=='t')
        check('teacher_excerpt:'+source['id'],text==source['excerpt'])
    model=contract['analysis_model'];a=model['semi_major_m'];rf=model['inverse_flattening']
    lon=model['origin_lon_degrees'];lat=model['origin_lat_degrees']
    proj=pyproj.Transformer.from_pipeline(f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
         f'+step +proj=cart +a={a} +rf={rf} +step +proj=topocentric +a={a} +rf={rf} +lon_0={lon} +lat_0={lat} +h_0=0')
    geod=pyproj.Geod(a=a,rf=rf)
    alt=pyproj.Proj(proj='aeqd',a=a,rf=rf,lon_0=lon,lat_0=lat,units='m')
    bbox=[min(p[k] for v in raw.values() for p in v[1]) for k in (0,1)]+[max(p[k] for v in raw.values() for p in v[1]) for k in (0,1)]
    check('origin_from_complete_raw_extent',same([lon,lat],[(bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2]))
    all_ledger=[];stage_total=Counter();segment_total=Counter();independent=[];segments_report=[];dp_report=[];direction_report=[];edge_report=[]
    max_coordinate_error=0.;all_xy={};all_alt={};all_pair_max_abs=0.;all_pair_max_rel=0.;pair_count=0
    by_id={r['record_id']:r for r in baseline['records']}
    expected_keys={(rid,i) for rid,(times,xy) in raw.items() for i in range(len(xy))}
    for rid,(times,angular) in raw.items():
        record=by_id[rid];source=record['source_record'];xy=source['xy'];all_xy[rid]=xy
        check(rid+':raw_values',same(source['raw_values'],raw[rid]) and same(source['timestamps'],times)
              and source['indices']==list(range(len(times))) and source['raw_record_sha256']==obj(raw[rid]))
        check(rid+':parent',record['parent_hash']==obj(source))
        for i,p in enumerate(angular):
            e,n,u=proj.transform(*p,0,errcheck=True)
            max_coordinate_error=max(max_coordinate_error,math.hypot(e-xy[i][0],n-xy[i][1]))
        axy=[list(alt(*p,errcheck=True)) for p in angular];all_alt[rid]=axy
        for i,p in enumerate(angular):
            for j in range(i):
                geo=geod.inv(*angular[j],*p)[2]; d=math.dist(xy[j],xy[i]);pair_count+=1
                all_pair_max_abs=max(all_pair_max_abs,abs(d-geo))
                if geo>1e-6:all_pair_max_rel=max(all_pair_max_rel,abs(d-geo)/geo)
        cuts=[0];boundary_rows=[]
        for i in range(1,len(times)):
            dt=times[i]-times[i-1];d=math.dist(xy[i],xy[i-1]);geo=geod.inv(*angular[i-1],*angular[i])[2]
            reasons=[]
            if dt<0:reasons.append('NEGATIVE_TIME_DIFFERENCE')
            elif dt>30:reasons.append('TIME_GAP')
            if d>400:reasons.append('DISTANCE_GAP')
            edge_report.append({'record_id':rid,'left_index':i-1,'right_index':i,'dt':dt,'enu_m':d,'ellipsoid_m':geo,
                'threshold_disagreement':(d>400)!=(geo>400),'combined_disagreement':(dt<0 or dt>30 or d>400)!=(dt<0 or dt>30 or geo>400)})
            if reasons:cuts.append(i);boundary_rows.append((i,reasons))
        cuts.append(len(times));groups=[list(range(start,end)) for start,end in zip(cuts,cuts[1:]) if start<end]
        check(rid+':boundaries',[(b['to_index'],b['reasons']) for b in record['boundaries']]==boundary_rows)
        counts=Counter(input=len(times),segmented=len(groups),filtered=0,denoised=0,simplified=0,retained=0,not_processed=0)
        seg_counts=Counter(total=len(groups),filtered=0,processed=0)
        observed={s['segment_index']:s for s in record['filtered_segments']}
        processed={s['segment_index']:s for s in record['processed_segments']}
        check(rid+':complete_segments',set(observed).isdisjoint(processed) and set(observed)|set(processed)==set(range(len(groups))))
        for si,indices in enumerate(groups):
            length=math.fsum(math.dist(xy[i],xy[j]) for i,j in zip(indices,indices[1:]))
            geo_length=math.fsum(geod.inv(*angular[i],*angular[j])[2] for i,j in zip(indices,indices[1:]))
            reasons=[]
            if len(indices)<5:reasons.append('TOO_FEW_POINTS')
            if length<65:reasons.append('TOO_SHORT_LENGTH')
            segments_report.append({'record_id':rid,'segment_index':si,'points':len(indices),'enu_length_m':length,
                                    'ellipsoid_length_m':geo_length,'reasons':reasons,'threshold_disagreement':(length<65)!=(geo_length<65)})
            actual_input=observed.get(si,processed.get(si,{}).get('input'))
            check(f'{rid}:{si}:partition_filter',actual_input is not None and actual_input['indices']==indices and
                  actual_input['filter_reasons']==reasons and (bool(reasons)==(si in observed)))
            if actual_input is None:continue
            check(f'{rid}:{si}:input_values',same(actual_input['timestamps'],[times[i] for i in indices]) and
                  same(actual_input['xy'],[xy[i] for i in indices]) and actual_input['parent_hash']==obj(source))
            if reasons:
                seg_counts['filtered']+=1;counts['filtered']+=len(indices)
                fates={i:('filtered',reasons,obj(source)) for i in indices}
            else:
                seg_counts['processed']+=1;seg=processed[si];rows=direction_rows(xy,indices);arows=direction_rows(axy,indices)
                deletes=[row['index'] for row in rows if row['candidate'] is True]
                clean_ids=[i for i in indices if i not in deletes];denoise=seg['denoise'];clean=denoise['record'];final=seg['output']
                check(f'{rid}:{si}:simultaneous_direction',denoise['method']=='single_pass_simultaneous_keep_undefined' and denoise['passes']==1
                      and denoise['deleted_indices']==deletes and clean['indices']==clean_ids)
                check(f'{rid}:{si}:direction_decisions',len(denoise['decisions'])==len(rows) and all(
                      (expected['index'],expected['reason'],expected['candidate'])==(actual['index'],actual['reason'],actual['candidate'])
                      for expected,actual in zip(rows,denoise['decisions'])))
                for row,other in zip(rows,arows):
                    direction_report.append({'record_id':rid,'segment_index':si,'original_index':row['index'],
                        'reason':row['reason'],'enu_differences_degrees':row['differences'],
                        'aeqd_differences_degrees':other['differences'],'predicate_disagreement':row['candidate']!=other['candidate']})
                expected_final=recurse_dp(xy,clean_ids,5)
                check(f'{rid}:{si}:recursive_DP_indices',final['indices']==expected_final,
                      {'expected':expected_final,'actual':final['indices']} if final['indices']!=expected_final else None)
                for label,actual,ids,parent in [('clean',clean,clean_ids,obj(actual_input)),('final',final,expected_final,obj(clean))]:
                    check(f'{rid}:{si}:{label}_actual_values',same(actual['timestamps'],[times[i] for i in ids]) and
                          same(actual['xy'],[xy[i] for i in ids]) and actual['parent_hash']==parent)
                    fedges=actual['features']['edges']
                    check(f'{rid}:{si}:{label}_adjacency',[(e['from_index'],e['to_index']) for e in fedges]==list(zip(ids,ids[1:])))
                    check(f'{rid}:{si}:{label}_dt_dist_speed',all(e['dt']==times[j]-times[i] and
                          abs(e['distance']-math.dist(xy[i],xy[j]))<=64*EPS*max(1,e['distance']) and
                          (e['speed'] is None if times[j]<=times[i] else abs(e['speed']-math.dist(xy[i],xy[j])/(times[j]-times[i]))<=64*EPS*max(1,e['speed']))
                          for e,i,j in zip(fedges,ids,ids[1:])))
                residual={i:0. for i in expected_final};alt_residual=dict(residual)
                for left,right in zip(expected_final,expected_final[1:]):
                    for i in clean_ids:
                        if left<i<right:residual[i]=distance(xy[i],xy[left],xy[right]);alt_residual[i]=distance(axy[i],axy[left],axy[right])
                allow=allowance([xy[i] for i in clean_ids]);maximum=max(residual.values());altmaximum=max(alt_residual.values())
                stored=seg['independent_review'];metrics=stored['metrics']
                check(f'{rid}:{si}:DP_all_intervals',len(residual)==len(clean_ids) and maximum<=5+allow)
                check(f'{rid}:{si}:DP_metrics',metrics['reference_points']['value']==len(clean_ids) and metrics['simplified_points']['value']==len(expected_final)
                      and metrics['saving']['value']==1-len(expected_final)/len(clean_ids) and
                      abs(metrics['max_error']['value']-maximum)<=allow and stored['floating_allowance']==allow)
                dp_report.append({'record_id':rid,'segment_index':si,'reference_points':len(clean_ids),'final_points':len(expected_final),
                                  'max_error_m':maximum,'aeqd_max_error_m':altmaximum,'allowance':allow,'max_error_index':max(residual,key=residual.get),
                                  'maximum_per_point_AEQD_change_m':max(abs(residual[i]-alt_residual[i]) for i in residual),
                                  'errors':residual,'aeqd_errors':alt_residual})
                counts['denoised']+=len(deletes);counts['simplified']+=len(clean_ids)-len(expected_final);counts['retained']+=len(expected_final)
                fates={i:('denoised',['DIRECTION_RULE'],obj(actual_input)) if i in deletes else
                       ('retained',['DP_RETAINED'],obj(clean)) if i in expected_final else
                       ('simplified',['DP_WITHIN_TOLERANCE'],obj(clean)) for i in indices}
            for i,(action,why,parent) in fates.items():
                all_ledger.append({'record_id':rid,'original_index':i,'segment_index':si,'action':action,'reasons':why,
                                   'parent_hash':parent,'timestamp':times[i],'xy':xy[i]})
        check(rid+':all_record_summaries',same(record['stage_counts'],dict(counts)) and same(record['segment_counts'],dict(seg_counts)))
        independent.append({'record_id':rid,'stage_counts':dict(counts),'segment_counts':dict(seg_counts)})
        stage_total.update(counts);segment_total.update(seg_counts)
    check('PROJ_all_coordinate_values',max_coordinate_error<=1e-6,max_coordinate_error)
    check('complete_ledger_raw_membership',Counter((r['record_id'],r['original_index']) for r in baseline['point_actions'])==Counter(expected_keys))
    check('complete_ledger_actual_values_reasons_parents',Counter(obj(x) for x in all_ledger)==Counter(obj(x) for x in baseline['point_actions']))
    check('global_stage_summary',same(baseline['stage_counts'],dict(stage_total)))
    check('global_segment_summary',same(baseline['segment_counts'],dict(segment_total)))
    check('no_points_unprocessed',stage_total['not_processed']==0 and sum(stage_total[k] for k in ['filtered','denoised','simplified','retained'])==783)
    check('max_pair_error_fixed_limit',all_pair_max_rel<=contract['validation']['max_observed_relative_distance_difference'])
    ledger_path=path.parent/'point_actions.jsonl'
    if ledger_path.exists():
        external=[json.loads(s) for s in ledger_path.read_text().splitlines()]
        check('external_ledger_exact',same(external,baseline['point_actions']))
    source_hashes={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'task1/workflow').glob('*.py')}
    report={'status':'REJECTED' if errors else 'VERIFIED','classification':'INDEPENDENT_C_REAL_DATA_CONDITIONAL_AUDIT',
            'run_id':run_id,'checked_components':['trusted_raw_scope','approved_analysis_contract','independent_coordinates','segmentation','filtering',
                'direction','actual_values','independent_recursive_DP','all_decimal_DP_intervals','point_accounting','summaries'],
            'source_crs':'UNVERIFIED','source_datum_proven':False,'raw_sha256':sha(RAW),'contract_sha256':sha(ROOT/'task1/config/conditional_planar.json'),
            'target':{'path':str(path.relative_to(ROOT)),'sha256':sha(path)},'probe_sha256':sha(__file__),
            'source_hashes':source_hashes,'check_count':len(checks),'checks':checks,'errors':errors,
            'structural_full_input':{'records':len(all_raw),'points':sum(len(v[1]) for v in all_raw.values()),'processing_scope':'ONLY_FIXED_PILOT'},
            'stage_counts':dict(stage_total),'segment_counts':dict(segment_total),'per_record':independent,
            'max_coordinate_crosscheck_error_m':max_coordinate_error,'within_record_pairs_checked':pair_count,
            'max_pair_distance_absolute_difference_m':all_pair_max_abs,'max_pair_distance_relative_difference':all_pair_max_rel,
            'edge_checks':edge_report,'segment_checks':segments_report,'direction_checks':direction_report,'dp_checks':dp_report,
            'limitations':['Unknown source datum and offset history remain unknown','No truth recovery or geographic accuracy proof',
                           'Full source structurally read, only seven fixed records processed','Decimal residuals use actual binary64 model coordinates']}
    dest=OUT/(run_id+'_independent.json');dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(checks),'errors':errors,'stage_counts':report['stage_counts'],
                      'max_error_m':max(r['max_error_m'] for r in dp_report),'output':str(dest.relative_to(ROOT))},ensure_ascii=False,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run_id');args=parser.parse_args();main(args.run_id)
