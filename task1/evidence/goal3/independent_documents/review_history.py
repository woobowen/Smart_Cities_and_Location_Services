"""Independent document traceability checks; reads historical evidence only."""
from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCES = {}
CHECKS = []


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def source(rel):
    p = ROOT / rel
    SOURCES[rel] = digest(p)
    return p


def read(rel):
    return json.loads(source(rel).read_text())


def table(name):
    with source(f'task1/evidence/goal2/tables/{name}.csv').open(newline='') as f:
        return list(csv.DictReader(f))


def check(name, actual, expected):
    CHECKS.append({'name': name, 'actual': actual, 'expected': expected,
                   'passed': actual == expected})


def main():
    OUT.mkdir(exist_ok=True)
    targets = {}
    for p in sorted((ROOT / 'task1/reports').rglob('*.tex')):
        if 'build' not in p.parts:
            targets[str(p.relative_to(ROOT))] = digest(p)
    for p in sorted((ROOT / 'task1/notebooks/final').glob('*.ipynb')):
        rel = str(p.relative_to(ROOT)); targets[rel] = digest(p)
        doc = json.loads(p.read_text())
        check(rel + ': notebook v4', doc['nbformat'], 4)
        code = [c for c in doc['cells'] if c['cell_type'] == 'code']
        for i, cell in enumerate(code):
            ast.parse(''.join(cell['source']))
        body = '\n'.join(''.join(c['source']) for c in doc['cells'])
        check(rel + ': default FULL_RECOMPUTE', "MODE = 'FULL_RECOMPUTE'" in body, True)
        check(rel + ': two registered Provider sentinels',
              all(x in body for x in ['ExperimentProvider.call = forbid_provider',
                                      'CodexProvider.call = forbid_provider']), True)
        check(rel + ': no personal absolute path', '/home/' not in body, True)
        check(rel + ': declared unexecuted source',
              all(c.get('execution_count') is None for c in code), True)
    for rel in ['task1/reports/experiment1/experiment1.tex', 'task1/reports/process1/process1.tex']:
        text = (ROOT / rel).read_text()
        check(rel + ': shared exact P2 source',
              r'\input{../../../templates/latex/common/p2_cloud_sorbet_colors.tex}' in text, True)
        check(rel + ': no synthetic template asset included', 'demo-assets/' not in text, True)
        for asset in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', text):
            p = (ROOT / rel).parent / asset
            check(rel + ': asset exists: ' + asset, p.is_file(), True)
            if p.is_file(): SOURCES[str(p.resolve().relative_to(ROOT))] = digest(p)
    # Verify original teacher pages, not only the author's requirement mapping.
    ppt = source('task1/实验课1.pptx')
    with ZipFile(ppt) as z:
        slides = {}
        for number in [5, 6, 18, 20, 22, 24, 26, 37, 42]:
            node = ET.fromstring(z.read(f'ppt/slides/slide{number}.xml'))
            slides[number] = re.sub(r'\s+', '', ''.join(n.text or '' for n in node.iter(
                '{http://schemas.openxmlformats.org/drawingml/2006/main}t')))
    check('teacher page 26 date', '10月5日前' in slides[26], True)
    check('teacher page 26 recipient', '52285903012@stu.ecnu.edu.cn' in slides[26], True)
    check('teacher page 26 naming', '学号_姓名_实验一' in slides[26], True)
    check('teacher page 6 known-answer counterexample', '至少构造一组反例' in slides[6], True)
    check('teacher page 37 search-only zero calls', '不含任何LLM调用' in slides[37], True)
    check('teacher page 42 order discussion', '可不可以调换顺序' in slides[42], True)

    binding = read('task1/evidence/goal3/report_build/history_value_bindings.json')
    for rel, expected in binding['source_sha256'].items():
        check('bound historical source: ' + rel, digest(source(rel)), expected)
    for rel, expected in binding['generated_files'].items():
        check('generated value file: ' + rel, digest(source(rel)), expected)
    summary = read('task1/evidence/goal2/result_summary.json')
    values = binding['values']
    cs = next(x for x in summary['single_candidates'] if x['candidate'] == 'C-S')
    reference = next(x for x in summary['single_candidates'] if x['candidate'] == 'C-D')
    direct_expected = {
        'DevelopmentConfigs': summary['parameters']['unique_development_configs'],
        'EvaluationConfigs': summary['parameters']['unique_evaluation_configs'],
        'GTwoEvalPoints': cs['n_input'], 'CSStrictRecords': cs['strict_gain_records'],
        'RZeroCovered': reference['common_covered_points'],
        'CSCovered': cs['common_covered_points'],
        'AddedCovered': cs['common_covered_points'] - reference['common_covered_points'],
        'RZeroEmpty': reference['n_no_output_records'], 'CSEmpty': cs['n_no_output_records'],
        'RZeroFinal': reference['n_final'], 'CSFinal': cs['n_final'],
        'MemoryDemo': summary['memory']['demonstration_records'],
        'SyntheticCases': summary['counterexamples']['synthetic_cases'],
        'KnownChecks': summary['counterexamples']['known_answer_checks'],
    }
    for key, expected in direct_expected.items():
        check('historical macro: ' + key, values[key], expected)
    # Structural all-raw reading computes no method results and opens no final feedback.
    raw = read('task1/作业/作业/traj_dict.json')
    counts = Counter()
    for times, positions in raw.values():
        check('raw alignment', len(times), len(positions)) if len(times) != len(positions) else None
        counts['RawPoints'] += len(times)
        counts['RawEdges'] += max(0, len(times)-1)
        for i in range(1, len(times)):
            dt = times[i] - times[i-1]
            same = positions[i] == positions[i-1]
            counts['ZeroDtEdges'] += dt == 0
            counts['SameTimeMoved'] += dt == 0 and not same
            counts['DuplicateEdges'] += same
            counts['LongGapEdges'] += dt > 30
    counts['RawRecords'] = len(raw)
    for key, actual in counts.items(): check('raw scalar: ' + key, actual, values[key])
    del raw
    pairs = table('candidate_record_pairs')
    for cid in ['C-S', 'C-D', 'C-P']:
        subset = [r for r in pairs if r['candidate'] == cid]
        item = next(x for x in summary['single_candidates'] if x['candidate'] == cid)
        check(cid + ': complete record denominator', len(subset), item['n_records'])
        check(cid + ': strict gains', sum(r['strict_gain'] == 'True' for r in subset), item['strict_gain_records'])
        for key, column in [('n_final','candidate_n_final'),('n_filtered','candidate_n_filtered'),
                            ('n_direction_removed','candidate_n_direction_removed'),
                            ('common_covered_points','candidate_common_covered_points')]:
            check(cid + ': record sum ' + key, sum(int(r[column]) for r in subset), item[key])
    mode_records = table('mode_record_results')
    calls = table('model_calls')
    historical_calls = table('historical_model_calls')
    check('valid visible model calls', len(calls), values['ValidModelCalls'])
    check('historical visible model calls', len(historical_calls), values['HistoricModelCalls'])
    for m in summary['mode_summary']:
        subset = [r for r in mode_records if (r['partition'],r['mode']) == (m['partition'],m['mode'])]
        prefix = m['partition'] + '/' + m['mode']
        check(prefix + ': observations', len(subset), m['record_episode_observations'])
        check(prefix + ': protected gains', sum(r['strict_gain'] == 'True' and r['feasible'] == 'True' for r in subset), m['protected_gain_records_episodes'])
        check(prefix + ': model receipts', len([r for r in calls if (r['partition'],r['mode']) == (m['partition'],m['mode'])]), m['experiment_model_dispatches'])
    consumption = table('memory_consumption')
    memory_result = {
        'observations':len({(r['partition'],r['episode'],r['record_id']) for r in consumption}),
        'rounds':len(consumption),
        'cited_rounds':sum(int(r['valid_citation_count']) > 0 for r in consumption),
        'consistent_rounds':sum(int(r['action_consistent_count']) > 0 for r in consumption),
    }
    check('memory denominators', memory_result, {'observations':96,'rounds':241,'cited_rounds':60,'consistent_rounds':49})
    ai = read('task1/evidence/goal2/a_epoch02/actual_ai_critique/actual_ai_critique.json')
    for c in ai['actual_ai_citations']:
        response = c['raw_response']; p = source(response['path'])
        check(c['citation_id'] + ': original response hash', digest(p), response['sha256'])
        check(c['citation_id'] + ': exact reason in original response',
              c['verbatim_model_reason'] in p.read_text(), True)
        trace_ref = c['candidate_trace_file']; p = source(trace_ref['path'])
        check(c['citation_id'] + ': saved candidate trace hash', digest(p), trace_ref['sha256'])
        traces = json.loads(gzip.decompress(p.read_bytes()))['results']
        for label in ['reference','candidate']:
            actual = traces[c[label+'_config_id']]
            check(c['citation_id'] + ': ' + label + ' parameters',
                  actual['parameters'], c[label+'_parameters'])
            for key, expected in c[label+'_metrics'].items():
                check(c['citation_id'] + ': ' + label + ' actual trace metric ' + key,
                      actual['metrics'].get(key, 'MISSING'), expected)
    check('AI preserved proposals', ai['actual_scope']['preserved_original_proposals'],148)
    check('AI evaluable predictions',ai['actual_scope']['evaluable_prediction_denominator'],70)
    synthetic = read('task1/evidence/goal2/counterexamples/formal-02/synthetic_cases.json')
    check('synthetic case count',len(synthetic['cases']),values['SyntheticCases'])
    check('synthetic executed chains',sum(len(c['executions']) for c in synthetic['cases']),19)
    check('synthetic known answers',sum(len(c['known_answer_checks']) for c in synthetic['cases']),values['KnownChecks'])
    check('synthetic observed expected agree',all(q['observed']==q['expected'] and q['passed'] for c in synthetic['cases'] for q in c['known_answer_checks']),True)
    coordinates = read('task1/evidence/goal2/coordinate_sensitivity/raw_preflight/coordinate_checks.json')
    check('G2 coordinate checked records',coordinates['records_checked'],307)
    check('G2 coordinate checked points',coordinates['points_checked'],30992)
    check('G2 coordinate checked pairs',coordinates['within_record_pairs_checked'],1594527)
    check('G2 coordinate implementation tolerance',coordinates['coordinate_error_m']['max'] < 1e-6,True)
    sensitivity_runs = []
    for part in ['development-02','evaluation-01']:
        d=read(f'task1/evidence/goal2/coordinate_sensitivity/{part}/summary.json')
        for r in d['runs']:
            check(r['run_id'] + ': coordinate threshold differences', r['sensitivity_difference_counts'],{})
            sensitivity_runs.append({'run_id':r['run_id'],'traces_checked':r['actual_traces_checked']})
    pilot = read('task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/result_summary.json')
    check('G1 pilot stage counts',pilot['stage_counts'],{'input':783,'segmented':30,'filtered':309,'denoised':13,'simplified':273,'retained':188,'not_processed':0})
    decisions=read('task1/evidence/goal1/revisions/SC-LAB1-G1-COMPLETE-001/USER_DECISIONS.json')
    check('D1 preserved quote', decisions['D1']['reply_verbatim'],'目前没有文件绑定的坐标说明')
    check('D2 preserved quote', decisions['D2']['reply_verbatim'],'批准采用上述一次标记、同时删除规则')
    source('task1/evidence/goal2/PROCESS_RECORD.md')
    source('task1/evidence/goal3/report_build/SOURCE_READ_SCOPE.md')
    source('task1/evidence/goal3/report_build/source_fetch_receipts.json')
    receipt = {
        'role_context':'C-Documents:/root/c_documents',
        'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'status':'VERIFIED_HISTORICAL_VALUES_ONLY' if all(x['passed'] for x in CHECKS) else 'FAIL',
        'review_target':'G1/G2 draft report and completed notebook sources; pre-production review',
        'targets':targets, 'source_hashes':SOURCES, 'checks':CHECKS,
        'teacher_pages_checked':list(slides), 'coordinate_sensitivity_scope':sensitivity_runs,
        'checked':['raw structural counts without method evaluation','23 historical numerical macros and source hashes',
                   'G2 C-S/C-D/C-P record pairing totals','G2 mode observations and visible calls',
                   'memory denominator distinction','all six cited model reasons in original responses',
                   'all six synthetic case metadata/25 known-answer records','G1 D1/D2 exact saved quotes',
                   'all notebook code cells AST and default offline boundary','shared P2/no demo asset use'],
        'unchecked':['G3 development/selection/final effects','full notebook execution','ZIP isolated reproduction',
                     'final PDFs/all-page >=200dpi visual acceptance','teacher identity','Evidence Master decisions/LOCK',
                     'reexecution of historical core mathematics (separate C protocol scope)',
                     'whether unobserved upstream provider requests exist'],
        'new_processing_runs':0,'new_model_calls':0,'FINAL_CONFIRM_effects_read':False,
    }
    (OUT/'historical_checks.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'checks':len(CHECKS),'failures':[x for x in CHECKS if not x['passed']],
                      'targets':len(targets),'sources':len(SOURCES)},ensure_ascii=False))


if __name__ == '__main__': main()
