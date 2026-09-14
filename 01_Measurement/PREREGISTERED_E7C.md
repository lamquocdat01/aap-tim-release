# PREREGISTERED E7-c — the `high_scores` disjunct is θ-independent, and that is not enough

**Locked 2026-09-08 10:25:00 +07** (Jetson clock, `dat-desktop`).
Registered under GT_PROTOCOL §11 as a **new locked pre-registration**, not as an
errata: it changes how a reported number may be read, and §11 forbids an errata
from changing a decision.

**Supersedes, in part, `PREREGISTERED_E7B_AMENDMENT.md`**
(`6d9bda777f235bc0062bdc52f992ed8ca82f5302d69575e4ee1544bd73d495eb`, locked
2026-09-07 14:22:02 +07). E7-b is kept unchanged; §5 below states exactly which
of its clauses this file withdraws and which it leaves standing.
`PREREGISTERED_E7_C1B_PILOT.md`
(`78ff9ec16543da647803fa80d99b1126565d340ae63729a0be4ec30e1e854fdf`) is
untouched.

---

## 1. The question E7-b §2d left open, and the answer

E7-b §2d made the collapse of the two lower grid points from intervals to
points conditional on one fact about the code: **does the `fired_by_high_scores`
disjunct reference θ (`FallDecision`) in any way?** If it did, the disjunct
would move with the grid and no rescoring rule could be written at all.

**It does not. The branch is θ-independent.** Read 2026-09-08 out of the pinned
image `ghcr.io/lamquocdat01/aap-ai-engine@sha256:2f41e5038c4377f7a5e340ff2161835e8a29935fd9291d38c3868f580d86c9c6`,
the same image every job of this campaign runs.

`/app/core/ai_modules/fall_check.py` (`33ee60b60c51f9416962d545005f8daf350e5fa00b4d23dfba5cb580f44d7795`),
lines **355–356**, the last two lines of `_analyze` before its return at 358:

```python
355        high_scores = sum(1 for s in scores if s > 0.55)
356        is_falling  = confidence > 0.45 or high_scores >= 2
```

Both operands of the second disjunct are literals — `0.55` on a per-feature
score, and the count `2`. Neither is a config key, neither is reachable from
`checker_params`, and `FallDecision` does not appear anywhere in the file.

The wrapper that moves the operating point,
`scripts/aap_offline_runner.py` line **348**, recovers the disjunct with the
*fixed* literal and not with θ:

```python
344    orig = checker._analyze
346    def analyze(*a, **kw):
347        is_falling, confidence, reason = orig(*a, **kw)
348        fired_by_high_scores = bool(is_falling) and not (confidence > 0.45)
349        return ((confidence > threshold) or fired_by_high_scores,
350                confidence, reason)
```

And `/app/core/ai_pipeline.py`
(`2e98cd2e4cf35c180b489404e32cff1cd039105b5248588d7b5a65eb8c76d618`) lines
**263–304**, the fall block E7-b's §2d named, contains **no threshold of any
kind**: it calls `on_violation(tid="fall_…")` and writes
`confirmed_violations` directly. Every θ-sensitive decision for Fall is taken
inside `fall_check.py`, upstream of that block.

## 2. What θ-independence buys, and it is real

Because the disjunct does not move with θ, the A1 evidence transfers as E7-b
§2d said it would. Read from `out/m1/*.csv`, all 175 segments, 83.9626 h:

- **91 Fall alerts. 0 of them carry confidence ≤ 0.45. The minimum recorded
  confidence is 0.451.**

Under `is_falling = confidence > 0.45 or high_scores >= 2` with A1 running the
literal (`checker_params: null` on all 175 segments, so `_patch_fall_decision`
was never applied), an alert with confidence ≤ 0.45 is exactly an alert the
`high_scores >= 2` disjunct produced on its own. There are none.

**Finding, and it stands:** across 83.9626 h of deployment the
`high_scores >= 2` branch never once produced an alert by itself. The
"unrecorded disjunct" ambiguity of E7-b §3 — the reason two grid points were
reported as intervals — is therefore **resolved, and resolved in the direction
that removes it**.

## 3. Why that is not enough, and the measurement that settles it

Resolving the disjunct would license rescoring only if the Fall alert count
were a function of the recorded per-alert confidence. **It is not.**
`FallChecker` carries its own stateful stage, inside the checker and therefore
invisible to the pipeline-level analysis recorded in `ops/c2_mode.json` rev 1.
`fall_check.py` lines **217–262**, `process()`:

