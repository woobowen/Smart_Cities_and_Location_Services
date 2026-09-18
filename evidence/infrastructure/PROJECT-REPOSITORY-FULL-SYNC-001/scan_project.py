from pathlib import Path
import hashlib, io, json, os, re, subprocess, zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'evidence/infrastructure/PROJECT-REPOSITORY-FULL-SYNC-001'
RULES={
 'private_key':rb'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----',
 'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,255}|github_pat_[A-Za-z0-9_]{40,255})\b',
 'cloud_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'google_api_key':rb'\bAIza[A-Za-z0-9_-]{35}\b',
 'slack_token':rb'\bxox[baprs]-[A-Za-z0-9-]{15,200}',
 'service_secret':rb'\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,240}|hf_[A-Za-z0-9]{25,100})\b',
 'jwt':rb'\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{15,}\b',
 'credential_url':rb'[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:<>"\x27]{1,100}:[^\s/@<>"\x27]{1,150}@',
 'credential_literal':rb'(?i)\b["\x27]?(?:[A-Z0-9_]{0,64}(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|secret[_-]?key))["\x27]?\s*[:=]\s*["\x27]([^"\x27\r\n]{4,240})["\x27]',
 'env_secret':rb'(?im)^\s*(?:export\s+)?(?:[A-Z0-9_]{0,64}(?:API_KEY|ACCESS_TOKEN|AUTH_TOKEN|CLIENT_SECRET|PASSWORD|SECRET_KEY))\s*=\s*([^\s#]{4,240})',
 'authorization':rb'(?i)Authorization["\x27]?\s*[:=]\s*["\x27]?(?:Bearer|Basic)\s+[A-Za-z0-9+/_.=-]{12,240}',
}
RULES={k:re.compile(v) for k,v in RULES.items()}
findings=[]; objects=0; pdfs=0; archive_members=0; archive_metadata=[]; errors=[]
skip_report={OUT/'secret-scan-summary.json',OUT/'secret-scan-summary.txt'}
def scan(label,data,depth=0):
 global objects,pdfs,archive_members
 objects+=1
 for rule,pattern in RULES.items():
  for m in pattern.finditer(data):
   findings.append({'path':label,'rule':rule,'line':data.count(b'\n',0,m.start())+1,'match_sha256':hashlib.sha256(m.group()).hexdigest()})
 if data.startswith(b'%PDF'):
  p=subprocess.run(['pdftotext','-','-'],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if p.returncode: errors.append({'path':label,'tool':'pdftotext','returncode':p.returncode})
  else:
   pdfs+=1
   scan(label+'::extracted-text',p.stdout,depth+1)
 if data[:4] in (b'PK\x03\x04',b'PK\x05\x06'):
  if depth>8: raise RuntimeError('Archive nesting exceeds limit: '+label)
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   for item in z.infolist():
    if item.is_dir(): continue
    archive_members+=1
    if item.file_size>200_000_000: raise RuntimeError('Large archive member requires review: '+label+'::'+item.filename)
    if any(s=='__MACOSX' or s.startswith('._') or s=='.DS_Store' or s.endswith(':Zone.Identifier') for s in Path(item.filename).parts): archive_metadata.append(label+'::'+item.filename)
    scan(label+'::'+item.filename,z.read(item),depth+1)
files=[]; oversized=[]
for base,dirs,names in os.walk(ROOT):
 dirs[:]=sorted(d for d in dirs if d!='.git')
 for name in sorted(names):
  p=Path(base)/name
  if p in skip_report: continue
  if p.is_symlink(): raise RuntimeError('Review symlink before scanning: '+str(p))
  rel=p.relative_to(ROOT).as_posix(); data=p.read_bytes(); files.append(rel)
  if len(data)>50_000_000: oversized.append({'path':rel,'bytes':len(data)})
  scan(rel,data)
result={'scope':'Every on-disk regular file except .git and this scanner output; recursively scans ZIP/PPTX members and extracted PDF text. Raw SQLite bytes are included. No task1 code is executed. Pattern scan is not a proof of absence.','file_count':len(files),'scanned_objects':objects,'archive_members':archive_members,'pdf_text_extractions':pdfs,'rules':list(RULES),'findings':findings,'errors':errors,'files_over_50_MB':oversized,'metadata_members_preserved_inside_original_archives':archive_metadata}
(OUT/'secret-scan-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='metadata_members_preserved_inside_original_archives'},ensure_ascii=False,indent=2))
print('Embedded archive metadata members:',len(archive_metadata))
