# PREREGISTERED E7-b — amendment to E7: the C1b pilot is cancelled before it runs, and the ambiguous band is reported as an interval

**Written 2026-09-07, 14:22:02 +07:00.** At the moment of writing: job C1 is running
(4 of 24 segments), job **C2 has not started**, `out/c2_rescore/` does not exist,
and **no FAR(θ) number for FallChecker has been computed or read at any
threshold**. The alert counts by confidence band that §3 governs have not been
looked at; they are read only after this file is hashed.

`PREREGISTERED_E7_C1B_PILOT.md` is locked at
`78ff9ec16543da647803fa80d99b1126565d340ae63729a0be4ec30e1e854fdf` and is **not
edited**. E7 registered a pilot and a two-branch decision; this file cancels the
pilot before either branch was entered, and registers what replaces it. Same
pattern as the M3 errata and the E5 addendum: the signed artefact keeps its hash.

---

## 1. Why the pilot is cancelled, read from the image and not from a plan

`core/ai_pipeline.py` in image `sha256:2f41e503…`:

| line | what is there |
|---|---|
| 263–302 | the **fall** block calls `on_violation(tid="fall_…")` directly and sets `confirmed_violations` itself |
| 307–337 | the **smoke_fire** block, same shape |
| 473 | `_detect_and_confirm` is defined |
| 348, 356, 372 | the only three calls to it — all on the STD/PPE path, all after the two blocks above |
| 501 / 625 | `_should_dispatch` called / defined, only from inside `_detect_and_confirm` |

FallChecker and SmokeFireChecker pass through **no** confirmation counter and
**no** cooldown. Their alert stream *is* their candidate stream. E7 was written
to buy back pre-confirmation information for them; there is none to buy.

**What the pilot would still have bought** is narrower than E7 assumed: one field
per alert (`fired_by_high_scores`), which disambiguates a band of two grid points
for one channel — at 1.24 h for the pilot, 12.72 h for C1b, and the loss of the
full-corpus `D5f` run. **The author cancelled that trade on 2026-09-07.** The
band is reported as an interval instead, at no machine cost, under §3.

**SmokeFireChecker needs nothing at all.** Counted over all 175 in-situ segments
of A1: FallChecker 91 alerts, HelmetChecker 696, IntrusionChecker 5832,
**SmokeFireChecker 0**, RunningChecker 0. Its in-situ FAR(θ) is identically zero
at every θ, reported with the rule-of-three bound already registered. There is
nothing to sweep and nothing a better recorder would have caught.

---

## 2. WHICH PASS THE CURVE IS BUILT FROM — the rule, and what it selects

E7 §3 registered the tie-break: *use the pass whose recorded θ is lowest, because
rescoring is only valid upward.* Applied to what the two passes actually recorded,
read from their own run metadata before this file was hashed:

| pass | segments | `checker_params` | FallDecision in force | detector `conf_threshold` |
|---|---:|---|---|---|
| **A1** (M1+) | 175 | `null` on all 175 | **0.45** — the deployed literal; `_patch_fall_decision` was never applied | 0.25 |
| **C1** | 24 | `{"FallDecision": 0.30, …}` | **0.30** | 0.15 |

So the rule selects **C1**, not A1 — the opposite of the working assumption when
the amendment was requested, and the reason the rule was registered in advance.
From A1 at 0.45 the grid points 0.30 and 0.375 are **unreachable**: they lie
below the recorded threshold and would require alerts that were never written.

**The consequence is a smaller denominator and it is stated, not softened.** The
in-situ Fall curve rests on C1's **24 segments** rather than the corpus's 175.

### 2b. A1 is not wasted: it gives three grid points exactly, on the whole corpus

A1 recorded at exactly the literal 0.45, and that coincidence removes the
ambiguity entirely for it. For an A1 alert:

* `confidence > 0.45` → it fired through the confidence disjunct;
* `confidence ≤ 0.45` → the confidence disjunct was false, so it fired through
  `high_scores ≥ 2`, and it therefore survives **every** higher θ.

Both cases are decided by the recorded number. So **A1 yields exact FAR(θ) at
θ ∈ {0.45, 0.525, 0.60} over all 175 segments and 83.96 h**, and those three
points are reported as a second, stronger line beside the 24-segment curve —
never merged into it. A curve whose points have different denominators is not a
curve.

### 2c. The free cross-check E7 §3 asked for

All 24 C1 segments are inside A1's 175. On those segments, C1 rescored to 0.45
and A1 measured at 0.45 are the same predicate over the same footage. Agreement
is reported; disagreement is reported and not reconciled. It costs nothing and
it is the only end-to-end check available on the Fall path.

### 2d. A refinement that may narrow the interval, registered WITH its gate

