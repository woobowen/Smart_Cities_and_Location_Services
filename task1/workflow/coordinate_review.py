"""Independent PROJ checks and bounded geometric sensitivity, not CRS proof."""
import math
import pyproj
from .coordinates import conditional_contract, working_xy
from .evaluation import verify_simplification
from .io import object_hash



def _direction_windows(xy, indices, threshold):
    """Independent common-grid headings; every point has a computable/undefined state."""
    bearings = []
    for i, j in zip(indices, indices[1:]):
        a, b = xy[i], xy[j]
        bearings.append(None if a == b else math.degrees(math.atan2(b[0]-a[0], b[1]-a[1])) % 360)
    rows = []
    for pos, index in enumerate(indices):
        reason = None
        if pos == 0 or pos == len(indices)-1:
            reason = 'ENDPOINT'
        elif pos+1 >= len(bearings):
            reason = 'MISSING_FOLLOWING_OUTGOING_EDGE'
        elif any(x is None for x in bearings[pos-1:pos+2]):
            reason = 'UNCOMPUTABLE_DIRECTION_IN_WINDOW'
        differences = None
        if reason is None:
            differences = []
            for other in (bearings[pos-1], bearings[pos+1]):
                direct = abs(bearings[pos]-other)
                differences.append(min(direct, 360-direct))
        rows.append({'index':index, 'reason':reason, 'differences_degrees':differences,
                     'candidate':None if reason else all(d > threshold for d in differences),
                     'margin_to_threshold_degrees':None if reason else min(abs(d-threshold) for d in differences)})
    return rows


