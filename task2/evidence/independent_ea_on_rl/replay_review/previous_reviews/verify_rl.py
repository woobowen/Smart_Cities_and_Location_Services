"""Independent raw-episode replay by the evolutionary-methods agent.

Reference replay deliberately does not import the author's RL simulator. Only
the explicit hand-calculation comparison imports functions under review.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import sys
from datetime import datetime,timezone
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[3]
TASK = ROOT/'task2'
OUT = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def near(actual, expected, label, tol=1e-7):
    if not np.allclose(actual, expected, atol=tol, rtol=1e-11, equal_nan=True):
        raise AssertionError(f'{label}: actual={actual}, reference={expected}')


def zone(xy):
    width = .30*111*math.cos(math.radians(40.74))
    height = .28*111
    xy = np.asarray(xy)
    return (np.clip((xy[..., 1]/height*8).astype(int), 0, 7)*8+
            np.clip((xy[..., 0]/width*8).astype(int), 0, 7))


def independent_lt(V):
    width, height = .30*111*math.cos(math.radians(40.74)), .28*111
    centers = np.array([((c+.5)*width/8, (r+.5)*height/8) for r in range(8) for c in range(8)])
    delta = np.maximum(1, np.ceil(np.abs(centers[:, None]-centers[None]).sum(-1)/(25/6))).astype(int)
    LT = np.zeros((108, 64, 64))
    for t in range(108):
        for i in range(64):
            for j in range(64):
                LT[t, i, j] = .92**int(delta[i, j])*V[min(t+int(delta[i, j]),108), j]-.92*V[t+1, i]
    return LT


def replay(episode_path, trace_path, expected, LT=None, beta=None, check_max_weight=False):
    with np.load(episode_path) as loaded:
        # NpzFile.__getitem__ decompresses the full member on every access.
        # Materialize once; reference mathematics/inputs are unchanged.
        e = {key:loaded[key] for key in loaded.files}
    tr = json.loads(trace_path.read_text())
    initial = e['drivers']
    near(initial, tr['initial'], 'trace initial drivers')
    n = len(e['step'])
    near(np.abs(e['oxy']-e['dxy']).sum(1), e['trip_km'], 'proxy trip metric')
    near(5+2*e['trip_km'], e['fare'], 'proxy fare')
    assert np.all(np.diff(e['step']) >= 0)
    pos, target = initial.copy(), initial.copy()
    free_at = np.zeros(len(pos), int)
    assignments_by_t = {t:[] for t in range(108)}
    movements_by_t = {t:[] for t in range(108)}
    for a in tr['assignments']:
        assignments_by_t[a['t']].append(a)
    for m in tr['movements']:
        movements_by_t[m['t']].append(m)
    seen, canceled, active = set(), set(), set()
    revenue = pickup_total = empty_total = empty_minutes = completed_revenue = 0.
    completed = feasible_edges = idle_opportunities = nonpositive_edges = 0
    contexts = []
    width, height = .30*111*math.cos(math.radians(40.74)), .28*111
    centers = np.array([((c+.5)*width/8, (r+.5)*height/8) for r in range(8) for c in range(8)])
    for t in range(108):
        available = np.flatnonzero(free_at <= t)
        pos[available] = target[available]
        active.update(map(int, np.flatnonzero(e['step'] == t)))
        expired = {o for o in active if t-int(e['step'][o]) > 2}
        active -= expired
        canceled |= expired
        offers = sorted(active)
        pickup = np.abs(pos[available, None]-e['oxy'][offers][None]).sum(-1)
        feas = pickup <= 3.
        feasible_edges += int(feas.sum())
        idle_opportunities += len(available)
        weights = None
        if LT is not None:
            weights = e['fare'][offers][None]+beta*LT[t][zone(pos[available])[:, None], e['dzone'][offers][None]]
            nonpositive_edges += int(np.sum(feas & (weights <= 0)))
        served_now = assignments_by_t[t]
        local_pairs = []
        drivers_now = set()
        for a in served_now:
            d, o = a['driver'], a['order']
            assert d in available and o in active and d not in drivers_now and o not in seen
            drivers_now.add(d);seen.add(o);active.remove(o)
            pk = float(np.abs(pos[d]-e['oxy'][o]).sum())
            assert pk <= 3.+1e-9 and t >= int(e['step'][o]) and t-int(e['step'][o]) <= 2
            duration = max(1, math.ceil((pk+float(e['trip_km'][o]))/(25/6)))
            near(a['pickup'], pk, 'actual pickup')
            near(a['trip'], e['trip_km'][o], 'actual trip')
            near(a['fare'], e['fare'][o], 'actual fare')
            near(a['origin'], pos[d], 'driver release position, no teleport')
            near(a['destination'], e['dxy'][o], 'passenger destination')
            assert a['release'] == t+duration
            free_at[d], target[d] = t+duration, e['dxy'][o]
            revenue += float(e['fare'][o]);pickup_total += pk
            if t+duration <= 108:
                completed += 1;completed_revenue += float(e['fare'][o])
            local_pairs.append((int(np.where(available == d)[0][0]), offers.index(o)))
        if check_max_weight and weights is not None and weights.size:
            W = np.where(feas, np.maximum(weights, 0), 0)
            ri, ci = linear_sum_assignment(-W)
            chosen = sum(W[a,b] for a,b in local_pairs)
            near(chosen, W[ri,ci].sum(), 'independent scalar utility optimum')
        contexts.append(dict(t=t, available=available.tolist(), offers=offers, pickup=pickup,
                             feas=feas, weights=weights, local_pairs=local_pairs))
        for m in movements_by_t[t]:
            d = m['driver']
            assert d in available and d not in drivers_now
            drivers_now.add(d)
            near(m['origin'], pos[d], 'empty move departure')
            destination = np.asarray(m['destination'])
            km = float(np.abs(destination-pos[d]).sum())
            duration = max(1, math.ceil(km/(25/6)))
            near(m['km'], km, 'empty move distance')
            assert m['release'] == t+duration and m['release'] < 108
            z0, z1 = int(zone(pos[d])), int(zone(destination))
            assert abs(z0//8-z1//8)+abs(z0%8-z1%8) == 1
            near(destination, centers[z1], 'actual neighboring-region center')
            free_at[d], target[d] = t+duration, destination
            empty_total += km;empty_minutes += duration*10
        step = tr['steps'][t]
        near([step['t'],step['available'],step['waiting'],step['accepted']],
             [t,len(available),len(active),len(served_now)], 'step ledger')
        near([step['revenue'],step['empty_km']], [revenue,empty_total], 'cumulative metrics')
    assert len(seen)+len(canceled)+len(active) == n
    near(tr['final_free_at'], free_at, 'final occupancy')
    obtained = dict(revenue=revenue, answer_rate=len(seen)/n, avg_pickup=pickup_total/len(seen),
                    pickup_km=pickup_total, served=len(seen), completed=completed,
                    outstanding=len(seen)-completed, completed_revenue=completed_revenue,
                    canceled=len(canceled), horizon_unassigned=len(active), orders=n,
                    empty_km=empty_total, empty_minutes=empty_minutes,
                    reposition_count=len(tr['movements']), diagnostic_net_revenue=revenue-empty_total,
                    feasible_edges=feasible_edges, idle_opportunities=idle_opportunities)
    if LT is not None:
        obtained.update(nonpositive_edges=nonpositive_edges,
                        nonpositive_fraction=nonpositive_edges/feasible_edges if feasible_edges else float('nan'))
    for key,value in obtained.items():
        near(expected[key], value, f'day metric {key}')
    return obtained, contexts


def hand_updates():
    sys.path.insert(0, str(TASK/'src'))
    from rl_dispatch import Config,QTable,DoubleQTable,q_update,double_q_update,region_long_term_value
    cfg = Config(grid=2,start=0,end=100)
    q = QTable(cfg)
    q.Q[5,1,2]=30;q.Q[5,1,3]=999;q.Q[5,1,cfg.wait]=10
    td = q_update(q,2,0,1,20,5,1,np.array([2]))
    near(td, 20+.92**3*30, 'feasible Q target')
    near(q.V[5,1],30,'feasible state value')
    q_update(q,2,0,1,0,5,1,np.array([],int))
    near(q.Q[2,0,1],(20+.92**3*30+.92**3*10)/2,'visit learning rate')
    near(q.V[5,1],20,'V sample mean')
    for update_a in [True,False]:
        d=DoubleQTable(cfg)
        one,two=(d.A,d.B) if update_a else (d.B,d.A)
        one[5,1,2]=30;one[5,1,0]=1000;one[5,1,cfg.wait]=2
        two[5,1,2]=7;two[5,1,cfg.wait]=9
        actual=double_q_update(d,2,0,1,20,5,1,np.array([2]),update_a=update_a)
        near(actual,20+.92**3*7,'Double argmax-one/evaluate-other')
        near(d.V[5,1],(7+2)/2,'symmetric cross-estimator V')
        near(two[2,0,1],0,'unselected estimator unchanged')
        near(double_q_update(d,9,0,cfg.wait,5,12,1,np.array([0]),update_a=update_a),5,'Double terminal target')
    V=np.random.default_rng(1).uniform(0,100,(109,64));V[-1]=0
    near(region_long_term_value(V),independent_lt(V),'full regional LT table')
    return dict(feasible_action_q=True,visit_mean=True,double_selection_evaluation=True,
                double_both_branches=True,double_terminal=True,full_LT=True)


def decode_independent(gene, pickup, feas):
    candidates=[]
    for j in range(pickup.shape[1]):
        ds=np.argsort(pickup[:,j],kind='stable')
        candidates.append([int(d) for d in ds if feas[d,j]])
    pairs,used=[],set()
    for j,g in enumerate(gene):
        c=candidates[j]
        if not g or not c:continue
        for shift in range(len(c)):
            d=c[(int(g)-1+shift)%len(c)]
            if d not in used:
                used.add(d);pairs.append((d,j));break
    return pairs


def static_fusion():
    dr=TASK/'results/rl/fusion_validation_v1'
    b=np.load(dr/'static_input.npz')
    V=np.load(TASK/'results/rl/development_v1/q_f60_s2024/model.npz')['V']
    LT=independent_lt(V)
    expected_weights=b['fare'][None]+.5*LT[int(b['t'])][b['drv_zone'][:,None],b['dest_zone'][None]]
    near(b['weights'],expected_weights,'static true estimated QKM weights')
    assert np.array_equal(b['feas'],(b['pickup']<=3)&(expected_weights>0))
    rows=json.loads((dr/'static_fronts.json').read_text())
    n_front=0
    for r in rows:
        saved=np.load(dr/f"static_seed{r['seed']}.npz")
        near(saved['F'],r['F'],'static dual serialization')
        for gene,F,pairs in zip(saved['genes'],saved['F'],r['pairs']):
            actual_pairs=decode_independent(gene,b['pickup'],b['feas'])
            assert set(actual_pairs)==set(map(tuple,pairs))
            val=sum(expected_weights[d,j] for d,j in pairs)
            pk=sum(b['pickup'][d,j] for d,j in pairs)
            near(F,[-val,pk],'static decoded objectives')
            n_front+=1
        assert r['n_eval']==30100
    # Independent exhaustive partial matchings on sparse 8-active-driver graph.
    drivers=np.flatnonzero(b['feas'].any(1))
    choices=[[-1]+np.flatnonzero(b['feas'][d]).tolist() for d in drivers]
    obj=[]
    for orders in itertools.product(*choices):
        used=[j for j in orders if j>=0]
        if len(set(used))!=len(used):continue
        pairs=[(d,j) for d,j in zip(drivers,orders) if j>=0]
        obj.append([-sum(expected_weights[d,j] for d,j in pairs),sum(b['pickup'][d,j] for d,j in pairs)])
    obj=np.asarray(obj)
    km=json.loads((dr/'static_weighted_km.json').read_text())
    for r in km:
        near(-r['F'][0]-r['lam']*r['F'][1],(-obj[:,0]-r['lam']*obj[:,1]).max(),'fusion exact scalar matching')
    return dict(static_front_solutions=n_front,exhaustive_partial_matchings=len(obj),
                active_drivers=len(drivers),checked_scalar_references=len(km))


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    core=[TASK/'src'/name for name in ['rl_dispatch.py','rl_extensions.py','rl_fusion.py']]
    packet=dict(reviewer='/root/evolution',role='independent RL verification, not RL author',
                verifier_sha256=sha(__file__),started_utc=datetime.now(timezone.utc).isoformat(),
                code_hashes={str(p.relative_to(ROOT)):sha(p) for p in core},
                reference='independent discrete-event reconstruction from raw episode NPZ and traces; hand-computed TD targets',
                tests=hand_updates(), trace_checks=[], static_fusion=static_fusion())
    locations=list((TASK/'results/rl/double_v2_rngfix').glob('*_validation'))
    locations += [TASK/'results/rl/component_ablation_v1',TASK/'results/rl/fusion_validation_v1/dynamic']
    locations += list((TASK/'results/rl/final_v1').glob('fleet*'))
    locations += [TASK/'results/rl/final_v1/enhancements',TASK/'results/rl/final_montecarlo_v1']
    for dr in sorted(locations):
        if not (dr/'day_metrics.json').is_file():
            continue
        day=json.loads((dr/'day_metrics.json').read_text())
        for tr in sorted(dr.glob('trace_*.json')):
            policy,seed=tr.stem[6:].rsplit('_',1)
            expected=next(r for r in day if r['policy']==policy and r['day_seed']==int(seed))
            ep=dr/f'episode_{seed}.npz'
            obtained,_=replay(ep,tr,expected)
            packet['trace_checks'].append(dict(trace=str(tr.relative_to(ROOT)),trace_sha256=sha(tr),
                episode=str(ep.relative_to(ROOT)),episode_sha256=sha(ep),policy=policy,
                metrics_sha256=sha(dr/'day_metrics.json'),served=obtained['served'],
                empty_km=obtained['empty_km'],revenue=obtained['revenue']))
        print('verified',dr.relative_to(ROOT),'cumulative traces',len(packet['trace_checks']),flush=True)
    packet['scope_exclusions']=['No claim of proving RL optimality or generalization to taxi operations.',
        'Run-time resource measurements are authors actual timings; reference replay verifies physical/metric arithmetic.',
        'Covers listed validation and frozen final/MonteCarlo traces; no unlisted source or artifact is certified.']
    packet['completed_utc']=datetime.now(timezone.utc).isoformat()
    packet['status']='PASS_IN_STATED_SCOPE'
    (OUT/'result.json').write_text(json.dumps(packet,indent=2)+'\n')
    print('independent validation traces',len(packet['trace_checks']),packet['static_fusion'])


if __name__=='__main__':
    main()
