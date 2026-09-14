# ADDENDUM to `PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md` (LOCKED) — the M4e ablation matrix, registered before M4e can run

**Written 2026-09-07, 10:20 +07:00.** At the moment of writing, job `M4e` is
`BLOCKED` in `ops/RUN_QUEUE.json`, `out/ablation/` does not exist, and no
ablation cell has been run, scored or seen. This file is therefore a
pre-registration in the only sense that matters: the matrix is fixed before any
number it produces exists.

`PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md` is locked at SHA256
`60aaa61bea38cbc54388c250107942f4ac96dbbbdf1f00b2793d43748ae8c41a` and is **not
edited** — the same rule the M3 errata follows. E5 section 3 said "`ops/
ablation_essential.yaml` has not been written yet … the cell count is fixed here
so that the matrix is written to it rather than reconciled to it afterwards."
This addendum records that the matrix was written, and to what.

---

## 1. The artefacts, by hash

| file | SHA256 |
|---|---|
| `ops/ablation_essential.yaml` | `ced38c5fa189eda1cea929eb015b0c79dd6cc7f37ccad64af6cea2745e7c023b` |
| `ops/lists/m4_sample.list` | `a3cf149c9620021eb16e78898fc693ec0c282f1741f3f9971a306dc82d9eb979` |
| `analysis/m4_sample.csv` | `4b4d2f25b8fa8b6fc7d905d3ea49d68f691938fa5732e9a1d9b9d8c2e81985af` |

Drawn against `ops/manifest_rows_closed.csv`, the closed 175-segment corpus,
whose own hash is recorded in `SHA256SUMS.corpus_closed_20260902.txt`.

## 2. The seven cells

E5 section 3 fixed the count: *"all-on, each of the five instantiated checkers
alone, and all-concurrent: seven cells."* Expanded by
`scripts/ablation_runner.py` `expand()`, the matrix yields exactly seven, and
the same seven under both of that function's parsers (PyYAML 5.4.1 and the
built-in `_mini_yaml` fallback), which was checked rather than assumed:

| # | label | checkers | gate | registered phrase |
|---|---|---:|---|---|
| 1 | `baseline` | 5 | off | **all-concurrent (= the A1 check)** |
| 2 | `only_FallChecker` | 1 | off | each instantiated checker alone |
| 3 | `only_IntrusionChecker` | 1 | off | " |
| 4 | `only_SmokeFireChecker` | 1 | off | " |
| 5 | `only_HelmetChecker` | 1 | off | " |
| 6 | `only_RunningChecker` | 1 | off | " |
| 7 | `gate_on` | 5 | **on** | **all-on** |

Cell 1 runs the frozen evaluation configuration read from the A1 run metadata
itself (`out/m1/*.json`, `config`): `clahe_enabled: true`,
`disable_motion_filter: false`, `confirm_frames: 3`, `conf_threshold: 0.25`,
`skip_frame: 2`, `adaptive_gate_enabled: **false**`. That is what makes cell 1 a
check on A1 rather than a new experiment.

**One ambiguity in the registered wording, resolved here rather than silently.**
`PROMPT_RUN_CAMPAIGN` names the cells "all-on · each checker alone · all-
concurrent". `ablation_runner` does not emit a separate "all" concurrency cell —
its own comment says *"The 'all' cell is the baseline, so it is not duplicated
here"* — so "all-concurrent" is cell 1. The remaining phrase, "all-on", maps
onto `gate_on`: the adaptive gate is the one switch the deployed configuration
leaves off, so cell 7 is the only cell in which more is switched on than in
cell 1. Read the other way the matrix would expand to **six** cells and
`M4e.done_check.n = 7` would fail — after five days of queue time, at the end of
the campaign. The mapping is written down so it can be disputed now instead of
discovered then.

**Two cells are absent because E5 withdrew their channels**: no
`only_EnhancedHelmetChecker`, no `only_ForkliftSpeedChecker`. Neither channel
was constructed in the recorded pass, so neither has an object to ablate. This
is the 9 → 7 that E5 registered.

**No component, resolution, fps or module-option cells.** Those are M4x, whose
count E5 explicitly declined to register until its own matrix is written. That
remains unregistered.

## 3. The sample

Five segments, **2.4994 h**, listed in `ops/lists/m4_sample.list`:

```
HOM_20260827_2030   HOM_20260828_0000   HOM_20260828_0230
HOM_20260831_1930   HOM_20260901_0130
```

Drawn 2026-09-07 by `scripts/select_m4_sample.py` `draw()` and by no other rule:
strata (domain × lighting), **seed 20260820** — the seed every sampling step in
this campaign uses — target 2.0 h, over the closed 175-segment corpus. Frozen on
the draw. `PHASE1B_RUNPLAN.md` §2b, which has said *"chưa rút được — manifest
rỗng"* since 2026-08-26, is answered by this file.

**Three things about the draw that a reader should not have to infer:**

1. **The lighting stratification collapses to one stratum** (`home/day`). The
   rule reads lighting from the manifest's `notes` column and no row carries a
   lighting word; the corpus is a single indoor camera. The stratified draw is
   therefore, in fact, a simple seeded draw. Saying "stratified" without saying
   this would overstate what the sampling controlled for.
2. **2.4994 h overshoots the 2.0 h target by a quarter of an hour**, because
   the registered rule does not split a file and does not trim the last one
   drawn — trimming mid-file would break the observation-time accounting in P5.
   The realised duration is reported, not the target.
3. **The queue's estimate for M4e is low.** 7 cells × 2.4994 h = **17.50
   video-hours** against the `est_video_h: 14.0` carried in `RUN_QUEUE.json`
   (2.0 h × 7). At the measured `rtf` of 0.8034 that is ≈ 21.8 machine-hours
   where the queue will project ≈ 17.5. The queue field is **not** edited here:
   it is a schedule estimate, not a registered quantity, and editing it is a
   queue write that would have to wait for a stop. The gap is recorded so the
   ETA is read with it in mind.

## 4. What this addendum does NOT claim

It does not claim M4e is runnable. Checked on 2026-09-07, the ablation
toolchain on the device is incomplete in four separate ways — `run_batch.py` is
absent, `scripts/configs/` is absent, `ABL_DIR` resolves to `aap_v3_meas/
ablation` while `M4e.done_check` globs `out/ablation/*/*.json`, and
`C.load_manifest()` reads a path that does not exist. Those are harness
defects, they are recorded as **HARNESS-18**, and none of them is a question
about what M4e should measure. This file settles what it should measure. The
tooling is repaired separately, without a queue restart, before M4e's turn
comes.

---

*Registered 2026-09-07 by the author's decision of the same date. Hash in
`PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.sha256`. This file adds to
`PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md`; that file is not edited and keeps
its hash.*
