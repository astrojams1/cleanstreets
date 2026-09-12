# Triage policy

Category to action mapping for inbox-processor. Edit this file, not SKILL.md,
when James wants a category handled differently. Every change gets a dated
line under "Changes" at the bottom so the ledger and this file agree on why
behavior shifted.

## Current state flags

- `job_applications_open`: no (set by James; do not change without instruction)
- `service_waitlist_open`: yes (we take requests, James decides coverage)

## Policy table

| Category | Default action | Send allowed? | Why |
|---|---|---|---|
| `intake-form` | replied | yes | The form already captured their details; a fast, warm acknowledgment is the whole job. Work requests get the "next step is email, what's your block and availability" reply. |
| `patreon-notice` | archived + handoff | no reply | Patreon mail is machine-generated. The information matters to patreon-growth (new, declined, cancelled), so record a hand-off and archive. |
| `service-request` | replied | yes | Acknowledge, ask for block and cross streets and how often, explain the community-funded model. No pricing, no promise of coverage. |
| `partner-community` | drafted | no | Existing relationships carry history James knows and the skill may not. Draft a reply so he can send in one click. If the thread is purely informational (an FYI, a newsletter from a partner), archive instead. |
| `press` | flagged | never | Every word to a journalist is on the record. James answers press himself. |
| `vendor-pitch` | archived | no | No reply, no unsubscribe click (that confirms the address). |
| `automated` | archived | no | Receipts and notices need no action. Exception: security alerts and payment failures for Clean Streets accounts are flagged. |
| `job-application` | flagged (no reply) | only if `job_applications_open` is yes | Applications are closed; a kind "not hiring right now" reply is allowed only when James opens them. |
| `personal` | flagged | never | Not Clean Streets business. |
| `unknown` | flagged | never | Guessing wrong costs more than asking. |

Overrides that beat the table, in order:

0. James already starred it: never archive; flagged, with the decision it
   holds named in the report. (Found on the first test run, 2026-09-11: a
   grant-cohort notice was starred and would otherwise have been archived as
   informational.)
1. Angry, legal, or complaint language anywhere in the thread: flagged.
2. James already replied in the thread: noted, no action.
3. A reply from someone to a message a skill sent (ref code `CS-` in the quoted
   text): replied if it is a simple question the templates cover, otherwise
   drafted, and always mentioned in the report.
4. Send cap reached: drafted instead of replied.

## Signals that identify categories

- Intake form: subject contains `Get in touch`; body has the form fields
  ("I'm reaching out to...", "What services do you need?").
- Patreon: sender domain `patreon.com`; subjects like "You have a new patron",
  "payment declined", "has cancelled".
- Service request: mentions a block, corner, address, "how much", "can you
  clean", "our building", "our store".
- Partner/community: known domains (`refuserefusesf.org`, `missionlocal.org`,
  neighborhood associations, merchants already on the site's partner list).
- Press: `.org` or media domains plus "story", "interview", "quote",
  "deadline", "podcast".
- Vendor pitch: "SEO", "grow your", "quick call", "partnership opportunity"
  from an unknown domain, unsubscribe footers.

## Changes

- 2026-09-12: initial policy.
- 2026-09-11 (PT): added override 0, starred messages are never archived.
