#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v xelatex >/dev/null || { printf 'XeLaTeX is required.\n' >&2; exit 1; }
mkdir -p build
export SOURCE_DATE_EPOCH=1790899200
export FORCE_SOURCE_DATE=1
# Compile the delivered static master. No models, network, input recovery or
# experiment execution is involved. Both passes are needed for references.
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex >build/compile_stdout_1.log 2>&1
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex >build/compile_stdout_2.log 2>&1
cp build/main.pdf Process_Report_Revised.pdf
printf 'Created %s/Process_Report_Revised.pdf\n' "$PWD"
