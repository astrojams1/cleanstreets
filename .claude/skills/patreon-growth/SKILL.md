---
name: patreon-growth
description: "Grow the number of monthly contributors on the Clean Streets Patreon (patreon.com/cleanstreets). Each run measures active patrons and joins, attributes new patrons to a source, then takes at least three concrete growth actions: welcome emails with referral links, ref-coded Patreon links on the site, conversion experiments on index.html, re-engagement of lapsed patrons, referral asks, and impact-update posts. Use whenever the user mentions Patreon, patrons, contributors, supporters, monthly donors, membership growth, 'how many patrons', 'grow the patreon', 'why aren't we growing', conversion, referrals, or on a scheduled growth run, even if they don't name the skill."
metadata:
  version: "1.0"
---

# Patreon Growth

One metric matters: **active monthly patrons**. Everything this skill does
either moves that number, measures it, or learns why it did not move.
Analysis that does not end in an action is not an output of this skill.
Conventions shared with every skill in this repository are in
`.claude/skills/README.md`; read it once per session before running this.

Ref code for this skill: `CS-PG-MMDD`. Per-run send cap: 5 emails.
Concurrent experiments: at most 3.

## Step 0: Preflight

1. Note the start time in Pacific time. Confirm this folder is a checkout
   (`git rev-parse --show-toplevel` succeeds and `scripts/ledger.py` exists);
   otherwise stop and report. Then `git push` any unpushed ledger commits from
   earlier runs and `git pull --ff-only origin master` so `data/supporters.csv`
   is current; if either fails, continue with local data and note it. Remove
   a stale `tmp-build/` if one exists.
2. Read the last three ledger entries and the experiment registry:
   ```bash
   python3 scripts/ledger.py show --skill patreon-growth --last 3
   ```
   Then read `references/experiments.md`. A `next:` line on the last entry is
   the first action this run takes.
3. If this run will send email, apply the account guard from the README
   (connected Gmail account must be `james@cleanstreets.io`). Without Gmail,
   the run still proceeds: email actions are written out in full in the run
   report for James to send, and the ledger records them as `drafted`.

## Step 1: Measure (do not skip, do not estimate)

Sources, best first. Record which one was used in the `source=` metric.

1. **Patreon API** when `.claude/data/patreon-config.json` exists (git-ignored;
   holds `creator_access_token` and `campaign_id`). One request:
   ```
   GET https://www.patreon.com/api/oauth2/v2/campaigns/<campaign_id>/members
     ?fields[member]=full_name,patron_status,currently_entitled_amount_cents,pledge_relationship_start,last_charge_status
     &page[count]=100
   Authorization: Bearer <creator_access_token>
   ```
   Follow `meta.pagination.cursors.next` until null. Count
   `patron_status == "active_patron"` for `active_patrons`, sum their
   `currently_entitled_amount_cents` for `mrr_usd`, and derive joins and
   churn against the previous ledger entry's numbers. On 401, note it in the
   report and fall through to source 2; do not retry.
2. **Repository data** (always available):
   ```bash
   python3 scripts/patron_metrics.py --since-days 7 --json
   python3 scripts/patron_metrics.py --since-days 30 --json
   ```
   `joined` is a reliable signal of new supporters; `roll_total` is an upper
   bound on active patrons, not the active count. Say which in the ledger.
3. **Hand-offs from the inbox**: grep the inbox-processor ledger for
   `handoff:patreon-growth` lines newer than this skill's last run. Each one
   is either a new patron to welcome, a lapsed patron to re-engage, or a
   sponsorship lead to hand a brief to.

Attribute every new patron to a source using the ref-code registry in
`references/playbook.md`: the `?ref=` on the link they used when it is known
(Patreon exposes it rarely), otherwise the closest recent action (a welcome
referral link, a site experiment, an email), otherwise `organic`. Record the
attribution as a `patron:<first-name-last-initial-slug> | <source>` detail line.

## Step 2: Learn

For each experiment in `references/experiments.md` with status `running`:

- Its measurement window has ended: decide `won`, `lost`, or `inconclusive`
  against the kill criterion written when it started. Move won tactics into
  the playbook's "What works" list; move lost ones into "What does not work"
  with the reason. Never leave a decision for a later run.
- Its window is open: leave it, unless a result is already impossible (then
  end it early as `lost`).

If any playbook entry contradicts what this run measured, fix the playbook in
the same run.

## Step 3: Execute (at least three actions per run)

Pick from this list in order. Every action changes a file, sends or drafts an
email, or starts an experiment. "Researched" is not an action.

