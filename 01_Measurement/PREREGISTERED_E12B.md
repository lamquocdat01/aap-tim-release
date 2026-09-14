# PREREGISTERED E12-b — THE REGISTERED COST AXIS IS EMPTY, AND THERE ARE THREE AXES

**Registered 2026-09-12, before one sentence about the three axes is written
into the manuscript, `THETA_DECISION`, or any figure.**

`PREREGISTERED_E12_COST_AXIS.md` is **not amended**. Its hash
`c36865afb79f42d58fd4ac68fe0058c073e48dd3b7287708cb76298529c03b90`, locked
2026-09-11T16:01:48+07, is unchanged and stays the file of record for what was
registered before the recomputation. This file registers only what E12's
reporting rule does not reach, and it is written the same way E7-b, E7-c, E7-d
and E10-b were: a new registration with its own hash, the superseded reasoning
kept intact beside it.

Prior registrations this one is subordinate to and does not amend:
`PREREGISTERED_M3.md`, `PREREGISTERED_E7B_AMENDMENT.md` §2,
`PREREGISTERED_E7C.md`, `PREREGISTERED_E7D.md`,
`PREREGISTERED_E12_COST_AXIS.md`, `PREREGISTERED_M3_ERRATA.md`.

---

## 0. THE QUESTION THIS FILE EXISTS TO ANSWER, AND THE ANSWER

E12 §5 step 2 was executed on 2026-09-11 after the lock.
`scripts/e12_cost_axis.py` (seed 20260911, 20 000 replicates) wrote
`analysis/e12/E12_COST_AXIS.json`. The question put to E12 before anything was
written into the paper was:

> **Does E12 §3's two-sided reporting rule cover the configuration that step 2
> actually produced?**

**It does not.** Three specific clauses fail, and each fails for a reason E12
states it did not know at the time of hashing. They are listed in §1 with the
clause each one falls outside. Nothing in E12 is called wrong: E12 registered a
rule for the configuration it could foresee, and the configuration is not that
one.

---

## 1. WHAT STEP 2 PRODUCED, AND THE THREE CLAUSES IT FALLS OUTSIDE

| axis | pass | what it emitted |
|---|---|---|
| **C1 → C2** | the axis **the registered rule selects** (E7 §3 tie-break, lowest recorded θ) | **0 points.** `runs/c2/sweep_curve.json` emits no point at any θ |
| **V1/V2/V3** | 8 segments, 3.9914 h — **not registered, and what the code prices on** | 3 points, degenerate at the deployed θ |
| **A1** | 175 segments, 83.9626 h | 3 points, non-degenerate; 2 grid points unreachable |

### Gap 1 — E12 §3.1 has no rule for an axis that emits nothing

§3.1 registers: *"The registered front (C1) is printed first, with its
interval, **and the interval is printed even where it is degenerate.**"*
That clause presumes a front with an interval. C1 emits **no point**, so there
is no interval to print degenerate or otherwise. The reproduction gate is the
reason and it is a measurement, not an absence of data:

> FallChecker over the C2 rescore: `segments 14 · ok 0 · real 185 · replay 0 ·
> verdict stateful_divergence` (`runs/c2/reproduction_gate.csv`)

Replaying the recorded candidates recovered **0 of 185** real FallChecker
alerts. Record-then-rescore is inadmissible for this checker on this pass —
which is the `theta_transport` finding `PREREGISTERED_E7C.md` already
registered, arriving at the one place E7-b's tie-break sends the cost axis. A
front that is *empty* is a different reportable object from a front that is
*wide*, and E12 registered a rule only for the second.

### Gap 2 — E12 §3 is a two-sided rule and the configuration is three-sided

§3 names exactly two objects: the registered front and the A1 front. §3a's two
branches both compare *two* fronts at a budget. There are three axes, and the
third is the one every number in the paper is currently computed from.

E12 **anticipated the discrepancy** — §1's fourth fact records that
`theta_vs_lambda.py` prices on V1/V2/V3 while E7-b §2 selects C1, and defers the
check to §4 step 2. What E12 did not do, and could not have done without
asserting the answer, is register **how a third axis is reported**. §3 gives it
no slot. This file gives it one.

### Gap 3 — §4's C1 column is falsified, and the consequence §4 drew changes

E12 §4's table records C1 as **`priced`** at all five grid points (0.300,
0.375, 0.450, 0.525, 0.600) and A1 as `UNREACHABLE` at the lowest two. On that
table, §4 concluded that coverage 0.6282 at θ = 0.30 *"is priced **only** by the
axis with the degenerate interval"* — meaning C1.

Step 2 falsifies the C1 column: it prices **none** of the five. So §4's
conclusion survives with its subject replaced, and the replacement is worse
than what was registered: the high-coverage end is priced only by **V**, the
axis **nobody registered**, on 8 segments, whose bootstrap interval at the
deployed point is `[0.00, 12.08]` with 33.9 % of resamples returning exactly
zero. E12 §4 could not register the reporting of a hole it did not know would
be this shape.

