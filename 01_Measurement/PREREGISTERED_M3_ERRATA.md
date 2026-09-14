# ERRATA to `PREREGISTERED_M3.md` (LOCKED)

**Written 2026-09-03, 10:15 +07:00**, after the VIRAT download and before any
VIRAT clip was scored.

`PREREGISTERED_M3.md` is locked at SHA256
`dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a` and is **not
edited**. Corrections live here, dated, in the same form the manifest correction
took: the signed artefact keeps its hash, and the appendix carries the change.

---

## E1 — the VIRAT running corpus is **14 clips**, not 15

**Where the wrong number appears:** `PREREGISTERED_M3.md` §3-continued
("Final VIRAT running GT: 16 events across 15 clips"), the K3 roster line
("16 events, VIRAT type 10"), `CHECKPOINT_2B_PRE_DECISIONS.md` K5 ("VIRAT tải
15 clip"), and `RUN_QUEUE.json` job `X3` as first written.

**What is true.** Counted from the ground-truth file of record,
`exsitu/virat/GT_running_virat.csv` (SHA256 `d1cb596f6c67e6102ed3fc370c19ca9e7ab8fc2c68dd5e337ef06f4ee5d1f260`, unchanged):

| quantity | value |
|---|---:|
| events (rows) | **16** |
| **distinct clips** | **14** |
| clips carrying two events | 2 (`VIRAT_S_050000_08_001235_001295`, `VIRAT_S_050300_01_000148_000396`) |
| total annotated running time | 108.9 s |

**How the 15 survived.** The exclusion chain was 22 raw type-10 annotations →
17 after P8's 20 s merge → 16 after §4.5's 1.0 s minimum duration. The event
that §4.5 removed lasted 0.033 s — a single annotated frame — and it was the
**only** event in its clip, `VIRAT_S_010004_06_000547_000715`. So the clip left
the corpus with the event. The event count was decremented three times and the
clip count was never decremented at all.

**Nothing else changes.** The 16 events, the 108.9 s, the GT hash, the ≥10-event
admission rule of B6 and RunningChecker's place in the allocation are all
unaffected: they are properties of the events, not of the clip count. What
changes is the denominator of any per-clip statement and the number of files the
ex-situ Running job must find.

**How it was caught.** `scripts/fetch_virat.py` derives its download list from
the ground-truth file rather than from the prose, and reported
`fetched 14/14 clips, missing 0`. The mismatch against the expected 15 is what
surfaced the error. That is P9 working as intended: **a countable quantity that
a script counts from the file of record cannot silently disagree with the file
of record — only a typed one can.**

This is the same shape as the manifest-duration bug of 2026-09-02 (a
correct-looking total over corrupt parts) and the "22 → 17" slippage recorded in
Draft 2: a number carried forward through a chain of corrections while one of
its components stopped being true. Three instances in two days is no longer a
coincidence, and the single sentence for the Discussion is *a derived count must
be re-derived after every exclusion, not adjusted*.

**Consequences applied 2026-09-03 10:20 +07:**

- `RUN_QUEUE.json` job `X3`: required inputs 15 → **14** clips, `done_check`
  75 → **70** results (14 clips × 5 θ). Without this the job would have blocked
  for ever waiting for a fifteenth file that does not exist and should not.
- The manuscript says **14 clips, 16 events**, and reports the exclusion chain
  including the fact that one exclusion emptied a clip.

**Clip list actually downloaded**, with sizes and SHA256:
`exsitu/virat/CLIPLIST_virat.csv` on the Jetson, fixed before any clip is
scored (§8.2). Source: Kitware Girder public API, no form, no e-mail.


---

## E2 — the 24 + 8 sample is drawn **after** M1+ finishes, and why that is not peeking

**Registered 2026-09-03 10:40 +07, before the draw.**

`PREREGISTERED_M3.md` A2 requires the occupancy stratum to be `ai_frames == 0`,
read from the M1 run metadata. That metadata exists only for segments M1 has
measured, so the draw executes as campaign job `S1`, after M1+ reaches 175/175 --
by which time the false-alarm rate at the frozen θ is known for every segment in
the corpus.

**The sentence that has to be on the record, because the obvious question is
"you drew the sample after you saw the numbers":**

> The sample is produced by `scripts/draw_sweep_samples.py` from the seeds
> registered before any of it existed (20260902 for the 24-segment sweep sample,
> 20260903 for the disjoint 8-segment verification sample). Its only inputs are
> the manifest and the three registered stratification variables --- view,
> day/night, and `ai_frames == 0`. **The false-alarm rate is not an input, is not
> read by the script, and no segment is chosen or rejected by hand.** The draw is
> reproducible from the manifest and the run metadata alone by anyone who has
> them, which is the property that makes the timing irrelevant.

Two further guards, both already in the script:

- it **refuses to draw** on fewer than 175 segments of metadata, so the stratum
  cannot quietly degrade into "measured versus not measured";
- disjointness holds **by construction** --- the verification sample is drawn
  from the segments the sweep draw did not take --- and is checked again
  afterwards, and a violation is a non-zero exit rather than a warning.

The draw also costs nothing in schedule: C1 already depended on M1+, so waiting
for the stratum spends no machine time that was otherwise available.

The written record of the draw is `ops/samples/*.meta.json` (seed, rule, per-cell
availability and quota, timestamp) plus the SHA256 of each list, all produced by
the script at the moment of drawing.


---

## E3 — the frame-count check is a note with a magnitude, not a pass/fail rule

**Registered 2026-09-03 11:25 +07, after the rule failed and before any rate
was recomputed.** This is an amendment made *after* seeing the rule fail, so it
is written down with the distribution that justifies it rather than applied
quietly in a script.

**What was written first.** `scripts/check_segment_output.py` was written on
2026-09-03 to verify the segment measured while two engines were briefly on the
device (KNOWN_ISSUES HARNESS-6). One of its checks was
`frames_read == frames_in_file`, failing any segment where the decoder consumed
fewer frames than the container holds.

**What running it over the corpus showed.**

| | |
|---|---:|
| segments checked | 77 |
| segments with a trailing-frame shortfall | **10** |
| shortfall range | **1 to 10 frames** |
| largest shortfall as a fraction | **0.048 %** |
| largest shortfall in time | **0.76 s** at 11.9 fps |
| days on which it occurs | **four** (27, 28, 29, 31 August) |
| decoder log | `[h264] error while decoding MB …` on the affected files |

The shortfall is a property of the footage: the recorder stores the camera's
own H.264 bitstream with `-c:v copy`, damaged trailing macroblocks and all, and
the decoder stops where the stream stops being decodable. It predates the
two-engine incident by four days, occurs on days with no incident at all, and
the segment measured during the incident carries the *smallest* shortfall in
the set (1 frame, 0.004 %).

**Amendment.** The check becomes a **note that reports the magnitude** — frames
short, fraction, and seconds — and fails only above **1 %**, which is a real
truncation rather than a ragged tail. Ten frames at 15 fps is 0.7 s against the
registered matching window W = 2.0 s, so no shortfall in this corpus can move
an alert across a matching boundary.

**Why the amendment is legitimate rather than convenient.** It changes no
decision: no θ grid, no seed, no sampling rule, no admission rule, no ρ, and no
reported rate. It changes a check *this session invented*, and the alternative
was a rule that failed 13 % of a corpus for a 0.04 % shortfall — a rule that
punishes the measurement for describing the data accurately. Under the errata
boundary registered in GT_PROTOCOL section 11, a descriptive threshold on an
already-existing property is exactly what an errata may amend.

**The consequence that outlives the rule** is registered separately and is the
more important half: GT_PROTOCOL **5.8** — observation time is
`sum(frames_read / fps)` over measured segments, and a manifest duration is
descriptive only.


---

## E4 — **not here.** The clock-substituted stratum is a *decision*, so it is a pre-registration

**Pointer written 2026-09-05 10:20 +07.** A reader working through E1–E3 looking
for E4 needs to be told where it went and why it is not in this file.

The eleven segments of 2026-08-31 08:00–13:00 that HARNESS-5 found with corrupt
container timing decode with `[h264] error while decoding MB …` throughout, and
9 % slower than the healthy group. A decoder recovering from damaged macroblocks
can hand the detector a frame that was never in the room, so their alerts may be a
property of the **recorder** rather than of the **scene** — which puts the in-situ
false-alarm measurand at risk and calls for a rule fixed before the numbers exist.

That rule can **remove eleven segments from the denominator of a reported rate**.
Section 11 of GT_PROTOCOL says an errata "may never change a decision … not an
**admission rule**", and that filing one here would make this file the back door
that clause exists to close. So the rule is registered as its own locked
artefact:

> **`PREREGISTERED_E4_CLOCK_STRATUM.md`**
> locked 2026-09-05 10:20:43 +07,
> SHA256 `2371fef5b718f76f3702d682f4a07ccf8170c89784deca20e9d5214eeb958885`,
> with its own row in GT_PROTOCOL section 11.

It keeps the name **E4** because that is what the working record calls it. It is a
pre-registration wearing an errata's name, not an errata — and the reason it is
not one is itself worth the paragraph: **the boundary only means anything the
first time it is inconvenient.**

Its section 4 also corrects, before locking, an honesty clause that had been
drafted wrong — the alert total of one of the eleven had already been read and
published in `STATUS_CHECKPOINT.md` an hour earlier, so the registration is
declared as **informed on 1 of 11**, not blind.

---

## E5, E6, E7 — where they live

**E5** is a *decision* (two θ grid rows withdrawn), so it is not here either:
`PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md`, locked 2026-09-06, SHA256
`60aaa61bea38cbc54388c250107942f4ac96dbbbdf1f00b2793d43748ae8c41a`, with its own
row in GT_PROTOCOL section 11, plus an addendum registering the M4e matrix
(`PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.md`,
`6fd7fdb372fe85b643ab208470815cffbefe9c7cbc5ae23d09030d0ea9d2da15`).

**E7** is a decision too — a gate, a threshold and a branch rule for the C1b
recorder pilot — so it is `PREREGISTERED_E7_C1B_PILOT.md`, locked 2026-09-07
13:25:21 +07, SHA256
`78ff9ec16543da647803fa80d99b1126565d340ae63729a0be4ec30e1e854fdf`.

**E6 belongs here, and it is the only one of the three that does**, because it
changes nothing: it restates a rule already signed.

## E6 — the spot-check voiding rule, restated where the FAR(θ) work will look for it

**Written 2026-09-07.** This is not a new rule and admits nothing. It repeats,
in the place the θ-sweep work will actually read, a condition already carried by
`GT_PROTOCOL.md` §5.5 and by the signed blanket negative declaration.

> A single **`REAL_EVENT`** found in the Fall or Helmet spot-check **voids that
> class**. The declaration for that class stops being a false-alarm denominator,
> and every rate already computed for it — including every point of FAR(θ)
> produced by C1/C2, C1b or V1–V5 — must be recomputed with the real events
> removed from the numerator, or reported as an **alert rate** rather than a
> false-alarm rate.

Two things follow that are worth naming, because they are the reason this is
written down before the labels are filled rather than after:

1. **The spot-check is the mitigation for a disclosed protocol violation, not a
   formality.** The declaration was signed *after* the declarant had been shown
   aggregate alert counts for the same span — `GT_PROTOCOL.md` §5.5 condition 1,
   violated and disclosed. The classes where that disclosure genuinely bites are
   Fall, Running and SmokeFire. The spot-check is what converts the declaration
   from an assertion into something falsifiable.
2. **The 132 label cells are therefore upstream of the FAR numbers, not
   downstream of them.** 100 Intrusion images, 12 Fall alerts, 20 Helmet alerts,
   all still blank as of 2026-09-07. Until they are filled, every in-situ Fall
   and Helmet rate in this campaign is provisional in exactly this sense — and
   `ops/c2_mode.json` carries the same clause so the pipeline states it too.

---

## E7 — ρ = 0.494 is **not the median** of OmniFall Table 2. The value stands; the word does not

**Written 2026-09-10, 13:10 +07:00**, after `count_everything.py` computed the
median of the source table for the first time and disagreed with every document
that quotes it. Filed here rather than in the locked files, under the rule
`GT_PROTOCOL.md` §11 and this errata's own preamble: **a descriptive count may
be corrected in a dated errata; a decision may not.** This is the first kind.
Nothing below changes a grid, a seed, a sampling rule, an admission rule, or a
bound.

### Where the wrong word appears

| file | line | text |
|---|---|---|
| `GT_PROTOCOL.md` §9 | 746 | *"**Primary: ρ = 0.494**, the median of those seven"* |
| `GT_PROTOCOL.md` changelog v1.3 | 778 | *"ρ = 0.494 (median of OmniFall … Table 2's seven staged→wild sensitivity ratios)"* |
| `PREREGISTERED_M3.md` | 206 | *"lower bound = upper × **ρ = 0.494**, the median staged→wild sensitivity ratio"* |
| `PREREGISTERED_M3.md` | 683 | *"ρ = 0.494 is the median staged→wild sensitivity ratio of a fall classifier"* |
| `exsitu/OMNIFALL_TABLE2_DEGRADATION.md` | 38 | *"min 0.080, **median 0.494**, max 0.568, mean 0.301"* |
| `exsitu/EXSITU_RESULTS_gmdcsa24.md` | 74 | *"(ρ = 0.494, median of OmniFall Table 2)"* |

**None of the four locked lines is edited.** `GT_PROTOCOL.md` and
`PREREGISTERED_M3.md` keep their hashes. The two derived extracts are corrected
in place, because they are transcriptions and a wrong transcription is not a
record of anything.

### What is true, computed from the table itself

The seven ρ values of OmniFall Table 2, class `Fall`, sorted:

    0.080  0.087  0.156  0.164  0.494  0.560  0.568
                            ^^^^^ median

| statistic | value | the documents say |
|---|---:|---|
| min | **0.080** (CAUCAFall) | 0.080 ✔ |
| **median** | **0.164** (UP-Fall) | 0.494 ✘ |
| mean | **0.301** | 0.301 ✔ |
| max | **0.568** (Le2i) | 0.568 ✔ |
| **GMDCSA24** | **0.494** | quoted as the median ✘ |

Three of the four statistics in the summary line are right. The fourth names
the wrong order statistic, and 0.494 is the row for **GMDCSA24**.

### Why this changes no number and no decision

1. **The registered bound is unchanged.** §9 registers *lower = upper × ρ* with
   ρ = 0.494 and **the full range [0.080, 0.568] carried through the sensitivity
   analysis**. Both endpoints are correct and both were correct when signed. The
   allocation is reported **across the whole range**, so no reported quantity
   was ever a function of the label attached to 0.494.
2. **The value was well chosen for a reason nobody wrote down.** 0.494 is the
   staged→wild ratio for **GMDCSA24** — the corpus this campaign actually
   replays to measure fall coverage. A central value taken from the corpus being
   scored is a *better* justification than a median over six datasets this work
   never touches, and it is the justification that was true all along.
3. **It is not a post-hoc rescue.** The number does not move: 0.494 before, 0.494
   after. Only the sentence explaining it moves, and it moves towards the
   stricter reading, not the looser one. Had the correction *changed* ρ, it
   would belong in a new pre-registration and not here.

### What was done

- `count_everything.py` now emits `rho_median` (**computed**, 0.164),
  `rho_central` (0.494) with `rho_central_dataset` (GMDCSA24) and
  `rho_central_why`, and `rho_doc_summary_disagrees`, and prints a NOTE on
  every run for as long as a source document contradicts its own table.
- `rho_band_line` deliberately quotes **no** median.
- The manuscript prints min, central and max together and states that the
  allocation is swept over the whole range.
- `scripts/theta_vs_lambda.py`'s `RHO` comment is corrected from "median" to
  the GMDCSA24 reading. The tuple `(0.080, 0.494, 0.568)` is unchanged.

**Registered anti-tuning check.** This errata is written while `X3b` is running
and no allocation exists on disk (`ops/lists/allocated_theta.json` absent), so
no result could have suggested it. It was produced by a counter, not by a
reading of an outcome.
