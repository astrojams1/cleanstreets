#!/usr/bin/env bash
# Bootstrap a scheduled skill run (Claude Code Routines).
#
# Fetches a fresh, clean checkout of master into /tmp/cleanstreets (or updates
# the one already there), confirms the tools the skills need, and prints one
# line per check. Lines start with OK, WARN, or ERROR. A Routine prompt stops
# on ERROR and notes WARN lines in its report.
#
#   curl -fsSL https://raw.githubusercontent.com/astrojams1/cleanstreets/master/scripts/bootstrap_run.sh | bash
#   cd /tmp/cleanstreets
set -u
REPO="${CLEANSTREETS_REPO:-https://github.com/astrojams1/cleanstreets.git}"
DIR="${CLEANSTREETS_DIR:-/tmp/cleanstreets}"
fail() { echo "ERROR: $*"; exit 1; }

if [ -d "$DIR/.git" ]; then
  git -C "$DIR" fetch -q origin master || fail "fetch failed for $DIR"
  git -C "$DIR" checkout -q -B master origin/master || fail "checkout failed in $DIR"
  git -C "$DIR" clean -qfd
  echo "OK: updated existing checkout at $DIR"
else
  rm -rf "$DIR"
  git clone -q --branch master "$REPO" "$DIR" || fail "clone failed: $REPO"
  echo "OK: cloned master into $DIR"
fi
cd "$DIR" || fail "cannot cd to $DIR"
echo "OK: head $(git rev-parse --short HEAD) $(git log -1 --format=%s | cut -c1-60)"

if [ -z "$(git config user.email)" ]; then
  git config user.name "Clean Streets skills"
  git config user.email "james@cleanstreets.io"
  echo "OK: git identity set for commits"
fi

command -v python3 >/dev/null || fail "python3 not found"
python3 -c "import pytest, bs4" 2>/dev/null || {
  python3 -m pip install -q pytest beautifulsoup4 requests pytz >/dev/null 2>&1 \
    && echo "OK: installed test dependencies" \
    || echo "WARN: could not install pytest/beautifulsoup4; run_tests.sh will fail"
}
python3 scripts/ledger.py check || fail "ledger check failed on a clean checkout"

for s in inbox-processor patreon-growth; do
  [ -f ".claude/skills/$s/SKILL.md" ] && echo "OK: skill $s present" || echo "WARN: skill $s missing"
done
[ -n "${PATREON_ACCESS_TOKEN:-}" ] && echo "OK: PATREON_ACCESS_TOKEN set" \
  || echo "WARN: PATREON_ACCESS_TOKEN not set; patreon-growth will use the supporter roll only"
git ls-remote -q --exit-code origin HEAD >/dev/null 2>&1 && echo "OK: remote reachable for push" \
  || echo "WARN: remote not reachable; the run will report its ledger commit as unpushed"
rm -rf tmp-build
echo "OK: bootstrap complete; work in $DIR"
