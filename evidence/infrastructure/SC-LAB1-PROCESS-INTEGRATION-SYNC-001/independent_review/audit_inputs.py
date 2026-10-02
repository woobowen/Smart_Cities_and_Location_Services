"""Independent read-only input identity/archive audit for this authorized handoff.

Expected hashes below are transcribed from the user's prompt, not the manifest.
Only this reviewer's evidence directory is written.
"""
from collections import Counter
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASELINE = {
    'AGENTS.md': 'e1797cf00af4b55c1885d8e8753d93b0f4feadc6b1295670676e2636827a3a62',
    'SMART_CITIES_RESEARCH_PROTOCOL.md': '19f9bb4670bc3a485b064854f3d035d2a50a192386be53396851443ee5654a3f',
    'SMART_CITIES_REPORT_WRITING_GUIDE.md': 'd513867e76da9d5683a2b76325fa71bce8bb4387af6c2d148acb2e70fa6a5d0c',
    'SMART_CITIES_VISUAL_SYSTEM.md': '31501be77664a4d7f35ebb8d11118bdf58a18db7ce0090a125b4d87e95590b59',
    'WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md': '681ce8af7ead9b0d4abe0575ff546bc143064de42952bb5110bc350a420e4aa8',
    '实验课1.pptx': 'cf5fdbdd0e116818f4bf195e8761dd55c4733443d7c360c986cf1cdfddfda075',
    '作业.zip': '818d483cf719aeb1145ea97b551b2648913559ed1fca0be220ed41eff8ba42cc',
    '作业1轨迹数据预处理.ipynb': '8601d1dfecaef062fef553992cc9774d3a0eb551751c70536f5b52f1343b158a',
    '任务3_LLM辅助评估清洗.ipynb': '4ecffe64024e002c0cffe7830e18b5f6ded04cd5aa9dd645d6798fc9b0715add',
    'publication-plots.zip': 'b3d20aec75a8450e62effcb51399115c952fa6c3787c254fa09305e44a9c3041',
    'Experiment_Report_P2_Exact.pdf': '6fd543f5123ba4d67985193d5658802ae820c6585dc3f509071b8b2d39b323dd',
    'Experiment_Report_吴博闻_10245102410.pdf': '2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0',
    'Experiment_Report_完整重构_源文件.zip': '6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd',
    'Process_Report_Revised.pdf': '45f3b86f47c1b5cc7cf759ff713f5df3d4036e7ea9b4fff5eb3a40b6123aba83',
    'Process_Report_Revised_LaTeX_Source.zip': '00cb7b641b37b2a71a552fc5bef47fc551a16ea7ce88bcf139f2e68a5f1451da',
}
SECRET_PATTERNS = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'openai_token': re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b'),
    'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'aws_access_key': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'literal_credential_assignment': re.compile(rb'(?i)(?:api[_-]?key|password|access[_-]?token|secret)\s*[=:]\s*[\"\'][^\"\'\r\n]{12,}[\"\']'),
}


def archive_audit(source, identity, depth=0):
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        counts = Counter(i.filename for i in infos)
        record = {'archive': identity, 'crc_error': archive.testzip(),
                  'members': [], 'duplicate_names': [n for n, c in counts.items() if c > 1],
                  'unsafe_members': [], 'font_members': [], 'credential_candidates': [], 'nested_archives': []}
        for info in infos:
            name = info.filename
            p = PurePosixPath(name)
            mode = info.external_attr >> 16
            if p.is_absolute() or '..' in p.parts or '\\' in name or re.match(r'^[A-Za-z]:', name) or stat.S_ISLNK(mode):
                record['unsafe_members'].append(name)
            if info.is_dir():
                continue
            blob = archive.read(info)
            record['members'].append({'path': name, 'size': len(blob), 'sha256': sha256(blob).hexdigest()})
            if p.suffix.lower() in {'.ttf', '.otf', '.ttc', '.woff', '.woff2', '.pfb', '.pfa'}:
                record['font_members'].append(name)
            if p.name.lower() in {'.env', 'id_rsa', 'id_ed25519', 'credentials.json'}:
                record['credential_candidates'].append({'path': name, 'reason': 'credential_filename'})
            if b'\x00' not in blob[:8192] and len(blob) <= 10000000:
                for reason, pattern in SECRET_PATTERNS.items():
                    if pattern.search(blob):
                        record['credential_candidates'].append({'path': name, 'reason': reason})
            if p.suffix.lower() == '.zip':
                if depth >= 3:
                    record['nested_archives'].append({'archive': name, 'status': 'DEPTH_LIMIT'})
                else:
                    record['nested_archives'].append(archive_audit(BytesIO(blob), identity + '!' + name, depth + 1))
        return record


def main():
    if (OUT / 'initial_input_archive_audit.json').exists():
        raise FileExistsError('Initial handoff audit already exists; preserve its historical state. Use audit_final_state.py for current checks.')
    release = ROOT / 'releases/chatgpt-project-sources'
    checks = []
    for name, expected in BASELINE.items():
        candidates = [release / name]
        if (ROOT / name).is_file():
            candidates.append(ROOT / name)
        for path in candidates:
            actual = sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            checks.append({'path': str(path.relative_to(ROOT)), 'expected_sha256': expected,
                           'actual_sha256': actual, 'match': actual == expected})
    archives = []
    for name in ['Process_Report_Revised_LaTeX_Source.zip', 'Experiment_Report_完整重构_源文件.zip',
                 'SC-LAB1-G1-CLOSURE-002_HANDOFF.zip', 'SC-LAB1-G1-COMPLETE-001_HANDOFF.zip']:
        archives.append(archive_audit(ROOT / name, name))
    process = next(a for a in archives if a['archive'].startswith('Process_Report'))
    pairing = next(m for m in process['members'] if m['path'] == 'Process_Report_Revised_Source/Process_Report_Revised.pdf')
    pairing['matches_approved_pdf'] = pairing['sha256'] == BASELINE['Process_Report_Revised.pdf']
    history = []
    for path in [ROOT / 'reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_REVISED.pdf',
                 ROOT / 'reports/process-report/pre-task1/WF_WorkflowConstruction_PreTask1_31p_LaTeX_Source.zip',
                 ROOT / 'task1/reports/process1/process1.pdf',
                 ROOT / 'templates/latex/process-report/preview/Process_Report_P2_Locked_v1.pdf']:
        history.append({'path': str(path.relative_to(ROOT)), 'exists': path.is_file(),
                        'sha256': sha256(path.read_bytes()).hexdigest() if path.is_file() else None})
    evidence = {'review_context': '/root/independent_review; read-only production scope',
                'command': '.venv/bin/python evidence/infrastructure/SC-LAB1-PROCESS-INTEGRATION-SYNC-001/independent_review/audit_inputs.py',
                'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'hash_checks': checks, 'zip_pairing': pairing, 'history_initial': history, 'archives': archives}
    (OUT / 'initial_input_archive_audit.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'hash_checks': len(checks), 'matches': sum(x['match'] for x in checks),
                      'pairing': pairing, 'archives': [{k: a[k] for k in ['archive','crc_error','duplicate_names','unsafe_members','font_members','credential_candidates']} for a in archives],
                      'history': history}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
