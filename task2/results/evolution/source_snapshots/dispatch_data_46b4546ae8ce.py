"""Teacher Foursquare proxy trips, with explicit chronology and source identity.

The NYC rectangle and local planar model reproduce advanced starter cells 1--3.
These are teaching coordinates, not an independently verified geographic CRS.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LAT_MIN, LAT_MAX = 40.60, 40.88
LON_MIN, LON_MAX = -74.05, -73.75
KM_PER_LAT = 111.0
KM_PER_LON = 111.0 * math.cos(math.radians(40.74))
W_KM = (LON_MAX - LON_MIN) * KM_PER_LON
H_KM = (LAT_MAX - LAT_MIN) * KM_PER_LAT
BASE_FARE, PER_KM, PICKUP_RADIUS = 5.0, 2.0, 3.0


def source_path(city='NYC'):
    city = city.upper()
    if city not in {'NYC', 'TKY'}:
        raise ValueError('Expected city NYC or TKY')
    p = ROOT / 'task2' / 'teacher_materials' / 'advanced' / 'foursquare' / f'dataset_TSMC2014_{city}.csv'
    if not p.is_file():
        raise FileNotFoundError(f'{p.relative_to(ROOT)}; run scripts/inspect_teacher_materials.py using the teacher archives')
    return p


def to_xy(lat, lon):
    return (lon - LON_MIN) * KM_PER_LON, (lat - LAT_MIN) * KM_PER_LAT


def load_checkins(path=None, city='NYC'):
    """NYC teacher rectangle; both cities remain available for source-level audit."""
    if city.upper() != 'NYC':
        raise ValueError('Only NYC has a teacher-approved simulation rectangle; use audit_source("TKY") for Tokyo source statistics')
    path = source_path(city) if path is None else Path(path)
    df = pd.read_csv(path, encoding='latin-1')
    df['source_row'] = np.arange(2, len(df) + 2)
    utc = pd.to_datetime(df['utcTimestamp'], format='%a %b %d %H:%M:%S +0000 %Y', utc=True, errors='raise')
    df['utc'] = utc
    # Offset belongs to each observation. Local is a civil-clock value, not UTC.
    df['local'] = utc.dt.tz_localize(None) + pd.to_timedelta(df['timezoneOffset'], unit='m')
    inside = df.latitude.between(LAT_MIN, LAT_MAX) & df.longitude.between(LON_MIN, LON_MAX)
    df = df.loc[inside].copy()
    df['x'], df['y'] = to_xy(df.latitude.to_numpy(), df.longitude.to_numpy())
    df['minute'] = df['local'].dt.hour * 60 + df['local'].dt.minute
    df['date'] = df['local'].dt.date
    return df.sort_values(['userId', 'local', 'source_row'], kind='stable').reset_index(drop=True)


def build_trips(ck, min_gap=10, max_gap=180, min_km=1.0):
    """Consecutive in-rectangle check-ins, following teacher cell 3 exactly.

    Filtering precedes pairing in the starter: a pair can skip an outside-rectangle
    observation. This is a documented proxy limitation, never a taxi trajectory.
    """
    ck = ck.sort_values(['userId', 'local', 'source_row'], kind='stable').reset_index(drop=True)
    fields = ['x', 'y', 'local', 'minute', 'source_row']
    prev = ck.groupby('userId', sort=False)[fields].shift()
    gap = (ck['local'] - prev['local']).dt.total_seconds() / 60
    km = (ck['x'] - prev['x']).abs() + (ck['y'] - prev['y']).abs()
    ok = (ck['local'].dt.date == prev['local'].dt.date) & gap.between(min_gap, max_gap) & (km >= min_km)
    trips = pd.DataFrame({
        'date': prev.loc[ok, 'local'].dt.date.to_numpy(),
        'minute': prev.loc[ok, 'minute'].to_numpy(dtype=int),
        'ox': prev.loc[ok, 'x'].to_numpy(), 'oy': prev.loc[ok, 'y'].to_numpy(),
        'dx': ck.loc[ok, 'x'].to_numpy(), 'dy': ck.loc[ok, 'y'].to_numpy(),
        'gap_min': gap.loc[ok].to_numpy(),
        'origin_source_row': prev.loc[ok, 'source_row'].to_numpy(dtype=int),
        'destination_source_row': ck.loc[ok, 'source_row'].to_numpy(dtype=int),
    })
    trips['trip_km'] = (trips.ox - trips.dx).abs() + (trips.oy - trips.dy).abs()
    trips['fare'] = BASE_FARE + PER_KM * trips['trip_km']
    return trips.sort_values(['date', 'minute', 'origin_source_row'], kind='stable').reset_index(drop=True)


def temporal_split(trips, validation_fraction=.2):
    dates = np.sort(trips['date'].unique())
    if len(dates) < 5 or not 0 < validation_fraction < 1:
        raise ValueError('At least five dates and validation_fraction in (0,1) required')
    n_train = int(len(dates) * .7)
    n_inner = int(n_train * (1 - validation_fraction))
    if not 0 < n_inner < n_train < len(dates):
        raise ValueError('Empty chronological partition')
    val_start, test_start = dates[n_inner], dates[n_train]
    return {
        'trips_train_inner': trips[trips.date < val_start].reset_index(drop=True),
        'trips_validation': trips[(trips.date >= val_start) & (trips.date < test_start)].reset_index(drop=True),
        'trips_train': trips[trips.date < test_start].reset_index(drop=True),
        'trips_test': trips[trips.date >= test_start].reset_index(drop=True),
        'validation_start': val_start,
        'test_start': test_start,
    }


def audit_source(city='NYC'):
    p = source_path(city)
    df = pd.read_csv(p, encoding='latin-1')
    utc = pd.to_datetime(df['utcTimestamp'], format='%a %b %d %H:%M:%S +0000 %Y', utc=True)
    local = utc.dt.tz_localize(None) + pd.to_timedelta(df['timezoneOffset'], unit='m')
    return {
        'city': city, 'path': str(p.relative_to(ROOT)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        'rows': len(df), 'columns': list(df.columns), 'missing_by_column': df.isna().sum().to_dict(),
        'exact_duplicate_rows': int(df.duplicated().sum()), 'users': int(df.userId.nunique()), 'venues': int(df.venueId.nunique()),
        'latitude_range': [float(df.latitude.min()), float(df.latitude.max())],
        'longitude_range': [float(df.longitude.min()), float(df.longitude.max())],
        'offset_minutes': sorted(int(x) for x in df.timezoneOffset.unique()),
        'utc_start': utc.min().isoformat(), 'utc_end': utc.max().isoformat(),
        'local_start': local.min().isoformat(), 'local_end': local.max().isoformat(),
        'source_crs': 'UNVERIFIED', 'time_semantics': 'per-record UTC plus timezoneOffset in minutes; local civil clock',
        'identity': 'teacher-provided check-ins, not ride-hailing orders',
    }


@dataclass
class DataBundle:
    checkins: pd.DataFrame
    trips: pd.DataFrame
    trips_train_inner: pd.DataFrame
    trips_validation: pd.DataFrame
    trips_train: pd.DataFrame
    trips_test: pd.DataFrame
    checkins_train_inner: pd.DataFrame
    checkins_train: pd.DataFrame
    audit: dict


def load_data(city='NYC', validation_fraction=.2):
    ck = load_checkins(city=city)
    trips = build_trips(ck)
    s = temporal_split(trips, validation_fraction)
    inner = ck[ck.date < s['validation_start']].reset_index(drop=True)
    train = ck[ck.date < s['test_start']].reset_index(drop=True)
    audit = audit_source(city)
    audit.update({
        'in_rectangle_checkins': len(ck), 'proxy_trips': len(trips),
        'model': 'teacher NYC rectangle, x=(lon+74.05)*111*cos(40.74deg), y=(lat-40.60)*111; Manhattan km',
        'proxy_criteria': {'same_local_day': True, 'gap_min_inclusive': [10, 180], 'Manhattan_km_min': 1.0, 'pairing': 'adjacent after NYC rectangle filtering, matching teacher starter'},
        'split': {k: {'rows': len(s[k]), 'dates': int(s[k].date.nunique()), 'start': str(s[k].date.min()), 'end': str(s[k].date.max())} for k in ['trips_train_inner', 'trips_validation', 'trips_train', 'trips_test']},
        'validation_start': str(s['validation_start']), 'test_start': str(s['test_start']),
        'initialization': 'development drivers use checkins_train_inner only; final drivers use checkins_train only',
        'selection_rule': 'test dates excluded from candidate selection and hyperparameter tuning',
        'dataset_page_date_discrepancy': 'author webpage says from 12 April 2012; teacher CSV includes 3 April 2012, retained as actually supplied',
    })
    return DataBundle(ck, trips, s['trips_train_inner'], s['trips_validation'], s['trips_train'], s['trips_test'], inner, train, audit)


def main():
    out = ROOT / 'task2' / 'results' / 'data'
    out.mkdir(parents=True, exist_ok=True)
    b = load_data()
    for name in ['trips', 'trips_train_inner', 'trips_validation', 'trips_train', 'trips_test', 'checkins_train_inner', 'checkins_train']:
        getattr(b, name).to_csv(out / (name + '.csv'), index=False)
    audit = {'NYC': b.audit, 'TKY': audit_source('TKY')}
    path = ROOT / 'task2' / 'evidence' / 'research_data' / 'data_audit.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
    print(json.dumps(audit, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
