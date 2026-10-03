"""Teacher-candidate safety gates; actual final ZIP is checked separately."""
import importlib.util
from pathlib import Path
import pytest
from task1.goal3 import package

spec = importlib.util.spec_from_file_location('teacher_submission',
    Path(__file__).resolve().parents[1] / 'submission/build_teacher_submission.py')
teacher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(teacher)


def test_existing_formal_candidate_is_preserved(tmp_path, monkeypatch):
    existing = tmp_path / (teacher.NAME + '.zip')
    existing.write_bytes(b'previous user candidate')
    monkeypatch.setattr(package, 'closure', lambda *a: pytest.fail('must reject before input reads'))
    with pytest.raises(ValueError, match='EXISTING_TEACHER_CANDIDATE_PROTECTED'):
        teacher.build_teacher(delivery=tmp_path)
    assert existing.read_bytes() == b'previous user candidate'


def test_symlink_delivery_rejected(tmp_path, monkeypatch):
    target = tmp_path / 'target'; target.mkdir()
    link = tmp_path / 'delivery'; link.symlink_to(target, target_is_directory=True)
    monkeypatch.setattr(package, 'closure', lambda *a: pytest.fail('must reject before input reads'))
    with pytest.raises(ValueError, match='SYMLINK_DELIVERY_PATH'):
        teacher.build_teacher(delivery=link)
    assert not list(target.iterdir())


def test_frozen_binding_failure_stops_before_staging(tmp_path, monkeypatch):
    monkeypatch.setattr(package, 'closure', lambda *a: (
        {'status': 'NOT_READY', 'missing': [], 'errors': [{'error': 'FROZEN_HASH_MISMATCH'}]}, {}))
    delivery = tmp_path / 'delivery'
    with pytest.raises(ValueError, match='FROZEN_CLOSURE_NOT_READY'):
        teacher.build_teacher(delivery=delivery)
    assert not delivery.exists()


def test_review_only_filename_gate_is_retained(tmp_path):
    with pytest.raises(ValueError, match='REVIEW_ONLY_FILENAME_REQUIRED'):
        package.build(tmp_path / (teacher.NAME + '.zip'), {'status': 'STATIC_CLOSURE_COMPLETE'}, {})
    assert not list(tmp_path.iterdir())


def test_windows_collision_is_not_zipped():
    with pytest.raises(ValueError, match='WINDOWS_PATH_COLLISION'):
        teacher.validate_payload({'README.md': b'readme', 'readme.md': b'collision'})


@pytest.mark.parametrize('path', ['../escape.py', 'font.otf', 'nested.zip'])
def test_unsafe_payload_path_is_not_zipped(path):
    with pytest.raises(ValueError):
        teacher.validate_payload({path: b'bad fixture'})


def test_old_process_hash_cannot_enter_formal_candidate():
    # Real current Experiment bytes; real protected old Process PDF, not a fake header.
    root = teacher.ROOT
    payload = {package.REPORTS[0]: (root / package.REPORTS[0]).read_bytes(),
        package.REPORTS[1]: (root / 'reports/process-report/experiment1-revised/history/accepted-20261002/Process_Report_Revised.pdf').read_bytes()}
    with pytest.raises(ValueError, match='AUTHORIZED_TEACHER_REPORT_HASH_MISMATCH'):
        teacher.validate_payload(payload)
