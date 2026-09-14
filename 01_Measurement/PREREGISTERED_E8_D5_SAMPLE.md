# PREREGISTERED E8 — the D5 sample, and the withdrawal of upgrade rule U1

**Locked 2026-09-09, author decision, before job D0 ran.**
Registered under GT_PROTOCOL §11 as a **new locked pre-registration**: it binds
which corpus §IV.D's allocated operating point is verified on, and it withdraws
a registered upgrade rule. §11 forbids an errata from changing a decision, so
this is a pre-registration and not an errata.

**Written before D0 finished.** Verified on the Jetson at 2026-09-09 10:45:35
+07, immediately before this lock: `D0` is `PENDING` with `V5` `RUNNING` at 3 of
8 segments; `out/d0_allocation/` does not exist; `ops/lists/allocated_theta.json`
does not exist; `D5s` is `PENDING`; `D5f` is `SKIPPED`; and every entry in
`policy.upgrade_rules` carries `applied = null` — `apply_upgrade_rules()`
evaluates `U1` on the first pass after `D0` reaches `DONE`, which had not
happened. `ops/lists/d5_32seg.list` **does** exist, built ahead of time on
2026-09-08 by `ops/make_d5_32seg.py` and hashed
`8ca63e4115d3661d4e01df6123ce0d889180a0a861b873824ba965a59705bfe6`; `D5s.cmd`
rebuilds it at job start and it must hash to that same value. That ordering is
the point: the rule is withdrawn before the projection that would have fired it
exists.

**Modifies** `PREREGISTERED_M3.md`
(`dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a`, LOCKED
2026-09-03 09:40 +07) only by withdrawal, never by rewriting: the text of U1
stays exactly as it was written there and in `RUN_QUEUE.json`, and this file is
the record of it being withdrawn. Nothing in M3 is edited.

---

## 0. Honest declaration of what had already been read

Registering a sample rule after measurements exist is exactly the move this
protocol is built to prevent, so what was on the table when this was written is
listed rather than glossed.

**Read before this file was written:**

- `measured_rtf` and every per-job realtime factor (HARNESS-23, this morning):
  in-situ 0.7734 against the daemon's 0.9221.
- V1–V4 complete, V5 at 3/8. Their per-segment metadata, alert counts and
  admissibility checks.
- C2's reproduction gate: 24 segments, 12 exact, all three checkers
  `stateful_divergence`, **0 curve points emitted**.
- Ex-situ alert counts at every registered θ: SmokeFireChecker **0 alerts at all
  five θ** on FURG, RunningChecker **0 alerts at all five θ** on VIRAT,
  IntrusionChecker Layer-1 person recall 0.630–0.740 across the conf grid,
  FallChecker alert counts 107/49/27/14/2 across its five θ.
- FallChecker ex-situ **recall is not yet scored**. `score_exsitu.py` has not
  been run on X4. No recall(θ) curve exists for the class this file's sample
  most affects.

**What this file decides, against that background.** It decides one thing: that
the allocated operating point is verified on the registered 32-segment sample,
24 of which chose it and 8 of which did not, rather than on the whole corpus.

**Why that decision cannot have been bought by the numbers above.** The 8
out-of-sample segments are `verify_sample_4h.list` — the same 8 that V1–V5 run —
and the 24 are `sweep_sample_12h.list`, drawn by job S1 on 2026-09-03 under M3
§A2 before any of this existed. Both sets were fixed before any θ was chosen.
The decision here is *which of two already-registered options runs*, and it
selects the **smaller** corpus, the one that measures less footage and produces
the weaker headline number. A decision that gives up 143 segments of measurement
is not a decision the above numbers could have tempted anyone into.

**What this file does NOT decide.** It does not choose θ. It does not touch
recall, FAR, the Pareto front, the budget, the weights, or which propositions
apply. It does not touch U2 or U3. Those remain exactly where they were.

---

## 1. The decision

> **Upgrade rule `U1-D5-full-corpus` is withdrawn. `D5f` is SKIPPED
> permanently. `D5s` runs.**

## 2. The reason, which is scientific and not schedule

`D5s` verifies the allocated θ on **32 segments: 24 + 8, disjoint by
construction.**

- The **24** are `sweep_sample_12h.list`. They are the segments C1 recorded and
  C2 swept. They are how the operating point was *chosen*.
- The **8** are `verify_sample_4h.list`. Nothing in the selection chain has ever
  read them at the allocated θ.

Those 8 segments are the only evidence in the entire campaign that the allocated
operating point works on data that was **not used to choose it**. That is the
whole content of the sentence §IV.D wants to be able to write. Its value comes
from the disjointness, not from the segment count.

`D5f` runs the allocated θ on all **175** segments. The 24 and the 8 are both
inside 175. Run that way:

1. The out-of-sample property **does not survive**. There is no subset of the
   D5f output that is out-of-sample, because the pass is the corpus and the
   corpus contains the selection set. Reporting "8 of these 175 were
   out-of-sample" after the fact is reporting a partition chosen after seeing
   the result, which §11 and P1 both forbid.
2. `ops/lists/d5_32seg.list` is **never exercised**. `D5s.cmd` rebuilds that
   file as its first command, so the run itself re-derives it and it can be
   hashed against the copy built ahead of time on 2026-09-08
   (`8ca63e4115d3661d4e01df6123ce0d889180a0a861b873824ba965a59705bfe6`, source
   16 of `LINKS.md`, asserted byte-identical to the `cat` D5s performs, with 32
   ids, two disjoint samples, no repeats, 32/32 in the closed manifest and 32/32
   on disk). `D5f.cmd` builds `d5_full.list` from a directory listing instead
   and never touches the checked list. Withdrawing D5s substitutes an unchecked
   denominator for a checked one, and removes the hash comparison that would
   have caught a redrawn sample.
