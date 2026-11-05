"""Teacher Q-learning+KM, with explicit simulation and feasible-action contracts.

The simulator preserves the teaching accepted-fare accounting and regional LT
approximation. Extra metrics expose horizon completion and empty travel costs.
"""
from dataclasses import dataclass
import math
import time
import numpy as np
from scipy.optimize import linear_sum_assignment

W_KM = .30 * 111 * math.cos(math.radians(40.74))
H_KM = .28 * 111


@dataclass(frozen=True)
class Config:
    grid: int = 8
    step_min: int = 10
    start: int = 360
    end: int = 1440
    speed: float = 25.
    radius: float = 3.
    patience: int = 2
    orders: int = 1500
    gamma: float = .92
    alpha_min: float = .05
    width: float = W_KM
    height: float = H_KM

    @property
    def T(self):
        return (self.end - self.start) // self.step_min

    @property
    def zones(self):
        return self.grid ** 2

    @property
    def wait(self):
        return self.zones

    @property
    def km_per_step(self):
        return self.speed * self.step_min / 60

    @property
    def centers(self):
        return np.array([((c+.5)*self.width/self.grid, (r+.5)*self.height/self.grid)
                         for r in range(self.grid) for c in range(self.grid)])

    @property
    def delta(self):
        xy = self.centers
        return np.maximum(1, np.ceil(np.abs(xy[:, None]-xy[None]).sum(-1)
                                    / self.km_per_step)).astype(int)


DEFAULT = Config()
T, N_ZONES, WAIT, GAMMA = DEFAULT.T, DEFAULT.zones, DEFAULT.wait, DEFAULT.gamma
DELTA = DEFAULT.delta


def zone_of(x, y, config=DEFAULT):
    col = np.clip((np.asarray(x)/config.width*config.grid).astype(int), 0, config.grid-1)
    row = np.clip((np.asarray(y)/config.height*config.grid).astype(int), 0, config.grid-1)
    return row*config.grid+col


class QTable:
    def __init__(self, config=DEFAULT):
        self.config = config
        shape = (config.T, config.zones, config.zones+1)
        self.Q = np.zeros(shape)
        self.N = np.zeros(shape, dtype=np.int32)
        self.V = np.zeros((config.T+1, config.zones))
        self.NV = np.zeros_like(self.V, dtype=np.int32)


def q_update(qt, t, z, a, r, t2, z2, avail, gamma=None):
    """Teacher TODO1: feasible-action SMDP Q update, return pre-update TD error."""
    cfg = qt.config
    gamma = cfg.gamma if gamma is None else gamma
    if t2 <= t:
        raise ValueError("transition must advance time")
    m = 0.
    if t2 < cfg.T:
        actions = np.append(avail, cfg.wait).astype(int)
        m = float(np.max(qt.Q[t2, z2, actions]))
        qt.NV[t2, z2] += 1
        qt.V[t2, z2] += (m-qt.V[t2, z2])/qt.NV[t2, z2]
    target = r + gamma ** (t2-t) * m
    td = target - qt.Q[t, z, a]
    qt.N[t, z, a] += 1
    qt.Q[t, z, a] += max(1/qt.N[t, z, a], cfg.alpha_min)*td
    return float(td)


class DoubleQTable:
    def __init__(self, config=DEFAULT):
        self.config = config
        shape = (config.T, config.zones, config.zones+1)
        self.A, self.B = np.zeros(shape), np.zeros(shape)
        self.NA, self.NB = np.zeros(shape, np.int32), np.zeros(shape, np.int32)
        self.V = np.zeros((config.T+1, config.zones))
        self.NV = np.zeros_like(self.V, np.int32)


def double_q_update(qt, t, z, a, r, t2, z2, avail, rng=None, update_a=None):
    """Argmax in one estimator, evaluation in the other; no infeasible max."""
    cfg = qt.config
    if t2 <= t:
        raise ValueError("transition must advance time")
    if update_a is None:
        if rng is None:
            raise ValueError("explicit random generator required")
        update_a = rng.random() < .5
    q1, q2, visits = (qt.A, qt.B, qt.NA) if update_a else (qt.B, qt.A, qt.NB)
    m = 0.
    if t2 < cfg.T:
        actions = np.append(avail, cfg.wait).astype(int)
        a1 = actions[np.argmax(q1[t2, z2, actions])]
        a2 = actions[np.argmax(q2[t2, z2, actions])]
        m = float(q2[t2, z2, a1])
        cross = .5*(m+q1[t2, z2, a2])
        qt.NV[t2, z2] += 1
        qt.V[t2, z2] += (cross-qt.V[t2, z2])/qt.NV[t2, z2]
    td = r + cfg.gamma ** (t2-t)*m-q1[t, z, a]
    visits[t, z, a] += 1
    q1[t, z, a] += max(1/visits[t, z, a], cfg.alpha_min)*td
    return float(td)