If an alert in C1 with `confidence ∈ (0.30, 0.45]` also appears in A1, then it
survived A1's `confidence > 0.45 or high_scores` with `confidence ≤ 0.45`, hence
it fired by `high_scores` — the disjunct C1b was meant to record. A1 could
therefore resolve C1's ambiguity for free.

**It is not assumed.** A1 ran at detector conf 0.25 and C1 at 0.15, so the two
runs do not partition detections into the same tracks and `track_id` cannot be
used to match. The refinement is admissible **only** if, on the 24 shared
segments, C1-rescored-to-0.45 and A1-at-0.45 match one-to-one on
`(segment, t_alert)` within **±1 frame** for at least **95 %** of A1's Fall
alerts. If that gate fails, the interval of §3 stands unnarrowed and the failure
is reported. The threshold is fixed here, before either stream has been read.

---

## 3. THE AMBIGUOUS BAND — the rule, fixed before the numbers are read

The registered FallDecision grid is **0.30, 0.375, 0.45, 0.525, 0.60**. For a
curve built from C1 (recorded at 0.30), an alert with `confidence ∈ (0.30, 0.45]`
fired through the confidence disjunct at 0.30; whether it *also* satisfies
`high_scores ≥ 2` is not recorded. Therefore:

| θ | how it is reported |
|---|---|
| **0.30** | **point** — every recorded alert is present at its own recording threshold |
| **0.375** | **interval** [lo, hi] |
| **0.45** | **interval** [lo, hi] |
| **0.525** | **point** — only `confidence > 0.45` alerts can be in doubt, and none are |
| **0.60** | **point** |

with

* **FAR_lo(θ)** = alerts with `confidence > θ`, divided by the observation hours
  of the pass. The lower bound assumes no ambiguous alert fired by `high_scores`.
* **FAR_hi(θ)** = FAR_lo(θ) + alerts with `confidence ≤ θ` **and** `confidence >
  0.30`. The upper bound assumes all of them did.

Both bounds carry the same block-bootstrap interval treatment as every other
in-situ rate; the ambiguity interval and the sampling interval are reported
separately and never added.

**In §IV.D the allocation uses Proposition 3** — the max–min solution under an
interval — which is already registered for interval-valued *coverage*. Applying
it to an interval-valued *FAR* is an **extension of its use, not a change to the
proposition**: the proposition is stated over an interval-valued argument and
does not care which quantity the interval belongs to. No proposition, no proof
and no admission rule is altered by this file. The extension is named here so
that it appears as a registered decision rather than as a modelling choice made
while looking at the result.

---

## 4. WHAT ELSE THIS FILE SETTLES

**Job P1 and job C1b are cancelled before running.** Neither was ever inserted
into `RUN_QUEUE.json`; the two segments E7 named — `HOM_20260901_1600` and
`HOM_20260829_2100` — were **never executed under the v2 recorder**. Recorded
here so the E7 §1 table is not later read as a description of work that happened.

**The runner is not swapped during this campaign.** `aap_offline_runner_v2.py`
(`92d06e18…`, 63 lines from v1) stays in the repository as the HARNESS-20 fix for
the next recording campaign. Its evidence is `test_recorder_v2.py` (5 scenario
groups, all passing, against a fake engine), which is sufficient for the harness
section §S5 and is not evidence about any measurement reported here.

**U1 is left alone and `D5f` is kept.** No threshold is moved in either
direction: the pilot is cancelled because it does not buy what it costs, not to
protect a schedule.

---

## 5. TRUTHFUL STATEMENT AT THE TIME OF LOCKING

1. **What has been read**: the two passes' configuration (§2 table); total Fall
   alerts over the 175 A1 segments (91) and over the 24 C1 segments by segment
   (§ E7 §1); SmokeFire and Running totals (0 and 0); and the reproduction table
   for the four C1 segments finished so far.
2. **What has NOT been read**: the distribution of Fall alert confidences — the
   counts in the bands `≤ 0.30`, `(0.30, 0.45]` and `> 0.45` — which is exactly
   the quantity §3 governs, and which decides whether the interval at 0.375 and
   0.45 is narrow or wide. That is read only after this file is hashed.
3. **The direction of the amendment favours the schedule**, and that is said
   rather than left to be noticed: cancelling C1b keeps `D5f` and saves 13.96
   machine-hours. The reason given in §1 is that the pilot buys one field at two
   grid points of one channel; if that reason is wrong the amendment is wrong,
   and it is stated plainly enough to be checked against the image.

---

*Locked 2026-09-07. Hash in `PREREGISTERED_E7B_AMENDMENT.sha256` and in
`GT_PROTOCOL.md` §11. Amends `PREREGISTERED_E7_C1B_PILOT.md`, which is not
edited and keeps its hash.*
