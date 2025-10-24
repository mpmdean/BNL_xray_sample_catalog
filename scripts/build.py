#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import itables
from string import Template

# --- config ----------------------------------------------------
CSV_PATH = Path("database.csv")
OUT_DIR = Path("site")
OUT_FILE = OUT_DIR / "index.html"

# Clamp body cells for these column indexes (0-based); [] to disable
CLAMP_COLUMNS = [2]
CLAMP_LINES = 2

# Optional: set predictable widths for body cells (by index)
COLUMN_WIDTHS = {2: "28ch"}

# Keep these header labels on one line and ensure a minimum width (by *name*)
COLUMN_MIN_WIDTHS_BY_NAME = {
    "Location": "9ch",
    "Salary":   "8ch",
}
# ---------------------------------------------------------------

df = pd.read_csv(CSV_PATH)

# Build DataTables columnDefs for body cells (widths + clamp class)
columnDefs = []
for idx, w in COLUMN_WIDTHS.items():
    columnDefs.append({"targets": idx, "width": w})
for idx in CLAMP_COLUMNS:
    columnDefs.append({"targets": idx, "className": "clamp-2"})

# Generate table HTML (no 'responsive', to avoid warnings)
html_snippet = itables.to_html_datatable(
    df,
    connected=True,
    classes="display",                 # <- no 'nowrap'
    display_logo_when_loading=False,
    autoWidth=False,                   # let CSS/layout control widths
    columnDefs=columnDefs,
)

# Dynamic CSS rules to set min-width for columns by *name*
min_width_rules = []
for name, width in COLUMN_MIN_WIDTHS_BY_NAME.items():
    if name in df.columns:
        nth = df.columns.get_loc(name) + 1  # nth-child is 1-based
        min_width_rules.append(
            f"table.dataTable th:nth-child({nth}), table.dataTable td:nth-child({nth}) {{ min-width: {width}; }}"
        )
column_min_width_css = "\n    ".join(min_width_rules) or "/* (no named min-width rules) */"

template = Template("""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Interactive Table</title>
  <meta name="description" content="CSV rendered as an interactive DataTable with itables">
  <style>
    body {
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
      padding: 2rem; max-width: 1100px; margin: auto;
    }
    h1 { font-weight: 600; }
    .note { color: #444; font-size: 0.95rem; margin-bottom: 1rem; }

    .table-wrap { width: 100%; overflow-x: auto; }

    /* Fixed layout = predictable widths; body cells may wrap */
    table.dataTable { table-layout: fixed; width: 100% !important; }

    /* BODY CELLS: allow wrapping and breaking long tokens */
    table.dataTable td {
      white-space: normal !important;
      word-break: break-word;
    }

    /* HEADERS: keep labels on a single line */
    table.dataTable thead th {
      white-space: nowrap !important;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    /* Column-specific minimum widths (by nth-child) */
    ${column_min_width_css}

    /* Optional: multi-line clamp for selected body columns */
    td.clamp-2 {
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: ${clamp_lines};
      overflow: hidden;               /* hide beyond the clamp */
      line-height: 1.25;
      max-height: calc(1.25em * ${clamp_lines});
      position: relative;             /* anchor for hover preview */
      cursor: help;                   /* hint that more text exists */
    }

    /* Hover preview bubble (doesn't reflow table) */
    td.clamp-2:hover { overflow: visible; }
    td.clamp-2:hover::after {
      content: attr(data-full);       /* set dynamically from cell text */
      position: absolute;
      left: 0; top: 100%;
      z-index: 9999;
      white-space: normal;
      max-width: min(48ch, 60vw);
      margin-top: .25rem;
      padding: .5rem .6rem;
      background: rgba(0,0,0,.92);
      color: #fff;
      border-radius: .5rem;
      box-shadow: 0 8px 28px rgba(0,0,0,.25);
      pointer-events: none;           /* don't steal mouse events */
    }

    /* If the bubble would overflow viewport on the right, allow wrapping */
    @media (max-width: 640px) {
      td.clamp-2:hover::after { max-width: 80vw; }
    }
  </style>
</head>
<body>
  <h1>BNL Sample Catalog</h1>
  <p class="note">Edit the database <a href="https://github.com/mpmdean/BNL_xray_sample_catalog/blob/main/database.csv">here</a>.</p>
  <div class="table-wrap">
    $table
  </div>

  <script>
    // Attach full text to clamped cells as both title=... (native tooltip)
    // and data-full (for the custom hover bubble). Re-apply on each draw.
    (function() {
      function annotateClampedCells(scope) {
        (scope.querySelectorAll ? scope : document).querySelectorAll('td.clamp-2').forEach(function(td) {
          var txt = (td.textContent || '').trim();
          if (txt) {
            if (!td.getAttribute('title')) td.setAttribute('title', txt);    // native tooltip
            td.setAttribute('data-full', txt);                                // custom bubble
          }
        });
      }

      function hookTables() {
        document.querySelectorAll('table.dataTable').forEach(function(tbl) {
          // initial pass
          annotateClampedCells(tbl);
          // on redraw (paging, sorting, search)
          if (window.jQuery && jQuery.fn && jQuery.fn.dataTable) {
            jQuery(tbl).on('draw.dt', function() { annotateClampedCells(tbl); });
          } else {
            // Fallback: periodic refresh if DataTables/jQuery not exposed
            setInterval(function(){ annotateClampedCells(tbl); }, 500);
          }
        });
      }

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', hookTables);
      } else {
        hookTables();
      }
    })();
  </script>
</body>
</html>""")

page = template.substitute(
    table=html_snippet,
    clamp_lines=CLAMP_LINES,
    column_min_width_css=column_min_width_css,
)

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(page, encoding="utf-8")
print(f"Wrote {OUT_FILE}")
