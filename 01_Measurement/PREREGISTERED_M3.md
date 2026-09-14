# PRE-REGISTERED THRESHOLD SWEEP (M3) — **LOCKED 2026-09-03 09:40 +07**

**Written 2026-09-02, 20:10 +07:00.** At the time of writing: **no Pareto curve
exists for any checker**, no allocation has been computed, and no sweep has been
run. Every decision below is therefore fixed before the quantity it governs
exists — the discipline of rule E3 and of §9.

> **STATUS: DRAFT for the author's review.** This file is **not** locked and has
> **no SHA256 yet**. The author reads it, changes what should change, and only
> then is it hashed and frozen. Locking it before review would make the
> registration a formality instead of a commitment.

---

## B1. The θ grid — one primary parameter per checker

One parameter per checker, chosen as the one that actually trades false alarms
against coverage. Every other parameter stays at its frozen deployed value. Grids
are five points and **each contains the frozen value**, so the deployed
configuration is always one point on its own curve rather than an extrapolation.

Values read from the code in the pinned image, not from the manuscript:

| Checker | Primary θ | Source line | Frozen value | **Registered 5-point grid** |
|---|---|---|---|---|
| **FallChecker** | `fall_angle_threshold` (deg) | `fall_check.py:36` `"fall_angle_threshold": 60.0` | **60.0** | 45, 52.5, **60**, 67.5, 75 |
| **RunningChecker** | `run_vel_threshold` (norm/frame) | `running_check.py:33` `"run_vel_threshold": 0.06` | **0.06** | 0.03, 0.045, **0.06**, 0.08, 0.10 |
| **SmokeFireChecker** | `confidence_threshold` | `smoke_fire_check.py:41` `"confidence_threshold": 0.5` | **0.5** | 0.30, 0.40, **0.50**, 0.60, 0.70 |
| **ForkliftSpeedChecker** | `pixel_speed_threshold` | `forklift_speed_check.py:55` `"pixel_speed_threshold": 0.12` | **0.12** | 0.06, 0.09, **0.12**, 0.16, 0.20 |
| **HelmetChecker (A0)** | `per_class_conf[2]` (no-helmet class) | `helmet_check.py:25` `_SPRINT_V23_DEFAULTS = {2: 0.30, 6: 0.15}` | **0.30** | 0.15, 0.22, **0.30**, 0.40, 0.50 |
| **EnhancedHelmetChecker (A1)** | `crop_conf` | `enhanced_helmet_check.py:27` `crop_conf default 0.08` | **0.08** | 0.04, 0.06, **0.08**, 0.12, 0.16 |
| **IntrusionChecker** | detector `conf` for `person` | pipeline-level `--conf`, deployed 0.25 | **0.25** | 0.15, 0.20, **0.25**, 0.35, 0.45 |

**Why one parameter and not a joint sweep.** A joint sweep over two parameters
per checker is 25 points per checker and roughly 175 runs; at the measured
throughput (B9) that is far beyond the machine budget, and it would buy a surface
where the paper needs a curve. One-at-a-time is registered here **as a
limitation, not as a claim of separability**, and the manuscript says so.

**IntrusionChecker's parameter is the detector confidence, not a module
threshold**, because `intrusion_check.py` has no threshold of its own — it fires
on any tracked `person` inside the region, and the region is the whole frame.
That is itself worth reporting: the only knob that changes intrusion behaviour is
upstream of the module.

---

## B2. In-situ sweep sample

Sweeping all 175 segments at 5 points × 7 checkers is not affordable (B9). The
sweep runs on a **registered stratified sample**.

- **Sweep sample: 24 segments ≈ 12 h.**
- **Strata: view (A/B) × day/night × occupancy (occupied/empty).** Up to 8 cells;
  **≥2 segments per non-empty cell**; the remainder allocated proportionally to
  cell hours.
- **Seed 20260902**, recorded, drawn with `random.Random(seed).sample` after
  sorting segment names, so the draw is reproducible from the manifest alone.
- Output: `analysis/sweep_sample_12h.csv` + **SHA256 of that list**, both fixed
  **before the first sweep run**.

**Verification sample: 8 segments ≈ 4 h, drawn by the same rule with the same
strata but seed 20260903, and DISJOINT from the sweep sample.**

*Decision and reason, registered:* disjoint, **not** a subset. A subset would
verify that the curve reproduces on data that helped locate it, which is the
question nobody is asking. The verification sample exists to answer "does the
operating point chosen on the sweep sample behave the same on footage it never
saw", and only a disjoint draw answers that. The cost is 4 h of extra machine
time and it is worth it.

**Blocking dependency:** the occupancy stratum needs the author's occupancy
answers. Only one window is currently declared (2026-08-28 08:00–10:30). If no
further occupancy information arrives, the occupancy dimension **collapses to
two strata** (that window vs everything else) and the draw is re-registered with
that reduced design, before running.

---

## B3. Record-then-rescore, and what may be reported from it

Registered unchanged from Checkpoint 1b-late:

1. The recording pass runs at the **loosest θ** in each grid, with
   `--record-candidates`, capturing every pre-confirm, pre-dedup violation.
2. The replayed curve **locates** candidate operating points. It is a search
   tool.
3. **Every number in a results table comes from one real engine run at exactly
   that θ.** No reported figure is produced by replay.
4. The **replay-to-real fidelity is measured at every reported point and
   published beside the curve**, not summarised as "good agreement".

The reason this is not negotiable is already measured: changing the confidence
floor changes which detections ByteTrack associates (219 track ids at the floor
against 149 at the reported threshold), and both temporal confirmation and dedup
key on track identity. No replay can undo that. The noise-floor result of §8.8
sharpens the point — the pipeline is bit-exactly deterministic given identical
input, so replay divergence is entirely a property of the changed input, not of
run-to-run variation.

