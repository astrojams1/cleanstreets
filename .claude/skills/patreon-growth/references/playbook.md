# Patreon growth playbook

The living record of what moves active patron count for Clean Streets.
Updated every run in Step 2. Keep it short and current; retired tactics move
to the bottom with the reason they were retired.

## Facts to build on

- Clean Streets is an LLC, not a 501(c)(3). No tax-deductible framing, no
  donation platforms that require charity status.
- $40 funds one hour of paid cleaning (site copy). $5/month is the entry tier
  mentioned on the site. Use these as the concrete-outcome anchors.
- Impact totals come from `data/impact.csv` (hours funded, pounds removed,
  miles cleaned). The site shows the running totals.
- Patreon page: `https://www.patreon.com/cleanstreets`. On-site buttons use
  the checkout path `https://www.patreon.com/join/cleanstreets?ref=<source>`
  (it lands on the pledge flow, not the profile); the JSON-LD `sameAs` entry
  is the bare profile URL because it states identity, not a call to action.
  Ref codes were added to every on-site link on 2026-09-11 (exp-001).
- The public Patreon page returns 403 to unauthenticated fetches, so the
  active patron count needs the API token; without it the skill reports the
  supporter roll only.
- Mission Local profiled Clean Streets in 2021; that article is the best
  third-party credibility link.

## Ref-code registry

Every Patreon link we put anywhere: `https://www.patreon.com/cleanstreets?ref=<source>`.

| Source | Used for |
|---|---|
| `site-hero` | Hero "Fund the workforce" button |
| `site-nav` | Desktop nav Donate button |
| `site-mobile` | Mobile menu Donate button |
| `site-footer` | Footer Patreon link |
| `schema` | JSON-LD potentialAction target |
| `inbox-<category>` | Replies sent by inbox-processor |
| `referral-<slug>` | A patron's personal referral link (slug: first name + last initial, lowercase) |
| `welcome` | Links in welcome emails other than the referral link |
| `reengage` | Lapsed-patron emails |
| `post-<yyyymm>` | Monthly impact update post |
| `exp-<id>` | A site experiment; one code per experiment |
| `organic` | Attribution fallback when nothing matches |

Add a row before using a new code. Never reuse an experiment code.

## What works (keep doing)

- Welcome emails that name the concrete outcome, include a personal referral
  link, and ask one attribution question. Short (five sentences or fewer).
- Location-specific, low-ask openers ("which corner always looks worst?")
  get replies where generic gratitude does not.
- Leads that came in warm (form submissions, community threads) convert;
  cold lists do not.

## What does not work (do not repeat without new evidence)

- Cold-emailing journalists: six pitches, zero replies. Press comes through
  warm intros or when a reporter asks first.
- Generic "support us" asks with no outcome attached.
- Anything requiring James to attend an event or take a call to close.

## Backlog of ideas (promote into experiments.md one at a time)

- Add a "$5 = 7.5 minutes of cleaning" line under the entry-tier mention.
- A short "Where your money goes" strip near the hero with the three impact
  numbers and a ref-coded button.
- A referral line in the monthly Patreon post ("forward this to one neighbor").
- Block sponsorship one-pager for merchants: what $200/month covers on their
  block, in their words.
- A "supporter of the month" mention in the post to reward referrers.

## Retired

(none yet)
