"""Teacher-compatible integer NSGA-II/III with explicit matching/HV contracts."""
from __future__ import annotations

import time
import numpy as np
from scipy.optimize import linear_sum_assignment


def make_batch(trip_pool, checkin_pool, hour=18, n_orders=80, n_drivers=40, seed=0):
    """Both trip and driver-hotspot pools must belong to the intended partition."""
    rng = np.random.default_rng(seed)
    pool = trip_pool[trip_pool.minute // 60 == hour]
    hot = checkin_pool[checkin_pool.minute // 60 == hour][['x', 'y']].to_numpy()
    if not len(pool) or not len(hot):
        raise ValueError(f'No trips/checkin hotspots for hour {hour}')
    od = pool.sample(n_orders, replace=len(pool) < n_orders, random_state=seed)
    drv = hot[rng.integers(0, len(hot), n_drivers)] + rng.normal(0, 1., (n_drivers, 2))
    origins = od[['ox', 'oy']].to_numpy()
    return dict(drv=drv, o_xy=origins, d_xy=od[['dx', 'dy']].to_numpy(),
                fare=od.fare.to_numpy(), pickup=np.abs(drv[:, None] - origins).sum(-1),
                trip_indices=od.index.to_numpy())


class EdgeDispatchProblem:
    """Optional matching, objective=(-sum edge value,sum pickup[, -count])."""
    def __init__(self, weights, pickup, feas, K=6, n_obj=2):
        self.weights = np.asarray(weights, float)
        self.pickup = np.asarray(pickup, float)
        self.n_drivers, self.n_var = self.pickup.shape
        if self.weights.shape != self.pickup.shape or np.shape(feas) != self.pickup.shape:
            raise ValueError('weights, pickup and feasibility must have matching shapes')
        self.K = min(self.n_drivers, K if K is not None else self.n_drivers)
        self.n_obj = n_obj
        if n_obj not in (2, 3):
            raise ValueError('Dispatch supports two or three objectives')
        self.cand = np.full((self.n_var, self.K), -1, int)
        for j in range(self.n_var):
            # Stable distance order matches teacher behavior, also supporting irregular graphs.
            ds = np.argsort(self.pickup[:, j], kind='stable')
            ds = ds[np.asarray(feas, bool)[ds, j]][:self.K]
            self.cand[j, :len(ds)] = ds
        self.n_cand = (self.cand >= 0).sum(1)
        self.feas = np.zeros_like(self.pickup, bool)
        for j, row in enumerate(self.cand):
            self.feas[row[row >= 0], j] = True

    def decode(self, gene):
        used, pairs = set(), []
        for j, g in enumerate(gene):
            c = self.n_cand[j]
            if g == 0 or c == 0:
                continue
            for s in range(c):
                d = int(self.cand[j, (int(g) - 1 + s) % c])
                if d not in used:
                    used.add(d)
                    pairs.append((d, j))
                    break
        return pairs

    def encode_pairs(self, pairs):
        gene = np.zeros(self.n_var, int)
        if len({d for d, _ in pairs}) != len(pairs) or len({j for _, j in pairs}) != len(pairs):
            raise ValueError('Matching repeats a driver or request')
        for d, j in pairs:
            loc = np.where(self.cand[j] == d)[0]
            if not len(loc):
                raise ValueError('Matching contains an infeasible candidate edge')
            gene[j] = loc[0] + 1
        if set(self.decode(gene)) != set(map(tuple, pairs)):
            raise AssertionError('Matching-to-gene roundtrip failed')
        return gene

    def evaluate_pairs(self, pairs):
        if not pairs:
            return np.zeros(self.n_obj)
        ds, js = np.asarray(pairs, int).T
        f = [-self.weights[ds, js].sum(), self.pickup[ds, js].sum()]
        if self.n_obj == 3:
            f.append(-len(pairs))
        return np.asarray(f, float)

    def evaluate_one(self, gene):
        return self.evaluate_pairs(self.decode(gene))

    def evaluate(self, pop):
        """Batch decode across chromosomes; request order/rotation is unchanged."""
        pop = np.atleast_2d(np.asarray(pop, int))
        size = len(pop)
        used = np.zeros((size, self.n_drivers), bool)
        F = np.zeros((size, self.n_obj))
        rows = np.arange(size)
        for j, c in enumerate(self.n_cand):
            if not c:
                continue
            pending = pop[:, j] != 0
            for s in range(c):
                ds = self.cand[j, (pop[:, j] - 1 + s) % c]
                take = pending & ~used[rows, ds]
                rr, dd = rows[take], ds[take]
                used[rr, dd] = True
                F[rr, 0] -= self.weights[dd, j]
                F[rr, 1] += self.pickup[dd, j]
                if self.n_obj == 3:
                    F[rr, 2] -= 1
                pending[take] = False
                if not pending.any():
                    break
        return F

    def random_population(self, size, rng):
        pop = rng.integers(0, self.K + 1, (size, self.n_var))
        if size:
            pop[0] = 1
        if size > 1:
            pop[1] = 0
        return pop


class DispatchProblem(EdgeDispatchProblem):
    def __init__(self, batch, K=6, radius=3., n_obj=2):
        self.fare = np.asarray(batch['fare'], float)
        pickup = np.asarray(batch['pickup'], float)
        super().__init__(np.broadcast_to(self.fare, pickup.shape), pickup,
                         pickup <= radius, K=K, n_obj=n_obj)
        self.radius = float(radius)

    def normalization(self):
        optimum = weighted_km(self, [0.])[0]
        revenue_bound = max(-optimum['F'][0], 1.)
        cap = min(self.n_drivers, self.n_var)
        ideal = [-revenue_bound, 0.]
        nadir = [0., max(cap * self.radius, 1.)]
        if self.n_obj == 3:
            ideal.append(-max(cap, 1))
            nadir.append(0.)
        return np.asarray(ideal), np.asarray(nadir)


def fast_non_dominated_sort(F):
    F = np.asarray(F, float)
    n = len(F)
    if not n:
        return np.zeros(0, int)
    dom = (F[:, None] <= F[None]).all(-1) & (F[:, None] < F[None]).any(-1)
    counts = dom.sum(0)
    rank = np.full(n, -1, int)
    current, r = np.where(counts == 0)[0], 0
    while len(current):
        rank[current] = r
        counts -= dom[current].sum(0)
        counts[rank >= 0] = -1
        current = np.where(counts == 0)[0]
        r += 1
    return rank


def unique_front(F):
    F = np.asarray(F, float)
    if not len(F):
        return F
    return np.unique(F[fast_non_dominated_sort(F) == 0], axis=0)


def crowding_distance(F):
    F = np.asarray(F)
    n, m = F.shape
    cd = np.zeros(n)
    if n <= 2:
        return np.full(n, np.inf)
    for k in range(m):
        idx = np.argsort(F[:, k], kind='stable')
        span = F[idx[-1], k] - F[idx[0], k]
        if span > 0:
            cd[idx[0]] = cd[idx[-1]] = np.inf
            cd[idx[1:-1]] += (F[idx[2:], k] - F[idx[:-2], k]) / span
    return cd


def tournament(rank, cd, n, rng):
    a, b = rng.integers(0, len(rank), (2, n))
    first = (rank[a] < rank[b]) | ((rank[a] == rank[b]) & (cd[a] > cd[b]))
    return np.where(first, a, b)


def variation(parents, K, rng, pc=.9, pm=None):
    n, length = parents.shape
    pm = 1. / max(length, 1) if pm is None else pm
    # One additional mate for odd N, then retain exactly N offspring.
    half = (n + 1) // 2
    p1 = parents[:half]
    p2 = parents[np.arange(half, 2 * half) % n]
    mask = (rng.random(p1.shape) < .5) & (rng.random((half, 1)) < pc)
    kids = np.vstack((np.where(mask, p2, p1), np.where(mask, p1, p2)))[:n]
    mutate = rng.random(kids.shape) < pm
    kids[mutate] = rng.integers(0, K + 1, mutate.sum())
    return kids


def nsga2_survival(F, n):
    rank, chosen = fast_non_dominated_sort(F), []
    for r in range(rank.max() + 1):
        front = np.where(rank == r)[0]
        if len(chosen) + len(front) <= n:
            chosen.extend(front)
        else:
            cd = crowding_distance(F[front])
            chosen.extend(front[np.argsort(-cd, kind='stable')[:n-len(chosen)]])
            break
    return np.asarray(chosen, int)


def das_dennis(n_obj, n_partitions):
    def rec(left, depth):
        if depth == n_obj - 1:
            return [[left]]
        return [[i] + rest for i in range(left + 1) for rest in rec(left-i, depth+1)]
    return np.asarray(rec(n_partitions, 0), float) / n_partitions


def normalize(F, ideal):
    translated = F - ideal
    weights = np.eye(F.shape[1]) + 1e-6
    asf = (translated[:, None] / weights[None]).max(-1)
    extreme = translated[asf.argmin(0)]
    try:
        intercept = 1. / np.linalg.solve(extreme, np.ones(F.shape[1]))
        if (intercept <= 1e-6).any() or not np.isfinite(intercept).all():
            raise np.linalg.LinAlgError
    except np.linalg.LinAlgError:
        intercept = translated.max(0)
    intercept = np.where(intercept <= 1e-6, translated.max(0) + 1e-6, intercept)
    return translated / intercept


def associate(Fn, ref_dirs):
    u = ref_dirs / np.linalg.norm(ref_dirs, axis=1, keepdims=True)
    proj = Fn @ u.T
    perp = np.sqrt(np.maximum((Fn**2).sum(1, keepdims=True) - proj**2, 0.))
    niche = perp.argmin(1)
    return niche, perp[np.arange(len(Fn)), niche]


def nsga3_survival(F, n, ref_dirs, rng):
    rank, chosen, last = fast_non_dominated_sort(F), [], None
    for r in range(rank.max() + 1):
        front = np.where(rank == r)[0]
        if len(chosen) + len(front) <= n:
            chosen.extend(front)
            if len(chosen) == n:
                return np.asarray(chosen, int)
        else:
            last = front
            break
    if last is None:
        return np.asarray(chosen, int)
    cand = np.asarray(chosen + list(last), int)
    Fn = normalize(F[cand], F[cand].min(0))
    niche, dist = associate(Fn, ref_dirs)
    k = len(chosen)
    counts = np.bincount(niche[:k], minlength=len(ref_dirs))
    pool = list(range(k, len(cand)))
    excluded = np.zeros(len(ref_dirs), bool)
    while len(chosen) < n:
        remaining_counts = np.where(excluded, np.inf, counts)
        if not np.isfinite(remaining_counts).any():
            raise RuntimeError('NSGA-III niche exhaustion before population filled')
        niche_id = rng.choice(np.where(remaining_counts == remaining_counts.min())[0])
        members = [p for p in pool if niche[p] == niche_id]
        if not members:
            excluded[niche_id] = True
            continue
        pick = members[int(np.argmin(dist[members]))] if counts[niche_id] == 0 else rng.choice(members)
        chosen.append(cand[pick])
        pool.remove(pick)
        counts[niche_id] += 1
    return np.asarray(chosen, int)


def run_nsga(problem, algo='nsga2', pop_size=100, n_gen=300, seed=0,
             ref_dirs=None, log_every=10, initial_genes=None):
    if algo not in ('nsga2', 'nsga3'):
        raise ValueError(algo)
    if algo == 'nsga3' and ref_dirs is None:
        ref_dirs = das_dennis(problem.n_obj, 99 if problem.n_obj == 2 else 13)
    rng = np.random.default_rng(seed)
    start = time.perf_counter()
    pop = problem.random_population(pop_size, rng)
    if initial_genes is not None and len(initial_genes):
        initial_genes = np.asarray(initial_genes, int)
        n_initial = min(len(initial_genes), max(0, pop_size-2))
        pop[2:2+n_initial] = initial_genes[:n_initial]
    F = problem.evaluate(pop)
    history = [dict(generation=0, F=unique_front(F).tolist())]
    for gen in range(1, n_gen+1):
        if algo == 'nsga2':
            rank = fast_non_dominated_sort(F)
            cd = np.zeros(len(F))
            for r in np.unique(rank):
                cd[rank == r] = crowding_distance(F[rank == r])
            parents = pop[tournament(rank, cd, pop_size, rng)]
        else:
            parents = pop[rng.integers(0, pop_size, pop_size)]
        kids = variation(parents, problem.K, rng)
        all_pop, all_F = np.vstack((pop, kids)), np.vstack((F, problem.evaluate(kids)))
        keep = nsga2_survival(all_F, pop_size) if algo == 'nsga2' else nsga3_survival(all_F, pop_size, ref_dirs, rng)
        pop, F = all_pop[keep], all_F[keep]
        if gen % log_every == 0 or gen == n_gen:
            history.append(dict(generation=gen, F=unique_front(F).tolist()))
    is_front = fast_non_dominated_sort(F) == 0
    F, indices = np.unique(F[is_front], axis=0, return_index=True)
    genes = pop[is_front][indices]
    return dict(genes=genes, F=F,
                pairs=[problem.decode(g) for g in genes] if hasattr(problem, 'decode') else None,
                history=history, n_eval=pop_size*(n_gen+1), runtime=time.perf_counter()-start,
                seed=seed, pop_size=pop_size, n_gen=n_gen, algorithm=algo)


def weighted_km(problem, lambdas):
    out = []
    for lam in lambdas:
        W = np.where(problem.feas, problem.weights - lam*problem.pickup, 0.)
        W = np.maximum(W, 0.)
        ds, js = linear_sum_assignment(-W)
        pairs = [(int(d), int(j)) for d, j in zip(ds, js) if W[d, j] > 0]
        out.append(dict(lam=float(lam), pairs=pairs, F=problem.evaluate_pairs(pairs),
                        gene=problem.encode_pairs(pairs)))
    return out


def km_initial_genes(problem, lambdas, max_seeds=10):
    all_genes = np.unique(np.asarray([r['gene'] for r in weighted_km(problem, lambdas)]), axis=0)
    if len(all_genes) <= max_seeds:
        return all_genes
    return all_genes[np.linspace(0, len(all_genes)-1, max_seeds).astype(int)]


def hv2d(F, ref):
    F, ref = np.asarray(F, float), np.asarray(ref, float)
    if not F.size:
        return 0.
    F = F[(F < ref).all(1)]
    hv, best = 0., ref[1]
    for f1, f2 in F[np.argsort(F[:, 0])]:
        if f2 < best:
            hv += (ref[0]-f1)*(best-f2)
            best = f2
    return float(hv)


def hv3d(F, ref):
    F, ref = np.asarray(F, float), np.asarray(ref, float)
    if not F.size:
        return 0.
    F = F[(F < ref).all(1)]
    if not len(F):
        return 0.
    F = F[np.argsort(F[:, 2])]
    return float(sum(hv2d(F[:i+1, :2], ref[:2]) * ((F[i+1, 2] if i+1 < len(F) else ref[2])-F[i, 2])
                     for i in range(len(F))))


def hypervolume(F, ideal, nadir):
    F = np.asarray(F, float)
    if not F.size:
        return 0.
    Fn = (F-np.asarray(ideal)) / np.maximum(np.asarray(nadir)-ideal, 1e-12)
    ref = np.full(F.shape[1], 1.1)
    return hv2d(Fn, ref) if F.shape[1] == 2 else hv3d(Fn, ref)


def spacing(F, ideal, nadir):
    F = np.asarray(F, float)
    Fn = np.unique((F-np.asarray(ideal)) / np.maximum(np.asarray(nadir)-ideal, 1e-12), axis=0)
    if len(Fn) < 2:
        return None
    D = np.abs(Fn[:, None]-Fn[None]).sum(-1)
    np.fill_diagonal(D, np.inf)
    d = D.min(1)
    return float(d.std()/d.mean()) if d.mean() > 0 else None


def knee_point(F):
    F = np.asarray(F, float)
    if not len(F):
        return None
    Fn = (F-F.min(0)) / np.maximum(F.max(0)-F.min(0), 1e-12)
    a, b = Fn[Fn[:, 0].argmin()], Fn[Fn[:, 0].argmax()]
    v, w = b-a, Fn-a
    distance = np.abs(v[0]*w[:, 1]-v[1]*w[:, 0])/(np.linalg.norm(v)+1e-12)
    return int(distance.argmax())


def constraint_choice(F, max_pickup):
    F = np.asarray(F, float)
    cand = np.where(F[:, 1] <= max_pickup)[0]
    return int(cand[F[cand, 0].argmin()]) if len(cand) else None


class DTLZ2:
    """Teacher's integer-discretized DTLZ2, not a replacement continuous task."""
    def __init__(self, n_obj=3, n_var=12, K=200):
        self.n_obj, self.n_var, self.K = n_obj, n_var, K

    def random_population(self, size, rng):
        return rng.integers(0, self.K+1, (size, self.n_var))

    def evaluate(self, pop):
        x, m = pop/self.K, self.n_obj
        g = ((x[:, m-1:]-0.5)**2).sum(1)
        F = np.ones((len(x), m))*(1+g)[:, None]
        for i in range(m):
            F[:, i] *= np.prod(np.cos(x[:, :m-1-i]*np.pi/2), 1)
            if i:
                F[:, i] *= np.sin(x[:, m-1-i]*np.pi/2)
        return F
