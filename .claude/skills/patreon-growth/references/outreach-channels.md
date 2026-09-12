# Outreach channels

Where new patrons come from, in the order to work them. Each channel has a
discovery method the run can execute, a template, a per-run quota, and a
kill signal. Evidence columns are updated every run from ledger data.

Ground rules that apply to every channel: the prior-correspondence check
(`from:<address> OR to:<address>`, any of our senders: james@, hello@,
jane@); at most 3 touches per contact ever (first touch, follow-up at
10 days or more, close-out at 21 days or more); never two contacts in one
run from the same household or business; no meetings proposed; no prices.

## Channel table

| # | Channel | Who | Discovery (how a run finds them) | Template | Quota per run | Evidence so far | Kill signal |
|---|---|---|---|---|---|---|---|
| 1 | Win-back | Former and declined patrons (82 former, per API; 17 have a resolvable email) | Patreon members API with `patron_status` and `last_charge_status`; sort former by lifetime support, declined by recency | win-back or declined-card | 3 | Run 0004 (2026-09-12): all 17 former patrons with an email already win-back'd by jane@/james@/hello@ March-July 2026; 0 sends possible, pool exhausted until new lapses | Reply rate under 5% over 30 sends |
| 2 | Referral | Active patrons never asked (26 active) | API list minus `patron:` ledger lines with `referral-asked` | referral ask | 2 | Run 0004: mass referral blast on 2026-06-29 already covered everyone who joined before that date; 1 send this run (Karen Hamrock, joined after the blast) | 0 attributed joins after all 26 asked and 30 days |
| 3 | Warm inbound | Anyone who ever wrote to james@ or hello@ and is not a patron: form submissions, "how do I help" notes, community threads, people who replied to past outreach | Gmail search `newer_than:2y -from:cleanstreets.io` for threads with a human reply; cross-check against the API member list by email | inbound lead | 3 | Historical: form and thread contacts converted at about 3% with 14-day lag; generic "thanks for your interest" got 0 replies, a specific block question got replies | Reply rate under 3% over 30 sends |
| 4 | Block merchants | Storefronts on blocks the crew cleans | Pick one block per run from `data/impact.csv` streets or the last Patreon post; web search `"<street> and <cross street>" San Francisco` plus directory sites for storefront names; find a public email on the business site; skip chains | merchant first touch, "we cleaned your block" | 3 | Historical: "we cleaned your block this week" from hello@ got warm replies from Black & Gold, Vive la Tarte, Heath Ceramics, VIP Grooming; sponsorship conversion 0 so far | Reply rate under 10% over 30 sends |
| 5 | Neighborhood groups | Block clubs, resident associations, Fix26-style lists, watch groups in the Mission | Web search `Mission District "neighborhood association" OR "block club" OR "residents" site:*.org OR groups.google.com`; SF Planning and SFPD community group lists | neighborhood peer | 2 | Historical: this frame had the best reply rate of any channel, about 30%, when it named a specific location and asked nothing in the first email | Reply rate under 10% over 20 sends |
| 6 | Property managers and HOAs | Buildings on cleaned blocks | Web search for the building's management company; contact the office email, never a resident | property first touch | 1 | Historical: low reply rate, occasional meeting requests (declined per policy) | Reply rate under 5% over 20 sends |
| 7 | Creator shifts | People in or near the Mission with a real local following (parents and family creators, neighborhood accounts, local food and lifestyle creators, newsletter writers), roughly 2,000+ followers | Web search: `"Mission District" San Francisco (mom OR dad OR family) (blogger OR creator OR influencer)`, `site:instagram.com "Mission District" San Francisco`, `site:tiktok.com "Mission District"`, local newsletters and Substacks, SF parent groups, Mission Local's contributors; confirm they live or work in or near the Mission from their own posts; contact only through an email on their bio, press page, or site (this skill sends no DMs) | creator shift offer | 2 | New channel (James's idea, 2026-09-11). No sends yet. | 0 acceptances after 20 sends |

Channel 7 is James's idea: pay a local creator the normal crew rate ($30 for
one hour of cleaning, paid the same day) in exchange for one post with a
before-and-after of what they did and their tracked Patreon link
(`?ref=creator-<slug>`). It costs nothing extra (the hour would be paid
anyway) and produces genuine local social content. The skill finds and
emails candidates and reports acceptances; James schedules the hour,
provides supplies, and pays. The offer email never promises anything beyond
$30 for one hour and the post; logistics come from James.

Total first touches per run at full quota: 16. Follow-ups and close-outs
are on top of that and always take priority over new first touches, because
the reply almost always comes on the second or third email.

## Per-run order of work

1. Follow-ups and close-outs due today (ledger `prospect:` lines whose last
   touch is 10 or 21 days old with no reply).
2. Replies to handle (any `prospect:` contact who wrote back: answer, and
   move them to `replied`; a join moves them to `converted`).
3. New first touches by channel order above until the send cap or the quotas
   are exhausted.

## What "moving the needle" means here

Net new active patrons per week is the number. Everything else (reply
rate, sends, prospects added) is diagnostic. With 26 active patrons, one
net new patron a week is 4% growth; that is the target for the first 60
days, and the channel mix should shift toward whichever channel produces
attributed joins.

## Retired levers

- On-site copy and button experiments (exp-002, exp-004, retired
  2026-09-11 on James's instruction: a couple dozen visitors a month
  cannot produce a readable signal). Ref codes on site links stay, as
  attribution infrastructure only.
- Cold pitches to journalists (0 replies on 6 sends, earlier in 2026).
