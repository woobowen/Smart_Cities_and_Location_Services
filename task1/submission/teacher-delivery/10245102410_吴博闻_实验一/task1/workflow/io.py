"""Small, explicit JSON and version helpers. No model-generated paths or commands."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'task1/作业/作业/traj_dict.json'
CONFIG = ROOT / 'task1/config/goal1.json'
EVIDENCE = ROOT / 'task1/evidence/goal1'


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':'))


def object_hash(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value, *, exclusive=False):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    if exclusive:
        with p.open('x', encoding='utf-8') as f:
            f.write(text)
    else:
        tmp = p.with_suffix(p.suffix + '.tmp')
        tmp.write_text(text, encoding='utf-8')
        os.replace(tmp, p)


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def bound_path(base, name):
    """Reject traversal, absolute paths and symlink components before any access."""
    base = Path(base).resolve()
    n = Path(name)
    if n.is_absolute() or not n.parts or any(x in ('.', '..') for x in n.parts):
        raise ValueError('ILLEGAL_PATH')
    p = base / n
    for component in (p, *p.parents):
        if component == base:
            break
        if component.is_symlink():
            raise ValueError('SYMLINK_PATH')
    if not p.resolve().is_relative_to(base):
        raise ValueError('ILLEGAL_PATH')
    return p
