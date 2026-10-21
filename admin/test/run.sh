#!/bin/bash
# bopaero-admin Worker tests: SF50 at /sf50, SR22T at /sr22t, index, Founder summary, comparison
# editor + planning guide. Bundles admin/worker.js exactly as wrangler would (pages as text) and
# runs every suite against mocked GitHub + Cloudflare Access. Needs ../sf50Program and
# ../sr22tProgram checked out beside this repo, like the deploy.
#   bash admin/test/run.sh
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO_DIR="$(cd "$HERE/../.." && pwd)"
SF="${SF_REPO:-$REPO_DIR/../sf50Program}"; SR="${SR_REPO:-$REPO_DIR/../sr22tProgram}"
npx -y esbuild "$REPO_DIR/admin/worker.js" --bundle --format=esm --loader:.html=text \
  --outfile="$HERE/worker.mjs" --log-level=warning
cd "$HERE"
REPO="$SF" node sf50.test.mjs | grep -v '^PASS'
REPO="$SF" SR_REPO="$SR" node sr22t.test.mjs | grep -v '^PASS'
REPO="$REPO_DIR" SF_REPO="$SF" SR_REPO="$SR" node comparison.test.mjs | grep -v '^PASS'