**Tooling check (required before Phase C):** `scripts/verify_operating_points.py`
exists and implements exactly this contract. It has **not** been run against the
current runner. **Action registered: run it on one segment, both `--dry-run` and
`--run`, record wall time, before any sweep is launched.** If it no longer
matches the runner's interface, it is fixed *before* the sweep, not after.

---

## B4. Verification points

**Three per checker: loosest, middle, tightest of its grid — plus the frozen θ**
(four runs where the frozen value is not already one of the three).

- One-at-a-time: all other checkers held at frozen values.
- Between measured points the curve is **interpolated**, and every interpolated
  region is drawn with the **fidelity bound** from B3 attached, so a reader can
  see which parts of the curve are measured and which are inferred.
- No operating point is reported from an interpolated region.

---

## B5. Ex-situ sweep, and the source situation

Ex-situ runs the **same θ grid**, and **every point is a real run** — there is no
record-then-rescore on the ex-situ side, because the corpora are small enough to
run directly.

For Fall, each θ additionally reports **recall(L)** for L ∈ {0, 1, 2, 3, 5, 10} s,
as measured in I3.

### Source availability, tested 2026-09-02 under the 15-minute rule

| Source | For | Result | Decision |
|---|---|---|---|
| **CUHK Avenue** | Running | downloaded, **813 MB**, zip verified; 21 test + 16 train `.avi`; GT = `volLabel`, a **per-frame binary mask** cell array | ❌ **INADMISSIBLE — see below** |
| **VIRAT Ground** | Running + Intrusion | `viratdata.org` reachable; data via `data.kitware.com` API, direct, no form; VIRAT ships **named activity annotations**, not binary anomaly labels | ✅ **the one real candidate; enumeration still to do** |
| **ShanghaiTech Campus** | Running / Intrusion | reachable; Google Drive / OneDrive links | ⚠️ same annotation problem as Avenue is likely — anomaly detection corpus, frame-level binary labels. Verify before spending time |
| **UMN** | Running | direct `.avi` links, but they are demo clips; the corpus is crowd-escape events with binary labels | ⚠️ same problem likely |

### ❌ Avenue is rejected, and the reason is a **third kind** of exclusion

Avenue costs nothing, needs no form, is frame-accurate video, and is still
unusable — because **its ground truth labels "abnormal", not "running"**. The
`.mat` files contain one variable, `volLabel`, a cell array of per-frame binary
masks. Avenue's anomalies mix running, throwing objects, wrong direction,
loitering and skipping, and **no per-class label is distributed**.

To get a RunningChecker recall from it we would have to decide ourselves which
anomalies are running. That is writing our own ground truth, which §8.1 forbids
outright, and §8.4 already anticipated this case: *a source whose annotation
granularity cannot support the matching rule is declared inadmissible rather
than accommodated.*

(Its demo code also states "for non-comercial use only" — a licence restriction —
but the annotation problem alone is decisive.)

**So the source taxonomy has three exclusion classes, not two, and this is worth
reporting as a finding about the field:**

1. **needs permission** — CMDFall (email), MCFD (bot protection);
2. **images only** — every open helmet/PPE corpus; cannot exercise the tracker;
3. **class-agnostic annotation** — Avenue, and probably ShanghaiTech and UMN:
   open, free, video, frame-accurate, and still unable to answer "how often does
   this checker catch *this class of event*".

Category 3 is the one nobody warns you about. The anomaly-detection literature
has produced a great deal of open video whose labels answer "was something odd
happening" — a question no per-checker recall can be built from.

**Consequence, registered:** unless VIRAT delivers named activity labels,
**RunningChecker is FAR-only** and does not enter the allocation. That is now the
expected outcome rather than a risk.

---

## B6. Which checkers enter the allocation

**Rule, registered now:** a checker enters the allocation only with **≥10
positive ex-situ events** *and* **an in-situ false-alarm rate**. Fewer than 10
positives makes the recall interval so wide it carries no information; no in-situ
FAR means there is no spend side to trade against.

Status under the rule, on data that exists today:

| Checker | ex-situ positives | in-situ FAR | Verdict |
|---|---|---|---|
| **FallChecker** | **78** (GMDCSA24) | 0.4804/h | ✅ **enters** |
| **SmokeFireChecker** | **17** (FURG, fire sub-class only) | 0 obs, UL 0.1477/h | ✅ enters, interval very wide |
| **RunningChecker** | Avenue **rejected** (class-agnostic GT); VIRAT pending | 0 obs, UL 0.1477/h | ⚠️ **expected FAR-only** |
| **IntrusionChecker** | pending VIRAT | **alert rate only** — not declared negative | ⚠️ **alert-rate-only** unless §5.4 sample is annotated |
| **HelmetChecker (A0)** | 0 — image corpora only | 8.0468/h | ❌ **FAR-only** |
| **EnhancedHelmetChecker** | 0 — image corpora only | 0 obs, UL 0.1477/h | ❌ **FAR-only** |
| **ForkliftSpeedChecker** | 0 — no open source | 0 obs, UL 0.1477/h | ❌ **FAR-only** |

**At least 3 of 7 checkers cannot enter the allocation, and that is a reported
result**, not a gap: *a detector whose coverage cannot be measured cannot be
funded on any principled basis; it can only spend.*

---

## B7. The recall interval

Unchanged from `GT_PROTOCOL.md` §9 and not reopened here:

- upper bound = measured ex-situ recall at that θ;
- lower bound = upper × **ρ = 0.494**, the median staged→wild sensitivity ratio
  of OmniFall (arXiv:2505.19889v3) Table 2;
