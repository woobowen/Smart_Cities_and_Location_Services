import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from rl_dispatch import Config,make_repositioner
from rl_extensions import cost_aware_repositioner

def test_cost_zero_preserves_parent_and_high_cost_stops_motion():
    cfg=Config(grid=2,end=410,width=8,height=8)
    V=np.zeros((cfg.T+1,cfg.zones));V[:-1,1]=100
    position=np.array([2.,2.])
    a=make_repositioner(V,cfg)(0,position,0)
    b=cost_aware_repositioner(V,0,cfg)(0,position,0)
    assert np.array_equal(a[0],b[0]) and a[1:]==b[1:]
    assert cost_aware_repositioner(V,1000,cfg)(0,position,0) is None

def test_movement_gain_and_cost_have_a_known_threshold():
    cfg=Config(grid=2,end=410,width=8,height=8,gamma=.5)
    V=np.zeros((cfg.T+1,cfg.zones));V[:-1,1]=16
    position=np.array([2.,2.])
    # Neighbor is4km away, one time step, discounted value8; cost threshold2/km.
    assert cost_aware_repositioner(V,1.9,cfg)(0,position,0) is not None
    assert cost_aware_repositioner(V,2.,cfg)(0,position,0) is None
