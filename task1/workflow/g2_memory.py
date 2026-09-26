"""Verified demonstration memory. Evaluation receives an immutable snapshot."""
from copy import deepcopy
import math
from pathlib import Path
from .io import ROOT, read_json, write_json, digest, object_hash, now, bound_path


def feature_vector(card):
    edges=max(0,card['n_points']-1)
    if edges==0 or card['median_positive_dt'] is None:
        return None
    return [math.log1p(card['n_points']),math.log1p(card['span_work_m']),
            math.log1p(card['median_positive_dt']),card['zero_dt_edges']/edges,
            card['adjacent_duplicate_edges']/edges,card['raw_break_edges']/edges]


def build_snapshot(path, entries, split, cards, contract_hash):
    path=Path(path)
    if path.exists():raise ValueError('MEMORY_SNAPSHOT_ALREADY_EXISTS')
    expected=set(split['splits']['DEMO_MEMORY'])
    if len(entries)!=len(expected) or {e['record_id'] for e in entries}!=expected:
        raise ValueError('MEMORY_DEMO_SCOPE_MISMATCH')
    clean=[]
    from .g2_data import raw_data,adapt
    from .g2_metrics import review_record
    from .g2_experiments import read_gzip,compact_metrics
    raw=raw_data()
    for entry in entries:
        if entry['engineering_status']!='VERIFIED' or not entry.get('review_sha256'):
            raise ValueError('UNVERIFIED_MEMORY_ADMISSION')
        rid=entry['record_id'];card=cards[rid]
        trace_path=bound_path(ROOT,entry['trace_path']);review_path=bound_path(ROOT,entry['review_path'])
        if digest(trace_path)!=entry['trace_sha256'] or digest(review_path)!=entry['review_sha256']:
            raise ValueError('MEMORY_ADMISSION_ARTIFACT_CHANGED')
        trace=read_gzip(trace_path);receipt=read_json(review_path)
        if receipt['status']!='VERIFIED' or receipt['target_hash']!=object_hash(trace):
            raise ValueError('MEMORY_ADMISSION_REVIEW_TARGET_MISMATCH')
        provenance=entry['trusted_provenance']
        if provenance['partition']!='DEMO_MEMORY' or provenance['raw_sha256']!=split['raw_sha256']:
            raise ValueError('MEMORY_ADMISSION_PARTITION_MISMATCH')
        audit=review_record(trace,adapt(rid,raw[rid]),expected_parameters=entry['selected_parameters'],
            expected_order='S-D-P',contract_hash=contract_hash,trusted_provenance=provenance)
        if audit['status']!='VERIFIED' or compact_metrics(trace['metrics'])!=entry['selected_metrics']:
            raise ValueError('MEMORY_ADMISSION_INDEPENDENT_RECHECK_FAILED')
        clean.append({**deepcopy(entry),'memory_id':'DEMO-'+rid,'partition':'DEMO_MEMORY',
            'record_content_sha256':card['record_content_sha256'],'stratum':card['stratum'],
            'features':feature_vector(card),'contract_sha256':contract_hash,
            'raw_sha256':split['raw_sha256']})
    vectors=[e['features'] for e in clean if e['features'] is not None]
    scales=[{'min':min(v[j] for v in vectors),'max':max(v[j] for v in vectors)} for j in range(6)]
    selected=[e['selected_parameters'] for e in clean]
    procedures={p:{'min':min(v[p] for v in selected),'max':max(v[p] for v in selected),
                   'values':sorted({v[p] for v in selected}),
                   'meaning':'range among verifier-selected demonstration outcomes; not a validated universal rule'}
                for p in selected[0]}
    snapshot={'snapshot_id':'G2_DEMO_MEMORY_V1','frozen_at':now(),'raw_sha256':split['raw_sha256'],
              'contract_sha256':contract_hash,'split_sha256':object_hash(split),
              'entries':clean,'feature_scales':scales,'procedural_memory':procedures,
              'human_knowledge':[],
              'human_knowledge_reason':'No separate user-authored case notes; real user/teacher definitions remain in the common contract',
              'working_memory_persisted':False,'evaluation_policy':'READ_ONLY'}
    write_json(path,snapshot,exclusive=True)
    return snapshot


