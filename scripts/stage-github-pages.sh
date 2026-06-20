#!/usr/bin/env bash
# Combine static front site (pages/) with Jupyter Book HTML (book/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d _build/html ]]; then
  echo "Run 'make html' first." >&2
  exit 1
fi

rm -rf site
mkdir -p site/book
cp -R pages/. site/
cp -R _build/html/. site/book/
touch site/.nojekyll
echo "Staged site -> site/ (front page + book/ + slides/)"