- full range **ρ ∈ [0.080, 0.568]** carried through the sensitivity analysis.

ρ and its citation go through `verify_refs.py` with every other reference.
Extraction and provenance: `exsitu/OMNIFALL_TABLE2_DEGRADATION.md`.

---

## B8. Fallbacks, with their trigger thresholds

Registered now so that a schedule slip cannot become a quiet reduction in rigour:

| Trigger | Fallback |
|---|---|
| Phase C projected **> 100 machine-hours** | verification points drop from 3 to **2 per checker** (loosest and tightest); the middle point is interpolated with its fidelity bound shown |
| **D5 cannot finish** before the writing window | verification runs on the **12 h sweep sample** instead of the disjoint 4 h sample, and the paper states that verification is no longer out-of-sample |
| **M5 soak** cannot get a clear window | soak reduced from 72 h to **48 h**, reported as 48 h |
| **M1+ not finished** when results are written | every in-situ rate stays labelled **PRELIMINARY** with its hours; no rate is quoted as final |

---

## B9. Machine-hour estimate, from the measured rate

Measured on the M1+ pass now running, not taken from the plan:
**aggregate `realtime_factor` = 0.6448** (3 segments, 3137.7 s video / 4866.1 s
wall). Wall time ≈ video seconds ÷ 0.6448.

| Phase | Work | Video hours | **Machine hours** |
|---|---|---:|---:|
| **A (running)** | M1+, 120 segments remaining | 58.13 | **90.1** |
| **C** | in-situ sweep, 24 segments × 7 checkers × 5 θ | 12 × 35 = 420 | **651** ⚠️ |
| **C′** | *record-then-rescore*: 1 recording pass + rescoring | 12 | **18.6** |
| **D** | verification, 3 pts × 7 checkers on 8 segments | 4 × 21 = 84 | **130** ⚠️ |
| **D′** | verification, 3 pts × 7 checkers, **one segment each** | 3.5 | **5.4** |
| **E** | ex-situ sweep, GMDCSA24 + FURG × 5 θ | ~2.5 | **~4** |

**⚠ The naive Phase C is 651 machine-hours and is not affordable.** This is
exactly what record-then-rescore exists for: one recording pass at the loosest θ
(18.6 h) locates the curve, and only the reported operating points are re-run for
real. Phase D likewise must not run every verification point over the whole 8-
segment sample; it runs each point on a segment drawn from that sample.

**Registered consequence:** the sweep design is **record-then-rescore first,
real runs only at reported points** — not a preference but the only design that
fits the machine budget. Total realistic C+D+E ≈ **28 machine-hours**, against
90 h for Phase A already committed.

*These numbers assume the current throughput holds and the GPU stays exclusive to
this project. If M1+ slows, B9 is recomputed before Phase C launches.*

---

## What the author is being asked to approve

1. **B1** — the seven parameters and their grids. Is `fall_angle_threshold` the
   right primary knob for Fall, or should it be `velocity_threshold`?
2. **B2** — 24 segments for sweep, 8 **disjoint** for verification. And: are
   there other occupancy windows beyond 2026-08-28 08:00–10:30?
3. **B6** — the ≥10-positive rule, and accepting that ≥3 checkers are FAR-only.
4. **B9** — that Phase C is record-then-rescore, because the direct sweep is
   651 h.

Once approved: this file is hashed, the SHA256 is recorded in `GT_PROTOCOL.md`,
and no grid or sample changes afterwards without a new version and a stated
reason.

---

# ⛔ DRAFT 2 — **NOT LOCKED. TWO BLOCKERS.**

**Updated 2026-09-02 22:10 +07.** The instruction was to apply A1–A4 and lock.
**Locking is refused**, for two reasons that are registered stop conditions.

---

## ⛔ BLOCKER 1 — Q1: FallChecker's firing rule is **not an AND**

The instruction anticipated this and said: *"Không phải AND → dừng, hỏi."*

Verbatim, `fall_check.py` (end of `_score_fall`):

```python
confidence  = float(np.mean(scores))
high_scores = sum(1 for s in scores if s > 0.55)
is_falling  = confidence > 0.45 or high_scores >= 2
```

Four features each *append a weighted score to a list*, and each threshold acts
as a **gate on whether that feature contributes at all**:

| Feature | Gate | Weight |
|---|---|---|
| bbox aspect ratio | `ratio < fall_ratio_threshold` (0.75) | ×1.0 |
| spine angle | `angle > fall_angle_threshold` (60°) | ×0.8 |
| centre-Y velocity | `vy > velocity_threshold` (0.04) | ×0.6 |
| hip≈knee proximity | `abs(hp_y-kn_y) < bh*0.22` | ×0.5 |

**Why this makes `fall_angle_threshold` unusable as a sweep parameter.** The
aggregate is `np.mean(scores)` over *the features that fired*. Raising the angle
threshold can **remove a low angle score from the list**, and removing a low
value from a mean **raises the mean**.

Concretely: scores `[0.9, 0.2, 0.5]` → mean 0.533 → fires. Raise
`fall_angle_threshold` so the 0.2 angle term no longer appends: `[0.9, 0.5]` →
mean 0.70 → fires *more confidently*. **Tightening the threshold made the
detector more likely to fire.**

So the FAR/recall response to `fall_angle_threshold` is **non-monotonic**, and a
non-monotonic knob cannot produce a Pareto front. Propositions 1 and 2 assume a
monotone trade-off curve per checker; sweeping this parameter would hand the
allocator a curve that violates its own premise. **This is not a tuning
inconvenience, it invalidates the sweep for this checker.**

### Options for the author — a decision is needed

