# itables + GitHub Pages (starter)

This repo turns a CSV into an interactive HTML table using itables and publishes it to GitHub Pages via GitHub Actions.

## Current config
- 1000-row sample CSV (`data/table.csv`).
- **Option B** enabled: table cells **wrap** long content (no `nowrap`).

## How it works
- `data/table.csv` → processed by `scripts/build.py` (pandas + itables)
- Output HTML goes to `site/index.html`
- Workflow `.github/workflows/pages.yml` uploads `site/` as a Pages artifact and deploys it