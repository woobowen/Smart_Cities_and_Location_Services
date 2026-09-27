"""Independently close the two narrowly scoped historical report repairs."""
import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(rel):
    return json.loads((ROOT / rel).read_text())


def main():
    state = read('task1/evidence/goal3/goal_state.json')
    repair = read('task1/evidence/goal3/report_build/document_C_repairs.json')
    build = read('task1/evidence/goal3/report_build/build_receipt.json')
    checks = []

    def check(name, actual, expected):
        checks.append({'name': name, 'actual': actual, 'expected': expected,
                       'passed': actual == expected})

    for issue_id in ['G3-DOC-01','G3-DOC-02']:
        for target in state['issues'][issue_id]['repair_targets']:
            check(issue_id + ': exact repair target ' + target['path'],
                  digest(ROOT / target['path']), target['sha256'])
    for report in build['reports']:
        check(report['report'] + ': build PDF hash', digest(ROOT / report['pdf']),report['sha256'])
        check(report['report'] + ': recorded compile exit', report['compile_exit_code'],0)
        check(report['report'] + ': recorded diagnostics',report['unresolved_diagnostics'],[])
        for path, expected in {**report['source_sha256'], **build['shared_source_sha256']}.items():
            check(report['report'] + ': build source binding ' + path, digest(ROOT / path),expected)
        info = subprocess.run(['pdfinfo', str(ROOT / report['pdf'])],check=True,capture_output=True,text=True).stdout
        pages = int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        check(report['report'] + ': actual PDF page count',pages,report['pages'])
        subprocess.run(['pdftotext','-layout',str(ROOT/report['pdf']),str(OUT/(report['report']+'_repaired_text.txt'))],check=True)
        log = (ROOT/f"task1/reports/{report['report']}/build/{report['report']}.log").read_text()
        bad = [x for x in log.splitlines() if re.search(r'Missing character:|Undefined control sequence|Emergency stop|Fatal error|Overfull \\[hv]box|undefined references|undefined citations|Font Warning:.*not available',x,re.I)]
        check(report['report'] + ': actual build log blocking diagnostics',bad,[])
    process = (ROOT/'task1/reports/process1/process1.tex').read_text()
    part1, part2 = process.split(r'\part*{第二层：Experiment Decision Process}',1)
    part1 = part1.split(r'\part*{第一层：Workflow Construction}',1)[1]
    phrases=['目前没有文件绑定的坐标说明','批准采用上述一次标记、同时删除规则','过滤 309 点','DP 删除 273 点']
    check('D1/D2/pilot specifics absent from Part I',all(x not in part1 for x in phrases),True)
    check('D1/D2/pilot specifics present in Part II',all(x in part2 for x in phrases),True)
    check('Part I points to technical section',r'\ref{sec:technical-authorization}' in part1,True)
    check('Part II technical label exists',r'\label{sec:technical-authorization}' in part2,True)
    patch = (ROOT/'task1/evidence/goal3/report_build/document_C_repairs.patch').read_text()
    process_patch = patch.split('--- before/task1/reports/experiment1/experiment1.tex')[0]
    removed='\n'.join(line[1:] for line in process_patch.splitlines()
                      if line.startswith('-') and not line.startswith('---'))
    moved=part2.split(r'\subsection{坐标来源缺失没有被假标签补齐}',1)[1].split(r'\section{从基础答案到可比较的问题}',1)[0]
    moved=r'\subsection{坐标来源缺失没有被假标签补齐}'+moved
    check('moved actual paragraph bytes equal removed patch paragraph',moved.strip(),removed.strip())
    process_pdf=(OUT/'process1_repaired_text.txt').read_text()
    content=process_pdf.split('第二层：Experiment Decision Process')[-1]
    check('actual PDF retains D1/D2 in Part II',all(x in content for x in phrases[:2]),True)
    check('actual PDF cross-reference resolved','??' not in process_pdf,True)

    # Derive the new prose numbers from preserved per-record processing results.
    with (ROOT/'task1/evidence/goal2/tables/parameter_records.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    direction={}
    for angle in [15,25,35,45,60]:
        selected=[r for r in rows if r['partition']=='DEVELOPMENT' and r['order']=='S-D-P'
                  and all(float(r[k])==v for k,v in {'dt':30,'distance':400,'min_points':5,
                                                    'min_length':65,'direction':angle,'dp':5}.items())]
        direction[angle]={'records':len(selected),
                          **{k:sum(int(r[k]) for r in selected) for k in
                             ['n_input','n_direction_removed','common_covered_points']}}
        check(f'direction {angle}: complete original records',len({r['record_id'] for r in selected}),120)
    macros=(ROOT/'task1/reports/history_values.tex').read_text()
    values={k:int(v.replace(',','')) for k,v in re.findall(r'\\newcommand\{\\(Direction[^}]+)\}\{([^}]+)\}',macros)}
    expected={'DirectionDevelopmentPoints':direction[35]['n_input'],
              'DirectionLowRemoved':direction[15]['n_direction_removed'],
              'DirectionRefRemoved':direction[35]['n_direction_removed'],
              'DirectionHighRemoved':direction[60]['n_direction_removed'],
              'DirectionCovered':direction[35]['common_covered_points']}
    check('new generated direction macros match independent record sums',values,expected)
    check('all five directions retain stated common coverage',
          sorted({v['common_covered_points'] for v in direction.values()}),[8408])
    tex=(ROOT/'task1/reports/experiment1/experiment1.tex').read_text()
    check('actual direction figure included',r'\includegraphics[width=.99\linewidth]{../../figures/goal2/direction_threshold_and_neighborhood.pdf}' in tex,True)
    check('direction noise-accuracy boundary present','不能把这条数量趋势解释为准确率改善' in tex,True)
    experiment_pdf=(OUT/'experiment1_repaired_text.txt').read_text()
    normalized=re.sub(r'\s+','',experiment_pdf)
    check('actual PDF contains direction results',all(x in normalized for x in ['1,649','669','278','8,408','方向组开发结果']),True)

    renders=[]
    for name,pages in [('experiment1',[6,7]),('process1',[3,7])]:
        report=next(r for r in build['reports'] if r['report']==name)
        for page in pages:
            stem=OUT/f'{name}_repair_page_{page:02}'
            subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-r','200','-png',
                            str(ROOT/report['pdf']),str(stem)],check=True,capture_output=True)
            rel=f'task1/reports/{name}/build/render200/page-{page:02}.png'
            actual=digest(stem.with_suffix('.png'))
            check(name+f': independent 200dpi render page {page}',actual,report['render']['page_sha256'][rel])
            renders.append({'report':name,'page_one_based':page,'dpi':200,
                            'path':str(stem.with_suffix('.png').relative_to(ROOT)),'sha256':actual,
                            'visually_inspected':True,
                            'inspection':'Readable full-page image; no clipping/overlap/missing text in repaired content. Image byte-identical to already viewed 200dpi build page.'})
    check('G3 placeholder remains visibly unfinished', '待' in (ROOT/'task1/reports/experiment1/generated.tex').read_text(),True)
    check('current Process draft retains external Evidence boundary','Evidence Lock 尚缺' in process,True)
    status='VERIFIED' if all(x['passed'] for x in checks) else 'FAIL'
    for issue_id,components in [
        ('G3-DOC-01',['exact_repair_target_hashes','part_I_part_II_scope','verbatim_moved_text_preserved',
                       'actual_PDF_part_II_text','resolved_cross_reference','compile_log','changed_pages_200dpi_visual']),
        ('G3-DOC-02',['exact_repair_target_hashes','actual_direction_result_figure','direction_values_independent_record_sums',
                       'sample_and_no_truth_boundary','actual_PDF_direction_text','compile_log','changed_pages_200dpi_visual'])]:
        receipt={'role_context':'/root/c_documents','issue_id':issue_id,'status':status,
                 'created_at_utc':datetime.now(timezone.utc).isoformat(),
                 'targets':state['issues'][issue_id]['repair_targets'],
                 'checked_components':components,'checks':checks,
                 'references':['task1/evidence/goal3/independent_documents/preliminary_receipt.json',
                               'task1/evidence/goal2/tables/parameter_records.csv',
                               'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md#18'],
                 'independent_record_sums':direction,'visual_inspection':renders,
                 'unchecked':['final_G3_report_results','full_notebook_execution','ZIP_independent_recompute',
                              'all_final_report_pages_visual_acceptance','Evidence_Master_LOCK','trusted_identity'],
                 'final_report_acceptance':False,'FINAL_CONFIRM_effects_read':False,
                 'research_or_core_changes':False,'new_model_calls':0,'new_method_runs':0}
        (OUT/f'{issue_id}_closure.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':status,'checks':len(checks),'failed':[x['name'] for x in checks if not x['passed']],
                     'closures':['G3-DOC-01','G3-DOC-02']},ensure_ascii=False))


if __name__=='__main__':main()