def region_long_term_value(V, gamma=None, config=DEFAULT):
    """Teacher TODO2, region-center approximation, distinct from actual duration."""
    gamma = config.gamma if gamma is None else gamma
    if V.shape != (config.T+1, config.zones):
        raise ValueError("V shape inconsistent with configuration")
    delta = config.delta
    future = np.minimum(np.arange(config.T)[:, None, None]+delta, config.T)
    destinations = np.arange(config.zones)[None, None, :]
    return gamma ** delta[None]*V[future, destinations]-gamma*V[1:, :, None]


def km_max(W):
    """Maximum positive-edge partial matching; zero dummies permit abstention."""
    W = np.asarray(W, dtype=float)
    if not W.size:
        return []
    if not np.isfinite(W).all():
        raise ValueError("nonfinite matching weight")
    # All rows/columns are otherwise complete zero edges, equivalent to dummies.
    positive = np.maximum(W, 0.)
    r, c = linear_sum_assignment(-positive)
    return [(int(a), int(b)) for a, b in zip(r, c) if positive[a, b] > 0]


def greedy_nearest(ctx):
    used, pairs = set(), []
    for b in range(ctx["pickup"].shape[1]):
        for a in np.argsort(ctx["pickup"][:, b], kind="stable"):
            if ctx["feas"][a, b] and int(a) not in used:
                used.add(int(a))
                pairs.append((int(a), b))
                break
    return pairs


def km_fare(ctx):
    return km_max(np.where(ctx["feas"], ctx["fare"][None], 0.))


def make_q_km(LT, beta=.5):
    """Teacher TODO3: regional long-term edge value plus immediate fare."""
    def q_km(ctx):
        L = LT[ctx["t"]][ctx["drv_zone"][:, None], ctx["dest_zone"][None]]
        W = ctx["fare"][None]+beta*L
        return km_max(np.where(ctx["feas"], W, 0.))
    q_km.LT, q_km.beta = LT, beta
    return q_km


