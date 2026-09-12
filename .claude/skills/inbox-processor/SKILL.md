---
name: inbox-processor
description: "Process the Clean Streets inbox (james@cleanstreets.io): sweep every unhandled inbound email, classify it (intake-form submission, patron or Patreon notice, service request, partner or community thread, press, vendor pitch, automated notice), reply as James where a standard reply fits, archive noise, flag the rest for James, and record every message in the skill ledger. Use this whenever the user says 'process my inbox', 'check the clean streets email', 'clear the inbox', 'any new emails', 'reply to that email', 'what came in', or on a scheduled inbox sweep, even if they don't name the skill."
metadata:
  version: "1.1"
---

# Inbox Processor

Turns the james@cleanstreets.io inbox into a handled inbox: every inbound
message ends up replied to, archived, or explicitly handed to James, and the
ledger says which. Conventions shared with every skill in this repository are
in `.claude/skills/README.md`; read it once per session before running this.

Ref code for this skill: `CS-IP-MMDD`. Per-run send cap: 10 emails.

## Step 0: Preflight

1. Note the start time in Pacific time (it goes on the ledger entry). Confirm
   this folder is a checkout (`git rev-parse --show-toplevel` succeeds and
   `scripts/ledger.py` exists); otherwise stop and report. Then
   `git push` any unpushed ledger commits from earlier runs and
   `git pull --ff-only origin master`; if either fails, continue and note it.
   Remove a stale `tmp-build/` if one exists.
2. Read the last three ledger entries for continuity:
   ```bash
   python3 scripts/ledger.py show --skill inbox-processor --last 3
   ```
   Anything on a `next:` line is the first thing this run does.
3. Account guard: fetch the connected Gmail account's profile. If it is not
   `james@cleanstreets.io`, stop here, write an `aborted` ledger entry, and
   report which account was connected. Use whichever Gmail tool is connected
   in this session (the Clean Streets Gmail MCP or a Gmail connector); the
   steps below name operations, not tool names.

## Step 1: Sweep

Search for candidate messages. Do not restrict to the inbox: a message
archived by hand or by another tool is still unhandled until this ledger
says otherwise (a September 3 new-patron notification was archived unseen
and missed a welcome; run 0001 could not find it).

```
newer_than:7d -from:cleanstreets.io -in:sent -in:draft
```

If the previous ledger entry is older than 7 days, widen `newer_than` to
cover the gap since that entry, up to 30 days.

Then, for every result, check whether the ledger already has it:

```bash
python3 scripts/ledger.py seen --skill inbox-processor --key msg:<message-id>
```

Exit 0 means handled on a previous run; skip it. The ledger is the only dedup
gate. Do not rely on read state, labels, or inbox presence, since James reads
mail on his phone and any of those can change without anything being handled.

If nothing survives the filter, skip to Step 5 and log a `noop` entry.

Outbound guard: a search term can still match our own sent mail. Before acting
on any message, confirm the sender is not a `@cleanstreets.io` address and the
message is not labeled `SENT`. Our own mail is never a candidate.

## Step 2: Classify

Read each surviving message in full (the thread, if it has one) and assign
exactly one category from `references/triage-policy.md`:

| Category | Signal |
|---|---|
| `intake-form` | Notification from the "Get in touch" form (subject contains "Get in touch") |
| `patreon-notice` | Patreon system mail: new patron, declined payment, cancellation, message |
| `service-request` | A person or business asking Clean Streets to clean a block or wants pricing |
| `partner-community` | Neighborhood groups, Refuse Refuse, merchants, BIDs, existing partners |
| `press` | Journalists, podcasts, newsletters asking for comment or interview |
| `vendor-pitch` | Sales, SEO, agencies, cold offers |
| `automated` | Receipts, platform notices, calendar, newsletters, security alerts |
| `job-application` | Someone asking to work for Clean Streets |
| `personal` | Mail to James as a person rather than to Clean Streets |
| `unknown` | Cannot tell; always flagged, never auto-answered |

Before drafting anything for a human sender, run the prior-correspondence check
from the README (`from:<address> OR to:<address>`). If James or a skill already
replied on this topic, the action is `noted`, not `replied`.

## Step 3: Act

The policy table in `references/triage-policy.md` maps each category to one of
four actions. Apply it as written; the reasoning behind each row is there too.

