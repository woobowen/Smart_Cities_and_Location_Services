"""Read-only final index/bundle/privacy audit; never writes the Git index or sources."""
import argparse
import ast
import copy
import difflib
import hashlib
import json
import re
import stat
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-refresh-root', type=Path, required=True)
    parser.add_argument('--private-process-archive', type=Path, required=True)
    args = parser.parse_args()
    review = Path(__file__).resolve().parent
    root = review.parents[3]
    prefix = 'evidence/infrastructure/SC-PROJECT-REFRESH-20261106/'
    baseline = 'b7fd9ee522905c11ddcea760470e7a5f0c1be9f0'

    def git(*arguments):
        return subprocess.check_output(['git', *arguments], cwd=root)

    def indexed(name):
        return git('show', ':' + name)

    def json_index(name):
        return json.loads(indexed(name))

    def index_objects():
        rows = {}
        for entry in git('ls-files', '--stage', '-z').split(b'\0'):
            if entry:
                header, name = entry.split(b'\t', 1)
                mode, oid, stage = header.decode().split()
                rows[name.decode()] = dict(mode=mode, git_blob=oid, stage=stage)
        return rows

    start_index = index_objects()
    paths = [p.decode() for p in git('diff', '--cached', '--name-only', '-z').split(b'\0') if p]
    deleted = [p.decode() for p in git('diff', '--cached', '--diff-filter=D', '--name-only', '-z').split(b'\0') if p]
    present = [p for p in paths if p not in deleted]
    blobs = {p: indexed(p) for p in present}
    snapshot = [dict(path=p, bytes=len(blobs[p]), sha256=sha(blobs[p]), **start_index[p])
                if p in blobs else dict(path=p, status='DELETED') for p in paths]
    failures = []

    def require(condition, name):
        if not condition:
            failures.append(name)
        return condition

    manifest_path = 'evidence/infrastructure/chatgpt-project-source-sync/sources.json'
    manifest = json_index(manifest_path)
    preflight = json_index(prefix+'preflight.json')
    old_rows = {r['canonical_name']: r for r in preflight['manifest_before']['sources']}
    rows = {r['canonical_name']: r for r in manifest['sources']}
    active = {name: row for name, row in rows.items() if row['project_source']}
    target = json_index(prefix+'approved_target.json')
    targets = {r['name']: r for r in target['target_project_sources']}
    versions = json_index(prefix+'approved_versions.json')
    require(len(rows) == 20 and len(active) == 12 and len(rows)-len(active) == 8, 'registration_20_active_12_false_8')
    require(set(active) == set(targets), 'active_names_exact_approved_target')
    require(all(active[n]['active_path'] == t['path'] and active[n]['semantic_role'] == t['kind']
                for n, t in targets.items()), 'active_paths_and_roles_exact_target')
    bundle_path = root/'releases/chatgpt-project-sources'
    require({p.name for p in bundle_path.iterdir()} == set(active), 'actual_bundle_exact_active_set')
    source_checks = []
    for name, row in active.items():
        source = indexed(row['active_path'])
        distribution = indexed('releases/chatgpt-project-sources/'+name)
        source_checks.append({'canonical_name': name, 'active_path': row['active_path'],
            'sha256': sha(source), 'bytes': len(source),
            'index_source_bundle_manifest_match': sha(source) == sha(distribution) == row['sha256'],
            'worktree_source_index_match': (root/row['active_path']).read_bytes() == source,
            'worktree_bundle_index_match': (bundle_path/name).read_bytes() == distribution})
    require(all(r['index_source_bundle_manifest_match'] and r['worktree_source_index_match'] and
                r['worktree_bundle_index_match'] for r in source_checks), 'all_12_authority_bundle_index_sha')
    retired = target['deactivate_keep_original_repo_files']
    require(set(deleted) == {'releases/chatgpt-project-sources/'+n for n in retired}, 'only_5_approved_release_deletions')
    historical = target['already_false_keep_false']
    require(all(rows[n] == old_rows[n] for n in historical), 'original_3_false_records_exactly_preserved')
    retired_checks = []
    for name in retired:
        expected_row = dict(old_rows[name], project_source=False)
        data = indexed(rows[name]['active_path'])
        backups = [args.private_refresh_root/'retired_release_backup'/name,
                   args.private_refresh_root/'retired_release'/name]
        retired_checks.append({'name': name, 'only_membership_changed': rows[name] == expected_row,
            'authority_preserved_in_index_and_worktree': sha(data) == rows[name]['sha256'] and
                data == (root/rows[name]['active_path']).read_bytes(),
            'two_private_copies_match_authority': all(p.is_file() and p.read_bytes() == data for p in backups)})
    require(all(all(value for key, value in r.items() if key != 'name') for r in retired_checks), 'retired_sources_and_private_backups_preserved')
    changed_docs = {r['filename'] for r in versions['changed_documents']}
    changed_names = changed_docs | set(retired) | {'Experiment2_Process_Report_吴博闻_10245102410.pdf'}
    require(all(rows[name] == row for name, row in old_rows.items() if name not in changed_names), 'unaffected_metadata_rows_preserved')

    package = args.private_refresh_root/'incoming_refresh/Smart_Cities_Project_Sources_Video_Workflow_Update_20261106.zip'
    doc_checks = []
    actual_diff = []
    with zipfile.ZipFile(package) as archive:
        require(sha(package.read_bytes()) == '5012d8643f7a59208b89dc5be803b65b8701e9c55a85cb8c345767adf55dae13', 'approved_package_exact_sha')
        settings = archive.read('PROJECT_SETTINGS_直接替换全文.txt')
        for row in versions['changed_documents']:
            name = row['repo_active_path']
            approved = archive.read('Project_Sources_Replace/'+row['filename'])
            data = indexed(name)
            doc_checks.append({'path': name, 'version': row['new_version'], 'sha256': sha(data),
                'approved_full_bytes_equal_index_worktree': data == approved == (root/name).read_bytes(),
                'manifest_hash_matches': sha(data) == row['new_sha256']})
            old = git('show', baseline+':'+name)
            actual_diff.append(''.join(difflib.unified_diff(old.decode().splitlines(keepends=True),
                data.decode().splitlines(keepends=True), fromfile='a/'+name, tofile='b/'+name)))
    require(all(r['approved_full_bytes_equal_index_worktree'] and r['manifest_hash_matches'] for r in doc_checks), 'all_4_approved_document_exact_bytes')
    require(''.join(actual_diff).encode() == indexed(prefix+'governance.diff'), 'actual_governance_diff_exact')
    protected = ['templates/','task1/','task2/src/','task2/results/','task2/public_results/',
        'task2/figures/','task2/diagrams/','task2/tests/','task2/notebooks/',
        'task2/reports/experiment/','task2/reports/generated/','task2/reports/common.tex',
        'task2/releases/Dispatch_Reports_LaTeX_Source.zip','docs/research/SMART_CITIES_RESEARCH_PROTOCOL.md']
    protected_changes = git('diff','--name-only',baseline,'--',*protected).decode().splitlines()
    require(not protected_changes, 'research_p2_experiment_and_research_artifacts_frozen')
    prior = 'task2/evidence/process_report_sync_20261106/independent_review/'
    original_audit = json_index(prior+'integration_audit.json')
    require(all(sha(indexed(r['path'])) == r['installed_sha256'] for r in original_audit['tex']), '11_process_tex_unchanged')
    require(all(sha(indexed(r['path'])) == r['sha256'] for r in original_audit['assets']), '18_png_inherited_exact_bytes')
    require({p for p in present if p.lower().endswith('.png')} == {r['path'] for r in original_audit['assets']}, 'published_png_set_exact_approved_18')
    pdfs = []
    for kind, expected, pages in [('process','c96c96bd267aaffd99232d23432bfe9dbc4804352acd0c25c145e9ddfa803e2f',16),
                                ('experiment','7a795625354e8a3c7034f8426171f8f8b32784db0cd398654b309c86ea72c101',26)]:
        p = 'task2/reports/'+kind+'/'+('Process_Report.pdf' if kind == 'process' else 'Experiment_Report.pdf')
        info = subprocess.check_output(['pdfinfo',str(root/p)],text=True)
        actual_pages = int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1))
        pdfs.append({'path':p,'sha256':sha(indexed(p)),'pages':actual_pages})
        require(sha(indexed(p)) == expected and actual_pages == pages, kind+'_approved_pdf_sha_pages')

    projection_meta = json_index(prefix+'publication_projection.json')
    original_path = args.private_refresh_root/'protected_evidence_audits/integration_original.json'
    original_bytes = original_path.read_bytes()
    original = json.loads(original_bytes)
    public = json_index('task2/evidence/process_report_sync_20261106/integration.json')
    require(sha(original_bytes) == projection_meta['original_record_sha256'], 'private_original_provenance_exact_sha')
    expected_public = copy.deepcopy(original)
    for asset in expected_public['selected_assets']:
        for field in ('video_timecode','raw_frame_sha256','crop_bounds_xyxy'):
            asset.pop(field,None)
    public_fields = dict(public)
    public_fields.pop('publication_projection')
    require(public_fields == expected_public, 'public_projection_only_approved_provenance_fields_omitted')
    require(sha(indexed('task2/evidence/process_report_sync_20261106/integration.json')) == projection_meta['public_projection_sha256'], 'public_projection_hash_exact')
    private_data = json_index('task2/evidence/research_data/local_only_manifest_current.json')
    private_data_paths = {r['path'] for r in private_data['files']}
    require(not (set(start_index) & private_data_paths), '1497_private_data_paths_absent_entire_index')
    require(not any(settings in data for data in blobs.values()), 'no_complete_settings_body_staged')
    forbidden = [p for p in present if Path(p).suffix.lower() in ('.mp4','.webm','.mov') or
        'PROJECT_SETTINGS_' in p or 'Smart_Cities_Project_Sources_Video_Workflow_Update_' in p or
        'SOURCE_resend.zip' in p or '/evidence/raw/' in p]
    require(not forbidden, 'no_private_input_or_raw_media_paths')
    with zipfile.ZipFile(args.private_process_archive) as archive:
        hidden = {sha(archive.read(n)) for n in archive.namelist()
                  if n.startswith('evidence/raw/') and n.endswith('.png') or
                     n.startswith('evidence/crops/D07') and n.endswith('.png')}
    raw_hash_references = []
    hidden_blob_matches = []
    for name, data in blobs.items():
        if sha(data) in hidden:
            hidden_blob_matches.append(name)
        if Path(name).suffix.lower() in ('.md','.json','.py','.txt','.tex','.diff'):
            text = data.decode('utf8',errors='replace')
            if any(h in text for h in hidden):
                raw_hash_references.append(name)
    require(not hidden_blob_matches and not raw_hash_references, 'hidden_17_media_bytes_and_hashes_absent')
    secret_patterns = [r'AKIA[0-9A-Z]{16}',r'AIza[A-Za-z0-9_-]{35}',r'github_pat_[A-Za-z0-9_]{40,}',
        r'gh[pousr]_[A-Za-z0-9]{36,}',r'sk-[A-Za-z0-9_-]{40,}',
        r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----']
    secret_candidates = []
    assignments = []
    links = []
    broken = []
    source_to_authority = {'releases/chatgpt-project-sources/'+n:r['active_path'] for n,r in active.items()}
    for name, data in blobs.items():
        if Path(name).suffix.lower() not in ('.md','.json','.txt','.tex','.py','.diff'):
            continue
        text = data.decode('utf8',errors='replace')
        secret_candidates.extend({'path':name,'signature':pattern} for pattern in secret_patterns if re.search(pattern,text))
        assignment = r'(?i)\b(?:api[_-]?key|access[_-]?token|secret[_-]?key|password|passwd)\b\s*[:=]\s*["\x27]([^"\x27\n]{6,})'
        assignments.extend({'path':name,'line':text.count('\n',0,m.start())+1} for m in re.finditer(assignment,text))
        if name.endswith('.md'):
            semantic_source = source_to_authority.get(name,name)
            for target_link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
                value = target_link.strip().strip('<>')
                if '://' in value or value.startswith(('#','mailto:','plugin:','app:')):
                    continue
                value = unquote(value.split('#',1)[0])
                if value:
                    links.append({'from':name,'resolved_as':semantic_source,'target':value})
                    if not (root/Path(semantic_source).parent/value).resolve().exists():
                        broken.append(links[-1])
    require(not secret_candidates and not assignments, 'no_high_confidence_secret_or_assignment_candidates')
    require(not broken, 'local_markdown_links_resolve_by_authoritative_source')
    navigation = ['README.md','task2/README.md','task2/reports/process/README.md',
        'task2/review/REVIEW_INDEX.md','task2/review/REPORT_PACKET.md',
        'task2/review/DELIVERY_GATE_REVIEW.md','evidence/infrastructure/chatgpt-project-source-sync/README.md']
    require(all('SC-PROJECT-REFRESH-20261106/REVIEW_PACKET.md' in indexed(p).decode() for p in navigation),
            'all_current_navigation_routes_new_review_packet')
    require('16 项中间方案历史记录' in indexed('task2/review/PROCESS_REPORT_SYNC_20261106.md').decode(),
            'old_16_member_plan_explicitly_historical')
    remote_tool_path = prefix+'verify_remote.py'
    remote_tool_bytes = indexed(remote_tool_path)
    remote_tree = ast.parse(remote_tool_bytes.decode())
    remote_git_verbs = sorted({node.args[0].value for node in ast.walk(remote_tree)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='git' and
           node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str)})
    require(set(remote_git_verbs) <= {'remote','rev-parse','ls-remote','show','ls-tree','diff'},
            'remote_tool_git_commands_read_only')
    help_run = subprocess.run([str(root/'.venv/bin/python'),'-B',str(root/remote_tool_path),'--help'],
        cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    require(help_run.returncode == 0 and (root/remote_tool_path).read_bytes() == remote_tool_bytes,
            'remote_tool_help_and_index_worktree_identity')
    require(all(start_index[p]['mode']=='100644' for p in present), 'staged_files_regular')
    worktree_mismatch = [p for p in present if (root/p).read_bytes() != blobs[p]]
    require(not worktree_mismatch, 'staged_bytes_match_worktree')
    checks = []
    commands = [[str(root/'.venv/bin/python'),'-B','evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py','--plan'],
        [str(root/'.venv/bin/python'),'-B','evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/sync_sources.py','--check'],
        [str(root/'.venv/bin/python'),'-B','evidence/infrastructure/SMART-CITIES-WORKFLOW-GOVERNANCE-AND-EVIDENCE-SYNC-001/validate_sync.py','--index'],
        ['git','diff','--cached','--check','--','*.md','*.py','*.tex','*.json'],
        ['git','diff','--cached','--check']]
    for command in commands:
        run = subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        checks.append({'command':command[1:] if command[0].endswith('/python') else command,
                       'returncode':run.returncode,'output':run.stdout})
    require(all(r['returncode']==0 for r in checks[:-1]), 'plan_check_index_source_doc_commands_pass')
    allowed_whitespace_records = {prefix+'governance.diff',
        'task2/evidence/process_report_sync_20261106/installed_build/process_compile.txt',
        'task2/evidence/process_report_sync_20261106/installed_build_fontfix/process_compile.txt'}
    actual_whitespace_records = set(re.findall(r'^(.+):\d+: (?:trailing whitespace|new blank line at EOF)\.',
        checks[-1]['output'],re.M))
    require(actual_whitespace_records <= allowed_whitespace_records, 'whitespace_warnings_only_3_original_records')
    require(index_objects() == start_index, 'index_objects_stable_during_audit')
    record = {'reviewer':'Codex independent agent process_integration_verifier',
        'recorded_utc':datetime.now(timezone.utc).isoformat(),'baseline':baseline,
        'scope':'Actual staged blobs, approved rule/package identity, 20/12/8 membership, authority/bundle/index hashes, preservation, privacy boundary and current navigation; no compile/experiment/push.',
        'staged_changed_paths':len(paths),'staged_present_files':len(present),'staged_deletions':deleted,
        'staged_snapshot_sha256':sha(json.dumps(snapshot,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()),
        'staged_snapshot':snapshot,'registered_rows':len(rows),'active_count':len(active),'inactive_count':len(rows)-len(active),
        'active_members':source_checks,'retired_checks':retired_checks,'approved_documents':doc_checks,
        'protected_changes':protected_changes,'reports':pdfs,'commands':checks,
        'private_projection':{'original_record_sha256':sha(original_bytes),'public_projection_sha256':projection_meta['public_projection_sha256'],
            'method':'Read private original bytes and compare public JSON against exactly the omitted selected-asset fields; original source conclusions unchanged.',
            'resolved_finding':'Detailed selected-frame timecode/raw-frame hash/crop bounds removed from public summary, original immutable bytes retained privately.'},
        'privacy':{'private_data_paths_checked':len(private_data_paths),'entire_index_intersection':sorted(set(start_index)&private_data_paths),
            'forbidden_paths':forbidden,'hidden_media_hashes_checked':len(hidden),'hidden_media_blob_matches':hidden_blob_matches,
            'hidden_media_hash_text_references':raw_hash_references,'high_confidence_secret_candidates':secret_candidates,'credential_assignment_candidates':assignments,
            'limits':'Static signatures do not prove all possible secrets absent. Same approved screenshot/PDF bytes inherit the prior scoped content and image-metadata review; no original video or broader historical Git scan is claimed.'},
        'local_links_checked':len(links),'broken_links':broken,'link_semantics':'Byte-identical release Markdown is checked in its authoritative active_path context; approved bytes were not edited to alter relative links.',
        'navigation_checked':navigation,
        'remote_tool_review':{'path':remote_tool_path,'git_blob':start_index[remote_tool_path]['git_blob'],
            'sha256':sha(remote_tool_bytes),'ast_syntax':'PASS','help_returncode':help_run.returncode,
            'actual_git_verbs':remote_git_verbs,
            'static_logic_review':'Exact repository and full commit identity checks; fixed HTTPS GET URLs quoted from Git paths; length/SHA256/Git blob checked before saving; output and readback root rejected inside repository; only external receipts/readback bytes are written; no push, local source mutation or remote mutation.',
            'scope_limit':'Actual network readback is a post-push action and was not executed. Operator uses fresh controlled external output directories; this is not an adversarial multi-tenant path-safety test.'},
        'whitespace_original_records':sorted(actual_whitespace_records),
        'worktree_mismatches':worktree_mismatch,
        'strict_render_limit':'Inherited same Process PDF/source: compile and text verified, 13 pages differ in strict 200-dpi pixels; complete validation command remained nonzero. No new compile/visual reread was performed.',
        'safety_regression_attribution':'37-test receipt is reviewed as the integration thread actual prior run; this independent audit does not claim to rerun that suite.',
        'fixed_remote_boundary':'No commit/push or remote fixed-object readback performed by this audit. After authorized ordinary push, coordinator must bind local/remote SHA and verify bytes at the fixed commit.',
        'not_granted':['ChatGPT UI completion','GPT external-review PASS','Evidence Master Lock','User final acceptance','Teacher submission'],
        'failures':failures,'release_recommendation':'PUBLISH_AUTHORIZED_SCOPE_AFTER_STAGING_REVIEW_RECEIPT' if not failures else 'DO_NOT_PUBLISH_UNTIL_RECORDED_FAILURES_RESOLVED'}
    (review/'FINAL_REFRESH_REVIEW.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'changed_paths':len(paths),'present_files':len(present),'snapshot_sha256':record['staged_snapshot_sha256'],
        '20_12_8':[len(rows),len(active),len(rows)-len(active)],'links_checked':len(links),'failures':failures,
        'recommendation':record['release_recommendation']},ensure_ascii=False))


if __name__ == '__main__':
    main()
