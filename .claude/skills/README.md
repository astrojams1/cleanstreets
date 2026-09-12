# Clean Streets skills

Repository-local skills live here, one directory per skill:

```
.claude/skills/<skill-name>/
├── SKILL.md        required: frontmatter (name, description, metadata.version) + instructions
├── LEDGER.md       required: append-only run log, written only via scripts/ledger.py
└── references/     optional: policies, templates, playbooks loaded on demand
```

`tests/test_skill_ledgers.py` fails if any skill directory is missing either
required file or if a ledger is malformed, so the conventions below apply to
every skill that exists now and every skill added later.

## The ledger rule

Every skill keeps a ledger, and every run of a skill ends by appending exactly
one entry to it, including runs that did nothing and runs that failed. The
ledger is how James sees what the automation did without reading transcripts,
how the next run knows where the last one stopped, and how skills hand work to
each other.

Append with the helper, never by hand:

```bash
python3 scripts/ledger.py add --skill <skill-name> \
  --outcome success|partial|error|aborted|noop \
  --actions <count of meaningful operations> \
  --summary "one line: what happened" \
  --metric key=value --metric key=value \
  --detail "one line per item handled" \
  --next "what the next run should pick up first"
```

Useful reads:

```bash
python3 scripts/ledger.py show --skill <skill-name> --last 3     # continuity at start of run
python3 scripts/ledger.py seen --skill <skill-name> --key msg:abc # exit 0 if already recorded
python3 scripts/ledger.py check                                   # validate every ledger
python3 scripts/ledger.py init --skill <new-skill>                # first ledger for a new skill
```

Entry format (produced by the helper; the test validates it):

```
## 2026-09-12T09:30-07:00 | run 0007 | success
- actions: 3
- summary: Processed 4 inbox messages: 2 replied, 1 archived, 1 flagged for James
- metrics: swept=4 replied=2 archived=1 flagged=1
- details:
  - msg:18f2c3a9b1 | intake-form | replied | gmail.com
  - handoff:patreon-growth | new patron Dana R joined via site-hero
- next: Dana R welcome email once patreon-growth confirms the pledge
```

Rules:

- **Outcome vocabulary.** `success` (did what it set out to), `partial` (some
  items failed), `error` (could not complete), `aborted` (a guard stopped it,
  e.g. wrong Gmail account), `noop` (nothing to do). An early exit is still a run.
- **Detail lines are the dedup and hand-off record.** Prefix stable keys so
  `ledger.py seen` can find them later: `msg:<gmail-message-id>`,
  `thread:<gmail-thread-id>`, `patron:<slug>`, `handoff:<target-skill>`,
  `experiment:<id>`.
- **Metrics are `key=value` tokens with no spaces.** Use the same keys from run
  to run so trends can be read straight off the ledger.
- **Never edit or delete past entries.** Corrections go in a new entry.
- **Commit the ledger at the end of every run** together with any other files
  the run changed, message `ledger(<skill-name>): <summary>`. If the run cannot
  push, say so in the run report so the entry is not lost with the sandbox.

### Privacy (this repository is public)

The site is published from this repository, so ledgers are public too. Never
write into a ledger: full email addresses, phone numbers, street addresses,
message bodies, pledge amounts tied to a named person, or anything a
correspondent would not expect to see on a public page. Identify people by
first name plus last initial (`Dana R`), senders by domain (`gmail.com`), and
messages by Gmail ID. Our own `@cleanstreets.io` addresses are fine to name.
Secrets and caches belong in `.claude/data/`, which is git-ignored.

## Shared conventions for skills that touch email

- **Account guard.** Before the first Gmail action, fetch the connected
  account's profile and confirm it is `james@cleanstreets.io`. Any other
  address: stop, ledger `aborted`, report.
- **Persona.** Replies are from James, first person, warm, plain, short. No
  corporate gratitude phrases, no jargon, nothing a neighbor would not say.
- **No meetings.** Never propose, accept, or confirm a call or in-person
  meeting. Move the conversation forward over email instead.
- **No commitments James has not made.** Do not quote prices, promise service
  on a block, promise dates, or speak for partners. Flag those for James.
- **Prior-correspondence check.** Before replying to anyone, search
  `from:<address> OR to:<address>`. If James (or a skill) already replied on
  this topic, do not reply again.
- **Ref codes.** Every outbound email carries a ref code in the signature so a
  reply can be routed back to the skill that sent it: `CS-<XX>-<MMDD>` where
  `XX` is the skill code (inbox-processor `IP`, patreon-growth `PG`,
  skill-improver `SI`, which sends no email) and
  `MMDD` is the send date. Every Patreon link we share carries `?ref=<source>`
  (see the patreon-growth playbook for the registry).
- **Signature.** Send as `text/html`. End the body with the signature and a
  closing `</p>`; the body must contain no XML, CDATA, or prompt scaffolding.

```html
<p>James Thompson<br>
Clean Streets<br>
<a href="https://www.cleanstreets.io">cleanstreets.io</a> · CS-XX-MMDD</p>
```

- **Send caps.** Each skill states its own per-run cap. Beyond the cap, leave a
  draft instead of sending, and note it in the ledger.

## Running on a schedule (Claude Code Routines)

The skills run as Routines in Claude Code on the web (claude.ai/code, Routines).
Each firing starts a fresh session in the environment that has this repository
and the Gmail connector, so nothing persists between runs except what is
committed. Two Routines exist:

| Routine | Schedule (PT) | Skill |
|---|---|---|
| Clean Streets: inbox-processor | hourly, 7:00 to 17:00 | inbox-processor |
| Clean Streets: patreon-growth | daily, 9:15 | patreon-growth |
| Clean Streets: skill-improver | weekly, Sunday 8:00 | skill-improver |

Each Routine's prompt does the same four things:

1. **Bootstrap.** `curl -fsSL https://raw.githubusercontent.com/astrojams1/cleanstreets/master/scripts/bootstrap_run.sh | bash`
   clones or updates a clean checkout of master at `/tmp/cleanstreets`,
   installs test dependencies, validates the ledgers, and prints `OK`, `WARN`,
   or `ERROR` lines. The run stops on `ERROR` and reports any `WARN`.
2. **Run the skill** from that checkout, following SKILL.md exactly, using
   whichever Gmail tool the session has (the account guard still applies).
3. **Ledger, tests, commit, push** to master with `scripts/ledger.py add`,
   `scripts/run_tests.sh`, `scripts/ledger.py check`, then `git push origin master`.
   A failed push is reported once as "ledger commit unpushed" with the full
   entry text in the report, never retried in a loop.
4. **Time cap** of 15 minutes; past it the run writes a `partial` entry with a
   `next:` line and exits.

Requirements the Routine itself must satisfy (set in the Routine's settings,
not in this repository): the Gmail connector attached, and, for active patron
counts, `PATREON_ACCESS_TOKEN` as an environment variable. Without Gmail the
inbox skill writes an `aborted` entry and stops; without the token the growth
skill reports the supporter roll only.

Scratch files go in `tmp-build/` inside the checkout (git-ignored) and are
removed at the end of the run. Keep the two schedules from starting within the
same five minutes, since both push to master.

## Adding a new skill

1. Create `.claude/skills/<name>/SKILL.md` with `name`, a pushy `description`
   (what it does and every phrasing that should trigger it), and
   `metadata.version: "1.0"`.
2. Run `python3 scripts/ledger.py init --skill <name>`.
3. Give the skill a two-letter ref code and add it to the list above.
4. Make its final step the ledger entry plus the commit.
5. Run `python3 -m pytest tests/test_skill_ledgers.py` before committing.
