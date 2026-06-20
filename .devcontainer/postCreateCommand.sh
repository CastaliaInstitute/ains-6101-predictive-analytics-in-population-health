#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name ains6003 --display-name "Python 3 (AINS6003)"

echo
echo "AINS6003 Codespace ready."
echo "Build the book with: make html"
echo "Preview with: python -m http.server 8000 --directory _build/html"
