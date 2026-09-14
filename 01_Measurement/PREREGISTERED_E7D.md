# PREREGISTERED E7-d — what the in-situ Fall θ-curve is allowed to be built from

**Locked 2026-09-08 10:46:16 +07** (Jetson clock, `dat-desktop`).
Registered under GT_PROTOCOL §11 as a **new locked pre-registration**: it binds
which measurements may enter §IV.D's allocation and which may not, and §11
forbids an errata from changing a decision.

**Written before V1 runs.** At the moment of this lock the queue holds V1–V5 as
`PENDING`, `out/v1_loose` does not exist, and no verification segment has been
measured at any θ. That ordering is the whole point: the rule below is fixed
before the numbers it governs exist.

**Builds on** `PREREGISTERED_E7C.md`
(`2c7a5550474de37f85b9ea38f1c1f6b265f1c5531f819f937bc71a2be984d26e`, locked
2026-09-08 10:25:00 +07), which established `theta_transport`. E7-c is not
modified. E7-b (`6d9bda77…`) and E7 (`78ff9ec1…`) are not modified.

---

## 0. Honest declaration of what was already read

**The A1, C1 and X4 Fall numbers had been read before this file was written.**
They are in E7-c and in `STATUS_CHECKPOINT.md` §15, and pretending otherwise
would be the kind of clean story this protocol exists to prevent. What follows
from that, stated rather than glossed:

- This file makes **one** determination that a prior number could have biased:
  that rescoring is inadmissible. It was made in E7-c, on the X4 control, and
  it is a determination *against* the cheaper option — it discards points
  already in hand and buys nothing.
- Every other clause below concerns measurements that **do not yet exist**:
  V1, V2 and V3 have not run. Their θ grid, their sample, their denominator and
  their confidence-interval method are fixed here, before the first segment.
- No threshold, no sample, no grid point and no interval method in this file
  was chosen after seeing a number it would apply to.

## 1. The three classes of Fall measurement, and what each may be used for

| class | what it is | may enter §IV.D allocation | may be printed |
|---|---|---|---|
| **native** | a pass whose runner ran at that θ, at a declared detector `conf` | **yes** | yes, as an estimate with an interval |
| **rescored upper bound** | a native pass's alert stream filtered to a higher θ | **no** | yes, in the supplement, labelled an upper bound, never with an interval |
| **other-instrument** | a native pass at a different detector `conf` | **no** | yes, reported separately, never joined to another curve |

## 2. The curve of record

**Detector `conf` = 0.25 throughout.** This is the deployed value and the value
A1 and V1–V3 all run at. A Fall FAR(θ) curve may contain points at one and only
one detector confidence, because `conf` sits upstream of the tracker and
therefore upstream of the state machine E7-c §3 describes.

| θ | source | sample | denominator | class |
|---|---|---|---|---|
| 0.30 | **V1** (`FallDecision` 0.30) | 8 verification segments | 3.9906 h | native |
| 0.375 | — | — | — | **no native pass; upper bound only** |
| 0.45 | **A1** (implementation literal 0.45) | 175 in-situ segments | 83.9626 h | native |
| 0.45 | **V2** (`FallDecision` 0.45) | 8 verification segments | 3.9906 h | native |
| 0.525 | — | — | — | **no native pass; upper bound only** |
| 0.60 | **V3** (`FallDecision` 0.60) | 8 verification segments | 3.9906 h | native |

The eight verification segments are disjoint from the twenty-four sweep
segments by construction (job S1, `ops/samples/verify_sample_4h.list`; checked
2026-09-08: intersection empty).

**θ = 0.45 is measured twice, on two disjoint denominators, and that is a
result, not a redundancy.** A1 measures it over 83.9626 h of the whole corpus;
V2 measures it over 3.9906 h of an eight-segment sample. Their agreement or
disagreement is the only direct evidence available about how far an
eight-segment rate generalises to the corpus, and it is therefore reported
whichever way it comes out. **No consistency threshold is registered, because a
threshold here would be a licence to discard the inconvenient one.** The
comparison is described, not gated.

## 3. Intervals

- **Rates** (alerts per hour over a segment set): **bootstrap over segments**,
  10 000 resamples, percentile interval, seed 20260820 — the seed every
  sampling step in this campaign uses. Segments are the resampling unit because
  they are the independent unit of observation; alerts within a segment are not
  independent of each other.
- **Proportions** (a fraction of alerts, e.g. a spot-check false-alarm
  fraction): **Wilson** score interval at 95 %.
- **A count of zero** is reported with the Poisson upper bound already in use
  in this campaign, and never as `zero_observed` for a channel that fires —
  `ops/c2_mode.json`'s `forbid_zero_observed_for` stands.
- **A rescored upper bound carries no interval.** An interval on it would
  describe sampling error around a number whose bias (E7-c §3: +56 % to
  +350 % on the X4 control) is larger than any sampling error it could have.

## 4. What §IV.D may allocate over

**Only rows of class `native` in §2, at `conf` = 0.25.** Concretely: the
allocation may use θ ∈ {0.30, 0.45, 0.60}. It may not interpolate to 0.375 or
0.525, and it may not substitute a rescored upper bound for a missing native
point.

**If the allocation's optimum falls between two native grid points**, the
reported allocated θ is the native grid point, named as such, with the
statement that the grid is three points wide. An interpolated θ would be a
number no pass ever ran at, presented as an operating point — which is the
thing §IV.C is about.

## 5. C1 is reported separately

C1 measured 24 sweep segments at `FallDecision` 0.30 with detector `conf`
**0.15**, not 0.25. It is a **native** measurement of a **different instrument
setting**. It is reported in its own row, with its `conf` on the row, and:

- it is **not** plotted on the curve of §2;
- it is **not** an input to the allocation;
- it is **not** compared to V1 as though the two were the same measurement,
  even though both ran at θ = 0.30. The difference between them is the
  detector confidence and is not attributable to θ.

Its value is what it was always for: it carries the recorded candidate stream
for Intrusion and Helmet, which is C2's input.

## 6. SmokeFire and the other channels

Unchanged by this file. SmokeFireChecker raised 0 alerts on all 175 in-situ
segments; its in-situ curve is flat zero with the Poisson bound already
reported, and V1–V3 sweep it jointly with Fall at 0.30/0.50/0.70 as registered.
Intrusion's knob is `conf`, swept natively by V4 and V5, and is unaffected by
`theta_transport` — nothing about Intrusion's rate is obtained by rescoring.

## 7. What this file does not decide

- Whether to buy the two missing native points. E7-c §6 costs them at ≈ 40.8
  machine-hours on the 24-segment sample or ≈ 180 h on the corpus. Neither is
  authorised here.
- Anything about the 132 unfilled label cells. They remain upstream of every
  in-situ FAR number for Fall and Helmet (E6), and no interval computed under
  §3 substitutes for them.

---

*Read for this file, all read-only:* `ops/RUN_QUEUE.json` (V1/V2/V3 operating
points and status), `ops/samples/verify_sample_4h.list`,
`ops/samples/sweep_sample_12h.list`, `ops/manifest_rows_closed.csv`,
`PREREGISTERED_E7C.md`. No measurement was launched or modified.
