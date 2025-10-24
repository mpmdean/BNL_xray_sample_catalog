from pathlib import Path
import pandas as pd
import itables
from string import Template

# Read the CSV
df = pd.read_csv("data/table.csv")

# Interactive DataTable HTML
html_snippet = itables.to_html_datatable(
    df,
    connected=True,
    classes="display nowrap",
    display_logo_when_loading=False,
)

template = Template("""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Interactive Table</title>
  <meta name="description" content="CSV rendered as an interactive DataTable with itables">
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
           padding: 2rem; max-width: 1100px; margin: auto; }
    h1 { font-weight: 600; }
    .note { color: #444; font-size: 0.95rem; margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>Interactive CSV Table</h1>
  <p class="note">Built from <code>data/table.csv</code> using <a href="https://github.com/mwouts/itables">itables</a>.</p>
  $table
</body>
</html>""")

page = template.substitute(table=html_snippet)

out_dir = Path("site")
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "index.html").write_text(page, encoding="utf-8")
print("Wrote site/index.html")