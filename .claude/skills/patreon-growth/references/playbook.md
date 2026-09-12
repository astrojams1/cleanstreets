# Patreon growth playbook

The living record of what moves active patron count for Clean Streets.
Updated every run in Step 2. Keep it short and current; retired tactics move
to the bottom with the reason. Per-run narrative belongs in the ledger, not
here.

## Facts to build on

- Clean Streets is an LLC, not a 501(c)(3). No tax-deductible framing, no
  donation platforms that require charity status.
- $40 funds one hour of paid cleaning. $5/month is the entry tier. These are
  the concrete-outcome anchors ($5 → 7.5 minutes a month).
- Baseline 2026-09-11 (API): 26 active patrons, $1,111/month, 82 former
  patrons, 114 members ever. The former-patron pool is three times the
  active one; win-back is the largest single channel.
- Impact totals come from `data/impact.csv`; no rows after 2026-07-07 as of
  this writing (a James finding, not a skill bug).
- Patreon page: `https://www.patreon.com/cleanstreets`. Site buttons use the
  checkout path with a `?ref=`; the JSON-LD `sameAs` is the bare profile
  URL. The public page returns 403 to anonymous fetches; counts come from
  the API via `scripts/patreon_stats.py` (token through 1Password, vault
  `API Tokens`).
- Mission Local profiled Clean Streets in 2021; best third-party link.
- **Other senders exist.** An older system emailed patrons and prospects
  from `jane@cleanstreets.io` and `hello@cleanstreets.io` through summer
  2026 (win-back, referral asks, merchant and neighborhood outreach). None
  of it is in this ledger. The prior-correspondence check must search the
  contact's address regardless of which of our addresses sent, and it
  caught five duplicates on 2026-09-11 before any send.
- The website gets a couple dozen visitors a month. It cannot produce a
  readable experiment signal and is not a growth lever (James, 2026-09-11).

## Ref-code registry

Every Patreon link we put anywhere: `https://www.patreon.com/cleanstreets?ref=<source>`.

| Source | Used for |
|---|---|
| `site-hero`, `site-nav`, `site-mobile`, `site-footer`, `schema` | Site links (attribution only) |
| `inbox-<category>` | Replies sent by inbox-processor |
| `referral-<slug>` | A patron's personal referral link |
| `welcome` | Links in welcome emails other than the referral link |
| `reengage` | Win-back emails (channel 1) |
| `inbound` | Warm inbound leads (channel 3) |
| `merchant` | Block merchants (channel 4) |
| `neighborhood` | Neighborhood groups (channel 5) |
| `property` | Property managers and HOAs (channel 6) |
| `post-<yyyymm>` | Monthly impact update post |
| `exp-<id>` | An experiment; one code per experiment |
| `organic` | Attribution fallback when nothing matches |

Add a row before using a new code. Never reuse an experiment code.

## What works (keep doing)

- Location-specific, dated, low-ask openers ("we were on 24th between
  Valencia and Guerrero on Tuesday") get replies; generic gratitude and
  generic introductions do not.
- The neighborhood-peer frame with zero ask in the first email had the best
  reply rate of any channel (about 30%) in the older system.
- Warm inbound leads (form submissions, thread contacts) convert at a few
  percent with a two-week lag; cold lists do not.
- Welcomes that name the concrete outcome, include a personal referral link,
  and ask one attribution question.
- The second and third touch produce most replies; first touches alone
  rarely do.

## What does not work (do not repeat without new evidence)

- Cold-emailing journalists: six pitches, zero replies.
- Generic "support us" asks with no outcome attached.
- Site copy and button changes (retired 2026-09-11).
- Anything requiring James to attend an event or take a call to close.

## Backlog of ideas (promote into experiments.md one at a time)

- Block sponsorship one-pager for merchants: what $200/month covers on their
  block, in their words.
- "Supporter of the month" mention in the monthly post to reward referrers.
- A referral line at the end of the monthly Patreon post (exp-003).
- Ask the three most engaged current patrons (by reply history) for one
  warm introduction each to a business owner they know on the route.

## Retired

- exp-002 hero subline and exp-004 impact-grid button: reverted
  2026-09-11; traffic too low to measure and not the kind of growth James
  wants.
