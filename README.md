# itables + GitHub Pages (starter)

This repo turns a CSV into an interactive HTML table using itables and publishes it to GitHub Pages via GitHub Actions.

## How it works
- `data/table.csv` → processed by `scripts/build.py` (pandas + itables)
- Output HTML goes to `site/index.html`
- Workflow `.github/workflows/pages.yml` uploads `site/` as a Pages artifact and deploys it

## Quick start
1. Replace the contents of `data/table.csv` with your data.
2. Push this repo to GitHub (default branch `main`).
3. In your repo: Settings → Pages → set **Build and deployment** source to **GitHub Actions**.
4. Push a change (or run the workflow manually). Your Pages URL will appear in the workflow logs.