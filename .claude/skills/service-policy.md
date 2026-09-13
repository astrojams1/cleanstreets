# Service policy: how a skill closes a lead on its own

The skills operate autonomously. When someone asks what Clean Streets
costs, whether it covers their block, or how to start, the skill answers
with the terms below and closes the deal in the same thread. Nothing here
waits on James. James changes these terms by editing this file; until he
does, these are the terms, and a quote given from this file is honored.

## What we sell

Paid sidewalk cleaning by the Clean Streets crew (independent contractors
paid a living-wage hourly rate, not volunteers and not employees) on a
fixed block or frontage in and around the Mission District, San Francisco. Litter, sweeping, and bagging on the sidewalk and
curb line. Not sold: large-item hauling (we report those to SF311), power
washing, graffiti removal, or anything inside a property line.

## Rates and plans

The public unit is the crew hour: **$40 funds one hour of paid cleaning**
(the figure on cleanstreets.io). Every plan is some number of hours per
week at that rate, billed monthly.

| Plan | Crew time | Monthly price |
|---|---|---|
| Weekly pass | 1 hour, once a week | $175 |
| Three days a week | 1 hour, three days a week | $520 |
| Daily (weekdays) | 1 hour every weekday | $865 |
| Daily, half hour | 30 minutes every weekday | $435 |
| One-time cleanup | 2 hours minimum | $80 |

Monthly prices are the hourly rate times 4.33 weeks, rounded to the
nearest $5. A custom schedule is priced the same way: hours per week ×
$40 × 4.33. Sponsors at $175/month and up are listed on the site's
supporters section and get a monthly note on what was done on their block.

## Coverage

The Mission District, and blocks within about ten minutes' walk of it
(Bernal north slope, the Hub around Market and Van Ness, Potrero west of
the freeway, Noe east of Castro). Farther than that: quote it anyway with
the same rates and say the start may take an extra week for routing.

## How to close

1. **Qualify in one reply**: the exact block or frontage (cross streets),
   how often, and when they'd like to start. If they already said, skip.
2. **Quote from the table**, in the thread, with the start date: crew
   starts within 7 days of payment for a monthly plan, within 3 days for
   a one-time cleanup.
3. **Take payment.** Default is a Patreon monthly pledge at the plan
   amount (`https://www.patreon.com/cleanstreets?ref=service`), which
   also lists them as a supporter. PayPal and Zelle are accepted too; ask
   which they prefer and give the details from the Payment section below.
   No invoices unless the payer's accounting requires one; then ledger
   `service:<slug> | invoice-needed | <amount> | <block>` so James sends it.
4. **Confirm** in one line once they pay or accept, with the first service
   day, and ledger `service:<slug> | closed | <monthly amount> | <block> |
   <start date>`. The crew schedule is James's to arrange; the ledger line
   is his notice.

## Handling objections

- Too expensive: offer the next plan down, or the half-hour daily; never
  a discount below the rate.
- Wants a walk-through or a call: say email is fastest and ask for the one
  fact the call was for (cross streets, a photo of the frontage).
- Asks about liability or a contract: the crew are independent contractors
  working for Clean Streets LLC; service is month to month, cancel any
  time by email. Do not claim insurance coverage; if they need a
  certificate of insurance or a signed agreement, say James will send what
  he has and ledger `service:<slug> | paperwork-needed | <what>`.

## Payment

| Method | Details | Notes |
|---|---|---|
| Patreon | `https://www.patreon.com/cleanstreets?ref=service`, custom pledge at the plan amount | Default; recurring; lists them as a supporter |
| PayPal | James to fill in the PayPal address here | One-time or monthly |
| Zelle | James to fill in the Zelle contact here | One-time or monthly |

Until the PayPal and Zelle lines are filled in, offer them by name and
say the details follow in a reply; ledger `service:<slug> | payment-details-needed`.
- Asks for a service we don't sell: say so plainly and offer what we do.

## Who to notify

James gets a line in the run report and the ledger when a deal closes or
an invoice is needed, and nothing before that. He is not asked to approve
a quote, choose a plan, or decide whether to take the work.

## Changes

- 2026-09-13: created after James's instruction that skills close leads
  themselves. Prices derived from the public $40-per-hour figure; James
  edits this table to change them.
- 2026-09-13: corrected per James: workers are independent contractors
  (not employees); payment is Patreon, PayPal, or Zelle, not invoices by
  default. No insurance claims.
