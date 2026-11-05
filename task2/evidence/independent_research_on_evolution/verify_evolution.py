"""Independent raw-input/matching/indicator audit by /root/research_data.

Expected values use explicit enumeration and coordinate-compressed box unions,
not the execution agent's decoder, rank implementation, or HV routine.
"""
from pathlib import Path
from itertools import combinations
import hashlib
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import evolution as candidate


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def decode(gene, pickup, radius=3., K=6):
    used, out = set(), []
    for j, g in enumerate(gene):
        ds = sorted(range(len(pickup)), key=lambda d: (pickup[d, j], d))[:K]
        ds = [d for d in ds if pickup[d, j] <= radius]
        if not g or not ds:
            continue
        ordered = ds[(g-1) % len(ds):] + ds[:(g-1) % len(ds)]
        for d in ordered:
            if d not in used:
                used.add(d)
                out.append((d, j))
                break
    return out


def box_union(points, ref):
    points, ref = np.asarray(points, float), np.asarray(ref, float)
    points = points[(points < ref).all(axis=1)]
    if not len(points):
        return 0.
    axes = [np.unique(np.r_[points[:, k], ref[k]]) for k in range(len(ref))]
    mask = np.zeros(tuple(len(a)-1 for a in axes), bool)
    for p in points:
        starts = [np.searchsorted(a, p[k]) for k, a in enumerate(axes)]
        mask[tuple(slice(s, None) for s in starts)] = True
    volume = np.ones(mask.shape)
    for k, a in enumerate(axes):
        shape = [1] * len(ref)
        shape[k] = len(a)-1
        volume *= np.diff(a).reshape(shape)
    return float(volume[mask].sum())


def enumerate_matchings(weights, pickup, feas):
    out = []
    def rec(j, used, pairs):
        if j == weights.shape[1]:
            out.append((pairs.copy(), [-sum(weights[d, q] for d, q in pairs), sum(pickup[d, q] for d, q in pairs)]))
            return
        rec(j+1, used, pairs)
        for d in range(weights.shape[0]):
            if d not in used and feas[d, j]:
                rec(j+1, used | {d}, pairs+[(d,j)])
    rec(0, set(), [])
    return out


def check_small():
    rng = np.random.default_rng(98765)
    for n_obj in [2, 3]:
        for _ in range(30):
            F = rng.uniform(-1., 1.5, (8, n_obj))
            ref = np.ones(n_obj)
            expected = box_union(F, ref)
            actual = candidate.hv2d(F, ref) if n_obj == 2 else candidate.hv3d(F, ref)
            assert abs(expected-actual) < 1e-10, (F, expected, actual)
    for case in range(30):
        weights = rng.integers(-5, 20, (3, 4)).astype(float)
        pickup = rng.integers(1, 10, (3, 4)).astype(float)
        feas = rng.random((3, 4)) < .65
        p = candidate.EdgeDispatchProblem(weights, pickup, feas, K=3)
        exact = enumerate_matchings(weights, pickup, feas)
        for result in candidate.weighted_km(p, [0., .1, 1., 3., 10.]):
            expected = max(-F[0]-result['lam']*F[1] for _, F in exact)
            obtained = -result['F'][0]-result['lam']*result['F'][1]
            assert abs(obtained-expected) < 1e-10
            assert set(p.decode(result['gene'])) == set(result['pairs'])
    return {'hv_reference_sets': 60, 'exhaustive_graphs': 30, 'scalar_checks': 150}


