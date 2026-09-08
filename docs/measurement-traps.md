# Every way the data lied

These cost far more time than the trading did. Each one produced a confident,
wrong conclusion that survived until something forced a re-check.

## 1. Empty books masquerade as volatility

Ranking pairs by the raw range of their exit spread put the *most parked* pair
at the top with a 94-cent range. The pair had not moved all day.

What happened: when one side of a book empties, the best offer jumps to
something like 0.97. The computed spread swings wildly. It looks like
enormous volatility and is actually the absence of a market.

Filtering to observations where **both venues quote inside ~5c** inverted the
ranking completely. The "94c range" pair had a true range of **0.0c** — a
single quote, all day.

    if (a_ask - a_bid) > 0.05 or (b_ask - b_bid) > 0.05: skip

## 2. Zero-size levels are not prices

A quoted level with no size behind it is not tradeable. Including them produced
a phantom arbitrage — a set of mutually exclusive outcomes whose bids summed to
1.0154, which is free money if you can sell all of them. The largest leg had
*zero size*. The actually-sellable subset summed to 0.42.

And the obvious filter is not enough:

    if size > 0:        # WRONG: 0.04 passes, then renders as "0.0"
    if round(size,1)>0: # round FIRST, then filter

## 3. Censored logs cannot answer frequency questions

The original scanner logged only observations where the edge was *positive*.
Asking "how often does an edge appear?" of that log is unanswerable — every
interval where it went negative is simply absent. The first cycle-time estimate
was built on it and was biased in a direction that could not be corrected.

The fix was a second recorder that logs **both spreads, both signs, every pair,
every pass**, whether or not anything is actionable. Rebuild the analysis on
that and the answers change materially.

**Log the state, not the signal.**

## 4. Distinct-value counts expose parked quotes

A pair with a 5-cent range across 1,474 observations sounds tradeable. That
pair had **four distinct values**. Another had two across 644 observations.

Range and standard deviation both fail to distinguish "moves continuously
within 5c" from "sits at one number and occasionally jumps". Counting distinct
values separates them instantly. Add it to every volatility table.

## 5. Silent pagination limits

Four separate times, a default page size or an offset guard truncated a market
universe and produced a confidently wrong count — off by an order of magnitude
in one case. Each wrong count led to a wrong strategic conclusion ("this
universe is exhausted", "there is nothing else to pair").

Always paginate to exhaustion, then assert the result is plausible. And verify
the offset parameter is actually respected — one endpoint accepted it and
returned the same page regardless.

## 6. Cumulative fields are not cost bases

A position's "total traded" field accumulates **buys and sells**. It equals the
cost basis right up until the first partial close, then silently inflates:

    after a 2-of-31 partial unwind:
      total_traded / qty      = 0.1997   wrong
      market_exposure / qty   = 0.1300   correct

Because nothing had ever been partially closed before, the wrong field had been
correct for the entire history of the system. The bug appeared only on the
first partial fill, and presented as a position mysteriously showing a loss.

## 7. Order responses that cannot report failure

On one venue, a *filled* immediate-or-cancel order and an order rejected for
insufficient collateral return byte-for-byte identical responses: HTTP 200, an
order id, and an empty executions array. There is no field that distinguishes
them.

The only ground truth is whether the position changed. Read positions before
and after, and compare **deltas** — absolute counts are wrong whenever you
already hold some of the pair.

An earlier version of this trusted the response and reported "you are naked"
when the hedge was in fact complete. Acting on that would have unwound a good
position.

## 8. Running processes hold stale code

Not a data trap, but it corrupted data three times. Editing source does nothing
to an already-running daemon. Symptoms were, in order: a control that silently
did nothing, a recorder that logged 3 snapshots instead of 1,900, and a
dashboard that reported a stale cost basis for hours after the underlying fix.

The third was the worst because two components disagreed and both looked
plausible. Restart everything after any edit, and mind the import graph — one
module goes stale in several processes at once.
