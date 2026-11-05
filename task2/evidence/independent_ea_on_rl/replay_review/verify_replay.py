"""Append-only verification of the accidental fixed-model final_v1 replay.

This reads replayed artifacts. It does not train a model, dispatch new requests,
select parameters from test results, modify originals, or replace prior reviews.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import csv
import hashlib
import json
import sys
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import t as student_t

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
TASK=ROOT/'task2'
sys.path.insert(0,str(OUT.parent))
from verify_rl import replay,near,sha,independent_lt
from verify_policy_weights import knee_reference


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot',type=Path,required=True)
    args=parser.parse_args()
    capture=args.snapshot.resolve()
    previous=capture/'surviving_prior_receipts'
    old=json.loads((OUT/'previous_reviews/result.json').read_text())
    saved_hashes=json.loads((OUT/'previous_review_hashes.json').read_text())
    for r in saved_hashes['entries']:
        assert sha(ROOT/r['path'])==r['sha256'],'Prior independent review must remain untouched'
        assert sha(ROOT/r['snapshot'])==r['sha256']
    registry=json.loads((previous/'task2/results/rl/ACTIVE_RUNS.json').read_text())
    old_summary=list(csv.DictReader((previous/'task2/results/rl/SUMMARY.csv').open()))
    old_pairs=json.loads((previous/'task2/results/rl/final_v1/paired_differences.json').read_text())
    old_fronts_path=previous/'task2/public_results/rl/final_fronts.json'
    old_fronts=json.loads(old_fronts_path.read_text())
    new_fronts_path=TASK/'results/rl/final_v1/fusion_fronts.json'
    new_fronts=json.loads(new_fronts_path.read_text())
    old_mapping_path=previous/'task2/results/rl/final_v1/front_episode_mapping.json'
    old_mapping=json.loads(old_mapping_path.read_text())
    current_input_hashes={}
    model_checks=[];seen=set()
    for run in registry['runs']:
        if not run['run_id'].startswith('final_') or run['run_id']=='final_secondary_montecarlo':continue
        for model in run.get('models',[]):
            if model['path'] in seen:continue
            seen.add(model['path']);p=TASK/model['path']
            assert sha(p/'model.npz')==model['model_sha256'],'Fixed trained model changed'
            assert sha(p/'manifest.json')==model['manifest_sha256'],'Original model training manifest changed'
            model_checks.append(dict(path=str(p.relative_to(ROOT)),model_sha256=sha(p/'model.npz'),
                                     manifest_sha256=sha(p/'manifest.json'),matches_prior_registry=True))
    V=np.load(TASK/'results/rl/final_v1/q_f60/model.npz')['V'];LT=independent_lt(V)
    checks=[];day_metrics={};unchanged_trace=unchanged_episode=0;fusion_checked=0
    final_entries=[x for x in old['trace_checks'] if '/results/rl/final_v1/' in x['trace']]
    assert len(final_entries)==95
    for index,entry in enumerate(final_entries):
        tr=ROOT/entry['trace'];ep=ROOT/entry['episode'];directory=tr.parent
        if directory not in day_metrics:
            day_metrics[directory]=json.loads((directory/'day_metrics.json').read_text())
        policy,seed=tr.stem[6:].rsplit('_',1);seed=int(seed)
        expected=next(r for r in day_metrics[directory] if r['policy']==policy and r['day_seed']==seed)
        trace_equal=sha(tr)==entry['trace_sha256'];episode_equal=sha(ep)==entry['episode_sha256']
        assert trace_equal and episode_equal,'A supposedly identical input/trajectory changed'
        unchanged_trace+=int(trace_equal);unchanged_episode+=int(episode_equal)
        is_fusion=policy in ['qnsga_knee','qnsga_constraint']
        obtained,contexts=replay(ep,tr,expected,LT=LT if is_fusion else None,beta=.5 if is_fusion else None)
        near(obtained['served'],entry['served'],'served vs old independent receipt')
        near(obtained['revenue'],entry['revenue'],'revenue vs old independent receipt')
        near(obtained['empty_km'],entry['empty_km'],'empty distance vs old independent receipt')
        if is_fusion:
            mapped=[r for r in old_mapping['rows'] if r['policy']==policy and r['day_seed']==seed]
            for item in mapped:
                frame=new_fronts[item['front_collection']][item['front_ordinal']]
                context=contexts[item['t']]
                assert frame['t']==context['t']
                pairs=list(map(tuple,frame['pairs']))
                assert set(pairs)==set(context['local_pairs'])
                F=np.asarray(frame['F'])
                near(F[frame['selected']],[-sum(context['weights'][a,b] for a,b in pairs),
                                            sum(context['pickup'][a,b] for a,b in pairs)],'replayed selected fusion objective')
                assert frame['n_eval']==1240
                if policy.endswith('knee'):
                    assert frame['selected']==knee_reference(F)
                else:
                    W=np.where(context['feas'],np.maximum(context['weights'],0),0)
                    ii,jj=linear_sum_assignment(-W)
                    budget=.6*sum(context['pickup'][a,b] for a,b in zip(ii,jj) if W[a,b]>0)
                    eligible=np.flatnonzero(F[:,1]<=budget+1e-9)
                    selected=int(eligible[np.argmin(F[eligible,0])]) if len(eligible) else int(F[:,1].argmin())
                    assert selected==frame['selected']
                fusion_checked+=1
        current_input_hashes[str(tr.relative_to(ROOT))]=sha(tr)
        current_input_hashes[str(ep.relative_to(ROOT))]=sha(ep)
        checks.append(dict(trace=str(tr.relative_to(ROOT)),old_and_replay_trace_sha256=sha(tr),
                           episode=str(ep.relative_to(ROOT)),old_and_replay_episode_sha256=sha(ep),
                           metric_path=str((directory/'day_metrics.json').relative_to(ROOT)),
                           old_metric_sha256=entry['metrics_sha256'],replayed_metric_sha256=sha(directory/'day_metrics.json'),
                           policy=policy,day_seed=seed,independent_physics_and_metric_replay=True))
        if (index+1)%15==0:print('independently verified replay traces',index+1,flush=True)
    summaries=[]
    for run in registry['runs']:
        if not run['run_id'].startswith('final_') or run['run_id']=='final_secondary_montecarlo':continue
        directory=TASK/run['path'];d=day_metrics[directory]
        for old_row in [r for r in old_summary if r['run_id']==run['run_id']]:
            subset=[r for r in d if r['policy']==old_row['policy']]
            assert len(subset)==int(old_row['n_simulated_days'])
            scientific=0
            for name,text in old_row.items():
                if name.startswith('runtime_'):continue
                if name.endswith('_mean') or name.endswith('_sample_sd'):
                    suffix='_mean' if name.endswith('_mean') else '_sample_sd'
                    metric=name[:-len(suffix)]
                    values=np.asarray([r[metric] for r in subset],float)
                    actual=float(np.nanmean(values) if suffix=='_mean' else np.nanstd(values,ddof=1))
                    near(actual,float(text),'scientific summary '+name)
                    scientific+=1
            runtimes=np.asarray([r['runtime'] for r in subset])
            summaries.append(dict(run_id=run['run_id'],policy=old_row['policy'],n=len(subset),
                scientific_mean_sd_fields_equal=scientific,
                old_surviving_runtime_mean=float(old_row['runtime_mean']),old_surviving_runtime_sample_sd=float(old_row['runtime_sample_sd']),
                replay_runtime_mean=float(runtimes.mean()),replay_runtime_sample_sd=float(runtimes.std(ddof=1)),
                runtime_identity='Current actual REPLAY timing. Original complete per-seed runtime bytes are unavailable and are not reconstructed.'))
    enhancements=day_metrics[TASK/'results/rl/final_v1/enhancements']
    paired=[]
    for row in old_pairs['rows']:
        a={r['day_seed']:r for r in enhancements if r['policy']==row['candidate']}
        b={r['day_seed']:r for r in enhancements if r['policy']==row['reference']}
        seeds=row['seeds'];diff=np.asarray([a[s][row['metric']]-b[s][row['metric']] for s in seeds])
        near(diff,row['differences'],'saved paired differences')
        n=len(diff);mean=diff.mean();sd=diff.std(ddof=1);half=student_t.ppf(.975,n-1)*sd/np.sqrt(n)
        near([mean,sd,mean-half,mean+half],[row['mean_difference'],row['sample_sd'],row['descriptive_t95_low'],row['descriptive_t95_high']],
             'paired mean/sampleSD/t95 vs original surviving receipt')
        paired.append(dict(candidate=row['candidate'],reference=row['reference'],metric=row['metric'],
                           n=n,all_differences_and_statistics_equal=True))
    fusion_runtime_changed=0;fusion_fields=0
    for label in ['knee','constraint']:
        assert len(old_fronts[label])==len(new_fronts[label])
        for before,after in zip(old_fronts[label],new_fronts[label]):
            for key,value in before.items():
                if key=='runtime':
                    fusion_runtime_changed+=int(value!=after[key])
                else:
                    assert after[key]==value,f'Fusion scientific field changed: {key}'
                    fusion_fields+=1
    original_review_checks=[]
    for r in saved_hashes['entries']:
        assert sha(ROOT/r['path'])==r['sha256']
        original_review_checks.append(dict(path=r['path'],sha256=r['sha256'],unchanged=True))
    result=dict(identity='REPLAY_RECOMPUTE_SAME_FROZEN_MODELS_NOT_A_NEW_INDEPENDENT_TEST',
        reviewer='/root/evolution',role='Independent appended verification; original RL author is /root/reinforcement',
        verifier_sha256=sha(__file__),completed_utc=datetime.now(timezone.utc).isoformat(),
        capture_manifest_sha256=sha(capture/'capture_manifest.json'),
        replayed_final_trace_count=len(checks),trace_bytes_equal_to_prior_review=unchanged_trace,
        episode_bytes_equal_to_prior_review=unchanged_episode,trace_checks=checks,
        model_and_original_training_manifest_checks=model_checks,scientific_summary_checks=summaries,
        paired_comparison_rows_checked=paired,selected_dynamic_fusion_frames_rechecked=fusion_checked,
        fusion=dict(previous_public_front_sha256=sha(old_fronts_path),replayed_full_front_sha256=sha(new_fronts_path),
                    old_full_front_sha256=old_mapping['source_front_sha256'],
                    scientific_aggregate_fields_equal=fusion_fields,frame_runtime_values_changed=fusion_runtime_changed,
                    scope='Full F/t/selected/evaluation-count sequences agree with the surviving pre-replay public projection; selected pairs independently agree with byte-identical old trajectories. Full original raw runtime/serialization bytes are not claimed recovered.'),
        preserved_original_reviews=original_review_checks,
        exclusions=['No model training or parameter selection occurred in this reviewer task.',
                    'MOO, development and secondary20MonteCarlo results are outside the accidental replay and were not rerun.',
                    'Original complete raw day-metric bytes/runtimes are unavailable; old hashes remain historical evidence.',
                    'New artifact hashes must replace affected active bindings; old independent receipt hashes must remain unchanged.'],
        status='PASS_SCIENTIFIC_EQUIVALENCE_WITH_ACTUAL_REPLAY_TIMING_AND_NEW_HASHES')
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print('REPLAY review passed:',len(checks),'traces;',len(summaries),'policy summaries;',len(paired),'paired rows;',fusion_checked,'fusion frames')


if __name__=='__main__':main()
