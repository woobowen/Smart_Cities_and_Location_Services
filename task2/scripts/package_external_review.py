"""Create a fixed-commit review ZIP after an ordinary, verified GitHub push.

Every repository payload is read from the commit object, never an unstaged file.
The ZIP is kept outside the repository to avoid circular commit/archive hashes.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = 'https://github.com/woobowen/Smart_Cities_and_Location_Services'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def include(name):
    if name in {'AGENTS.md', 'README.md', '.gitignore', 'task2/.gitignore', 'task2/README.md', 'task2/requirements.txt'}:
        return True
    if name.startswith(('docs/research/', 'docs/report-writing/', 'docs/design-system/',
                        'docs/process-report/', 'tools/skills/publication-plots/', 'templates/latex/common/')):
        return Path(name).suffix in {'.md', '.tex', '.py'}
    if not name.startswith('task2/'):
        return False
    if Path(name).suffix in {'.png', '.npz', '.pptx'}:
        return False
    if name.startswith('task2/teacher_materials/'):
        return Path(name).suffix == '.ipynb'
    if name.startswith(('task2/src/', 'task2/tests/', 'task2/scripts/', 'task2/docs/', 'task2/review/',
                        'task2/notebooks/', 'task2/reports/', 'task2/figures/formal/',
                        'task2/figures/data/', 'task2/diagrams/', 'task2/public_results/', 'task2/releases/')):
        return True
    if name.startswith('task2/evidence/'):
        if any(part in name for part in ('/pdf_round1/', '/pdf_final/', '/report_render/',
                                         '/round1_snapshot/', '/previous_reviews/', '/surviving_prior_receipts/',
                                         '/replayed_output/', '/hash_verified_original_recovery/')):
            return False
        return Path(name).suffix in {'.md', '.json', '.py', '.txt', '.stdout', '.patch'} or name.endswith('ppt_render/实验2-任务分配（1）.pdf') or name.endswith('ppt_render/实验3-任务分配(2) 多目标与强化学习派单.pdf')
    if name.startswith('task2/results/online/'):
        return Path(name).name in {'metrics.csv', 'manifest.json'}
    if name.startswith('task2/results/evolution/'):
        return Path(name).name in {'SUMMARY.md', 'SUMMARY.csv'}
    if name.startswith('task2/results/rl/'):
        return Path(name).name in {'ACTIVE_RUNS.json', 'SUMMARY.csv', 'SUMMARY.md', 'COST_SCENARIOS.csv',
                                   'COST_SCENARIOS.json', 'day_metrics.json', 'paired_differences.json',
                                   'manifest.json', 'front_episode_mapping.json'}
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--remote-receipt', type=Path)
    args = parser.parse_args()
    commit = git('rev-parse', 'HEAD').decode().strip()
    branch = git('branch', '--show-current').decode().strip()
    remote = git('ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    if branch != 'main' or remote != commit:
        parser.error('main local HEAD and actual origin main must match before packaging')
    if git('status', '--porcelain').strip():
        parser.error('working tree must be clean; review the pending changes first')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f'Experiment2_Dispatch_GPT_Review_{commit[:12]}.zip'
    if output.exists():
        parser.error('fixed-version archive already exists; choose a fresh output directory')
    all_paths = [x.decode() for x in git('ls-tree', '-r', '--name-only', '-z', commit).split(b'\0') if x]
    selected = [name for name in all_paths if include(name)]
    payload = {name: git('show', f'{commit}:{name}') for name in selected}
    identity = dict(repository=REPOSITORY, branch=branch, local_head=commit, remote_main=remote,
                    fixed_commit_url=f'{REPOSITORY}/commit/{commit}',
                    review_url=f'{REPOSITORY}/blob/{commit}/task2/review/REVIEW_INDEX.md',
                    recorded_utc=datetime.now(timezone.utc).isoformat(),
                    status='READY_FOR_GPT_REVIEW_NOT_EXTERNAL_ACCEPTANCE',
                    payload_source='git show <fixed commit>:<path>; all omitted public engineering files remain at the same commit',
                    scope='All local research completed; restricted records not redistributed; Process native UI pages/Evidence Master Lock remain external.')
    payload['FIXED_COMMIT.json'] = json.dumps(identity, ensure_ascii=False, indent=2).encode()
    if args.remote_receipt:
        payload['REMOTE_READ_VERIFICATION.json'] = args.remote_receipt.read_bytes()
    readme = f'''# Fixed-version GPT review package

Commit: `{commit}`; local HEAD and actual origin/main were checked equal.

Start with [the review index](task2/review/REVIEW_INDEX.md), then requirement matrix,
method/metric definitions, experiment index, result/negative-result summary,
independent verification, visualizations, both PDFs, and reproduction instructions.

Remote immutable review entry: {identity['review_url']}

This small package includes actual code/tests, executed notebooks, public aggregate
fronts and metrics, formal vector figures, native diagrams, both reports and their
paired source ZIP, teacher text/PDF audits and independent evidence. Large public
synthetic instance/assignment sets, model arrays, duplicate page-render snapshots
and teacher PPTX remain available at the same remote commit. Original Foursquare
and reconstructable per-record derivatives remain local under the user's explicit
publication boundary; the real author download/hash/conversion path is documented.

Read FIXED_COMMIT.json and FILE_MANIFEST.json before reviewing. All repository
payloads came from the fixed Git object. This archive does not claim GPT review,
user understanding, teacher submission or Process Evidence Master Lock has passed.
'''
    payload['REVIEW_INDEX.md'] = readme.encode()
    payload['FILE_MANIFEST.json'] = json.dumps([
        dict(path=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
             source='fixed_git_commit' if name in selected else 'post_push_identity_envelope')
        for name, data in sorted(payload.items())
    ], ensure_ascii=False, indent=2).encode()
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 11, 5, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            archive.writestr(item, data)
    # Validate archive CRC, manifest payload hashes and exact fixed-commit binding.
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('archive CRC check failed')
        for row in json.loads(archive.read('FILE_MANIFEST.json')):
            if hashlib.sha256(archive.read(row['path'])).hexdigest() != row['sha256']:
                raise ValueError('manifest hash mismatch: ' + row['path'])
    receipt = dict(path=str(output.resolve()), sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                   bytes=output.stat().st_size, members=len(payload), fixed_commit=commit,
                   remote_main=remote, status='ARCHIVE_CRC_AND_PAYLOAD_HASHES_VERIFIED',
                   omitted_public_files='See same fixed commit; exclusions are for package size, not deletion from GitHub')
    output.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
