"""Compile the received source archive in a C-owned empty fixture, without its PDF."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
SOURCE = OUT / "build" / "clean_archive_source"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    if SOURCE.exists():
        raise SystemExit("Independent clean build fixture already exists; do not overwrite")
    SOURCE.mkdir(parents=True)
    with zipfile.ZipFile(OUT.parent / "received" / "Experiment_Report_完整重构_源文件.zip") as z:
        names = []
        for info in z.infolist():
            name = Path(info.filename).relative_to("Experiment_Report_source")
            if str(name) == "Experiment_Report.pdf":
                continue
            p = SOURCE / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(z.read(info))
            names.append(str(name))
    assert not (SOURCE / "Experiment_Report.pdf").exists()
    env = os.environ.copy()
    env["TEXINPUTS"] = str(ROOT / ".venv/texmf/tex/latex") + "//:" + env.get("TEXINPUTS", "")
    commands = {}
    for command in (["xelatex", "--version"], ["kpsewhich", "-var-value=TEXMFROOT"], ["kpsewhich", "placeins.sty"], ["kpsewhich", "needspace.sty"]):
        proc = subprocess.run(command, env=env, text=True, capture_output=True)
        commands[" ".join(command)] = {"exit": proc.returncode, "output": proc.stdout + proc.stderr}
    build = subprocess.run(["bash", "build.sh"], cwd=SOURCE, env=env, text=True, capture_output=True)
    (OUT / "independent-build-console.txt").write_text(build.stdout + build.stderr)
    result = {"reviewer": "independent C", "classification": "REPORT_REBUILD_NOT_EXPERIMENT", "new_model_calls": 0,
              "command": ["bash", "build.sh"], "cwd": str(SOURCE.relative_to(ROOT)),
              "portable_source_members_extracted": len(names), "prebuilt_output_pdf_excluded": True,
              "environment": {"TEXINPUTS": ".venv/texmf/tex/latex//:", "new_installations_by_C": []},
              "provenance": commands, "build_exit_code": build.returncode}
    if build.returncode == 0:
        pdf = SOURCE / "Experiment_Report.pdf"
        info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
        subprocess.run(["pdftotext", "-layout", str(pdf), str(OUT / "independent-rebuilt-text.txt")], check=True)
        approved_text = subprocess.check_output(["pdftotext", "-layout", str(OUT.parent / "received" / "Experiment_Report_吴博闻_10245102410.pdf"), "-"], text=True)
        rebuilt_text = (OUT / "independent-rebuilt-text.txt").read_text()
        log = (SOURCE / "build/Experiment_Report.log").read_text(errors="replace")
        (OUT / "independent-build-latex-log.txt").write_text(log)
        result.update({"rebuilt_sha256": sha(pdf.read_bytes()),
                       "approved_sha256": sha((OUT.parent / "received" / "Experiment_Report_吴博闻_10245102410.pdf").read_bytes()),
                       "pages": int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1)),
                       "exact_extracted_text_equal": approved_text == rebuilt_text,
                       "whitespace_normalized_text_equal": re.sub(r"\s", "", approved_text) == re.sub(r"\s", "", rebuilt_text),
                       "identity_in_text": all(s in rebuilt_text for s in ("吴博闻", "10245102410")),
                       "diagnostics": [line for line in log.splitlines() if re.search(r"^!|Missing character|undefined references|undefined citations|Overfull|LaTeX Font Warning|Rerun", line)],
                       "visual_review": "PENDING_SEPARATE_SAMPLE_INSPECTION"})
        (OUT / "independent-rebuilt-pdfinfo.txt").write_text(info)
    (OUT / "independent-build-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
