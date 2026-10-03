"""Synthetic verifier fixtures only; these are NOT the teacher submission package."""
from pathlib import Path
import argparse,importlib.util,tempfile,hashlib,json,zipfile,sys
spec=importlib.util.spec_from_file_location('checker',Path(__file__).with_name('verify_teacher_zip.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--experiment-pdf',type=Path,required=True);parser.add_argument('--process-pdf',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
exp=args.experiment_pdf.read_bytes();pro=args.process_pdf.read_bytes()
nb=json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':[{'cell_type':'code','metadata':{},'source':['print("SYNTHETIC VALIDATOR FIXTURE")'],'execution_count':1,'outputs':[]}]}).encode()
base_payload={m.EXPERIMENT:exp,m.PROCESS:pro,m.NOTEBOOKS[0]:nb,m.NOTEBOOKS[1]:nb,'README.md':b'SYNTHETIC VERIFIER FIXTURE ONLY, NOT A SUBMISSION.','requirements.txt':b'# synthetic fixture\n'}
sha=lambda d:hashlib.sha256(d).hexdigest()
cases=[]
def archive(path,modify=None,post=None):
 data=base_payload.copy()
 if modify:modify(data)
 entries=[{'path':p,'bytes':len(d),'archive_sha256':sha(d)} for p,d in data.items()]
 man={'members':entries,'sent_to_teacher':False,'package_status':'TEACHER_SUBMISSION_CANDIDATE','member_count':len(entries),'total_uncompressed_bytes':sum(len(d) for d in data.values()),'test_fixture':True}
 if post:post(data,man)
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as z:
  for p,d in data.items():z.writestr(p,d)
  z.writestr('PACKAGE_MANIFEST.json',json.dumps(man).encode())

def check(name,okay=True,modify=None,post=None,wrong_hash=False):
 with tempfile.TemporaryDirectory(prefix='sc-synthetic-zip-test-') as td:
  p=Path(td)/'fixture.zip';archive(p,modify,post)
  try:m.validate(p,sha(exp),'0'*64 if wrong_hash else sha(pro));got=True;err=None
  except Exception as e:got=False;err=type(e).__name__+':'+str(e)
  cases.append({'test':name,'passed':got==okay,'expected_valid':okay,'observed_valid':got,'rejection':err})
check('valid declared files and actual PDF parsing')
check('wrong Process PDF hash',False,wrong_hash=True)
check('undeclared extra member',False,post=lambda d,j:d.update({'extra.txt':b'x'}))
check('manifest hash mismatch',False,post=lambda d,j:j['members'][0].update({'archive_sha256':'0'*64}))
check('missing required README',False,modify=lambda d:d.pop('README.md'))
check('path traversal',False,modify=lambda d:d.update({'../escape.txt':b'x'}))
check('font binary name',False,modify=lambda d:d.update({'fonts/forbidden.ttf':b'fixture'}))
check('nested ZIP',False,modify=lambda d:d.update({'nested.zip':b'fixture'}))
check('Windows case collision',False,modify=lambda d:d.update({'readme.MD':b'fixture'}))
check('incorrect declared count',False,post=lambda d,j:j.update({'member_count':999}))
check('misleading submitted flag',False,post=lambda d,j:j.update({'sent_to_teacher':True}))
check('old REVIEW_ONLY classification',False,post=lambda d,j:j.update({'package_status':'REVIEW_ONLY'}))
result={'scope':'SYNTHETIC_VERIFIER_FIXTURES_ONLY; not actual package verification or experiment execution','tests':cases,'passed':sum(c['passed'] for c in cases),'failed':sum(not c['passed'] for c in cases),'optional_real_static_probe_branch':'NOT_RUN_WITH_SYNTHETIC_FIXTURES; must run on actual package in Codex environment'}
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result['failed']))
