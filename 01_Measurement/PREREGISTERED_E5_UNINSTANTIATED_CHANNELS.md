# PREREGISTERED E5 — TWO CHANNELS THAT WERE NEVER INSTANTIATED

**Status: locked.** Registered under GT_PROTOCOL section 11 as a *scope of
acquisition* change, not an errata. Section 11 forbids an errata from touching a
decision — a θ grid is a decision — so this is its own pre-registration with its
own hash, exactly as E4 was. The superseded lines of `PREREGISTERED_M3.md` are
not edited; they are superseded by this file and remain readable there.

**Author decision, 2026-09-06:** measure nothing further for
`EnhancedHelmetChecker` (the A1 helmet variant) or `ForkliftSpeedChecker`.

---

## 1. The fact this rests on, read from files and not from a summary

The M1 recorded pass built five of the instrument's seven checkers. Every one of
the 175 segments carries the identical effective configuration:

```
modules     = intrusion,helmet,fall,smoke_fire,running     175 / 175 segments
helmet_mode = standard                                     175 / 175 segments
```

`aap_offline_runner.py` builds `EnhancedHelmetChecker` **instead of**
`HelmetChecker` when `helmet_mode == "advanced"`, and builds
`ForkliftSpeedChecker` only when `forklift_speed` appears in `--modules`.
Neither condition holds on any segment. The two channels were therefore never
constructed, never shown a frame, and never had the opportunity to fire.

Counted, not asserted — `scripts/count_everything.py`, keys registered under P9:

| key | value |
|---|---|
| `far_checkers_n` | 7 |
| `far_checkers_measured` | FallChecker, HelmetChecker, IntrusionChecker, RunningChecker, SmokeFireChecker |
| `far_checkers_measured_n` | 5 |
| `far_checkers_not_measured` | EnhancedHelmetChecker, ForkliftSpeedChecker |
| `far_checkers_not_measured_n` | 2 |

Source of record: `01_Measurement/generated_counts.json`, SHA256
`d41e141f47062fb2b4a2eef0f3c25db349d68a72cc293547a1df6aad75aa5cc2`, generated
2026-09-06 from the 175 run-metadata files under `runs/m1/`.

**Where the roster of seven comes from, and why it is not evidence of
observation.** `far_checker_roster` is built from `per_checker_cooldown_s`,
which every run writes in full because it is a *configuration table*. It lists
all seven whatever ran. Reading it as a list of channels that were observed is
the error this file exists to close, and it is the same error as HARNESS-12 one
layer up: a configuration read as an observation.

---

## 2. THE RULE

> **`EnhancedHelmetChecker` and `ForkliftSpeedChecker` are outside the scope of
> in-situ measurement and outside the allocation.**
>
> In every in-situ table they are printed as an em dash with the fixed
> footnote **"not instantiated in the recorded pass"**.
>
> **No Poisson upper limit, no rule-of-three bound, and no rate — of any kind,
> in any table, main text or supplement — may be printed for either channel.**

**Why the bound is forbidden rather than merely omitted.** A rule-of-three or
Poisson upper limit is a statement about a channel that ran and stayed silent:
it says *we watched for T hours and saw nothing, so the rate is below 3.689/T
with 95% confidence*. Printed under a channel that was never built, the same
number reads as evidence that the channel rarely fires. It is not weak
evidence; it is no evidence, wearing the notation of evidence.

This is not hypothetical. `analysis/FAR_TWO_PIPELINES.md` printed
`UL 0.1477/h` for both channels and was corrected on 2026-09-06 for exactly
this reason. That correction is what prompted this pre-registration.

**Zero and blank are different claims** and must remain visually different:

| case | printed as | meaning |
|---|---|---|
| ran, observed zero | `0`, with `≤ 0.0439/h` | an observation with an upper bound |
| never built | `—`, "not instantiated in the recorded pass" | no observation, no bound |

---

## 3. WITHDRAWN FROM THE θ GRID

`PREREGISTERED_M3.md` section "Registered 5-point grid" registers one primary θ
per checker. Two rows are **withdrawn**:

| checker | knob | frozen value | registered grid | status under E5 |
|---|---|---|---|---|
| `EnhancedHelmetChecker` (A1) | `crop_conf` | 0.08 | 0.04, 0.06, **0.08**, 0.12, 0.16 | **withdrawn** |
| `ForkliftSpeedChecker` | `pixel_speed_threshold` | 0.12 | 0.06, 0.09, **0.12**, 0.16, 0.20 | **withdrawn** |

**This is a withdrawal. No other knob's value, grid, or frozen point changes.**
In particular:

- `HelmetChecker` (A0) keeps `per_class_conf[2]`, frozen 0.30, grid 0.15 / 0.22
  / **0.30** / 0.40 / 0.50 — **unchanged**. A0 is the standard-mode helmet
  checker and it *was* instantiated on all 175 segments; it is FAR-only for a
  different reason (no open video corpus for helmet coverage), which E5 does
  not touch. Withdrawing A0's knob because A1's is withdrawn would remove the
  θ curve of a channel that was measured, and the two must not be confused
  because they share the word "helmet".
- Sample sizes are unchanged: sweep **24** segments, verification **8**
  segments, and every registered seed is unchanged.
- ρ, the degradation band, is unchanged.

