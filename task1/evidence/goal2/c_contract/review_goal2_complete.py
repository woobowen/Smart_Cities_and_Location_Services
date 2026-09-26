"""C's independent full Goal2 prepublication acceptance from immutable snapshots.

Must be supplied the root's exact reviewed targets and as-of snapshots after all
17 prerequisite tasks have been verified. It checks the complete target/source
hash graph and requirements; prior C raw/math evidence is reused explicitly.
Actual publication and the external GPT review remain unchecked.
"""
import argparse
from collections import Counter
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from review_development_runs import Audit
from task1.workflow.io import read_json,write_json,digest,object_hash,now
from task1.workflow.g2_journal import REQUIRED_COMPONENTS,task_sources
OUT=Path(__file__).parent;EV=ROOT/'task1/evidence/goal2'
MAPPING={
 'A01':(['contract','analysis'],'Unique R01-R10 source/experiment/artifact/review mapping; prepublication R10 boundary explicit.'),
 'A02':(['handoff'],'Raw/teacher/starter/G1/user archives unchanged; independent seven exposed pilot regression matches approved contract.'),
 'A03':(['contract','split','evaluation_freeze'],'Record-grouped frozen split, predeclared scopes and no G3 method run; all eval parents frozen beforehand.'),
 'A04':(['development_parameters','evaluation_parameters'],'59 full development configurations and14 frozen evaluation configurations; complete record denominators and teacher optional experiments.'),
 'A05':(['development_orders','evaluation_orders'],'Six actual development stage permutations, four constraint rejections, two frozen evaluation orders; actual raw break and neighborhood failure evidence.'),
 'A06':(['development_modes','evaluation_modes'],'Real CLI/model evidence for three LLM structures, strict zero-model deterministic search; formal four modes times24records times3episodes.'),
 'A07':(['development_modes','evaluation_modes'],'Per-record20 budget, at most3feedback rounds, true raw proposal legality/fallback accounting, actual causal contexts and isolated mode feedback.'),
 'A08':(['memory','development_modes','evaluation_modes'],'60 DEMO records, independent admission, frozen unchanged snapshot, source/scope applicability and real retrieval/consumption, leakage and write refusal.'),
 'A09':(['candidates'],'Three independently confirmed single groups; shared reference computations explicit, optional structures not admitted with reasons; no final enhanced combination.'),
 'A10':(['core','analysis'],'Independent raw common reference and DP immediate reference/denominator, null reasons, point identities, full per-record aggregation and paired differences; conditional coordinate verification.'),
 'A11':(['counterexamples'],'19 authored synthetic executions with25known answers,10exposedpilot executions,6real model citations with actual before/after metrics; synthetic/real/history separated.'),
 'A12':(['core','analysis'],'All13actual issues closed with independent receipts and parent resumption; context bug triggered new code and rebuilt real LIVE decisions; test faults labelled separately.'),
 'A13':(['notebooks','core'],'Three real fresh kernels and21code cells;17,401raw deterministic recomputations; actual zero-call sentinel; full production and independent fault regression tests407passed.'),
 'A14':(['notebooks','figures','analysis'],'All current seven runs,39tables/111053rows,three notebooks,11figures and stage analysis tied to one processing epoch plus exact presentation source versions.'),
 'A15':(['figures'],'All11native PNG and200dpi PDF renders actually viewed;44exports and C rerender bytes verified; native draw.io11vertices13edges editable and mapped to actual modules.'),
 'A16':(['analysis','candidates','counterexamples'],'Negative results, coverage/geometric tradeoffs, unknown datum/no noise truth and bounded search limits explicit; no causal memory/accuracy/global-optimality claim.'),
 'A17':([],'Reviewed complete release scan plus delta, protected files, secrets/size/cache/links/dependencies/upload bundle and source commit binding; actual push/readback follows acceptance.')}