| Option | What it sweeps | Monotone? | Cost |
|---|---|---|---|
| **(a) the decision threshold `0.45`** ⭐ | `confidence > 0.45` | **Yes, strictly** | It is a **hardcoded literal**, not a config key. Sweeping it means exposing it as a parameter in the measurement harness. At 0.45 behaviour is bit-identical to deployed, so the frozen point is preserved. |
| (b) `pose_conf` (0.4) | upstream pose confidence | Yes | Changes detections, so it moves tracker association too — same coupling as Intrusion's `--conf` |
| (c) `confirm_frames` (4) | temporal confirmation | Yes, but integer | Only ~4 usable points, coarse grid |
| (d) drop Fall from the sweep | — | — | Fall keeps a single operating point; loses the checker with the best ex-situ evidence (78 events) |

**Recommendation: (a).** It is the module's actual operating point, it is
strictly monotone, and the frozen configuration stays on the curve.

**And it is itself a finding worth a sentence in the paper:** the only monotone
operating point of this checker is a bare literal in the source, while the four
values that *are* exposed as configuration are non-monotone gates. A practitioner
tuning this module through its configuration surface cannot move it along its own
trade-off curve.

---

## ⛔ BLOCKER 2 — the manifest's durations are wrong for eleven segments

Found while answering I6. Not anticipated by the instruction, and it invalidates
corpus-wide numbers until fixed.

Eleven segments recorded **2026-08-31 08:00–13:00** carry container metadata the
muxer was handed rather than measured (KNOWN_ISSUES HARNESS-5), and the manifest
took `format=duration` at face value:

| file | manifest | file size | true ≈ |
|---|---:|---:|---:|
| `HOM_20260831_0800` | **19,614 s (5.45 h)** | 98.3 MB | ~1,800 s |
| `HOM_20260831_0830` … `1230` (9 files) | **1 s each** | 74–100 MB each | ~1,800 s each |
| `HOM_20260831_1300` | 169 s | 75.4 MB | ~1,800 s |

**The total nearly cancels** — one 5-hour overstatement against nine
half-hour understatements — so the corpus headline (83.9775 h) looked plausible
while eleven segments were individually wrong by hours. That is the dangerous
shape: a correct-looking total over corrupt parts.

**What it does and does not affect:**

- ✅ **The reported FAR figures are safe.** All 52 measured segments are from
  27–29/08; **none of the eleven is among them.** Fall 0.4804/h and Helmet
  8.0468/h over 24.9789 h stand.
- ❌ **Every corpus-wide in-situ number is affected**: the 83.9775 h denominator,
  Tier 0's per-hour and per-day tables, the temporal split, and the block
  bootstrap — which resamples *segments carrying their durations*, so a segment
  claiming 5.45 h with half an hour of alerts distorts the rate badly.
- ❌ M1+ is currently measuring toward these segments; their observation time
  must be right before any corpus-wide rate is computed.

**Correction in progress**, by decoding rather than by trusting the container:
`duration = nb_read_frames / fps_ref`, with `fps_ref` = **14.883069**, the median
`avg_frame_rate` of the **164 healthy segments** (range 11.15–15.01). Frame count
is what the pipeline actually consumes; the container's timing is the thing that
is broken, so it is not used. The original manifest is kept; nothing is deleted
and no footage is added.

**Registered rule, new:** a manifest duration is admissible only if it is
consistent with the file's decoded frame count. `validate_manifest.py` gains this
check so a corrupt duration cannot re-enter silently.

---

## ✅ I6 — answered (was required before locking)

`record_watcher.sh` lines 174–175, verbatim:

```
ffmpeg ... -rtsp_transport tcp -stimeout 10000000 -i "$U" \
       -c:v copy -an \
       -f segment -segment_time 1800 -segment_atclocktime 1 ...
```

**`-c:v copy` — stream copy, no re-encode.** `ffprobe` on a real segment:
h264 High, 1280×720, yuv420p, ~350 kbps.

**One line for §8.5:** *the in-situ corpus is the camera's own H.264 bitstream,
stored without transcoding; unlike the ex-situ branch it carries no re-encode
stage, so the 34.4% re-encode sensitivity measured in §8.8 does not apply to any
in-situ number.*

This also explains the corrupt timestamps: stream copy preserves whatever the
RTSP source sent, including the non-monotonic DTS that produced Blocker 2.
**The same decision that keeps the in-situ corpus pristine is what let the
timing metadata rot** — worth one sentence, because it is a genuine trade-off
rather than a mistake.

---

## ✅ §3 — VIRAT decided, with one correction to the plan

VIRAT Ground is **open, scriptable, no form** (Kitware API), and it ships
**named activity annotations** — the thing Avenue lacked. All **329**
`*.viratdata.events.txt` files were fetched and histogrammed:

| type | activity | events | clips |
|---:|---|---:|---:|
| 9 | carrying object | 822 | 194 |
| **10** | **person running** | **22** | **15** |
| **11** | **person entering a facility** | **156** | **70** |
| 12 | person exiting facility | 133 | 65 |
| 5 | getting into vehicle | 111 | 69 |

### RunningChecker → ✅ admissible

Type 10 maps cleanly onto §4.5's definition (a run judged from gait). **22 events
in 15 clips**, which clears the ≥10 rule of B6 — but only just, so the Wilson
interval will be wide and the paper says so.

### IntrusionChecker → ⚠️ type 11 is the **wrong construct**, do not use it

Our deployed intrusion configuration is `monitor_full_frame=true` with no
polygon, so under §4.2 the event is **"a person is present in the frame"**.
VIRAT type 11 is the much narrower activity **"person walks into a building"**.

Scoring our checker against type 11 would count every person who appears and
does *not* enter a facility as a false positive — inflating FP by roughly the
ratio of persons to facility-entries, which in VIRAT is large. Recall would be
meaningless and FAR absurd.

