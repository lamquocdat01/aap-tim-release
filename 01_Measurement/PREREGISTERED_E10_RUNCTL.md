# PREREGISTERED E10 — a positive control for RunningChecker

**Locked 2026-09-10, evening, author decision.** Registered under
`GT_PROTOCOL.md` §11 as a new locked pre-registration. Builds on
`PREREGISTERED_E9_CHANNEL_RECOVERY.md`
(`3a9a750199c654ab1b7a31af91604d19111f05d5a1ee3cbca440dfeeac63def8`), which is
not edited.

**Written while the answer is unknown.** At the moment of this lock
`out/runctl_virat_t001` does not exist, `RUNCTL` is not in `RUN_QUEUE.json`, and
no pass has been run at any threshold below the registered grid for this
channel. That is the only condition under which a pre-registration means
anything, and it is the reason this file is being written tonight rather than
after the queue reaches it.

---

## 0. What is already known, declared so no clause below can be read as fitted to it

- **X3b (DONE 2026-09-10 15:56)**: `RunningChecker.process()` executed
  **214,715** times with boxes across five registered θ on 14 VIRAT clips, and
  produced **0** alerts at every θ. E9 §1.4 **branch 1**: the checker executed,
  so its zero is a *measurement* and enters the allocation.
- **X3 (the run X3b replaces)**: the same checker executed **0** times across
  44,801 frames (HARNESS-24). Its output is VOID and contributes nothing.
- **SFCTL (DONE 2026-09-10 16:27)**: the sibling positive control for
  `SmokeFireChecker` raised **0** alerts at conf 0.01 on 23 FURG clips. E9 §2.4
  **branch 2** fired: that channel's zeros are **uncharacterised**, not measured,
  and it leaves the allocation.
- `run_batch.py` has recorded since **2026-08-26** that `RunningChecker` fires
  only on vertical image motion in its deployed configuration
  (`analysis/alert_parity.md` §5) — a property of the system, not a defect.

**What E10 does with those facts: nothing.** It changes no θ grid, no clip list,
no ground truth, no matching rule, no interval method, no weight, and **no
admission rule**. X3b's result stands as E9 §1.4 already decided it, whatever
E10 returns.

---

## 1. Why this is not moving the goalposts

SFCTL exposed an asymmetry that is now on the page: two channels report zero
coverage, and **only one of them has been asked whether it can report anything
else**. SmokeFire was asked and failed. Running has never been asked.

The dishonest move available here is to demand a positive control of Running
*because* its zero is inconvenient, and then to treat a failure as grounds for
withdrawing a result already admitted under a registered rule. E10 forecloses
that explicitly:

> **E10 cannot remove RunningChecker from the allocation.** E9 §1.4 branch 1
> admitted it on a criterion — `side_calls_with_boxes ≥ 1` — that is already
> satisfied and is not reopened. E10 measures the **grade of evidence** behind
> the zero, and grade of evidence is reported, not used to retro-fit admission.

Changing an admission rule after seeing the result it governs is what
`GT_PROTOCOL.md` §11 forbids, and it is forbidden here in the file that would
otherwise be the vehicle for it.

---

## 2. The run

| held fixed | value | provenance |
|---|---|---|
| clip list | the **same 14 VIRAT clips** as X3b | `exsitu/virat/CLIPLIST_virat.csv` |
| ground truth | 16 `person_running(type10)` events | `GT_running_virat.csv`, `d1cb596f6c67e6102ed3fc370c19ca9e7ab8fc2c68dd5e337ef06f4ee5d1f260` |
| modules | `intrusion,running` — Intrusion for boxes only, contributing no number | as X3b |
| image, dedup, cooldowns, virtual clock | unchanged | pinned digest `sha256:2f41e503…` |

**The single change:** `run_vel_threshold` = **0.01**, deliberately **below** the
registered grid {0.03, 0.045, 0.06, 0.08, 0.10}, chosen as "essentially any
vertical motion at all" rather than as a candidate operating point — the same
construction, and the same reasoning, as SFCTL's 0.01.

Estimated cost **≈ 0.5 h** of device time: one pass over the 2.26 video-hours
X3b measured five times.

---

## 3. Status of the point, fixed before it runs

> **E10 is instrument validation, not a measurement.**
> The point at 0.01 does **not** enter any Pareto front, coverage table, recall
> curve, sensitivity analysis or allocation. It appears as **one sentence** in
> §IV or §S5 about whether the alert path fires, and nowhere else.

Printing a below-grid point as a coverage number is extending a registered grid
after seeing that the grid returned zeros — exactly what §9's anti-tuning clause
forbids, and exactly what SFCTL was fenced against. The fence is identical here.

---

## 4. The two-branch reading rule, fixed before the run

- **alerts > 0 at 0.01** → the alert path is sound. X3b's zeros keep the grade
  of evidence E9 §1.4 gave them and **gain** a positive control: coverage 0 on
  16 annotated running events at every registered θ, rule-of-three upper bound
  **3/16 = 0.1875**, with the path demonstrated capable of firing. The
  Limitations asymmetry sentence is then **removed**, because it no longer holds.
- **alerts = 0 at 0.01** → the alert path has never been shown to fire on any
  input. X3b's zeros **remain measurements** under E9 §1.4 — that rule is not
  reopened — but the manuscript must report that this channel, like
  SmokeFire, has no positive control, and the Limitations asymmetry sentence
  becomes a statement about **two** channels rather than one.

**There is no third branch**, and neither branch is conditioned on the *value*
of anything. A result of 0 at 0.01 may **not** be rescued with a lower
threshold, a different corpus, a different module list, or a synthetic clip,
without a new pre-registration carrying its own stated reason.

**Both outcomes are reported.** A run that is only reported when it is flattering
is not a control; it is a lottery ticket. This clause exists because the
temptation on the unflattering branch is to leave the run out of the paper
entirely, and that temptation is strongest for exactly the result that matters
most.

---

## 5. What E10 cannot settle

It cannot separate "the deployed velocity rule is insensitive to this corpus's
running" from "the checker's alert path is inert". VIRAT's running events are
mostly **lateral** motion across the frame, and the deployed rule keys on
**vertical** image motion (`analysis/alert_parity.md` §5) — so a zero at 0.01
is consistent with a working checker watching for something this corpus does not
contain. E10 answers exactly one question — *does the path fire* — and the
manuscript must not claim it answers more. A corpus with vertical-motion running
would answer the other question, and no admissible one has been found.

---

## 6. Scheduling

Queued **after M5**, which is the 48 h soak started 2026-09-10 16:28 and is
expected to finish about 2026-09-12 16:30. E10 is ≈ 0.5 h, leaving roughly eight
days before the hard deadline of 2026-09-20. It is queued behind rather than
ahead of the soak because the soak is the long pole and E10 is half an hour;
nothing about E10's result changes what M5 measures.
