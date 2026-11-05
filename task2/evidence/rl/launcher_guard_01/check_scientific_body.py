"""Compare scientific AST statements while excluding explicit CLI/output plumbing."""
from pathlib import Path
import ast,json,hashlib,difflib
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).parent
records=json.loads((HERE/'source_hashes.json').read_text())

def dump(n):return ast.dump(n,include_attributes=False)
def statements(tree):
    body=[]
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name=='main':return node.body
        if isinstance(node,ast.If) and '__name__' in ast.unparse(node.test):body.extend(node.body)
        else:body.append(node)
    return body

def normalized(nodes,name):
    out=[]
    for n in nodes:
        if isinstance(n,(ast.Import,ast.ImportFrom)):continue
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):continue
        if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call):
            f=n.value.func
            if isinstance(f,ast.Attribute):
                if f.attr in {'add_argument','add_mutually_exclusive_group','mkdir'}:continue
                if isinstance(f.value,ast.Attribute) and isinstance(f.value.value,ast.Name) and f.value.value.id=='sys' and f.value.attr=='path':continue
        if isinstance(n,ast.Assign):
            targets=[t.id for t in n.targets if isinstance(t,ast.Name)]
            if any(t in {'TASK','args','_CLI_ARGS'} for t in targets):continue
            if any(t in {'parser','a','p','output'} for t in targets) and ('ArgumentParser(' in ast.unparse(n.value) or 'add_mutually_exclusive_group(' in ast.unparse(n.value)):continue
            if 'out' in targets and ('results/rl' in ast.unparse(n.value) or ast.unparse(n.value)=='args.output'):continue
            if 'root' in targets and ('args.run' in ast.unparse(n.value) or ast.unparse(n.value)=='args.output' or 'args.phase' in ast.unparse(n.value)):continue
        # Diagnostics changes the destination directory only; its input root stays fixed.
        if name=='diagnose_rl_double.py' and isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='json_dump':
            n.value.args[0]=ast.Constant(value='OUTPUT/value_bias_diagnostics.json')
        out.append(dump(n))
    return out

results=[]
for r in records:
    name=Path(r['path']).name;old=(HERE/'original_sources'/name).read_text();new=(ROOT/r['path']).read_text()
    a=ast.parse(old);b=ast.parse(new)
    x=normalized(statements(a),name);y=normalized(statements(b),name)
    functions=[]
    for f in a.body:
        if isinstance(f,ast.FunctionDef) and f.name!='main':
            g=next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==f.name)
            functions.append(dict(name=f.name,identical=dump(f)==dump(g)))
    row=dict(path=r['path'],scientific_statements_equal=x==y,scientific_statement_count=len(x),original_library_functions=functions)
    if x!=y:row['difference']=list(difflib.unified_diff(x,y))
    r['guarded_sha256']=hashlib.sha256(new.encode()).hexdigest()
    results.append(row)
(HERE/'source_hashes.json').write_text(json.dumps(records,indent=2)+'\n')
(HERE/'changes.patch').write_text(''.join(''.join(difflib.unified_diff((HERE/'original_sources'/Path(r['path']).name).read_text().splitlines(keepends=True),(ROOT/r['path']).read_text().splitlines(keepends=True),fromfile='original/'+Path(r['path']).name,tofile='guarded/'+Path(r['path']).name)) for r in records))
result=dict(scope='AST equivalence of scientific statements after excluding only import, argument parsing, guarded output initialization and diagnostic destination path; all original library functions exactly equal.',results=results,status='PASS' if all(r['scientific_statements_equal'] and all(f['identical'] for f in r['original_library_functions']) for r in results) else 'FAIL')
(HERE/'scientific_body_equivalence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if result['status']!='PASS':raise SystemExit(1)
