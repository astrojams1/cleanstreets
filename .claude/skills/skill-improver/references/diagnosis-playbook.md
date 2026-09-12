# Diagnosis playbook

Ledger patterns and the fix that has worked for each. Update the "Worked" and
"Did not work" columns every run from the `verdict:` lines. Add a row when a
new pattern appears twice.

## Patterns and fixes

| Pattern in the ledger | Likely cause | Fix in the skill | Worked | Did not work |
|---|---|---|---|---|
| Same `next:` line on 2+ consecutive runs | The next-run action depends on something the skill cannot do (a token, a connector, a decision) | Move the item to an `env` or `proposal` line for James; remove it from `next:` | | |
| `aborted` with the same reason on 2+ runs | Environment (wrong Gmail account, no connector, no checkout) | No skill edit. Report the exact fix for James. If the skill wastes work before the guard fires, move the guard earlier | | |
| `partial` from the time cap on 2+ runs | Scope too large per run | Lower per-run caps (items processed, actions), or split a step into a reference the run reads only when needed | | |
| `noop` on most runs | Cadence faster than the inflow | Propose a slower Routine schedule; add an early-exit check before any expensive step | | |
| Zero-action `success` runs | Skill treats measuring or research as the deliverable | Restate the minimum action count at the top of the Execute step; list concrete fallback actions that are always available | | |
| Required metric missing from entries | The ledger command in SKILL.md is long and runs paraphrase it | Give the exact command in one block near the end; name each metric once; add a sentence on why the metric matters | | |
| Detail lines with personal data (test catches these) | Privacy rule buried | Put the privacy line inside the ledger step itself, next to the command | | |
| High `flagged` share for a processing skill | Policy has no row for a common category | Add the category and default action to the policy file, with the signals that identify it | | |
| High `drafted`, near-zero `replied` | Reply templates need facts the run lacks | Add the facts to the template file or reclassify the category as draft-only and say so | | |
| Metric flat while actions are being taken | Actions aren't the ones that move the metric | Reorder the action list; retire actions that never attributed; promote an experiment from the backlog | | |
| `error` detail lines naming a tool | Tool name or argument shape drift | Describe the operation, not the tool name, and note the shape that worked in the ledger | | |
| Lint: path does not exist | Junk or drift from another tool or a rename | Delete the reference or point it at the real file | | |
| Lint: SKILL.md over budget | Accreted instructions | Move detail to references; delete steps no run has exercised in 10 runs | | |
| Hand-offs emitted but never consumed | Consumer skill doesn't read the producer's ledger | Add the read to the consumer's Measure or Sweep step with the exact grep | | |
| Two or more bloat signals over 5 runs (size, mixed cadences, time-cap partials with actions left, unused actions, too many metrics) | One skill carrying two jobs | Split per SKILL.md Step 3c: new skill, ledger, hand-off contract, README rows, Routine | | |
| A sweep or search misses items that were handled elsewhere (archived, labeled, read) | Query filters on mailbox state instead of the ledger | Remove the state filter; the ledger is the only dedup gate (inbox-processor v1.1, 2026-09-11) | | |

## Facts about this repository the reviewer should know

- Ledgers are public (the site deploys from this repository). The
  privacy rule in `.claude/skills/README.md` is a guardrail: tighten only.
- The site's Patreon links are ref-coded as of 2026-09-11 (patreon-growth
  exp-001). Attribution only works if those codes survive later site edits.
- `data/supporters.csv` and `data/impact.csv` are regenerated daily by a
  GitHub Action from a Google Sheet. Skills read them; nothing here writes
  them. If impact rows stop appearing, that is a James finding, not a skill
  bug.
- The Routines that run the skills are configured outside this repository.
  The connector list and environment variables on a Routine are environment
  findings.

## History

- 2026-09-12: playbook created with the first run of skill-improver. No
  verdicts yet; every "Worked" cell is empty until an edit has been observed
  across at least two later runs of the target skill.
