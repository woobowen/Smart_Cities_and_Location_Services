"""Write a fresh controlled conversion; never rewrite prior conversion history."""
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
import csv
import io
import hashlib
import json
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[3]
HEADERS = ['userId','venueId','venueCategoryId','venueCategory','latitude','longitude','timezoneOffset','utcTimestamp']
TEACHER = {'NYC': '60a235386a5324f55c9f24fb1b06e55a38a0d53c0242435d754b38c0cc0b514a',
           'TKY': '849365e52e970c85819b3cc1559bb00bedbe2e37f8e274d77241d62e89ac85f2'}


def convert_coordinate(text):
    value = Decimal(text)
    value = value.quantize(Decimal(1).scaleb(value.adjusted()-9), rounding=ROUND_HALF_UP)
    result = format(value, 'f')
    return result.rstrip('0').rstrip('.') if '.' in result else result


def main():
    source = ROOT/'task2/teacher_materials/author_original/dataset_tsmc2014.zip'
    archive_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    assert archive_hash == 'cbe3fdab373d24b09b5fc53509c8958c77ff72b6c1a68589ce337d4f9a80235b'
    folder = ROOT/'task2/teacher_materials/author_original/half_up_exact_no_final_eol'
    folder.mkdir(exist_ok=True)
    result = dict(actual_utc=datetime.now(timezone.utc).isoformat(),
                  source_zip_sha256=archive_hash, conversion='Latin1 TSV -> UTF8 CRLF-separated CSV without terminal CRLF; direct Decimal 10 significant digits ROUND_HALF_UP, no preliminary15digit rounding',
                  scope='Fresh controlled copies only; old converted inputs and experiment CSVs untouched', cities={})
    with ZipFile(source) as archive:
        for city in ['NYC','TKY']:
            raw = archive.read(f'dataset_tsmc2014/dataset_TSMC2014_{city}.txt')
            data = io.StringIO(newline='')
            writer = csv.writer(data, lineterminator='\r\n')
            writer.writerow(HEADERS)
            count = 0
            for row in csv.reader(io.StringIO(raw.decode('latin1')), delimiter='\t'):
                row[4],row[5] = convert_coordinate(row[4]),convert_coordinate(row[5])
                writer.writerow(row)
                count += 1
            # Teacher serialization has CRLF between records, no final CRLF.
            output = data.getvalue().removesuffix('\r\n').encode('utf8')
            target = folder/f'dataset_TSMC2014_{city}.csv'
            if target.exists() and target.read_bytes() != output:
                raise ValueError('Controlled target already exists with different bytes')
            if not target.exists():
                target.write_bytes(output)
            digest = hashlib.sha256(output).hexdigest()
            teacher = ROOT/f'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_{city}.csv'
            teacher_hash = hashlib.sha256(teacher.read_bytes()).hexdigest()
            assert teacher_hash == TEACHER[city]
            result['cities'][city] = dict(rows=count, source_tsv_sha256=hashlib.sha256(raw).hexdigest(),
                                          output=str(target.relative_to(ROOT)), csv_sha256=digest,
                                          teacher_sha256=teacher_hash, bytes_equal_to_teacher=output==teacher.read_bytes())
    (ROOT/'task2/evidence/research_data/half_up_conversion_verified.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
