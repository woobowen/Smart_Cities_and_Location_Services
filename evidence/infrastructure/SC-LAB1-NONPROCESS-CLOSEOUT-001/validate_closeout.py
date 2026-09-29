"""Read-only checks for this scoped closeout; writes only its own evidence JSON."""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = '89371f6597f92f7dac9abf61f6f6b18e29ed76cc'
DECLARATION = 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
SYNC = 'evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py'
OLD_REVIEW = 'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/REVIEW_PACKET.md'
AUTHORIZED = {
    'AGENTS.md', DECLARATION, SYNC, OLD_REVIEW,
    'evidence/infrastructure/chatgpt-project-source-sync/SOURCE_MANIFEST.md',
    'evidence/infrastructure/chatgpt-project-source-sync/UPLOAD_INSTRUCTIONS.md',
    'README.md', 'task1/README.md', 'task1/evidence/goal3/REVIEW_PACKET.md',
    'task1/docs/goal3/TECHNICAL_HANDOFF.md', 'task1/reports/README.md',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git_bytes(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def slug(text):
    text = re.sub(r'<[^>]*>', '', text).strip().lower()
    return re.sub(r'[^\w\- ]', '', text, flags=re.UNICODE).replace(' ', '-')


def check_links(paths):
    rows = []
    for relative in paths:
        source = ROOT / relative
        for match in re.finditer(r'\[[^\]]*\]\(([^\n)]+)\)', source.read_text()):
            raw = match.group(1).strip().strip('<>')
            link = urlsplit(raw)
            if link.scheme:
                prefix = 'https://github.com/woobowen/Smart_Cities_and_Location_Services/'
                if not raw.startswith(prefix + 'blob/main/') and not raw.startswith(prefix + 'tree/main/'):
                    continue
                rest = raw.split('/main/', 1)[1]
                local, _, anchor = rest.partition('#')
                target = ROOT / unquote(local)
            else:
                local, _, anchor = raw.partition('#')
                target = (source.parent / unquote(local)).resolve() if local else source
            valid = target.exists()
            if valid and anchor and target.suffix == '.md':
                headings = re.findall(r'^#{1,6}\s+(.+)$', target.read_text(), re.MULTILINE)
                valid = unquote(anchor) in {slug(h) for h in headings}
            rows.append(dict(source=relative, link=raw, valid=valid))
    return rows


def main():
    starting = json.loads((OUT / 'starting-protection-inventory.json').read_text())['files']
    moved = {r['source']: r for r in json.loads((OUT / 'metadata-relocation.json').read_text())['records']}
    unchanged, changed, relocated, failures = [], [], [], []
    for row in starting:
        path = row['path']
        item = ROOT / path
        if path in moved:
            saved = ROOT / moved[path]['preserved_path']
            ok = not item.exists() and saved.is_file() and digest(saved.read_bytes()) == row['sha256']
            ok = ok and saved.stat().st_mtime_ns == row['mtime_ns']
            (relocated if ok else failures).append(path)
            continue
        if item.is_symlink():
            stat = item.lstat()
            ok = row['type'] == 'symlink' and stat.st_size == row['size'] and stat.st_mtime_ns == row['mtime_ns']
            (unchanged if ok else failures).append(path)
            continue
        if not item.is_file():
            failures.append(path)
            continue
        stat = item.stat()
        current = digest(item.read_bytes())
        if current == row.get('sha256') and stat.st_mtime_ns == row['mtime_ns']:
            unchanged.append(path)
        elif path in AUTHORIZED:
            changed.append(dict(path=path, before_sha256=row.get('sha256'), after_sha256=current))
        else:
            failures.append(path)
    protection = dict(starting_files=len(starting), unchanged_count=len(unchanged),
                      unchanged_path_digest=digest('\n'.join(sorted(unchanged)).encode()),
                      authorized_changes=changed, metadata_relocations=relocated, failures=failures,
                      symlink_scope='Existing symlink lstat type/size/mtime preserved; no following or repairing dangling historical test links.',
                      pass_all=not failures)
    (OUT / 'protection-check.json').write_text(json.dumps(protection, ensure_ascii=False, indent=2) + '\n')

    received = json.loads((OUT / 'received-input-checks.json').read_text())
    inputs = []
    for r in received:
        paths = [OUT / 'received' / r['name'], ROOT / r['active_path'],
                 ROOT / 'releases/chatgpt-project-sources' / r['name']]
        inputs.append(dict(name=r['name'], all_three_match=all(
            p.stat().st_size == r['expected_size'] and digest(p.read_bytes()) == r['expected_sha256'] for p in paths)))
    current = json.loads((ROOT / DECLARATION).read_text())
    old = json.loads(git_bytes(DECLARATION))
    previous_rows = {r['canonical_name']: r for r in old['sources']}
    current_rows = {r['canonical_name']: r for r in current['sources']}
    other_metadata_unchanged = all(r == previous_rows[n] for n, r in current_rows.items() if n != 'AGENTS.md')
    actual_members = list((ROOT / 'releases/chatgpt-project-sources').iterdir())
    bundle = dict(declared_count=len(current_rows), set_matches_baseline=set(current_rows) == set(previous_rows),
                  actual_set_matches=set(p.name for p in actual_members) == set(current_rows),
                  all_regular=all(p.is_file() and not p.is_symlink() for p in actual_members),
                  all_hashes_match=all(digest((ROOT / r['active_path']).read_bytes()) == r['sha256'] ==
                                      digest((ROOT / 'releases/chatgpt-project-sources' / n).read_bytes())
                                      for n, r in current_rows.items()),
                  other_fifteen_metadata_unchanged=other_metadata_unchanged)
    before_ast = ast.parse(git_bytes(SYNC).decode())
    after_ast = ast.parse((ROOT / SYNC).read_text())
    for tree in [before_ast, after_ast]:
        tree.body = [n for n in tree.body if not isinstance(n, ast.FunctionDef) or n.name != 'instructions_text']
    synchronization_logic_unchanged = ast.dump(before_ast) == ast.dump(after_ast)

    history = {}
    for path, marker in [
        ('task1/evidence/goal3/REVIEW_PACKET.md', b'---\n\n## \xe5\x8e\x86\xe5\x8f\xb2\xef\xbc\x9aSC-LAB1-G3-CLOSEOUT-001'),
        ('task1/docs/goal3/TECHNICAL_HANDOFF.md', 'Parent Goal：`SC-LAB1-G3-FINAL-001`'.encode()),
    ]:
        before, after = git_bytes(path), (ROOT / path).read_bytes()
        history[path] = before.split(marker, 1)[1] == after.split(marker, 1)[1]
    history[OLD_REVIEW] = (ROOT / OLD_REVIEW).read_bytes().startswith(git_bytes(OLD_REVIEW))
    active_paths = [r['active_path'] for r in received]
    docs = sorted(set(active_paths + [p for p in AUTHORIZED if p.endswith('.md')] + [
        (OUT / 'REVIEW_PACKET.md').relative_to(ROOT).as_posix(),
        (OUT / 'UI_HANDOFF.md').relative_to(ROOT).as_posix(),
        'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/REVIEW_RECEIPT.md',
        'evidence/infrastructure/SC-PROJECT-SOURCES-SYNC-003/external_review/USER_RELAYED_PRIOR_REVIEW.md',
    ]))
    links = check_links(docs)
    reference = ROOT / 'reports/experiment-report/experiment1-reconstructed'
    artifacts = {
        'accepted_pdf': digest((reference / 'Experiment_Report_吴博闻_10245102410.pdf').read_bytes()) == '2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0',
        'accepted_source_zip': digest((reference / 'Experiment_Report_完整重构_源文件.zip').read_bytes()) == '6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd',
        'current_pdf': digest((ROOT / 'task1/reports/experiment1/experiment1.pdf').read_bytes()) == '2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0',
        'current_review_zip': digest((ROOT / 'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一_25页报告同步.zip').read_bytes()) == '231ce92475fdfe7ed12fa1c7e3304c22d6fd56ce39a0b53b43fee87103334a63',
    }
    result = dict(input_checks=inputs, bundle=bundle, only_instructions_text_ast_changed=synchronization_logic_unchanged,
                  historical_bodies_preserved=history, approved_artifacts=artifacts,
                  local_links_checked=len(links), local_link_rows=links,
                  protected_files=protection['starting_files'], protection_pass=protection['pass_all'],
                  new_report_builds=0, new_packages=0, new_experiment_model_calls=0, new_numerical_runs=0,
                  scope='Governance/navigation checks and hash inheritance; no inherited experiment or report build is represented as newly executed.')
    result['pass_all'] = (all(r['all_three_match'] for r in inputs) and all(v for k, v in bundle.items() if k != 'declared_count')
                          and synchronization_logic_unchanged and all(history.values()) and all(artifacts.values())
                          and all(r['valid'] for r in links) and protection['pass_all'])
    (OUT / 'author-verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(pass_all=result['pass_all'], protected_files=len(starting), unchanged=len(unchanged),
                         authorized_changes=len(changed), relocated=len(relocated), input_count=len(inputs),
                         bundle_count=len(current_rows), links_checked=len(links),
                         broken_links=[r for r in links if not r['valid']], protection_failures=failures), ensure_ascii=False))
    raise SystemExit(not result['pass_all'])


if __name__ == '__main__':
    main()