- **replied**: compose from `references/reply-templates.md`, adapt to the
  message, send as `text/html` in the original thread. Only when the template
  needs no fact you do not have (no pricing, no dates, no promises).
- **drafted**: same composition, saved as a draft in the thread, not sent. Use
  this when the reply needs James's judgment or a fact only he has, and
  whenever the send cap has been reached.
- **archived**: remove from inbox. Nothing to answer, nothing James needs to
  see. Never delete.
- **flagged**: leave in the inbox, star it, and list it in the run report with
  a one-line reason and the decision James has to make.

Reply composition rules (all of them, every time):

1. James's voice: first person, warm, direct, five sentences or fewer.
2. Answer the actual question first. Then, if it fits, one line on how
   Clean Streets works and a Patreon link with a ref code
   (`https://www.patreon.com/cleanstreets?ref=inbox-<category>`).
3. No meetings or calls proposed or accepted. If they ask for one, reply that
   email is fastest and ask the question that a call would have answered.
4. No prices, no service commitments, no dates. Those are James's to give.
5. Signature block from the README with ref code `CS-IP-MMDD` (today's date),
   body ends with `</p>`, no scaffolding text of any kind in the body.
6. Reread the draft as the recipient before sending. If it reads like a form
   letter, rewrite it shorter and more specific.

Hand-offs: when a message reveals a new patron, a lapsed patron, someone asking
how to support, or a business wanting to sponsor, add a ledger detail line
`handoff:patreon-growth | <one-line context, no personal data>` so the
patreon-growth skill picks it up on its next run.

## Step 4: Caps and safety

- Send at most 10 emails per run. Past that, draft instead and say so.
- Never reply to `press`, `unknown`, or anything with a complaint, legal
  language, or an angry tone. Flag those.
- Never reply to a job application unless James has said applications are open
  (they are closed by default; the policy file records the current state).
- Never unsubscribe, forward, or share a message outside this inbox.
- If a Gmail operation fails, retry once; on the second failure, record the
  message as `error` in the details and keep going with the rest.
- Stop new work after 15 minutes. Write a `partial` entry with a `next:` line
  naming the first unhandled message ID and exit.

## Step 5: Ledger and commit (every run, including noop and aborted)

One detail line per message handled, with the message ID, category, action,
and sender domain only. No addresses, names beyond first name and last
initial, or message content (the repository is public).

```bash
python3 scripts/ledger.py add --skill inbox-processor \
  --started "<start time>" \
  --outcome success \
  --actions <messages acted on> \
  --summary "Processed N messages: a replied, b drafted, c archived, d flagged" \
  --metric swept=N --metric replied=a --metric drafted=b --metric archived=c --metric flagged=d \
  --detail "msg:<id> | <category> | <action> | <sender-domain>" \
  --detail "handoff:patreon-growth | <context>" \
  --next "<first thing the next run should do, or omit>"
```

Then validate and commit:

```bash
python3 scripts/ledger.py check
bash scripts/run_tests.sh
git add .claude/skills/inbox-processor/
git commit -m "ledger(inbox-processor): <summary>"
git push origin HEAD
```

If the push fails (no credentials in the sandbox), do not retry in a loop.
Report "ledger commit unpushed"; the next run's preflight pushes it. Delete
`tmp-build/` if this run created it.

## Run report

End with this structure, and nothing after it:

```
Inbox processed: N new messages (swept M, K already in ledger)
Replied (a): first-name L — category — one line on what was said
Drafted (b): ... — why it needs James
Flagged (d): ... — the decision James has to make
Archived (c): categories only
Hand-offs: to patreon-growth: ...
Ledger: run NNNN appended and committed (or: not pushed, reason)
```

## What this skill does not do

- Does not run Patreon growth actions; it hands those to patreon-growth.
- Does not process the personal inbox (astrojams1@gmail.com).
- Does not delete mail, change filters, or manage labels beyond starring flags.
- Does not create tasks for James to review drafts; the report and the draft
  itself are the hand-off.

## Changes

- 2026-09-11 v1.1: sweep no longer restricted to `in:inbox`, and widens to
  the gap since the last run. Evidence: a new-patron notification from
  September 3 sat archived and unhandled; run 0001's inbox-only sweep could
  not see it and the patron got no welcome.
