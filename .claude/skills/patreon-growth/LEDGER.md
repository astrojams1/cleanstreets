# Ledger: patreon-growth

Append-only run log for this skill. One entry per run, newest at the bottom.
Written by `scripts/ledger.py add`; never hand-edit or delete past entries.
Format and privacy rules: `.claude/skills/README.md`.

## 2026-09-11T18:37-07:00 | run 0001 | success
- actions: 3
- summary: Roll 106 (0 joined, 1 left in 30d), active count unknown without API token; ref-coded every site Patreon link (exp-001 running); impact data has no rows since 2026-07-07
- metrics: active_patrons=unknown roll_total=106 joined_7d=0 left_7d=1 joined_30d=0 left_30d=1 mrr_usd=unknown sends=0 experiments_running=1 source=csv
- details:
  - experiment:exp-001 | started | ref codes on hero, nav, mobile, footer, JSON-LD; sameAs set to bare profile URL
  - experiment:exp-002 | corrected | subline math fixed to 7.5 minutes per month
  - action | index.html: 6 Patreon links ref-coded (live once merged to master)
  - action | references/posts/2026-09-totals.md: totals post drafted for James to publish
  - action | playbook: recorded /join/ path convention and that patreon.com returns 403 to anonymous fetches
  - handoffs | none from inbox-processor this run
- next: On 2026-09-25 decide exp-001; ask James for a Patreon API token in .claude/data/patreon-config.json and for impact rows after 2026-07-07
