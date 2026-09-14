# PREREGISTERED E9 — recovering two channels: X3b (Running) and SFCTL (SmokeFire positive control)

**Locked 2026-09-09, author decision, after Checkpoint 3 opened and before
either job was queued.**
Registered under GT_PROTOCOL §11 as a **new locked pre-registration**. It fixes,
before the runs exist, (a) the configuration under which RunningChecker is
re-measured and the rule for reading the result, (b) the status of a
below-grid SmokeFire pass as an instrument check rather than a measurement, and
(c) a defect correction to the M4e ablation matrix.

**Written before X3b and SFCTL exist.** At the moment of this lock:
`out/x3b_virat_t*` does not exist, `out/sfctl_furg_t001` does not exist, neither
job is in `RUN_QUEUE.json`, `V5` is `RUNNING` at 4 of 8 segments and `D0` is
`PENDING`. Both jobs are queued only after this file is hashed.

**Builds on** `PREREGISTERED_M3.md`
(`dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a`, LOCKED),
`PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md`, its M4e addendum
(`6fd7fdb372fe85b643ab208470815cffbefe9c7cbc5ae23d09030d0ea9d2da15`) and
`PREREGISTERED_E8_D5_SAMPLE.md`
(`ba2112c2fc92cc5d8340f3ca35aa20d56e80cf10d7e07ba56ec58908e0efe605`). None of
them is edited.

---

## 0. Honest declaration of what had already been read

At the moment of this lock the following were known and are listed so that no
clause below can be read as having been chosen to suit them:

- FallChecker ex-situ recall at all five registered θ, strict and extended,
  with Wilson intervals (`exsitu/SCORE_X4_t*.json`, scored 2026-09-09 11:00).
- SmokeFireChecker: **0 alerts at all five registered θ** on FURG (X2).
- RunningChecker: **`process()` executed 0 times** in X3 (HARNESS-24).
- IntrusionChecker Layer-1 person recall 0.630–0.740 over the conf grid (X1).
- C2's reproduction gate: 24 segments, 12 exact, all three checkers
  `stateful_divergence`, zero curve points emitted.
- In-situ false-alarm rates for every declared channel, including 0/h for
  SmokeFire and Running over 83.9626 h.

**What E9 does with those numbers: nothing.** It changes no θ, no clip list, no
ground truth, no matching rule, no interval method and no weight. It (a) repairs
a checker that was never executed, at the θ grid already registered, and (b)
adds one pass that is declared **outside every curve** before it runs. Both
changes are corrections to instrumentation, and both are specified so that they
cannot flatter a result: §1's decision rule and §2's two-branch rule are written
here, with their thresholds, before the runs.

**One thing must be conceded plainly.** The trigger for looking was a zero.
Nobody would have opened the diagnostics if SmokeFire and Running had returned
plausible curves. That is why the readings below are fixed in advance and why
§2 has exactly two branches with no third: the protection against "check until
the answer is pleasant" is that the answer is committed to in writing before it
is known.

---

## 1. X3b — RunningChecker measured under a configuration in which it can run

### 1.1 What went wrong, from the counters and the source

`RunningChecker` is a **side checker**. It does not run a detector; it consumes
the boxes of the shared STD detection pass. `aap_offline_runner.py`:

```python
if side and model_std is not None:
    def track_capturing(*a, **kw):
        res = _track(*a, **kw)
        engine._offline_std_boxes = (res[0].boxes if (res and res[0].boxes is not None
                                     and len(res[0].boxes) > 0) else None)
...
    out = (chk.process(boxes, snames, frame=frame) if boxes is not None else {})
```

`X3.cmd` ran `--modules running` alone. The measured consequence, from the
runner's own stage counters:

| pass | modules | frames | `side_calls_with_boxes` | `side_calls_no_boxes` | `RunningChecker.process()` calls |
|---|---|---:|---:|---:|---:|
| X3 (ex situ) | `running` | 44 801 | **0** | 44 801 | **0** |
| A1 (in situ) | 5 modules | — | **3 220 694** | 1 269 458 | 3 220 694 |
| C1 (in situ) | 5 modules | — | 411 390 | 184 704 | 411 390 |
| V1 (in situ) | 5 modules | — | 137 899 | 76 047 | 137 899 |

`boxes` was `None` on 100 % of X3's frames, so the call was short-circuited to
`{}` and the checker never executed. X3 decoded 14 clips and measured nothing.
Whether the STD model was never asked for a detection or asked and returned
none is not resolved by these counters and is not needed: either way the
checker was not run, and in situ — where an STD-consuming module is present —
it plainly is.

### 1.2 Why re-running is a move TOWARD the frozen configuration

