"""Validate A's current source/locator links without granting content acceptance."""
from pathlib import Path
from datetime import datetime
import hashlib
import json
import re
import subprocess
from urllib.parse import unquote

OUT=Path(__file__).resolve().parent
ROOT=next(p for p in OUT.parents if (p/'AGENTS.md').is_file() and (p/'task1').is_dir())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def normal(s):return re.sub(r'\s+','',s)
d=json.loads((OUT/'MASTER_REQUIREMENTS_REVIEW.json').read_text())
expected={f'T1-{i:02}' for i in range(1,14)}|{f'T2-{i:02}' for i in range(1,9)}|{f'U{i:02}' for i in range(1,45)}
issues=[];checks=[]
snapshot_dir=str((OUT.parent/'review_input_snapshot').relative_to(ROOT))
manifest_path=f'{snapshot_dir}/SNAPSHOT_MANIFEST.json'
active_links=['task1/evidence/goal3/requirements.json','task1/evidence/goal3/goal_state.json',str((OUT.parent/'ACCEPTANCE_MATRIX.json').relative_to(ROOT))]
snapshot_expected={p:f'{snapshot_dir}/{Path(p).name}' for p in active_links[:2]}
snapshot_rows={};observed_at=None
# Snapshot validity is checked independently of later legitimate active-state changes.
# Do not compare active bytes with an older observation, and never omit snapshot hashes.
try:
    binding=d['bindings']['review_input_snapshot_manifest']
    if binding['path']!=manifest_path or binding['sha256']!=digest(ROOT/manifest_path):
        raise ValueError('review manifest binding mismatch')
    manifest=json.loads((ROOT/manifest_path).read_text())
    if manifest['purpose']!='IMMUTABLE_REVIEW_INPUT_SNAPSHOT_NOT_ACTIVE_STATE':
        raise ValueError('review manifest purpose mismatch')
    observed_at=manifest['created_at']
    if datetime.fromisoformat(observed_at.replace('Z','+00:00')).tzinfo is None:
        raise ValueError('review observation time has no timezone')
    if manifest['active_state_links']!=active_links or d['state_authority']!=active_links:
        raise ValueError('active navigation authority mismatch')
    rows=manifest['sources']
    if len(rows)!=2 or {r['active_path'] for r in rows}!=set(snapshot_expected):
        raise ValueError('review manifest must contain exactly two governance snapshots')
    for r in rows:
        expected_path=snapshot_expected[r['active_path']]
        p=ROOT/r['snapshot_path']
        if r['snapshot_path']!=expected_path or not p.is_file() or p.is_symlink() or digest(p)!=r['sha256']:
            raise ValueError(f"snapshot path/bytes mismatch: {r['active_path']}")
        snapshot_rows[r['active_path']]=r
    if len(d['bindings']['review_input_snapshots'])!=2:
        raise ValueError('derived ledger must bind both review inputs')
    checks.append({'id':'immutable_review_input_manifest_and_two_snapshots','ok':True})
except (KeyError,ValueError,TypeError,OSError) as exc:
    issues.append({'kind':'review_input_snapshot','reason':str(exc)})
    checks.append({'id':'immutable_review_input_manifest_and_two_snapshots','ok':False})
ids=[x['id'] for x in d['entries']]
checks.append({'id':'65_stable_ids','ok':len(ids)==65 and set(ids)==expected})
if not checks[-1]['ok']:issues.append('65_stable_ids')
# All Markdown local paths must resolve from their own document location.
link_count=0
for p in OUT.glob('*.md'):
    for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',p.read_text()):
        if '://' in target or target.startswith('mailto:'):continue
        fragment=target.split('#',1)[1] if '#' in target else None
        rel=unquote(target.split('#',1)[0])
        if not rel:
            if fragment and f'id="{fragment}"' not in p.read_text():issues.append({'kind':'missing_local_anchor','document':str(p.relative_to(ROOT)),'target':target})
            continue
        dest=(p.parent/rel).resolve();link_count+=1
        if not dest.exists():issues.append({'kind':'broken_link','document':str(p.relative_to(ROOT)),'target':target})