def main():
    result = {'reviewer': '/root/research_data', 'scope': 'independent raw replay; author tests not used as oracle',
              'candidate_code_sha256': digest(ROOT / 'src' / 'evolution.py'), 'small_references': check_small(), 'runs': [], 'km': []}
    base = ROOT / 'results' / 'evolution'
    batches = {}
    for file in sorted((base / 'batches').glob('*.npz')):
        b = dict(np.load(file))
        pickup = np.abs(b['drv'][:,None,:]-b['o_xy'][None,:,:]).sum(axis=2)
        assert np.allclose(pickup, b['pickup'], atol=1e-12, rtol=0.)
        fare = 5 + 2*np.abs(b['o_xy']-b['d_xy']).sum(axis=1)
        assert np.allclose(fare, b['fare'], atol=1e-10, rtol=0.)
        batches[file.stem] = b
    for file in sorted((base / 'runs').glob('*.json')):
        r = json.loads(file.read_text())
        F = np.array(r['F'])
        assert r['n_eval'] == r['pop_size'] * (r['n_gen']+1)
        if r['batch_id'] == 'dtlz2_integer_teacher':
            genes = np.array(r['genes'])
            expected_norm = 1+np.sum((genes[:,2:]/200-.5)**2, axis=1)
            assert np.allclose(np.linalg.norm(F,axis=1), expected_norm, atol=1e-10)
            assert abs(np.mean(np.abs(expected_norm-1))-r['front_error']) < 1e-10
        else:
            b = batches[r['batch_id']]
            assert digest(ROOT.parent / r['batch_path']) == r['batch_sha256']
            for g, original_pairs, actual_F in zip(r['genes'], r['pairs'], F):
                pairs = decode(g, b['pickup'])
                assert set(pairs) == set(map(tuple, original_pairs))
                assert len({d for d,j in pairs}) == len(pairs) == len({j for d,j in pairs})
                expected = [-sum(b['fare'][j] for d,j in pairs), sum(b['pickup'][d,j] for d,j in pairs)]
                if r['n_obj'] == 3:
                    expected.append(-len(pairs))
                assert np.allclose(expected, actual_F, atol=1e-9, rtol=0.)
        ideal, nadir = np.array(r['ideal']), np.array(r['nadir'])
        normalized = (F-ideal) / np.maximum(nadir-ideal, 1e-12)
        hv = box_union(normalized, np.full(r['n_obj'], 1.1))
        assert abs(hv-r['HV']) < 1e-9, file
        for h in r['history']:
            points = np.array(h['F'])
            expected = box_union((points-ideal)/np.maximum(nadir-ideal,1e-12),np.full(r['n_obj'],1.1))
            assert abs(expected-h['HV']) < 1e-9
        result['runs'].append({'path': str(file.relative_to(ROOT.parent)), 'sha256':digest(file), 'front_points':len(F), 'raw_HV':hv})
    for file in sorted((base / 'km').glob('*.json')):
        r = json.loads(file.read_text()); b = batches[r['batch_id']]
        for item in r['runs']:
            pairs = list(map(tuple,item['pairs']))
            assert len({d for d,j in pairs})==len(pairs)==len({j for d,j in pairs})
            for d,j in pairs:
                allowed = sorted(range(len(b['pickup'])), key=lambda x:(b['pickup'][x,j], x))[:6]
                assert d in allowed and b['pickup'][d,j] <=3
            expected=[-sum(b['fare'][j] for d,j in pairs),sum(b['pickup'][d,j] for d,j in pairs)]
            if r['n_obj']==3:expected.append(-len(pairs))
            assert np.allclose(expected,item['F'],atol=1e-9,rtol=0.)
        result['km'].append({'path':str(file.relative_to(ROOT.parent)),'sha256':digest(file),'scalar_solves':len(r['runs'])})
    result['status'] = 'PASS_SCOPE_LIMITED'
    result['limits'] = ['Raw execution HV is separately checked; canonical nondominated/precision metrics correction requires its own audit.',
                        'Results appearing after this script reads the directory are outside this receipt.',
                        'Execution traces prove artifact consistency, not original teacher reference numerical claims.']
    destination=Path(__file__).parent/'result.json'
    if destination.exists():
        history=destination.with_name('result_previous_'+digest(destination)[:12]+'.json')
        if not history.exists():history.write_bytes(destination.read_bytes())
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'runs':len(result['runs']),'km_batches':len(result['km']),'small_references':result['small_references']},indent=2))


if __name__ == '__main__':
    main()
