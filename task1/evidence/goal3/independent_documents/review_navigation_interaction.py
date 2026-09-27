"""Independent read-only audit of teacher navigation and 19-entry handoff."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
EV = 'task1/evidence/goal3/'
CHECKS, SOURCES = [], {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path(relative):
    result = ROOT / relative
    SOURCES[relative] = sha(result)
    return result


def read(relative):
    return json.loads(path(relative).read_text())


def check(name, actual, expected=True):
    CHECKS.append({'name': name, 'passed': actual == expected,
                   'actual': actual, 'expected': expected})


def compact(text):
    return re.sub(r'\s+', '', text)


def main():
    target_paths = [EV + 'teacher_delivery_mapping.json', EV + 'teacher_delivery_mapping.md',
                    EV + 'interaction_candidates.json', 'task1/docs/goal3/INTERACTION_HANDOFF.md']
    nav = read(target_paths[0])
    nav_md = path(target_paths[1]).read_text()
    interaction = read(target_paths[2])
    interaction_md = path(target_paths[3]).read_text()
    for key, ref in nav['sources'].items():
        check('navigation original source:' + key, sha(path(ref['path'])), ref['sha256'])
    requirements = {g: {x['id']: x['requirement'] for x in read('task1/evidence/' + g + '/requirements.json')['requirements']}
                    for g in ['goal1', 'goal2']}
    check('22 navigation entries', len(nav['entries']), 22)
    check('unique stable navigation IDs', len({e['id'] for e in nav['entries']}), 22)
    for goal, key in [('goal1', 'g1_requirement_ids'), ('goal2', 'g2_requirement_ids')]:
        actual = sorted({rid for entry in nav['entries'] for rid in entry[key]})
        check(goal + ': complete original requirement IDs', actual, sorted(requirements[goal]))
        check(goal + ': honest coverage list', actual,
              nav['requirement_coverage']['G1_ids_located' if goal == 'goal1' else 'G2_ids_located'])
    check('no unlocated original ID', nav['requirement_coverage']['unlocated_ids'], [])
    teacher = read(nav['sources']['teacher_inventory']['path'])
    check('teacher PPT actual preserved source', sha(path(nav['sources']['teacher_ppt']['path'])),
          nav['sources']['teacher_ppt']['sha256'])
    with ZipFile(ROOT / nav['sources']['teacher_ppt']['path']) as z:
        slide = ET.fromstring(z.read('ppt/slides/slide26.xml'))
        original = ''.join(e.text or '' for e in slide.iter() if e.tag.endswith('}t'))
    for anchor in ['10月5日', '52285903012@stu.ecnu.edu.cn', '学号', '姓名', '实验一']:
        check('teacher slide26 literal:' + anchor, anchor in compact(original))
        check('teacher submission remains in navigation:' + anchor, anchor in compact(nav_md))

    notebooks = {}
    for key, item in nav['notebooks'].items():
        doc = read(item['path']); notebooks[key] = doc
        normalized = [{'index_zero_based': i, 'id': c['id'], 'cell_type': c['cell_type'],
                       'source': ''.join(c['source'])} for i, c in enumerate(doc['cells'])]
        b = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        check(key + ': source-only notebook hash', hashlib.sha256(b).hexdigest(), item['source_cells_sha256'])
        check(key + ': actual physical cells', len(doc['cells']), item['cell_count'])
        check(key + ': source navigation does not assert FULL',
              item['full_execution_status'].startswith('NOT_ASSERTED_BY_THIS_NAVIGATION'))

    reports = {}
    previous_report = read(EV + 'independent_documents/full_report_review_receipt.json')
    previously_viewed = {(r['report'], r['pdf_page_1based']): r['sha256'] for r in previous_report['pages']}
    for key, report in nav['reports'].items():
        pdf = path(report['path'])
        extracted = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], check=True,
                                   capture_output=True).stdout
        check(key + ': exact current report text hash', hashlib.sha256(extracted).hexdigest(), report['text_sha256'])
        check(key + ': archived text equals current extraction', path(report['text_path']).read_bytes(), extracted)
        CHECKS[-1]['actual'] = sha(ROOT / report['text_path'])
        CHECKS[-1]['expected'] = hashlib.sha256(extracted).hexdigest()
        pages = extracted.decode('utf8').split('\f')
        if not pages[-1].strip():
            pages.pop()
        reports[key] = pages
        check(key + ': current actual PDF pages', len(pages), report['pages'])
        for n, page_text in enumerate(pages, 1):
            check(key + ': exact page text ' + str(n), hashlib.sha256(page_text.encode()).hexdigest(),
                  report['page_text_sha256'][str(n)])
            report_name = 'experiment1' if key == 'E' else 'process1'
            check(key + ': mapped actual visual page ' + str(n),
                  report['page_render_sha256_at_B_visual_review'][str(n)], previously_viewed[(report_name, n)])
        # PDF metadata identity is an observation, not used to silently accept a rebuilt PDF.
        check(key + ': navigation observed PDF hash format', bool(re.fullmatch('[0-9a-f]{64}', report['pdf_sha256_at_navigation'])))

    cell_locations = report_locations = 0
    for entry in nav['entries']:
        eid = entry['id']
        check(eid + ': actual Markdown table row', '| ' + eid + ' |' in nav_md)
        allowed_navigation_states = {
            'CONTENT_LOCATED_NOT_ACCEPTANCE', 'EXTERNAL_DEPENDENCIES_EXPLICIT_NOT_CLOSED',
            'STATUS_DEFERRED_TO_ACTUAL_PUBLICATION_AND_EXTERNAL_REVIEW',
            'PACKAGE_CONTENT_NAVIGATION_NOT_READY_OR_SUBMITTED_CLAIM',
        }
        check(eid + ': no acceptance inflation', entry['navigation_state'] in allowed_navigation_states)
        for req in entry['historical_requirement_sources']:
            check(eid + ': original requirement wording ' + req['g1_requirement_id'], req['requirement'],
                  requirements['goal1'][req['g1_requirement_id']])
        md_line = next(line for line in nav_md.splitlines() if line.startswith('| ' + eid + ' |'))
        for nb in entry['notebooks']:
            check(eid + ': notebook path', nb['path'], nav['notebooks'][nb['notebook']]['path'])
            seq = ','.join(str(c['index_zero_based']) for c in nb['cells'])
            check(eid + ': Markdown cell sequence', nb['notebook'] + ' ' + seq in md_line)
            for locator in nb['cells']:
                cell_locations += 1
                index = locator['index_zero_based']
                cell = notebooks[nb['notebook']]['cells'][index]
                text = ''.join(cell['source'])
                check(eid + ': cell stable ID ' + str(index), cell['id'], locator['cell_id'])
                check(eid + ': cell type ' + str(index), cell['cell_type'], locator['cell_type'])
                check(eid + ': exact source ' + str(index), hashlib.sha256(text.encode()).hexdigest(), locator['source_sha256'])
                check(eid + ': first line ' + str(index), text.splitlines()[0], locator['source_first_line'])
        for locator in entry['reports']:
            report_locations += 1
            key = locator['report']; pages = locator['pdf_pages_one_based']
            check(eid + ': report path', locator['path'], nav['reports'][key]['path'])
            check(eid + ': declared page range present', all(1 <= n <= len(reports[key]) for n in pages))
            combined = ''.join(reports[key][n - 1] for n in pages)
            check(eid + ': actual anchor within declared pages ' + locator['verified_text_anchor'],
                  compact(locator['verified_text_anchor']) in compact(combined))
            check(eid + ': Markdown actual PDF page sequence', key + ' ' + ','.join(map(str, pages)) in md_line)
            for n, printed in zip(pages, locator['printed_page_labels']):
                actual_label = '' if n == 1 else reports[key][n - 1].strip().splitlines()[-1].strip()
                expected = printed if n != 1 else ''
                check(eid + ': physical/printed page mapping ' + str(n), actual_label, expected)
        for rel in entry['additional_source_paths']:
            check(eid + ': extra source exists ' + rel, (ROOT / rel).exists())
    check('90 source-cell locators (repeated cells allowed)', cell_locations, 90)
    check('45 report-locator groups (not 45 independent pages)', report_locations, 45)
    for bound in ['CONTENT_LOCATED', 'NOT_ASSERTED_BY_THIS_NAVIGATION']:
        check('navigation scoped state ' + bound, bound in json.dumps(nav))
    check('no method execution by mapping', nav['new_method_runs'], 0)
    check('no model calls by mapping', nav['new_model_calls'], 0)

    refs, quotes = [], []
    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and re.fullmatch('[0-9a-f]{64}', str(value.get('sha256', ''))):
                refs.append(value)
            if isinstance(value.get('verbatim'), str) and isinstance(value.get('source'), dict):
                quotes.append(value)
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
    walk(interaction)
    for ref in refs:
        check('interaction bound source:' + ref['path'], sha(path(ref['path'])), ref['sha256'])
    for n, quote in enumerate(quotes):
        original = path(quote['source']['path']).read_text()
        check('actual user quotation exact bytes:' + str(n), quote['verbatim'] in original)
        match = re.fullmatch(r'lines (\d+)-(\d+)', quote['source'].get('locator', ''))
        if match:
            check('actual user quotation line span:' + str(n),
                  '\n'.join(original.splitlines()[int(match[1]) - 1:int(match[2])]), quote['verbatim'])
    candidates = interaction['candidates']
    check('19 unique interaction candidate IDs', len({c['candidate_id'] for c in candidates}), 19)
    check('19 candidate objects', len(candidates), 19)
    md_ids = re.findall(r'^#{2,3} (IH-[A-Z0-9-]+) · ', interaction_md, re.M)
    check('19 Markdown sections match candidate index', md_ids, [c['candidate_id'] for c in candidates])
    for candidate in candidates:
        cid = candidate['candidate_id']
        for field in ['Tier', 'screenshot_spec', 'annotation_spec', 'report_order']:
            check(cid + ': not assigned ' + field, candidate[field], None)
        for field in ['Evidence_Lock', 'formal_evidence_selection']:
            check(cid + ': no claimed ' + field, candidate[field], 'NOT_ASSIGNED_BY_THIS_HANDOFF')
        if candidate['Human_Judgment']['status'] == 'NOT_AVAILABLE':
            check(cid + ': no invented human verbatim', candidate['Human_Judgment']['verbatim'], None)
            check(cid + ': no invented human meaning', candidate['Human_Judgment']['meaning'], None)
        if candidate['User_verbatim_and_source']['status'] == 'NOT_AVAILABLE':
            check(cid + ': no invented user quote', candidate['User_verbatim_and_source']['quotes'], [])
    for candidate in candidates[:15]:
        serialized = json.dumps(candidate['Referenced_materials_and_experiments'])
        check(candidate['candidate_id'] + ': original A research does not read final/selection effects',
              not any(x in serialized for x in ['g3-final-confirm', 'release_decision', 'selection_decision', 'g3-full-production']))
    for candidate in candidates[-4:]:
        cid = candidate['candidate_id']
        check(cid + ': actual root postfreeze append', candidate['Available_message_range']['root_context'], '/root')
        check(cid + ': system decision identity', candidate['Actual_decision']['type'], 'SYSTEM_DECISION_WITHIN_USER_PREAPPROVED_RULES')
    check('native metadata not claimed as transcript', 'not recovered verbatim' in interaction['native_message_limits'])
    check('final effects explicitly excluded from A', interaction['FINAL_CONFIRM_effects_read'],
          'ROOT_AND_C_ONLY_AFTER_FINAL_FREEZE; NOT_SENT_TO_A')
    boundary = read(EV + 'independent_c/new_coverage_boundary_receipt.json')
    check('full boundary independently verified', boundary['status'], 'VERIFIED')
    check('full boundary quote exact source artifact time', candidates[-1]['Available_message_range']['artifact_time'], boundary['checked_at_utc'])
    # G2 proposal dictionaries were independently matched earlier; bind the same
    # exact source fields and current artifact bytes, without pretending new LIVE.
    old = read(EV + 'independent_documents/handoff_preliminary_receipt.json')
    check('prior independent history/development/final fact checks', all(c['passed'] for c in old['checks']))
    for rel in target_paths:
        text = (ROOT / rel).read_text()
        for url in re.findall(r'\]\(([^)]+)\)', text):
            if '://' in url or url.startswith('#'): continue
            check('relative link:' + rel + ':' + url, ((ROOT / rel).parent / url.split('#')[0]).exists())

    errors = [x for x in CHECKS if not x['passed']]
    result = {
        'role_context': '/root/c_documents', 'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'VERIFIED_NAVIGATION_AND_INTERACTION_SCOPE' if not errors else 'REPAIR_REQUIRED',
        'targets': [{'path': rel, 'sha256': sha(ROOT / rel)} for rel in target_paths],
        'source_hashes': SOURCES, 'checks': CHECKS, 'errors': errors,
        'checked_components': ['all G1 R01–R16 and G2 R01–R10 mapped without acceptance inflation',
                               '22 topics manually compared with actual notebook source and full report content',
                               '90 exact cell locators with stable IDs/source hashes and 45 PDF page-range/anchor groups',
                               'actual slide26 submission text and source preservation',
                               '19 interaction entries, all cited source hashes and exact available user quotations',
                               'all absent per-decision human judgments left unavailable; no Tier/spec/LOCK invented',
                               'original A context versus four root postfreeze entries explicitly distinguished'],
        'unchecked_components': ['Notebook FULL execution outcome (separate independent C verification)',
                                 'ZIP construction, extraction and full integration',
                                 'later REPORT_BUILD PDF metadata/pixel delta and parent task closure',
                                 'unavailable original screenshots, approved annotation plan and Evidence Lock',
                                 'GitHub remote publication and webpage GPT review'],
        'external_dependencies': ['trusted formal identity', 'real screenshots/full message ranges',
                                  'Evidence Master specification and final Lock'],
        'new_processing_runs': 0, 'new_model_calls': 0, 'parent_task_closed': False,
        'actual_command': '.venv/bin/python task1/evidence/goal3/independent_documents/review_navigation_interaction.py',
        'checker_sha256': sha(Path(__file__)),
    }
    (HERE / 'navigation_interaction_receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(CHECKS), 'errors': errors,
                      'source_cell_locators': cell_locations, 'report_locator_groups': report_locations,
                      'interaction_references': len(refs), 'user_quotes': len(quotes)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
