"""Mathematical checks using explicit enumeration and box inclusion/exclusion."""
import itertools
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from evolution import (DispatchProblem, EdgeDispatchProblem, DTLZ2, weighted_km,
    fast_non_dominated_sort, crowding_distance, variation, das_dennis, normalize,
    hv2d, hv3d, hypervolume, spacing, run_nsga, km_initial_genes)


def tiny_problem(n_obj=2):
    return DispatchProblem({'fare': np.array([9., 12., 7.]),
                            'pickup': np.array([[.5, 2., 4.], [2., .8, 1.]])},
                           K=2, radius=3, n_obj=n_obj)


def enumerated_matchings(problem):
    out = []
    for assignment in itertools.product(range(-1, problem.n_drivers), repeat=problem.n_var):
        ds = [d for d in assignment if d >= 0]
        if len(ds) != len(set(ds)):
            continue
        pairs = [(d, j) for j, d in enumerate(assignment) if d >= 0]
        if all(problem.feas[d, j] for d, j in pairs):
            out.append(pairs)
    return out


def union_volume(points, ref):
    # Independent inclusion/exclusion of axis-aligned boxes (small sets only).
    points = np.asarray(points)
    points = points[(points < ref).all(1)]
    ans = 0.
    for size in range(1, len(points)+1):
        for chosen in itertools.combinations(points, size):
            lo = np.max(chosen, axis=0)
            ans += (-1)**(size+1)*np.maximum(np.asarray(ref)-lo, 0).prod()
    return ans


def test_decode_batched_matches_scalar_exhaustive():
    for n_obj in [2, 3]:
        p = tiny_problem(n_obj)
        pop = np.array(list(itertools.product(range(3), repeat=3)))
        np.testing.assert_allclose(p.evaluate(pop), [p.evaluate_one(g) for g in pop])
        for g in pop:
            pairs = p.decode(g)
            assert len({d for d, _ in pairs}) == len(pairs)
            assert len({j for _, j in pairs}) == len(pairs)
            assert all(p.feas[d, j] for d, j in pairs)


def test_matching_encoder_covers_feasible_graph():
    p = tiny_problem()
    for pairs in enumerated_matchings(p):
        gene = p.encode_pairs(pairs)
        assert set(p.decode(gene)) == set(pairs)


def test_weighted_km_equals_independent_exhaustive():
    p = tiny_problem()
    all_F = np.array([p.evaluate_pairs(x) for x in enumerated_matchings(p)])
    lambdas = [0., .5, 3., 20.]
    for lam, result in zip(lambdas, weighted_km(p, lambdas)):
        expected = (-all_F[:, 0]-lam*all_F[:, 1]).max()
        assert abs(-result['F'][0]-lam*result['F'][1]-expected) < 1e-10
        np.testing.assert_allclose(p.evaluate_one(result['gene']), result['F'])
    genes = km_initial_genes(p, lambdas)
    assert len(genes) >= 2


def test_hv_2d_3d_known_answers_and_pymoo():
    from pymoo.indicators.hv import HV
    for dim in [2, 3]:
        rng = np.random.default_rng(88)
        for _ in range(10):
            F, ref = rng.uniform(-.2, 1.3, (5, dim)), np.full(dim, 1.1)
            actual = hv2d(F, ref) if dim == 2 else hv3d(F, ref)
            assert abs(actual-union_volume(F, ref)) < 1e-10
            assert abs(actual-HV(ref_point=ref)(F)) < 1e-10
    assert abs(hv2d([[.2, .8], [.8, .2]], [1, 1])-.28) < 1e-12
    assert hv3d([[0, 0, 0]], [1, 2, 3]) == 6.


def test_nondominance_and_degenerate_spacing():
    F = np.array([[0, 2], [1, 1], [2, 0], [2, 2], [1, 1], [3, 3.]])
    assert fast_non_dominated_sort(F).tolist() == [0, 0, 0, 1, 0, 2]
    assert spacing([[0, 0]], [0, 0], [1, 1]) is None
    assert spacing([[0, 0], [0, 0]], [0, 0], [1, 1]) is None
    assert spacing([[0, 1], [1, 0]], [0, 0], [1, 1]) == 0.
    assert np.isfinite(crowding_distance(np.zeros((4, 2)))).all()


def test_odd_population_and_reference_counts():
    rng = np.random.default_rng(12)
    assert variation(rng.integers(0, 6, (105, 80)), 6, rng).shape == (105, 80)
    assert len(das_dennis(3, 13)) == 105
    assert len(das_dennis(2, 99)) == 100
    assert np.isfinite(normalize(np.zeros((4, 3)), np.zeros(3))).all()
    for algo in ['nsga2', 'nsga3']:
        p = tiny_problem(3)
        r = run_nsga(p, algo=algo, pop_size=11, n_gen=4, seed=3)
        assert r['n_eval'] == 55
        assert np.isfinite(r['F']).all()
        assert (fast_non_dominated_sort(r['F']) == 0).all()


def test_dtlz_known_front_and_pymoo_definition():
    from pymoo.problems import get_problem
    p = DTLZ2()
    pop = np.random.default_rng(4).integers(0, 201, (8, 12))
    expected = get_problem('dtlz2', n_var=12, n_obj=3).evaluate(pop/200.)
    np.testing.assert_allclose(p.evaluate(pop), expected)
    pop[:, 2:] = 100
    np.testing.assert_allclose(np.linalg.norm(p.evaluate(pop), axis=1), 1.)


def test_infeasible_and_zero_matching_have_explicit_endpoints():
    p = EdgeDispatchProblem(np.ones((2, 3)), np.ones((2, 3)), np.zeros((2, 3), bool))
    assert p.decode([1, 1, 1]) == []
    np.testing.assert_array_equal(p.evaluate([[1, 1, 1]]), [[0, 0]])
    assert hypervolume([[0, 0]], [-1, 0], [0, 6]) > 0


def test_unsupported_pareto_point_is_not_a_km_implementation_bug():
    p = DispatchProblem({'fare': np.array([3., 6., 9.]),
                         'pickup': np.array([[1., 3., 4.]])}, K=1, radius=5.)
    # (revenue6,pickup3) is nondominated, but beating the revenue3 alternative
    # requires lambda<=1.5 and beating the revenue9 alternative requires lambda>=3.
    F = np.array([[0., 0.], [-3., 1.], [-6., 3.], [-9., 4.]])
    assert (fast_non_dominated_sort(F) == 0).all()
    solved = weighted_km(p, np.r_[0., np.geomspace(.001, 1000, 1000)])
    assert not any(np.array_equal(r['F'], [-6., 3.]) for r in solved)


def test_reporting_metric_removes_dominated_and_numerical_duplicates():
    from front_metrics import canonical_front, evaluate_front
    F = np.array([[-5., 1.], [-5.+1e-13, 1.+1e-13], [-5., 2.], [0., 0.]])
    np.testing.assert_allclose(canonical_front(F), [[-5., 1.], [0., 0.]])
    m = evaluate_front(F, [-10, 0], [0, 10])
    assert m['rounding_merged'] == 1 and m['dominated_removed'] == 1
    assert m['canonical_nondominated'] == 2 and m['Spacing_cv'] == 0.
