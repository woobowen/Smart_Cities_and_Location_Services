"""Bonus C: feasible NSGA-II QKM edge-value versus pickup front."""
import numpy as np
from evolution import EdgeDispatchProblem,run_nsga,knee_point
from rl_dispatch import km_max

class NSGADispatch:
    def __init__(self,LT,beta=.5,pop_size=40,n_gen=30,seed=0,choice='knee',pickup_fraction=.6):
        self.LT,self.beta=LT,beta
        self.pop_size,self.n_gen,self.seed=pop_size,n_gen,seed
        self.choice,self.pickup_fraction=choice,pickup_fraction
        self.fronts=[]

    def __call__(self,ctx):
        L=self.LT[ctx['t']][ctx['drv_zone'][:,None],ctx['dest_zone'][None]]
        W=ctx['fare'][None]+self.beta*L
        feasible=ctx['feas'] & (W>0)
        if not feasible.any():return []
        p=EdgeDispatchProblem(W,ctx['pickup'],feasible,K=None)
        r=run_nsga(p,pop_size=self.pop_size,n_gen=self.n_gen,seed=self.seed+ctx['t'])
        F=r['F']
        if self.choice=='knee':i=int(knee_point(F))
        elif self.choice=='constraint':
            parent=km_max(np.where(feasible,W,0))
            budget=self.pickup_fraction*sum(ctx['pickup'][a,b] for a,b in parent)
            eligible=np.flatnonzero(F[:,1]<=budget+1e-9)
            i=int(eligible[np.argmin(F[eligible,0])]) if len(eligible) else int(np.argmin(F[:,1]))
        else:raise ValueError('unknown front selection')
        self.fronts.append(dict(t=int(ctx['t']),F=F.tolist(),selected=i,n_eval=r['n_eval'],runtime=r['runtime'],pairs=r['pairs'][i]))
        return r['pairs'][i]
