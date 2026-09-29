"""Capture the authorized input before any source or bundle mutation."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EXPECTED = {
    "SMART_CITIES_RESEARCH_PROTOCOL.md": (11981, "332741175630b1329387a0d69acf0061c6278c82bb27596f1d4629c2aa13a378"),
    "SMART_CITIES_REPORT_WRITING_GUIDE.md": (24040, "abc729c5f7f764021ae1417dc6e8fcb1997eb3632747e46c8d0d53166642ff37"),
    "SMART_CITIES_VISUAL_SYSTEM.md": (42569, "fbba109a796cff5ffe09848986a75b749248e5d609860c54eb2004b839fd9cbc"),
    "WORKFLOW_INTERACTION_EVIDENCE_PROTOCOL.md": (44284, "2385583504caa7c4a7708cd12602c2f692dfd6bb217e1b6ffdd3558b25a22fbd"),
    "AGENTS.md": (33593, "aec7864126d07644ab2d8a724aad7357d146b9adf000ff3e8a3a70b2b644d171"),
    "Experiment_Report_吴博闻_10245102410.pdf": (907540, "2a940be556262725acbe666bbe5b5f8a6b20e08d6838770f0b681bb17bf5cdd0"),
    "Experiment_Report_完整重构_源文件.zip": (3515637, "6c0d2cc5e3b65bccb0279e1dd7ad5e776b5a8fc098b159f34bfd5301242e4dcd"),
}

def record(path):
    st = path.lstat()
    kind = "symlink" if path.is_symlink() else "directory" if path.is_dir() else "file"
    return {"path": path.relative_to(ROOT).as_posix(), "type": kind,
            "size": st.st_size, "mtime_ns": st.st_mtime_ns,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if kind == "file" else None}

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

def main():
    received = OUT / "received"
    if received.exists():
        raise SystemExit("Immutable received capture already exists; refusing overwrite")
    received.mkdir()
    save("starting-workspace.json", {cmd: subprocess.check_output(cmd.split(), cwd=ROOT, text=True)
         for cmd in ("git status --short --branch", "git rev-parse HEAD origin/main",
                     "git remote -v", "git ls-remote origin refs/heads/main")})
    bundle = ROOT / "releases/chatgpt-project-sources"
    save("received-release-inventory.json", [record(p) for p in sorted(bundle.rglob("*"))])
    checks = []
    for name, (size, sha) in EXPECTED.items():
        path = bundle / name
        item = record(path)
        item.update(expected_size=size, expected_sha256=sha,
                    match=item["size"] == size and item["sha256"] == sha,
                    snapshot=f"received/{name}", role="IMMUTABLE_RECEIVED_HISTORY")
        if item["type"] != "file":
            raise SystemExit(f"Unsafe input: {name}")
        shutil.copy2(path, received / name)
        checks.append(item)
    save("received-input-checks.json", checks)
    inventory = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in {".git", ".venv", ".pytest_cache", "__pycache__"}
                         and Path(base, d) != OUT)
        for name in sorted(files):
            inventory.append(record(Path(base, name)))
    save("starting-protection-inventory.json", inventory)
    print(json.dumps({"received": len(checks), "input_matches": all(c["match"] for c in checks),
                      "protected_inventory_files": len(inventory)}, ensure_ascii=False))

if __name__ == "__main__":
    main()
