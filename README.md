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
- **Refresh** (`.github/workflows/refresh.yml`): started by the costing editor right after a publish
  (it waits for the costing to go live), and on a 15-min schedule as backup (GitHub runs it hours apart). Compares the live SF50 and SR22T
  costing versions with `data/build.json` and runs Publish when either changed (a comparison
  publish commits here, so Publish runs directly).
- Local check: `python3 tools/build-pdf.py --check` (needs Chrome + poppler).
- Wording change to the LOI → bump `LOI_VERSION`. A program added to either costing appears in the
  LOI by itself; a new aircraft type is one entry in `AIRCRAFT` in `loi.html`.

## LOI in DocuSign (2026-10-24)

The LOI PDF carries an invisible DocuSign anchor tag at every field (white 5pt text painted under the
page's ink, PDF only: the website never shows them). Raymond's DocuSign template places each field
with Auto-Place on its tag, so replacing the template's document keeps the fields in place.
`build-pdf.py` refuses a PDF unless every tag appears exactly once. Every deployed change to the
LOI PDF (wording or either costing) opens an issue asking Raymond to replace the template's document;
it lists any tags that were added or removed.

| Tag | Role | DocuSign field |
|---|---|---|
| `\m_eff\` `\m_effyr\` | Manager | Effective Date (month/day, year) |
| `\o_name\` | Prospective Owner | Prospective Owner name (text) |
| `\o_pg_<aircraft>_<key>\` | Prospective Owner | One checkbox per program, e.g. `\o_pg_sf50_g2plus\`, `\o_pg_sr22t_g7plus\` |
| `\o_shares\` | Prospective Owner | Ownership Shares Selected (number) |
| `\o_pay1\` `\o_pay2\` | Prospective Owner | SR22T payment option (radio group) |
| `\o_fc\` | Prospective Owner | Founder's Circle (checkbox) |
| `\m_exp\` `\m_expyr\` | Manager | Expiration date (month/day, year) |
| `\o_sig\` `\o_printname\` `\o_date\` | Prospective Owner | Signature, Full Name, Date Signed |
| `\m_sig\` `\m_printname\` `\m_title\` `\m_date\` | Manager | Signature, Full Name, Title, Date Signed |
| `\o_attach\` | Prospective Owner | Attachment A (attachment field, optional) |

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
  sf50Program, sr22tProgram and programs, plus Actions **write** on programs: a costing publish starts
  `refresh.yml` (wait_minutes 20), which waits for the costing to go live and runs Publish, so the
  LOI, comparison and Founder's Circle PDFs follow within minutes (2026-10-24). Without that permission
  the publish still succeeds and the editor reports the rebuild as scheduled. Set with `pbpaste | npx wrangler secret put GITHUB_TOKEN`
  (from `admin/`). Never type it on a command line.
- `admin/legacy/`: the old `sf50-costing` name, deployed as a 301 redirect to this Worker.
