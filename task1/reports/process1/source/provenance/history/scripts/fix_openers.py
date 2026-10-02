from pathlib import Path
import sys,json,shutil,numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent));from editorial import ROOT,UNITS,EXPECTED_WIDTH
au=json.loads((ROOT/'provenance/artifact_audit.json').read_text());bad=[o['unit'] for o in au['openers'] if not o['pass_ui']]
fixes={};history=[]
for uid in bad:
 u=next(u for u in UNITS if u['id']==uid);p=u['panels'][0].copy()
 if uid=='E06':
  p['src']='raw/ow54ouwaKl4.png';p['box']=[60,1223,474,1405]
 f=ROOT/'assets'/p['src']
 if not f.exists():shutil.copyfile(Path('/mnt/data')/Path(p['src']).name,f)
 im=Image.open(f).convert('L');a=np.array(im);W,H=im.size
 good=(a<75).mean(1)>.20;yy=np.where(good)[0];runs=[]
 if len(yy):
  start=last=int(yy[0])
  for y in yy[1:]:
   y=int(y)
   if y-last>12:
    if last-start>=18:runs.append((start,last))
    start=y
   last=y
  if last-start>=18:runs.append((start,last))
 assert runs,(uid,'No genuine user bubble found in this source')
 mid=(p['box'][1]+p['box'][3])/2
 run=min(runs,key=lambda a:abs((a[0]+a[1])/2-mid))
 # Keep the original horizontal conversational column, adjust only the true bubble window.
 p['box'][1]=max(0,run[0]-7);p['box'][3]=min(H,run[1]+8)
 p['role']='transfer' if p['role']=='transfer' else 'user'
 p['label']='我转交的Codex原始回复' if p['role']=='transfer' else '我的原始发言（该轮节选）'
 p['ay']=int(run[0]+.35*(run[1]-run[0]))
 fixes[uid]=p;history.append(dict(unit=uid,previous=u['panels'][0],replacement=p,detected_bubble_rows=run))
(ROOT/'provenance/opener_fixes.json').write_text(json.dumps(fixes,ensure_ascii=False,indent=2));(ROOT/'provenance/opener_window_repair.json').write_text(json.dumps(history,ensure_ascii=False,indent=2))
print('Repaired opener windows:',bad)