# All bound local sources are checked; none are silently treated as present.
source_count=0;seen=set()
def walk(x):
    global source_count
    if isinstance(x,dict):
        path=x.get('path');bound=x.get('sha256')
        active=x.get('source_active_path')
        if active in snapshot_expected:
            expected_snapshot=snapshot_rows.get(active,{})
            if path!=expected_snapshot.get('snapshot_path') or bound!=expected_snapshot.get('sha256') or x.get('observed_at_utc')!=observed_at or x.get('snapshot_manifest_path')!=manifest_path:
                issues.append({'kind':'snapshot_reference_binding','source_active_path':active,'path':path})
        if path in snapshot_expected and bound:
            issues.append({'kind':'mutable_active_state_hash_binding_forbidden','path':path})
        if path and isinstance(path,str) and not path.startswith(('https:','http:')):
            key=(path,bound)
            if key not in seen:
                seen.add(key);p=ROOT/path;source_count+=1
                if not p.exists():issues.append({'kind':'missing_source','path':path})
                elif bound and digest(p)!=bound:issues.append({'kind':'source_hash_changed','path':path})
        for v in x.values():walk(v)
    elif isinstance(x,list):
        for v in x:walk(v)
walk(d)
pdf={}
for r in d['bindings']['reports']:
    p=ROOT/r['path'];text=subprocess.check_output(['pdftotext','-layout',str(p),'-']).decode();arr=text.split('\f')
    if not arr[-1].strip():arr.pop()
    pdf[r['path']]=arr
    if digest(p)!=r['sha256'] or len(arr)!=r['page_count']:issues.append({'kind':'pdf_binding','path':r['path']})
nb_cache={};cell_count=0;anchor_count=0
for e in d['entries']:
    required=['sources','current_authority','why','implementation_applicability','comparison_and_checks','reviews','this_closeout_check','quality_supports','does_not_prove','status','remaining']
    if any(k not in e for k in required):issues.append({'kind':'schema','id':e['id']})
    for n in e['notebook_locators']:
        path=n['path']
        if path not in nb_cache:nb_cache[path]=json.loads((ROOT/path).read_text())
        cells=nb_cache[path]['cells'];c=cells[n['physical_index_zero_based']];src=''.join(c['source']) if isinstance(c['source'],list) else c['source']
        cell_count+=1
        if c['id']!=n['stable_cell_id'] or hashlib.sha256(src.encode()).hexdigest()!=n['source_sha256']:issues.append({'kind':'cell_binding','id':e['id'],'cell':n['stable_cell_id']})
    for r in e['report_locators']:
        anchor_count+=1
        if not r['physical_pages_one_based']:issues.append({'kind':'missing_pdf_anchor','id':e['id'],'anchor':r['text_anchor']})
        for page in r['physical_pages_one_based']:
            if normal(r['text_anchor']) not in normal(pdf[r['path']][page-1]):issues.append({'kind':'pdf_anchor','id':e['id'],'page':page})
for e in json.loads((OUT/'literature_use_map.json').read_text())['entries']:
    if not all(k in e for k in ['id','title','authors','venue_or_institution','status','actual_use','historical_causation_boundary','supported_proposition']):issues.append({'kind':'literature_schema','id':e['id']})
result={'role':'A_SELF_CHECK_NOT_INDEPENDENT_C','status':'LOCATOR_CHECKS_PASS' if not issues else 'REPAIR_REQUIRED','checks':checks,'counts':{'markdown_local_links':link_count,'unique_source_bindings':source_count,'entry_notebook_cell_locators':cell_count,'entry_pdf_text_locators':anchor_count,'immutable_governance_snapshots':len(snapshot_rows)},'issues':issues,'scope':'Current exact local links, bound source bytes, two real immutable governance-input snapshots and their manifest, all 65 IDs, all mapped stable cells and actual text-page anchors. Active governance is navigation only; no later-state equality, visual/experiment/teacher acceptance claim.','inputs':{p.name:digest(p) for p in [OUT/'MASTER_REQUIREMENTS_REVIEW.json',OUT/'literature_use_map.json',OUT/'TEACHING_DIFFERENCES.md']}}
(OUT/'A_SELF_CHECK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
raise SystemExit(bool(issues))