**Consequence in the executable configuration: none, because there was none.**
Checked over the whole of `ops/RUN_QUEUE.json`: the strings `crop_conf`,
`pixel_speed_threshold`, `forklift`, `Enhanced`, `helmet_mode` and `advanced`
appear **zero** times. Every queued engine pass (C1, V1–V5, D5s, D5f) already
runs `--modules intrusion,helmet,fall,smoke_fire,running` at default helmet
mode. The grid rows existed only in this pre-registration; the queue never
carried them. C1 therefore needs no edit and no restart, and the withdrawal
costs and saves nothing on the sweep itself.

**The one place it does change machine time is M4.** M4e is registered as nine
essential cells — "all-on, each of the seven checkers alone, and all-concurrent".
Under E5 that becomes **all-on, each of the five instantiated checkers alone,
and all-concurrent: seven cells.** Two ablation cells that would each have
measured a checker that does not exist in the pass are withdrawn with the
channels. `ops/ablation_essential.yaml` has not been written yet, so there is
nothing to edit; the cell count is fixed here so that the matrix is written to
it rather than reconciled to it afterwards. `M4e.done_check.n` must move 9 → 7
at the same time, and that is a queue edit, so it belongs to the next planned
restart. M4x ("the remaining nine cells") is re-counted when its own matrix is
written; no number is registered for it here, because none has been derived.

---

## 4. THE FIXED COUNTS

Registered here so that no table has to re-derive them, and emitted as P9 macros
so that no table can type them:

| quantity | value | macro key |
|---|---|---|
| detection channels in the instrument | **7** | `far_checkers_n` |
| channels instantiated in the recorded pass | **5** | `far_checkers_measured_n` |
| channels never instantiated | **2** | `far_checkers_not_measured_n` |
| channels FAR-only among the instantiated | **1** (HelmetChecker, standard) | `e5_far_only_n` |
| channels that are candidates for the allocation | **4** | `e5_allocation_candidates_n` |

The four allocation candidates are `FallChecker`, `SmokeFireChecker`,
`RunningChecker`, and `IntrusionChecker` (through the Layer-1 recall curve).
**E5 does not admit any of them**; admission remains governed by
`PREREGISTERED_M3.md`, and two of the four are still conditional there:
`RunningChecker` on the VIRAT coverage measurement (job X3), and
`IntrusionChecker` on the false-positive fraction from the label pack. E5 fixes
only the *denominator*: the roster is five, not seven, so at most five channels
can be admitted and the two withdrawn here can never be.

**Statements to be corrected wherever they appear, in both manuscript trees:**
any wording of the form *"Helmet A0/A1 and Forklift are FAR-only"* conflates
three different situations and is replaced by:

> Helmet (standard) is FAR-only: it was measured in situ and has no open video
> corpus for coverage. The enhanced-helmet variant and forklift-speed channels
> are *not measured at all*: they were never instantiated in the recorded pass.

---

## 5. TRUTHFUL STATEMENT AT THE TIME OF LOCKING

This pre-registration is written **after** the numbers it borders have been seen,
and that has to be said plainly rather than left for a reader to work out.

1. **The in-situ false-alarm rates of the five instantiated channels are FINAL
   and have been read.** `insitu_rate_status = FINAL`, coverage 1.0, 175/175
   segments, and Section IV.A of the TIM manuscript was drafted from them
   earlier on 2026-09-06. E5 is not registered blind.
2. **E5 changes no number among those five.** Not a rate, not an interval, not
   a denominator, not a grid point, not a seed. Every quantity in IV.A is
   identical before and after this file exists. What E5 does is remove two rows
   that never carried a number and forbid a bound from being invented for them.
3. **The direction of the change favours the paper, and that is stated rather
   than discovered.** A five-row table reads better than a seven-row table with
   two dashes; a seven-cell ablation is cheaper than a nine-cell one (≈6.2 h of
   registered machine time); and a roster of five makes the allocation argument
   tidier. None of those is a reason, and none of them was the reason. The
   reason is that a bound printed under a channel that never ran is a false
   statement, and it was already printed once.
4. **What could have made this file dishonest, and why it does not.** The
   temptation available here was to withdraw `HelmetChecker` (A0) along with the
   other two — it is FAR-only, its θ curve costs machine time, and the three are
   named alike in the older documents. A0 *was* instantiated on all 175
   segments and its false-alarm rate (`far_helmetchecker_pooled_rate`) is one of
   the paper's reported numbers. It stays, with its grid intact.

---

## 6. ENFORCEMENT

- `scripts/count_everything.py` emits `far_checkers_measured` /
  `far_checkers_not_measured` from each run's own `modules` and `helmet_mode`,
  and writes `"not measured in this pass"` into
  `far_<checker>_pooled_ci_method` instead of a bound. A table cannot print a
  bound for these channels without the counts file first inventing one.
- `02_Manuscript/render_check.py` (TIM) fails the build on a hand-typed numeral
  in the sections it polices, so a bound cannot be reinstated as prose.
- `analysis/FAR_TWO_PIPELINES.md` carries the 2026-09-06 correction inline.

---

*Locked 2026-09-06. Hash in `PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.sha256`
and in GT_PROTOCOL section 11. This file supersedes the two withdrawn grid rows
of `PREREGISTERED_M3.md`; that file is not edited.*