def bound(path):return {'path':str(path.resolve().relative_to(ROOT)),'sha256':digest(path)}
def read_binding(binding):
 p=ROOT/binding['path'];assert digest(p)==binding['sha256'];value=read_json(p)
 if binding.get('representation')=='json_wrapper_content':
  assert value['source_path']==binding['source_path'] and value['source_sha256']==binding['source_sha256_at_capture']
  original=(json.dumps(value['content'],ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
  assert hashlib.sha256(original).hexdigest()==binding['source_sha256_at_capture']
  return value['content']
 return value
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--targets',type=Path,required=True);args=parser.parse_args();start=time.perf_counter();a=Audit()
 registry=read_json(args.targets);submitted=registry['targets'];snaps=registry['snapshots']
 for t in submitted:a.check('all_submitted_immutable_targets',digest(ROOT/t['path'])==t['sha256'],t['path'])
 for name,b in snaps.items():a.check('asof_snapshot_binding',digest(ROOT/b['path'])==b['sha256'],name)
 state=read_binding(snaps['goal_state']);requirements=read_binding(snaps['requirements']);reviewed_tasks={};task_targets=set()
 a.check('no_mutable_self_reference',not any(t['path'] in ('task1/evidence/goal2/goal_state.json','task1/evidence/goal2/requirements.json') for t in submitted))
 prerequisites=set(state['tasks'])-{'internal_acceptance','publication'}
 a.check('seventeen_prerequisite_tasks',len(prerequisites)==17)
 for task in sorted(prerequisites):
  row=state['tasks'][task];a.check('task_is_verified:'+task,row['status']=='VERIFIED')
  for t in row['evidence']+[row['review']]:a.check('task_target_current_hash',digest(ROOT/t['path'])==t['sha256'],t['path']);task_targets.add(t['path'])
  receipt=read_json(ROOT/row['review']['path']);item=receipt.get('tasks',{}).get(task,receipt)
  a.check('real_independent_receipt:'+task,receipt['role_context']=='/root/c_contract' and item['status']=='VERIFIED' and not item.get('errors'))
  a.check('required_components_complete:'+task,set(REQUIRED_COMPONENTS[task])<=set(item['checked_components']))
  a.same('exact_task_source_dependencies:'+task,sorted(row['source_hashes']),sorted(task_sources(task)))
  a.same('review_source_epoch:'+task,item['source_hashes'],row['source_hashes'])
  for p,sha in row['source_hashes'].items():a.check('current_task_source_bytes',digest(ROOT/p)==sha,p)
  a.check('actual_target_set_bound:'+task,{object_hash(t) for t in row['evidence']}<={object_hash(t) for t in item['targets']})
  a.check('dependency_closure:'+task,all(state['tasks'][x]['status']=='VERIFIED' for x in row['depends_on']))
  reviewed_tasks[task]=row['review']
 a.check('external_status_not_forged',state['gpt_second_review']=='PENDING' and state['submission']=='NOT_READY' and state['tasks']['publication']['status']!='VERIFIED')
 a.check('active_controller_exact_submitted176_targets',len(submitted)==176 and read_json(EV/'goal_state.json')['tasks']['internal_acceptance']['evidence']==submitted)
 a.check('pending_external_review_and_submission',requirements['gpt_second_review']=='PENDING' and requirements['submission']=='NOT_READY' and requirements['publication_status']=='NOT_PUBLISHED')
 governance=read_binding(snaps['governance']);progress=read_binding(snaps['progress'])
 a.check('governance_dispatches_separate_from_experiment_model_calls',governance['scope']=='governance; never experiment model calls' and governance['governance_role_dispatches']==len(governance['role_dispatches']))
 a.check('native_roles_have_visible_distinct_dispatches',{'a_contract','b_engine','c_contract'}<={r['target'] for r in governance['role_dispatches']} and all(r['tool_result_present'] for r in governance['role_dispatches']))
 a.check('inflight_and_open_issues_empty',progress['inflight'] is None and not progress['open_issues'] and state['inflight'] is None)
 reqs=requirements['requirements'];a.same('unique_R01_R10',[r['id'] for r in reqs],['R%02d'%i for i in range(1,11)])
 a.check('prompt_authority_not_human_fabrication',requirements['current_authority']['internal_A_C_is_human_approval'] is False)
 for r in reqs:
  a.check('complete_requirement_mapping',bool(r['sources']) and bool(r['artifacts']) and bool(r['conclusion_boundary']),r['id'])
  if r['id']=='R10':
   a.check('R10_prepublication_review_is_future_not_fabricated',r['status']=='INTERNAL_ACCEPTANCE_PENDING' and not r['review_evidence'] and {'independent_C_A01_A17','publication_receipt','fixed_SHA_review_packet','FINAL_RESPONSE'}<=set(r['planned_artifact_roles']) and state['tasks']['publication']['status']!='VERIFIED')
  else:a.check('R01_R09_complete_review_mapping',bool(r['review_evidence']),r['id'])
  for p in r['artifacts']+r['review_evidence']:a.check('requirement_entry_resolves', (ROOT/p).is_file(),p)
 contractpath=ROOT/'task1/config/goal2/contract.json';contract=read_json(contractpath);splitpath=EV/'data/split_manifest.json';split=read_json(splitpath);freeze=read_json(EV/'evaluation_freeze.json')
 rawpath=ROOT/contract['raw_path'];a.check('trusted_raw_hash',digest(rawpath)==contract['raw_sha256']);raw=read_json(rawpath)
 a.check('raw_complete_readonly_inventory',len(raw)==11386 and sum(len(v[0]) for v in raw.values())==1173410)
 memberships={rid:k for k,ids in split['splits'].items() for rid in ids}
 a.same('split_sizes',{k:len(v) for k,v in split['splits'].items()},{'PILOT_REGRESSION':7,'DEMO_MEMORY':60,'DEVELOPMENT':120,'G2_EVAL':120,'G3_RESERVED':11079})
 a.check('complete_unique_record_partition',len(memberships)==11386 and sum(map(len,split['splits'].values()))==11386 and set(memberships)==set(raw))
 code=read_json(EV/'code_freeze.json');a.check('processing_code_sha',code['code_sha']=='c1c6272606716f9f59aa785d48bfeadb09c7a30e')
 for p,sha in code['processing_source_hashes'].items():
  a.check('processing_tree_unchanged',digest(ROOT/p)==sha)
  committed=subprocess.check_output(['git','show',code['code_sha']+':'+p],cwd=ROOT);a.check('actual_COMMITTED_processing_bytes',hashlib.sha256(committed).hexdigest()==sha,p)
 a.same('evaluation_processing_freeze',freeze['processing_source_hashes'],code['processing_source_hashes'])
 current=read_json(EV/'current_runs.json');scope={};total=0
 expected={'parameter_development':('DEVELOPMENT',59,7080),'order_development':('DEVELOPMENT',6,720),'memory':('DEMO_MEMORY',20,1200),
  'mode_development':('DEVELOPMENT',12,1218),'evaluation_parameters':('G2_EVAL',14,1680),'evaluation_orders':('G2_EVAL',2,240),'mode_evaluation':('G2_EVAL',36,3583)}
 for key,(partition,n,count) in expected.items():
  directory=EV/'runs'/current[key];m=read_json(directory/'manifest.json');a.check('current_run_complete',m['status'] in ('REVIEW_PENDING','VERIFIED'))
  a.check('no_G3_run',m['partition']==partition and all(memberships[r]==partition for r in m['input_ids']))
  if 'mode_episodes' in m:
   a.check('actual_complete_batches',len(m['mode_episodes'])==n);observations=Counter();calls=Counter();calcs=0
   for e in m['mode_episodes']:
    p=directory/e['path'];a.check('episode_current_binding',digest(p)==e['sha256']);ep=read_json(p)
    for rid in ep['input_ids']:observations[(ep['mode'],ep['episode'],rid)]+=1
    calls[ep['mode']]+=ep['resources']['experiment_model_dispatches'];calcs+=ep['resources']['candidate_evaluations']
   nrepeat=1 if key=='mode_development' else 3;llmids=split['llm_subsets'][partition]
   a.check('identical_mode_scope_repetitions',set(observations)=={(mode,episode,rid) for mode in ('llm-only','search-only','llm+search','llm+memory+search') for episode in range(1,nrepeat+1) for rid in llmids} and set(observations.values())=={1})
   a.same('visible_mode_dispatches',dict(calls),{'llm-only':3*nrepeat,'search-only':0,'llm+search':9*nrepeat,'llm+memory+search':9*nrepeat})
   a.check('actual_candidate_denominator',calcs==count)
  else:
   a.check('complete_configs_or_orders',len(m['artifacts'])==n)
   a.check('all_batch_full_partition',all(e['input_ids']==split['splits'][partition] for e in m['artifacts'].values()))
   a.check('actual_record_config_denominator',sum(len(e['input_ids']) for e in m['artifacts'].values())==count)
  scope[key]={'run_id':m['run_id'],'partition':partition,'record_configurations':count};total+=count
 a.check('all15721_current_configurations',total==15721)
 # Actual issue chronology: an independent closure must precede the current
 # accepted parent task, whose current source epoch is verified above.
 events=state['events']
 previous='ROOT'
 for i,event in enumerate(events):
  payload={k:v for k,v in event.items() if k!='hash'}
  a.check('actual_controller_hash_chained_events',event['sequence']==i and event['previous_hash']==previous and object_hash(payload)==event['hash'])
  previous=event['hash']
 for iid,issue in state['issues'].items():
  a.check('no_open_actual_issue',issue['status']=='VERIFIED' and issue['verifier']=='C:/root/c_contract' and issue['repairer']!='C:/root/c_contract',iid)
  a.check('issue_has_recorded_fact_and_clause',all(issue.get(k) for k in ('fact','violated_clause','affected_artifacts','repairer','source')))
  for target in issue['closure_evidence']:
   a.check('closed_issue_receipt_preserved',digest(ROOT/target['path'])==target['sha256'])
   receipt=read_json(ROOT/target['path']);part=receipt.get('issues',{}).get(iid,receipt)
   a.check('independent_issue_closure',receipt['role_context']=='/root/c_contract' and part['status']=='VERIFIED' and {'fault_rejected','valid_receipt_accepted','source_epoch'}<=set(part['checked_components']))
  closed=[i for i,e in enumerate(events) if e.get('issue_id')==iid and e.get('kind',e.get('event'))=='C_VERIFIED_PARENT_RESUMED']
  a.check('actual_parent_resumed_event',bool(closed),iid)
  if closed:a.check('parent_verified_after_issue_closure',any(i>closed[-1] and e.get('task')==issue['parent_task'] and e.get('kind',e.get('event'))=='TASK_VERIFIED' for i,e in enumerate(events)),iid)
 a.check('thirteen_real_closed_issues',len(state['issues'])==13)
 prior={}
 for name in ('final_representative_raw_receipt.json','final_protected_bytes_receipt.json','coordinate_complete_receipt.json','analysis_complete_receipt_v2.json','figures_complete_receipt.json','notebooks_complete_receipt_v2.json','handoff_receipt_bound.json'):
  p=OUT/name;r=read_json(p);a.check('prior_actual_C_evidence',r['status']=='VERIFIED' and not r.get('errors'),name);prior[name]=bound(p)
 a.same('G1_approved_regression',read_json(OUT/'handoff_receipt_bound.json')['stage_counts'],{'input':783,'segmented':30,'filtered':309,'denoised':13,'simplified':273,'retained':188,'not_processed':0})
 tests=ET.parse(OUT/'final_all_tests.xml').getroot();cases=list(tests.iter('testcase'))
 a.check('407_actual_tests_passed',len(cases)==407 and not any(c.find('failure') is not None or c.find('error') is not None or c.find('skipped') is not None for c in cases))
 a.check('independent_test_command_exit',read_json(OUT/'final_all_tests_execution.json')['exit_code']==0)
 # Text conclusions have been independently read by C; machine checks guard
 # the essential final-stage boundaries as well as the artifact hash bindings.
 summary=read_json(EV/'result_summary.json');a.check('no_unfounded_quality_final_method',summary['source_crs']=='UNVERIFIED' and summary['quality_accepted'] is False and summary['final_method_frozen'] is False and summary['selection_after_evaluation'] is False)
 a.check('all39tables111053rows',len(summary['tables'])==39 and sum(t['rows'] for t in summary['tables'].values())==111053)
 # Release schema is validated by the independent supplemental C release review,
 # whose exact target hash is included by root. It covers scan plus changed-file
 # delta and explicitly classified portability observations.
 release_binding=bound(OUT/'release_preparation_receipt_v2.json')
 release=read_binding(release_binding);a.check('release_preparation_independently_closed',release['status']=='VERIFIED' and not release.get('errors') and release.get('role_context')=='/root/c_contract')
 a.check('independent_review_covers_exact_B_release_target',registry['release_review'] in release['targets'])
 a.check('A17_no_remote_claim',release.get('publication_completed') is False)
 matrix=[]
 for ident,(tasks,explanation) in MAPPING.items():
  matrix.append({'id':ident,'status':'VERIFIED' if not a.errors else 'REVIEW_INCOMPLETE','evidence':[reviewed_tasks[t] for t in tasks],'scope':explanation})
 receipt={'goal_id':'SC-LAB1-G2-EXPERIMENTS-001','task':'internal_acceptance','classification':'INDEPENDENT_C_COMPLETE_PREPUBLICATION_ACCEPTANCE','role_context':'/root/c_contract','at':now(),
  'status':'VERIFIED' if not a.errors else 'REJECTED','checked_components':['A%02d'%i for i in range(1,18)],
  'unchecked_components':['actual_GitHub_push_and_remote_fixed_SHA_readback','GPT_SECOND_REVIEW','source_datum_or_real_noise_truth','Goal3_combinations_full_final_processing_and_formal_reports'],
  'targets':submitted,'source_hashes':{p:digest(ROOT/p) for p in task_sources('internal_acceptance')},'check_count':a.check_count,'errors':a.errors,
  'acceptance_matrix':matrix,'current_scope':scope,'prior_independent_reviews':prior,'extra_final_raw_sample':bound(OUT/'final_representative_raw_receipt.json'),
  'actual_tests':[bound(OUT/'final_all_tests_execution.json'),bound(OUT/'final_all_tests.xml')],'release_preparation':release_binding,'input_registry':bound(args.targets),'audit_program':bound(Path(__file__)),
  'formal_original_proposals':{'total':467,'legal_and_executed':467,'research_assessments':release['formal_original_proposal_research_statuses'],'coverage_tradeoff_witnesses':2,'illegal_proposals':0,'engineering_fallbacks':0,'distinction':'Legal parameter-domain execution does not imply passing research protection; 22 common5mDP-budget rejections and two coverage TRADEOFF proposals remain genuine negative results.'},
  'statistical_unit':'original_record; three model episodes are within-record repeated observations','full_vs_sample':'Full input/scope/hash/ledger/common metric/summary/mode/cost/lineage checks are documented in each component review. Independent Decimal geometric reconstruction used documented per-run representative samples (DEV parameter239/order75/demo88 and formal samples) plus final42 distinct trace-record-configurations; not all15,721 traces are claimed independently Decimal-rebuilt.',
  'engineering_status':'VERIFIED_PREPUBLICATION' if not a.errors else 'REJECTED','publication_status':'PENDING_AUTHORIZED_PUSH_AFTER_ACCEPTANCE','gpt_second_review':'PENDING','submission':'NOT_READY','new_model_calls':0,'elapsed_seconds':time.perf_counter()-start}
 receipt['C_audit_corrections']=['Initial CLI target path needed absolute resolution; no receipt emitted.', 'Rejected v1 C summary compared unordered task-source path sets as ordered lists and incorrectly required a future R10 publication review before prepublication acceptance. Both C schema checks corrected; all production artifacts and 176 submitted hashes remain unchanged.']
 write_json(OUT/'internal_acceptance_receipt_v2.json',receipt,exclusive=True)
 lines=['# Goal 2 独立内部全验收','',f"状态：{receipt['status']}。范围：内部发布前工程验收；实际 GitHub 发布和网页 GPT 二重验收不在本回执中预先宣称。",'',f"17 个必需子任务、13 个真实 Issue 的当前目标和源码绑定已核对；本次跨任务检查 {a.check_count:,} 项。此前实际组件核验、独立 raw 重构与 407 项完整回归一并绑定。",'', '| 项目 | 状态 | 实际检查范围 |','|---|---|---|']
 lines.extend(f"| {r['id']} | {r['status']} | {r['scope']} |" for r in matrix)
 lines.extend(['','全检与抽查边界：完整范围、哈希、账本、共同指标、汇总、模式因果和记忆隔离按各组件回执全核；独立 Decimal 几何重构使用有规则的代表/最差/阈值抽查，最终另重建42项。没有把抽查写成15,721条的全量独立重跑。','','source_crs=UNVERIFIED；无真实噪声标签；不作全局最优或因果记忆收益声明。GPT_SECOND_REVIEW=PENDING，Submission=NOT_READY。','','本回执绑定不可变时点快照，后续发布状态更新不冒充已经发生的远程验收。'])
 lines.extend(['','正式467条原始提议全部合法执行；研究判定为291条 SUPPORTED_WITHIN_SCOPE、152条 NO_DEMONSTRATED_GAIN、22条 REJECTED_BY_CONSTRAINT（共同DP 5工作米预算）、2条覆盖 TRADEOFF。两条覆盖损失并非全部负结果，合法性也不等同研究可行性；原话→episode→trace→锁定输出的独立重接见 [补充回执](release_preparation_receipt_v2.json)。',''])
 (OUT/'GOAL2_COMPLETE_ACCEPTANCE.md').write_text('\n'.join(lines)+'\n')
 print(json.dumps({k:receipt[k] for k in ('status','check_count','errors','elapsed_seconds')},ensure_ascii=False))
if __name__=='__main__':main()
