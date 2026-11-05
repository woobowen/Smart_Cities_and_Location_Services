"""Teacher single-use online matching, with explicit units and exact offline references."""
from dataclasses import dataclass, asdict
import heapq
import math
import numpy as np
from scipy.optimize import linear_sum_assignment


@dataclass(frozen=True)
class Worker:
    id: int
    loc: tuple[float, float]
    arrival_time: float


@dataclass(frozen=True)
class Request:
    id: int
    loc: tuple[float, float]
    arrival_time: float


@dataclass(frozen=True)
class Assignment:
    worker_id: int
    request_id: int
    assign_time: float
    delay: float
    pickup_distance: float = 0.0
    wait: float = 0.0
    phase: str = "arrival"


def euclidean_distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def _assignment(w, r, time, speed, phase):
    if time + 1e-10 < max(w.arrival_time, r.arrival_time):
        raise ValueError("Dispatch before arrival")
    distance = euclidean_distance(w.loc, r.loc)
    wait = time - r.arrival_time
    return Assignment(w.id, r.id, float(time), wait + distance / speed,
                      distance, wait, phase)


def cost_matrix(workers, requests, speed=1.0, dispatch_time=None):
    """Offline edges dispatch at earliest feasible arrival; batch edges at batch time."""
    if speed <= 0:
        raise ValueError("speed must be positive")
    if not workers or not requests:
        return np.empty((len(workers), len(requests)))
    d = np.linalg.norm(np.asarray([w.loc for w in workers])[:, None, :] -
                       np.asarray([r.loc for r in requests])[None, :, :], axis=2)
    wa = np.asarray([w.arrival_time for w in workers])[:, None]
    ra = np.asarray([r.arrival_time for r in requests])[None, :]
    t = np.maximum(wa, ra) if dispatch_time is None else np.full(d.shape, dispatch_time)
    if np.any(t + 1e-10 < np.maximum(wa, ra)):
        raise ValueError("Cost matrix includes unavailable object")
    return t - ra + d / speed


def bottleneck_assignment(cost):
    """Minimum maximum cost among size min(n,m) matchings; no sum-optimal shortcut."""
    cost = np.asarray(cost, dtype=float)
    if cost.ndim != 2 or not np.all(np.isfinite(cost)):
        raise ValueError("finite 2D cost required")
    if not min(cost.shape):
        return np.array([], dtype=int), np.array([], dtype=int)
    levels = np.unique(cost)
    lo, hi = 0, len(levels) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        i, j = linear_sum_assignment((cost > levels[mid]).astype(int))
        if np.all(cost[i, j] <= levels[mid]):
            hi = mid
        else:
            lo = mid + 1
    i, j = linear_sum_assignment((cost > levels[lo]).astype(int))
    assert np.all(cost[i, j] <= levels[lo])
    return i, j


def offline_reference(workers, requests, speed=1.0, objective="sum"):
    if objective not in ("sum", "max"):
        raise ValueError(objective)
    c = cost_matrix(workers, requests, speed)
    if not min(c.shape):
        return []
    ii, jj = linear_sum_assignment(c) if objective == "sum" else bottleneck_assignment(c)
    return [_assignment(workers[i], requests[j],
                        max(workers[i].arrival_time, requests[j].arrival_time),
                        speed, "offline_" + objective) for i, j in zip(ii, jj)]


