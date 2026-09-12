#!/usr/bin/env bash
# Run the repository's test suite. Used by the skills before every commit and
# by scheduled runs. Exit status is pytest's.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 1
python3 -c "import pytest, bs4" 2>/dev/null || python3 -m pip install -q pytest beautifulsoup4 requests pytz >/dev/null 2>&1
python3 -m pytest tests/ -q
