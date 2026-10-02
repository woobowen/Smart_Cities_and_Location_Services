#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
compile_block() {
  local n="$1"
  local d tex
  d=$(printf "block%02d" "$n")
  tex="$d.tex"
  echo "[build] $d/$tex"
  (cd "$ROOT/$d" && latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "$tex" >/dev/null)
  cp "$ROOT/$d/${tex%.tex}.pdf" "$BUILD/$d.pdf"
}
for n in $(seq 1 12); do compile_block "$n"; done
pdfunite "$BUILD"/block{01..12}.pdf "$BUILD/WF_WorkflowConstruction_PreTask1_31p.pdf"
pages=$(pdfinfo "$BUILD/WF_WorkflowConstruction_PreTask1_31p.pdf" | awk '/^Pages:/ {print $2}')
echo "[result] pages=$pages"
[ "$pages" = "31" ] || { echo "expected 31 pages, got $pages" >&2; exit 1; }
