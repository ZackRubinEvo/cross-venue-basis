# Execution: legging, idempotence, and failure modes

## Legging order is the whole game

You cannot fill two venues atomically. Between the legs you are exposed, and
**the two half-done states are wildly asymmetric**:

    long the cheap leg only    -> max loss is the premium paid (cents)
    short the expensive leg only -> naked short, ~full contract value at risk

So always open the **long** leg first, and size the second leg to what the
first *actually filled*. Unwinding runs in reverse: close the short first, then
sell the long. The intermediate state is then always "long only", which is the
cheap state.

    ENTER: buy long leg  -> read fill -> sell short leg sized to the fill
    EXIT : buy back short -> read fill -> sell long leg sized to the fill

Firing both in parallel is about a second faster and can orphan either side.
That trade is not worth it. In one live incident, sequential ordering was the
only reason a failed second leg left a bounded long position instead of a naked
short roughly thirty times larger.

## When the second leg fails

A pre-flight probe is **not** the fix. Probing means opening the short first to
test whether it can fund — which is precisely the dangerous direction. Trading
a naked short to avoid a bounded long is not an improvement.

The fix is: if the second leg comes up short, **immediately flatten the first**,
paying one spread to get flat. Fall back to halting only if the flatten itself
fails.

## Idempotence across restarts

Any executor that recomputes signals from scratch on startup will re-fire on
every restart. Patching a file three times in ten minutes stacked a position to
three times its intended size while the log showed a single small execution.

Take a positions snapshot at the top of every cycle and skip anything already
held.

## Walk the book, always

Top-of-book pricing lies about anything larger than the touch. One position's
unwind priced at roughly ten times the position's value once the real ladder
was walked, because the visible best offer was three contracts deep and the
next real liquidity was far away.

This also protects you: a tool that walks the book prices a liquidity hole
honestly and will refuse to trade into it. A tool that trusts the touch will
happily fire.

## Exitability is a separate check from price

Containment guarantees you cannot lose at settlement. It says nothing about
being able to get out early. Before opening anything, walk the *exit* side for
the full intended size and refuse if the average price is unreasonable.

One pair had a perfectly healthy bid side, a normal-looking spread, and an ask
side of three contracts. Enterable, not exitable. That is a settlement hold
whether you intended one or not.

## Halt semantics

Two distinct states are worth separating:

    STOP   hard halt: exit, require human review before restarting
    PAUSE  soft hold: keep running, keep monitoring exits, open nothing new

Under a supervisor that restarts on failure, a deliberate halt must exit with
**success** status, or it will restart-loop against its own stop file.
