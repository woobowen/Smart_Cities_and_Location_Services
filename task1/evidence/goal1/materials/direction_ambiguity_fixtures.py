"""CONSTRUCTED_FIXTURE: show why unspecified marking schedule changes deletions.
This is a mathematical counterexample, not an approved teacher-data denoiser.
No repository processing module or real trajectory data is imported.
"""
from pathlib import Path
import json, math

def direction(a,b):
    if a==b: return None
    return math.degrees(math.atan2(b[0]-a[0], b[1]-a[1])) % 360

def gap(a,b):
    return abs((a-b+180)%360-180)

def comparisons(points, ids, threshold):
    dirs=[direction(a,b) for a,b in zip(points,points[1:])]
    out=[]
    for i in range(1,len(points)-2):
        values=dirs[i-1:i+2]
        valid=all(v is not None for v in values)
        gs=[gap(dirs[i],dirs[i-1]),gap(dirs[i],dirs[i+1])] if valid else None
        out.append({'original_index':ids[i], 'directions_deg':values,'differences_deg':gs,'marked': valid and all(g>threshold for g in gs)})
    return out

def simulate(points, policy, threshold=35.0):
    points=list(points); ids=list(range(len(points))); steps=[]
    if policy=='one_simultaneous_pass':
        checks=comparisons(points,ids,threshold);marked=[c['original_index'] for c in checks if c['marked']]
        steps.append({'checks':checks,'deleted':marked});ids=[i for i in ids if i not in marked]
    elif policy=='simultaneous_until_stable':
        for _ in range(len(points)):
            checks=comparisons(points,ids,threshold); marked=[c['original_index'] for c in checks if c['marked']]
            steps.append({'checks':checks,'deleted':marked})
            if not marked: break
            pairs=[(i,p) for i,p in zip(ids,points) if i not in marked]
            ids=[i for i,p in pairs];points=[p for i,p in pairs]
    elif policy=='left_to_right_immediate_recompute':
        for original in list(ids):
            c=next((c for c in comparisons(points,ids,threshold) if c['original_index']==original),None)
            if c is None: continue
            marked=[original] if c['marked'] else []
            steps.append({'checks':[c],'deleted':marked})
            if marked:
                at=ids.index(original);ids.pop(at);points.pop(at)
    return {'policy':policy,'kept_original_indices':ids,'steps':steps}

fixtures=[
 {'id':'DIRECTION-SCHEDULE-01','points':[(0,0),(0,1),(0,2),(1,2),(1,3)],'policies':['one_simultaneous_pass','simultaneous_until_stable'],'expected':[[0,1,3,4],[0,3,4]]},
 {'id':'DIRECTION-SCHEDULE-02','points':[(0,0),(0,3),(1,3),(1,4),(2,4)],'policies':['one_simultaneous_pass','left_to_right_immediate_recompute'],'expected':[[0,3,4],[0,2,3,4]]},
]
for f in fixtures:
    f['classification']='CONSTRUCTED_FIXTURE'
    f['purpose']='demonstrate unresolved marking schedule only; not authorize either schedule'
    f['coordinate_semantics']='abstract planar units, x east/y north; no CRS assumption about teacher data'
    f['threshold_deg']=35.0
    f['runs']=[simulate(f['points'],p) for p in f['policies']]
    actual=[r['kept_original_indices'] for r in f['runs']]
    assert actual==f['expected'],(f['id'],actual,f['expected'])
    f['verification']='PASS_FOR_COUNTEREXAMPLE'
p=Path(__file__).with_name('direction_ambiguity_fixtures.json')
p.write_text(json.dumps(fixtures,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'classification':'CONSTRUCTED_FIXTURE','examples':len(fixtures),'verification':'PASS_FOR_COUNTEREXAMPLE','output':p.name},ensure_ascii=False))