The correct GT for our definition is VIRAT's **object tracks**
(`*.viratdata.objects.txt`, person class), not its event annotations. That is a
different construction and must be registered before use, not improvised.

**Registered for now:** Intrusion ex-situ is **not yet admissible**; it awaits a
registered GT construction from the object files. It does not enter the
allocation on the strength of type 11.

---

## §3 continued — IntrusionChecker: **ex-situ recall is degenerate, and the reason is the checker, not the data**

Registered 2026-09-02 23:05 +07, after building the GT construction and testing
it — before any recall number was computed.

The earlier note said type 11 ("person entering a facility") is the wrong
construct and that the right GT is VIRAT's **object tracks**. That was correct,
and building it settles the question in the opposite direction from what was
expected.

### The construction

VIRAT `*.viratdata.objects.txt` carries per-frame boxes with a track id and an
object type; **type 1 = person**. Under §4.2 the deployed intrusion event is
*"a person is present in the monitored region"*, and the region is
`monitor_full_frame=true` with no polygon — the whole frame. Two candidate
mappings, both merged with IntrusionChecker's 30 s gap (P8):

- **presence** — maximal intervals during which at least one person is visible;
- **per-track** — the first appearance of each person track.

### The measurement, on five sample clips

| clip | person rows | person tracks | presence events | per-track events |
|---|---:|---:|---:|---:|
| VIRAT_S_010004_07_000729_000809 | 12,858 | 27 | **1** | **1** |
| VIRAT_S_010005_02_000177_000203 | 3,502 | 10 | **1** | **1** |
| VIRAT_S_010114_01_000235_000311 | 1,921 | 5 | **1** | **1** |
| VIRAT_S_010205_02_000301_000345 | 8,287 | 19 | **1** | **1** |
| VIRAT_S_010208_00_000000_000049 | 6,337 | 11 | **1** | **1** |

**Every clip collapses to exactly one event, under both mappings.** People are
present essentially continuously in VIRAT's parking-lot scenes, so after a 30 s
merge the entire clip is one interval. Twenty-seven person tracks become one
event.

### What that means, and why it is a result rather than a failure

An event count of one per clip makes recall degenerate. Any detector that fires
once anywhere in a continuously-occupied scene scores 100%; one that never fires
scores 0. There is no curve, because the quantity has no resolution: sweeping θ
moves the *person detector*, and the module has no threshold of its own (B1).

So **IntrusionChecker cannot be given an informative ex-situ recall — and the
obstacle is its own event definition, not the availability of data.** With
`monitor_full_frame=true` and `target_classes=["person"]`, its event is "a person
is visible", so its recall *is* the person detector's recall, which is already
measured at Layer-1 on COCO and does not need a video corpus to establish.

This is worth a paragraph in the paper, because it is the sharpest form of an
argument the paper is already making:

> A checker whose event definition is coextensive with its detector's output has
> no coverage curve of its own to trade against its cost. It consumed 91.8% of
> the offline alert budget and 95.2% of the production budget, and there is no
> principled recall against which to weigh that spend — not because we could not
> obtain the data, but because the question "how often does it catch an
> intrusion" reduces, under this configuration, to "how often does the detector
> see a person".

### Registered decision

**IntrusionChecker does not enter the allocation.** It is reported with:

- an **in-situ alert rate** on the corpus (it is not covered by the negative
  declaration — intrusion events did occur);
- an **in-situ FP-fraction** from the 100-image label pack (§2), giving a
  false-alarm rate for the production column under the declared transfer
  assumption;
- **no ex-situ recall**, with this subsection as the stated reason.

VIRAT remains admissible and is still used for **RunningChecker** (type 10,
22 events, 15 clips), where the event definition is a genuine sub-class of what
the detector sees and the count is not degenerate.

### Updated allocation roster

| Checker | ex-situ positives | in-situ | Verdict |
|---|---|---|---|
| **FallChecker** | 78 (GMDCSA24) | FAR 0.4804/h | ✅ enters |
| **SmokeFireChecker** | 17 (FURG, fire only) | 0 obs, UL 0.1477/h | ✅ enters, wide interval |
| **RunningChecker** | 22 (VIRAT type 10) | 0 obs, UL 0.1477/h | ✅ enters, wide interval |
| **IntrusionChecker** | **degenerate — 1 event/clip** | alert rate + FP-fraction | ❌ **excluded, by its own definition** |
| HelmetChecker A0 | 0 — images only | FAR 8.0468/h | ❌ FAR-only |
| EnhancedHelmetChecker | 0 — images only | 0 obs | ❌ FAR-only |
| ForkliftSpeedChecker | 0 — no open source | 0 obs | ❌ FAR-only |

**Three of seven enter the allocation. Four are excluded, for four different
reasons** — no open video source (Forklift), image-only corpora (Helmet ×2), and
a degenerate event definition (Intrusion). That the four exclusions have four
distinct causes is the finding; a single cause would have looked like bad luck.

### Correction to the Running count, after applying the protocol's own merge rule

The raw histogram reported **22** type-10 events in 15 clips. That is the count
*before* P8's merge gap. RunningChecker's gap is
`max(operational 10 s, production cooldown 20 s) = 20 s`, and applying it merges
adjacent running events into single occurrences:

| | |
|---|---|
| raw type-10 events | 22 |
| **after the 20 s merge gap (P8)** | **17** |
| clips | 15 |
| total annotated running time | **108.9 s** |
| GT file | `exsitu/virat/GT_running_virat.csv` |

**17, not 22.** It still clears the ≥10 rule of B6, but by less than first
reported, and the Wilson interval will be correspondingly wide. Recorded here
rather than quietly carried, because the difference between a raw annotation
count and the count after our own merge rule is exactly the sort of slippage
that makes a denominator wrong.

