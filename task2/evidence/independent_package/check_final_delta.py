"""Bounded semantic review of real index changes after the3518-file reviewed set."""
from pathlib import Path
import ast,collections,hashlib,io,json,math,re,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
base=json.loads((HERE/'staged_semantic_inventory_guarded.json').read_text());old={r['path']:r for r in base['blob_inventory']}
index=json.loads((HERE/'final_delta_index.json').read_text())['entries']
read=lambda oid:subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
sha=lambda b:hashlib.sha256(b).hexdigest()
newnames=sorted(set(index)-set(old));modified=sorted(n for n in index if n in old and index[n]!=old[n]['blob_oid']);removed=sorted(set(old)-set(index));assert not removed
current={n:read(index[n]) for n in newnames+modified}
previous={n:read(old[n]['blob_oid']) for n in modified}
private=json.loads((ROOT/'task2/evidence/research_data/local_only_manifest_current.json').read_text())['files']
assert len(private)==1497
assert not set(index)&{r['path'] for r in private}
privhash={r['sha256'] for r in private}
assert not [(n,sha(b)) for n,b in current.items() if sha(b) in privhash]
secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
record=re.compile(r'^\s*\d+\s*[,\t]\s*[0-9a-fA-F]{24}\b',re.M)
risks=[];riskkeys={'pairs','genes','initial_genes','initial','assignments','movements','drivers','orders','source_row','origin_source_row','destination_source_row','context','samples','origin','destination'}
def numbers(x):
 if isinstance(x,(int,float)) and not isinstance(x,bool):return 1
 if isinstance(x,list):return sum(numbers(v) for v in x)
 if isinstance(x,dict):return sum(numbers(v) for v in x.values())
 return 0
def walk(x,n,path=()):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in riskkeys and isinstance(v,(list,dict)) and numbers(v)>0:risks.append(dict(path=n,field=list(path)+( [k]),numeric_leaves=numbers(v)))
   walk(v,n,path+(k,))
 elif isinstance(x,list):
  for i,v in enumerate(x):walk(v,n,path+(i,))
for n,b in current.items():
 assert not secret.search(b),n
 if n.endswith('.json'):walk(json.loads(b),n)
 elif n.endswith(('.md','.txt','.py','.patch','.csv')):assert not record.search(b.decode(errors='replace')),n
 elif not n.endswith('.zip'):raise AssertionError('Unexpected new/changed binary '+n)
# New snapshots of formerly reviewed aggregates/source are matched to their old blobs.
old_snapshots=[]
prefix='task2/evidence/evolution/km_runtime_scope_fix/before/'
for n in newnames:
 if n.startswith(prefix):
  source=n[len(prefix):];assert source in old and sha(current[n])==old[source]['sha256'],n
  old_snapshots.append(dict(path=n,exact_previously_reviewed_source=source))
# The only possible numeric membership flags are schema/shape metadata inside the captured review inventory.
for r in risks:
 assert r['path']=='task2/evidence/independent_package/staged_semantic_inventory_guarded.json',r
 assert 'npz' in r['field'] and 'arrays' in r['field'],r
# Scientific metric JSON numbers are independently compared by complete paths.
def numeric_map(x,path=()):
 if isinstance(x,(int,float)) and not isinstance(x,bool):return {path:x}
 if isinstance(x,list):return {k:v for i,q in enumerate(x) for k,v in numeric_map(q,path+(i,)).items()}
 if isinstance(x,dict):return {k:v for i,q in x.items() for k,v in numeric_map(q,path+(i,)).items()}
 return {}
def diff(a,b,path=()):
 if type(a)!=type(b):return [dict(path=list(path),before=a,after=b)]
 if isinstance(a,dict):
  out=[]
  for k in sorted(set(a)|set(b)):
   if k not in a or k not in b:out.append(dict(path=list(path+(k,)),before=a.get(k),after=b.get(k)))
   else:out+=diff(a[k],b[k],path+(k,))
  return out
 if isinstance(a,list):
  assert len(a)==len(b)
  return [r for i,(x,y) in enumerate(zip(a,b)) for r in diff(x,y,path+(i,))]
 if isinstance(a,float) and math.isnan(a) and math.isnan(b):return []
 return [] if a==b else [dict(path=list(path),before=a,after=b)]
metric_checks=[]
for n in ['task2/results/evolution/metrics.json','task2/public_results/evolution/metrics.json']:
 a=json.loads(previous[n]);b=json.loads(current[n]);x=numeric_map(a);y=numeric_map(b)
 assert set(x)==set(y) and all(x[k]==y[k] or isinstance(x[k],float) and math.isnan(x[k]) and math.isnan(y[k]) for k in x)
 changes=diff(a,b);scope=[r for r in changes if r['path'][-1]=='runtime_scope'];assert len(scope)==5
 assert all(r['path'][-1] in {'runtime_scope','runner_sha256','sha256'} for r in changes)
 metric_checks.append(dict(path=n,numeric_leaves_exact=len(x),changes=changes))
n='task2/public_results/projection_manifest.json';md=diff(json.loads(previous[n]),json.loads(current[n]));assert len(md)==2 and all(r['path'][:2]==['bindings',120] and r['path'][-1] in {'source_sha256','public_sha256'} for r in md)
# Exclude precisely one metadata keyword to verify all other evaluator AST statements remain identical.
class MetadataOnly(ast.NodeTransformer):
 def visit_keyword(self,n):
  if n.arg=='runtime_scope':n.value=ast.Constant(value='RUNTIME_SCOPE_METADATA')
  return self.generic_visit(n)
