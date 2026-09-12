# Experiment registry

At most 3 `running` at once. Every experiment has one variable, a window, a
success threshold, and a kill criterion decided before it starts. Decisions
are made in Step 2 of the skill and never deferred. Since 2026-09-11,
experiments are about outreach (who we contact, what we say, when we follow
up), not the website.

Statuses: `proposed`, `running`, `won`, `lost`, `inconclusive`, `retired`.

## The bar an experiment must clear (James, 2026-09-11)

The creator shift is the model: pay a local creator the normal crew rate
for one hour of cleaning, get a before-and-after post with a tracked link.
An experiment qualifies when all four hold:

1. **It reaches people we don't already reach.** New eyes, not a better
   pitch to the same two dozen site visitors.
2. **It spends an asset we already have.** Paid crew hours, the crew's
   presence on a block, existing patrons' goodwill, James's inbox history.
   Extra cash is a last resort; extra attention is the point.
3. **It produces a measurable channel.** Every path to Patreon carries its
   own `?ref=`, so joins can be counted per experiment within 30 days.
4. **It scales if it works.** One creator becomes ten; one merchant window
   becomes a block.

Not experiments, whatever they are called: website copy, buttons,
layout, colors, and anything else whose audience is the site's own
traffic. Those were tried (exp-002, exp-004) and retired.

Ideas that clear the bar, for the skill to promote one at a time:

- Parent-creator shifts via the Mission Parents list (1,000 to 2,000
  members): one note offering the paid hour and post.
- School and PTA cleanup hour: a Mission school's parent group takes an
  hour on their own block at the crew rate, posts to their families.
- Merchant window card: a small sign with a QR code and `?ref=window-<slug>`
  for merchants who replied warmly; measures foot-traffic conversion.
- Patron-hosted hour: an existing patron invites two neighbors to join a
  paid hour with the crew; each gets a referral link.
- Crew before-and-after posts on Nextdoor and Instagram with block names and
  `?ref=social-<platform>`, weekly, measured like any other channel.

| ID | Started | Window | Change (one variable) | Ref code | Success | Kill | Status | Result |
|---|---|---|---|---|---|---|---|---|
| exp-001 | 2026-09-11 | infra | `?ref=` codes on every Patreon link on the site, so any join can be attributed | site-* | n/a | n/a | running | Infrastructure; keep |
| exp-002 | 2026-09-11 | 14d | Hero subline copy | exp-002 | | | retired | Reverted 2026-09-11: site traffic too low to measure (James) |
| exp-003 | | 30d | Referral line at the end of the monthly Patreon post | post-yyyymm | ≥ 1 join attributed to a referral slug | 0 referral joins after 2 posts | proposed | |
| exp-004 | 2026-09-11 | 14d | Button below the impact grid | exp-004 | | | retired | Reverted 2026-09-11: same reason as exp-002 |
| exp-005 | | 30d | Win-back subject line: "Your Clean Streets pledge" vs "Checking in from Clean Streets" (alternate by send) | reengage | Reply rate difference ≥ 10 points over 20 sends each | Both under 5% | proposed | |
| exp-006 | | 30d | Merchant first touch: "we cleaned your block this week" (specific, dated) vs generic introduction | merchant | Specific frame wins on reply rate over 15 sends each | Both under 10% | proposed | |
| exp-007 | | 45d | Referral ask to active patrons: with a concrete "one neighbor on your block" line vs plain link | referral-<slug> | ≥ 1 attributed join | 0 joins after all 26 asked | proposed | |
| exp-008 | | 60d | Creator shifts: paid hour of cleaning for a before-and-after post with a tracked link (channel 7) | creator-<slug> | ≥ 1 attributed join per 3 completed shifts, or ≥ 2,000 post reach per shift | 0 acceptances after 20 offers | proposed | James's model experiment |

## Log

- 2026-09-12: registry created with three proposals; nothing running yet.
- 2026-09-11 (PT), run 0001: exp-001 started (site links ref-coded).
- 2026-09-11 (PT), run 0002: exp-002 started. run 0003: exp-004 started.
- 2026-09-11 (PT): exp-002 and exp-004 retired and reverted on James's
  instruction; the skill's experiments now target outreach channels and copy
  (exp-005 to exp-007 proposed).
