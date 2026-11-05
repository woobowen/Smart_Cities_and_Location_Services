"""Independent isolated exact reconstruction, acquisition identity and dataframe checks."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,subprocess,sys,tempfile,time
import pandas as pd
ROOT=Path(__file__).resolve().parents[3];TASK=ROOT/'task2';OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
source=TASK/'src/dispatch_data.py';fetcher=TASK/'scripts/fetch_public_data.py';archive=TASK/'teacher_materials/author_original/dataset_tsmc2014.zip'
original=module('pkg_original_data',source);checks=[];started=time.perf_counter()
with tempfile.TemporaryDirectory(prefix='dispatch_exact_public_') as folder:
 d=Path(folder);ds=d/'task2/src/dispatch_data.py';ds.parent.mkdir(parents=True);shutil.copyfile(source,ds)
 fs=d/'task2/scripts/fetch_public_data.py';fs.parent.mkdir(parents=True);shutil.copyfile(fetcher,fs)
 output=d/'task2/teacher_materials/author_original/public_conversion_exact';output.mkdir(parents=True);shutil.copyfile(archive,output/'dataset_tsmc2014.zip')
 p=subprocess.run([str(ROOT/'.venv/bin/python'),str(fs)],cwd=d,capture_output=True,text=True,check=True)
 receipt=json.loads(p.stdout);assert receipt['source_action']=='verified_existing_local_author_zip'
 (OUT/'exact_public_converter_stdout.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2))
 isolated=module('pkg_isolated_data',ds)
 for city in ['NYC','TKY']:
  file=output/f'dataset_TSMC2014_{city}.csv';teacher=TASK/f'teacher_materials/advanced/foursquare/dataset_TSMC2014_{city}.csv'
  assert sha(file)==sha(teacher)==isolated.TEACHER_SHA256[city]
  m=isolated.source_metadata(file,city);assert m['source_identity']=='AUTHOR_RECONSTRUCTED_EXACT_BYTES' and m['teacher_byte_identity']
  checks.append(dict(case='actual_converter_byte_identity_and_provider',city=city,csv_sha256=sha(file),provider=m['source_identity'],rowcount=receipt['cities'][city]['rows']))
 assert not (d/'task2/teacher_materials/advanced').exists()
 a=original.load_data();b=isolated.load_data();frames={}
 for key in ['checkins','trips','trips_train_inner','trips_validation','trips_train','trips_test','checkins_train_inner','checkins_train']:
  pd.testing.assert_frame_equal(getattr(a,key),getattr(b,key),check_exact=True);frames[key]=dict(rows=len(getattr(a,key)),exact=True)
 checks.append(dict(case='exact_dataframe_replay_no_teacher_files',frames=frames,provider=b.audit['source_identity']))
 rp=output/'FETCH_RECEIPT.json';valid_receipt=rp.read_bytes();rp.unlink()
 assert isolated.source_metadata(output/'dataset_TSMC2014_NYC.csv')['source_identity']=='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'
 checks.append(dict(case='missing_receipt_in_author_directory',provider='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'))
 bad=json.loads(valid_receipt);bad['cities']['NYC']['csv_sha256']='0'*64;rp.write_text(json.dumps(bad))
 assert isolated.source_metadata(output/'dataset_TSMC2014_NYC.csv')['source_identity']=='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'
 checks.append(dict(case='corrupt_receipt_in_author_directory',provider='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'))
 rp.write_bytes(valid_receipt)
 unknown=d/'unknown.csv';shutil.copyfile(output/'dataset_TSMC2014_NYC.csv',unknown)
 assert isolated.source_metadata(unknown)['source_identity']=='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'
 checks.append(dict(case='same_known_bytes_unknown_acquisition_path',provider='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'))
 p2=subprocess.run([str(ROOT/'.venv/bin/python'),str(fs),'--install-converted-layout'],cwd=d,capture_output=True,text=True,check=True)
 canonical=d/'task2/teacher_materials/advanced/foursquare/dataset_TSMC2014_NYC.csv'
 assert isolated.source_path()==canonical and isolated.source_metadata(canonical)['source_identity']=='AUTHOR_RECONSTRUCTED_EXACT_BYTES'
 sidecar=canonical.with_suffix('.provenance.json');before=sidecar.read_bytes();bad=json.loads(before);bad['archive_sha256']='0'*64;sidecar.write_text(json.dumps(bad))
 assert isolated.source_metadata(canonical)['source_identity']=='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'
 checks.append(dict(case='explicit_install_sidecar_and_corrupt_sidecar',correct_sidecar_provider='AUTHOR_RECONSTRUCTED_EXACT_BYTES',corrupt_sidecar_provider='TEACHER_EQUIVALENT_BYTES_PROVIDER_UNVERIFIED'))
 # Copy the actual teacher-provided source into thisowned test fixture, withoutauthor-sidecar.
 sidecar.unlink();shutil.copyfile(TASK/'teacher_materials/advanced/foursquare/dataset_TSMC2014_NYC.csv',canonical)
 assert isolated.source_path()==canonical and isolated.source_metadata(canonical)['source_identity']=='TEACHER_PROVIDED'
 checks.append(dict(case='actual_teacher_fixture_priority',provider='TEACHER_PROVIDED'))
report=dict(reviewer='/root/reinforcement, independent ofdata-fetch/metadataauthor',source_sha256=sha(source),fetcher_sha256=sha(fetcher),cached_author_archive_sha256=sha(archive),network_redownload_by_this_reviewer=False,scope='Actualconversionfromverifiedcachedpublicarchive; bothcityexactbytes,8dataframes, provenance/entryguards. Freshnetworkdownloadclaimedonlybyauthorsseparatelivefetchreceipt, notthisreview.',checks=checks,seconds=time.perf_counter()-started,status='PASS_IN_STATED_SCOPE')
(OUT/'exact_public_data_review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('PASS',len(checks),'cases,8exactdataframes,bothcitybyteidentity')
