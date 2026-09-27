"""Bind the independently inspected FIG01 repair to its actual new artifacts."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

import review_figure_data

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FIG = ROOT/'task1/figures/goal3'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    state = json.loads((ROOT/'task1/evidence/goal3/goal_state.json').read_text())
    issue = state['issues']['G3-FIG-01']
    checks = []

    def check(label, actual, expected=True):
        checks.append({'check':label,'passed':actual == expected,'actual':actual,'expected':expected})

    targets = issue['repair_targets']
    check('exact15submittedtargets',len(targets),15)
    for t in targets:
        check('actual_repair_target:'+t['path'],sha(ROOT/t['path']),t['sha256'])

    # Re-evaluate the actual rebuilt artifacts; retain the original audit unchanged.
    with tempfile.TemporaryDirectory(prefix='FIG01-review-',dir=HERE) as temporary:
        review_figure_data.HERE = Path(temporary)
        review_figure_data.main()
        data_receipt = json.loads((Path(temporary)/'figure_data_receipt.json').read_text())
    data_receipt['actual_command'] = '.venv/bin/python task1/evidence/goal3/independent_documents/review_figure_repairs.py (calls unchanged review_figure_data.main with isolated receipt output)'
    data_path = HERE/'figure_data_repaired_receipt.json'
    data_path.write_text(json.dumps(data_receipt,ensure_ascii=False,indent=2)+'\n')
    check('rebuilt_actual_data_verified',data_receipt['status'],'VERIFIED_DATA_ONLY')
    check('rebuilt_actual_data_zero_errors',data_receipt['errors'],[])

    old = json.loads((HERE/'figure_visual_preliminary_receipt.json').read_text())
    rebound = []
    for f in old['figures']:
        if f['name'] not in ('production_trajectory_cases','goal3_actual_workflow'):
            digest = sha(ROOT/f['actual_inspected_render'])
            check('unchanged_independently_seen_pixels:'+f['name'],digest,f['render_sha256'])
            rebound.append({'name':f['name'],'current_render_sha256':digest,
                'visual_basis':'Prior actual whole-image review, exact rendered PNG hash unchanged'})

    root = ET.parse(FIG/'goal3_actual_workflow.drawio').getroot()
    edges = {(c.attrib['source'],c.attrib['target']):c
             for c in root.findall('.//mxCell') if c.attrib.get('edge')=='1'}
    check('10_native_editable_edges',len(edges),10)
    check('native_reviewed_results_before_freeze',edges[('c','ctl')].attrib['value'],
          'Reviewed development results; before freeze')
    check('native_next_plan_development_only',edges[('ctl','a')].attrib['value'],
          'Next development plan only')
    check('no_release_to_A_edge',('release','a') not in edges and ('release','ctl') not in edges)
    svg = (FIG/'goal3_actual_workflow.svg').read_text()
    check('visible_final_confirm_exclusion','FINAL_CONFIRM never feeds A.' in svg)
    trajectory_svg = (FIG/'production_trajectory_cases.svg').read_text()
    for label in ('S filtered','D removed','Stored output (R0 blue / S0 orange)'):
        check('visible_action_legend:'+label,label in trajectory_svg)
    for t in targets:
        check('stable_at_end:'+t['path'],sha(ROOT/t['path']),t['sha256'])
    errors = [c for c in checks if not c['passed']]
    receipt = {'role_context':'/root/c_documents','issue_id':'G3-FIG-01',
        'status':'VERIFIED' if not errors else 'FAILED',
        'checked_at_utc':datetime.now(timezone.utc).isoformat(),'targets':targets,
        'checks':len(checks),'data_checks':data_receipt['checks'],'errors':errors,
        'data_receipt':{'path':str(data_path.relative_to(ROOT)),'sha256':sha(data_path)},
        'checked_components':['All15actualsubmittedrepairhashes atstart/end; reviewed actual presentation-only patch/impact',
            'Independent fresh2965checks ofnewmanifest/data/exports/renders and source CSV/actualtrace bindings',
            'Actualcomplete200dpi revisedtrajectoryimage visuallyviewed: visibleS-filterx/D-removeplus/outputlegend, noaxisclip; complete352window preserved',
            'Actualcomplete200dpi revisedworkflowimage visuallyviewed: External3lines fitinsidebox; incomingarrow clear; Cresults routed aroundBto controller andnextplan toA',
            'Nativeeditable drawio10edges andlabels matchnewplot; developmentonly/beforefreeze restrictions; PDF/SVGfooter explicitly excludesFINAL_CONFIRMtoA',
            'Other5previouslyviewed200dpirenders haveexactunchangedpixel-filehashes andcurrent source/data rechecked'],
        'visual_observations':{'production_trajectory_cases':'All9panels, lowerlegend, workingunit axes and4point labels read inactual200dpiimage; nooverlap/cropping atnewlegend.',
            'goal3_actual_workflow':'Externalnode textfullycontained; revieweddevelopmentfeedback path avoidsBnode andreturnscontroller; next-plan arrow direction towardA; FINAL_CONFIRM neverfeedsA explicit.'},
        'rebound_unchanged_figures':rebound,
        'unchecked_components':['ThisclosesFIG01presentationissue only, notparentfigures task orGoal3',
            'FinalExperiment/Processreportallpagevisual/textchecks andfinalNotebook/ZIPintegration',
            'ExternalEvidenceMaster/identity/GPTsecondreview/Understanding'],
        'trajectory_processing_evaluations':0,'new_model_calls':0,'parent_task_closed':False,
        'actual_command':'.venv/bin/python task1/evidence/goal3/independent_documents/review_figure_repairs.py',
        'checker_sha256':sha(Path(__file__))}
    out = HERE/'G3-FIG-01_closure.json'
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'checks':len(checks),'errors':errors,'receipt_sha256':sha(out)}))


if __name__=='__main__':
    main()