| line | mechanism | value |
|---|---|---|
| 228 | `STANDING → FALLING` on the first `is_falling` frame | — |
| 239 | `FALLING → FALLEN` after `confirm_frames` consecutive `is_falling` frames | **4** |
| 254 | `FALLEN → ALERTED`, emits `FALL_DETECTED`, only after `stationary_seconds` elapsed | **2.0 s** |
| 222 | `ALERTED → STANDING` requires `not is_falling` **and** `cooldown_seconds` elapsed | **30.0 s** |

`is_falling` is θ-dependent at every one of those four transitions. Moving θ
therefore moves the **trajectory**, not just the filter: the confirm counter,
the stationary timer and the cooldown all see a different frame sequence. The
`elapsed=2.0s`, `elapsed=2.1s`, `elapsed=5.7s` fields in every `FALL_DETECTED`
line of `ops/job_C1.log` are that stationary timer, printed by line 260.

**The controlled test, on data already measured.** Job **X4** (DONE
2026-09-06 22:14:55, `sha_outputs` recorded in `RUN_QUEUE.json`) is five
**native** passes over the same 160 GMDCSA24 clips (0.3577 h), fall-only,
detector `conf` fixed at 0.25, differing **only** in `FallDecision`. It is
exactly the experiment that asks whether rescoring reproduces a native run.

Rescoring the native θ = 0.45 pass upward — the operation E7-b performed on
A1 — against the native passes at the same θ:

| θ | native alerts | rescored from native 0.45 | error |
|---|---:|---:|---:|
| 0.450 | 27 | 27 | +0 (identity) |
| 0.525 | 14 | 25 | **+79 %** |
| 0.600 | 2 | 8 | **+300 %** |

And from the loosest pass, the operation planned for C1:

| θ | native alerts | rescored from native 0.30 | error |
|---|---:|---:|---:|
| 0.300 | 107 | 107 | +0 (identity) |
| 0.375 | 49 | 50 | +2 % |
| 0.450 | 27 | 42 | **+56 %** |
| 0.525 | 14 | 31 | **+121 %** |
| 0.600 | 2 | 9 | **+350 %** |

The bias is one-signed and large. Its mechanism is the table above: at higher θ
fewer frames satisfy `is_falling`, so the `confirm_frames = 4` counter completes
far less often and the 2 s stationary timer is reached far less often. The
recorded confidence distribution knows nothing about either.

**In-situ, the same disagreement appears.** On the 23 segments C1 and A1 share
(10.7284 h), C1 rescored to θ = 0.45 gives **41** Fall alerts; A1 measured
natively at θ = 0.45 on those same segments gives **34**. E7-b registered this
comparison as a free cross-check. **It fails, by +20.6 %.** The in-situ pair is
confounded — C1 ran at detector `conf` 0.15 and A1 at 0.25 — which is why X4,
where `conf` is held fixed, is the evidence of record and this is corroboration.

## 4. Ruling

**R1. Rescoring an alert stream across θ is not admissible for FallChecker, in
either direction, at any grid point.** The limitation is named
**`theta_transport`** and is distinct from the `unrecorded_disjunct` limitation
of E7-b §3, which §2 above closes. Closing one did not close the other; nothing
in the disjunct analysis ever bore on the state machine.

**R2. A grid point may be reported as a number only if a pass ran natively at
that θ.** As of this lock the in-situ passes are:

| θ | native in-situ pass | alerts | denominator | status |
|---|---|---:|---|---|
| 0.30 | C1, detector conf 0.15, 23 of 24 segments | 168 | 10.7284 h | native, **but 23/24 and on a different detector conf — not on A1's curve** |
| 0.375 | — | — | — | **no native pass** |
| 0.45 | A1, detector conf 0.25, 175 segments | 91 | 83.9626 h | **native. FAR = 1.0838 alert/h** |
| 0.525 | — | — | — | **no native pass** |
| 0.60 | — | — | — | **no native pass** |

**R3. E7-b's three-point A1 table is reduced to one point.** The 0.525 (44
alerts, 0.5240/h) and 0.60 (15 alerts, 0.1787/h) rows were produced by the
rescoring R1 forbids and are, by §3, **upper bounds and not estimates**. They
may appear in the manuscript only as upper bounds, labelled as such, or not at
all. The θ = 0.45 row is unaffected: it is A1's native operating point, and the
independent agreement between `far_fall_a1_rate_t045` and
`far_fallchecker_pooled_rate` at 1.0838 recorded in E7-b still holds.

