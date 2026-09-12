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

## 2026-09-11T23:08-07:00 | run 0002 | partial
- actions: 2
- summary: Roll 106 (0 joined 7d/30d, Mystic left, already reflected in prior run); started exp-002 hero-subline experiment; no 3rd action possible without a resolvable Patreon token
- metrics: active_patrons=unknown roll_total=106 joined_7d=0 left_7d=1 joined_30d=0 left_30d=1 mrr_usd=unknown sends=0 experiments_running=2 source=csv
- details:
  - experiment:exp-002 | started | hero subline to "$5 a month funds 7.5 minutes of paid cleanup."; hero CTA ref site-hero -> exp-002 for the window; decide 2026-09-26
  - action | index.html: hero subline + hero CTA ref updated for exp-002
  - action | references/experiments.md, references/playbook.md: exp-002 marked running, corrected math baked in, token-resolution failure recorded as a fact
  - note | OP_SERVICE_ACCOUNT_TOKEN present but 1Password SDK resolve raised and no op CLI on PATH; patreon_stats.py and per-patron email lookups unavailable this run
  - handoffs | none from inbox-processor this run
- next: Get a resolvable Patreon token (fix 1Password SDK auth/network or install op CLI) so active_patrons and per-patron emails are measurable; on 2026-09-25 decide exp-001; on 2026-09-26 decide exp-002

## 2026-09-11T23:14-07:00 | run 0003 | success
- actions: 3
- summary: First working token resolution (active_patrons=26, mrr_usd=1111, source=api) after PR #80 fixed the vault mid-run; started exp-004 (CTA below impact grid); skipped all sends after finding every top candidate already contacted by an untracked sender
- metrics: active_patrons=26 roll_total=106 total_members=114 former_patrons=82 joined_7d=0 left_7d=1 mrr_usd=1111 sends=0 experiments_running=3 source=api
- details:
  - experiment:exp-004 | started | CTA button below impact-numbers grid; decide 2026-09-26
  - action | index.html: exp-004 CTA added below impact grid
  - action | references/playbook.md: recorded that PR #80 (landed mid-run) fixed the vault mismatch; patreon_stats.py and per-patron lookups now resolve from this platform
  - action | references/playbook.md: recorded that the top re-engagement/referral candidates (1 declined, top lapsed, 3 longest-tenured active) were all already emailed on this exact topic by a `jane@` sender this skill has never used and that is not in this ledger -- flagged as a cross-skill dedup gap, no emails sent
  - candidate:mego | skipped | already re-engaged by jane@cleanstreets.io (declined-card thread, last 2026-06-18)
  - candidate:chet | skipped | already re-engaged by jane@cleanstreets.io (no-pressure close-out, last 2026-07-17)
  - candidate:aislingf | skipped | already sent a referral ask (2026-06-26 and 2026-07-24)
  - candidate:melissab | skipped | already sent a referral ask (2026-06-26 and 2026-07-24)
  - candidate:stephaniec | skipped | already sent a referral ask (2026-06-26 and 2026-07-24)
  - handoffs | none from inbox-processor this run
- next: Find and coordinate with whichever skill sends from jane@cleanstreets.io (likely patron-reactivation or cold-lead-followup) so patron outreach shares one dedup record; once that's resolved, patreon-growth can safely pick re-engagement/referral targets from live API data. On 2026-09-25 decide exp-001, on 2026-09-26 decide exp-002 and exp-004.
