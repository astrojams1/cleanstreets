---
name: patreon-growth
description: "Grow the number of monthly contributors on the Clean Streets Patreon (patreon.com/cleanstreets) through outreach: win back former patrons, ask current patrons for referrals, follow up with everyone who ever wrote in, and reach merchants, neighborhood groups, and property managers on the blocks the crew cleans. Each run measures active patrons, works the prospect pipeline (follow-ups first, then new first touches by channel), attributes joins to their source, and records every contact in the ledger. Use whenever the user mentions Patreon, patrons, contributors, supporters, monthly donors, membership growth, outreach, prospects, win-back, referrals, 'how many patrons', 'grow the patreon', 'why aren't we growing', or on the scheduled growth run, even if they don't name the skill."
metadata:
  version: "2.0"
---

# Patreon Growth

One metric matters: **active monthly patrons**. The lever is outreach:
finding people with a reason to give, writing to them as James, following
up, and measuring which channel produces joins. The website is not a lever
(a couple dozen visitors a month); site work is limited to keeping ref codes
intact. Conventions shared with every skill in this repository are in
`.claude/skills/README.md`; read it once per session before running this.

Ref code for this skill: `CS-PG-MMDD`. Per-run send cap: 20 emails.
Concurrent experiments: at most 3. Touches per contact, ever: 3.

## Step 0: Preflight

1. Note the start time in Pacific time. Read the last three ledger entries:
   ```bash
   python3 scripts/ledger.py show --skill patreon-growth --last 3
   ```
   A `next:` line on the last entry is the first action this run takes.
2. Read `references/outreach-channels.md` (channels, quotas, order of work)
   and `references/experiments.md`.
3. Apply the account guard from the README before any send: the connected
   Gmail account must be `james@cleanstreets.io`. Without Gmail, the run
   still measures and plans; emails are written out in full in the run
   report and ledgered as `drafted`.

## Step 1: Measure

1. **Patron counts.** `data/patreon_stats.json` if its `synced_at` is within
   36 hours (`source=workflow`); otherwise
   ```bash
   python3 scripts/patreon_stats.py
   ```
   which resolves the token itself (never fetch or print it) and prints
   `active_patrons`, `mrr_usd`, `declined_patrons`, `former_patrons`. Exit 1
   means no token or API refusal: note the WARN and fall through to
   `python3 scripts/patron_metrics.py --since-days 7 --json` (`source=csv`).
2. **Joins and churn** against the previous entry's numbers. For each new
   patron, attribute a source: the `?ref=` on the link if known, else a
   `prospect:` ledger line for that person in `replied` or later, else a
   referral slug, else `organic`. Record `patron:<slug> | joined | <source>`.
3. **Pipeline state** from this ledger: every `prospect:` line, latest stage
   per slug. Count open prospects, follow-ups due (last touch 10 or more
   days ago, no reply), close-outs due (21 or more days), replies waiting.
4. **Hand-offs** from the inbox: `handoff:patreon-growth` lines in
   `.claude/skills/inbox-processor/LEDGER.md` newer than this skill's last
   run. Each is a new patron to welcome, a lapsed patron, a lead, or a reply
   to one of our prospects.

## Step 2: Learn

- Decide every experiment whose window has ended (`won`, `lost`,
  `inconclusive`) against its kill criterion; update
  `references/experiments.md`.
- Update the evidence column in `references/outreach-channels.md` for every
  channel that had sends or replies since the last run: sends, replies,
  conversions. A channel that hits its kill signal is paused in that file
  with the date; a channel that produced a join gets its quota raised by
  one.
- Fix any playbook statement the ledger now contradicts.

## Step 3: Execute (the outreach engine)

Work in this order until the send cap is reached. Every email follows the
README's persona, no-meetings, no-commitments, and signature rules, and
`references/email-templates.md` for the skeleton.

1. **Replies.** For every prospect who wrote back: answer in the thread,
   move them to `replied`; if they joined, `converted` and a welcome.
2. **Follow-ups and close-outs due**, oldest first. A reply almost always
   comes on the second or third email; these outrank new first touches.
3. **Welcome new patrons** from Step 1 (template requires the concrete
   outcome line, the personal referral link
   `https://www.patreon.com/cleanstreets?ref=referral-<slug>`, and the
   "how'd you hear about Clean Streets" question). Once per patron, ever.
4. **New first touches**, by channel order and quota in
   `references/outreach-channels.md`: win-back, referral, warm inbound,
   block merchants, neighborhood groups, property managers. Discovery for
   each channel is described there; do the discovery, then send.
