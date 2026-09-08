# Cross-venue basis trading: notes from a live experiment

Two prediction-market venues, Kalshi and Polymarket, list contracts on the same
underlying events. Their prices drift apart. This repo documents what happens
when you try to trade that gap, and — more usefully — the many ways the
measurement itself misleads you.

Written from roughly a week of live trading at small size. It is a field
report, not a strategy pitch. **The headline finding is that the opportunity is
real, small, and does not scale.**

## The two trades

**1. The locked arb (containment).** Some paired contracts settle on *different
oracles*. A Kalshi "will BTC touch $X" triggers on spot at any instant;
Polymarket's equivalent triggers on a 60-second trimmed mean. A trimmed mean
above X requires at least one print above X, so

    {Polymarket YES} ⊂ {Kalshi YES}

Buying Kalshi and selling Polymarket therefore cannot lose at settlement — in
every world where you owe on Poly, Kalshi pays you. Only that direction is
safe; the reverse loses on any wick that clears the strike without dragging the
mean along.

**2. The swing (basis mean-reversion).** The interesting one. The basis
oscillates. Buy the cheap side when the gap is wide, unwind when it narrows.
This needs no edge at entry, and — importantly — the basis never has to change
sign. See [docs/swing-thesis.md](docs/swing-thesis.md).

Where the two combine, you get a free roll: enter the containment-safe
direction, and if the basis never reverts you simply hold to settlement and
collect the locked spread instead. There is no losing branch, only an
opportunity-cost branch.

## What actually limits it

Not opportunity. Three other things:

- **Tick size.** Both venues quote in 1c increments with ~1c spreads, so a
  round trip costs about 2.9c before you start. A 1c gap can never survive one,
  no matter how perfectly it converges.
- **Fees scale as `p(1-p)`.** They vanish on longshots and peak at even money.
  So edge survives only where the price is *low* — which is also where the tick
  is the largest fraction of the price. The two constraints pull opposite ways.
- **Liquidity, separately from price.** Containment guarantees you cannot lose
  at settlement. It guarantees nothing about getting out early. One pair here
  had a healthy bid side and an ask side of three contracts, which made
  unwinding cost roughly ten times the position's value.

## Results, honestly

Over ~20 hours of clean measurement across 15 BTC pairs: the best pair offered
a profitable unwind from 73% of entry points with a median wait around 3.5
hours. **A third of the pairs never once became exitable** — one showed *two
distinct quotes* across 644 observations. Those are parked market makers, not
markets.

A parallel scan of 222 college-football pairs found the spreads *tighter* than
crypto, mostly below the round-trip cost.

## The measurement traps

These cost more time than the trading did, and they are the real content here.
See [docs/measurement-traps.md](docs/measurement-traps.md). Briefly:

1. **Empty books masquerade as volatility.** Raw spread ranges made the most
   *parked* pair look like the most volatile one. Filtering to real two-sided
   quotes inverted the entire ranking.
2. **Censored logs.** A log that records only *profitable* observations cannot
   answer "how often is it profitable".
3. **Sign conventions.** The cost of exiting reads like a profit if you are not
   careful. It is a toll.
4. **Silent pagination limits**, which produced confidently wrong universe
   sizes four separate times.

## Layout

    docs/containment.md        why one direction cannot lose, and the algebra
    docs/swing-thesis.md       basis mean-reversion, sign conventions, results
    docs/measurement-traps.md  every way the data lied
    docs/execution.md          legging, idempotence, failure modes
    tools/basis_cycle.py       the cycle-time analysis, venue-agnostic

## Scope

No credentials, no account data, no positions, no venue clients. The tool here
reads a generic JSONL of quote snapshots; wiring it to a venue is left out on
purpose.

Nothing here is financial advice. The author lost money to at least three of
the traps described.
