"""Read-only delivery checks; write the measured results beside this script."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MIRROR = ROOT / 'releases/chatgpt-project-sources'
results = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(name, condition, detail=None):
    results[name] = {'pass': bool(condition), 'detail': detail}

def main():
    before = json.loads((OUT / 'preflight.json').read_text())
    changes = [p for p, h in before['task1_hashes'].items() if sha(ROOT / p) != h]
    check('teacher_task1_unchanged', not changes, {'checked_files': len(before['task1_hashes']), 'changed': changes})
    palette = ROOT / 'templates/latex/common/p2_cloud_sorbet_colors.tex'
    check('palette_byte_identical', sha(palette) == before['palette_sha256'])
    colors = re.findall(r'\\definecolor\{([^}]+)\}\{HTML\}\{([^}]+)\}', palette.read_text())
    visual = (ROOT / 'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md').read_text()
    check('all_13_exact_colors', len(colors) == 13 and all('#' + h in visual for _, h in colors))
    versions = {'docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md': 'Version: **v1.0**',
                'docs/process-report/WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md': 'Version: **v2.3**',
                'docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md': 'Design System v2.2'}
    check('active_versions', all(v in (ROOT / p).read_text() for p, v in versions.items()), versions)
    canonical = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'docs').rglob('*PROTOCOL*.md'))
    check('single_active_protocols', canonical == sorted(list(versions)[:2]), canonical)
    check('single_active_visual_system', len(list((ROOT / 'docs').rglob('SMART_CITIES_VISUAL_SYSTEM*.md'))) == 1)
    check('single_process_preview', len(list((ROOT / 'templates/latex/process-report/preview').glob('*.pdf'))) == 1)
    research = (ROOT / list(versions)[0]).read_text()
    check('research_modules_A_to_M', re.findall(r'^## ([A-M])\.', research, re.M) == list('ABCDEFGHIJKLM'))
    evidence = (ROOT / list(versions)[1]).read_text()
    required = ['Retrieval Screenshot', 'Formal Evidence Screenshot', 'Micro Trace', 'Interaction Window',
                'USER anchor phrase', 'RESPONDS_TO', 'ADOPTED_AS', 'one-to-many', 'many-to-one',
                'PHRASE MATCH: PASS / REVISE', 'ARROW RELATION: PASS / REVISE',
                'ARROW ENDPOINT: PASS / REVISE', 'SOURCE RESOLUTION: PASS / RECAPTURE',
                'Raw Screenshot Pixel Size', 'Final Display Size', 'Effective PPI', 'Annotation Medium']
    check('evidence_additions', all(t in evidence for t in required), {'missing': [t for t in required if t not in evidence]})
    rows = json.loads((OUT / 'source-inventory.json').read_text())
    manifest = (MIRROR / 'SOURCE_MANIFEST.md').read_text()
    verified = []
    for r in rows:
        src, dst = ROOT / r['source'], MIRROR / r['canonical']
        verified.append(sha(src) == sha(dst) == r['sha256'] and r['sha256'] in manifest)
    check('mirror_hashes_and_manifest', len(rows) == 11 and all(verified), {'payload_files': len(rows), 'manifest_rows': len(re.findall(r'^\| .* \| (?:PROJECT_SOURCE|NEW_PROJECT_SOURCE_TO_UPLOAD|SUPPORTING_GOVERNANCE|DISTRIBUTION_ARCHIVE) \|', manifest, re.M))})
    check('canonical_mirror_inventory', sorted(p.name for p in MIRROR.iterdir()) == sorted([r['canonical'] for r in rows] + ['SOURCE_MANIFEST.md']))
    index_equal = []
    for row in rows:
        src_index = subprocess.check_output(['git', 'show', ':' + row['source']], cwd=ROOT)
        dst_index = subprocess.check_output(['git', 'show', ':releases/chatgpt-project-sources/' + row['canonical']], cwd=ROOT)
        index_equal.append(src_index == dst_index == (MIRROR / row['canonical']).read_bytes())
    check('git_index_source_mirror_bytes', all(index_equal), {'pairs_checked': len(index_equal)})
    # Resolve real relative links in both installed and mirrored Markdown, and
    # repository URL links locally (their remote tree is checked after push).
    markdown = [ROOT / 'AGENTS.md', *list((ROOT / 'docs').rglob('*.md')),
                ROOT / 'templates/latex/process-report/README.md',
                ROOT / 'evidence/process-report/workflow-construction/WORKFLOW_EVIDENCE_PLAN.md',
                *list(MIRROR.glob('*.md')), OUT / 'README.md']
    broken = []; count = 0
    prefix = 'https://github.com/woobowen/Smart_Cities_and_Location_Services/blob/main/'
    for p in markdown:
        text = p.read_text()
        check('fenced_blocks_closed:' + str(p.relative_to(ROOT)), text.count('```') % 2 == 0)
        for link in re.findall(r'\]\(([^)\s]+)\)', text):
            count += 1
            path, _, anchor = unquote(link).partition('#')
            if path.startswith(prefix):
                target = ROOT / path[len(prefix):]
            elif re.match(r'\w+://', path):
                continue
            else:
                target = (p.parent / path).resolve() if path else p
            if not target.exists():
                broken.append({'source': str(p.relative_to(ROOT)), 'link': link})
            elif anchor and target.suffix == '.md':
                headings = re.findall(r'^#+\s+(.+)$', target.read_text(), re.M)
                anchors = [re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings]
                if anchor not in anchors:
                    broken.append({'source': str(p.relative_to(ROOT)), 'link': link, 'reason': 'missing anchor'})
    check('markdown_links', not broken, {'checked': count, 'broken': broken})
    with zipfile.ZipFile(ROOT / 'task1/作业.zip') as z:
        notebooks = []
        for name in ['任务3_LLM辅助评估清洗.ipynb', '作业1轨迹数据预处理.ipynb']:
            p = ROOT / 'task1/作业/作业' / name
            member = '作业/' + name
            notebooks.append({'name': name, 'cells': len(json.loads(p.read_text())['cells']), 'archive_member': member, 'identical': z.read(member) == p.read_bytes(), 'sha256': sha(p)})
    check('notebooks_match_teacher_archive', all(r['identical'] for r in notebooks), notebooks)
    with zipfile.ZipFile(ROOT / 'task1/实验课1.pptx') as z:
        slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
        title = ' '.join(ET.fromstring(z.read('ppt/slides/slide1.xml')).itertext())
    check('teacher_slides_content', len(slides) == 43 and '实验课安排和考核方式' in title, {'slides': len(slides), 'first_slide': title})
    archives = []
    for rel in ['releases/chatgpt-project-sources/publication-plots.zip', 'releases/skills/publication-plots.zip']:
        p = ROOT / rel
        with zipfile.ZipFile(p) as z:
            names = [n for n in z.namelist() if not n.endswith('/') and '__MACOSX' not in n and not n.endswith('.DS_Store')]
            equal = all(z.read(n) == (ROOT / 'tools/skills/publication-plots' / n.split('publication-plots/', 1)[-1]).read_bytes() for n in names)
        archives.append({'path': rel, 'sha256': sha(p), 'effective_members': len(names), 'equal_installed': equal})
    check('skill_archive_provenance', all(a['equal_installed'] and a['effective_members'] == 6 for a in archives) and archives[0]['sha256'] == 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041', archives)
    # Immutable Experiment source and preview remain their starting Git bytes.
    immutable = ['templates/latex/experiment-report/experiment_report_template.tex', 'templates/latex/experiment-report/preview/Experiment_Report_P2_Exact.pdf']
    same = [subprocess.check_output(['git', 'show', before['starting_sha'] + ':' + p], cwd=ROOT) == (ROOT / p).read_bytes() for p in immutable]
    check('experiment_report_unchanged', all(same), immutable)
    log = (OUT / 'latex-log.txt').read_text()
    warning_patterns = [r'^!', r'Undefined control sequence', r'LaTeX Warning:', r'Package \w+ Warning:', r'Overfull \\[hv]box', r'Missing character:', r'destination with the same identifier', r'Fatal error']
    warnings = [line for line in log.splitlines() if any(re.search(pat, line) for pat in warning_patterns)]
    check('latex_log', not warnings, warnings)
    pdftext = (OUT / 'pdf-text.txt').read_text()
    check('pdf_expected_content', 'SYNTHETIC / TEMPLATE ONLY' in pdftext and '短语对应与矢量批注' in pdftext)
    check('fresh_preview_matches_build', (ROOT / 'templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf').read_bytes() == (ROOT / 'templates/latex/process-report/build/process_report_template.pdf').read_bytes())
    ppilist = []
    for line in (OUT / 'pdf-images.txt').read_text().splitlines()[2:]:
        parts = line.split()
        if parts: ppilist.append({'page': int(parts[0]), 'size_px': [int(parts[3]), int(parts[4])], 'x_ppi': int(parts[12]), 'y_ppi': int(parts[13])})
    check('embedded_image_resolution', len(ppilist) == 5 and min(min(p['x_ppi'], p['y_ppi']) for p in ppilist) >= 200, ppilist)
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    check('git_diff_check', diff.returncode == 0, diff.stdout + diff.stderr)
    staged = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, capture_output=True, text=True)
    check('git_staged_diff_check', staged.returncode == 0, staged.stdout + staged.stderr)
    runtime = [ROOT / 'templates/latex/process-report/process_report_template.tex', ROOT / 'templates/latex/process-report/components/interaction_evidence.tex', ROOT / 'templates/latex/process-report/demo-assets/micro_trace_specimen.tex', OUT / 'sync_sources.py', OUT / 'validate_sync.py', OUT / 'build_preview.py']
    badpaths = [str(p.relative_to(ROOT)) for p in runtime if re.search(r'/(?:home|Users|mnt/[a-z])/', p.read_text())]
    check('no_absolute_personal_runtime_paths', not badpaths, badpaths)
    for p in runtime:
        if p.suffix == '.py': compile(p.read_text(), str(p), 'exec')
    check('python_syntax', True)
    (OUT / 'validation.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
    failed = {k: v for k, v in results.items() if not v['pass']}
    print(json.dumps({'checks': len(results), 'failed': failed}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(failed))

if __name__ == '__main__':
    main()