5. **Monthly post** once a month from `data/impact.csv` totals, put in the
   report for James to publish.

Before every send, without exception:

- **Prior-correspondence check** across all our senders:
  `from:<address> OR to:<address>` in Gmail. If James, hello@, jane@, or
  any skill already wrote to this person on this topic, do not send; ledger
  the prospect as `skipped | already contacted <yyyy-mm-dd>`. (Run 0003
  found five candidates already emailed from jane@ by an older system;
  that check is what prevented a third message in one summer.)
- **Touch count**: three lifetime touches per contact. The third is the
  close-out; after it, `closed`.
- **One contact per business or household per run.**
- **Address resolution at send time**, never from the ledger: the API for
  patrons, Gmail for inbound leads, the business's own site for merchants.

Record every contact as a ledger detail line:

```
prospect:<slug> | <channel> | <stage> | <yyyy-mm-dd> | <one-line note, no address>
```

Slug: business name in lowercase with hyphens, or first name plus last
initial for a person. Stages: `identified`, `first_touch`, `follow_up`,
`close_out`, `replied`, `converted`, `declined`, `bounced`, `skipped`,
`closed`. The ledger is public: no email addresses, phone numbers, or
message text.

Guardrails, every run:

- Numbers come from `data/impact.csv`, `data/supporters.csv`, or the API.
  Never invent a stat.
- No cold pitches to journalists. No tactics needing 501(c)(3) status. No
  events. No prices. No site copy or layout changes; only ref-code repair
  when a Patreon link on the site has lost its `?ref=`.
- Send cap 20 per run; beyond it, draft and say so.
- Stop new work after 15 minutes; write a `partial` entry with a `next:`
  line. Measurement and the ledger always complete.

## Step 4: Ledger and commit (every run)

```bash
python3 scripts/ledger.py add --skill patreon-growth \
  --started "<start time>" \
  --outcome success \
  --actions <emails sent + prospects identified + experiment decisions> \
  --summary "<active patrons and delta>; <sends by channel>; <replies/conversions>; <one learning>" \
  --metric active_patrons=<n|unknown> --metric mrr_usd=<n|unknown> \
  --metric joined_7d=<n> --metric left_7d=<n> --metric source=workflow|api|csv \
  --metric sends=<n> --metric first_touches=<n> --metric followups=<n> \
  --metric replies=<n> --metric converted=<n> --metric prospects_open=<n> \
  --detail "prospect:<slug> | <channel> | <stage> | <date> | <note>" \
  --detail "patron:<slug> | joined | <source>" \
  --detail "experiment:<id> | started|won|lost | <one line>" \
  --next "<follow-ups due tomorrow, channel to open next, anything for James>"
```

`success` needs a measured patron count and at least five sends or a full
pipeline sweep with nothing due; `partial` if the time cap or the send cap
stopped work; `noop` should not happen while any channel has quota.

Then:

```bash
bash scripts/run_tests.sh
python3 scripts/ledger.py check
git add .claude/skills/patreon-growth/
git commit -m "ledger(patreon-growth): <summary>"
git push origin HEAD
```

If the push fails, report "ledger commit unpushed" once with the entry text
and stop. Delete `tmp-build/` if this run created it.

## Run report

```
Patrons: <active> (<+/- since last run>), MRR $<n>, source: <source>
Pipeline: <open> open, <due> follow-ups due, <replies> replies handled
Sent (<n>): <channel>: <slug>, <slug> ... (first touch / follow-up / close-out)
Skipped: <slug>: already contacted <date> by <sender> ...
Joined: <slug> via <source> ...
Experiments: <id>: <status> ...
Learned: <one line>
For James: <replies needing his judgment, the monthly post, anything blocked>
Ledger: run NNNN appended and committed
```

## What this skill does not do

- Does not triage the inbox; inbox-processor does, and hands leads here.
- Does not change site copy, layout, or the generated supporter lists.
- Does not change Patreon tiers or settings; it proposes copy for James.
- Does not store anyone's email address, phone number, or message text in
  the repository.

## Changes

- 2026-09-11 v2.0: refocused from site experiments to outreach on James's
  instruction. Added the prospect pipeline, channel quotas and order of
  work (`references/outreach-channels.md`), the cross-sender
  prior-correspondence rule, and pipeline metrics. Retired exp-002 and
  exp-004 and reverted their site changes.
- 2026-09-11 v1.x: token resolution via 1Password, `data/patreon_stats.json`
  as first source, ref-code sweep (exp-001).