The frozen deployment configuration always runs the STD detection pass; that is
what the five live modules share, and it is the claim the manuscript makes
about the architecture. **Single-module isolation is an artefact of the ex-situ
harness, not a configuration the deployment ever has.** Running the ex-situ pass
with a module list that produces boxes therefore moves it closer to the frozen
configuration, not further from it. GT_PROTOCOL §8's table of permitted ex-situ
deviations (E-1..E-6) is untouched: none of them is invoked, because nothing
about the video, the frame rate, the resolution or the model changes.

### 1.3 What X3b holds fixed — everything already registered

| held fixed | value | provenance |
|---|---|---|
| θ grid | `run_vel_threshold` ∈ {0.03, 0.045, 0.06, 0.08, 0.10} | M3, verbatim, unchanged |
| clip list | VIRAT, 14 clips | `exsitu/virat/CLIPLIST_virat.csv` |
| ground truth | 16 `person_running(type10)` events | `exsitu/virat/GT_running_virat.csv`, SHA256 `d1cb596f6c67e6102ed3fc370c19ca9e7ab8fc2c68dd5e337ef06f4ee5d1f260`, LOCKED 2026-09-02 22:10 |
| matching rule | §3 unchanged: W = 2.0 s, greedy one-to-one, TP ≤ GT asserted, P8 merge gap 20 s | GT_PROTOCOL |
| image, dedup, cooldowns, virtual clock | as every other pass | pinned digest `sha256:2f41e503…` |

**The single change:** `--modules running` becomes `--modules intrusion,running`.
`IntrusionChecker` is present **only** to make the STD detection pass run.
Its own alerts are written to the same CSV and are **ignored** — the scorer
filters on `checker == "RunningChecker"`, as it already does. `IntrusionChecker`
takes no parameter from this job and contributes no number to any table from it.

### 1.4 The decision rule, fixed before the run

Read from the X3b run metadata, summed over the 14 clips at any one θ:

- **`side_calls_with_boxes` ≥ 1** → the checker executed. `coverage(θ)` from
  X3b is a valid ex-situ measurement, is scored by the registered rule, and
  enters the allocation exactly as FallChecker's does — **including if it is
  again 0 at every θ**, which would then be a measured zero with a rule-of-three
  upper bound, not an empty result.
- **`side_calls_with_boxes` = 0 at every θ** → the checker still did not
  execute. This is **not** a result. A new HARNESS entry is opened, RunningChecker
  leaves the allocation, and the manuscript states the architectural reason:
  a checker that consumes another module's detections cannot be characterised in
  isolation by this harness.

There is no third branch, and neither branch is conditioned on the value of the
coverage.

### 1.5 X3's existing output

Kept, not deleted. `out/x3_virat_t*` is marked
`VOID -- checker never invoked (HARNESS-24)`. **No number from X3 appears in any
table, figure, curve, allocation or sentence.** It survives as the evidence for
the defect and for this correction.

---

## 2. SFCTL — a positive control for SmokeFireChecker, outside every curve

### 2.1 The debt this repays

`scripts/run_batch.py` has carried this since **2026-08-26**, months before any
ex-situ zero existed:

> Verified for: IntrusionChecker, HelmetChecker (A0), EnhancedHelmetChecker
> (A1), ForkliftSpeedChecker (alert path, synthetic track).
> **NOT verified for: FallChecker, SmokeFireChecker** — no clip with such an
> event survives.

FallChecker's half of that debt was discharged by X4, which raised 107 alerts.
SmokeFireChecker's was not. Before "coverage = 0 at every registered θ on 17
annotated fire events" is printed, it must be known whether that channel's alert
path is capable of firing at all. **This clause exists because of the 2026-08-26
note, not because of the 2026-09-09 zero**; the zero is what made the debt
urgent, not what created it.

### 2.2 What SFCTL is

One pass over the same 23 FURG clips, same clip list
(`CLIPLIST_furg.csv`, `3c16a0d792b9e49bcabeb07dbe441c7c104b4b653c8b5033e8d3fb45a3f9efe5`),
same image, same everything, with `SmokeFireChecker` `confidence_threshold` =
**0.01** — deliberately **outside** the registered grid {0.30, 0.40, 0.50, 0.60,
0.70}, chosen as "essentially any positive response" rather than as a candidate
operating point.

### 2.3 Its status, fixed before it runs

> **SFCTL is instrument validation, not a measurement.**
> The point at θ = 0.01 does **not** enter any Pareto front, coverage table,
> recall curve, sensitivity analysis or allocation. It appears in §III (or §S5)
> as one sentence about whether the alert path fires, and nowhere else.

