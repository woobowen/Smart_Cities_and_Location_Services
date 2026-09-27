"""Package-engineering checks; synthetic ZIP fixtures are temporary, not deliverables."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from task1.goal3.package import (ROOT, G2, build, closure, content_issues, json_bytes,
                                relative_path, sha, verify_directory)


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.payload = closure()

    def test_current_real_closure_has_no_unsafe_or_changed_binding(self):
        self.assertEqual(self.report['errors'], [])
        self.assertTrue(self.report['members'])
        raw = 'task1/作业/作业/traj_dict.json'
        self.assertEqual(sha(self.payload[raw]), 'c59be4c079d2ffd8ae0127c8a361c77ba277252abb2c7202efb9ee4e8e6084d3')

    def test_all_processing_snapshot_sources_are_present(self):
        from task1.workflow.g2_journal import source_snapshot
        for path, expected in source_snapshot().items():
            self.assertEqual(sha(self.payload[path]), expected)

    def test_only_named_metadata_command_is_normalized(self):
        path = G2+'result_summary.json'
        before = json.loads((ROOT/path).read_bytes())
        after = json.loads(self.payload[path])
        provenance = after.pop('_package_provenance')
        self.assertFalse(provenance['numeric_results_and_proposals_changed'])
        self.assertEqual(provenance['source_sha256'], sha((ROOT/path).read_bytes()))
        self.assertEqual(after['actual_command'][0], 'task1/scripts/build_goal2_analysis.py')
        after['actual_command'][0] = before['actual_command'][0]
        self.assertEqual(before, after)

    def test_unsafe_and_forbidden_paths_rejected(self):
        for path in ('../escape', '/absolute', 'x/../escape', 'x//file', 'C:/file',
                     'x\\file', '.git/config', '.venv/bin/python', 'x/font.ttf', 'unrelated.zip'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                relative_path(path)

    def test_secret_and_personal_path_scanner(self):
        self.assertIn('POSSIBLE_SECRET', content_issues('fixture.txt', ('ghp_'+'A'*36).encode()))
        self.assertIn('PERSONAL_ABSOLUTE_PATH', content_issues('fixture.txt', ('/'+ 'home/example/private').encode()))
        self.assertEqual(content_issues('fixture.txt', b'task1/config/goal2/contract.json'), [])

    def test_not_ready_build_refused(self):
        with tempfile.TemporaryDirectory(prefix='g3-package-test-') as folder:
            target = Path(folder)/'REVIEW_ONLY_ENGINEERING_FIXTURE.zip'
            with self.assertRaisesRegex(ValueError, 'PACKAGE_INPUTS_NOT_READY'):
                build(target, {'status': 'NOT_READY'}, {})
            self.assertFalse(target.exists())

    def test_real_zip_hash_tamper_and_overwrite_checks(self):
        with tempfile.TemporaryDirectory(prefix='g3-package-test-') as folder:
            folder = Path(folder); target = folder/'REVIEW_ONLY_ENGINEERING_FIXTURE.zip'
            payload = {'fixture.txt': b'ENGINEERING_TEST_ONLY\n'}
            data = payload['fixture.txt']
            report = {'status': 'STATIC_CLOSURE_COMPLETE', 'members': [{'path': 'fixture.txt',
                       'bytes': len(data), 'source_sha256': sha(data), 'archive_sha256': sha(data)}]}
            result = build(target, report, payload)
            self.assertEqual(result['archive_crc_and_sha256'], 'VERIFIED')
            with self.assertRaisesRegex(ValueError, 'REFUSE_TO_OVERWRITE'):
                build(target, report, payload)
            extracted = folder/'unpacked'; extracted.mkdir()
            with zipfile.ZipFile(target) as archive:
                archive.extractall(extracted)
            self.assertEqual(verify_directory(extracted)['status'], 'VERIFIED')
            (extracted/'fixture.txt').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'PACKAGE_FILE_HASH_MISMATCH'):
                verify_directory(extracted)

    def test_symlink_member_rejected(self):
        with tempfile.TemporaryDirectory(prefix='g3-package-test-') as folder:
            folder = Path(folder); data = b'original'
            (folder/'target.txt').write_bytes(data)
            (folder/'linked.txt').symlink_to(folder/'target.txt')
            (folder/'PACKAGE_MANIFEST.json').write_bytes(json_bytes({'members': [
                {'path': 'linked.txt', 'bytes': len(data), 'archive_sha256': sha(data)}]}))
            with self.assertRaisesRegex(ValueError, 'SYMLINK_PACKAGE_MEMBER'):
                verify_directory(folder)


if __name__ == '__main__':
    unittest.main()
