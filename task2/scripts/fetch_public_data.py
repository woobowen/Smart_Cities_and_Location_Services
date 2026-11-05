#!/usr/bin/env python3
"""Fetch the author's public Foursquare source, never redistribute it.

The author TSV and teacher CSV are distinct acquisition sources. The verified
transform uses direct Decimal half-up rounding to10 significant coordinate
digits, UTF-8, CRLF between records and no terminal CRLF. Both city CSVs then
match the audited teacher hashes exactly, while retaining author-reconstructed
provenance. Earlier approximate float conversions remain historical artifacts.
"""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import io
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SOURCE_PAGE='https://sites.google.com/site/yangdingqi/home/foursquare-dataset'
SOURCE_URL='https://drive.google.com/file/d/1VE67jfSN-GV6fkCfuyBEQJzk_qy-SfOk/view?usp=sharing'
DOWNLOAD_URL='https://drive.usercontent.google.com/download?id=1VE67jfSN-GV6fkCfuyBEQJzk_qy-SfOk&export=download&confirm=t'
ZIP_SHA256='cbe3fdab373d24b09b5fc53509c8958c77ff72b6c1a68589ce337d4f9a80235b'
TSV_SHA256={'NYC':'2f39ce698e5bff6683c74bec30c436cc022c160b0f3d73c5268b55491b2445f9',
            'TKY':'85542c605ce708d8584637756590383a84e9bbdb71342d0d8e78858ba2a0e5c8'}
TEACHER_SHA256={'NYC':'60a235386a5324f55c9f24fb1b06e55a38a0d53c0242435d754b38c0cc0b514a',
                'TKY':'849365e52e970c85819b3cc1559bb00bedbe2e37f8e274d77241d62e89ac85f2'}
HEADERS=['userId','venueId','venueCategoryId','venueCategory','latitude','longitude','timezoneOffset','utcTimestamp']
RULE_VERSION='decimal10_half_up_crlf_no_final_eol_v2'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def coordinate_text(text):
    value=Decimal(text)
    value=value.quantize(Decimal(1).scaleb(value.adjusted()-9),rounding=ROUND_HALF_UP)
    fixed=format(value,'f')
    return fixed.rstrip('0').rstrip('.') if '.' in fixed else fixed


def fetch_zip(folder):
    destination=folder/'dataset_tsmc2014.zip'
    downloaded=False
    if not destination.exists():
        temporary=destination.with_suffix('.download')
        request=urllib.request.Request(DOWNLOAD_URL,headers={'User-Agent':'SmartCitiesDispatchResearch/1.0'})
        with urllib.request.urlopen(request,timeout=60) as source, temporary.open('wb') as out:
            copied=0
            while True:
                block=source.read(1024*1024)
                if not block:break
                copied+=len(block)
                if copied>100_000_000:raise RuntimeError('Public archive exceeds bounded 100MB download budget')
                out.write(block)
        if digest(temporary)!=ZIP_SHA256:
            raise RuntimeError('Author archive differs from audited version; temporary download retained for review, no data installed')
        temporary.replace(destination)
        downloaded=True
    if digest(destination)!=ZIP_SHA256:
        raise RuntimeError('Existing source ZIP differs from audited hash; refusing overwrite')
    return destination,downloaded


