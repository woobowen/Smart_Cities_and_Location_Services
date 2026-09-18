"""Package installed Design System sources, then compile only the extracted package."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
archive = ROOT / "releases/design-system/smart_cities_design_system_v2.1.zip"
assert not archive.exists(), "Do not overwrite an existing release"
archive.parent.mkdir(parents=True, exist_ok=True)
prefix = "smart_cities_design_system_v2.1/"
sources = [ROOT / "docs/design-system/SMART_CITIES_VISUAL_SYSTEM.md"]
sources += sorted(p for p in (ROOT / "templates/latex").rglob("*") if p.is_file())
for p in sources:
    assert p.suffix not in {".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk"}
    assert "build" not in p.parts and ":Zone.Identifier" not in p.name
manifest = """# Design System distribution manifest

- version = v2.1
- Experiment Report = LOCKED
- Process Report = LOCKED
- P2 Cloud Sorbet Exact = LOCKED
- Compilation engine = XeLaTeX
- Demo assets are synthetic/template material, not experimental results or real interaction evidence.

v2.1 is a technical repair release of the installed v2 specification: corrected demo-asset paths, a common P2 color source, LaTeX warning fixes, and installed Skill references. It introduces no visual redesign.

The installed publication-plots Skill is distributed separately under releases/skills/publication-plots.zip. It is not needed to compile these template previews.

From each report directory, run:

```bash
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build experiment_report_template.tex
latexmk -xelatex -interaction=nonstopmode -file-line-error -halt-on-error -outdir=build process_report_template.tex
```

The packaged previews are installed visual references. Fresh build PDFs are generated from the packaged sources during release verification.
"""
payload = {}
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in sources:
        name = p.relative_to(ROOT).as_posix()
        z.write(p, prefix + name)
        payload[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    z.writestr(prefix + "MANIFEST.md", manifest)
(EVIDENCE / "package-files.sha256.json").write_text(json.dumps(payload, indent=2) + "\n")

work = Path(tempfile.mkdtemp(prefix="project-baseline-sync-001-"))
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        p = PurePosixPath(name)
        assert not p.is_absolute() and ".." not in p.parts
    z.extractall(work)
extracted = work / prefix.rstrip("/")
for name, sha in payload.items():
    assert hashlib.sha256((extracted / name).read_bytes()).hexdigest() == sha

# Record every engine return while leaving latexmk's arguments unchanged.
engine = shutil.which("xelatex")
assert engine
bin_dir = work / "bin"
bin_dir.mkdir()
wrapper = bin_dir / "xelatex"
wrapper.write_text(
    "#!/usr/bin/python3\nimport json, os, subprocess, sys\n"
    f"r = subprocess.run([{engine!r}, *sys.argv[1:]])\n"
    "with open(os.environ['BASELINE_ENGINE_LOG'], 'a') as f:\n"
    "    f.write(json.dumps({'returncode': r.returncode, 'args': sys.argv[1:]}) + '\\n')\n"
    "sys.exit(r.returncode)\n"
)
wrapper.chmod(0o755)
bundle = ROOT / "releases/chatgpt-project-sources"
bundle.mkdir(parents=True)
results = {}
for kind, pages, preview_name in [
    ("experiment", 5, "Experiment_Report_P2_Exact.pdf"),
    ("process", 10, "Process_Report_P2_Locked_v1.pdf"),
]:
    dest = EVIDENCE / kind
    dest.mkdir()
    cwd = extracted / "templates/latex" / f"{kind}-report"
    command = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-file-line-error",
               "-halt-on-error", "-outdir=build", f"{kind}_report_template.tex"]
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
               BASELINE_ENGINE_LOG=str(dest / "xelatex-status.jsonl"))
    run = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    console = run.stdout + run.stderr
    (dest / "build-console.txt").write_text(console)
    build = cwd / "build"
    stem = f"{kind}_report_template"
    log = (build / f"{stem}.log").read_text(errors="replace")
    (dest / "latex-log.txt").write_text(log)
    diagnostics = [line for line in log.splitlines() if re.search(
        r"^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Missing character|"
        r"Undefined control sequence|Emergency stop|Fatal error|Unable to load", line)]
    duplicates = [line for line in console.splitlines() if "already defined" in line]
    engine_codes = [json.loads(line)["returncode"] for line in (dest / "xelatex-status.jsonl").read_text().splitlines()]
    result = {"command": command, "cwd": str(cwd), "latexmk_return": run.returncode,
              "xelatex_returns": engine_codes, "final_diagnostics": diagnostics,
              "duplicate_page_warnings": duplicates}
    assert run.returncode == 0 and all(code == 0 for code in engine_codes)
    assert not diagnostics and not duplicates
    pdf = build / f"{stem}.pdf"
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    (dest / "pdfinfo.txt").write_text(info.stdout + info.stderr)
    text = subprocess.run(["pdftotext", "-layout", str(pdf), str(dest / "pdf-text.txt")], capture_output=True, text=True)
    actual_pages = int(re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)[1])
    assert info.returncode == text.returncode == 0 and actual_pages == pages
    assert f"{kind.title()} Report" in (dest / "pdf-text.txt").read_text()
    shutil.copy2(pdf, bundle / preview_name)
    result.update(page_count=actual_pages, pdfinfo_return=info.returncode,
                  pdftotext_return=text.returncode, exported_pdf=str((bundle / preview_name).relative_to(ROOT)),
                  pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
    results[kind] = result
    print(json.dumps(result), flush=True)
(EVIDENCE / "smoke-results.json").write_text(json.dumps(results, indent=2) + "\n")
(EVIDENCE / "release.json").write_text(json.dumps({
    "path": str(archive.relative_to(ROOT)), "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
    "source_file_count": len(payload), "source_bytes_verified": True,
    "clean_extraction": str(extracted), "manifest": manifest,
}, indent=2) + "\n")