Note the coincidence worth not over-reading: **SmokeFire also has 17 events**
(FURG, fire sub-class). Two of the three checkers entering the allocation rest
on 17 positive events each. The allocation will therefore be dominated by Fall's
78, and the sensitivity analysis of B7 has to show what happens when the two
17-event curves move within their intervals.

### And one more, applying §4.5's minimum duration

§4.5 sets RunningChecker's **minimum event duration at 1.0 s**. One merged event
in the VIRAT set lasts **0.033 s** — a single annotated frame — and is therefore
excluded by the protocol's own rule, not by judgement:

| stage | events |
|---|---:|
| raw type-10 annotations | 22 |
| after the 20 s merge gap (P8) | 17 |
| **after the 1.0 s minimum duration (§4.5)** | **16** |

Exclusion recorded in `GT_running_virat_excluded.csv` with its reason, in the
same form §2.2's exclusion file uses, so the drop is visible rather than
implicit.

**Final VIRAT running GT: 16 events across 15 clips, 108.9 s of annotated
running**, min 1.8 s / median 5.6 s / max 21.4 s.
`GT_running_virat.csv`, SHA256 `d1cb596f6c67e6102ed3fc370c19ca9e7ab8fc2c68dd5e337ef06f4ee5d1f260`,
fixed before any clip is scored (§8.2).

Running still clears B6's ≥10 rule, at 16. Together with SmokeFire's 17, **two of
the three checkers entering the allocation rest on fewer than 20 positive events
each**, and the paper must not present their curves with the same visual weight
as Fall's 78.

---

# ✅ DRAFT 3 → **LOCKED**

**Written 2026-09-03, 09:40 +07:00**, before the campaign queue was launched and
before any sweep, verification or ex-situ threshold number existed. Draft 2's two
blockers are both resolved below; the resolutions are recorded with their
reasons rather than applied silently.

Applies: Checkpoint 2a **A1–A4**, Checkpoint 2b-pre **K2–K5**. Where a decision
here reverses one in Draft 2, the reversal is stated as a reversal.

---

## A1 → replaces B4 and the D' line of B9: the verification design

Draft 1's B9 line *"one segment per verification point"* is withdrawn. With a
false-alarm rate of 0.5–8 per hour, one 30-minute segment yields 0–4 alerts per
point: no usable interval, and no way to measure replay-to-real fidelity at all.
That line was the one place in this file where the machine budget had quietly
been taken out of the statistics.

Two principles replace it.

**(i) Only checkers that enter the allocation are verified.** A FAR-only checker
(Helmet A0/A1, Forklift) needs no θ curve — the paper uses its false-alarm rate
at its frozen θ, already measured in M1. Verification therefore covers the
allocation roster, not all seven modules.

**(ii) Independent downstream knobs are verified jointly.**
`FallChecker`'s decision threshold and `SmokeFireChecker.confidence_threshold`
live in different modules, both downstream of the tracker, and the offline
runner drives every cooldown from a virtual clock — so there is no load-induced
frame drop by which one could affect the other. They are therefore swept in
**three joint runs** — (loose, loose), (middle, middle), (tight, tight) — over
the **whole 8-segment verification sample**, not one segment.

**The independence is declared as an assumption and is not proven.** The paper
says so in those words.

**IntrusionChecker's `--conf` is upstream**, not downstream: it changes which
detections ByteTrack associates, for every module at once. It is therefore swept
**separately**, two points either side of the frozen value, each a full 8-segment
run; and inside the three joint runs `--conf` is held at the deployed **0.25**.

| runs | video h | machine h at rtf 0.6448 |
|---|---:|---:|
| 3 joint (Fall × SmokeFire) × 8 segments | 12 | **18.6** |
| 2 Intrusion `--conf` × 8 segments | 8 | **12.4** |
| **verification total** | 20 | **≤ 31** |

The 8-segment sample is kept at full size. Nothing is bought back from rigour.

---

## A2 → replaces the occupancy stratum of B2

The occupancy stratum is **`ai_frames == 0`** (the motion gate never opened in
that segment) against `ai_frames > 0`, read from the M1 run metadata.

It replaces an occupancy diary reconstructed from the author's memory. The
reason is not convenience: a stratification variable has to divide the corpus
reproducibly, and it does **not** have to mean what its name suggests. "The
motion gate never opened" is measured, objective, already recorded for every
segment, and re-derivable by anyone with the metadata. A remembered list of
hours when the house was empty is none of those things.

This is **not** ground truth about occupancy and is never reported as such. The
one declared empty window (2026-08-28 08:00–10:30) is carried in `notes`, and
changes no stratum.

**Consequence for timing, registered:** `ai_frames` exists only for segments M1
has measured. The draw therefore executes **after M1+ reaches 175/175**, as job
`S1` of the campaign queue, from `scripts/draw_sweep_samples.py` with the seeds
below. Drawing earlier would put every unmeasured segment into the "motion"
stratum by default, which is not a stratification but a coin flip wearing a
label. The script refuses to draw until it has 175 rows.

Seeds unchanged: **20260902** for the 24-segment sweep sample, **20260903** for
the 8-segment verification sample, drawn from the segments the first draw did
not take, so disjointness holds by construction rather than by a later check.

---

## A3 → B7, what ρ is and is not

ρ = 0.494 is the median staged→wild sensitivity ratio of a **fall classifier**
(I3D / VideoMAE, OmniFall Table 2). It is not a property of a posture rule and
certainly not of fire.

