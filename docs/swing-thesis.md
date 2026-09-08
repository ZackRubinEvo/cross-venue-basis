# The swing thesis: basis mean-reversion

## The claim

Two venues list the same event. One is persistently a little cheaper. The gap
is not wide enough to arbitrage, but it *moves*. So: buy the cheap side when
the gap is wide, sell it back when the gap narrows. You are not betting on the
underlying. You are betting the gap reverts.

## What it does NOT require

**It does not require the basis to cross zero.** This is worth stating plainly
because it is the mistake I made first, and it wrongly disqualified more than
half the candidate pairs.

If venue A is *always* cheaper than venue B — say the basis oscillates between
+2c and +9c and never touches zero — that is still tradeable. Buy at +9, sell
at +3. The sign never flips. What matters is the **amplitude relative to the
round-trip cost**, nothing else.

A one-sided basis with 9c of swing is a better trade than a symmetric one with
2c of swing, even though only the latter "crosses zero".

## Sign conventions (get these right)

    entry = (venue B bid) - (venue A ask)     what you capture going IN
    exit  = (venue B ask) - (venue A bid)     what you PAY coming OUT

    profit = entry(t0) - exit(t1) - fees

**`exit` higher is worse.** It is a toll, not a gain. A bare "+3.0c" on the
exit side reads like profit and is exactly the opposite. Say "cost" out loud.

## The structural constant

Because both venues quote 1c spreads:

    exit ≈ entry + 2.0c

So an *instant* round trip always loses about 2.9c (two spreads plus fees), and
a profitable flip requires the whole basis to shift roughly 3c between entry
and exit. This is why tick size, not opportunity, is the binding constraint on
cheap contracts: a 1c gap on a 3c contract is 33% in relative terms and
completely untradeable in absolute terms.

## Direction asymmetry

Where the two venues settle on *different but nested* oracles (see
[containment.md](containment.md)), one direction is a free roll and the other
is naked:

    A: buy the superset venue, sell the subset venue
       -> if it never reverts, hold to settlement and collect the spread.
          No losing branch.
    B: the reverse
       -> if it never reverts, you can lose the full contract value.

Measured across 15 pairs, direction B fired 1-18% of the time on pairs where A
worked. The pairs where B worked well (53%) were precisely those where A never
worked. So enabling B means accepting the full downside exactly where the free
roll is unavailable. Not a good trade.

## Measured results

20 hours, 15 pairs, ~1,500 clean observations each. "flip%" is the share of
random entry points from which a profitable unwind later appeared.

| tier | flip% | median wait |
|---|---|---|
| best pair | 73% | 3.5h |
| good (5 pairs) | 43-53% | 3.5-5.5h |
| marginal (3) | 5-27% | varies |
| **parked (5)** | **0-1%** | never |

Two observations matter more than the table:

**The good pairs fire every few hours, not continuously.** Median waits of
210-330 minutes mean this is a handful of round trips per day at best, per
pair.

**A third of every family is parked.** Not slow — parked. One pair produced
*two distinct quotes* across 644 observations; another gave 279 consecutive
observations at a single value. Before believing any volatility number, count
distinct values. Four distinct quotes over a day is a market maker's resting
order, not a market.

## Where to hunt

Bigger universes are the obvious move, and cross-venue pairing is the
bottleneck. Matching contracts by their internal abbreviations failed badly
(21 of 240) because venues use different ones. Matching on **date plus
normalised entity name** got 222 of 240.

That said, the 222 sports pairs came back *tighter* than crypto — spreads
mostly below the round-trip cost, with 1 of 98 showing any flippable moment in
the first few hours. Caveat: those events had not started. Pre-event lines are
near-static; in-play is a different market and worth measuring separately
before drawing conclusions.