class TBGAlgorithm:
    """All teacher TODO 1—5; gamma is a time threshold, distance/speed is travel time."""
    def __init__(self, gamma, speed=1.0):
        if gamma < 0 or speed <= 0:
            raise ValueError("gamma >= 0, speed > 0 required")
        self.gamma, self.speed = float(gamma), float(speed)
        self.available_workers, self.buffered_requests, self.assignments = [], [], []
        self.current_time = 0.0

    def on_request_arrival(self, request):
        self.current_time = request.arrival_time
        candidates = [(euclidean_distance(w.loc, request.loc) / self.speed, w.id, w)
                      for w in self.available_workers]
        if candidates and min(candidates)[0] <= self.gamma:
            _, _, worker = min(candidates)
            self.assignments.append(_assignment(worker, request, self.current_time,
                                                self.speed, "request"))
            self.available_workers.remove(worker)  # TODO 1
        else:
            self.buffered_requests.append(request)  # TODO 2
            self.buffered_requests.sort(key=lambda r: (r.arrival_time, r.id))

    def on_worker_arrival(self, worker):
        self.current_time = worker.arrival_time
        overdue = [r for r in self.buffered_requests
                   if self.current_time - r.arrival_time >= self.gamma]
        if overdue:
            request = overdue[0]  # TODO 3: earliest overdue, no distance cutoff
        else:
            candidates = [(self.current_time - r.arrival_time +
                           euclidean_distance(worker.loc, r.loc) / self.speed, r.id, r)
                          for r in self.buffered_requests]
            request = min(candidates)[2] if candidates and min(candidates)[0] < self.gamma else None
        if request is not None:
            self.assignments.append(_assignment(worker, request, self.current_time,
                                                self.speed, "worker"))
            self.buffered_requests.remove(request)  # TODO 3/4
        else:
            self.available_workers.append(worker)  # TODO 5

    def finalize(self, final_time):
        """Use existing buffers only; maximum cardinality, minimum sum at horizon."""
        if final_time < self.current_time:
            raise ValueError("final_time precedes last arrival")
        c = cost_matrix(self.available_workers, self.buffered_requests, self.speed, final_time)
        if min(c.shape):
            ii, jj = linear_sum_assignment(c)
            for i, j in zip(ii, jj):
                self.assignments.append(_assignment(self.available_workers[i], self.buffered_requests[j],
                                                    final_time, self.speed, "finalize"))
            self.available_workers = [w for i, w in enumerate(self.available_workers) if i not in set(ii)]
            self.buffered_requests = [r for j, r in enumerate(self.buffered_requests) if j not in set(jj)]
        self.current_time = final_time


class BBAlgorithm:
    """Batch KM with explicit teacher-recycling or starter-discard treatment."""
    def __init__(self, theta, speed=1.0, recycle=True, objective="sum"):
        if theta <= 0 or speed <= 0:
            raise ValueError("theta and speed must be positive")
        self.theta, self.speed, self.recycle = float(theta), float(speed), bool(recycle)
        if objective not in ("sum", "max"):
            raise ValueError(objective)
        self.objective = objective
        self.buffered_workers, self.buffered_requests, self.assignments = [], [], []
        self.discarded_workers, self.discarded_requests = [], []
        self.next_batch_time, self.last_batch_time = float(theta), None

    def on_worker_arrival(self, worker):
        self.buffered_workers.append(worker)

    def on_request_arrival(self, request):
        self.buffered_requests.append(request)

    def _process_batch(self, batch_time):
        c = cost_matrix(self.buffered_workers, self.buffered_requests, self.speed, batch_time)
        if min(c.shape):
            ii, jj = linear_sum_assignment(c) if self.objective == "sum" else bottleneck_assignment(c)
        else:
            ii, jj = [], []
        for i, j in zip(ii, jj):
            self.assignments.append(_assignment(self.buffered_workers[i], self.buffered_requests[j],
                                                batch_time, self.speed, "batch"))
        workers = [w for i, w in enumerate(self.buffered_workers) if i not in set(ii)]
        requests = [r for j, r in enumerate(self.buffered_requests) if j not in set(jj)]
        if self.recycle:
            self.buffered_workers, self.buffered_requests = workers, requests
        else:
            self.discarded_workers.extend(workers)
            self.discarded_requests.extend(requests)
            self.buffered_workers, self.buffered_requests = [], []
        self.last_batch_time = batch_time

    def advance_to_time(self, current_time, inclusive=True):
        while self.next_batch_time < current_time or (inclusive and self.next_batch_time <= current_time):
            self._process_batch(self.next_batch_time)
            self.next_batch_time += self.theta

    def finalize(self, final_time):
        self.advance_to_time(final_time)
        if self.last_batch_time != final_time:
            self._process_batch(final_time)


def validate_instance(workers, requests, horizon):
    for objects in (workers, requests):
        if len({o.id for o in objects}) != len(objects):
            raise ValueError("Duplicate identity")
        if any(not np.all(np.isfinite((*o.loc, o.arrival_time))) or
               not 0 <= o.arrival_time <= horizon for o in objects):
            raise ValueError("Invalid coordinate/arrival or arrival outside horizon")