- **Fall** — ρ is applied as a sourced approximation.
- **SmokeFire** — no published degradation factor for fire detection is in hand,
  and none is going looking for: the "use what is downloadable" rule applies to
  citations as well as to corpora. The same ρ is used as a **declared
  assumption**, labelled as such wherever it appears.
- **Both** — the sensitivity analysis sweeps the **entire range ρ ∈ [0.080,
  0.568]**, so no conclusion about allocation *order* rests on a single ρ.

---

## A4 → new section D5, and B9's real total

**D5 — verification of the allocated θ.**

| | design | video h | machine h |
|---|---|---:|---:|
| **target** | whole corpus, 175 segments | 84 | **130** |
| **registered fallback** | 24 + 8 = **32 segments**, of which 8 are out-of-sample | 16 | **25** |

At the measured rtf, 84 video-hours is 130 machine-hours, not the 76 the plan
assumed. The fallback is the campaign's **default**; the full corpus is added
only if the queue's §4 upgrade rule fires on measured throughput. Neither
version may restate a number reported for the other: an upgrade adds a labelled
row, it never edits one.

**B9, corrected total:** A 90 + C' 18.6 + verification ≤ 31 + ex-situ ~12 +
D5 25–130 + M4 28–56 + M5 48–72 ≈ **255–400 machine-hours**. M5 is the first
thing that shortens, and it shortens to 48 h, which is already the registered
figure rather than a concession.

---

## K3 → B6 reversed for Intrusion: it **enters** the allocation

**This reverses Draft 2's registered decision of 2026-09-02 23:05.** Draft 2
concluded that IntrusionChecker cannot be given an informative ex-situ recall,
because with `monitor_full_frame=true` and `target_classes=["person"]` its event
is coextensive with the detector's output, and every VIRAT clip collapses to one
event under P8's 30 s merge. **That observation stands and is still reported.**
What does not stand is the step from it to "therefore there is no principled
coverage curve".

Precisely *because* the event is coextensive with the detector's output, the
checker's coverage curve **is** the detector's person-recall curve — and that is
measurable at Layer-1, on COCO val 5000, which is already downloaded and already
in the plan. No video corpus is needed, and none would help.

Registered:

- **Coverage curve** = person-class recall of the detector, measured **per
  image** on **COCO val 5000**, over `conf ∈ {0.15, 0.20, 0.25, 0.35, 0.45}`
  (the B1 grid, containing the deployed 0.25). Ex-situ, labelled ex-situ.
- Declared as a **lower-bound proxy** for event-level recall: the tracker and
  `confirm_frames` can only raise event recall above frame recall, never lower
  it. The COCO → living-room domain gap goes through the same uncertainty-band
  rule as everything else (ρ, full range).
- **In-situ FAR by conf** = the sweep/verification alert rate at each `--conf`
  (the separate Intrusion runs of A1) **×** the FP-fraction from the 100-image
  label pack, with the transfer between operating points declared as an
  assumption. A second 50-image pack at the loosest conf — job V4 produces the
  alerts for it — gives that fraction a second point instead of one.
- **Mandatory sensitivity:** the allocation computed **with** Intrusion and
  **without** it (fixed spend), printed side by side. If the ordering does not
  change, the proxy decided nothing; if it does, the reader sees exactly what
  the proxy decided.

**Why this matters more than any other line in this file.** Intrusion consumes
**91.8 %** of the offline alert budget and **95.2 %** of production's. Outside
the allocation with a fixed spend, the whole optimisation divides the remaining
8 % between Fall, SmokeFire and Running, and the paper's central result becomes
a footnote. Inside it, the question worth asking can be asked: *is raising
Intrusion's confidence to free budget for Fall (weight 1.0) worth it, and how
far?*

The sentence for the paper keeps Draft 2's finding and states it exactly:
*a checker whose event definition coincides with its detector's output has no
coverage curve of its own — its curve is the detector's, measurable at image
level, and that is the whole of what can be said about its coverage.*

**Allocation roster, locked at 4 of 7:**

| Checker | coverage evidence | in-situ | verdict |
|---|---|---|---|
| **FallChecker** | 78 events, GMDCSA24 | FAR 0.4804/h | ✅ enters |
| **SmokeFireChecker** | 17 events, FURG (fire sub-class only) | 0 obs, UL 0.1477/h | ✅ enters, wide |
| **RunningChecker** | 16 events, VIRAT type 10 after P8 + §4.5 | 0 obs, UL 0.1477/h | ✅ enters, wide |
| **IntrusionChecker** | Layer-1 person recall by conf, COCO val 5000 | alert rate × FP-fraction | ✅ **enters (K3)** |
| HelmetChecker A0 | images only | FAR 8.0468/h | ❌ FAR-only |
| EnhancedHelmetChecker | images only | 0 obs | ❌ FAR-only |
| ForkliftSpeedChecker | no open source | 0 obs | ❌ FAR-only |

**Helmet does not get the Layer-1 proxy**, and the asymmetry is the point: its
event is "a person **without** a helmet inside the region", which is *not*
coextensive with a single-class detector's output. The proxy is admissible for
Intrusion for a specific structural reason, not because it is convenient.

---

## K4 → how the 16- and 17-event curves are read, registered before they exist

Fall's 78 positives will dominate any allocation. Registered now:

1. **Wilson intervals at every point of every curve**, printed, never
   summarised as "good agreement".
2. **Joint sensitivity:** both 16/17-event curves are moved to the edges of
   their intervals **simultaneously**, and the allocation ordering is reported
   at all four corners (both low, both high, and the two diagonals).
3. **No conclusion is rounded off on SmokeFire or Running alone.** A statement
   that depends on one 17-event curve is reported as depending on it.
4. The two curves are **not drawn with the same visual weight** as Fall's.

---

## Q1 → **RESOLVED**. FallChecker's operating point is the decision literal

