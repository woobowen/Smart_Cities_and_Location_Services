#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v xelatex >/dev/null || { echo '需要安装 XeLaTeX。' >&2; exit 1; }
mkdir -p build
for pass in 1 2; do
  if ! xelatex -interaction=nonstopmode -halt-on-error -output-directory=build Experiment_Report.tex >"build/compile-${pass}.log" 2>&1; then
    tail -n 70 "build/compile-${pass}.log" >&2
    exit 1
  fi
done
cp build/Experiment_Report.pdf Experiment_Report.pdf
printf '已生成 %s/Experiment_Report.pdf\n' "$PWD"