def run_simulation(workers, requests, algorithm, horizon):
    validate_instance(workers, requests, horizon)
    events = [(r.arrival_time, 0, r.id, r) for r in requests] + [
              (w.arrival_time, 1, w.id, w) for w in workers]
    events.sort(key=lambda x: x[:3])
    # Flush a boundary only after *all* arrivals at that timestamp, never between tied events.
    for time in sorted({e[0] for e in events}):
        if isinstance(algorithm, BBAlgorithm):
            algorithm.advance_to_time(time, inclusive=False)
        for _, kind, _, obj in (e for e in events if e[0] == time):
            (algorithm.on_request_arrival if kind == 0 else algorithm.on_worker_arrival)(obj)
        if isinstance(algorithm, BBAlgorithm):
            algorithm.advance_to_time(time)
    algorithm.finalize(horizon)
    assignments = algorithm.assignments
    assert len({a.worker_id for a in assignments}) == len(assignments)
    assert len({a.request_id for a in assignments}) == len(assignments)
    return assignments


def summarize(assignments, n_requests, n_workers):
    delays = [a.delay for a in assignments]
    return {"num_assigned": len(delays), "num_requests": n_requests, "num_workers": n_workers,
            "match_rate": len(delays) / n_requests if n_requests else None,
            "unmatched_requests": n_requests - len(delays),
            "avg_delay": float(np.mean(delays)) if delays else None,
            "max_delay": float(np.max(delays)) if delays else None,
            "p95_delay": float(np.quantile(delays, .95)) if delays else None,
            "total_delay": float(np.sum(delays)) if delays else None,
            "avg_wait": float(np.mean([a.wait for a in assignments])) if delays else None,
            "avg_pickup_distance": float(np.mean([a.pickup_distance for a in assignments])) if delays else None}


def instance_ratios(online, opt_sum, opt_max):
    result = {}
    for objective, reference in (("sum", opt_sum), ("max", opt_max)):
        name = "ratio_" + objective
        if len(online) != len(reference) or not online:
            result[name], result[name + "_status"] = None, "INCOMPARABLE_CARDINALITY_OR_EMPTY"
            continue
        aggregate = sum if objective == "sum" else max
        numerator = aggregate(a.delay for a in online)
        denominator = aggregate(a.delay for a in reference)
        if denominator == 0:
            result[name], result[name + "_status"] = None, "ZERO_REFERENCE_COST"
        else:
            result[name], result[name + "_status"] = numerator / denominator, "INSTANCE_RATIO"
    return result


class SimulationEnvironment:
    """Starter-compatible generator; local RNG and stable heap keys avoid hidden global state."""
    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)
        self.reset()

    def reset(self):
        self.workers, self.requests, self.events, self.assignments = [], [], [], []
        self.next_worker_id = self.next_request_id = 0

    def generate_synthetic_data(self, num_workers, num_requests, time_range=(0, 2000),
                                space_range=(0, 1000), worker_time_dist="uniform",
                                request_time_dist="uniform", loc_dist="uniform"):
        t0, t1 = time_range
        s0, s1 = space_range
        def times(n, dist):
            if dist == "uniform":
                return self.rng.uniform(t0, t1, n)
            if dist == "normal":
                return np.clip(self.rng.normal((t0 + t1)/2, (t1-t0)/6, n), t0, t1)
            if dist == "zipf":
                v = self.rng.zipf(2, n)
                return t0 + (v-v.min()) / (np.ptp(v) or 1) * (t1-t0) if n else np.array([])
            raise ValueError(dist)
        def locations(n):
            if loc_dist == "uniform":
                return self.rng.uniform(s0, s1, (n, 2))
            if loc_dist == "normal":
                return np.clip(self.rng.normal((s0+s1)/2, (s1-s0)/6, (n, 2)), s0, s1)
            raise ValueError(loc_dist)
        for cls, n, distribution, dest, kind in (
                (Worker, num_workers, worker_time_dist, self.workers, 1),
                (Request, num_requests, request_time_dist, self.requests, 0)):
            for time, loc in zip(times(n, distribution), locations(n)):
                obj = cls(len(dest), tuple(loc), float(time))
                dest.append(obj)
                heapq.heappush(self.events, (float(time), kind, obj.id, obj))
        self.next_worker_id, self.next_request_id = len(self.workers), len(self.requests)

    def get_results(self):
        return summarize(self.assignments, len(self.requests), len(self.workers))
