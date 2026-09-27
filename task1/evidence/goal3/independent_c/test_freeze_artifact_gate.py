"""Independent synthetic artifact-gate challenges; no real held-out data read."""
import hashlib
import json
from pathlib import Path

import pytest

from task1.goal3 import freezes


def fixture_run(tmp_path, monkeypatch):
    ev = tmp_path/'evidence'
    run_dir = ev/'runs'/'synthetic'
    run_dir.mkdir(parents=True)
    (ev/'independent_c').mkdir()
    source = tmp_path/'source.py'
    source.write_text('# synthetic frozen source\n')
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    sources = {'source.py': sha(source)}
    shard = run_dir/'traces.jsonl.gz'
    shard.write_bytes(b'SYNTHETIC_ARTIFACT_GATE_FIXTURE_NOT_TRAJECTORY_DATA')
    manifest = run_dir/'manifest.json'
    manifest.write_text(json.dumps({
        'status': 'MACHINE_VERIFIED_PENDING_C', 'failed_records': [],
        'completed_record_ids': ['synthetic'], 'input_ids': ['synthetic'],
        'bindings': {}, 'source_hashes': sources,
        'shards': [{'path': shard.name, 'sha256': sha(shard)}]}))
    receipt = ev/'independent_c'/'synthetic_receipt.json'
    receipt.write_text(json.dumps({'status': 'VERIFIED', 'source_hashes': sources,
        'targets': [{'path': str(manifest.relative_to(tmp_path)), 'sha256': sha(manifest)}]}))
    monkeypatch.setattr(freezes, 'ROOT', tmp_path)
    monkeypatch.setattr(freezes, 'EV', ev)
    monkeypatch.setattr(freezes, 'source_snapshot', lambda: sources)
    return shard, receipt, manifest, sources


def test_current_actual_artifact_accepted(tmp_path, monkeypatch):
    fixture_run(tmp_path, monkeypatch)
    run, _ = freezes.verified_run('synthetic')
    assert run['completed_record_ids'] == ['synthetic']


def test_changed_shard_cannot_reuse_old_manifest_receipt(tmp_path, monkeypatch):
    shard, _, _, _ = fixture_run(tmp_path, monkeypatch)
    shard.write_bytes(b'CHANGED_SYNTHETIC_ARTIFACT')
    with pytest.raises(ValueError):
        freezes.verified_run('synthetic')


def test_receipt_from_different_source_epoch_rejected(tmp_path, monkeypatch):
    _, receipt, _, _ = fixture_run(tmp_path, monkeypatch)
    value = json.loads(receipt.read_text())
    value['source_hashes'] = {'source.py': '0'*64}
    receipt.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        freezes.verified_run('synthetic')


def test_additional_receipt_target_must_still_exist(tmp_path, monkeypatch):
    _, receipt, _, _ = fixture_run(tmp_path, monkeypatch)
    value = json.loads(receipt.read_text())
    value['targets'].append({'path': 'missing-reviewed-artifact', 'sha256': '0'*64})
    receipt.write_text(json.dumps(value))
    with pytest.raises((ValueError, OSError)):
        freezes.verified_run('synthetic')


def test_processing_epoch_must_match_current_sources(tmp_path, monkeypatch):
    fixture_run(tmp_path, monkeypatch)
    monkeypatch.setattr(freezes, 'source_snapshot', lambda: {'source.py': '1'*64})
    with pytest.raises(ValueError):
        freezes.verified_run('synthetic')
