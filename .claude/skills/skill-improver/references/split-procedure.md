# Splitting and merging skills

Read from SKILL.md Step 3c when a skill shows bloat signals. `skill_stats.py
stats` reports `skill_md_lines`, `steps`, `reference_lines`, and
`metric_keys` per skill so the signals are measured, not felt.

## Bloat signals (split when two or more hold across the last 5 runs)

- SKILL.md over 250 lines, or over 8 numbered steps, or references a run
  must read totaling over 600 lines.
- Two responsibilities with different natural cadences or inflows in one
  skill (an hourly sweep plus a weekly campaign; reactive mail plus
  scheduled outreach).
- `partial` entries from the time cap while the action list still had items.
- Half or more of the action list never appears in any `action |` detail
  line.
- Metric keys over 12, or metrics serving two unrelated north stars.

## Split procedure (one run, one commit)

1. Name the piece that leaves (the secondary responsibility): a skill name,
   a two-letter ref code, a cadence.
2. Create `.claude/skills/<new>/SKILL.md` per `.claude/skills/README.md`,
   moving the relevant steps, references, caps, and templates out of the
   parent verbatim where they are good. Then
   `python3 scripts/ledger.py init --skill <new>`.
3. Define the contract in both files: what the parent hands off (as
   `handoff:<new> | ...` ledger lines) and what the new skill reads (the
   parent's ledger, with the exact grep). No shared files other than ledgers.
4. Shrink the parent: remove what moved, bump its version, add a Changes line
   naming the new skill and the runs that justified the split.
5. Add the new skill to the README's ref-code list and Routines table. Run
   `python3 scripts/skill_stats.py lint` and `bash scripts/run_tests.sh`.
6. Create the Routine with the Claude Code Remote `create_trigger` tool when
   the session has it: fresh session per run; the README's "Routine prompt
   template" with the skill name filled in; the same connectors as the
   parent's Routine (Gmail if the skill touches mail); a cron in
   `CRON_TZ=America/Los_Angeles` staggered at least 5 minutes from every
   other Clean Streets Routine; push notifications on. Ledger it as
   `routine:<new> | created <trigger id> <cron>`. If the tool is absent or
   the call is denied, put the exact settings and prompt in the run report
   under "For James" and ledger `routine:<new> | needs James`. Never delete
   or modify an existing Routine.

## Merge rule

Two skills whose ledgers show the same hand-off bouncing between them every
run, or a skill under 40 lines averaging under one action per run, are
candidates to merge. Follow the procedure in reverse. Leave the retired
skill's ledger in place with a final entry pointing at the successor, and
ask James before any Routine is deleted.
