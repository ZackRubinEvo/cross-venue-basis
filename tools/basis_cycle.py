#!/usr/bin/env python3
"""
Cycle-time analysis for a cross-venue basis.

Answers: from a random entry point, how often does a profitable unwind appear
later, and how long does it take?

Venue-agnostic on purpose. It reads a JSONL of quote snapshots you produce
yourself; there is no exchange client here and no credentials.

INPUT  one JSON object per line:

    {"ts": 1788800000.0,
     "q": [{"pair": "some-id",
            "a_bid": 0.05, "a_ask": 0.06,     # venue A, the one you BUY
            "b_bid": 0.08, "b_ask": 0.09}]}   # venue B, the one you SELL

From those:

    entry = b_bid - a_ask      captured going IN
    exit  = b_ask - a_bid      PAID coming out   (higher is worse)
    a round trip pays when   entry(t0) - exit(t1) - fees > 0

WHY THE FILTERS EXIST. Both are load-bearing, and skipping either produces a
ranking that is not merely noisy but inverted:

  * --max-spread drops observations where either venue is quoting absurdly
    wide, which means one side of its book is empty. Those generate huge fake
    swings; without this the most PARKED instrument ranks as the most volatile.
  * distinct-value counting separates "moves continuously" from "sits at one
    number and occasionally jumps". Range and stdev cannot tell those apart. An
    instrument with four distinct quotes in 1,500 observations is a resting
    order, not a market.

    python3 basis_cycle.py quotes.jsonl
    python3 basis_cycle.py quotes.jsonl --fees 0.86 --max-spread 5
"""
import argparse, json, collections, statistics as st


def load(path, max_spread):
    per, kept, total = collections.defaultdict(list), 0, 0
    with open(path) as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = rec.get("ts")
            for q in rec.get("q", []):
                total += 1
                try:
                    ab, aa = float(q["a_bid"]), float(q["a_ask"])
                    bb, ba = float(q["b_bid"]), float(q["b_ask"])
                except (KeyError, TypeError, ValueError):
                    continue
                if (aa - ab) * 100 > max_spread or (ba - bb) * 100 > max_spread:
                    continue          # a side is empty; its mid is fiction
                kept += 1
                per[q["pair"]].append((ts, (bb - aa) * 100, (ba - ab) * 100))
    return per, kept, total


def cycle(series, fees):
    """For each entry point, minutes until an unwind would have paid."""
    waits, never = [], 0
    for i, (t0, entry, _) in enumerate(series):
        for t1, _, ex in series[i + 1:]:
            if entry - ex - fees > 0:
                waits.append((t1 - t0) / 60.0)
                break
        else:
            never += 1
    return waits, never


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path")
    p.add_argument("--fees", type=float, default=0.86,
                   help="round-trip cost in cents/contract (default 0.86)")
    p.add_argument("--max-spread", type=float, default=5.0,
                   help="drop quotes wider than this, in cents (default 5)")
    p.add_argument("--min-obs", type=int, default=100)
    a = p.parse_args()

    per, kept, total = load(a.path, a.max_spread)
    if not per:
        print("no usable quotes"); return
    print(f"{kept:,} clean quotes of {total:,} "
          f"({100 * (1 - kept / total):.0f}% dropped as empty-book)")
    print(f"fees {a.fees:.2f}c  max-spread {a.max_spread:.0f}c\n")
    print(f"{'pair':<24}{'obs':>7}{'distinct':>10}{'range':>8}"
          f"{'flip%':>8}{'median':>9}{'best':>8}")
    rows = []
    for pair, series in per.items():
        series.sort()
        if len(series) < a.min_obs:
            continue
        ex = [x[2] for x in series]
        waits, never = cycle(series, a.fees)
        tot = len(waits) + never
        rows.append((100 * len(waits) / tot if tot else 0, pair, len(series),
                     len(set(ex)), max(ex) - min(ex), waits))
    for pct, pair, n, distinct, rng, waits in sorted(rows, reverse=True):
        med = f"{st.median(waits):.0f}m" if waits else "-"
        best = f"{min(waits):.0f}m" if waits else "-"
        flag = "  <- parked?" if distinct <= 4 else ""
        print(f"{pair[:23]:<24}{n:>7}{distinct:>10}{rng:>7.1f}c"
              f"{pct:>7.0f}%{med:>9}{best:>8}{flag}")
    print("\nflip%   share of entry points from which an unwind later paid")
    print("median  typical wait to get there")
    print("distinct  how many different exit values were ever quoted;")
    print("          <=4 over a long window means a resting order, not a market")


if __name__ == "__main__":
    main()
