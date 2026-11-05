"""Aggregate-only diagnosis; no source values or reconstructed rows are saved."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from datetime import datetime, timezone
import csv
import hashlib
import json
import io
from zipfile import ZipFile
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]


def rounded(value, significant, mode):
    return value.quantize(Decimal(1).scaleb(value.adjusted() - significant + 1), rounding=mode)


def main():
    source = ROOT / 'task2/teacher_materials/author_original/dataset_tsmc2014.zip'
    teacher = ROOT / 'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_NYC.csv'
    with ZipFile(source) as archive:
        source_bytes = archive.read('dataset_tsmc2014/dataset_TSMC2014_NYC.txt')
    raw = list(csv.reader(io.StringIO(source_bytes.decode('latin1')), delimiter='\t'))
    with teacher.open(encoding='utf8', newline='') as stream:
        expected = list(csv.reader(stream))[1:]
    assert len(raw) == len(expected) == 227428
    wanted = [[Decimal(row[j]) for j in (4, 5)] for row in expected]
    counts = {}
    for name, first, final in [
            ('decimal_direct_half_even', None, ROUND_HALF_EVEN),
            ('decimal_direct_half_up', None, ROUND_HALF_UP),
            ('decimal15_half_even_then10_half_even', ROUND_HALF_EVEN, ROUND_HALF_EVEN),
            ('decimal15_half_up_then10_half_up', ROUND_HALF_UP, ROUND_HALF_UP),
            ('decimal15_half_even_then10_half_up', ROUND_HALF_EVEN, ROUND_HALF_UP),
            ('decimal15_half_up_then10_half_even', ROUND_HALF_UP, ROUND_HALF_EVEN)]:
        different = [0, 0]
        for row, target in zip(raw, wanted):
            for index, col in enumerate((4, 5)):
                value = Decimal(row[col])
                if first:
                    value = rounded(value, 15, first)
                different[index] += rounded(value, 10, final) != target[index]
        counts[name] = dict(latitude=different[0], longitude=different[1])
    # Pandas' CSV float parser can round the input at a different binary ulp
    # from Python's float(). This is diagnosed, never used to patch the source.
    for mode in ['high', 'legacy', 'round_trip']:
        values = pd.read_csv(io.BytesIO(source_bytes), sep='\t', header=None, encoding='latin1',
                             usecols=[4, 5], float_precision=mode).to_numpy()
        different = [0, 0]
        for row, target in zip(values, wanted):
            for index in range(2):
                different[index] += Decimal(format(float(row[index]), '.10g')) != target[index]
        counts['pandas_' + mode + '_then_python10g'] = dict(latitude=different[0], longitude=different[1])
    output = dict(actual_utc=datetime.now(timezone.utc).isoformat(), city='NYC', rows=len(raw),
                  source_tsv_sha256=hashlib.sha256(source_bytes).hexdigest(),
                  teacher_sha256=hashlib.sha256(teacher.read_bytes()).hexdigest(),
                  differences=counts,
                  scope='All NYC coordinate fields; exact numeric Decimal equality after specified formatting. Other fields not reconverted here. No conversion or algorithm input changed; no per-record values saved.')
    p = ROOT / 'task2/evidence/research_data/author_rounding_diagnostic_aggregate.json'
    p.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