3. `D5f`'s own registered note says it is *"reported as an ADDITIONAL labelled
   row; it never restates the 32-segment number"* — but `U1` as written carries
   `"disable": ["D5s"]`, which removes the row it promised to leave standing.
   The rule and the note contradict each other. This file resolves that
   contradiction in favour of the note.

**So `D5f` is not an upgrade.** It is a *different and weaker claim*: more
footage, no out-of-sample evidence. Trading a claim about generalisation for a
claim about volume is a downgrade whatever the segment count says, and the
registered fallback was registered precisely so that this trade would never be
made unattended by a projection.

**This reason is independent of throughput.** It holds if the machine runs at
0.5× real time and it holds if it runs at 2×. Nothing in §2 depends on
`measured_rtf`, on any ETA, or on the 2026-09-20 deadline.

## 3. The secondary reason, recorded for completeness and NOT load-bearing

`Queue.measured_rtf()` divided each job's **registered** `est_video_h` by its
**measured** `actual_h`. For a resumed pass those describe different segment
sets: C1's 2026-09-08 resume measured 1 segment and SKIPped 23 already-measured
ones, so 12.0 registered video-hours were divided by 0.735 h of wall clock and
the queue recorded `rtf = 16.3265` for a device that has never exceeded 0.84.
That one row lifted the aggregate to 0.9221 against a true in-situ 0.7734 —
**about +19%, in the optimistic direction**. Full working: `KNOWN_ISSUES.md`
§HARNESS-23, `ops/RUN_DASHBOARD_ANALYSIS.md` (2026-09-09 block),
`ops/rtf_by_job.py`.

`U1` compares `project(only={D5s, M4e, M5})` against 2026-09-12T23:59:59.
Evaluated after D0 at the two figures:

| `measured_rtf` | D5s | M4e | M5 | total | projected ETA | U1 |
|---|---:|---:|---:|---:|---|---|
| 0.9140 (queue, after V5) | 17.6 | 15.4 | 48.0 | 81.0 h | 2026-09-12 22:30 | **fires** |
| 0.7734 (correct, in-situ) | 20.8 | 18.2 | 48.0 | 87.0 h | 2026-09-13 04:31 | does not fire |

**This is recorded, and it is deliberately not the reason.** The distinction
matters and is stated so it cannot be blurred later:

> If §3 were the only reason, the correct action would be to **fix the number
> and let U1 evaluate again** — not to withdraw the rule. A rule is not
> invalidated by being fed a bad input; the input is. Withdrawing a rule because
> its input was wrong, when the corrected input would have produced the same
> answer one wants, is choosing an outcome and finding a procedure for it
> afterwards.

The rule is withdrawn on §2 alone. §3 explains why the withdrawal had to be
decided **today, before D0**, rather than at leisure: with the uncorrected
figure the rule would have fired within the hour on a margin of about 1.5 hours.
§3 sets the deadline. §2 sets the decision. Had §2 not held, the answer to §3
would have been to restart with the corrected `measured_rtf` and abide by
whatever U1 then decided.

## 4. What changes, exactly

| artefact | change |
|---|---|
| `RUN_QUEUE.json` → job `D5f` | `status` stays `SKIPPED`, permanently; `note` records the withdrawal; `adjudicated` names this file and its SHA |
| `RUN_QUEUE.json` → `policy.upgrade_rules[U1-D5-full-corpus]` | disabled in the form the daemon honours, with the original text preserved verbatim alongside |
| `RUN_QUEUE.json` → job `D5s` | **unchanged**, stays `PENDING`, still blocked on `ops/lists/allocated_theta.json` |
| `PREREGISTERED_M3.md` | **not edited.** U1's text stands there as written; this file is the withdrawal record |
| upgrade rules `U2-M4-remaining-cells`, `U3-soak-72h` | **not touched** |

## 5. U2 and U3 are untouched, and here is why that is consistent

`M4x` and `M5x` are additive: they add ablation cells and soak hours to results
that already stand. Neither replaces a registered artefact, neither disables
another job, and neither can remove a property from a measurement that was
designed to have it. They are upgrades in the sense U1 was not.

They are also **insensitive to `measured_rtf`**, so the §3 defect never reached
them: U2's `eta_scope` is `["M5"]` and U3's is `[]`, and `M5` carries no
`est_video_h`, so `project()` never rescales it. They would evaluate identically
at 0.77 and at 0.92.

Whether `M4x` and `M5x` are worth running is therefore left open, to be decided
**by the author at Checkpoint 3 on content, not on schedule**. For the record,
schedule does not constrain the choice: at the corrected rtf the whole tail
including both upgrades lands about 2026-09-15, roughly 5.8 days inside the
2026-09-20 deadline.

## 6. What the manuscript must say

§IV.D reports the allocated operating point verified on **32 segments (24 in
the selection sample, 8 out-of-sample)**, and says that the whole-corpus
alternative was registered, was available, and was **withdrawn before it could
be triggered**, because running it would have dissolved the out-of-sample split.
The withdrawal is a limitation of scope and is reported as one: D5's verification
covers 15.2106 h of footage, not 83.94 h.

## 7. Anti-tuning clause

This withdrawal may not be reversed after any allocation has been computed. If
the whole-corpus pass is later judged worth running, it runs as an **additional
labelled row** alongside the 32-segment result, never in place of it, and never
by re-enabling a rule that disables `D5s`. Any such run requires a new
pre-registration, a stated reason, and recomputation of every affected table.
