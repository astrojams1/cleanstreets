# Experiment registry

At most 3 `running` at once. Every experiment has one variable, a ref code,
a window, a success threshold, and a kill criterion decided before it starts.
Decisions are made in Step 2 of the skill and never deferred.

Statuses: `proposed`, `running`, `won`, `lost`, `inconclusive`.

| ID | Started | Window | Change (one variable) | Ref code | Success | Kill | Status | Result |
|---|---|---|---|---|---|---|---|---|
| exp-001 | 2026-09-11 | 14d (decide 2026-09-25) | Add `?ref=` codes to every Patreon link on the site (hero, nav, mobile, footer, JSON-LD). Not a copy change; it makes later experiments measurable. | site-* | Attribution coverage of new joins rises above 0 | n/a (infrastructure) | running | |
| exp-002 | 2026-09-12 | 14d (decide 2026-09-26) | Hero subline: replace "Chip in what you can." with "$5 a month funds 7.5 minutes of paid cleanup." | exp-002 | Joins via hero CTA in window ≥ prior 14d joins + 1 | 0 joins in window with ≥ 1 join in prior window | running | |
| exp-003 | | 30d | Referral line at the end of the monthly Patreon post | post-yyyymm | ≥ 1 join attributed to a referral slug | 0 referral joins after 2 posts | proposed | |

## Log

- 2026-09-12: registry created with three proposals; nothing running yet.
- 2026-09-11 (PT), run 0001: exp-001 started (site links ref-coded on the working branch; live once merged to master). exp-002 wording corrected: $5 at $40/hour is 7.5 minutes per month, the earlier text said per day.
- 2026-09-12 (PT), run 0002: exp-002 started. Hero subline swapped to "$5 a month funds 7.5 minutes of paid cleanup."; hero CTA ref switched from `site-hero` to `exp-002` for the window so joins attribute to the variant. Decide 2026-09-26.
