"""Read actual staged blobs; summarize record-level risk without copying private values."""
from pathlib import Path
import argparse, ast, collections, csv, hashlib, io, json, re, subprocess, zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=Path(__file__).with_name('staged_semantic_inventory.json'))
OUT=parser.parse_args().output
changed={p.decode() for p in subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACMR','-z'],cwd=ROOT).split(b'\0') if p}
entries=[]
for entry in subprocess.check_output(['git','ls-files','-s','-z'],cwd=ROOT).split(b'\0'):
    if not entry:continue
    attrs,path=entry.split(b'\t',1);mode,oid,stage=attrs.decode().split();name=path.decode()
    if name in changed:entries.append((name,mode,oid))
entries.sort()
reader=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
npzs=[];csvs=[];nbs=[];risks=[];logs=[];svgs=[];archives=[];files=[];counts=collections.Counter()
secret=re.compile(rb'(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-[A-Za-z0-9]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
recordline=re.compile(r'^\s*\d+\s*[,\t]\s*(?:[0-9a-fA-F]{16,}|[0-9a-fA-F]{8}-)[^\n]*[,\t]\s*(?:[-+]?\d{1,3}\.\d{4,})',re.M)
riskkeys={'pairs','genes','initial_genes','initial','assignments','movements','drivers','orders','source_row','origin_source_row','destination_source_row','context','samples','origin','destination'}

def number_count(x):
    if isinstance(x,(int,float)):return 1
    if isinstance(x,list):return sum(number_count(y) for y in x)
    if isinstance(x,dict):return sum(number_count(y) for y in x.values())
    return 0

def walk(x,path,name):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in riskkeys and isinstance(v,(list,dict)) and number_count(v)>0:
                risks.append(dict(path=name,key_path=path+[k],kind='numeric membership/record context; classify synthetic vs real',numeric_leaves=number_count(v)))
            if k in {'lat','latitude','lon','longitude','venue_id','user_id'} and isinstance(v,(int,float,list)):
                risks.append(dict(path=name,key_path=path+[k],kind='coordinate/identity field with values'))
            walk(v,path+[k],name)
    elif isinstance(x,list):
        for i,v in enumerate(x):walk(v,path+[i],name)

for name,mode,oid in entries:
    reader.stdin.write((oid+'\n').encode());reader.stdin.flush()
    header=reader.stdout.readline().split();size=int(header[2]);blob=reader.stdout.read(size);assert reader.stdout.read(1)==b'\n'
    digest=hashlib.sha256(blob).hexdigest();suffix=Path(name).suffix.lower();counts[suffix]+=1
    files.append(dict(path=name,blob_oid=oid,bytes=size,sha256=digest))
    if secret.search(blob):risks.append(dict(path=name,kind='high-confidence secret pattern'))
    if suffix=='.npz':
        with np.load(io.BytesIO(blob),allow_pickle=False) as z:
            arrays={k:dict(shape=list(z[k].shape),dtype=str(z[k].dtype)) for k in z.files}
        npzs.append(dict(path=name,arrays=arrays))
    elif suffix=='.csv':
        rows=list(csv.reader(io.StringIO(blob.decode('utf-8-sig'))));csvs.append(dict(path=name,rows=len(rows)-1,columns=rows[0] if rows else []))
    elif suffix=='.ipynb':
        nb=json.loads(blob);outputs=[]
        for i,c in enumerate(nb['cells']):
            for j,o in enumerate(c.get('outputs',[])):
                texts=[]
                if 'text' in o:texts.append(''.join(o['text']))
                for k,v in o.get('data',{}).items():
                    if k.startswith('text/'):texts.append(''.join(v) if isinstance(v,list) else v)
                output='\n'.join(texts)
                if recordline.search(output):risks.append(dict(path=name,cell=i,kind='possible printed check-in record'))
                outputs.append(dict(cell=i,output=j,type=o.get('output_type'),text_chars=len(output),text_sha256=hashlib.sha256(output.encode()).hexdigest(),mime_types=list(o.get('data',{}))))
        nbs.append(dict(path=name,cells=len(nb['cells']),outputs=outputs))
    elif suffix=='.json':
        try:walk(json.loads(blob),[],name)
        except json.JSONDecodeError:risks.append(dict(path=name,kind='malformed JSON'))
    elif suffix=='.svg':
        text=blob.decode();collections_svg=re.findall(r'id="(PathCollection_\d+)"',text)
        svgs.append(dict(path=name,path_collections=collections_svg,use_elements=text.count('<use ')))
    elif suffix in {'.zip','.pptx'}:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            members=z.namelist();susp=[p for p in members if Path(p).suffix.lower() in {'.csv','.npz','.npy','.tsv'}]
        archives.append(dict(path=name,members=len(members),record_file_members=susp))
    elif suffix in {'.txt','.log','.md','.tex'}:
        text=blob.decode(errors='replace')
        if recordline.search(text):risks.append(dict(path=name,kind='possible tabular check-in line'))
        if suffix in {'.txt','.log'}:logs.append(dict(path=name,lines=len(text.splitlines()),bytes=len(blob),sha256=digest))
reader.stdin.close();reader.wait()
result=dict(scope='Actual index blobs for current changed/added files, not working tree or only inventory. Full blob bytes read. Numeric membership/context and coordinates recursively flagged for human classification; no private values copied.',staged_set_sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),files=len(files),bytes=sum(x['bytes'] for x in files),suffix_counts=dict(counts),npz=npzs,csv=csvs,notebooks=nbs,archives=archives,logs=logs,svg=svgs,content_risks=risks,blob_inventory=files,status='INVENTORIED_PENDING_SEMANTIC_ADJUDICATION')
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({**{k:result[k] for k in ['staged_set_sha256','files','bytes','suffix_counts']},'content_risk_paths':dict(collections.Counter(r['path'] for r in risks))},ensure_ascii=False,indent=2))
