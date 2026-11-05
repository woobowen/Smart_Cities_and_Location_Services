"""Public-clone and installed-layout provenance regression on temporary copies."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util
import hashlib
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'task2/src'))
import dispatch_data as data


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    original_root = data.ROOT
    original_sources = {city:data.source_path(city) for city in ['NYC','TKY']}
    original_hashes = {city:sha(p) for city,p in original_sources.items()}
    reference = data.load_data()
    conversion = ROOT/'task2/teacher_materials/author_original/public_conversion_exact'
    fetch_receipt = json.loads((conversion/'FETCH_RECEIPT.json').read_text())
    assert all(fetch_receipt['cities'][c]['byte_identity_to_teacher'] for c in ['NYC','TKY'])
    checks = []
    with tempfile.TemporaryDirectory(prefix='smartcities-exact-source-') as tmp:
        clone = Path(tmp)
        author = clone/'task2/teacher_materials/author_original/public_conversion_exact'
        author.mkdir(parents=True)
        for city in ['NYC','TKY']:
            filename=f'dataset_TSMC2014_{city}.csv'
            shutil.copy2(conversion/filename, author/filename)
        shutil.copy2(conversion/'FETCH_RECEIPT.json',author/'FETCH_RECEIPT.json')
        data.ROOT=clone
        rebuilt = data.load_data()
        assert rebuilt.audit['source_identity']=='AUTHOR_RECONSTRUCTED_EXACT_BYTES'
        assert rebuilt.audit['teacher_byte_identity'] is True
        for field in ['checkins','trips','trips_train_inner','trips_validation',
                      'trips_train','trips_test','checkins_train_inner','checkins_train']:
            if not getattr(reference,field).equals(getattr(rebuilt,field)):
                raise AssertionError(field+' not exactly frame-equal')
            checks.append(field+': exact DataFrame equality after public fallback')
        tky=data.audit_source('TKY')
        assert tky['rows']==573703 and tky['source_identity']=='AUTHOR_RECONSTRUCTED_EXACT_BYTES'
        checks.append('TKY source rows/hash and author reconstruction identity')
        partitions={k:len(getattr(rebuilt,k)) for k in ['trips','trips_train_inner','trips_validation','trips_train','trips_test']}
        assert partitions==dict(trips=25550,trips_train_inner=19617,trips_validation=1972,trips_train=21589,trips_test=3961)
        checks.append('all expected proxy and date partition counts')
        # Actual teacher provision still wins when a verified original is present.
        canonical=clone/'task2/teacher_materials/advanced/foursquare'
        canonical.mkdir(parents=True)
        for city in ['NYC','TKY']:
            shutil.copy2(original_sources[city],canonical/original_sources[city].name)
        assert data.source_path('NYC')==canonical/original_sources['NYC'].name
        assert data.audit_source('NYC')['source_identity']=='TEACHER_PROVIDED'
        checks.append('canonical original teacher provision retains priority and identity')
        # Same bytes alone do not establish who provided an arbitrary file.
        arbitrary=clone/'unattributed.csv'
        shutil.copy2(original_sources['NYC'],arbitrary)
        assert data.source_metadata(arbitrary)['source_identity']=='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'
        checks.append('same hash outside known acquisition paths does not invent provider')
    data.ROOT=original_root
    # Exercise the real install command in a distinct empty temporary layout.
    spec=importlib.util.spec_from_file_location('exact_fetch_test',ROOT/'task2/scripts/fetch_public_data.py')
    fetch=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fetch)
    with tempfile.TemporaryDirectory(prefix='smartcities-exact-install-') as tmp:
        clone=Path(tmp)
        author=clone/'task2/teacher_materials/author_original/public_conversion_exact'
        author.mkdir(parents=True)
        shutil.copy2(conversion/'dataset_tsmc2014.zip',author/'dataset_tsmc2014.zip')
        fetch.ROOT=clone
        saved=sys.argv
        sys.argv=['fetch_public_data.py','--install-converted-layout']
        try:
            fetch.main()
        finally:
            sys.argv=saved
        data.ROOT=clone
        for city in ['NYC','TKY']:
            metadata=data.audit_source(city)
            assert metadata['source_identity']=='AUTHOR_RECONSTRUCTED_EXACT_BYTES'
            assert metadata['teacher_byte_identity'] is True
            assert metadata['acquisition_provenance'].endswith('.provenance.json')
        checks.append('real explicit install writes validated sidecars; teacher path does not rewrite provider')
    data.ROOT=original_root
    assert all(sha(p)==original_hashes[c] for c,p in original_sources.items())
    checks.append('original two teacher CSV hashes unchanged')
    receipt=dict(actual_utc=datetime.now(timezone.utc).isoformat(),status='EXACT_INPUT_AND_ACQUISITION_REGRESSION_PASS',
                 checks=checks,partition_rows=partitions,original_teacher_sha256=original_hashes,
                 default_source_identity=reference.audit['source_identity'],
                 fetch_source_action=fetch_receipt['source_action'],
                 fetch_receipt_sha256=sha(conversion/'FETCH_RECEIPT.json'),
                 code_sha256={'src/dispatch_data.py':sha(ROOT/'task2/src/dispatch_data.py'),
                              'scripts/fetch_public_data.py':sha(ROOT/'task2/scripts/fetch_public_data.py')},
                 scope='Read-only original inputs and temporary copies; no current-run CSV regenerated, no model retraining, not a claim of universal bitwise stochastic artifacts')
    (ROOT/'task2/evidence/research_data/source_entry_exact_regression.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
