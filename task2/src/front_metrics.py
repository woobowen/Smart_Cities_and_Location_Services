"""Shared numerical reporting front; raw EA selection remains unchanged.

R-001 independent review found KM Spacing included dominated scalar solutions,
and ~1e-13 summation-order duplicates. Round every method to 10 decimal places,
deduplicate, then filter nondominated points before reporting set indicators.
"""
import numpy as np
from evolution import fast_non_dominated_sort, hypervolume, spacing


def canonical_front(F, decimals=10):
    F = np.asarray(F, float)
    if not F.size:
        return F
    points = np.unique(np.round(F, decimals=decimals), axis=0)
    return points[fast_non_dominated_sort(points) == 0]


def evaluate_front(F, ideal, nadir, decimals=10):
    F = np.asarray(F, float)
    front = canonical_front(F, decimals)
    raw_unique = len(np.unique(F, axis=0))
    rounded_unique = len(np.unique(np.round(F, decimals=decimals), axis=0))
    return dict(HV=hypervolume(front, ideal, nadir), Spacing_cv=spacing(front, ideal, nadir),
                front=front.tolist(), raw_count=len(F), raw_unique=raw_unique,
                canonical_unique=rounded_unique, canonical_nondominated=len(front),
                rounding_merged=raw_unique-rounded_unique,
                dominated_removed=rounded_unique-len(front), decimals=decimals)
