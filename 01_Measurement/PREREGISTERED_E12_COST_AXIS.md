# PREREGISTERED E12 — THE IN-SITU COST AXIS OF THE FALL FRONT

**Registered 2026-09-11, before any number in it is recomputed.**
Registers a defect that was found, a reporting rule that answers it, and the
limits of the answer. It does **not** register a result.

Prior registrations this one is subordinate to and does not amend:
`PREREGISTERED_M3.md` (grids, samples, allocation roster),
`PREREGISTERED_E7B_AMENDMENT.md` §2 (which pass the in-situ Fall curve is built
from), `PREREGISTERED_E7D.md`, `PREREGISTERED_M3_ERRATA.md`.

---

## 1. THE DEFECT, IN NUMBERS

The allocation in `scripts/theta_vs_lambda.py` prices the FallChecker front on
an in-situ alert rate. On 2026-09-11 that rate was traced to its segments for
the first time. What was found, stated as counts and not as an impression:

| θ | alerts | segments carrying them | of how many | Poisson 95% | **segment block bootstrap 95%** |
|---:|---:|---:|---:|---|---|
| 0.30 | 51 | 3 | 8 | [9.51, 16.80] | **[0.50, 28.81]** |
| 0.45 | 16 | **1** | 8 | [2.29, 6.51] | **[0.00, 12.08]**, and **33.9 %** of resamples give exactly 0 |
| 0.60 | 0 | 0 | 8 | [0.00, 0.92] | [0.00, 0.00] |

Three facts follow, and each is a fact about the sample, not a judgement:

1. **At the deployed operating point θ = 0.45, one segment carries every
   alert.** `HOM_20260831_0800`, 0.4919 h of 3.9914 h.
2. **That segment is the only one of the eight on the substituted clock**
   (HARNESS-5, damaged H.264 container timing). It is 12.3 % of the sample's
   hours and 100 % of its fall alerts.
3. **The interval that respects the clustering contains zero.** A budget
   threshold placed at 4.009 alerts/h is not separable from one placed at
   12.777 alerts/h on this evidence.

**A fourth fact, about the code rather than the data, and it is registered here
because it changes what "the registered axis" even refers to.**
`PREREGISTERED_E7B_AMENDMENT.md` §2 selects **C1** (24 segments, recorded
θ = 0.30, detector conf 0.15) as the pass the in-situ Fall curve is built from,
under E7 §3's tie-break *"use the pass whose recorded θ is lowest, because
rescoring is only valid upward."* `theta_vs_lambda.py` states in its own source
comment that it prices on **V1/V2/V3, the eight-segment verification sample**.
Those are not the same pass and not the same denominator. Whether the numbers
coincide is **not asserted here and is not known at the time of hashing**; §4
step 2 is where it gets checked.

*(Provenance of the table: `analysis/FALL_FRONT_PROVENANCE.json`, written by
`scripts/fall_front_provenance.py`, seed 20260911, 20000 replicates, run
2026-09-11 before this file existed. No number in it is recomputed by this
registration.)*

---

## 2. WHY A SILENT SWITCH TO A1 IS FORBIDDEN

A1 (175 segments, 83.9626 h) yields an exact FAR(θ) at three grid points and
would give a cost axis with 150 alert events behind it instead of 16. It is the
better-resolved axis and this registration does not pretend otherwise.

**But the selection rule was registered in advance, and it selects C1.** Moving
to A1 *after* seeing that the registered choice produced a degenerate interval
is changing the selection rule after seeing the result. That is the defect this
campaign exists to report, and committing it in the act of reporting it would
cost more than the better interval buys.

**The author's decision page of 2026-09-11 morning proposed exactly that switch
and is therefore withdrawn.** It is superseded by whatever §4 produces.

---

## 3. THE REPORTING RULE — REGISTERED BEFORE THE NUMBERS ARE RECOMPUTED

**Both fronts are printed. A1 is ADDED, never SUBSTITUTED.**