def validate_coordinates(raw, baseline=None):
    c=conditional_contract();m=c['analysis_model'];v=c['validation']
    a=m['semi_major_m'];rf=m['inverse_flattening'];lon=m['origin_lon_degrees'];lat=m['origin_lat_degrees']
    transform=pyproj.Transformer.from_pipeline(
        f'+proj=pipeline +step +proj=unitconvert +xy_in=deg +xy_out=rad '
        f'+step +proj=cart +a={a} +rf={rf} '
        f'+step +proj=topocentric +a={a} +rf={rf} +lon_0={lon} +lat_0={lat} +h_0=0')
    geod=pyproj.Geod(a=a,rf=rf)
    alternate=pyproj.Proj(proj='aeqd',a=a,rf=rf,lon_0=lon,lat_0=lat,units='m')
    max_coordinate_error=0.;max_radius=0.;max_pair_relative=0.;max_pair_absolute=0.
    pair_count=0;edges=[];coordinates={};alternate_xy={};errors=[]
    for rid,(times,coords) in raw.items():
        xy=working_xy(coords);coordinates[rid]=xy;alt=[]
        for i,(p,q) in enumerate(zip(coords,xy)):
            east,north,_=transform.transform(p[0],p[1],0,errcheck=True)
            err=math.hypot(q[0]-east,q[1]-north);max_coordinate_error=max(max_coordinate_error,err)
            radius=geod.inv(lon,lat,p[0],p[1])[2];max_radius=max(max_radius,radius)
            alt.append(list(alternate(p[0],p[1],errcheck=True)))
            for j in range(i):
                s=geod.inv(coords[j][0],coords[j][1],p[0],p[1])[2]
                d=math.dist(xy[j],q);pair_count+=1
                max_pair_absolute=max(max_pair_absolute,abs(d-s))
                if s>1e-6:max_pair_relative=max(max_pair_relative,abs(d-s)/s)
            if i:
                s=geod.inv(coords[i-1][0],coords[i-1][1],p[0],p[1])[2]
                d=math.dist(xy[i-1],q)
                edges.append({'record_id':rid,'left_index':i-1,'right_index':i,'enu_m':d,'ellipsoid_m':s,
                              'absolute_difference_m':abs(d-s),'margin_to_400m':abs(d-400),
                              'threshold_disagreement':(d>400)!=(s>400)})
        alternate_xy[rid]=alt
    if max_coordinate_error>v['coordinate_absolute_tolerance_m']:errors.append('INDEPENDENT_PROJ_COORDINATE_MISMATCH')
    if max_radius>m['domain_max_radius_m']:errors.append('OUTSIDE_LOCAL_DOMAIN')
    if max_pair_relative>v['max_observed_relative_distance_difference']:errors.append('LOCAL_MODEL_DISTANCE_DIFFERENCE_TOO_LARGE')
    result={'status':'REJECTED' if errors else 'VERIFIED','errors':errors,
            'classification':'CURRENT_RUN_CONDITIONAL_ANALYSIS','source_crs':'UNVERIFIED',
            'contract_id':c['contract_id'],'contract_sha256':object_hash(c),'raw_scope_sha256':object_hash(raw),
            'independent_implementation':{'pyproj':pyproj.__version__,'proj':pyproj.proj_version_str},
            'points_checked':sum(len(v[1]) for v in raw.values()),'within_record_pairs_checked':pair_count,
            'max_coordinate_crosscheck_error_m':max_coordinate_error,'max_model_geodesic_radius_m':max_radius,
            'max_pair_distance_relative_difference':max_pair_relative,'max_pair_distance_absolute_difference_m':max_pair_absolute,
            'edge_checks':edges,'edge_400m_disagreements':sum(e['threshold_disagreement'] for e in edges),
            'source_datum_proven':False,'quality_claim':'implementation and finite pilot model sensitivity only',
            'unavailable_claims':['absolute_geographic_accuracy','true_ground_error','datum_or_offset_identification']}
    if baseline is None:
        result['processing_threshold_checks']='NOT_RUN_PREPROCESSING_VALIDATION'
        return result
    if baseline.get('status')!='VERIFIED': raise ValueError('ACTUAL_BASELINE_REQUIRED')
    segment_checks=[];direction_checks=[];dp_checks=[]
    for record in baseline['records']:
        rid=record['record_id'];times,coords=raw[rid]
        segments=[(s,False) for s in record['filtered_segments']]+[(s['input'],True) for s in record['processed_segments']]
        for segment,processed in segments:
            indices=segment['indices']
            enu=sum(math.dist(coordinates[rid][i],coordinates[rid][j]) for i,j in zip(indices,indices[1:]))
            geo=sum(geod.inv(*coords[i],*coords[j])[2] for i,j in zip(indices,indices[1:]))
            segment_checks.append({'record_id':rid,'segment_index':segment['segment_index'],'points':len(indices),
                'enu_length_m':enu,'ellipsoid_length_m':geo,'margin_to_65m':abs(enu-65),
                'threshold_disagreement':(enu<65)!=(geo<65)})
            if not processed:continue
            enu_windows = _direction_windows(coordinates[rid], indices, c['parameters']['direction'])
            aeqd_windows = _direction_windows(alternate_xy[rid], indices, c['parameters']['direction'])
            actual = next(s for s in record['processed_segments'] if s['segment_index'] == segment['segment_index'])
            for en, alt in zip(enu_windows, aeqd_windows):
                direction_checks.append({'record_id':rid, 'segment_index':segment['segment_index'],
                    'original_index':en['index'], 'direction_convention':'CLOCKWISE_FROM_POSITIVE_Y',
                    'enu_differences_degrees':en['differences_degrees'],
                    'aeqd_grid_differences_degrees':alt['differences_degrees'],
                    'enu_undefined_reason':en['reason'], 'aeqd_undefined_reason':alt['reason'],
                    'enu_candidate':en['candidate'], 'aeqd_candidate':alt['candidate'],
                    'actual_deleted':en['index'] in actual['denoise']['deleted_indices'],
                    'margin_to_35deg':en['margin_to_threshold_degrees'],
                    'predicate_disagreement':en['candidate'] != alt['candidate'],
                    'undefined_disagreement':en['reason'] != alt['reason']})
        for segment in record['processed_segments']:
            clean=segment['denoise']['record'];final=segment['output']
            def rec(r, source):
                ids=r['indices'];return {'record_id':rid,'indices':ids,'timestamps':[times[i] for i in ids],
                                        'xy':[source[rid][i] for i in ids]}
            checked=verify_simplification(rec(clean,alternate_xy),rec(final,alternate_xy),c['parameters']['dp'])
            enu_check=verify_simplification(rec(clean,coordinates),rec(final,coordinates),c['parameters']['dp'])
            alt_error=checked['metrics']['max_error']['value']
            enu_error=enu_check['metrics']['max_error']['value']
            dp_checks.append({'record_id':rid,'segment_index':segment['segment_index'],
                              'alternate_projection':'ellipsoid_AEQD_same_fixed_center_model_only',
                              'status':checked['status'],'max_error_m':alt_error,
                              'enu_status':enu_check['status'],'enu_max_error_m':enu_error,
                              'max_error_change_m':None if alt_error is None or enu_error is None else alt_error-enu_error,
                              'exceeding_points':checked.get('exceeding_points',[])})
    result.update(processing_threshold_checks='EXECUTED',segment_65m_checks=segment_checks,
                  direction_35deg_checks=direction_checks,dp_5m_checks=dp_checks,
                  segment_65m_disagreements=sum(c['threshold_disagreement'] for c in segment_checks),
                  direction_35deg_disagreements=sum(c['predicate_disagreement'] for c in direction_checks),
                  direction_undefined_disagreements=sum(c['undefined_disagreement'] for c in direction_checks),
                  direction_undefined_points=sum(c['enu_undefined_reason'] is not None for c in direction_checks),
                  dp_5m_disagreements=sum(c['status']!='VERIFIED' for c in dp_checks),
                  interpretation='Disagreements limit robustness claims; they do not alter the fixed ENU contract or relax DP tolerance.')
    return result
