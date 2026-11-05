"""Independent basic OD validation and MILP scalar references."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
from verify_evolution import ROOT, decode, digest


def main():
    folder=ROOT/'results/evolution/basic'
    b=dict(np.load(folder/'basic_synthetic_od.npz'))
    pickup=np.sqrt(((b['drv'][:,None]-b['o_xy'][None])**2).sum(2))
    fare=np.sqrt(((b['o_xy']-b['d_xy'])**2).sum(1))
    assert np.allclose(b['pickup'],pickup,atol=1e-12,rtol=0.)
    assert np.allclose(b['fare'],fare,atol=1e-12,rtol=0.)
    n,m=pickup.shape
    A=np.zeros((n+m,n*m))
    for d in range(n):A[d,d*m:(d+1)*m]=1
    for j in range(m):A[n+j,j::m]=1
    exact={}
    for lam in [0.,.25,.5,1.,2.]:
        objective=-(np.broadcast_to(fare,pickup.shape)-lam*pickup).ravel()
        solve=milp(objective,integrality=np.ones(n*m),bounds=Bounds(0.,1.),constraints=LinearConstraint(A,0.,1.))
        assert solve.success
        exact[lam]=-solve.fun
    reviewed=[]
    for p in sorted(folder.glob('basic_nsga2_seed*.json')):
        r=json.loads(p.read_text());F=np.array(r['F'])
        assert digest(folder/'basic_synthetic_od.npz')==r['provenance']['batch_sha256']
        for g,saved_pairs,f in zip(r['genes'],r['pairs'],F):
            pairs=decode(g,pickup,radius=float('inf'),K=n)
            assert set(pairs)==set(map(tuple,saved_pairs))
            e=[-sum(fare[j] for d,j in pairs),sum(pickup[d,j] for d,j in pairs)]
            assert np.allclose(e,f,atol=1e-9,rtol=0.)
        for entry in r['scalar_comparisons']:
            lam=entry['lam'];utility=(-F[:,0]-lam*F[:,1]).max()
            assert abs(exact[lam]-entry['exact_utility'])<1e-8
            assert abs(utility-entry['obtained_utility'])<1e-8
            assert abs(exact[lam]/utility-entry['ratio'])<1e-10
        reviewed.append({'path':str(p.relative_to(ROOT.parent)),'sha256':digest(p),'fronts':len(F)})
    receipt={'status':'PASS_SCOPE_LIMITED','reviewer':'/root/research_data','batch_sha256':digest(folder/'basic_synthetic_od.npz'),
             'exact_oracle':'SciPy MILP integral bipartite capacity <=1, distinct from execution linear_sum_assignment',
             'scalar_optima':exact,'reviewed':reviewed,
             'scope':'basic full-candidate Euclidean OD Pareto and static scalar approximation ratios; no online competitive guarantee'}
    (Path(__file__).parent/'basic_result.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':receipt['status'],'runs':len(reviewed),'MILP_scalar_references':len(exact)},indent=2))


if __name__=='__main__':main()
