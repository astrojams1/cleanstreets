# Experiment registry

At most 3 `running` at once. Every experiment has one variable, a ref code,
a window, a success threshold, and a kill criterion decided before it starts.
Decisions are made in Step 2 of the skill and never deferred.

Statuses: `proposed`, `running`, `won`, `lost`, `inconclusive`.

| ID | Started | Window | Change (one variable) | Ref code | Success | Kill | Status | Result |
|---|---|---|---|---|---|---|---|---|
| exp-001 | | 14d | Add `?ref=` codes to every Patreon link on the site (hero, nav, mobile, footer, JSON-LD). Not a copy change; it makes later experiments measurable. | site-* | Attribution coverage of new joins rises above 0 | n/a (infrastructure) | proposed | |
| exp-002 | | 14d | Hero subline: replace "Chip in what you can." with "$5/month keeps a corner clean for 7 minutes a day." | exp-002 | Joins via site-hero in window ≥ prior 14d joins + 1 | 0 joins in window with ≥ 1 join in prior window | proposed | |
| exp-003 | | 30d | Referral line at the end of the monthly Patreon post | post-yyyymm | ≥ 1 join attributed to a referral slug | 0 referral joins after 2 posts | proposed | |

## Log

- 2026-09-12: registry created with three proposals; nothing running yet.