---

## 2. THE REPORTING RULE FOR A THREE-AXIS CONFIGURATION — REGISTERED BEFORE ANY OF IT IS WRITTEN

E12 §3's principle is **kept and extended**, not replaced: *nothing is
substituted, everything is added, and the gap between them is the finding.*

1. **All three axes are printed, in this order, in one table**: the registered
   axis, the axis the code used, the A1 axis. One table, because three tables
   in three places is how a reader comes to believe one of them is *the*
   answer.
2. **The registered axis is printed as empty, with the gate number that made it
   empty.** `0 points`, and `segments 14 · ok 0 · real 185 · replay 0 ·
   stateful_divergence` beside it. It is **not** omitted for having no row to
   show, **not** replaced by V, and **not** described as "a wider interval".
   An axis that priced nothing is reported as having priced nothing.
3. **The axis the code used (V) is printed, labelled as unregistered**, with its
   degenerate interval printed in full: `[0.00, 12.08]` and `P(0) = 33.9 %` at
   θ = 0.45, one segment of eight carrying 100 % of the alerts, and that segment
   being the only one of the eight on the substituted clock (HARNESS-5). The
   fact that it was **selected by code and not by a registration** is printed as
   part of the row, not as a footnote.
4. **The A1 axis is printed with its hole as a hole.** No entry at θ = 0.300 or
   0.375 — not an interpolation, not a bound, not a dash. This is E12 §4's rule
   and it is carried forward unchanged.
5. **The high-coverage end is printed as a stated hole in the evidence**, in the
   main text and not only in the supplement: the most attractive point the
   instrument offers (coverage 0.6282 at θ = 0.30) is priced by **no axis this
   campaign registered**. The sentence appears next to the coverage number, not
   in a different table from it.
6. **No single θ is named where the three A1 bootstrap intervals overlap.**
   `[0.472, 1.838]`, `[0.251, 0.844]` and `[0.060, 0.331]` — the first two
   intersect, so a budget boundary drawn between 0.524 and 1.084 alerts/h is not
   separable on this evidence. The paper reports a **budget-conditional
   threshold table**, and says in those words that the boundaries between its
   cells are not sharp. Naming one θ there would assert a resolution the
   measurement does not have, in a paper whose title says *under uncertainty*.
7. **Neither of the two non-empty axes is presented as correcting the other**,
   and neither is presented as correcting the empty one.

### 2a. Which branch this registration is prepared to publish

Written now, both ways, so neither is chosen after the fact. E12 §3a's two
branches are **void** — they presume two comparable fronts. These replace them
for the three-axis case:

- **Branch A — V and A1 order the grid points the same way.** They do: both put
  0.30 cheapest-to-coverage-richest and 0.60 tightest. Then the paper reports
  that the *ordering* is stable across the two axes that emitted points, and
  that the *cost* is not, and it does not treat the stable ordering as evidence
  that either axis resolved the cost.
- **Branch B — they disagree on the ordering at some budget.** Then the paper
  prints both orderings and names no allocated θ at those budgets.

Branch A is what step 2 delivered. It is recorded here as an observation about
the two axes, and **explicitly not** as a recovery of the registered axis.

---

## 3. THE UNREGISTERED SUBSTITUTION IS OURS, AND IT IS REPORTED WHERE OURS ARE REPORTED

