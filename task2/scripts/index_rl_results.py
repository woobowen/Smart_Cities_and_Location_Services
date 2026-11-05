"""Explicit active-run registry; old Double outputs cannot enter canonical means."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import pandas as pd
TASK=Path(__file__).resolve().parents[1]
ROOT=TASK/'results/rl'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    records=[];summary=[]
    replay_path=ROOT/'final_v1/REPLAY_RECEIPT.json'
    replay=json.loads(replay_path.read_text()) if replay_path.exists() else None
    def add(name,path,identity,active=True,models=(),note=''):
        path=ROOT/path;metrics=path/'day_metrics.json'
        if not metrics.exists():return
        row=dict(run_id=name,path=str(path.relative_to(TASK)),identity=identity,active=active,
                 metrics_path=str(metrics.relative_to(TASK)),metrics_sha256=sha(metrics),
                 note=note,models=[],producer_metadata=[])
        row['execution_identity']=replay['identity'] if replay and path.is_relative_to(ROOT/'final_v1') else 'ORIGINAL_RECORDED_RUN'
        if replay and path.is_relative_to(ROOT/'final_v1'):
            row['replay_receipt']=str(replay_path.relative_to(TASK))
            row['note']+='; Samefrozenprimary5replayed, scientificvaluesunchanged; currentelapsedtimesareReplaymeasurements, notanewindependenttest.'
        for model in models:
            m=ROOT/model;mf=m/'manifest.json';npz=m/'model.npz'
            if npz.exists():
                source=json.loads(mf.read_text())
                row['models'].append(dict(path=str(m.relative_to(TASK)),model_sha256=sha(npz),manifest_sha256=sha(mf),source_hashes_at_execution=source.get('code_hashes',{})))
        for key in ['manifest.json','followup_manifest.json','contract.json','fusion_contract.json']:
            f=path/key
            if f.exists():row['producer_metadata'].append(dict(path=str(f.relative_to(TASK)),sha256=sha(f),content=json.loads(f.read_text())))
        records.append(row)
        if active:
            d=pd.DataFrame(json.loads(metrics.read_text()))
            for policy,g in d.groupby('policy'):
                s=dict(run_id=name,identity=identity,execution_identity=row['execution_identity'],policy=policy,n_simulated_days=len(g),statistical_unit='sampled_simulated_day_within_this_run')
                for k in ['revenue','completed_revenue','answer_rate','avg_pickup','pickup_km','empty_km','empty_minutes','reposition_count','served','completed','outstanding','canceled','horizon_unassigned','nonpositive_fraction','runtime']:
                    if k in g:
                        s[k+'_mean']=float(g[k].mean());s[k+'_sample_sd']=float(g[k].std(ddof=1))
                summary.append(s)
    add('pilot','pilot_v1/pilot_validation','development',models=['pilot_v1/pilot_q'],note='10actual episodes, cost pilot, never pooled with teacher300episode runs')
    for fleet in [40,60,100]:
        add(f'baseline_f{fleet}','development_v1/'+f'baseline_f{fleet}_s2024','development',models=[f'development_v1/q_f{fleet}_s2024'],note='Valid original Q-only code; separate-RNG fix does not change this branch, parity recorded')
    base='development_v1/q_f60_s2024'
    for name in ['beta_validation_v1','reposition_validation_v1','reposition_cost_validation_v1','component_ablation_v1']:
        add(name,name,'development',models=[base],note='Same learnedV, distinct controlled validation intervention; overlapping simulated seeds are not independent additional days')
    for c in ['gamma08','gamma095','grid6','grid10','patience1','patience3']:
        old=f'sensitivity_v1/{c}_validation';new=f'sensitivity_v2_rngfix/{c}_validation'
        if (ROOT/old/'day_metrics.json').exists():add('sensitivity_'+c,old,'development',models=[f'sensitivity_v1/{c}'])
        elif (ROOT/new/'day_metrics.json').exists():add('sensitivity_'+c,new,'development',models=[f'sensitivity_v2_rngfix/{c}'])
    for seed in range(2024,2029):
        for learner in ['q','double']:
            name=f'{learner}_b1_s{seed}';new=f'double_v2_rngfix/{name}_validation'
            model=f'double_v2_rngfix/{name}'
            if not (ROOT/model/'manifest.json').exists():model=f'double_validation_v1/{name}'
            add('fair_'+name,new,'development',models=[model],note='Behavior RNG separate from Double update coin; Q-only predecessor reused when valid')
            old=f'double_validation_v1/{name}_validation'
            add('old_'+name,old,'invalid' if learner=='double' else 'historical_equivalent',active=False,
                models=[f'double_validation_v1/{name}'],note='INVALID_FOR_FAIR_DOUBLE_COMPARE: shared update/behavior RNG' if learner=='double' else 'Valid original Q-only, duplicated by explicitly registeredv2 evaluation; excluded from canonical tables')
    for seed in range(2024,2029):
        model=f'movement_trainseed_confirmation_v1/q_s{seed}' if seed!=2024 else base
        add(f'movement_trainseed_{seed}',f'movement_trainseed_confirmation_v1/validation_s{seed}','development',models=[model])
    add('offset_robustness','offset_robustness_v1/validation','development',models=['offset_robustness_v1/q_filtered'],note='UTC-consistent training subset sensitivity; teacher-local-clock main identity unchanged')
    add('fusion_dynamic','fusion_validation_v1/dynamic','development',models=[base],note='Actual full-day NSGA40pop30gen per dispatch; estimated objective never called realized revenue')
    for fleet in [40,60,100]:add(f'final_fleet{fleet}',f'final_v1/fleet{fleet}','final',models=[f'final_v1/q_f{fleet}'])
    add('final_enhancements','final_v1/enhancements','final',models=['final_v1/q_f60','final_v1/q_beta1','final_v1/double_beta1'])
    add('final_secondary_montecarlo','final_montecarlo_v1','final',models=['final_v1/q_f60'],note='20new simulated resampling seeds60000–60019; fixed model/parameters, separate from primary5; not new real dates or trained models')
    final_complete=(ROOT/'final_v1/completion_manifest.json').exists()
    verification=[]
    for filename in ['result.json','policy_result.json']:
        p=TASK/'evidence/independent_ea_on_rl'/filename
        if p.exists():
            v=json.loads(p.read_text())
            verification.append(dict(path=str(p.relative_to(TASK)),sha256=sha(p),status=v.get('status'),reviewer=v.get('reviewer'),scope='Only actual listed source, traces, policies and statistics; see full independent report'))
    if replay:
        for filename in ['result.json','recovered_front_result.json','cli_guard_independent.json','public_binding_result.json']:
            p=TASK/'evidence/independent_ea_on_rl/replay_review'/filename
            if p.exists():
                v=json.loads(p.read_text())
                verification.append(dict(path=str(p.relative_to(TASK)),sha256=sha(p),status=v.get('status'),reviewer=v.get('reviewer'),scope='Append-only replay/CLI/public-binding verification. Originalreview remains historical inits actualhashscope.'))
    index=dict(generated_utc=datetime.now(timezone.utc).isoformat(),schema=1,
               state='FINAL_CONFIRMATION_EXECUTED' if final_complete else 'DEVELOPMENT_EXECUTED_FINAL_PENDING',
               active_day_metrics=[r['metrics_path'] for r in records if r['active']],
               path_base='task2 (repository relative path = task2/ + entry path)',
               identities={'development':'training/validation/selection; never held-out confirmation','final':'frozen candidates, held-out dates; no retuning','invalid':'retained failure/history; excluded','historical_equivalent':'valid predecessor retained, excluded to avoid duplicate pooling'},
               producer_script_sha256=sha(__file__),runs=records,
               independent_verifications=verification,
               replay_receipt=dict(path=str(replay_path.relative_to(TASK)),sha256=sha(replay_path)) if replay else None,
               pending='Final evaluation index appears only after actual metrics exist; external verifier records separately')
    (ROOT/'ACTIVE_RUNS.json').write_text(json.dumps(index,ensure_ascii=False,indent=2))
    table=pd.DataFrame(summary);table.to_csv(ROOT/'SUMMARY.csv',index=False)
    lines=['# RL canonical result index','',f'{len(records)} registered run identities; {sum(r["active"] for r in records)} active day-metric tables. All dates/partitions and seeds retained separately.','',
           'Author: native reinforcement child. Author tests are not independent review; independent audit is stored under evidence/independent_ea_on_rl.','',
           'Primary data = teacher-local-clock Foursquare check-in proxy, conditional localkm/Manhattan teaching model. Accepted fare is dispatch-time proxy income; completed and outstanding counts are distinct.','',
           'Canonical machine index: ACTIVE_RUNS.json. Canonical numerical summary: SUMMARY.csv. Never rglob old experiment files into an aggregate.','',
           '|Run|Identity|Active|Day metrics|','|---|---|---|---|']
    if replay:
        lines[2:2]=['**Primary final execution identity: REPLAY / RECOMPUTE of the same frozenfive simulations.** Root accidentally invoked an old script with ignored `--help`; the models, inputs, selection and scientificvalues are unchanged. Currentruntimevaluesreplaceelapsedmeasurements; no extra independenttest or newtraining occurred. Originalreview, oldsummarystatistics andreceipts remain archived; unavailableoldindividualruntimes are not reconstructed. See `final_v1/REPLAY_RECEIPT.json` and append-only independentreplay review.','']
    lines += [f'|{r["run_id"]}|{r["identity"]}|{r["active"]}|{r["metrics_path"]}|' for r in records]
    if final_complete:
        lines += ['','## Frozen held-out confirmation','',
                  'Candidates were frozen in evidence/rl/FINAL_SELECTION.json before held-out outcomes were opened. Each row below averages five paired sampled simulated days; the dates are held out, the simulations are not five real operating days. Fare is accepted-at-dispatch proxy currency.','',
                  '|Fleet/run|Policy|Fare mean|Response|Pickup km|Empty reposition km|','|---|---|---:|---:|---:|---:|']
        for s in summary:
            if s['identity']=='final':
                lines.append(f'|{s["run_id"]}|{s["policy"]}|{s["revenue_mean"]:.2f}|{s["answer_rate_mean"]:.5f}|{s["avg_pickup_mean"]:.3f}|{s["empty_km_mean"]:.2f}|')
        lines += ['','No retuning follows these held-out observations. The selected gross-revenue candidate may lose on other metrics; see empty distance, response, and pickup separately. Hypothetical diagnostic net revenue is not measured real profitability.']
    else:
        lines += ['','## Current state','','All baseline, sensitivity, component, Double, and fusion development runs are real. Final held-out evaluation has not yet completed; no final PASS is asserted.']
    if len([s for s in summary if s['run_id'].startswith('fair_') and s['policy']=='beta1'])==10:
        lines += ['','## Double Q development replication','',
                  'Five distinct training seeds, each evaluated on five common validation simulations. Independent behavior/update random streams; old shared-stream Double results excluded.','',
                  '|Learner at beta1|Mean across training-seed day means|Response|Nonpositive feasible-edge fraction|','|---|---:|---:|---:|']
        for learner in ['q','double']:
            d=table[(table.run_id.str.startswith('fair_'+learner+'_')) & (table.policy=='beta1')]
            lines.append(f'|{learner}|{d.revenue_mean.mean():.2f}|{d.answer_rate_mean.mean():.5f}|{d.nonpositive_fraction_mean.mean():.5f}|')
        lines += ['','Double improves beta1 revenue here but lowers response. DescriptiveV minus realized-policy-return gap averages42.00 forQ vs2.89 forDouble; policies and visited states differ, so this is not an unbiased optimal-value error estimate.']
    lines += ['','## Independent verification','','Native independent context `/root/evolution` verified the listed375rawtrace simulations with its own event reconstruction, fullLT/Double hand calculations, actual weightedpolicy and NSGA selection/objectives, and primary/secondarypaired statistics. Reports bind actual source/model/trace hashes; the status is limited to their stated scope.']
    lines += [f'- [{v["path"]}](../../{v["path"]}): {v["status"]}' for v in verification]
    lines += ['','Interpretation and all teacher thought-question answers: `../../evidence/rl/TEACHER_QUESTIONS_AND_LIMITS.md`; result-triggered decisions: `../../evidence/rl/DECISIONS.md`.','',
              'The final confirmation section is added only when final_v1 actually exists. Original Q-only results retain their execution hash; exact Q/V/N/NV/curve/TD/episode-array parity under the Double-only RNG fix is recorded in evidence/rl/history_rngfix/parity.json. Old shared-RNG Double outputs are explicitly invalid for the fair comparison.']
    (ROOT/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print('registered',len(records),'active',sum(r['active'] for r in records))
if __name__=='__main__':main()
