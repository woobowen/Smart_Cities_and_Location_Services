"""Check basic CLI guard without importing or running the evolutionary algorithm."""
from datetime import datetime, timezone
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SCRIPT = ROOT / 'task2/scripts/run_basic_multiobjective.py'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
before = json.loads((OUT / 'before.json').read_text())
old = ast.parse((OUT / 'source_before.py').read_text())
new = ast.parse(SCRIPT.read_text())
get = lambda tree, name: next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
# Only output-path selection, directory refusal, and CLI dispatch differ.
assert ast.dump(get(old, 'convert')) == ast.dump(get(new, 'convert'))
assert [ast.dump(n) for n in get(old, 'main').body[2:]] == [ast.dump(n) for n in get(new, 'main').body[1:]]
assert all(sha(ROOT / path) == digest for path, digest in before['protected_artifacts'].items())
cases = []
with tempfile.TemporaryDirectory(prefix='basic_cli_guard_') as temporary:
    sandbox = Path(temporary)
    occupied = sandbox / 'occupied'
    occupied.mkdir()
    marker = occupied / 'marker.txt'
    marker.write_text('preserve existing artifact\n')
    direct_file = sandbox / 'direct-file.json'
    direct_file.write_text('preserve existing file\n')
    dangling = sandbox / 'dangling'
    dangling.symlink_to(sandbox / 'does-not-exist')
    fresh = sandbox / 'fresh'
    specs = [
        ('help', ['--help'], 0), ('default-existing', [], 2),
        ('existing-directory', ['--output', str(occupied)], 2),
        ('existing-file', ['--output', str(direct_file)], 2),
        ('dangling-symlink', ['--output', str(dangling)], 2),
        ('unknown-argument', ['--unknown-option', '--output', str(fresh)], 2),
    ]
    for mode, entry in [('direct', [str(SCRIPT)]), ('module', ['-m', 'task2.scripts.run_basic_multiobjective'])]:
        for label, arguments, expected in specs:
            command = [sys.executable, '-S', '-B'] + entry + arguments
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=15)
            assert result.returncode == expected, (mode, label, result.stdout, result.stderr)
            assert 'Traceback' not in result.stderr
            assert not fresh.exists()
            assert marker.read_text() == 'preserve existing artifact\n'
            assert direct_file.read_text() == 'preserve existing file\n'
            assert dangling.is_symlink() and not dangling.exists()
            cases.append(dict(mode=mode, case=label, returncode=result.returncode,
                              expected=expected, stdout=result.stdout, stderr=result.stderr,
                              site_packages_disabled=True, bytecode_disabled=True))
    # Parse the fresh destination in isolation; no scientific imports and no main body.
    nodes = [n for n in new.body if
             (isinstance(n, (ast.Import, ast.ImportFrom)) and
              (getattr(n, 'module', None) == 'pathlib' or
               any(alias.name == 'argparse' for alias in getattr(n, 'names', [])))) or
             (isinstance(n, ast.FunctionDef) and n.name == 'parse_args')]
    namespace = {'__file__': str(SCRIPT), 'ROOT': ROOT}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SCRIPT), 'exec'), namespace)
    parsed = namespace['parse_args'](['--output', str(fresh)])
    assert parsed.output == fresh.resolve() and not fresh.exists()

after = {path: sha(ROOT / path) for path in before['protected_artifacts']}
assert after == before['protected_artifacts']
assert all(r['runner_sha256_at_execution'] == before['old_runner_sha256']
           for r in before['existing_basic_runs'].values())
(OUT / 'source_after.py').write_bytes(SCRIPT.read_bytes())
receipt = dict(
    actual_utc=datetime.now(timezone.utc).isoformat(), author='/root/evolution',
    status='PASS_CLI_ONLY_NO_EXPERIMENT_EXECUTED',
    source_before_sha256=before['old_runner_sha256'], source_after_sha256=sha(SCRIPT),
    cases=cases, fresh_destination_parse_without_creation=True,
    main_scientific_body_ast_equal=True, conversion_function_ast_equal=True,
    protected_files=len(after), protected_sha256=after, protected_mutations=[],
    existing_basic_run_count=len(before['existing_basic_runs']),
    existing_run_identity='All five raw runs retain their original runner hash and bytes; CLI-only engineering revision is not retroactively their executed source.',
    limits='Author safety/AST checks only, no five-seed NSGA recomputation, no new statistical samples, and no claim to independent review.')
(OUT / 'result.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ['status', 'source_before_sha256', 'source_after_sha256', 'protected_files']}, ensure_ascii=False))