def convert_city(archive,city,folder,teacher_dir=None):
    member=f'dataset_tsmc2014/dataset_TSMC2014_{city}.txt'
    raw=archive.read(member)
    raw_hash=hashlib.sha256(raw).hexdigest()
    if raw_hash!=TSV_SHA256[city]:raise RuntimeError(f'{city} TSV checksum mismatch')
    target=folder/f'dataset_TSMC2014_{city}.csv'
    temporary=target.with_suffix('.conversion')
    count=0
    with temporary.open('w',encoding='utf-8',newline='') as out:
        writer=csv.writer(out,lineterminator='\r\n')
        writer.writerow(HEADERS)
        for row in csv.reader(io.StringIO(raw.decode('latin-1')),delimiter='\t'):
            if len(row)!=8:raise RuntimeError('Unexpected TSV schema')
            row[4],row[5]=coordinate_text(row[4]),coordinate_text(row[5])
            writer.writerow(row);count+=1
    # This is the audited CSV serialization, not a per-record value patch.
    with temporary.open('r+b') as out:
        out.seek(-2,2)
        if out.read()!=b'\r\n':raise RuntimeError('Unexpected CSV terminal bytes')
        out.truncate(temporary.stat().st_size-2)
    if digest(temporary)!=TEACHER_SHA256[city]:
        raise RuntimeError(f'{city} controlled conversion failed expected teacher-byte hash; temporary copy retained')
    if target.exists() and digest(target)!=digest(temporary):
        raise RuntimeError(f'Existing converted {city} file differs; refusing overwrite')
    if target.exists():temporary.unlink()
    else:temporary.replace(target)
    info={'rows':count,'tsv_sha256':raw_hash,'csv_sha256':digest(target),
          'teacher_expected_sha256':TEACHER_SHA256[city],
          'byte_identity_to_teacher':digest(target)==TEACHER_SHA256[city],
          'conversion':'original Latin1 TSV -> UTF8 CSV; direct Decimal10 significant digits ROUND_HALF_UP; original row order; CRLF between records, no terminal CRLF',
          'rule_version':RULE_VERSION,
          'source_identity':'AUTHOR_RECONSTRUCTED_EXACT_BYTES',
          'identity':'author-public-source reconstructed input; CSV bytes equal audited teacher CSV, acquisition provider remains author reconstruction'}
    if teacher_dir:
        reference=teacher_dir/f'dataset_TSMC2014_{city}.csv'
        if reference.is_file():
            if digest(reference)!=TEACHER_SHA256[city]:raise RuntimeError('Comparison teacher file not the audited input')
            differences={h:0 for h in HEADERS};maximum={'latitude':0.,'longitude':0.}
            with target.open(encoding='utf-8',newline='') as a,reference.open(encoding='utf-8',newline='') as b:
                ra,rb=csv.reader(a),csv.reader(b);next(ra);next(rb)
                compared=0
                from itertools import zip_longest
                for x,y in zip_longest(ra,rb):
                    if x is None or y is None:raise RuntimeError('Row count mismatch')
                    compared+=1
                    for j,h in enumerate(HEADERS):
                        if x[j]!=y[j]:differences[h]+=1
                        if h in maximum:maximum[h]=max(maximum[h],abs(float(x[j])-float(y[j])))
            info['teacher_comparison']={'rows_compared':compared,'field_differences':differences,'max_coordinate_difference_degree':maximum}
    return info,target


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'task2/teacher_materials/author_original/public_conversion_exact')
    ap.add_argument('--compare-teacher-dir',type=Path)
    ap.add_argument('--install-converted-layout',action='store_true',help='Install exact-byte reconstructed inputs only into absent teacher paths, retaining acquisition provenance in a sidecar')
    args=ap.parse_args()
    if args.install_converted_layout:
        for city in ['NYC','TKY']:
            dst=ROOT/f'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_{city}.csv'
            if dst.exists():raise RuntimeError('Teacher-layout input exists; refusing any installation or overwrite.')
    folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=True)
    source,downloaded=fetch_zip(folder)
    receipt={'source_page':SOURCE_PAGE,'source_url':SOURCE_URL,'archive_sha256':digest(source),
             'operation_utc':datetime.now(timezone.utc).isoformat(),
             'source_action':'downloaded_from_public_author_url' if downloaded else 'verified_existing_local_author_zip',
             'redistribution':'NOT_ESTABLISHED; this script fetches from the author into the local workspace only',
             'exact_reproduction':'Both reconstructed city CSVs must match audited teacher hashes. This verifies exact input bytes, not cross-environment bitwise equality of stochastic experiment artifacts.',
             'reconstruction_rule_version':RULE_VERSION,
             'cities':{}}
    with zipfile.ZipFile(source) as z:
        for city in ['NYC','TKY']:
            info,target=convert_city(z,city,folder,args.compare_teacher_dir)
            receipt['cities'][city]=info
            if args.install_converted_layout:
                dst=ROOT/f'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_{city}.csv'
                if dst.exists():raise RuntimeError('Teacher-layout input exists; refusing overwrite. Use --output without installation.')
                dst.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(target,dst)
                provenance={**info,'archive_sha256':digest(source),'source_page':SOURCE_PAGE,
                            'source_url':SOURCE_URL,'acquisition':'author_public_source_reconstruction',
                            'operation_utc':receipt['operation_utc']}
                dst.with_suffix('.provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
        readme=z.read('dataset_tsmc2014/dataset_TSMC2014_readme.txt')
        (folder/'dataset_TSMC2014_readme.txt').write_bytes(readme)
    (folder/'FETCH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
