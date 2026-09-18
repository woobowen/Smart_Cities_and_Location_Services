"""Compile installed reference templates in fresh temporary trees; render audit evidence.

This script never imports or runs task1. Outputs are template previews, not research results.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[2]
WORK = Path(tempfile.mkdtemp(prefix="codex-infra-repair-001-final-"))
ENGINE = shutil.which("xelatex")
assert ENGINE, "XeLaTeX is required"

# Capture the actual engine exit status for every pass launched by latexmk.
bin_dir = WORK / "bin"
bin_dir.mkdir()
wrapper = bin_dir / "xelatex"
wrapper.write_text(
    "#!/usr/bin/python3\n"
    "import json, os, subprocess, sys\n"
    f"result = subprocess.run([{ENGINE!r}, *sys.argv[1:]])\n"
    "with open(os.environ['INFRA_XELATEX_STATUS'], 'a') as log:\n"
    "    log.write(json.dumps({'args': sys.argv[1:], 'returncode': result.returncode}) + '\\n')\n"
    "sys.exit(result.returncode)\n"
)
wrapper.chmod(0o755)

for name in ("common", "experiment-report", "process-report"):
    shutil.copytree(
        ROOT / "templates/latex" / name,
        WORK / name,
        ignore=shutil.ignore_patterns(
            "build", "_build", "*.aux", "*.log", "*.out", "*.toc",
            "*.fls", "*.fdb_latexmk", "*.synctex.gz",
        ),
    )

results = {}
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
for kind, expected_pages in (("experiment", 5), ("process", 10)):
    dest = EVIDENCE / kind
    dest.mkdir(exist_ok=True)
    pages_dir = dest / "pages"
    pages_dir.mkdir(exist_ok=True)
    assert not list(pages_dir.glob("*.png")), "Do not reuse rendered pages"
    tex = f"{kind}_report_template.tex"
    stem = Path(tex).stem
    status = dest / "xelatex-status.jsonl"
    assert not status.exists(), "Do not mix engine status with an earlier run"
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
               INFRA_XELATEX_STATUS=str(status))
    command = ["latexmk", "-xelatex", "-interaction=nonstopmode", "-file-line-error",
               "-halt-on-error", "-outdir=build", tex]
    run = subprocess.run(command, cwd=WORK / f"{kind}-report", env=env,
                         capture_output=True, text=True)
    console = run.stdout + run.stderr
    (dest / "build-console.txt").write_text(console)
    build = WORK / f"{kind}-report" / "build"
    log = (build / f"{stem}.log").read_text(errors="replace")
    (dest / "latex-log.txt").write_text(log)
    shutil.copy2(build / f"{stem}.fls", dest / "input-recorder.txt")
    result = {"cwd": str(WORK / f"{kind}-report"), "command": command,
              "latexmk_return": run.returncode,
              "xelatex_returns": [json.loads(line)["returncode"]
                                  for line in status.read_text().splitlines()],
              "source_sha256": hashlib.sha256((ROOT / "templates/latex" / f"{kind}-report" / tex).read_bytes()).hexdigest()}
    results[kind] = result
    assert run.returncode == 0, f"{kind}: compile failed; inspect build-console.txt"
    assert all(code == 0 for code in result["xelatex_returns"])
    pdf = dest / f"{stem}.pdf"
    shutil.copy2(build / pdf.name, pdf)
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    (dest / "pdfinfo.txt").write_text(info.stdout + info.stderr)
    text = subprocess.run(["pdftotext", "-layout", str(pdf), str(dest / "pdf-text.txt")],
                          capture_output=True, text=True)
    result.update(pdfinfo_return=info.returncode, pdftotext_return=text.returncode,
                  pdf_bytes=pdf.stat().st_size,
                  page_count=int(re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)[1]))
    assert info.returncode == text.returncode == 0
    assert result["page_count"] == expected_pages
    assert f"{kind.title()} Report" in (dest / "pdf-text.txt").read_text()
    final_diagnostics = [line for line in log.splitlines() if re.search(
        r"^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Missing character|"
        r"Undefined control sequence|Emergency stop|Fatal error|Unable to load", line)]
    duplicate = [line for line in console.splitlines()
                 if re.search(r"already defined|duplicate.*(?:page|destination|object)", line, re.I)]
    result.update(final_log_diagnostics=final_diagnostics, duplicate_page_warnings=duplicate)
    assert not final_diagnostics and not duplicate, (kind, final_diagnostics, duplicate)
    render_cmd = ["pdftoppm", "-r", "110", "-png", str(pdf), str(pages_dir / "page")]
    render = subprocess.run(render_cmd, capture_output=True, text=True)
    (dest / "render-console.txt").write_text(render.stdout + render.stderr)
    pages = sorted(pages_dir.glob("page-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
    result.update(render_command=render_cmd, render_return=render.returncode, rendered_pages=len(pages))
    assert render.returncode == 0 and len(pages) == expected_pages
    cols, thumb_w, thumb_h, label_h, gap = 2, 595, 842, 34, 18
    rows = (len(pages) + cols - 1) // cols
    montage = Image.new("RGB", (cols * (thumb_w + gap) + gap,
                                rows * (thumb_h + label_h + gap) + gap), "#e8e8e8")
    draw = ImageDraw.Draw(montage)
    for i, page in enumerate(pages):
        with Image.open(page) as im:
            im = im.convert("RGB")
            im.thumbnail((thumb_w, thumb_h))
            x = gap + (i % cols) * (thumb_w + gap)
            y = gap + (i // cols) * (thumb_h + label_h + gap)
            draw.text((x, y), f"{kind.title()} template | page {i + 1}", font=font, fill="black")
            montage.paste(im, (x, y + label_h))
    montage.save(dest / "montage.jpg", quality=92)
    print(json.dumps(result), flush=True)

(EVIDENCE / "smoke-results.json").write_text(json.dumps(results, indent=2) + "\n")
print("Temporary clean build:", WORK)