Reporting a below-grid point as a coverage number would be extending a
registered grid after seeing that the grid produced zeros, which is the exact
move §9's anti-tuning clause forbids. It is fenced off here so it cannot happen
later by convenience.

### 2.4 The two-branch reading rule, fixed before the run

- **alerts > 0 at θ = 0.01** → the alert path is sound. The registered-grid
  result stands as a **real measurement**: coverage = 0 on 17 annotated fire
  events at every registered θ, with the rule-of-three 95 % upper bound
  3/17 = 0.176, and SmokeFireChecker stays in the allocation as a channel whose
  measured coverage is zero.
- **alerts = 0 at θ = 0.01** → **no conclusion about coverage may be drawn.**
  The manuscript then says: *SmokeFireChecker's alert path has never been shown
  to fire on any input, in situ or ex situ; the channel is removed from the
  allocation and its zero is reported as uncharacterised, not as measured.*
  This goes in §8.5 and in Limitations.

**There is no third branch.** In particular, a result of 0 at 0.01 may not be
rescued by trying a lower threshold, a different corpus, or a different module
list: any such attempt requires a new pre-registration with a stated reason.

### 2.5 What SFCTL cannot settle

It cannot separate "the checker's own model produced no candidate" from "it
produced candidates below 0.30", because no counter exists for the model-owning
checkers' internal stage (`raw_by_checker` is fed only from `_run_detection`).
SFCTL answers exactly one question — does the path fire — and the manuscript
must not claim it answers more.

---

## 3. The same defect in the M4e ablation matrix

### 3.1 The affected cell

`ablation_essential.yaml` emits `only_<Checker>` for each of five checkers.
Classified by how each obtains its detections:

| cell | checker | source of detections | affected? |
|---|---|---|---|
| `only_IntrusionChecker` | Intrusion | **produces** the STD pass | no |
| `only_HelmetChecker` | Helmet | own PPE pass | no |
| `only_FallChecker` | Fall | model-owning (own model, `--device`) | no — X4 proves it fires in isolation |
| `only_SmokeFireChecker` | SmokeFire | model-owning | no (subject to §2) |
| **`only_RunningChecker`** | Running | **side checker: consumes the STD pass** | **YES — would measure 0 calls** |

`ForkliftSpeedChecker` is the only other side checker in the codebase and is
already withdrawn from the matrix by E5 §3, so the audit finds exactly one
affected cell.

### 3.2 The correction

The cell is **redefined**, not dropped: dropping it would change the registered
cell count from seven, which E5 §3 fixes and which `M4e.done_check.n = 7`
enforces.

| | |
|---|---|
| old label | `only_RunningChecker` |
| new label | `only_RunningChecker_with_std` |
| modules in the cell | `IntrusionChecker` (for boxes only) + `RunningChecker` |
| what the cell now means | the **minimum configuration in which RunningChecker can execute at all**, against the 5-checker baseline |

The label changes so that the difference is visible in every table rather than
carried in a footnote: this cell is not "one checker alone" and must not be read
as one. The other four `only_*` cells are unchanged.

`ablation_runner.expand()` gains a declared `side_checkers` set and a
`std_companion`, both read from the matrix file rather than hard-coded, so that
the correction is data and can be audited.

### 3.3 Hashes, so the change is a correction and not a re-selection

| artefact | before | after |
|---|---|---|
| `ops/ablation_essential.yaml` | `ced38c5fa189eda1cea929eb015b0c79dd6cc7f37ccad64af6cea2745e7c023b` | recorded in `KNOWN_ISSUES.md` §HARNESS-24 and in `RUN_QUEUE.json`'s `registered_matrix` at the moment of the edit |
| `RUN_QUEUE.json` `registered_matrix.cells` | `only_RunningChecker` | `only_RunningChecker_with_std` |
| `PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.md` | `6fd7fdb372fe85b643ab208470815cffbefe9c7cbc5ae23d09030d0ea9d2da15` | **not edited** |

The E5 addendum keeps its hash and its text. E9 is the record that one cell in
the matrix it registered could not have measured what it was written to measure.
**No ablation number existed when this correction was made** — M4e has never
produced an output — so nothing is re-selected in the light of a result, and the
`--plan --strict` gate is updated in the same edit so it still fails closed.

---

## 4. Anti-tuning clause

θ grids, clip lists, ground truth, the matching rule and the interval method are
untouched by this file and may not be changed by it later. If X3b or SFCTL
produces a result that suggests a different grid, that is a new
pre-registration with a stated reason and a recomputation of every affected
table — never a quiet substitution. The X3 output stays on disk as the record of
what the defect was, and the θ = 0.01 point stays outside every curve
permanently.
