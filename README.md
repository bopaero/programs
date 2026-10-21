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

The costings (and their `costing.js`) are read from the two program sites at render time; the
comparison data (`data/comparison.json`) and `assets/comparison.js` live in this repo, edited at
the admin Worker's `/comparison/`.

- **Publish** (`.github/workflows/publish.yml`): every push to main. `tools/build-pdf.py --out _site --archive`
  refuses to publish unless each PDF has its exact page count, its version stamp on every page, all
  documents agree on the source versions, and nothing leaked (`undefined`, error text, a figure on
  the Insert). New versions are archived to `versions/` and committed `[skip ci]`.
- **Refresh** (`.github/workflows/refresh.yml`): every 15 min, compares the live SF50 and SR22T
  costing versions with `data/build.json` and runs Publish when either changed (a comparison
  publish commits here, so Publish runs directly).
- Local check: `python3 tools/build-pdf.py --check` (needs Chrome + poppler).
- Wording change to the LOI → bump `LOI_VERSION`. A program added to either costing appears in the
  LOI by itself; a new aircraft type is one entry in `AIRCRAFT` in `loi.html`.

## Admin Worker (`admin/`)

`bopaero-admin` at https://bopaero-admin.compilotrc.workers.dev — every private editor behind one
Cloudflare Access login (moved here from the SF50 repo's `sf50-costing` Worker, 2026-10-21):
`/` index · `/sf50/` SF50 costing · `/sr22t/` SR22T costing · `/comparison/` comparison data (commits
here) · `/founders` Founder's Circle Summary · `/planning` planning guide.

- The SF50 and SR22T editor pages and `costing.js` are bundled from `../sf50Program` and
  `../sr22tProgram`: deploy with both checked out (on main) beside this repo.
- Deploy: `cd admin && npx wrangler deploy`. Tests: `bash admin/test/run.sh` (+ `bash tests/run.sh`).
- Verifies the Access JWT itself and fails closed until `ACCESS_TEAM_DOMAIN` / `ACCESS_AUD` are set
  (`admin/wrangler.toml`; the AUD is the `kid` in an unauthenticated request's login redirect).
- Secret `GITHUB_TOKEN`: ONE fine-grained token, Contents read/write + Actions read on
  sf50Program, sr22tProgram and programs. Set with `pbpaste | npx wrangler secret put GITHUB_TOKEN`
  (from `admin/`). Never type it on a command line.
- `admin/legacy/`: the old `sf50-costing` name, deployed as a 301 redirect to this Worker.
