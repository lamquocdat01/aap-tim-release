# PREREGISTERED E7 — the C1b recorder pilot, and the rule that decides whether C1b runs at all

**Written 2026-09-07, 13:05 +07:00.** At the moment of writing: job C1 is running
(4 of 24 segments), the v2 recorder exists but has never been run against the
engine, no pilot segment has been processed, and no number this file governs
exists. `ops/c2_mode.json` is at revision 1 and job C2 has not started.

This is a **decision**, not a count, so under `GT_PROTOCOL.md` §11 it cannot be an
errata line. It is its own locked pre-registration with its own hash.

---

## 0. What this rests on, read from the image and not from a summary

`core/ai_pipeline.py` in image `sha256:2f41e503…`, read 2026-09-07:

| line | what is there |
|---|---|
| 263–302 | the **fall** block: calls `on_violation(tid="fall_…")` directly and sets `confirmed_violations` itself |
| 307–337 | the **smoke_fire** block: the same shape |
| 473 | `_detect_and_confirm` is *defined* |
| 348, 356, 372 | the only three places it is *called* — all on the STD/PPE path, all **after** the two blocks above |
| 501 | `_should_dispatch` is called, only from inside `_detect_and_confirm` |
| 625 | `_should_dispatch` is *defined* |

**Therefore FallChecker and SmokeFireChecker have no confirmation counter and no
cooldown.** Their alert stream *is* their candidate stream. This corrects the
first reading of HARNESS-20 on 2026-09-07 morning, which treated the empty
candidate file as lost pre-confirm information. There is no pre-confirm stage to
lose. What is lost is narrower, and §2 says exactly what.

---

## 1. THE PILOT — two segments, named here, chosen before it runs

Rule, applied to the 24 segments of `ops/samples/sweep_sample_12h.list` against
**A1** run output (`out/m1/*.csv`), never against C1 output: take the segment
with the most `FallChecker` alerts, then the next.

| # | segment | A1 FallChecker alerts | duration |
|---|---|---:|---:|
| 1 | **`HOM_20260901_1600`** | **17** | 1801 s |
| 2 | **`HOM_20260829_2100`** | **9** | 1800 s |

Total **1.0003 video-hours** → **≈ 1.24 machine-hours** at the measured
`rtf` 0.8034. Run with `aap_offline_runner_v2.py`, at C1's registered θ
(`conf 0.15`, `FallDecision 0.30`, `SmokeFireChecker 0.30`,
`RunningChecker 0.03`, `HelmetChecker 0.15`), `--record-candidates` on.

### 1b. The SmokeFire arm does not exist, and this is why

The registered rule also asks for the segment with the most `SmokeFireChecker`
alerts. Counted over **all 175** in-situ segments of A1: `FallChecker` **91**,
`HelmetChecker` **696**, `IntrusionChecker` **5832**, and
`SmokeFireChecker` **0** — the checker does not appear in a single row.
`RunningChecker` likewise **0**.

So the rule degenerates: every candidate segment ties at zero and the tie-break
would select an arbitrary one, on which a gate of the form "reproduce the alert
count" is satisfied by 0 = 0 and proves nothing about the recorder. **A pilot
that cannot fail is not a pilot.** The SmokeFire arm is therefore not run in
situ, and the second pilot segment is the second-ranked Fall segment instead, so
that both pilot segments exercise the path actually under test.

**Substitute, registered here:** one FURG clip from the X2 corpus, where
`SmokeFireChecker` did fire, is run with the v2 recorder in the same slot
(≈ 2.6 min video, negligible machine time). It tests the same property — does
the recorder see a callback-path violation — on the only footage in this
campaign where that channel fires at all. It is **not** an in-situ measurement
and contributes to no in-situ rate.

**And this is a finding, not a gap:** SmokeFireChecker raised **zero** alerts in
83.94 h of in-situ footage. Its in-situ curve is flat at zero for every θ tried,
with the Poisson upper bound already reported (`far_smokefirechecker_pooled_rate`
0.0, `ci_hi` 0.0439/h). Nothing C1b could do would change that.

---

## 2. THE PILOT GATE — thresholds fixed before the pilot runs

Three conditions, all on the two pilot segments, all for `FallChecker`:

| # | condition | threshold |
|---|---|---|
| G1 | every alert has a candidate row: the candidate stream and the alert stream agree 1:1 on `(frame_idx, track_id, event_type)` | **exact**, 0 unmatched either way |
| G2 | `t_alert` agreement | **± 1 frame**; and see the note below on W |
| G3 | `fall_disjunct` is recorded for every alert, and the count of `ambiguous` is reported | recorded for **100 %**; `ambiguous` **≤ 10 %** of alerts |
| G4 | replaying the recorded candidates at the deployed θ = 0.30 reproduces the alert stream | **identity**, 0 added, 0 lost |

**On W = 2.0 s.** The author registered a tolerance of W = 2.0 s for the alert
*timestamp*, on the ground that Fall is a post-event/stateful detector. That
tolerance is registered and stands. It is also, on the evidence of §0, expected
to be **unnecessary**: the candidate row and the alert row for a fall violation
are written from the same `on_violation` call on the same frame, so the
difference should be exactly zero. **If W is ever needed, that is itself a
finding** — it would mean the two writes are not the same event — and it is
reported rather than absorbed. G2 therefore passes at ±1 frame; a result that
needs W ∈ (1 frame, 2.0 s] passes the registration and is reported as an anomaly.