def sample_episode(trip_pool, n_drivers, seed, initial_pool, config=DEFAULT):
    """Explicit train-only initial_pool prevents teacher-global-ck leakage."""
    rng = np.random.default_rng(seed)
    pool = trip_pool[(trip_pool.minute >= config.start) & (trip_pool.minute < config.end)]
    if len(pool) == 0:
        raise ValueError("empty trip pool")
    od = pool.iloc[rng.integers(0, len(pool), config.orders)]
    minute = np.clip(od.minute.to_numpy()+rng.integers(-5, 6, config.orders), config.start, config.end-1)
    jitter = lambda v, hi: np.clip(np.asarray(v)+rng.normal(0, .3, len(v)), 0, hi)
    oxy = np.column_stack([jitter(od.ox, config.width), jitter(od.oy, config.height)])
    dxy = np.column_stack([jitter(od.dx, config.width), jitter(od.dy, config.height)])
    trip_km = np.abs(oxy-dxy).sum(1)
    order = np.argsort(minute, kind="stable")
    orders = dict(step=((minute-config.start)//config.step_min)[order].astype(int),
                  oxy=oxy[order], dxy=dxy[order],
                  dzone=zone_of(dxy[:, 0], dxy[:, 1], config)[order],
                  trip_km=trip_km[order], fare=(5+2*trip_km)[order])
    morning = initial_pool[(initial_pool.minute >= 360) & (initial_pool.minute < 480)][["x", "y"]].to_numpy()
    if len(morning) == 0:
        raise ValueError("empty training morning driver pool")
    drivers = morning[rng.integers(0, len(morning), n_drivers)]+rng.normal(0, .5, (n_drivers, 2))
    drivers = np.clip(drivers, 0, [config.width, config.height])
    return orders, drivers


def make_repositioner(V, config=DEFAULT):
    """4-neighbor move only if discounted arrival V beats staying one step."""
    xy, delta = config.centers, config.delta
    neighbors = []
    for z in range(config.zones):
        r, c = divmod(z, config.grid)
        neighbors.append([rr*config.grid+cc for rr, cc in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
                          if 0 <= rr < config.grid and 0 <= cc < config.grid])
    def reposition(t, position, zone):
        cand = neighbors[int(zone)]
        if not cand:
            return None
        distances = np.abs(xy[cand]-position).sum(1)
        duration = np.maximum(1, np.ceil(distances/config.km_per_step)).astype(int)
        arrival = t+duration
        feasible = arrival < config.T
        score = np.full(len(cand), -np.inf)
        score[feasible] = config.gamma ** duration[feasible]*V[arrival[feasible], np.asarray(cand)[feasible]]
        best = int(np.argmax(score))
        wait_value = config.gamma*V[min(t+1, config.T), int(zone)]
        if score[best] <= wait_value+1e-12:
            return None
        return xy[cand[best]].copy(), int(cand[best]), int(duration[best]), float(distances[best])
    return reposition


def run_episode(episode, policy, collect=False, config=DEFAULT, reposition=None, trace=False):
    """Simulate actual driver occupancy and record explicit terminal categories."""
    start_time = time.perf_counter()
    orders, initial = episode
    pos = initial.copy()
    zone = zone_of(pos[:, 0], pos[:, 1], config)
    target_pos, target_zone = pos.copy(), zone.copy()
    free_at = np.zeros(len(pos), int)
    active = np.zeros(0, int)
    ptr, n_orders = 0, len(orders["step"])
    revenue = pickup_km = completed_revenue = empty_km = empty_steps = 0.
    served = completed = canceled = reposition_count = 0
    trans, pending, assignments, movements, step_metrics = [], {}, [], [], []
    no_avail = np.zeros(0, int)
    nonpositive_edges = feasible_edges = idle_opportunities = 0
    for t in range(config.T):
        released = free_at <= t
        pos[released], zone[released] = target_pos[released], target_zone[released]
        new_end = ptr
        while new_end < n_orders and orders["step"][new_end] == t:
            new_end += 1
        active = np.concatenate((active, np.arange(ptr, new_end)))
        ptr = new_end
        alive = t-orders["step"][active] <= config.patience
        canceled += int(np.sum(~alive))
        active = active[alive]
        idle = np.flatnonzero(released)
        P = np.abs(pos[idle, None]-orders["oxy"][active][None]).sum(-1)
        ctx = dict(t=t, pickup=P, feas=P <= config.radius, fare=orders["fare"][active],
                   drv_zone=zone[idle], dest_zone=orders["dzone"][active])
        pairs = policy(ctx) if len(idle) and len(active) else []
        # Completion transitions see this time's available offers before matching.
        if collect:
            for a, driver in enumerate(idle):
                if int(driver) in pending:
                    pending.pop(int(driver))[6] = np.unique(ctx["dest_zone"][ctx["feas"][a]])
        if len(set(a for a,b in pairs)) != len(pairs) or len(set(b for a,b in pairs)) != len(pairs):
            raise ValueError("policy returned duplicate driver/order")
        feasible_edges += int(ctx["feas"].sum())
        idle_opportunities += len(idle)
        if hasattr(policy, "LT"):
            L = policy.LT[t][zone[idle, None], orders["dzone"][active][None]]
            nonpositive_edges += int(np.sum(ctx["feas"] & (ctx["fare"][None]+policy.beta*L <= 0)))
        busy, done = set(), []
        for a, b in pairs:
            driver, order_id = int(idle[a]), int(active[b])
            if not ctx["feas"][a,b]:
                raise ValueError("policy selected infeasible pickup")
            pickup = float(P[a,b])
            dur = max(1, math.ceil((pickup+orders["trip_km"][order_id])/config.km_per_step))
            fare = float(orders["fare"][order_id])
            if collect:
                tr = [t, int(zone[driver]), int(orders["dzone"][order_id]), fare,
                      t+dur, int(orders["dzone"][order_id]), no_avail]
                trans.append(tr)
                pending[driver] = tr
            revenue += fare
            pickup_km += pickup
            served += 1
            if t+dur <= config.T:
                completed += 1
                completed_revenue += fare
            if trace:
                assignments.append(dict(driver=driver, order=order_id, t=t, release=t+dur,
                                        pickup=pickup, trip=float(orders["trip_km"][order_id]), fare=fare,
                                        origin=pos[driver].tolist(), destination=orders["dxy"][order_id].tolist()))
            target_pos[driver], target_zone[driver] = orders["dxy"][order_id], orders["dzone"][order_id]
            free_at[driver] = t+dur
            busy.add(driver)
            done.append(b)
        for driver in idle:
            driver = int(driver)
            if driver in busy:
                continue
            move = None if reposition is None else reposition(t, pos[driver], zone[driver])
            if move is not None:
                target, target_z, dur, distance = move
                if dur < 1 or distance <= 0 or dur*config.km_per_step+1e-9 < distance:
                    raise ValueError("invalid reposition movement")
                target_pos[driver], target_zone[driver], free_at[driver] = target, target_z, t+dur
                empty_km += distance
                empty_steps += dur
                reposition_count += 1
                if trace:
                    movements.append(dict(driver=driver, t=t, release=t+dur, km=distance,
                                          origin=pos[driver].tolist(), destination=target.tolist()))
            if collect:
                # Reposition training is separate: no reposition used in base training.
                if move is not None:
                    raise ValueError("reposition training transition not defined in teaching Q action set")
                tr = [t, int(zone[driver]), config.wait, 0., t+1, int(zone[driver]), no_avail]
                trans.append(tr)
                pending[driver] = tr
        active = np.delete(active, done)
        if trace:
            step_metrics.append(dict(t=t, available=len(idle), waiting=len(active), accepted=len(pairs),
                                     revenue=revenue, empty_km=empty_km))
    if ptr != n_orders:
        raise ValueError("orders outside simulation horizon or unsorted")
    if served+canceled+len(active) != n_orders:
        raise AssertionError("order conservation failure")
    metrics = dict(revenue=float(revenue), answer_rate=served/n_orders if n_orders else float("nan"),
                   avg_pickup=pickup_km/served if served else float("nan"), pickup_km=pickup_km,
                   served=served, completed=completed, outstanding=served-completed,
                   completed_revenue=completed_revenue, canceled=canceled, horizon_unassigned=len(active),
                   orders=n_orders, empty_km=float(empty_km), empty_minutes=empty_steps*config.step_min,
                   reposition_count=reposition_count, diagnostic_net_revenue=revenue-empty_km,
                   nonpositive_edges=nonpositive_edges, feasible_edges=feasible_edges,
                   nonpositive_fraction=nonpositive_edges/feasible_edges if feasible_edges else float("nan"),
                   idle_opportunities=idle_opportunities, runtime=time.perf_counter()-start_time)
    if trace:
        metrics["trace"] = dict(assignments=assignments, movements=movements, steps=step_metrics,
                                final_free_at=free_at.tolist(), initial=initial.tolist())
    return metrics, trans


def train_q_km(trip_pool, initial_pool, n_drivers, n_episodes=300, beta=.5, seed=2024,
               validation_pool=None, config=DEFAULT, double=False, eval_every=20, verbose=False):
    """Inverse-time replay, train-only transitions, explicit validation pool."""
    qt = DoubleQTable(config) if double else QTable(config)
    rng = np.random.default_rng(seed)
    # Double-estimator update coins must not consume the behavior-policy stream.
    update_rng = np.random.default_rng(seed + 1_000_000)
    validation_pool = trip_pool if validation_pool is None else validation_pool
    val_eps = [sample_episode(validation_pool, n_drivers, 10000+k, initial_pool, config) for k in range(3)]
    curve, td_log, episode_log = [], [], []
    start_time = time.perf_counter()
    for ep in range(n_episodes):
        eps = .5+(.05-.5)*ep/max(1,n_episodes-1)
        q_policy = make_q_km(region_long_term_value(qt.V, config=config), beta)
        def behavior(ctx):
            if rng.random() < eps:
                return km_max(np.where(ctx["feas"], rng.random(ctx["feas"].shape)+.01, 0.))
            return q_policy(ctx)
        metrics, trans = run_episode(sample_episode(trip_pool, n_drivers, seed+ep, initial_pool, config),
                                     behavior, collect=True, config=config)
        errors = []
        for tr in sorted(trans, key=lambda x: -x[0]):
            errors.append(abs(double_q_update(qt,*tr,rng=update_rng) if double else q_update(qt,*tr)))
        td_log.append(float(np.mean(errors)) if errors else float("nan"))
        episode_log.append([ep,metrics["revenue"],metrics["served"],len(trans)])
        if ep % eval_every == 0 or ep == n_episodes-1:
            policy = make_q_km(region_long_term_value(qt.V,config=config), beta)
            vals = [run_episode(e,policy,config=config)[0] for e in val_eps]
            curve.append([ep,np.mean([m["revenue"] for m in vals]),np.mean([m["answer_rate"] for m in vals])])
            if verbose:
                print(f"episode={ep} double={double} fleet={n_drivers} td={td_log[-1]:.3f} val={curve[-1][1]:.3f}",flush=True)
    return qt, np.asarray(curve), np.asarray(td_log), np.asarray(episode_log), time.perf_counter()-start_time
