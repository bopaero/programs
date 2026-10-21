# programs.bopaero.com

Documents that cover **more than one** bop Aero ownership program (set up 2026-10-21).
Program-specific documents stay on their own sites: sf50program.bopaero.com (bopaero/sf50Program)
and sr22tprogram.bopaero.com (bopaero/sr22tProgram).

| Page | PDF | Pages | Built from |
|---|---|---|---|
| `loi.html` | `bop-Aero-Letter-of-Intent.pdf` | 6 | LOI wording (`LOI_VERSION` in the page) + both costings |
| `comparison.html` | `bop-Aero-Aircraft-Ownership-Comparison.pdf` | 2 | comparison data + both costings |
| `founders-insert.html` | `bop-Aero-Founders-Circle-Insert.pdf` | 2 | `assets/founders.js` + both costings (no figures) |
| `founders-detail.html` | `bop-Aero-Founders-Circle-Detail-Sheet.pdf` | 2 | `assets/founders.js` + both costings |

Every source is read from the live sites at render time: costings (and their `costing.js`) from
the two program sites; the comparison data and `assets/comparison.js` still live in the SF50 repo
(edited at the costing editor's `/comparison`) until the editor Worker moves.

- **Publish** (`.github/workflows/publish.yml`): every push to main. `tools/build-pdf.py --out _site --archive`
  refuses to publish unless each PDF has its exact page count, its version stamp on every page, all
  documents agree on the source versions, and nothing leaked (`undefined`, error text, a figure on
  the Insert). New versions are archived to `versions/` and committed `[skip ci]`.
- **Refresh** (`.github/workflows/refresh.yml`): every 15 min, compares the live SF50 costing, SR22T
  costing and comparison versions with `data/build.json` and runs Publish when any changed.
- Local check: `python3 tools/build-pdf.py --check` (needs Chrome + poppler).
- Wording change to the LOI → bump `LOI_VERSION`. A program added to either costing appears in the
  LOI by itself; a new aircraft type is one entry in `AIRCRAFT` in `loi.html`.
