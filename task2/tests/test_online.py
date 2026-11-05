import itertools
import numpy as np
import pytest
from task2.src.online import (Worker, Request, TBGAlgorithm, BBAlgorithm, SimulationEnvironment,
                             run_simulation, cost_matrix, offline_reference, bottleneck_assignment,
                             summarize, instance_ratios)


def enumerated(cost, objective):
    c = np.asarray(cost)
    if len(c) > c.shape[1]:
        c = c.T
    return min(objective(c[range(len(c)), p]) for p in itertools.permutations(range(c.shape[1]), len(c)))


def test_offline_exact_and_sum_not_bottleneck():
    c = np.array([[0., 6.], [6., 10.]])
    from scipy.optimize import linear_sum_assignment
    i, j = linear_sum_assignment(c)
    bi, bj = bottleneck_assignment(c)
    assert c[i, j].sum() == 10 and c[i, j].max() == 10
    assert c[bi, bj].max() == 6 and c[bi, bj].sum() == 12
    rng = np.random.default_rng(72)
    for n, m in ((2, 3), (4, 3), (4, 4)):
        for _ in range(10):
            c = rng.integers(0, 30, (n, m)).astype(float)
            i, j = bottleneck_assignment(c)
            assert c[i, j].max() == enumerated(c, np.max)
            i, j = linear_sum_assignment(c)
            assert c[i, j].sum() == enumerated(c, np.sum)


def test_event_ties_and_batch_boundary():
    w = [Worker(0, (0, 0), 1), Worker(1, (1, 0), 1)]
    r = [Request(0, (0, 0), 1), Request(1, (1, 0), 1)]
    for method in (TBGAlgorithm(1), BBAlgorithm(1)):
        a = run_simulation(w, r, method, 1)
        assert len(a) == 2 and all(x.delay == 0 for x in a)


def test_tbg_all_branches_finalize_and_units():
    # request matches worker; request buffers; overdue forces long pickup; eligible total delay;
    # worker buffers; finalize uses existing real worker even beyond gamma.
    a = TBGAlgorithm(1, speed=2)
    a.on_worker_arrival(Worker(0, (0, 0), 0))
    a.on_request_arrival(Request(0, (2, 0), 0))
    assert a.assignments[0].delay == 1
    a.on_request_arrival(Request(1, (50, 0), 1))
    a.on_worker_arrival(Worker(1, (0, 0), 2))
    assert a.assignments[-1].request_id == 1 and a.assignments[-1].delay == 26
    a.on_request_arrival(Request(2, (0, 0), 3))
    a.on_worker_arrival(Worker(2, (0, 0), 3.5))
    assert a.assignments[-1].delay == .5
    a.on_worker_arrival(Worker(3, (100, 0), 4))
    a.on_request_arrival(Request(3, (0, 0), 4))
    a.on_request_arrival(Request(4, (0, 0), 4))
    a.finalize(5)
    assert len(a.assignments) == 4 and len(a.buffered_requests) == 1
    assert a.assignments[-1].phase == "finalize" and a.assignments[-1].delay == 51
    a.finalize(5)
    assert len(a.assignments) == 4


def test_discard_masks_unserved_but_recycle_preserves():
    w = [Worker(0, (0, 0), .1)]
    r = [Request(0, (0, 0), 1.1)]
    drop = run_simulation(w, r, BBAlgorithm(1, recycle=False), 2)
    keep = run_simulation(w, r, BBAlgorithm(1, recycle=True), 2)
    assert len(drop) == 0 and len(keep) == 1
    assert summarize(drop, 1, 1)["avg_delay"] is None
    assert instance_ratios(drop, keep, keep)["ratio_max"] is None


def test_cardinality_offline_timing_empty_and_errors():
    w = [Worker(0, (0, 0), 4)]
    r = [Request(0, (3, 4), 1), Request(1, (100, 0), 1)]
    assert cost_matrix(w, r, 1)[0, 0] == 8
    assert offline_reference(w, r)[0].assign_time == 4
    assert run_simulation([], r, TBGAlgorithm(1), 5) == []
    assert offline_reference([], r) == []
    with pytest.raises(ValueError):
        run_simulation(w+w, r, TBGAlgorithm(1), 5)
    with pytest.raises(ValueError):
        run_simulation(w, r, TBGAlgorithm(1), 2)
    z = run_simulation([Worker(0,(0,0),0)], [Request(0,(0,0),0)], TBGAlgorithm(1), 1)
    assert instance_ratios(z, z, z)["ratio_sum_status"] == "ZERO_REFERENCE_COST"


def test_generator_reproducible_and_all_capacity():
    for seed in range(5):
        s = SimulationEnvironment(seed)
        s.generate_synthetic_data(20, 25, (0, 20), (0, 10))
        for method in (TBGAlgorithm(2), BBAlgorithm(2)):
            a = run_simulation(s.workers, s.requests, method, 20)
            assert len(a) == 20
            for x in a:
                w, r = s.workers[x.worker_id], s.requests[x.request_id]
                assert x.assign_time >= max(w.arrival_time, r.arrival_time)
                assert np.isclose(x.delay, x.wait + x.pickup_distance)


def test_batch_bottleneck_same_feasible_cardinality():
    s = SimulationEnvironment(48)
    s.generate_synthetic_data(4, 5, (0, 1), (0, 10))
    c = cost_matrix(s.workers, s.requests, 1, 1)
    a = run_simulation(s.workers, s.requests, BBAlgorithm(1, objective="max"), 1)
    assert len(a) == 4
    assert np.isclose(max(x.delay for x in a), enumerated(c, np.max))
