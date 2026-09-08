# Containment: why one direction cannot lose

## The setup

Two venues list what looks like the same contract but resolve it differently.
A concrete pair:

    Venue A: pays if the underlying TOUCHES $X at any instant
    Venue B: pays if a 60-second TRIMMED MEAN of the underlying exceeds $X

These are not the same event. And crucially, one contains the other.

## The argument

A trimmed mean above X requires at least one observation above X — you cannot
average above a threshold without any sample exceeding it. So:

    B pays  ⟹  some print exceeded X  ⟹  A pays

    {B YES} ⊂ {A YES}

Therefore **long A / short B cannot lose at settlement**:

| world | A | B | net |
|---|---|---|---|
| both resolve YES | +1 | −1 | 0, keep the spread |
| A YES, B NO | +1 | 0 | **+1** plus the spread |
| both NO | 0 | 0 | keep the spread |
| A NO, B YES | — | — | **impossible by containment** |

The losing row cannot occur. The reverse position — short A / long B — is
exactly the losing row, and it loses the full contract value on any spike that
clears the threshold without dragging the mean with it.

## Why cheapness is not the criterion

A tempting error: "B is trading above A, so sell B and buy A." That is correct
here, but only because containment happens to point the same way. If you pick
direction by price alone you will eventually take the naked side of a pair
whose containment runs the other way.

**Direction must be chosen by the settlement rules, never by which side looks
rich.** Read both rule texts. Every time.

## The identity that kills naive arbitrage

For pairs with genuinely *different* oracles and no containment relationship,
there is a general result worth internalising:

    cost ≡ E[payout]

The combined cost of the pair equals its expected payout exactly. So "the two
legs sum to less than $1" is **not** free money — it is compensation for the
states where the oracles disagree. You have not found an arbitrage; you have
found a correctly priced spread on oracle divergence.

Containment is what breaks this. It removes the losing state entirely, so cost
below $1 becomes genuinely locked.

## Estimating divergence probability

For a nested pair, the probability the two oracles disagree has a clean form:

    P(divergence at X) = P(A pays) − P(B pays) = A_fair − B_fair

i.e. the divergence probability *is* the fair-value gap. It can also be
computed structurally as

    (density of the running max at X) × (width of the smoothing band)

Both routes agreed at roughly 0.01–0.17 cents per contract on the pairs
measured, against 0.4–2.6 cents of fees. **Fees dominate divergence risk by
10–20x.** The naked direction is not blocked by oracle risk; it is blocked by
transaction costs.

One caveat that matters: that estimate was measured in calm conditions, and the
thresholds in question only get tested during violent moves — precisely when
the smoothing band is widest. The estimate is conditioned on the wrong regime.
Treat it as a lower bound.