n='task2/scripts/evaluate_evolution.py';assert ast.dump(MetadataOnly().visit(ast.parse(previous[n])))==ast.dump(MetadataOnly().visit(ast.parse(current[n])))
n='task2/scripts/resume_rl_rngfix.py';assert ast.dump(ast.parse(previous[n]))==ast.dump(ast.parse(current[n]))
sidecars=[]
for n in modified:
 if n.startswith('task2/figures/'):
  assert n.endswith('.json');changes=diff(json.loads(previous[n]),json.loads(current[n]))
  assert all(r['path'][0] in {'input_sha256','metadata_inheritance'} for r in changes),n
  sidecars.append(dict(path=n,changes=changes))
assert len(sidecars)==10
# Current report ZIP contains the same compiled assets; only provenance members can differ.
n='task2/releases/Dispatch_Reports_LaTeX_Source.zip'
with zipfile.ZipFile(io.BytesIO(previous[n])) as a,zipfile.ZipFile(io.BytesIO(current[n])) as b:
 assert a.namelist()==b.namelist() and len(a.namelist())==81
 package_changes=[p for p in a.namelist() if a.read(p)!=b.read(p)]
 assert set(package_changes)=={'task2/reports/generated/sources.json','SOURCE_PACKAGE_MANIFEST.json'},package_changes
 unchanged_assets=[dict(path=p,sha256=sha(b.read(p))) for p in b.namelist() if p not in package_changes]
receipt=json.loads(current['task2/evidence/report_source_package.json']);assert receipt['sha256']==sha(current[n]) and receipt['members']==81
# The independent CLI receipt binds all13 current launcher/helper sources, including the whitespace correction.
cli=json.loads(current['task2/evidence/independent_cli_guard/result.json']);assert cli['status']=='PASS_INDEPENDENT_CLI_AND_IMPORT_SCOPE' and cli['cases_count']==168
for n,h in cli['source_sha256'].items():assert sha(read(index[n]))==h,n
# Metadata-only additions are human-adjudicated within the explicit paths above.
allowed_prefixes=['task2/evidence/evolution/km_runtime_scope_fix/','task2/evidence/independent_cli_guard/','task2/evidence/independent_package/','task2/evidence/rl/launcher_guard_01/']
allowed_additions={'task2/evidence/publication/source_whitespace_scope.json','task2/evidence/report_build/km_metadata_table_regression.json','task2/review/DELIVERY_GATE_REVIEW.md'}
assert all(any(n.startswith(p) for p in allowed_prefixes) or n in allowed_additions for n in newnames)
# Every unaffected byte is inherited from the actual3518-file semantic review.
files=[]
for n in sorted(index):
 if n in current:b=current[n];size=len(b);h=sha(b)
 else:size=old[n]['bytes'];h=old[n]['sha256']
 files.append(dict(path=n,blob_oid=index[n],bytes=size,sha256=h))
collection_sha256=sha(json.dumps(files,sort_keys=True).encode())
result=dict(status='PASS_FINAL_BOUNDED_DELTA_IN_STATED_SCOPE',reviewer='/root/reinforcement',base_review='task2/evidence/independent_package/staged_semantic_review.json',base_staged_set_sha256=base['staged_set_sha256'],final_staged_files=len(files),final_staged_bytes=sum(r['bytes'] for r in files),final_staged_set_sha256=collection_sha256,unchanged_inherited_files=len(index)-len(newnames)-len(modified),added_files=newnames,modified_files=modified,removed_files=removed,all_delta_blob_bytes_read=True,raw_sensitive_path_intersections=0,raw_sensitive_hash_intersections=0,local_only_files_preserved=1497,new_real_record_inputs_or_membership=0,old_snapshots_verified=old_snapshots,metric_scientific_values=metric_checks,public_manifest_changes=md,evaluator_ast_equal_except_runtime_scope=True,resume_ast_equal_whitespace_only=True,sidecar_metadata_only=sidecars,report_source_package=dict(sha256=receipt['sha256'],members=81,changed_members=package_changes,unchanged_compilation_assets=unchanged_assets,inherited_compile='task2/evidence/independent_package/report_source_01/compile_comparison.json',scope='Current781d package byte-compared with priorc386 package.79compiled/deliveryassets unchanged; onlysources.json andSOURCE_PACKAGE_MANIFESTprovenance changed. Original0215 isolated26+8page compile/fulltext/200dpipixels inherited transitively viaEA assetidentity review. No newcompile or newvisualview claimed.'),independent_cli_receipt=dict(path='task2/evidence/independent_cli_guard/result.json',sha256=sha(current['task2/evidence/independent_cli_guard/result.json']),cases=168,sources_match_index=True),scope='Actual final index snapshot bound by final_delta_index.json. Prior3518 semantic review inherited only for identicalblob OIDs; all38added/30modified or actual counts above inspected. Metadata text andhash propagation only; no experiment/figure/report recomputation. Reviewer is independent ofrootpackaging/filter/report/Notebook andEAmetadatafix authors; RLguard authorship remains selfcheck, withR independentCLIreceipt separately attributed.',permitted_after_receipt='Root may append only evidence/independent_package/check_final_delta.py,final_delta_index.json,final_delta_review.json andthe finalR independentmetadata inheritance receipt, plusrefresh evidence/publication/staged_structural_audit.json. These are auditmetadata/code only andrequire exactpath/content check. No scientificdata/model/plot/report/code change iscovered bythat allowance.',external_limits='No remote publication, externalGPTreview, useracceptance, teacher submission orProcessUIEvidenceLock performed bythisreview.')
(HERE/'final_delta_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['status','final_staged_files','final_staged_bytes','final_staged_set_sha256','unchanged_inherited_files','raw_sensitive_path_intersections','new_real_record_inputs_or_membership']},indent=2))