1. **Welcome new patrons.** For each new patron with a known email (from the
   inbox hand-off or the API), send the welcome in
   `references/email-templates.md`. It must contain the concrete-outcome line,
   the personal referral link `https://www.patreon.com/cleanstreets?ref=referral-<slug>`,
   and the "how'd you hear about Clean Streets" question. One welcome per
   patron ever; check `python3 scripts/ledger.py seen --skill patreon-growth --key patron:<slug>` first.
2. **Ref-code sweep of the site.** Every Patreon link in `index.html` carries
   a `?ref=` from the registry (hero, nav, mobile menu, footer, JSON-LD). Fix
   any that do not, in a commit of its own. Never touch the `#supporters` or
   `#top-supporters` lists; they are generated.
3. **Site conversion experiment.** If fewer than 3 experiments are running,
   start one from the backlog in `references/experiments.md`: a single change
   to a CTA, headline, or the "$40 funds 1 hour" line, with a ref code unique
   to the experiment so joins can be attributed, a 14-day window, and a kill
   criterion. Commit the change on the current branch and record it. One
   variable per experiment.
4. **Re-engage lapsed patrons.** For declined or cancelled patrons surfaced
   by the API or an inbox hand-off, send the re-engagement template once,
   30 days or more after the lapse, never twice. Declined cards get the
   "your card bounced" note; cancellations get the no-pressure check-in.
5. **Referral asks to existing patrons.** Up to 3 per run, longest-tenured
   first, to active patrons who never received a personal referral link.
   Template in `references/email-templates.md`. Track with `patron:<slug>`
   detail lines so nobody gets asked twice.
6. **Impact update post.** Once a month, draft the Patreon post from
   `data/impact.csv` totals (hours funded, pounds removed, miles cleaned)
   and the month's new-supporter count. Put the full text in the run report
   for James to post, or post via the API if a token with `campaigns.posts`
   scope is present.
7. **Sponsorship briefs.** For a business lead from the inbox, write a short
   block-sponsorship brief (what $X/month funds on their block, using the
   $40-per-hour figure) as a draft reply in the thread.

Guardrails, all of them, every run:

- Numbers come from `data/impact.csv`, `data/supporters.csv`, or the Patreon
  API. Never invent or round up a stat.
- Every Patreon link shared anywhere carries a `?ref=` from the registry.
- No cold pitches to journalists (tried, zero replies). No tactics that need
  501(c)(3) status; Clean Streets is an LLC. No in-person events proposed.
- No more than 5 emails sent per run; drafts beyond that.
- No pledge amounts tied to names in any committed file.
- Site edits keep the existing section patterns and Tailwind classes
  described in `agents.md` and must pass `python3 -m pytest tests/`.
- Stop new work after 15 minutes. Write a `partial` entry with a `next:` line
  and exit; measurement and ledger always complete, actions can wait.

## Step 4: Ledger and commit (every run)

```bash
python3 scripts/ledger.py add --skill patreon-growth \
  --started "<start time>" \
  --outcome success \
  --actions <count of Step 3 actions> \
  --summary "<active patrons and delta>; <top action>; <one learning>" \
  --metric active_patrons=<n or unknown> --metric roll_total=<n> \
  --metric joined_7d=<n> --metric left_7d=<n> --metric mrr_usd=<n or unknown> \
  --metric sends=<n> --metric experiments_running=<n> --metric source=api|csv \
  --detail "patron:<slug> | joined | <attributed source>" \
  --detail "experiment:<id> | started|won|lost | <one line>" \
  --detail "action | <what changed, file or email>" \
  --next "<first action for the next run>"
```

`success` requires a measured number and at least three actions; `partial`
if only one of those held; `noop` only when there was truly nothing to do,
which should be rare because the ref-code sweep and experiment backlog
almost always offer an action.

Then:

```bash
python3 -m pytest tests/ -q
python3 scripts/ledger.py check
git add .claude/skills/patreon-growth/ index.html
git commit -m "ledger(patreon-growth): <summary>"
git push -u origin <current branch>
```

If the push fails (no credentials in the sandbox), do not retry in a loop.
Report "ledger commit unpushed"; the next run's preflight pushes it. Delete
`tmp-build/` if this run created it.

If the run changed `index.html`, say so plainly in the report: a push to
`master` deploys the site.

## Run report

```
Patrons: <active or roll total> (<+/- since last run>), source: api|csv
New this week: <first name L, source> ...
Experiments: <id: status, days left> ...
Actions taken (n):
  1. ...
Learned: <one line>
For James: <anything only he can do: post text, tier copy, a send without Gmail>
Ledger: run NNNN appended and committed (or: not pushed, reason)
```

## What this skill does not do

- Does not triage the inbox; inbox-processor does, and hands leads here.
- Does not edit the supporter lists or impact numbers in `index.html`; the
  daily workflow generates those.
- Does not change Patreon tier prices or campaign settings; it proposes exact
  copy for James to apply in the Patreon UI.