1. **The registered front (C1) is printed first**, with its interval, **and the
   interval is printed even where it is degenerate.** A bootstrap interval
   containing zero appears in the table as an interval containing zero. It is
   not replaced by a Poisson interval, not footnoted away, not omitted for
   width.
2. **The A1 front is printed beside it**, labelled as what it is: a second
   in-situ cost axis on the whole corpus, at the three grid points A1's recorded
   threshold makes exact, introduced *because* the registered front did not
   resolve — and that reason is printed too.
3. **Neither front is presented as correcting the other.** The reader is told
   what the registered rule delivered and what a second pass delivers, and the
   gap between them is the finding.
4. **If the two fronts select different operating points at some budget, that
   disagreement is reported as a result**, not resolved by preferring one.

### 3a. Which branch this registration is prepared to publish

Written before the recomputation, both ways, so that neither is chosen after
the fact:

- **Branch 1 — the two fronts agree on the selected θ at every budget.** Then
  the allocation statement is unchanged and the C1 interval is reported as a
  precision limit, not a threat to the ordering.
- **Branch 2 — they disagree at some budget.** Then the paper reports that the
  selected operating point depends on which in-situ pass prices it, prints both,
  and **does not name a single allocated θ** for the budgets where they differ.
  §IV-D says so in those words.

---

## 4. THE θ RANGE EACH AXIS CAN PRICE — AND WHERE THE TABLE MUST HAVE A HOLE

`PREREGISTERED_E7B_AMENDMENT.md` §2b establishes that A1 recorded FallChecker at
exactly the deployed literal 0.45, and that every A1 alert's confidence decides
its fate at higher θ exactly. Therefore:

| θ | C1 (registered) | **A1** |
|---:|---|---|
| 0.300 | priced | **UNREACHABLE** — below A1's recorded threshold |
| 0.375 | priced | **UNREACHABLE** — same reason |
| 0.450 | priced | exact, 175 segments |
| 0.525 | priced | exact, 175 segments |
| 0.600 | priced | exact, 175 segments |

**The hole is printed as a hole.** The A1 column carries no entry at 0.30 and
0.375 — not an interpolation, not a bound, not a dash that could be read as
zero. E7-d already set this precedent for a different gap and the same wording
is reused: a grid point that a pass cannot price is named as unreachable and the
reason is given.

**Consequence for the high-coverage end.** Coverage 0.6282 sits at θ = 0.30,
which only C1 prices. So the most attractive end of the front is priced **only**
by the axis with the degenerate interval. That is not a presentational problem
and must not be presented as one.

---

## 5. ORDER OF OPERATIONS — BINDING

1. This file is hashed. Its SHA256 goes in `GT_PROTOCOL` §11 and in
   `PREREGISTERED_E12_COST_AXIS.sha256`.
2. **Only then** are the C1 and A1 fronts computed.
3. `scripts/fall_front_provenance.py` is **not run again before step 1**.
4. The output of step 2 is reported **whichever branch of §3a it falls in**, on
   the same day it is computed.
5. `THETA_DECISION` is rewritten from step 2's output. The 2026-09-11 morning
   version is withdrawn and is not shown to the author for signature.

---

## 6. WHAT THIS REGISTRATION DOES NOT DO

- It does **not** claim the substituted-clock segment is invalid. E4's
  pre-registered test found the substituted stratum indistinguishable from the
  native stratum **corpus-wide**, and that result stands. This registration says
  something narrower: in a sample of eight, that stratum is the sole
  contributor, so the corpus-wide pooling result does not transfer to it.
- It does **not** re-open the allocation roster. Intrusion stays out by
  `PREREGISTERED_M3`; SmokeFire stays uncharacterised by E9; Running stays as
  E9/E10 left it.
- It does **not** license a third pass. If C1 and A1 both fail to resolve the
  axis, the paper reports an unresolved cost axis. It does not go shopping.
