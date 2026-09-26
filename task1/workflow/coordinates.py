"""Explicit conditional working coordinates, never a source datum assignment."""
from copy import deepcopy
import math
from .io import ROOT, read_json, digest

CONTRACT_PATH=ROOT/'task1/config/conditional_planar.json'
CONTRACT_SHA256='5b1ab7dbf25797a51405a2cddd93a8d2ea3e3b69530369366d0e05be7abb8169'


def conditional_contract():
    if digest(CONTRACT_PATH)!=CONTRACT_SHA256: raise ValueError('UNREGISTERED_CONDITIONAL_CONTRACT')
    return read_json(CONTRACT_PATH)


def _ecef(lon_degrees,lat_degrees,model):
    if (not all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
                for v in (lon_degrees,lat_degrees)) or abs(lon_degrees)>180 or abs(lat_degrees)>90):
        raise ValueError('INVALID_ANGULAR_COORDINATE')
    lon,lat=math.radians(lon_degrees),math.radians(lat_degrees)
    f=1/model['inverse_flattening'];e2=f*(2-f);a=model['semi_major_m']
    n=a/math.sqrt(1-e2*math.sin(lat)**2);h=model['assumed_height_m']
    return ((n+h)*math.cos(lat)*math.cos(lon),(n+h)*math.cos(lat)*math.sin(lon),
            (n*(1-e2)+h)*math.sin(lat))


def working_xy(coordinates,model=None):
    model=conditional_contract()['analysis_model'] if model is None else model
    lon0,lat0=map(math.radians,(model['origin_lon_degrees'],model['origin_lat_degrees']))
    origin=_ecef(model['origin_lon_degrees'],model['origin_lat_degrees'],model)
    points=[]
    for p in coordinates:
        if not isinstance(p,(list,tuple)) or len(p)!=2: raise ValueError('LON_LAT_PAIR_REQUIRED')
        q=_ecef(*p,model);dx,dy,dz=[v-o for v,o in zip(q,origin)]
        east=-math.sin(lon0)*dx+math.cos(lon0)*dy
        north=-math.sin(lat0)*math.cos(lon0)*dx-math.sin(lat0)*math.sin(lon0)*dy+math.cos(lat0)*dz
        if math.hypot(east,north)>model['domain_max_radius_m']: raise ValueError('OUTSIDE_FIXED_LOCAL_DOMAIN')
        points.append([east,north])
    return points


def conditional_adapter(record_id,raw_record):
    times,coords=raw_record
    if len(times)!=len(coords): raise ValueError('RAW_ALIGNMENT_MISMATCH')
    return {'record_id':record_id,'indices':list(range(len(coords))),
            'timestamps':deepcopy(times),'xy':working_xy(coords)}


def registration():
    contract=conditional_contract()
    approval=contract['approval_source']
    if digest(ROOT/approval['path'])!=approval['sha256']: raise ValueError('CONDITIONAL_APPROVAL_CHANGED')
    decision=read_json(ROOT/approval['path'])
    if (decision['D1']['conditional_analysis']!='AUTHORIZED' or decision['D1']['source_crs']!='UNVERIFIED'
            or decision['D2']['status']!='USER_APPROVED' or decision['D2']['method']!=contract['method']):
        raise ValueError('CONDITIONAL_APPROVAL_MISSING')
    supplement=ROOT/decision['D1']['source']
    if digest(supplement)!=decision['D1']['sha256']: raise ValueError('AUTHORIZATION_TEXT_CHANGED')
    return {**contract,'adapter':conditional_adapter}
