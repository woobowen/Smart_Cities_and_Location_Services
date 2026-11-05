"""Independent context verification: raw inputs + alternative exact references."""
from pathlib import Path
from itertools import permutations
import csv, hashlib, json, math, sys, time
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
TASK=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(TASK/'src'))
import online
OUT=Path(__file__).resolve().parent

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def full_match_under(C, threshold):
    # Independent augmenting paths, no linear assignment routine.
    if C.shape[0]>C.shape[1]:C=C.T
    n,m=C.shape
    assigned=[-1]*m
    def augment(i,seen):
        for j in np.flatnonzero(C[i]<=threshold):
            if j in seen:continue
            seen.add(int(j))
            if assigned[j]<0 or augment(assigned[j],seen):
                assigned[j]=i
                return True
        return False
    return all(augment(i,set()) for i in range(n))

def exact_bottleneck(C):
    levels=np.unique(C)
    lo,hi=0,len(levels)-1
    while lo<hi:
        mid=(lo+hi)//2
        if full_match_under(C,levels[mid]):hi=mid
        else:lo=mid+1
    return float(levels[lo])

def lp_min_sum(C):
    if C.shape[0]>C.shape[1]:C=C.T
    n,m=C.shape
    eq=lil_matrix((n,n*m));ub=lil_matrix((m,n*m))
    for i in range(n):eq[i,i*m:(i+1)*m]=1
    for j in range(m):ub[j,j::m]=1
    r=linprog(C.ravel(),A_ub=ub.tocsr(),b_ub=np.ones(m),A_eq=eq.tocsr(),b_eq=np.ones(n),bounds=(0,1),method='highs')
    assert r.success
    return float(r.fun)

def main():
    started=time.time();checks=[]
    rng=np.random.default_rng(891)
    for n,m in [(1,1),(2,3),(3,2),(4,4)]:
        for _ in range(50):
            C=rng.integers(0,20,(n,m)).astype(float)
            A=C if n<=m else C.T
            opts=[max(A[i,p[i]] for i in range(len(A))) for p in permutations(range(A.shape[1]),len(A))]
            r,c=online.bottleneck_assignment(C)
            assert max(C[r,c])==min(opts)==exact_bottleneck(C)
    checks.append({'name':'bottleneck_independent_enumeration','instances':200,'status':'PASS'})
    # Explicit counterexample: min-sum diagonal max10; bottleneck off-diagonal max6.
    C=np.array([[0.,6.],[6.,10.]])
    r,c=online.bottleneck_assignment(C);assert C[r,c].max()==6
    checks.append({'name':'sum_not_bottleneck','matrix':C.tolist(),'bottleneck':6,'minimum_sum':10,'status':'PASS'})
    # Same-timestamp arrivals precede batch boundary, zero horizon, float batch lengths.
    for horizon,theta in [(0,.3),(1,.3),(2.1,.7)]:
        w=[online.Worker(1,(0.,0.),horizon)]
        q=[online.Request(2,(1.,0.),horizon)]
        for speed in [.5,2.]:
            alg=online.BBAlgorithm(theta,speed)
            a=online.run_simulation(w,q,alg,horizon)
            assert len(a)==1 and a[0].assign_time==horizon
            assert a[0].delay==1/speed
    checks.append({'name':'same_time_zero_horizon_float_theta_and_speed','cases':6,'status':'PASS'})
    try:online.run_simulation([online.Worker(1,(0,0),0),online.Worker(1,(1,1),0)],[],online.TBGAlgorithm(1),1)
    except ValueError:pass
    else:raise AssertionError('duplicate identity not rejected')
    checks.append({'name':'duplicate_ids','status':'PASS'})
    root=TASK/'results/online/development_v1'
    rows=list(csv.DictReader((root/'metrics.csv').open()))
    cached={};raw_edges=0
    for row in rows:
        inp=root/row['input'];mp=root/row['matches']
        assert digest(inp)==row['input_sha256'] and digest(mp)==row['matches_sha256']
        if row['input'] not in cached:
            d=json.loads(inp.read_text());ws={w['id']:w for w in d['workers']};rs={r['id']:r for r in d['requests']}
            C=np.array([[max(w['arrival_time'],r['arrival_time'])-r['arrival_time']+math.dist(w['loc'],r['loc'])/d['config']['speed'] for r in d['requests']] for w in d['workers']])
            cached[row['input']]=(d,ws,rs,lp_min_sum(C),exact_bottleneck(C))
        d,ws,rs,opt_sum,opt_max=cached[row['input']]
        matches=json.loads(mp.read_text());assert len(matches)==int(row['num_assigned'])
        assert len({a['worker_id'] for a in matches})==len(matches)
        assert len({a['request_id'] for a in matches})==len(matches)
        delays=[]
        for a in matches:
            w,r=ws[a['worker_id']],rs[a['request_id']]
            assert a['assign_time']+1e-9>=max(w['arrival_time'],r['arrival_time'])
            assert a['assign_time']<=d['config']['horizon']+1e-9
            pk=math.dist(w['loc'],r['loc']);wait=a['assign_time']-r['arrival_time'];delay=wait+pk/d['config']['speed']
            assert math.isclose(pk,a['pickup_distance'],abs_tol=1e-9)
            assert math.isclose(wait,a['wait'],abs_tol=1e-9)
            assert math.isclose(delay,a['delay'],abs_tol=1e-9)
            delays.append(delay);raw_edges+=1
        if delays:
            assert math.isclose(float(row['total_delay']),sum(delays),rel_tol=1e-12)
            assert math.isclose(float(row['max_delay']),max(delays),rel_tol=1e-12)
            assert math.isclose(float(row['p95_delay']),float(np.quantile(delays,.95)),rel_tol=1e-12)
        full=min(len(ws),len(rs))==len(matches)
        for key,opt,actual in [('sum',opt_sum,sum(delays)),('max',opt_max,max(delays) if delays else None)]:
            status=row['ratio_'+key+'_status']
            if full and delays and opt>0:
                assert status=='INSTANCE_RATIO'
                assert math.isclose(float(row['ratio_'+key]),actual/opt,rel_tol=1e-9)
                assert float(row['ratio_'+key])>=1-1e-9
            elif not full or not delays:
                assert status=='INCOMPARABLE_CARDINALITY_OR_EMPTY'
    checks.append({'name':'all_raw_dispatch_and_reported_metrics','runs':len(rows),'raw_assignments':raw_edges,'inputs':len(cached),'status':'PASS','reference':'LP (HiGHS) minimum-sum; custom augmenting paths bottleneck; raw geometric recompute'})
    report={'reviewer':'native child /root/reinforcement; independent of online author /root','scope':'current online.py and development_v1 raw results; no claim about future changes or RL own work','source_sha256':digest(TASK/'src/online.py'),'metrics_sha256':digest(root/'metrics.csv'),'checks':checks,'seconds':time.time()-started}
    (OUT/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
