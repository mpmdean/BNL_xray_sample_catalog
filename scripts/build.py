from pathlib import Path
import pandas as pd
import itables
from string import Template

# --- Settings you can customize ---------------------------------------------
# Columns that should be truncated by default (2-line clamp),
# expand in place on hover, and show a full-value tooltip.
COLUMNS_TO_TRUNCATE = ["name", "department"]

# Number of visible lines before clamping
CLAMP_LINES = 2
# -----------------------------------------------------------------------------

# Read the CSV
df = pd.read_csv("data/table.csv")

# Find column indices for DataTables "targets"
targets = [df.columns.get_loc(c) for c in COLUMNS_TO_TRUNCATE if c in df.columns]

# Build interactive DataTable HTML
html_snippet = itables.to_html_datatable(
    df,
    connected=True,                 # Load required JS/CSS from CDNs (works on GitHub Pages)
    classes="display",              # Allow wrapping (Option B baseline)
    display_logo_when_loading=False,
    layout={                        # DataTables v2 layout
        "topStart": "pageLength",
        "topEnd": {"search": {"placeholder": "Search table..."}},
        "bottomStart": "info",
        "bottomEnd": "paging",
    },
    pageLength=25,
    lengthMenu=[10, 25, 50, 100, 250, 500],
    search={"caseInsensitive": True},
    columnDefs=[
        {"targets": targets, "className": "clip-2"}  # mark cells to clamp
    ] if targets else None,
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

    /* Option B baseline: wrap long content inside table cells */
    table.dataTable td, table.dataTable th {
      white-space: normal;        /* allow wrapping */
      overflow-wrap: anywhere;    /* break long tokens */
      word-break: break-word;     /* fallback */
    }

    /* Clamp for selected cells; the inner .clip element is what gets clamped */
    td.clip-2 .clip {
      display: -webkit-box;
      -webkit-line-clamp: ${clamp_lines};
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    /* Hover: expand in place (remove clamp) */
    td.clip-2:hover .clip {
      -webkit-line-clamp: unset;
      max-height: none;
    }
  </style>
</head>
<body>
  <h1>Interactive CSV Table</h1>
  <p class="note">
    Cells in <code>${truncate_cols}</code> are truncated to ${clamp_lines} line(s) by default.
    Hover to expand. A native tooltip shows the full value.
  </p>
  $table

  <script>
  // Wrap target cells with a <div class="clip"> and set a native tooltip (title).
  (function(){
    function wrapCells(scope){
      var root = (scope instanceof Element ? scope : document);
      var tds = root.querySelectorAll('td.clip-2:not([data-wrapped])');
      for (var i=0; i<tds.length; i++){
        var td = tds[i];
        td.setAttribute('data-wrapped', '1');
        var txt = (td.textContent || '').trim();
        td.title = txt; // native tooltip
        var div = document.createElement('div');
        div.className = 'clip';
        div.textContent = txt; // safe text insertion
        td.textContent = '';
        td.appendChild(div);
      }
    }

    // Initial pass
    wrapCells(document);

    // Re-run when DataTables redraws/paginates/sorts (DOM changes)
    var mo = new MutationObserver(function(muts){
      for (var j=0; j<muts.length; j++){
        var m = muts[j];
        if (m.addedNodes) {
          for (var k=0; k<m.addedNodes.length; k++){
            var node = m.addedNodes[k];
            if (node && node.nodeType === 1) wrapCells(node);
          }
        }
      }
    });
    mo.observe(document.body, {subtree:true, childList:true});
  })();
  </script>
</body>
</html>""")

page = template.substitute(
    table=html_snippet,
    truncate_cols=", ".join(COLUMNS_TO_TRUNCATE) if COLUMNS_TO_TRUNCATE else "(none)",
    clamp_lines=str(CLAMP_LINES),
)

out_dir = Path("site")
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / "index.html").write_text(page, encoding="utf-8")
print("Wrote site/index.html")
