#!/bin/bash
# Tests for programs.bopaero.com. Needs ../sf50Program and ../sr22tProgram checked out beside this repo.
#   bash tests/run.sh
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$REPO" SF_REPO="$REPO/../sf50Program" SR_REPO="$REPO/../sr22tProgram" node "$REPO/tests/founders.test.mjs" | grep -v '^PASS'
