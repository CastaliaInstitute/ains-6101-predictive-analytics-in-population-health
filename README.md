# AINS6101 Predictive Analytics in Population Health

Jupyter Book course repository for **AINS6101** / Aurnova **AIN6101** — Predictive Analytics in Population Health.

[Open in GitHub Codespaces](https://codespaces.new/CastaliaInstitute/ains-6101-predictive-analytics-in-population-health)

Structure follows [CastaliaInstitute/ains-6003-deep-learning-and-neural-networks](https://github.com/CastaliaInstitute/ains-6003-deep-learning-and-neural-networks) and the Aurnova MSAI course-site pattern.

## Contents

- prose chapters per module
- Thebe-enabled assignment notebooks
- RISE-ready slide notebooks
- slide narration and instructor notes
- executable lab notebooks (Modules 1-8)

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make html
```

## Export formats

- `make html` — web book
- `make pdf` — LaTeX PDF
- `make epub` — EPUB export

## Publishing

Push to `main` to publish via GitHub Pages (see `.github/workflows/pages.yml`).

**Canonical URL:** https://ains6101.courses.castalia.institute/

Fallback: https://castaliainstitute.github.io/ains-6101-predictive-analytics-in-population-health/