`scripts/theta_vs_lambda.py` states in its own source comment that the in-situ
FAR it prices on is *"V1/V2/V3 at 0.30/0.45/0.60 over the 8-segment verification
sample"*. `scripts/count_everything.py::count_fall_front()` reads the same three
verification directories and emits `\CntBudgetThresholds` and
`\CntFallFrontSegments` from them. The registered rule
(`PREREGISTERED_E7B_AMENDMENT.md` §2, under E7 §3's tie-break) selects **C1**.

Both are code that **asserted a source and used another**, with no branch, no
warning and no fallback notice — the exact mechanism this paper characterises
on the system under test, committed by us, and this time **on the central result
path rather than in the harness**. It is therefore:

1. **Registered as a silent-failure row of ours** in
   `analysis/harness_silent.csv`, which is the register the supplementary table
   S5 is generated from. It is not put in the deployment table: that table is
   about the system under test.
2. **Marked in that table as the one on the result path**, because a defect in
   an instrument and a defect in the number the paper reports are not the same
   size of defect, and a table that flattens them misreports our own record.
3. **Not repaired by switching the code to A1 today.** The first repair is that
   the code stops being silent: it declares which pass it prices on and fails
   rather than defaults. Changing the data source is a separate decision, is the
   author's, and is not taken inside this registration.

---

## 4. WHAT THIS REGISTRATION DOES NOT DO

- It does **not** amend E12, and it does **not** re-run
  `scripts/e12_cost_axis.py` or `scripts/fall_front_provenance.py`. Every number
  quoted above was computed on 2026-09-11 after E12's lock, and this file
  recomputes none of them.
- It does **not** license a fourth axis. E12 §6's prohibition on going shopping
  is carried forward verbatim: if the cost axis is unresolved at the
  high-coverage end, the paper reports an unresolved cost axis. Pricing
  θ = 0.30 in-situ would take a **new** recording pass at a low θ over the full
  corpus; it is not run, and it is not run because the deadline would have made
  the decision look like the registration's.
- It does **not** re-open the allocation roster: Intrusion out by
  `PREREGISTERED_M3`, SmokeFire uncharacterised by E9, Running as E9/E10 left it.
- It does **not** declare the substituted-clock segment invalid. E4's finding
  stands corpus-wide; what is said here is E12 §6's narrower statement, that in
  a sample of eight it is the sole contributor and the corpus-wide pooling
  result does not transfer to it.
- It does **not** change any θ grid, sample, seed, matching rule, ρ, or interval
  method.

---

## 5. ORDER OF OPERATIONS — BINDING

1. This file is hashed. Its SHA256 goes in `PREREGISTERED_E12B.sha256` and in
   `GT_protocol/GT_PROTOCOL.md` §11.
2. **Only then** is any sentence about the three axes written into `main.tex`,
   `supp.tex`, `THETA_DECISION`, or a figure.
3. The three-axis table is generated from `analysis/e12/E12_COST_AXIS.json` by
   `scripts/count_everything.py`. **No number in it is typed by hand into
   LaTeX**, which is rule P9 and is what makes the claim in §2 checkable rather
   than asserted.
4. `THETA_DECISION` is rewritten to carry the threshold table of §2.6, and is
   the only place a demonstration operating point may be named — see §6.

---

## 6. THE ONE PLACE A SINGLE θ MAY STILL APPEAR, AND UNDER WHAT NAME

§2.6 forbids the paper from naming a single allocated θ. A verification job
(`D5s`) nevertheless needs one literal number to run, and a threshold table
cannot be passed to a runner.

Registered, before the number is chosen:

- The number D5s runs at is a **demonstration point**, named as one everywhere
  it appears, and it is **a member of the admissible set, not an optimum**.
- Its **selection rule is written down before it is applied**, and it is this:

  > *Admissible = the grid points priced by an axis that resolved — that is, the
  > A1 points whose segment-block bootstrap interval excludes zero. Among the
  > admissible points, take the **median by cost** (alerts per hour). Ties are
  > broken toward the cheaper point.*

  The rule is arithmetic on numbers already measured and already on disk. It
  introduces no new measurement, imports no undeclared site event rate
  $\lambda$, and expresses no preference between coverage and cost — the median
  is chosen precisely because it is the one member of the admissible set that
  cannot be argued to be the endpoint somebody wanted. It is written here
  **before** it is evaluated.
- D5s tests **that one point** on the 8 out-of-sample segments. It does **not**
  test the table, and the paper does not report it as having tested the table.
- If D5s's out-of-sample rate falls outside the bootstrap interval the
  demonstration point was selected inside, **that is reported as a result** and
  the table is not adjusted to accommodate it.

---

## 7. WHAT THIS COSTS, AND WHAT IT BUYS

The narrowed form of contribution (c) was, before today, an assertion: *a
procedure for allocating an alert budget, plus the data conditions under which
it can run.* The conditions were argued, not exhibited.

This campaign now has **three real cases, measured, on one deployment**:

| case | pass | verdict |
|---|---|---|
| **not eligible** | C1 → C2 | the pass the registered rule selects prices nothing: 0/185 replayed |
| **formally eligible, not powerful** | V | 3 points, 1 of 8 segments carrying 100 % of the alerts, interval containing zero |
| **eligible** | A1 | 3 points, 17 of 175 segments, no resample returning zero at the deployed point |

That is no longer an assertion. It is a **contrastive demonstration**, on one
instrument, of a procedure together with the conditions that decide whether it
can be run at all — and it is stronger than the version this campaign intended
to write. It is recorded here so that it cannot later be presented as the plan
all along.

---

## 8. PROVENANCE

| thing | where |
|---|---|
| E12, locked, unamended | `PREREGISTERED_E12_COST_AXIS.md` + `.sha256` |
| three axes, full | `analysis/e12/E12_COST_AXIS.json` (`scripts/e12_cost_axis.py`, seed 20260911, 20 000 replicates) |
| A1 per segment | `analysis/e12/A1_FALL_BY_SEGMENT.json` |
| V per segment | `analysis/FALL_FRONT_PROVENANCE.json` |
| C2 reproduction gate | `runs/c2/sweep_curve.json`, `runs/c2/reproduction_gate.csv` |
| coverage | `exsitu/RECALL_L_X4.json`, `exsitu/SCORE_X4_t*.json` |
| the silent substitution | `scripts/theta_vs_lambda.py` source comment; `scripts/count_everything.py::count_fall_front()` |

No machine hour is spent by this registration. Every number in it is a re-read
of a measurement already on disk.
