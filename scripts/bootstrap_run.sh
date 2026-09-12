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
if [ -n "${OP_SERVICE_ACCOUNT_TOKEN:-}" ]; then
  # The op CLI honors the sandbox's SSL_CERT_FILE and proxy settings, so it is
  # the primary resolver; the Python SDK is the fallback.
  OP_VERSION="${OP_CLI_VERSION:-v2.31.1}"
  mkdir -p "$HOME/.local/bin"
  if ! command -v op >/dev/null 2>&1 && [ ! -x "$HOME/.local/bin/op" ]; then
    if curl -sSfL -o "$HOME/.local/bin/op.zip" \
        "https://cache.agilebits.com/dist/1P/op2/pkg/$OP_VERSION/op_linux_amd64_$OP_VERSION.zip" \
       && python3 -c "import zipfile,sys; zipfile.ZipFile(sys.argv[1]).extract('op', sys.argv[2])" \
            "$HOME/.local/bin/op.zip" "$HOME/.local/bin" \
       && chmod +x "$HOME/.local/bin/op"; then
      echo "OK: installed op CLI $OP_VERSION to $HOME/.local/bin"
    else
      echo "WARN: could not install the op CLI; falling back to the 1Password SDK"
    fi
    rm -f "$HOME/.local/bin/op.zip"
  fi
  export PATH="$HOME/.local/bin:$PATH"
  python3 -c "import onepassword" 2>/dev/null || python3 -m pip install -q onepassword-sdk >/dev/null 2>&1 \
    || echo "WARN: could not install onepassword-sdk"
fi
python3 scripts/cs_secrets.py check patreon || true
git ls-remote -q --exit-code origin HEAD >/dev/null 2>&1 && echo "OK: remote reachable for push" \
  || echo "WARN: remote not reachable; the run will report its ledger commit as unpushed"
rm -rf tmp-build
echo "OK: bootstrap complete; work in $DIR"