class FrozenMemory:
    def __init__(self,path,expected_hash,contract_hash,split):
        self.path=Path(path);self.expected_hash=expected_hash
        if digest(self.path)!=expected_hash:raise ValueError('MEMORY_HASH_MISMATCH')
        self._snapshot=read_json(path);self._snapshot_content_hash=object_hash(self._snapshot)
        self.contract_hash=contract_hash;self.split=deepcopy(split)
        if self.snapshot['contract_sha256']!=contract_hash or self.snapshot['raw_sha256']!=split['raw_sha256']:
            raise ValueError('MEMORY_VERSION_MISMATCH')
        if self.snapshot['split_sha256']!=object_hash(split):raise ValueError('MEMORY_SPLIT_MISMATCH')

    def write(self,*args,**kwargs):
        raise PermissionError('EVALUATION_MEMORY_READ_ONLY')

    @property
    def snapshot(self):
        return deepcopy(self._snapshot)

    def verify_unchanged(self):
        if digest(self.path)!=self.expected_hash:raise ValueError('MEMORY_CHANGED_DURING_EPISODE')
        if object_hash(self._snapshot)!=self._snapshot_content_hash:raise ValueError('MEMORY_IN_PROCESS_CONTENT_CHANGED')
        return self.expected_hash

    def retrieve(self,card,limit=3):
        if type(limit) is not int or not 1<=limit<=3:raise ValueError('FROZEN_RETRIEVAL_LIMIT_EXCEEDED')
        self.verify_unchanged();vector=feature_vector(card);eligible=[];rejected=[]
        for entry in self.snapshot['entries']:
            reasons=[]
            if entry['record_id']==card['record_id'] or entry['record_content_sha256']==card['record_content_sha256']:
                reasons.append('SAME_PARENT_RECORD_OR_EXACT_DUPLICATE')
            if entry['record_id'] not in self.split['splits']['DEMO_MEMORY'] or entry['partition']!='DEMO_MEMORY':
                reasons.append('NOT_DEMO_MEMORY')
            if entry['contract_sha256']!=self.contract_hash or entry['raw_sha256']!=self.split['raw_sha256']:
                reasons.append('WRONG_DATA_OR_CONTRACT')
            if entry['engineering_status']!='VERIFIED':reasons.append('NOT_VERIFIED')
            if entry['stratum']!=card['stratum']:reasons.append('STRATUM_NOT_APPLICABLE')
            if vector is None or entry['features'] is None:reasons.append('DIAGNOSTIC_FEATURE_UNAVAILABLE')
            if reasons:
                rejected.append({'memory_id':entry['memory_id'],'reasons':reasons});continue
            squared=0.0
            for a,b,scale in zip(vector,entry['features'],self.snapshot['feature_scales']):
                width=scale['max']-scale['min']
                if width:squared+=((a-b)/width)**2
            eligible.append((math.sqrt(squared),entry['memory_id'],entry))
        eligible.sort(key=lambda e:(e[0],e[1]))
        delivered=[{**deepcopy(e),'retrieval_distance':d} for d,_,e in eligible[:limit]]
        return {'query_record_id':card['record_id'],'snapshot_sha256':self.expected_hash,
                'eligible_count':len(eligible),'filtered':rejected,'delivered':delivered,
                'empty_reason':None if delivered else 'NO_APPLICABLE_VERIFIED_DEMONSTRATION'}


def consumption(retrieval,response):
    delivered={e['memory_id']:e for e in retrieval['delivered']}
    cited=response.get('memory_ids_used',[])
    valid=[m for m in cited if m in delivered]
    invalid=[m for m in cited if m not in delivered]
    used=[]
    for m in valid:
        memory=delivered[m]
        for proposal in response['proposals']:
            if proposal['parameters']==memory['selected_parameters']:
                used.append({'memory_id':m,'candidate_id':proposal['candidate_id'],
                             'kind':'CITED_AND_PARAMETERS_MATCH_VERIFIED_OUTCOME'})
    return {'retrieved_eligible':retrieval['eligible_count'],'delivered_ids':list(delivered),
            'model_cited_valid':valid,'model_cited_invalid':invalid,'action_consistent':used,
            'causal_benefit_proven':False}
