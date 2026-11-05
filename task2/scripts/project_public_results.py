#!/usr/bin/env python3
"""Publish only explicitly allowlisted aggregate optimization results.

Original local research artifacts are never edited. Matching membership plus
aggregate objectives can reveal individual proxy fares, so chromosomes, pairs,
candidate/context arrays and record-level bindings are deliberately absent.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT/'task2'
PUBLIC = TASK/'public_results'

RUN_SCALARS = (
    'n_eval','runtime','seed','pop_size','n_gen','algorithm','run_id','stage','batch_id',
    'batch_sha256','n_obj','initialization','reference_directions','HV','spacing',
    'completed_utc','knee_index','pickup_budget','constraint_index',
    'initialization_seconds','initialization_scalar_solves','initialization_objective_evals',
    'inserted_km_genes','normalization_seconds','normalization_scalar_solves',
    'runtime_scope','total_runtime','total_objective_evals','front_error',
)
KM_SCALARS = (
    'batch_id','n_obj','HV','spacing','batch_sha256','exact_scalar_solves','scope',
    'solve_seconds','normalization_seconds','objective_evals','normalization_scalar_solves','runtime_scope',
)
CODE_INPUT_HASHES = ('evolution_sha256','runner_sha256','data_code_sha256','source_data_sha256')
METRIC_ROW_SCALARS = (
    'raw_sha256','run_id','stage','algorithm','batch_id','n_obj','seed','pop_size','n_gen',
    'n_eval','total_objective_evals','runtime','total_runtime','runtime_scope','front_error',
    'timing_recompute_sha256',
)
FRONT_METRIC_SCALARS = (
    'HV','Spacing_cv','raw_count','raw_unique','canonical_unique','canonical_nondominated',
    'rounding_merged','dominated_removed','decimals',
)


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def scalar_fields(source, names):
    result={}
    for name in names:
        if name in source:
            value=source[name]
            if value is not None and not isinstance(value,(str,int,float,bool)):
                raise ValueError(f'Expected aggregate scalar for {name}')
            result[name]=value
    return result


def numeric_vector(value, size=None):
    if not isinstance(value,list) or (size is not None and len(value)!=size):
        raise ValueError('Expected numeric objective/normalization vector')
    if any(not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) for v in value):
        raise ValueError('Non-numeric/nonfinite objective vector')
    return list(value)


def objective_points(value,n_obj):
    if not isinstance(value,list):
        raise ValueError('Expected list of objective-space points')
    return [numeric_vector(v,n_obj) for v in value]


def normalizers(source,n_obj):
    return {name:numeric_vector(source[name],n_obj) for name in ['ideal','nadir','ref'] if name in source}


def provenance_hashes(source):
    result={}
    for key in CODE_INPUT_HASHES:
        if key in source:
            value=source[key]
            if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
                raise ValueError(f'Invalid SHA-256 field {key}')
            result[key]=value
    return result


def project_run(source):
    n_obj=int(source.get('n_obj',len(source['F'][0]) if source.get('F') else 2))
    if n_obj not in [2,3]:
        raise ValueError('Only the approved two/three-objective aggregate schema is supported')
    result=scalar_fields(source,RUN_SCALARS)
    result.update(F=objective_points(source['F'],n_obj),**normalizers(source,n_obj))
    result['history']=[]
    for history in source.get('history',[]):
        point=scalar_fields(history,('generation','HV'))
        point['F']=objective_points(history['F'],n_obj)
        result['history'].append(point)
    result['provenance']=provenance_hashes(source.get('provenance',{}))
    return result


def project_km(source):
    n_obj=int(source['n_obj'])
    result=scalar_fields(source,KM_SCALARS)
    result.update(algorithm='weighted_km',**normalizers(source,n_obj))
    result['runs']=[]
    for solution in source['runs']:
        row=scalar_fields(solution,('lam',))
        row['F']=numeric_vector(solution['F'],n_obj)
        result['runs'].append(row)
    result['provenance']=provenance_hashes(source.get('provenance',{}))
    return result


def metric_front(source):
    result=scalar_fields(source,FRONT_METRIC_SCALARS)
    value=source['front']
    n_obj=len(value[0]) if value else 2
    result['front']=objective_points(value,n_obj)
    return result


def source_binding(path,data):
    return dict(path=str(path.relative_to(ROOT)),sha256=sha_bytes(data),
                identity='LOCAL_ORIGINAL_WITHHELD; aggregate-only public projection')


def atomic_json(path,payload):
    data=(json.dumps(payload,ensure_ascii=False,indent=2)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists() or path.read_bytes()!=data:
        temporary=path.with_name('.'+path.name+'.projection.tmp')
        temporary.write_bytes(data)
        temporary.replace(path)
    return sha_bytes(data)


def project_fusion_collection(source):
    # A selected/knee index names only an objective-space point, never a member.
    if isinstance(source,list):
        result=[]
        for front in source:
            row=scalar_fields(front,('seed','t','n_eval','runtime','knee','selected'))
            row['F']=objective_points(front['F'],2)
            result.append(row)
        return result
    return {name:project_fusion_collection(source[name]) for name in ['knee','constraint'] if name in source}


def main():
    producer_sha256=sha(__file__)
    bindings=[]
    local_hashes={}
    projected={}
    for folder,projector in [('runs',project_run),('km',project_km)]:
        for path in sorted((TASK/'results/evolution'/folder).glob('*.json')):
            data=path.read_bytes();local_hashes[path]=sha_bytes(data)
            result=projector(json.loads(data))
            result['public_projection']=dict(schema='dispatch-aggregate-v1',producer_sha256=producer_sha256,
                                              source=source_binding(path,data),
                                              excluded='matching/chromosome/initial-genotype/candidate/edge/individual/context arrays')
            target=PUBLIC/'evolution'/folder/path.name
            target_hash=atomic_json(target,result)
            original=str(path.relative_to(ROOT))
            projected[original]=(str(target.relative_to(ROOT)),target_hash)
            bindings.append(dict(source_path=original,source_sha256=sha_bytes(data),
                                 public_path=str(target.relative_to(ROOT)),public_sha256=target_hash))
    mp=TASK/'results/evolution/metrics.json'
    metric_bytes=mp.read_bytes();local_hashes[mp]=sha_bytes(metric_bytes)
    original_metrics=json.loads(metric_bytes)
    public_rows=[]
    for row in original_metrics['rows']:
        record=scalar_fields(row,METRIC_ROW_SCALARS)
        record.update(normalizers(row,int(row['n_obj'])))
        source_path=row['path']
        if source_path in projected:
            path,pub_hash=projected[source_path]
        else:
            # Only the separately synthetic basic task may remain a full source.
            source=ROOT/source_path
            if '/results/evolution/basic/' not in source_path:
                raise ValueError(f'Unclassified canonical source {source_path}')
            path,pub_hash=source_path,sha(source)
        record.update(path=path,source_path=source_path,public_sha256=pub_hash,
                      metrics=metric_front(row['metrics']),
                      numerical_sensitivity={str(d):metric_front(row['numerical_sensitivity'][str(d)]) for d in [8,12]})
        public_rows.append(record)
    metric_packet=scalar_fields(original_metrics,('evaluator_sha256','runner_sha256','primary_decimals','rule','supersedes'))
    metric_packet.update(rows=public_rows,public_projection=dict(schema='dispatch-aggregate-v1',
        producer_sha256=producer_sha256,source=source_binding(mp,metric_bytes)))
    target=PUBLIC/'evolution/metrics.json'
    metric_hash=atomic_json(target,metric_packet)
    bindings.append(dict(source_path=str(mp.relative_to(ROOT)),source_sha256=sha_bytes(metric_bytes),
                         public_path=str(target.relative_to(ROOT)),public_sha256=metric_hash))
    for source,target_name in [
        (TASK/'results/rl/fusion_validation_v1/static_fronts.json','static_fronts.json'),
        (TASK/'results/rl/fusion_validation_v1/dynamic_nsga_fronts.json','dynamic_validation_fronts.json'),
        (TASK/'results/rl/final_v1/fusion_fronts.json','final_fronts.json'),
    ]:
        data=source.read_bytes();local_hashes[source]=sha_bytes(data)
        result=project_fusion_collection(json.loads(data))
        # Keep collection shape compatible with the plotting code. Its source
        # binding lives in the explicit public manifest rather than a raw copy.
        target=PUBLIC/'rl'/target_name
        output_hash=atomic_json(target,result)
        bindings.append(dict(source_path=str(source.relative_to(ROOT)),source_sha256=sha_bytes(data),
                             public_path=str(target.relative_to(ROOT)),public_sha256=output_hash))
    if any(sha(path)!=old_hash for path,old_hash in local_hashes.items()):
        raise RuntimeError('Original local research bytes changed during aggregate projection')
    manifest=dict(schema='dispatch-aggregate-v1',producer_sha256=producer_sha256,
        policy='User explicitly authorizes aggregate-only public results; source rows, identities, coordinates, matching memberships and decodable genotypes stay local.',
        local_original_bytes_verified_unchanged=True,bindings=bindings,
        raw_retention='Original files remain at their existing local paths. This projection does not certify an upstream redistribution license.',
        allowlists=dict(run_scalars=RUN_SCALARS,km_scalars=KM_SCALARS,code_input_hashes=CODE_INPUT_HASHES,
                        history=['F','generation','HV'],fusion=['F','seed','t','n_eval','runtime','knee','selected'],
                        note='knee/selected refer only to objective-space point positions; no matching membership is published.'))
    atomic_json(PUBLIC/'projection_manifest.json',manifest)
    print('Public aggregate projections',len(bindings),'original source bytes unchanged')


if __name__=='__main__':
    main()
