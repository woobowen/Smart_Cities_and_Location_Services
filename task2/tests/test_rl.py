import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
import numpy as np
import pytest
from rl_dispatch import (Config, DEFAULT, T, N_ZONES, WAIT, GAMMA, DELTA,
                        QTable, DoubleQTable, q_update, double_q_update,
                        region_long_term_value, make_q_km, km_max, km_fare,
                        run_episode, make_repositioner)


def test_teacher_todo_1_verbatim():
    qt=QTable()
    qt.Q[5,3,7],qt.Q[5,3,9],qt.Q[5,3,WAIT]=30.,99.,10.
    td=q_update(qt,2,0,3,20.,5,3,np.array([7]))
    assert abs(td-(20+GAMMA**3*30))<1e-9
    assert qt.N[2,0,3]==1 and abs(qt.Q[2,0,3]-(20+GAMMA**3*30))<1e-9
    assert abs(qt.V[5,3]-30)<1e-9
    q_update(qt,2,0,3,0.,5,3,np.array([],int))
    assert abs(qt.Q[2,0,3]-(20+GAMMA**3*30+GAMMA**3*10)/2)<1e-9
    assert abs(qt.V[5,3]-20)<1e-9
    assert abs(q_update(qt,T-1,0,WAIT,7.,T+2,1,np.array([5]))-7)<1e-9


def test_teacher_todo_2_3_verbatim():
    V=np.zeros((T+1,N_ZONES));V[:T,0],V[:T,1]=5.,50.
    LT=region_long_term_value(V)
    assert LT.shape==(T,N_ZONES,N_ZONES)
    assert abs(LT[10,0,1]-(GAMMA**DELTA[0,1]*50-GAMMA*5))<1e-9
    assert abs(LT[T-1,1,0])<1e-9
    assert abs(LT[10,1,2]-(-GAMMA*50))<1e-9
    ctx=dict(t=10,fare=np.array([10.,10.]),drv_zone=np.array([0,1]),
             dest_zone=np.array([1,2]),feas=np.ones((2,2),bool))
    assert make_q_km(LT)(ctx)==[(0,0)]


def test_double_uses_other_table_and_actual_actions():
    qt=DoubleQTable()
    qt.A[5,3,[7,9,WAIT]]=[30,999,10]
    qt.B[5,3,[7,9,WAIT]]=[12,888,40]
    td=double_q_update(qt,2,0,3,20,5,3,np.array([7]),update_a=True)
    assert td==pytest.approx(20+GAMMA**3*12)
    assert qt.A[2,0,3]==td and qt.B[2,0,3]==0
    assert qt.NA[2,0,3]==1 and qt.NB[2,0,3]==0
    # A selects7, B evaluates12; B selectsWAIT, A evaluates10.
    assert qt.V[5,3]==11
    assert double_q_update(qt,T-1,0,WAIT,7,T+2,1,np.array([7]),update_a=False)==7


def test_partial_positive_km_matches_brute_force():
    from itertools import product
    rng=np.random.default_rng(3)
    for _ in range(20):
        W=rng.integers(-5,10,(3,2)).astype(float)
        exact=0
        for choices in product(range(-1,2),repeat=3):
            used=[v for v in choices if v>=0]
            if len(set(used))!=len(used):continue
            exact=max(exact,sum(W[a,b] for a,b in enumerate(choices) if b>=0))
        pairs=km_max(W)
        assert sum(W[a,b] for a,b in pairs)==exact
        assert all(W[a,b]>0 for a,b in pairs)


def tiny_episode(steps=(0,0,1),xy=((0,0),(0,0),(0,0)),trips=(8.,8.,1.)):
    oxy=np.asarray(xy,float)
    return (dict(step=np.asarray(steps),oxy=oxy,dxy=oxy+np.c_[trips,np.zeros(len(trips))],
                 dzone=np.zeros(len(steps),int),trip_km=np.asarray(trips),fare=np.ones(len(steps))*10),
            np.zeros((1,2)))


def test_occupancy_cancellation_and_conservation():
    cfg=Config(end=400,orders=3)
    metrics,trans=run_episode(tiny_episode(),km_fare,collect=True,config=cfg,trace=True)
    matches=metrics["trace"]["assignments"]
    assert all(b["t"]>=a["release"] for a,b in zip(matches,matches[1:]))
    assert metrics["orders"]==metrics["served"]+metrics["canceled"]+metrics["horizon_unassigned"]
    assert metrics["served"]==1 and metrics["canceled"]==1 and metrics["horizon_unassigned"]==1
    assert trans[0][4]==2
    # At release the driver is at (8,0), farther than radius3; no fake return.
    assert trans[0][6].size==0


def test_duplicate_driver_or_order_rejected():
    cfg=Config(end=400,orders=3)
    with pytest.raises(ValueError,match="duplicate"):
        run_episode(tiny_episode(),lambda ctx:[(0,0),(0,1)],config=cfg)


def test_no_match_metric_is_nan_and_end_ride_visible():
    cfg=Config(end=370,orders=1)
    ep=tiny_episode(steps=(0,),xy=((0,0),),trips=(8.,))
    m,_=run_episode(ep,lambda ctx:[],config=cfg)
    assert np.isnan(m["avg_pickup"]) and m["horizon_unassigned"]==1
    m,_=run_episode(ep,km_fare,config=cfg)
    assert m["served"]==1 and m["completed"]==0 and m["outstanding"]==1
    assert m["revenue"]==10 and m["completed_revenue"]==0


def test_beta_zero_is_exact_km_fare():
    rng=np.random.default_rng(4)
    V=rng.uniform(0,100,(T+1,N_ZONES));V[-1]=0
    ctx=dict(t=10,fare=rng.uniform(1,50,9),drv_zone=np.arange(4),
             dest_zone=np.arange(9),feas=rng.random((4,9))>.5)
    assert make_q_km(region_long_term_value(V),0)(ctx)==km_fare(ctx)


def test_reposition_has_time_distance_and_occupancy():
    cfg=Config(grid=2,end=410,width=8,height=8,orders=2)
    V=np.zeros((cfg.T+1,cfg.zones));V[:cfg.T,1]=100
    rep=make_repositioner(V,cfg)
    ep=(dict(step=np.array([0,1]),oxy=np.array([[7.,7.],[6.,2.]]),
             dxy=np.array([[7.,7.],[6.,2.]]),dzone=np.array([3,1]),
             trip_km=np.zeros(2),fare=np.ones(2)*10),np.array([[2.,2.]]))
    m,_=run_episode(ep,km_fare,config=cfg,reposition=rep,trace=True)
    move=m["trace"]["movements"][0]
    assert move["km"]==4 and move["release"]==1
    assert m["empty_km"]>=4 and m["empty_minutes"]>=10
    for ride in m["trace"]["assignments"]:
        assert ride["t"]>=move["release"]


def test_terminal_lt_zeros():
    V=np.ones((T+1,N_ZONES));V[-1]=0
    assert np.all(region_long_term_value(V)[-1]==0)