Draft 2 refused to lock because `fall_angle_threshold` is non-monotone: the four
configurable thresholds are *gates on whether a feature appends a score to a list
that is then averaged*, so tightening one can remove a low score from the mean
and make the module **more** likely to fire. That analysis is confirmed and
stands.

Verbatim, `fall_check.py`, end of `_analyze`:

```python
confidence  = float(np.mean(scores))
high_scores = sum(1 for s in scores if s > 0.55)
is_falling  = confidence > 0.45 or high_scores >= 2
```

**Registered decision: the swept parameter is the literal `0.45`** — Draft 2's
option (a), the only strictly monotone operating point the checker has.

- It is exposed in the **measurement harness only**, as
  `--checker-params '{"FallDecision": x}'`, by wrapping `FallChecker._analyze`.
  The pinned image `sha256:2f41e503…` is **not modified**; that image is the
  basis of the whole in-situ branch and stays byte-identical.
- The wrapper is the **identity at 0.45** by construction (it reproduces both
  disjuncts separately: `confidence > x` for the first, and "the original fired
  while `confidence > 0.45` was false" for the second). So the deployed
  configuration remains a measured point on its own curve, not an extrapolation
  toward it.
- **Registered 5-point grid, containing the frozen value:**
  **0.30, 0.375, 0.45, 0.525, 0.60.**

**Knob-selection pilot (K2), job `X0`, registered as a pilot.** Because the
harness's existing Fall parameter is `pose_conf` (an upstream, also-monotone
knob), two ex-situ runs on GMDCSA24 decide which knob actually binds:

| arm | knob | value | frozen |
|---|---|---|---|
| X0-a | `FallDecision` | 0.30 | 0.45 |
| X0-b | `FallChecker` → `pose_conf` | 0.30 | 0.40 |

**Rule, fixed before the runs:** the knob producing the larger absolute shift in
recall over the 78 GMDCSA24 positives is the binding knob and is swept in X4.
Ties go to `FallDecision`, which is monotone by construction rather than by
observation. **Both grids are registered here, now**, so the pilot chooses the
knob and never the grid — choosing a knob by pilot is legitimate, choosing a
grid by pilot is not. `pose_conf` grid, if selected: **0.25, 0.325, 0.40, 0.50,
0.60.**

**And this is itself a result worth one sentence.** The only monotone operating
point of this module is a bare literal in its source, while all four values it
*exposes as configuration* are non-monotone gates. A practitioner tuning this
module through its documented configuration surface cannot move it along its own
trade-off curve.

---

## Blocker 2 → **RESOLVED**: manifest durations

The eleven segments of 2026-08-31 08:00–13:00 carried container timing the muxer
was handed rather than measured (KNOWN_ISSUES HARNESS-5). Corrected by decoding:
`duration = nb_read_frames / 14.883069`, the median `avg_frame_rate` of the 164
healthy segments. **Corpus 83.9775 h → 83.9442 h (−0.0333 h).**

The original manifest is kept (`manifest_rows_closed.csv.pre_duration_fix`);
the corrected file is `manifest_rows_closed.csv`; every changed row records its
old value and the method. The signed declaration is **not edited** — an appendix
carries both hashes with its own date and time.

**New admissibility rule, into GT_PROTOCOL:** a manifest duration is admissible
only if it is consistent with the file's decoded frame count (±10 %).
`validate_manifest.py` enforces it, so a corrupt duration cannot re-enter
quietly.

The shape of this bug is the thing to report: a 5.45-hour overstatement almost
exactly cancelled nine half-hour understatements, so the corpus headline looked
right while eleven segments were individually wrong by hours. **A correct total
over corrupt parts** is the failure mode a headline number cannot reveal.

---

## The campaign, registered as run

The remaining work is executed by `01_Measurement/ops/run_queue.py` from
`RUN_QUEUE.json`, unattended, GPU-exclusive and strictly sequential. Registered
properties, all of them consequences of rules already in this file:

- **A job is finished when its output files satisfy `done_check`**, never when
  its process exits. No `pgrep`.
- **No automatic retry.** A failure is notified and left; independent jobs go on.
- **A suspected misconfiguration halts everything** — output off-schema,
  `cooldown_mode` not `per_checker`, or an alert count more than 10× from the
  estimate registered here. This is "correct data over progress", executable.
- **15 GB free-space floor** measured as `statvfs.f_bavail` (the non-root
  figure), checked before every job. Below it the queue pauses; it never deletes.
- **Registered fallbacks are the defaults** (D5 on 32 segments, M4 on its 9
  essential cells, M5 at 48 h). The fuller versions are enabled only by the
  §4 upgrade rules in `RUN_QUEUE.json`, on **measured** throughput, and only
  ever as additional labelled rows.
- **Hard deadline 2026-09-20.** Any job projected past it is not started; it is
  recorded SKIPPED with its reason and the registered fallback stands.
- Every job writes `config_effective.json` and SHA256s of its outputs into its
  own output directory. A result without provenance is not a finished job.

**Production stack stopped 2026-09-03** (author's decision) so that the GPU and
CPU are exclusive to the campaign; instant and evidence in
`ops/PRODUCTION_STOPPED.json`, reproducibility snapshot taken first. Realtime
factors are reported **on their own side of that instant**: throughput changes,
results do not, because the offline runner drives every cooldown from a virtual
clock keyed to video time.

---

## LOCK

With Draft 2's two blockers resolved and A1–A4 / K2–K5 applied, this file is
**LOCKED**. Its SHA256 is recorded in `GT_PROTOCOL.md`. No grid, sample, seed or
admission rule changes after this point without a new version, a stated reason
and a new hash — and the superseded version is kept, not overwritten.