**G3's 10 % is the one number here with no precedent to lean on.** It bounds how
often two tracks in one frame share a rounded confidence and disagree on which
disjunct fired, which is the only way `ambiguous` arises. It is set before any
pilot output exists; if the realised figure exceeds it, the gate fails and C1b
does not run for FallChecker.

---

## 3. THE DECISION — deterministic, two branches, no third

**PASS** (G1–G4 all met) → **C1b runs for FallChecker**: the remaining 22
segments of the C1 sample, v2 recorder, same θ. 10.2197 video-hours →
**≈ 12.72 machine-hours**. In-situ FAR(θ) for FallChecker is then computed on all
24 segments and reported in §IV.C/§IV.D.

**FAIL** (any of G1–G4) → **C1b does not run.** In-situ evidence for FallChecker
stays at the three joint operating points V1/V2/V3 (LOOSE / FROZEN / TIGHT),
which are real runs and do not depend on any of this. §IV.D uses the sparse grid
under Proposition 3, and §8.5 states in one sentence that the in-situ Fall curve
is three measured points rather than a swept curve, and why.

There is no third branch. In particular there is no "run C1b anyway and mark the
result provisional".

### 3b. What C1b actually buys — stated before the pilot, so the decision is not made twice

Without C1b, FallChecker's in-situ curve is **already** computable from C1's
existing alert stream, because there is no stateful stage between candidate and
alert. The patched operating point is

    (confidence > θ) or fired_by_high_scores

so for an alert recorded at θ = 0.30:

| recorded confidence | rescoring at a higher θ |
|---|---|
| ≤ 0.30 | must have fired by `high_scores` → **survives every θ**, exactly known |
| > 0.45 | fired by the confidence branch → survives iff `confidence > θ`, exactly known |
| in (0.30, 0.45] | **ambiguous**: it fired by confidence at 0.30, and whether it *also* satisfies `high_scores` is not recorded |

The registered FallDecision grid is **0.30, 0.375, 0.45, 0.525, 0.60**. Two of
those five points — **0.375 and 0.45** — fall inside the ambiguous band. So C1b
buys exactness at 2 of 5 registered grid points, and buys nothing at the other
three. That is the whole of what 13.96 machine-hours purchases, and it is written
down here so the pilot result is judged against it rather than against a hope.

---

## 4. WHERE IT SITS IN THE QUEUE, AND WHAT IT COSTS

Pilot job **P1** and conditional job **C1b** are inserted **after V5 and before
D0**, at the planned restart described in the runbook. Projections from the
daemon's own `measured_rtf` = 0.8034 at the time of writing (D0 projected
2026-09-09 03:15, U1 requires D0 complete before **2026-09-09 10:25**):

| scenario | D0 lands | U1 (`D5f`) | campaign complete |
|---|---|---|---|
| neither P1 nor C1b | 09/09 03:15 | **fires** → D5f | ≈ 16/09 05:06 |
| **P1 only** (+1.24 h) | 09/09 04:29 | **still fires** → D5f | ≈ 16/09 06:20 |
| **P1 + C1b** (+13.96 h) | 09/09 17:11 | **does not fire** → D5s | ≈ **13/09 06:45** |

So the pilot alone is free of consequence for U1: it costs 1.24 h against a
5 h 56 min margin. **C1b is what costs `D5f`**, and the author accepted that
trade on 2026-09-07 in exchange for an in-situ Fall curve with the recorder that
sees the channel. Note the direction of the last column: giving up the
full-corpus D5f run also finishes the campaign about three days earlier.

**No threshold is moved to save D5f.** U1's rule, its scope and its date are
unchanged; if it does not fire, it does not fire, and D5s — the registered
fallback — runs.

---

## 5. TRUTHFUL STATEMENT AT THE TIME OF LOCKING

This file is written after some of the data it borders has been seen. Stated
plainly rather than left to be worked out:

1. **Four of C1's 24 segments have been processed and their reproduction table
   has been read.** On `HOM_20260827_1330` specifically: FallChecker 6 alerts /
   0 candidates, HelmetChecker 4 / 20, IntrusionChecker 140 / 5010, and the
   replay-vs-engine comparison for all three.
2. **The pilot segments were NOT chosen from that.** The selection rule reads
   `out/m1/*.csv` — job **A1**, complete since 2026-09-05, before the recorder
   defect was known and before C1 existed. Neither `HOM_20260901_1600` nor
   `HOM_20260829_2100` is among the four C1 segments seen.
3. **The direction of the pilot result is not known.** The v2 recorder has
   passed a unit test against a fake engine (`test_recorder_v2.py`, 5 scenarios)
   and has never met the real one.
4. **The counts in §1b are final and were read before this file was written.**
   `SmokeFireChecker` 0 alerts over 175 segments is not a prediction; it is why
   the SmokeFire arm is withdrawn, and withdrawing it after seeing the count is
   exactly the kind of move that needs saying out loud. It is withdrawn because
   a gate that cannot fail is not a gate, not because zero was inconvenient.

---

*Locked 2026-09-07. Hash in `PREREGISTERED_E7_C1B_PILOT.sha256` and in
`GT_PROTOCOL.md` §11. Supersedes nothing; adds a decision that did not exist.*
