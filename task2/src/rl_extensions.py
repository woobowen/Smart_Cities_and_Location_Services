"""Result-triggered repositioning candidate; base training implementation frozen."""
import numpy as np
from rl_dispatch import DEFAULT


def cost_aware_repositioner(V, cost_per_km=1., config=DEFAULT):
    """Require discounted value gain to cover an explicitly hypothetical km cost."""
    if cost_per_km<0:raise ValueError('nonnegative cost required')
    xy=config.centers
    neighbors=[]
    for z in range(config.zones):
        r,c=divmod(z,config.grid)
        neighbors.append([rr*config.grid+cc for rr,cc in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
                          if 0<=rr<config.grid and 0<=cc<config.grid])
    def reposition(t,position,zone):
        cand=neighbors[int(zone)]
        if not cand:return None
        distances=np.abs(xy[cand]-position).sum(1)
        duration=np.maximum(1,np.ceil(distances/config.km_per_step)).astype(int)
        arrival=t+duration
        eligible=arrival<config.T
        gains=np.full(len(cand),-np.inf)
        gains[eligible]=(config.gamma**duration[eligible]*V[arrival[eligible],np.asarray(cand)[eligible]]
                         -config.gamma*V[min(t+1,config.T),int(zone)]-cost_per_km*distances[eligible])
        best=int(np.argmax(gains))
        if gains[best]<=1e-12:return None
        return xy[cand[best]].copy(),int(cand[best]),int(duration[best]),float(distances[best])
    return reposition
