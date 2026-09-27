"""Read the actually published, fixed Git commit; never predict a future SHA."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import quote
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[5]
BASE = Path(__file__).resolve().parent
REPOSITORY = 'https://github.com/woobowen/Smart_Cities_and_Location_Services.git'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    target = git('rev-parse', args.commit + '^{commit}').decode().strip()
    assert len(target) == 40
    branch = git('branch', '--show-current').decode().strip()
    origin = git('remote', 'get-url', 'origin').decode().strip()
    local = git('rev-parse', 'HEAD').decode().strip()
    tracking = git('rev-parse', 'origin/main').decode().strip()
    remote = git('ls-remote', '--heads', 'origin', 'main').decode().split()[0]
    assert branch == 'main' and origin == REPOSITORY
    assert target == local == tracking == remote
    paths = [
        'task1/evidence/goal3/REVIEW_PACKET.md',
        'task1/evidence/goal3/requirements.json',
        'task1/docs/goal3/REVIEW_GUIDE.md',
        'task1/evidence/goal3/closeout/SC-LAB1-G3-CLOSEOUT-001/a_diagnosis/MASTER_REQUIREMENTS_REVIEW.md',
        'task1/evidence/goal3/report_build/build_receipt.json',
        'task1/reports/experiment1/experiment1.pdf',
        'task1/reports/process1/process1.pdf',
        'task1/notebooks/final/作业1轨迹数据预处理_完成版.ipynb',
        'task1/notebooks/final/任务3_LLM辅助评估清洗_完成版.ipynb',
        'task1/submission/REVIEW_ONLY_10245102410_吴博闻_实验一.zip',
    ]
    results = []
    for path in paths:
        url = 'https://raw.githubusercontent.com/woobowen/Smart_Cities_and_Location_Services/' + target + '/' + quote(path)
        expected = git('show', target + ':' + path)
        with urlopen(url, timeout=60) as response:
            actual = response.read()
            code = response.status
        assert code == 200 and actual == expected, path
        results.append({'path': path, 'fixed_url': url, 'http_status': code,
                        'bytes': len(actual), 'sha256': sha(actual), 'equals_committed_blob': True})
    package = json.loads((BASE / 'PACKAGE_VALIDATION.json').read_text())
    record = {
        'at': datetime.now(timezone.utc).isoformat(), 'status': 'ARTIFACT_REMOTE_VERIFIED',
        'repository': REPOSITORY, 'branch': branch, 'CLOSEOUT_ARTIFACT_SHA': target,
        'local_HEAD_at_check': local, 'origin_main_at_check': tracking,
        'actual_remote_main_at_check': remote, 'local_remote_equal_at_check': True,
        'NUMERIC_CODE_SHA': package['NUMERIC_CODE_SHA'],
        'historical_numeric_ARTIFACT_SHA': 'fd559e451291b9d424682853ef0909aa5eb94b32',
        'DOCUMENT_BUILD_CODE_SHA': package['DOCUMENT_BUILD_CODE_SHA'],
        'PACKAGE_CONTENT_ID': package['PACKAGE_CONTENT_ID'],
        'files': results,
        'boundary': 'This record documents the already published artifact commit. Its own later bookkeeping commit is not predicted; final HEAD is checked after that actual push and reported in chat. Fixed remote byte checks are engineering evidence, not the pending web GPT content review.',
        'GPT_SECOND_REVIEW': 'PENDING', 'Understanding': 'LEARNING',
        'Submission': 'NOT_READY', 'sent_to_teacher': False,
    }
    assert not args.output.exists(), 'Do not overwrite an original publication receipt'
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'commit': target, 'fixed_files_verified': len(results)}))


if __name__ == '__main__':
    main()