**R4. C1 and A1 are not two points on one curve.** They differ in the detector
confidence upstream of the checker (0.15 vs 0.25) as well as in θ. A Fall
FAR(θ) curve drawn through both would be drawn through two experiments.

**R5. `ops/c2_mode.json` rev 1 misclassifies FallChecker.** Its
`bypass_confirm_and_cooldown` block is correct about the *pipeline* stages —
`_detect_and_confirm` (473) and `_should_dispatch` (625) are not on the fall
path — and its `no_stateful_stage` label is therefore right about the pipeline
and **wrong about the checker**, which has confirm, dwell and cooldown of its
own at `fall_check.py` 217–262. C2 must classify FallChecker as
**`stateful_divergence`**, not `no_stateful_stage`. This is a factual
correction to a classification, not a change to C2's decision procedure; the
hard prohibition on `zero_observed` for FallChecker and SmokeFireChecker
(`forbid_zero_observed_for`) stands unchanged and for the unchanged reason.
SmokeFireChecker's classification is not disturbed: it raised 0 alerts on all
175 segments and no rescoring of it is contemplated.

**R6. The §2d 1:1 gate is demoted to evidence, as E7-b §2d directed — and its
precondition is currently unmet.** The gate (1:1 match on `(segment, t_alert)`
within ±1 frame for ≥ 95 % of A1's Fall alerts) is recorded in this file as
evidence, never as a condition on a reported number. It was to run when C1
reached 24/24. **C1 reached 23/24**: `HOM_20260831_0900` was refused by the
runner's own plausibility guard (`the container reports 14787.7340 fps, outside
the plausible band 5.0-60.0`, `ops/job_C1.log` line 173). Whether the refused
segment is recovered, replaced, or excluded with a stated denominator is an
author decision and is not taken here.

## 5. What this file withdraws from E7-b, and what it leaves standing

**Withdrawn:**

- E7-b §2d's conditional promise that θ-independence of the disjunct would
  convert the 0.375 and 0.45 grid points from intervals to points. The
  antecedent is true (§1) and the consequent is false (§3). The conditional
  itself was wrong, because it did not contemplate `theta_transport`.
- E7-b's characterisation of the three A1 rows at θ ≥ 0.45 as exact over the
  whole 175-segment corpus, for the 0.525 and 0.60 rows. See R3.

**Standing, unchanged:**

- E7-b's pass-selection rule and its result: A1 recorded at the literal 0.45,
  C1 at 0.30, and the two lower grid points unreachable from A1.
- The cancellation of P1 and C1b.
- The A1 confidence-band table of E7-b, which is a description of a recorded
  distribution and is correct as such. What is withdrawn is the inference drawn
  from it about counts at other θ.
- `U1`, `D5f`/`D5s`, and every schedule decision. Nothing here was decided to
  protect a date, and nothing here moves one.

## 6. What would restore the grid

Only native passes. Three in-situ passes at θ ∈ {0.375, 0.525, 0.60} on a fixed
detector `conf` would give the curve; on the 24-segment sweep sample at the C1
measured rtf of 0.8826 that is ≈ 3 × 13.6 h ≈ **40.8 machine-hours**, and on the
full 175-segment corpus ≈ 3 × 60.0 h ≈ **180 machine-hours**. Neither is
authorised by this file. This section exists so that the cost of the missing
points is on the record next to the reason they are missing, rather than being
discovered later as a surprise.

---

*Evidence read for this file, all read-only:*
`out/m1/*.csv` and `*.json` (A1, 175 segments) ·
`out/c1_record/*.csv` and `*.json` (C1, 23 segments) ·
`out/x4_fall_t{030,0375,045,0525,060}/*.csv` (X4, 5 native passes) ·
`/app/core/ai_modules/fall_check.py` and `/app/core/ai_pipeline.py` in the
pinned image · `scripts/aap_offline_runner.py` · `ops/c2_mode.json` rev 1
(`ce3f4f5c30233f66a383538d48bef22ccb1f9d53ec04dd24864854a963cd2cee`) ·
`ops/job_C1.log` · `ops/RUN_QUEUE.json` (read only; not modified).
