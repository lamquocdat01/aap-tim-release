# GROUND-TRUTH PROTOCOL — AAP v3

**Version:** 1.3a · **Fixed on:** 2026-09-02 · **Status:** frozen before any measurement is taken. **No segment has been scored for any checker in any version up to and including v1.3a**, so nothing needs re-scoring. The annotation count is still zero; that is what keeps the window for registering rules legitimately open, and it closes the moment the first file is scored.

> **v1.3 adds the ex-situ half of the evidence.** Sections 1–7 govern *in-situ* measurement: false alarms on this deployment's own footage. **Section 8** governs *ex-situ* measurement: recall replayed from public video through the same frozen pipeline. **Section 9** pre-registers, with a timestamp and before any allocation has been computed, how a recall interval is derived. Sections 8 and 9 are numbered after the existing measurement sections rather than inserted as a new "section 6", because `scripts/aap_common.py` and §5.2 of this document both cite "section 6" as the file-format section; renumbering would silently invalidate those citations, which is the class of error this protocol exists to prevent.

**This document is written before the measurements and must not be changed after any measurement has been scored.** If a definition here turns out to be wrong, the fix is a new version number, a note saying what changed and why, and a re-score of *every* affected table — never a quiet edit. The previous version of this work defined its scoring after seeing the results, which is how it ended up reporting more true positives than there were events.

Applies to all seven checkers. Every table in the manuscript is produced by `scripts/score_events.py` reading this protocol's two CSV formats; no number is entered by hand.

---

## 1. Principles

| # | Rule | Why it exists |
|---|---|---|
| P1 | Ground truth is annotated by a person, from the video, **without running the system first**. | v2 generated ground truth by running its own detector at `conf=0.10`. That makes the ground truth a function of the system under test: the system is then compared against itself, and a systematic miss becomes invisible because it is missing from both sides. |
| P2 | **TP ≤ GT always.** The scorer asserts it and aborts if violated. | v2 reported `GT=0, TP=83` on `Production.mp4`. Those 83 alerts were false alarms on footage with no event, reported as a detection gain. |
| P3 | Precision is reported only when TP+FP > 0. Otherwise the cell reads *no positive predictions* and points to the false-alarm rate. | Precision is undefined at TP+FP=0. v2 printed 100% there, and in the same table printed "--" for an identical 0/0/0 row. |
| P4 | Footage with no annotated event yields **only** a false-alarm rate. No recall, no precision. | A negative segment carries no information about detection ability. |
| P5 | Observation time is counted **once per checker per file**. A file scored by four checkers contributes its duration to four separate denominators and is never summed into one corpus total. | v2's "10 minutes of footage" counted `Production.mp4` four times. |
| P6 | Every proportion carries a Wilson 95% interval; every rate carries a block-bootstrap 95% interval; zero observed events are reported with the two-sided 95% Poisson upper limit (3.689/T, not the one-sided rule-of-three 3/T) and never as "zero". | A recall of 100% from 3 events and one from 300 must not look alike on the page. |
| P7 | An annotation is never revised because a detector disagreed with it. | Revising ground truth to match output is the mechanism by which an evaluation stops measuring anything. |
| P8 | **The merge gap of every checker is `max(operational merge, production cooldown)`**, using the cooldown read from the deployed configuration, not from the manuscript. | If ground truth merges two occurrences that the system deliberately reports as one, the second becomes a false negative that measures the dedup policy rather than the detector. v1.0 applied this reasoning to IntrusionChecker alone and left the other six unchecked; the config dump then showed RunningChecker's cooldown is 20 s against a 10 s merge gap, which would have manufactured false negatives. |
| **P9** | **Every countable quantity in the paper is produced by a script that counts the files actually used**, written to a generated file and regenerated at build time. Clips, videos, events, hours, resolution and frame-rate distributions included. No countable number is typed by hand from an abstract, a README, a dataset card, or one of our own earlier summaries. | Added 2026-09-02 after three instances in one day, all the same shape — trusting a digest instead of counting. "GMDCSA24 is uniformly 1280×720" came from three rows of a probe (18 of 160 clips are 640×480). "FURG has 29 videos" came from a summary (the repository holds 23). And a probe file we generated ourselves was written with a header in a different order from the one `ffprobe` emits, transposing two columns. None of the three was carelessness; each was a reasonable-looking shortcut past counting. A wrong count in a published paper is an erratum, and prevention costs one script: `scripts/count_everything.py`, wired in as build step 0. |

---

## 1a. Deployed configuration this protocol is pinned to

Read from the running system on 2026-08-20, not from the manuscript. Full dump with the commands used: `production_config_dump_20260820.txt`.

- Image `ghcr.io/lamquocdat01/aap-ai-engine@sha256:2f41e5038c4377f7a5e340ff2161835e8a29935fd9291d38c3868f580d86c9c6`, built 2026-06-27, git `33ebefb`.
- Pipeline: `confirm_frames=3`, `skip_frame=2` (`AI_SKIP_FRAME`), `clahe_enabled=True`, `adaptive_gate_enabled=False`.

| Checker | Module cooldown | Module confirm | Source |
|---|---|---|---|
| FallChecker | **30.0 s** | 4 frames | `fall_check.py` `DEFAULT_CFG` |
| IntrusionChecker | **none in module** | — | `intrusion_check.py` has no cooldown key |
| SmokeFireChecker | **none** (`no_cooldown=True`) | 2 frames + window vote | `smoke_fire_check.py` `DEFAULT_CFG` |
| HelmetChecker (A0) | **none in module** | `temporal_n=5` | `helmet_check.py` |
| EnhancedHelmetChecker (A1) | **30.0 s** | `temporal_n=3` | `enhanced_helmet_check.py` |
| RunningChecker | **20.0 s** | 4 frames | `running_check.py` `DEFAULT_CFG` |
| ForkliftSpeedChecker | **15.0 s** | 3 frames | `forklift_speed_check.py` `DEFAULT_CFG` |

Three findings from the dump change what this protocol has to say.

**(i) Dedup in live operation is not a time cooldown at all.** `stream_manager.py` constructs the pipeline with `cooldown_enabled=False`, which selects the `alert_sent` path: **one alert per track per violation type per session**, with no time limit. A violation that persists for an hour on one track alerts once. Under that policy a second genuine event on the same track can never be detected, so event-level recall over long footage is not a well-defined quantity.

Measurement therefore runs the time-cooldown path (`cooldown_enabled=True`) with the per-checker cooldown in the table above, and the paper states that it does. The difference between the two policies is itself measured, as one row of the ablation, because "the deployed dedup policy costs *this much* recall" is a deployment result rather than an inconvenience.

**(ii) `ALERT_COOLDOWN=30` and `CONFIRM_FRAMES=3` in the production environment are dead.** No Python file reads either name; `grep -rn "ALERT_COOLDOWN\|CONFIRM_FRAMES" --include="*.py"` returns nothing. The values that take effect are hardcoded in `stream_manager.py`. The manuscript must not quote the environment file as if it configured anything.

**(iii) Two checkers are not in the live pipeline.** `stream_manager.py` instantiates intrusion, helmet, vehicle, fall and smoke_fire. `RunningChecker` and `ForkliftSpeedChecker` appear only in `video_test_worker.py`, the offline path. Any statement about seven modules running concurrently has to say which pipeline that refers to (see §4.7).

---

## 1b. Frozen deployment configuration during corpus collection

This clause is registered **before** the corpus is scored, so that it reads to a
reviewer as a constraint that was imposed rather than a habit claimed after the
fact.

**The rule.** For the whole time a corpus is being recorded from a live
deployment, no threshold, no ROI polygon, no module enablement, no model and no
camera-side detection setting is changed **after looking at what that deployment
produces**. If any such change is made, the segments recorded before it and the
segments recorded after it belong to two different systems, and the earlier
footage stops being independent of development: `independent_of_dev` must then
be set to `n` on one side of the split and the reason logged.

**Why no script can check it.** The manifest records what the configuration
*was*; it cannot record whether the author looked at an output before changing
it. No tool in this repository can verify this clause. It is a statement about
the author's conduct, written here in advance so that it is falsifiable against
the change log rather than against memory, and `sync_footage.py` restates it on
every run.

**What the clause covers and what it cannot.** It covers the *system*: detection
configuration, thresholds, model weights, module wiring, dedup policy. It does
not, and cannot, cover the *scene*: a household goes on living in the room, the
light changes, furniture moves, and a family member may reposition the camera.
Scene changes are not violations -- they are the phenomenon being measured -- but
a change large enough to alter the field of view **must be detected, dated and
disclosed**, because a false-alarm rate quoted over a corpus whose field of view
changed halfway through is two rates reported as one.

**Field-of-view segmentation.** Every corpus is checked for field-of-view change
before scoring, by estimating the horizontal image shift between consecutive
segments (`scripts/fov_check.py`). Where a step change is found, the corpus is
split into views, the view label is written into the manifest `notes` column as
`view=<letter>`, and the corpus table reports observation hours per view as well
as in total. A rate stratified by view is reported whenever a single view holds
less than 80% of the observation time.

**Recorded exceptions.**

| Date/time (site local) | What changed | Handling |
|---|---|---|
| 2026-08-27 19:40:20 -- 19:40:50 | Home camera panned right by at least 80 px at 1280x720 (about 7% of frame width), inside segment `HOM_20260827_1930.mp4`. A single step: no drift before or after, checked at 200 s intervals within three segments. Not a detection-configuration change -- `intrusion_config` in the database is identical before and after, and `monitor_full_frame=true` with no polygon means a pan cannot move an ROI boundary. | Corpus split into **view A** (start to 19:40:35) and **view B** (19:40:35 to end); `view=` written into `notes`; per-view hours reported. The segment spanning the change contributes its duration to both views. |


## 2. What an event is

An **event** is a maximal interval of wall-clock time during which the condition a checker is built to signal is true in the scene, judged by a person watching the video, independent of whether any detector fires.

Two occurrences of the same condition for the same subject separated by less than the checker's **merge gap** are one event. The merge gap is fixed per checker in Section 4 and is chosen from how an operator would experience the situation, not from what makes the numbers better.

An event has: a start time, an end time, a subject (which person or object), and a label.

### 2.1 Subject identity

Events are annotated per subject. Two workers without helmets in the same frame are two events, not one. If a subject leaves the frame and returns after longer than the merge gap, that is a new event.

### 2.2 What is *not* an event

- A condition visible for less than the checker's **minimum duration** (Section 4). Below that, no annotation and the interval is excluded from the negative denominator too, because it is neither clearly positive nor clearly negative. These intervals are listed in `gt_exclusions.csv` and their total is reported.
- A condition occurring on a subject that is unidentifiable to the annotator (too small, too occluded, too dark to judge). Also an exclusion, not a negative.

Exclusions are the honest handling of ambiguity. They are reported as a fraction of total footage in the corpus table; if that fraction is large for some checker, that fact is a result about deployment conditions and is discussed, not hidden.

---

## 3. Matching rule

**One rule for all seven checkers: hit-within-window.**

A detection with alert timestamp `t_alert` matches an annotated event `[t_start, t_end]` if

```
t_start - W  ≤  t_alert  ≤  t_end + W
```

where **W = 2.0 seconds** for every checker.

### 3.1 Why hit-within-window, and why W = 2 s

The alternative was temporal IoU between a detection interval and the event interval. It was rejected because the system does not emit intervals; it emits an alert at an instant, then suppresses repeats for a cooldown. Scoring an instant against an interval with IoU would make the score depend on the cooldown length rather than on whether the event was caught, which is exactly the confusion that made v2's intrusion recall uninterpretable.

W = 2.0 s is set from annotator timing precision, not from detector behaviour. In repeated-pass annotation, boundary times drift by roughly a second between passes; W must be larger than that drift so a match does not depend on which pass is used, and small enough that an alert cannot be credited to an event it has no plausible connection to. W is the same for every checker so that recalls are comparable across the table.

**W is fixed. It is not tuned per checker, and it is not adjusted after seeing results.**

### 3.2 Assignment

Matching is one-to-one and greedy in time:

1. Sort detections by `t_alert`.
2. For each detection, find the unmatched events whose window contains it. If several, take the one with the nearest `t_start`.
3. If one is found, mark the pair matched. This is a **true positive**.
4. If none is found, the detection is a **false positive**.
5. A detection falling inside the window of an event that is *already matched* is a **repeat alert**: it is neither TP nor FP, and it is counted separately in `repeat_alerts`.
6. Any event with no matched detection is a **false negative**.

Step 5 is what keeps the counts operator-meaningful. Repeated alerting on one ongoing event is a nuisance property, not a false alarm, and it is reported in its own column rather than being folded into FP where it would inflate the alarm rate, or ignored where it would hide a real annoyance.

Because every TP consumes exactly one event, `TP ≤ GT` holds by construction. The scorer asserts it anyway.

---

## 4. Per-checker definitions

All seven checkers. Values in this table are **frozen**; the "why" column is there so that a reviewer can see the choice was made on operational grounds before measurement.

### 4.1 FallChecker

| Field | Value |
|---|---|
| Event starts | The first frame in which the subject's posture has clearly departed from upright and the subject is descending involuntarily. |
| Event ends | The first frame in which the subject has either regained an upright posture or has been stationary on the ground for 3 s (whichever comes first). |
| Minimum duration | 1.0 s |
| Merge gap | **30 s** = max(operational 10 s, production cooldown 30.0 s) |
| Subject | One person. |
| Not an event | Sitting down, kneeling, lying down deliberately, crouching to pick something up, bending at the waist. These are the confusable negatives and **must** be present in the negative footage. |
| Why the merge gap | Operationally a person who falls, half-rises and falls again within 10 s is one incident. The module's own cooldown is 30 s (`fall_check.py`), so under P8 the gap is 30 s: a second fall 15 s after the first would be suppressed by the module, and annotating it separately would score a dedup decision as a miss. |

### 4.2 IntrusionChecker

| Field | Value |
|---|---|
| Event starts | The first frame in which any part of a person's ground-contact footprint is inside the configured zone polygon. |
| Event ends | The first frame in which the footprint has been fully outside the polygon continuously for the merge gap. |
| Minimum duration | 1.0 s |
| Merge gap | **30 s** = max(operational 30 s, measurement cooldown 30 s) |
| Subject | One person. Two people entering together are two events. |
| Not an event | A person passing outside the polygon; a person whose footprint touches the boundary line but does not cross it; a reflection or a shadow. |
| Why the merge gap | The merge gap **must equal the production cooldown** for this checker. If ground truth merged at 2 s while the system suppressed repeats for 30 s, the system would be scored as missing events it deliberately consolidated. That mismatch, not detector quality, produced v2's 25% intrusion recall, which v2 then explained away as an artifact rather than fixing. If the deployed cooldown changes, this merge gap changes with it and every intrusion table is re-scored. |

### 4.3 SmokeFireChecker

| Field | Value |
|---|---|
| Event starts | The first frame in which flame or smoke is visible to the annotator as a distinct region, not merely a brightness change. |
| Event ends | The first frame after which no flame or smoke is visible for the merge gap. |
| Minimum duration | 2.0 s |
| Merge gap | **60 s** = max(operational 60 s, production cooldown 0 s) |
| Subject | One fire or smoke source. Two separate sources are two events. |
| Label | `fire` or `smoke`, annotated separately; a source producing both is annotated as two overlapping events, one per label, and scored per label. |
| Not an event | Steam, dust, exhaust, fog, vehicle headlights, sunlight glare, a heater's heat shimmer. These are the confusable negatives and must be represented in the negative footage. |
| Why the merge gap | A fire that flares, subsides and flares again inside a minute is one incident. |

### 4.4 HelmetChecker (A0, standard) and EnhancedHelmetChecker (A1, advanced)

Both PPE modes use **identical** event definitions, so that A0 and A1 are compared on the same ground truth and the comparison means something. This is the direct replacement for v2's "+83×", which compared alert counts between the two modes on footage with no annotated events.

| Field | Value |
|---|---|
| Event starts | The first frame in which a person is inside the designated PPE-required area with no helmet on their head. |
| Event ends | The first frame in which that person either wears a helmet or leaves the area, sustained for the merge gap. |
| Minimum duration | 2.0 s |
| Merge gap | **30 s** = max(operational 15 s, A1 cooldown 30.0 s). A0 has no module cooldown, but both PPE modes are scored against the same ground truth so they must share one gap; the larger governs. |
| Subject | One person. Three bare-headed workers are three events. |
| Not an event | A person wearing a helmet incorrectly but wearing one (annotate as `helmet_worn_improperly` for information, scored as negative); a person carrying a helmet; a person outside the PPE area; a head too small or too occluded for the annotator to judge, which is an **exclusion**, not a negative. |
| Extra recorded field | Approximate head height in pixels at event start, banded as `<20`, `20--40`, `40--80`, `>80`. Recall is reported per band as well as overall, because head resolution is the stated limit on this checker and a single pooled recall would hide it. |

### 4.5 RunningChecker

v2 never evaluated this checker on a single positive event. The definition below exists so that it can be.

| Field | Value |
|---|---|
| Event starts | The first frame of a continuous run: a person moving at a clearly running gait, both feet leaving the ground in the stride, sustained for the minimum duration. |
| Event ends | The first frame after the subject has returned to a walking gait or stopped, sustained for 2 s. |
| Minimum duration | 1.5 s |
| Merge gap | **20 s** = max(operational 10 s, production cooldown 20.0 s). *This is the defect Checkpoint 1a caught in v1.0:* the gap was 10 s against a 20 s cooldown, so two runs 15 s apart would have been two ground-truth events with only one alert possible. |
| Subject | One person. |
| Not an event | Brisk walking; jogging in place; a person moving fast toward the camera with little image-plane displacement (**this is the hard negative for a velocity-proxy checker and must be represented**); a person on a bicycle or a vehicle. |
| Annotator note | Gait, not image speed, decides the label. The checker infers running from image-plane displacement, so a subject running along the optical axis is a genuine miss and must be annotated as an event, not excused. |

### 4.6 ForkliftSpeedChecker

Also never evaluated on a positive event in v2.

| Field | Value |
|---|---|
| Event starts | The first frame in which a powered industrial vehicle is moving faster than the site speed limit recorded in `footage_manifest.csv` for that location, sustained for the minimum duration. |
| Event ends | The first frame after the vehicle is at or below the limit, sustained for 2 s. |
| Minimum duration | 2.0 s |
| Merge gap | **20 s** = max(operational 20 s, production cooldown 15.0 s) |
| Subject | One vehicle. |
| Ground-truth speed | Established by a physical reference in the scene: two markers a measured distance apart, and the frame count between the vehicle's front axle passing each. The distance and the marker positions are recorded per location in `gt_speed_references.csv`. **Without a measured reference, no speed event may be annotated for that footage** — it becomes an exclusion. |
| Not an event | A vehicle moving fast in the image because it is close to the camera; a vehicle at legal speed on a downward slope; a pedestrian-operated pallet truck. |
| Honesty note | v2 stated that real speed in km/h requires homography calibration and that this was pending. It is still pending. Until it is done this checker is evaluated against a **threshold-crossing** ground truth from the physical reference above, and the manuscript says exactly that rather than implying calibrated speed measurement. |

### 4.7 Which pipeline a measurement refers to

`stream_manager.py` (live RTSP) wires intrusion, helmet, vehicle, fall and smoke_fire. `video_test_worker.py` (offline) additionally wires running and forklift_speed. So "all modules concurrently" means different sets in the two paths, and a table that does not say which is being measured is ambiguous.

For this paper: every reported measurement runs the offline path with all seven checkers enabled, and the manuscript says so in those words. The claim being supported is that seven checkers share one detection pass on one device, which the offline path does. The claim NOT being made is that the currently deployed live service runs all seven; it does not, and Limitations says so.

---

## 5. Annotation procedure

### 5.1 Who and how

Single annotator (the author), stated plainly in the manuscript as a limitation. Tool: any frame-accurate player able to report time to 0.1 s. Annotations are typed into `gt_annotations.csv` (Section 6).

**The system's output is not visible during annotation.** Annotation of a file is completed and the file's rows committed before that file is scored.

### 5.2 Order of work

1. Annotate. Commit `gt_annotations.csv`.
2. Run the system (`scripts/run_batch.py`), producing `predictions.csv`.
3. Score (`scripts/score_events.py`).

If step 3 reveals an annotation that is simply wrong — a missed event visible on review, a typo in a timestamp — the correction is allowed, but it is logged in `gt_corrections.log` with the file, the row, what changed, and the reason, and the log is released with the data. Corrections that consist of deleting an event the system missed, or adding one the system found, are not permitted (P7).

### 5.3 Repeatability check

At least **20% of files per domain**, chosen by a fixed rule (every fifth file in manifest order), are annotated a second time at least seven days after the first pass, without consulting the first pass. Agreement is reported as:

- **Event-count agreement:** the number of events matched between passes under the same window rule of Section 3, over the mean event count of the two passes.
- **Boundary agreement:** the median absolute difference in `t_start` between matched pairs.

Both are reported in the corpus table. The second-pass file is kept as `gt_annotations_pass2.csv`; the first pass is the one used for scoring, decided in advance so the choice cannot follow the result.

### 5.4 Pre-registered sampling for IntrusionChecker on continuous deployment footage

**The problem this solves.** The deployed intrusion configuration is
`monitor_full_frame=true` with no polygon (Section 1a). Under the event
definition of Section 4.2 the region is therefore the entire frame, so *every*
entry of a person into the room is an intrusion event that would have to be
annotated per subject. On the home corpus the deployment raises thousands of
such events in twenty-four hours. Annotating all of them is not possible, and
the failure mode of trying is worse than not trying: annotation quality
collapses, and it collapses on whichever segments were annotated last, which
correlates with time of day.

**The rule, registered before any segment's content was examined for
intrusion.**

- **Sample.** In `footage_manifest.csv` order, within one domain, **every sixth
  row** -- 1-based positions 6, 12, 18, ... -- is an *intrusion sample* segment.
  The offset is fixed at 6 and is not chosen per corpus.
- **Inside the sample.** Full event-level, per-subject annotation for
  IntrusionChecker, exactly as Sections 2 to 4.2 require.
- **Outside the sample.** Segments not in the sample are **out of scope for
  IntrusionChecker**: not positive, not negative, not counted in any intrusion
  denominator. This is recorded mechanically -- `IntrusionChecker` is removed
  from the `checkers` column of those rows, so P5 cannot silently count them.
- **The other five checkers are unaffected.** The whole corpus remains negative
  observation time for FallChecker, SmokeFireChecker, HelmetChecker,
  EnhancedHelmetChecker and RunningChecker, counted once per checker per file
  (P5).
- **Applied by script, not by hand.** `scripts/intrusion_sample.py` rewrites the
  `checkers` column from manifest order and writes the sample list. Running it
  twice on the same manifest produces the same sample; it refuses to run if a
  segment it would drop already carries intrusion annotations or intrusion
  scores.

**Why every sixth and not a random draw.** A fixed positional rule is
reproducible from the manifest alone by anyone holding the released data, and it
cannot be re-drawn until it gives a convenient answer. Every sixth 30-minute
segment yields about 4 h of fully annotated intrusion footage per 24 h, spread
across day and night rather than concentrated in whichever hours were
convenient.

**What the sample can and cannot support.** It supports an intrusion event-level
recall and a per-event false-alarm accounting on about 4 h per 24 h, with
intervals computed on that smaller denominator and reported as such. It does
**not** support quoting an intrusion false-alarm rate over the full corpus
duration: the denominator for that checker is the sample, and the corpus table
prints the sample hours in the intrusion row.

### 5.5 Blanket negative declaration

**The problem this solves.** Six of the seven checkers look for events that did
not occur during corpus collection: nobody fell, nothing burned, nobody ran,
there is no forklift, and nobody wore or failed to wear a hard hat in a
residential living room. Annotating 83.98 h of footage frame by frame to record
seven kinds of nothing is both impossible and pointless. But a false-alarm rate
requires a denominator that is *known* to contain no events, and "the annotator
did not notice any" is not the same statement as "there were none".

**The rule.** For a stated checker and a stated contiguous span of the corpus,
the person who was present may sign a **blanket negative declaration**: an
assertion that no event of that checker's type occurred anywhere in that span.
The declaration is a first-person statement of fact about the world, not an
inference from any detector output.

Conditions, all required:

1. **Signed before any alert from that span is inspected.** The declarant must
   not have seen where the system fired. A declaration written after looking at
   the alert log is an annotation of the log, not of the world.
2. **Per checker, per span, in writing**, recorded in
   `blanket_negative_declaration.md` with the checker name, the exact segment
   range, the date signed, and the declarant.
3. **It creates negative observation time only.** Under P4 a declared span
   yields a false-alarm rate and nothing else: no recall, no precision.
4. **It is refusable per checker.** A declarant who is confident that nobody
   fell but unsure whether an unattended pan of rice smoked may sign for
   FallChecker and decline for SmokeFireChecker. A declined checker keeps that
   span out of its denominator entirely.
5. **It does not extend to IntrusionChecker.** Intrusion events did occur, in
   quantity, and are governed by the §5.4 sample instead.

**Why this is legitimate and where its limit is.** For the classes concerned the
declarant's knowledge is genuinely better than any annotator's: a person knows
whether they fell over in their own home. The limit is that it is a human
statement, subject to human error, and it cannot be audited from the released
data. It is therefore recorded as an assumption in the manuscript's limitations,
named as such, with the alternative stated plainly — the alternative is to have
no false-alarm denominator for six of seven checkers, which is not an
improvement in rigour but the absence of a measurement.

**Status at v1.3b: RECORDED 2026-09-02, WITH A DISCLOSED P1 VIOLATION.**

| | |
|---|---|
| File | `blanket_negative_declaration.md` |
| SHA256 (signed text) | `1b2937c4d19a1816aca18f486e0c9bc75bfaf0331b20236660f574d1254cf31a` — hashed 2026-09-02T17:26, before any appendix |
| SHA256 (current file) | `a92de5951b02c33d9bd40a192dc5dec17c615a1c30a9ed14444ac93f6d6ecad4` — includes the post-signature correction appended 22:40, which records that the span is 83.9444 h rather than 83.9775 h (HARNESS-5). The signed text above the appendix is byte-unchanged; the same 175 segments are covered, so the assertion stands and only the derived rates were recomputed. |
| Recorded at | 2026-09-02T17:26:22+07:00 |
| Declarant | the author, resident of the site, present during the span |
| Transcribed by | Claude Code, on the author's explicit instruction. The assertion is the author's; the typing is not. Claude Code was not present and asserts nothing. |
| Classes declared event-free | FallChecker, SmokeFireChecker, RunningChecker, HelmetChecker (A0), EnhancedHelmetChecker (A1), ForkliftSpeedChecker — all six |
| Occupancy | 2026-08-28 08:00–10:30 confirmed empty |
| **Condition 1 (sign before seeing alert output)** | **VIOLATED — disclosed, not waived** |

**The P1 violation, stated here and not only in the declaration file.** Aggregate
alert output for this span had already been reported to the author before the
declaration was made: offline `runs/m1` totals (2,393 intrusion / 201 helmet /
12 fall = 2,606), live in-window totals (11,270, 134.2 alerts/h), and the full
per-hour rate breakdown. The violation was introduced by the measurement
assistant, not by the author.

What the author saw was **aggregate counts, never individual timestamps or
snapshots**, and four of the six classes are vacuous by setting (no helmets and
no forklifts exist in a living room). The classes where the disclosure carries
real weight are **FallChecker, RunningChecker and SmokeFireChecker**.

**Consequence, binding:** the spot-check of the Checkpoint-1i procedure §3 is
**mandatory rather than optional** for the three non-vacuous classes, and its
result (n reviewed / n discrepant) is reported in the paper next to every rate
derived from this declaration. A single genuine event voids its class. This
disclosure appears verbatim in the manuscript's limitations.

Until the spot-check is returned, rates for the three non-vacuous classes remain
labelled **PRELIMINARY**.

### 5.6 Stratified reporting rule (D8)

Registered before any FAR is scored, so that the choice between reporting strata
separately and pooling them cannot be made after seeing which presentation
flatters the result.

- A stratum (a camera view, a domain, a time band) with **≥ 8 h** of observation
  time for a given checker is **reported as its own row**, with its own interval.
- A stratum with **< 8 h** is **pooled**, and the pooled row carries a footnote
  naming every stratum inside it and its hours.
- The threshold is 8 h, chosen because below it a two-sided 95% Poisson upper
  limit on zero events (P6) exceeds 0.46 alerts/h, which is coarser than the
  differences the paper needs to discuss.
- Pooling across strata that individually clear 8 h is **not permitted**. If two
  views each have 10 h, they get two rows, even if pooling would look tidier.
- **A stratum that clears 8 h is still not reportable if it is confounded.**
  Hours are necessary, not sufficient. Where a stratum is perfectly or nearly
  perfectly aligned with another varying factor — as camera view currently is
  with time of day, view A being observed only in daylight hours and view B
  almost only at night — the comparison is reported as blocked, with the
  confound named, and no effect is attributed to the stratum. See
  `analysis/tier0/TIER0_RESULTS.md` Result 4.

### 5.7 Corpus M1 close

Recorded here because the closing date is part of the evidence and must not be
reconstructed later from file timestamps.

| | |
|---|---|
| Rule invoked | **E3**, registered 2026-08-30, *before any FAR had been seen*: "M1 closes on 2026-09-15 **or** on reaching 48 usable hours, whichever comes first." |
| Threshold crossed | 48 h raw passed during segment `HOM_20260831_1800.mp4` (cumulative 48.066 h) |
| Actual close | **2026-09-02T06:28:43+07:00** |
| Proximate cause of stop | the recorder's own free-space floor fired (KNOWN_ISSUES MEAS-5). The corpus had already passed the rule threshold, so the disk incident changed the closing *hour*, not the closing *decision*. |
| Final size | **175 segments, 83.9444 h raw** |
| Duration correction | 11 segments recorded 2026-08-31 08:00-13:00 carried corrupt container timing (HARNESS-5) and were logged with durations wrong by hours: one at 19,614 s (5.45 h) and nine at 1 s, all of them ~30 min files. Corrected 2026-09-02 by decoding: `nb_read_frames / 14.883069`, the median `avg_frame_rate` of the 164 healthy segments. Recovered values fall in 1,764.6-1,804.1 s, i.e. a 30-minute segment. Original manifest kept (SHA256 `2f779eb8…eba715`); corrected manifest SHA256 `b67ae5ba…ba3e7a6f`. **The total moved only 83.9775 -> 83.9444 h because the errors nearly cancelled — the per-segment values, which every stratified and bootstrap figure depends on, were wrong by hours.** No footage added, nothing deleted; the corpus remains closed under E3. |
| First / last segment | `HOM_20260827_0923.mp4` / `HOM_20260902_0600.mp4` |
| Excluded | `HOM_20260827_0931.mp4`, `HOM_20260827_0933.mp4` — both verified independently on 2026-09-02 to have no `moov` atom; `ffprobe` returns "Invalid data found when processing input" for each. They are unreadable, not merely short. |
| Last-segment rescue | `HOM_20260902_0600.mp4` (1686.776 s) was initially stranded outside the manifest by the "always skip the newest file" rule, which assumes a newer file is coming. `append_rows final` was added for the one case where that assumption is false. |
| Lock | the corpus directory carries a `CORPUS_CLOSED` marker recording the above; nothing may be appended to `manifest_rows.csv` after it. |

**No footage recorded after this instant may enter M1**, regardless of quality or
convenience. Choosing corpus size after seeing results is exactly what rule E3
was registered to prevent, and the temptation is strongest once the results are
in view.


---

## 6. File formats

Both files are UTF-8 CSV with a header row. `scripts/score_events.py` validates these schemas and refuses to run on a file that does not conform.

### 6.1 `gt_annotations.csv`

```csv
video_id,checker,subject_id,t_start,t_end,label,annotator,pass,notes
```

| Column | Type | Meaning |
|---|---|---|
| `video_id` | string | Must match a `file` in `footage_manifest.csv`. |
| `checker` | enum | One of: `FallChecker`, `IntrusionChecker`, `SmokeFireChecker`, `HelmetChecker`, `EnhancedHelmetChecker`, `RunningChecker`, `ForkliftSpeedChecker`. |
| `subject_id` | string | Stable within a file: `p1`, `p2`, `veh1`, `fire1`. |
| `t_start` | float | Seconds from the start of the file, one decimal. |
| `t_end` | float | Seconds, one decimal, `> t_start`. |
| `label` | string | `fall`, `intrusion`, `fire`, `smoke`, `no_helmet`, `running`, `overspeed`. |
| `annotator` | string | Initials. |
| `pass` | int | 1 or 2. |
| `notes` | string | Free text; for PPE events, the head-height band goes here as `head_px=20-40`. |

PPE rows additionally carry the head-height band; the scorer reads it for the per-band recall table and ignores the rest of `notes`.

### 6.2 `gt_exclusions.csv`

```csv
video_id,checker,t_start,t_end,reason
```

`reason` is one of `below_min_duration`, `subject_unidentifiable`, `no_speed_reference`, `occluded`, `other`. Excluded intervals are removed from the observation time for that checker on that file, so they inflate neither the numerator nor the denominator of a rate.

### 6.3 `predictions.csv`

Emitted by `scripts/run_batch.py`; this is the only output format the scorer accepts.

```csv
run_id,video_id,checker,t_alert,confidence,frame_idx,track_id,event_type
```

| Column | Meaning |
|---|---|
| `run_id` | Ties the row to a configuration header in `runs/<run_id>.json` (thresholds, resolution, fps, modules enabled, gate on/off, image digest). Ablation depends on this. |
| `t_alert` | Seconds from file start; the instant the alert would have been dispatched. |
| `confidence` | Detector confidence at the alert, for the threshold sweep. |
| `frame_idx` | For manual review of a disputed alarm. |
| `track_id` | Tracker identity, where the checker has one. |
| `event_type` | The normalized string the checker emits. |

### 6.4 `gt_speed_references.csv`

```csv
video_id,marker_a_desc,marker_b_desc,distance_m,speed_limit_kmh
```

Required for any file carrying `ForkliftSpeedChecker` annotations.

---

## 7. What the scorer outputs

`scripts/score_events.py` writes one row per (`run_id`, `video_id`, `checker`):

```csv
run_id,video_id,checker,gt_events,tp,fp,fn,repeat_alerts,observed_seconds,excluded_seconds
```

and asserts, per row:

- `tp + fn == gt_events`
- `tp <= gt_events`
- `observed_seconds > 0`
- every `video_id` appears in `footage_manifest.csv`
- `checker` is one of the seven

A violated assertion aborts the run. It does not warn and continue.

Aggregation into rates and intervals is `scripts/stats.py`, never the scorer, and never a spreadsheet.

---

## 8. Ex-situ recall protocol

Sections 1–7 govern measurement on this deployment's own footage. This section
governs the other half of the evidence: **recall measured on public video
recorded elsewhere**, replayed through the same frozen pipeline.

This is the part of the paper a reviewer will attack first, so it is held to a
stricter standard than the in-situ half, not a looser one.

### 8.1 Ground truth is not ours to write

**We do not annotate ex-situ video.** The source corpus's own published
annotation is the ground truth, used unmodified. We do not re-cut it, re-time
it, or re-label a clip because our pipeline disagreed with it — P7 applies with
particular force here, because the temptation is larger when the annotation was
written by someone else.

For every corpus used, `01_Measurement/exsitu/EXSITU_SOURCES.md` records: name,
version, licence, DOI or permanent URL, retrieval date, the file-level checksum
of what was downloaded, and **the exact clip list**. All of it goes into Data
Availability.

### 8.2 The clip list is fixed and hashed before anything is scored

The clip list is written, its SHA256 recorded, and only then is the pipeline
run. Selecting clips after seeing results — dropping the ones where the pipeline
did badly, keeping the ones where it shone — is the ex-situ equivalent of the
error that produced v2's `GT=0, TP=83`, and it is invisible in the output unless
the list is pinned in advance.

A clip may be removed after hashing for exactly one reason: it is technically
unreadable (no video stream, truncated container). Each removal is logged in
`EXSITU_SOURCES.md` with the decoder error, and the count of removals appears in
the results table. Any other removal invalidates the run.

### 8.3 Source admissibility: open access only, no negotiation

Registered as a rule, not applied case by case. A corpus is admissible only if it
can be obtained **without requesting permission**: an open licence and a direct
download. No request forms, no correspondence with dataset authors, no access
agreements.

This is deliberately restrictive and it costs real data. It is adopted because it
is the constraint the reader operates under: a practitioner allocating an alert
budget uses what they can download this afternoon, not what they could obtain
after a month of correspondence. A checker for which no admissible corpus exists
**falls back to false-alarm-only and is excluded from the allocation**, with the
reason recorded. The number of checkers that survive this rule is itself a
reported result.

### 8.4 The matching rule does not change

Everything in Section 3 applies unchanged: hit-within-window **W = 2.0 s**, merge
gap = `max(operational merge, production cooldown)` per checker (P8), the
`repeat_alerts` column, TP ≤ GT (P2), and the interval rules of P6. **The
matching rule is not relaxed because the video came from somewhere else.** If a
source's annotation granularity is incompatible with W = 2.0 s, that source is
declared inadmissible rather than accommodated.

### 8.5 Declared configuration deviations

Replaying foreign video through a pipeline tuned for one camera **forces**
deviations. They are enumerated here rather than discovered by a reviewer.

**The frozen-configuration guarantee is unchanged for in-situ work.** Every
in-situ false-alarm number is produced by the deployed configuration with not one
byte altered. The exceptions below apply **only** to the ex-situ branch, are
listed exhaustively, and there are no implicit ones. Any deviation not in this
table invalidates the run that used it.

| # | Parameter | Deployed value | Ex-situ value | Why it must change |
|---|---|---|---|---|
| E-1 | intrusion zone | `monitor_full_frame=true`, no polygon | **whole frame**, unless the source defines its own region | The deployed setting already is the whole frame, so this is a deviation in name only; it is listed so the absence of a zone is explicit rather than assumed. |
| E-2 | input frame rate | 15 fps (camera stream2) | source resampled to **15 fps** | `confirm_frames` and the tracker count *frames*, not seconds. Feeding 25 fps video makes every temporal threshold 0.6× as long in wall-clock terms, which silently changes the detector. |
| E-3 | input resolution | 1280×720 | source native, letterboxed to 1280×720 without cropping | Speed thresholds are in px/s and scale with apparent object size. Cropping would change which parts of the scene are visible; letterboxing preserves geometry at the cost of a border. |
| E-4 | `skip_frame` | 2 | 2 (unchanged) | — |
| E-5 | `clahe_enabled` | True | True (unchanged) | — |
| E-6 | per-module thresholds | as deployed | as deployed for the operating point under test; swept for the curve | Sweeping is the measurement, not a deviation. |
| **E-7** | **timestamp regularity** | camera stream, effectively constant rate | **VFR → CFR normalisation, applied to 160/160 clips including every clip in the §8.8 control cell** | GMDCSA24 is variable-frame-rate phone footage: **0 of 160 clips carry an identical `avg_frame_rate` before and after**, and none is exactly `15/1`. Re-encoding regularises container timestamps whether or not the frame rate is otherwise changed. This is listed as its own deviation because it applies to *every* clip and would otherwise be an implicit exception, which §8.5 forbids. |

#### How the pipeline reads time, and what E-7 therefore does and does not affect

`aap_offline_runner.py` line 647 computes `t_video = frame_idx / fps`. **The
runner never reads presentation timestamps.** `fps` is a single scalar taken from
`cv2.CAP_PROP_FPS`, guarded by a plausibility band of 5–60 fps that *refuses* the
file rather than substituting a guess (KNOWN_ISSUES HARNESS-5).

Three consequences, each measured rather than argued:

1. **The §8.8 control cell is clean on the time axis.** Time is a function of
   frame index, and the control clips have *identical decoded frame counts*, so
   the frame sequences are identical. The only residual is a clock **scale**
   factor — native ≈15.0014–15.0150 fps against an adapted exact 15.0 — worth at
   most ≈0.001 relative, i.e. **≈0.012 s** accumulated over a 12 s clip. Against
   W = 2.0 s that is a factor of about 170. E-7 does not compromise the control.
2. **But `frame_idx / fps` is not real presentation time for a VFR source**, and
   the ground truth is annotated in real seconds. The drift at clip end,
   `|duration − nb_read_frames / avg_fps|`, is measured over all 160 clips:

   | | median | p95 | max |
   |---|---:|---:|---:|
   | native (VFR) | 0.0065 s | 0.0384 s | **0.0662 s** |
   | adapted (CFR) | 0.0003 s | 0.0007 s | **0.0007 s** |

   The worst native case is **0.0662 s against W = 2.0 s, a factor of 30**, so no
   clip's clock drift can move an alert across a matching boundary. Adaptation
   incidentally removes this drift almost entirely, which is a point in favour of
   the adapted numbers rather than against them.
3. **No ground-truth event sits close enough to a clip end for the residual to
   matter.** Checked on all **78** fall-bearing clips: the distance from the last
   annotated fall to the end of the clip exceeds that clip's clock residual in
   **78 of 78** cases. **Zero violations**, so no event is excluded and none is
   scored against a truncated window.

Source for the three tables above: `exsitu/PAIR_PROBE_gmdcsa24.csv`, SHA256
`825428a68b954d059d38330ce8cd65f462e06c1bd1219dc7f28f569cf39c7fe8`, generated
2026-09-02T15:30 — **after** the column-transposition defect was found and the
probe rewritten to read every field by name. The superseded file is retained as
`SUPERSEDED_MISLABELLED_NATIVE_PROBE_gmdcsa24.csv` and no number here comes from
it.

### 8.6 Two recall numbers wherever the source allows

Where a source's native frame rate or resolution differs from the deployment's,
recall is reported **twice**: once at deployment fps/resolution (deviations E-2
and E-3 applied) and once at the source's native fps/resolution.

The difference between the two is not noise to be averaged away. It is a direct
measurement of **what the act of adaptation costs**, and no benchmark paper
reports it, because a benchmark runs one configuration. Both numbers appear in
the results table; neither is presented alone.

### 8.7 Labelling is mandatory and mechanical

Every table, figure and sentence carries the origin of its numbers: **in situ**
or **ex situ**. No table pools the two without an explicit column naming which
is which. `render_check.py` enforces the presence of the label on every results
table; a table without one fails the build rather than printing unlabelled.

### 8.8 The noise floor, measured before any adaptation effect is read

Added 2026-09-02 (CP1h H2). The §8.6 comparison asks what adapting a clip costs.
That question is unanswerable until we know what *nothing* costs.

**The trap this closes.** The 2×2 grid of deviations has a cell of clips whose
frame rate and resolution both come through the adaptation unchanged. It is
tempting to treat those as a determinism control — identical parameters, so
identical output expected. **They are not**, because the adapted files were
re-encoded and a lossy codec does not preserve pixel values. A disagreement there
has two possible causes, pipeline non-determinism and re-encode noise, and the
cell cannot separate them.

**Cell 0.** The same native file is therefore run through the same pipeline
**twice**. Nothing differs — same bytes, same command, same image — so any
disagreement is pipeline non-determinism alone. That rate is the **noise floor**.

**The comparison predicate is fixed before the runs.** Two runs agree on a clip
when their alert sets are identical as multisets of
`(checker, event_type, t_alert, frame_idx, track_id)`. `confidence` is excluded
and reported separately: an alert that appears or disappears is a different kind
of event from a float that moved in its seventh decimal.

**Reported as a rate, never as pass/fail:**

```
noise floor = alerts present in exactly one of the two runs
              / total alerts across both runs
```

**The reading rule, binding on §8.6:** no adapted-versus-native effect may be
claimed unless it exceeds the noise floor, and the floor is printed in the paper
beside the §8.5 deviation table. One divergent alert in five hundred and a
systematic drift must not be allowed to look alike on the page.

**Cell membership is decided by decoded frame counts, not by the container's fps
field.** A clip whose native rate is 14.985 or 15000/1001 against an adapted
15/1 has *changed* frame rate, slightly, and does not belong in the unchanged
cell. Membership is therefore assigned from `nb_read_frames` (which requires
decoding) and the nominal duration, and any clip that fails equality moves to the
changed cell. The count of clips genuinely remaining in the unchanged cell is
reported.

---

## 9. Pre-registered recall interval (Proposition 3)

**Registered 2026-09-02, 13:05 +07:00.** At the time of writing: zero ex-situ
clips have been scored, zero recall curves exist, and no allocation has been
computed under any weight vector. The rule below is therefore fixed before it
can be tuned to produce a preferred allocation, which is its entire purpose.

Proposition 3 treats `recall_i(θ)` not as a number but as an interval
`[recall⁻_i(θ), recall⁺_i(θ)]` and seeks the max-min allocation. The interval is
constructed as follows.

**Upper bound.** `recall⁺_i(θ)` = the recall measured on the admissible ex-situ
corpus at threshold θ, with its Wilson 95% upper limit where the count is small.
This is an *in-distribution* number relative to the corpus that produced it, and
it is the most optimistic defensible value.

**Lower bound.** `recall⁻_i(θ) = ρ · recall⁺_i(θ)`, where ρ is a staged-to-wild
degradation factor taken from **independently published measurements, never from
our own results**.

**The value of ρ, fixed now.** From OmniFall (arXiv:2505.19889v3) Table 2, which
trains one architecture on each of seven staged fall corpora and tests each both
in-domain and on genuine in-the-wild accident video. The ratio
`Se_in-the-wild / Se_in-domain` for class `Fall` is:

| source | CMDFall | UP-Fall | Le2i | GMDCSA24 | EDF | OCCU | CAUCAFall |
|---|---|---|---|---|---|---|---|
| ρ | 0.560 | 0.164 | 0.568 | 0.494 | 0.156 | 0.087 | 0.080 |

- **Primary: ρ = 0.494**, the median of those seven.
- **Reported range: ρ ∈ [0.080, 0.568]**, the full observed span, carried
  through the sensitivity analysis.
- Full extraction and provenance: `exsitu/OMNIFALL_TABLE2_DEGRADATION.md`.

**What is assumed, stated plainly.** OmniFall's ρ describes a fine-tuned
end-to-end video classifier. The checkers here are threshold rules over a frozen
detector and tracker. Nothing guarantees the two degrade alike, and we do not
claim they do. The claim is narrower and survivable: degradation of this
magnitude is *ordinary* rather than exceptional, so a point estimate of recall is
not defensible and a wide interval is. The load-bearing result is the sensitivity
analysis — *how wrong may the curves be before the allocation order changes* —
and it is reported across the whole range of ρ, not at the primary value alone.

**Anti-tuning clause.** ρ may not be widened, narrowed, or re-sourced after an
allocation has been computed. If a better published estimate is found later, the
change requires a new protocol version, a stated reason, and recomputation of
every affected table — never a quiet substitution. Both outcomes of the
sensitivity analysis are publishable: a stable ordering means a practitioner does
not need accurate recall curves to allocate well, and an unstable ordering means
every multi-function deployment is allocating blind. The rule is registered
before we know which one we have.

---

## 10. Change log

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-20 | First version. Frozen before any measurement. |
| 1.1 | 2026-08-20 | Checkpoint 1a condition. Added principle **P8** (merge gap = max(operational, production cooldown)) and applied it to all seven checkers against the config dump, not to IntrusionChecker alone. Changed: **RunningChecker 10 s → 20 s** (the defect Checkpoint 1a identified), **FallChecker 10 s → 30 s**, **PPE 15 s → 30 s**. Unchanged: Intrusion 30 s, SmokeFire 60 s, Forklift 20 s. Added §1a recording the deployed configuration this protocol is pinned to, including three findings from the dump: live dedup is `alert_sent` rather than a time cooldown, `ALERT_COOLDOWN`/`CONFIRM_FRAMES` are dead environment variables, and two checkers are absent from the live pipeline. Added §4.7 on which pipeline a measurement refers to. **No annotation existed at the time of this change, so nothing required re-scoring.** |
| 1.2 | 2026-08-28 | Checkpoint 1c decisions 2 and 3. Added **Section 1b, frozen deployment configuration during corpus collection**: the constraint stated in advance, what it covers, what it cannot cover, field-of-view segmentation, and the one recorded exception (the home camera was panned at least 80 px at 19:40 on 2026-08-27, so the corpus is split into view A and view B). Added **Section 5.4, pre-registered intrusion sampling**: every sixth manifest row is annotated in full for IntrusionChecker, every other row has IntrusionChecker removed from its `checkers` column and is out of scope for that checker, and the other five checkers keep the whole corpus as negative observation time. **No segment had been scored for any checker when this version was made, so nothing required re-scoring** -- which is what makes it legitimate to register the sampling rule at this point and not later. |
| 1.3 | 2026-09-02 | Checkpoint 1g. The paper's evidence became two-sided, and this version says so. Added **§5.5 blanket negative declaration** (how six checkers acquire a negative denominator without frame-by-frame annotation of seven kinds of nothing, and the conditions that keep that legitimate — signed before any alert from the span is inspected, per checker, refusable per checker); **§5.6 stratified reporting rule D8** (≥8 h reported separately, <8 h pooled with a footnote, and the added clause that clearing 8 h does not make a confounded stratum reportable); **§5.7 corpus M1 close**, recording that rule E3's 48 h threshold was crossed during `HOM_20260831_1800.mp4` and the corpus closed 2026-09-02T06:28:43+07:00 at 175 segments / 83.9775 h, with the two unreadable segments verified unreadable rather than assumed so. Added **§8, the ex-situ recall protocol**: ground truth is the source corpus's own annotation and is never re-cut by us; the clip list is fixed and SHA256-hashed before any clip is scored; sources are admissible only if obtainable without asking permission, and a checker with no admissible source drops to false-alarm-only; the §3 matching rule is unchanged (W = 2.0 s, P8 merge gaps) and a source whose annotation granularity cannot support it is declared inadmissible rather than accommodated; **an exhaustive table of the six permitted configuration deviations (E-1..E-6)**, which apply to the ex-situ branch only and leave the in-situ frozen-configuration guarantee untouched; two recall numbers wherever source fps/resolution differs from the deployment's, so that the cost of adaptation is measured rather than absorbed; and mandatory in-situ/ex-situ labelling enforced at build time. Added **§9, the pre-registered recall interval**, timestamped 2026-09-02 13:05 +07:00 while zero ex-situ clips had been scored and no allocation existed: upper bound is the measured ex-situ recall, lower bound is ρ × upper, ρ = 0.494 (median of OmniFall arXiv:2505.19889v3 Table 2's seven staged→wild sensitivity ratios) with the full range [0.080, 0.568] carried through the sensitivity analysis, plus an anti-tuning clause and an explicit statement of the assumption that a factor measured on a fine-tuned classifier is being borrowed for threshold rules. Sections 8 and 9 were appended rather than inserted as a "section 6" because `scripts/aap_common.py` and §5.2 cite section 6 as the file-format section. **No segment had been scored for any checker when this version was made, so nothing required re-scoring** — which is precisely what makes registering §9 at this point legitimate rather than convenient. |
| 1.3a | 2026-09-02 | Checkpoint 1h, same day, no measurement scored in between. Added principle **P9** (every countable quantity is counted by a script from the files actually used, regenerated at build time) after three same-shaped errors in one day, all of them trusting a digest instead of counting — including one in a file we generated ourselves, whose header order did not match the order `ffprobe` emits. Added **§8.8, the noise floor**: the cell of clips whose frame rate and resolution both survive adaptation unchanged is *not* a determinism control, because the adapted files were re-encoded with a lossy codec; a disagreement there confounds pipeline non-determinism with re-encode noise. A **cell 0** was added — the same native file run through the same pipeline twice — which isolates non-determinism alone, with the comparison predicate `(checker, event_type, t_alert, frame_idx, track_id)` fixed in writing before the runs, `confidence` excluded and reported separately, the result quoted as a rate rather than pass/fail, and a binding reading rule that no adapted-versus-native effect may be claimed below the floor. Cell membership is decided by decoded `nb_read_frames`, not by the container's frame-rate field, so a clip at 14.985 fps against an adapted 15/1 is correctly treated as changed. **Still no segment scored for any checker**, so nothing required re-scoring. |
| 1.4 | 2026-09-03 | Checkpoint 2b. **`PREREGISTERED_M3.md` is LOCKED**, SHA256 `dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a`, recorded here before the campaign queue was launched and before any sweep, verification or ex-situ threshold number existed. It carries Checkpoint 2a A1-A4 and Checkpoint 2b-pre K2-K5. Four changes in it bear on this protocol. **(a) Verification design (A1):** the "one segment per verification point" line is withdrawn -- at 0.5-8 false alarms per hour it yields 0-4 alerts per point and no measurable replay-to-real fidelity. Verification now covers only checkers that enter the allocation, runs three JOINT Fall x SmokeFire points over the whole 8-segment sample, and sweeps IntrusionChecker's `--conf` separately because it is upstream of ByteTrack and therefore of every module at once. The independence of the two downstream knobs is declared an assumption, not a proof. **(b) Stratification (A2):** the occupancy stratum is `ai_frames == 0` from the run metadata, not a remembered occupancy diary -- a stratification variable must divide the corpus reproducibly and need not mean what its name suggests; it is never reported as occupancy ground truth. The draw therefore waits for M1+ to reach 175/175, because drawing earlier would put every unmeasured segment in the "motion" stratum by default. **(c) Manifest durations:** eleven segments of 2026-08-31 carried muxer-supplied container timing (one overstated by 5.45 h, nine understated to 1 s), which nearly cancelled in the total -- a correct-looking headline over corrupt parts. Corrected by decoding, `duration = nb_read_frames / 14.883069` (median `avg_frame_rate` of the 164 healthy segments); **corpus 83.9775 h -> 83.9442 h**. The pre-fix manifest is kept; the signed declaration is not edited, an appendix carries both hashes. **New admissibility rule, binding: a manifest duration is admissible only if it agrees with the file's decoded frame count to within 10 %**, enforced in `validate_manifest.py`. **(d) IntrusionChecker enters the allocation (K3), reversing the decision of 2026-09-02 23:05.** The observation that its event definition is coextensive with the detector's output stands, and every VIRAT clip does collapse to one event under P8's 30 s gap; what does not follow is that it has no principled coverage curve. Because the event coincides with the detector's output, its curve IS the detector's person-recall curve, measured per image on COCO val 5000 over the B1 conf grid, declared a lower-bound proxy for event recall (tracker and `confirm_frames` can only raise it), with a mandatory with/without sensitivity pair. Helmet is deliberately NOT given the same proxy: its event is "a person WITHOUT a helmet", which is not coextensive with a single-class detector's output. **No segment had been scored for any checker at any operating point when this version was made, so nothing required re-scoring.** |
| 1.5 | 2026-09-03 | Added **section 5.8, observation time**: the denominator of every in-situ rate is the sum of `frames_read / fps` over the segments actually measured, and a manifest duration is descriptive only. Two hour figures were in circulation differing in the fourth decimal -- the recorder's account of the footage and the pipeline's account of what it decoded -- with nothing distinguishing them; the gap is trailing-frame loss in the camera's stream copy, characterised over the corpus in errata E3. `count_everything.py` now emits the two under separate names and **asserts** they agree once M1+ covers the manifest; `tier0_analysis.py` takes segment lengths from decoded frames and records how many came from each source, so a mixed figure says so. **No rate had been finalised when this version was made** -- every in-situ rate carries B8's PRELIMINARY status until coverage reaches 100 %, so nothing required re-scoring. |
| 1.6 | 2026-09-10 | Added **section 5.9, labelling provenance**. The three label packs (100 Intrusion, 12 Fall, 20 Helmet -- 132 cells) were returned filled, SHA256-sealed **before any cell was read**, and labelled **directly by the author in one pass (P1)** with no machine-assisted proposal step, so there is **no override rate** and S6 reports it as not applicable rather than blank. Records why there is no AI-assisted-labelling section: the arrangement `PROMPT_LABELLING.md` proposed for a section numbered 5.8 was never used, and 5.8 was taken by observation time in v1.5 the same day. Registers that the optional 50-alert loose pack, if ever drawn, inherits 5.9 and must register any machine assistance **before** its first image is opened. **The Fall spot-check returned 12/12 `false_alarm`, so errata E6 was NOT triggered and the blanket negative declaration for Fall stands**; Helmet returned 20/20 `false_alarm`, likewise. The Intrusion pack returned 100 YES / 0 NO / 0 UNSURE, giving FP-fraction 0/100 -- the first false-alarm denominator this campaign has had for that channel. Nothing was re-scored: the packs are inputs the rates were always waiting on, and every rate computed before today already carried B8 PRELIMINARY status for exactly this reason. |

---

## 11. Locked pre-registrations

Every file in this table was written before the quantity it governs existed, and is hashed here so that claim is checkable rather than asserted. A changed hash with no new row is a protocol violation.

| File | Locked | SHA256 |
|---|---|---|
| `PREREGISTERED_M3.md` (threshold sweep, samples, allocation roster) | 2026-09-03 09:40 +07 | `dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a` |
| `exsitu/virat/GT_running_virat.csv` (16 running events, **14** distinct clips -- see the errata row below) | 2026-09-02 22:10 +07 | `d1cb596f6c67e6102ed3fc370c19ca9e7ab8fc2c68dd5e337ef06f4ee5d1f260` |
| `exsitu/PREREGISTERED_CP1H.md` (FURG reading rules) | 2026-09-02 15:20 +07 | see file |
| `PREREGISTERED_M3_ERRATA.md` (E1 VIRAT clip count; E2 sample-draw provenance; E3 frame-count check; E4/E5/E7 pointers; **E6** the spot-check voiding rule restated) | 2026-09-03 11:25 +07, E4 pointer appended 2026-09-05 10:20 +07, E6 appended 2026-09-07 13:30 +07 | `cdf4f2b0857c9558ba93bac446d49c79581cb2d5ba304907c4664ae667eeb76a` — **current, re-hashed 2026-09-12.** (was `38a78d117687c001d112f3b96de6a8fa1387989fe9ea81b7ddbd2dd47d8f9213`, was `f7c69f00df27bf06a2e73db2b059f9b425b97878cb811b0946fa799d5d032655`, was `33f3087d10eb14bcdc048b6fb4b4d2fee225302212c858ede7a5fb0d2ad1a414`). **The file changed on 2026-09-10 13:14 — errata E7, HARNESS-26 — and neither this row nor the `.sha256` was updated until 2026-09-12, so for two days the registry asserted a hash the file did not have.** The change is identifiable and admissible under the errata boundary stated below: E7 corrects the DESCRIPTION of rho = 0.494 (it is not the median of the seven OmniFall ratios) and changes no decision, no grid, no seed, no sampling rule, no admission rule, and not rho. Recorded rather than silently re-hashed. |
| `PREREGISTERED_E4_CLOCK_STRATUM.md` (**E4** — the clock-substituted stratum and the admission rule for the in-situ FAR) | 2026-09-05 10:20:43 +07 | `2371fef5b718f76f3702d682f4a07ccf8170c89784deca20e9d5214eeb958885` |
| `PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md` (**E5** — two channels never instantiated in the recorded pass: out of in-situ scope, out of the allocation, two θ grid rows withdrawn) | 2026-09-06 12:48:44 +07 | `60aaa61bea38cbc54388c250107942f4ac96dbbbdf1f00b2793d43748ae8c41a` |
| `PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.md` (**E5 addendum** — the seven M4e ablation cells and the seeded 2 h sample, registered while M4e was still BLOCKED) | 2026-09-07 10:20 +07 | `6fd7fdb372fe85b643ab208470815cffbefe9c7cbc5ae23d09030d0ea9d2da15` |
| `PREREGISTERED_E7_C1B_PILOT.md` (**E7** — the C1b recorder pilot: two named segments, a four-condition gate with thresholds fixed before it runs, and a two-branch decision) | 2026-09-07 13:25:21 +07 | `78ff9ec16543da647803fa80d99b1126565d340ae63729a0be4ec30e1e854fdf` |
| `PREREGISTERED_E7B_AMENDMENT.md` (**E7-b** — the pilot cancelled before it ran; the pass whose recorded θ is lowest selected as the curve's source; the unrecorded-disjunct band reported as an interval) | 2026-09-07 14:22:02 +07 | `6d9bda777f235bc0062bdc52f992ed8ca82f5302d69575e4ee1544bd73d495eb` |
| `PREREGISTERED_E7C.md` (**E7-c** — the `high_scores` disjunct is θ-independent, so E7-b's `unrecorded_disjunct` band closes; but FallChecker's own state machine makes rescoring across θ inadmissible (`theta_transport`), measured on X4's five native passes, so E7-b's three "exact" A1 rows reduce to one. Partially supersedes E7-b; E7-b itself unchanged) | 2026-09-08 10:25:00 +07 | `2c7a5550474de37f85b9ea38f1c1f6b265f1c5531f819f937bc71a2be984d26e` |
| `PREREGISTERED_E7D.md` (**E7-d** — what the in-situ Fall θ-curve may be built from: native points only at one detector `conf`, rescored points as labelled upper bounds outside the allocation, C1 reported as a separate instrument setting; bootstrap/Wilson intervals fixed. Locked **before V1 ran**, with `out/v1_loose` verified absent) | 2026-09-08 10:46:16 +07 | `4ca3353ed82e27ca04e889cda8c7c3fcc07dd758f9a6516b55aefaa1fdb6732d` |
| `PREREGISTERED_E8_D5_SAMPLE.md` (**E8** — the D5 verification sample. Upgrade rule `U1-D5-full-corpus` is **withdrawn** and `D5f` is SKIPPED permanently, on the ground that the whole-corpus pass dissolves the 24+8 disjoint split and so makes a different, weaker claim rather than an upgrade; the `measured_rtf` defect of HARNESS-23 is recorded as the reason the decision could not wait, and explicitly NOT as the reason for it. `PREREGISTERED_M3.md` is not edited. U2 and U3 untouched. Locked **before D0 ran**, with `out/d0_allocation/` and `allocated_theta.json` verified absent and every upgrade rule `applied = null`) | 2026-09-09 10:46:00 +07 | `ba2112c2fc92cc5d8340f3ca35aa20d56e80cf10d7e07ba56ec58908e0efe605` |
| `PREREGISTERED_E9_CHANNEL_RECOVERY.md` (**E9** — recovering two channels. (a) **X3b**: RunningChecker is a side checker that consumes the STD detection pass, so `--modules running` alone left `boxes` None on 44 801/44 801 frames and `process()` executed 0 times (HARNESS-24); it is re-measured at the SAME registered theta grid, clip list, ground truth and matching rule, with `intrusion` present only to produce boxes, and a decision rule fixed in advance on `side_calls_with_boxes`. (b) **SFCTL**: one FURG pass at `confidence_threshold` 0.01, declared BEFORE it runs to be instrument validation and to enter no curve, table or allocation, with a two-branch reading rule and no third branch. (c) the M4e cell `only_RunningChecker` carries the same side-channel defect and is redefined as `only_RunningChecker_with_std`; the E5 addendum is NOT edited. No theta, clip list, ground truth, matching rule or interval method is changed. Locked before either job existed) | 2026-09-09 11:30:43 +07 | `3a9a750199c654ab1b7a31af91604d19111f05d5a1ee3cbca440dfeeac63def8` |
| `PREREGISTERED_E10_RUNCTL.md` (**E10** — the RunningChecker positive control: one pass over the X3b clips at `run_vel_threshold` 0.01, declared before it ran to be instrument validation and to enter no curve, table or allocation, with both reading branches written down and no third branch, and an explicit clause that it cannot remove the channel from the allocation) | 2026-09-10 16:57 +07 | `d350b51daa883a50f25218d3a401ff60beed8eb31583ffaa9e8a2051c89bbe01` |
| `PREREGISTERED_E10B_AMENDMENT.md` (**E10-b** — the control dispatched to the other checkers and not to Running, so the measured zero separates into a zero for the channels that ran and an uncharacterised path for the one that did not. Registered as an amendment with its own hash rather than as an edit to E10, and locked BEFORE RUNCTL started) | 2026-09-10 21:05 +07 | `ba97277117bfa240c43bb8b7128e9035259c0063017899da997a86215fca2243` |
| `PREREGISTERED_E12_COST_AXIS.md` (**E12** — the in-situ cost axis of the fall front: the defect stated in counts, the ban on a silent switch to A1 after seeing that the registered choice did not resolve, a two-sided reporting rule with both branches written before the recomputation, and the theta range each axis can price. Locked **before** `scripts/e12_cost_axis.py` ran) | 2026-09-11 16:01:48 +07 | `c36865afb79f42d58fd4ac68fe0058c073e48dd3b7287708cb76298529c03b90` |
| `PREREGISTERED_E12B.md` (**E12-b** — E12's two-sided rule does not cover what E12's own step 2 produced. The **registered axis emitted zero points**: the C2 replay recovered 0 of 185 FallChecker alerts, verdict `stateful_divergence`. A **third** axis exists and is the one the code silently prices on. E12 section 4's C1 column is falsified, which leaves the high-coverage end priced only by the unregistered axis. Registers a three-axis reporting rule, forbids naming a single allocated theta where the A1 bootstrap intervals overlap, and registers the demonstration point D5s runs at together with the rule that selects it. **E12 is not amended.** Locked before one sentence about the three axes was written into the manuscript) | 2026-09-12 09:11:28 +07 | `e1b3e2249c530f1f2fb81589a27077b739c094d28203bcfe89299ba2da8da0e3` |
| `PREREGISTERED_E12C.md` (**E12-c** — amends **one clause** of E12-b, item 5, and nothing else: the coverage hole at the high-coverage end stays **in the main text, next to the coverage number, carrying the factor-58 interval and the fact that its pass was selected by code and not by a registration**, while the working-through moves to the supplement. Reason: page budget, author decision 2026-09-13 in chat. **No number changes.** E12-b items 1–4, 6, 7 and E12 §4 are unaffected; `PREREGISTERED_M5_WITHDRAWAL.md` §4 is explicitly NOT amended because that paragraph was left word for word in Section III. Hashed **before** the paragraph was moved, with the paragraph verified still in place) | 2026-09-13 11:56:21 +07 | `1498fde5a0d37f5d0fa4432b2a0f89ce7907b954a3a538beb6ef1336c30cb063` |


**What an errata file may and may not do.** An errata attached to a locked pre-registration may correct only a **descriptive count of something that already exists** -- how many clips, how many events, how many hours -- where the stated value and the file of record have come apart. It may **never** change a **decision**: not a θ grid, not a seed, not a sampling rule, not an admission rule, not ρ. Changing a decision requires a new version of the pre-registration with a stated reason and a new hash, and the superseded version is kept. The distinction is the whole point of locking: a count was always meant to describe the world and can be wrong about it, whereas a decision was meant to bind us before we saw the world and cannot be revised by discovering what the world turned out to be. Without this line an errata file is a back door.

**The first time that line was inconvenient: 2026-09-05.** The rule deciding
whether eleven clock-substituted segments stay in the in-situ false-alarm
denominator is an **admission rule**, so it could not be errata E4 however
naturally it followed E1–E3. It was registered as its own locked
pre-registration, `PREREGISTERED_E4_CLOCK_STRATUM.md`, and the errata file
carries only a pointer. A boundary that is only observed when it costs nothing
is not a boundary.

**The second time, 2026-09-06 — and this one costs nothing, which is the harder
case.** Two of the seven checkers were never built in the recorded pass, so they
have no in-situ rate and no upper bound. Removing them from the θ grid is a
change to a **decision** — a grid — so it could not be errata either, however
obviously right it is and however little machine time it saves. It was
registered as `PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md`. The rule that made
E4 expensive to obey is the same rule that makes E5 cheap to obey, and a
boundary observed only when it is expensive is the same non-boundary as one
observed only when it is cheap.


---

## 5.8 Observation time — one source, and it is the decoded one

**Registered 2026-09-03 11:30 +07.** Appended rather than inserted, for the
reason recorded for sections 8 and 9: `scripts/aap_common.py` and section 5.2
cite section numbers by position, and renumbering them to make a document read
tidily is how a citation quietly starts pointing at the wrong rule.

> **Observation time = the sum of `frames_read / fps` over the segments
> actually measured. A manifest duration is descriptive only and is never the
> denominator of any rate.**

**Why this needs saying.** Two quantities were in circulation and they
disagreed: what the recorder wrote down about the footage it collected, and
what the pipeline actually decoded from it. They differ by a few parts in ten
thousand, because some segments lose between one and ten trailing frames to
damaged macroblocks in the camera's H.264 stream copy — a property of the
footage, established over the corpus (errata E3), not a defect in any run.

A few parts in ten thousand is precisely the size of discrepancy that never
gets noticed and never gets explained. A corpus table and a false-alarm
denominator quoting hours that differ in the fourth decimal, with nothing in
either saying which is which, is not a rounding question: it is two numbers
claiming to be the same number.

**How it is enforced, not merely stated.**

- `scripts/count_everything.py` emits `insitu_hours` (the decoded sum, the
  denominator) and `insitu_manifest_hours` (descriptive) as separate,
  separately named quantities, under P9.
- `analysis/tier0/tier0_analysis.py` takes each segment's length from its
  decoded frame count wherever the segment has been measured, and records
  `corpus.hours_source` — how many segments came from each — so a mixed figure
  announces that it is mixed.
- Once every manifest segment has been measured, `count_everything.py`
  **asserts** that the corpus hours and the denominator agree to within
  0.01 h, and refuses the build's clean bill of health if they do not. While
  coverage is below 100 % the corpus figure is labelled MIXED and may not be
  quoted as a denominator, and every in-situ rate carries the PRELIMINARY
  status of B8.

The point of the assertion is the lesson this protocol has now learned three
times: an invariant that lives only in a sentence is an invariant nobody is
enforcing, and it looks exactly the same whether or not it holds.

---

## 5.9 Labelling provenance — the 132 cells were labelled by a human, in one pass

**Added 2026-09-10T16:20 +07:00, after the three packs were returned and
SHA256-sealed, and before any verdict in them was read.** The seal is
`GT_protocol/LABEL_PACK_SEAL_20260910.md`.

### What was done

| pack | cells | file | SHA256 |
|---|---:|---|---|
| Intrusion | 100 | `intrusion_label_pack/labels.csv` | `dea87abb233f3362da467836e6f3fe651cd38a9ddf5c207b0594217fb5ecbb1b` |
| Fall spot-check | 12 | `spotcheck/spotcheck_FallChecker.csv` | `82843c354e518a9cc16afc043e9adbd22cd08a4b17f04060257cf0bb5362d574` |
| Helmet spot-check | 20 | `spotcheck/spotcheck_HelmetChecker.csv` | `55c1dac3526df28dfa7bf06614a967d5a13b541e29ff0b17095444b2ba70cdb0` |

All 132 cells were filled **directly by the author, pass 1 only (P1)**, the
procedure §5 already specifies. **No machine-assisted proposal step was used**:
no model produced a candidate verdict, so no verdict was adjudicated, so there
is no override rate.

### Why there is no §5.8 about AI-assisted labelling, and why this section is 5.9

`PROMPT_LABELLING.md` (2026-09-03) proposed adding a section numbered **5.8**,
*"AI-assisted labelling, human-approved"*, to be written **before any image was
opened**, because the plan of the day was for a model to propose and the author
to approve. **That plan was not used.** §5.8 was meanwhile taken by *Observation
time* in v1.5 on the same day, and the labelling section was never written
because the arrangement it would have governed never happened.

So there is nothing to narrow: this section **records the procedure that was
actually used** rather than scoping down a rule for one that was not. Renumbering
§5.8 to make room would rewrite a section that four scripts and two errata cite
by number, to describe a thing that did not occur.

### The optional 50-alert loose pack, if it is ever drawn

`PROMPT_LABELLING.md` §4 registers an optional second pack: 50 alerts drawn
**only** from those present at conf 0.15 and absent at 0.25 — the margin, which
is where a second FP-fraction point has to come from — seed 20260905, same
question, same blinding.

**If that pack is ever drawn it inherits §5.9's requirement, not an exemption
from it.** Should it be labelled with machine assistance rather than by hand,
that arrangement must be registered **before the first image is opened**, in its
own dated section, carrying at minimum: that the model sees one image at a time
with no score, threshold or timestamp; that every proposal is adjudicated by the
author; that the override rate is computed and reported; and that a disagreement
is resolved in favour of the human without the model's proposal being deleted.
A pack labelled first and registered afterwards is not admissible, and the
two-point interpolation §4 describes — linear between 0.15 and 0.25,
**extrapolation forbidden** — is unaffected either way.

### Consequence for the supplementary material

Supplementary Section S6 was scaffolded to report an **override rate**. There is
none to report, and the section must say **not applicable, because labelling was
direct and single-pass**, rather than leaving the figure blank. A blank invites
the reading that a number exists and is being withheld; the whole point of §5.9
is that the number does not exist because the step that would produce it never
ran.

---

## §11 registry — locked pre-registrations

| id | file | SHA256 | locked |
|---|---|---|---|
| E10 | `PREREGISTERED_E10_RUNCTL.md` | `d350b51daa883a50f25218d3a401ff60beed8eb31583ffaa9e8a2051c89bbe01` | 2026-09-10 evening |
| E10-b | `PREREGISTERED_E10B_AMENDMENT.md` | `ba97277117bfa240c43bb8b7128e9035259c0063017899da997a86215fca2243` | 2026-09-10 evening, BEFORE RUNCTL started |
| E12 | `PREREGISTERED_E12_COST_AXIS.md` | `c36865afb79f42d58fd4ac68fe0058c073e48dd3b7287708cb76298529c03b90` | 2026-09-11 16:01:48, BEFORE `e12_cost_axis.py` ran |
| E12-b | `PREREGISTERED_E12B.md` | `e1b3e2249c530f1f2fb81589a27077b739c094d28203bcfe89299ba2da8da0e3` | 2026-09-12 09:11:28, BEFORE any sentence about the three axes reached the manuscript |

**These two tables are one registry kept in two places, and they had drifted.** The table under `## 11. Locked pre-registrations` ran M3 to E9 and stopped; this appendix carried E10 and E10-b and nothing else; E12 was in neither, although E12 section 5 step 1 made the entry a binding step of its own order of operations. Both were completed 2026-09-12. A registry that is written in two places and checked in neither is the same defect this paper reports in the system under test, and it is recorded here rather than quietly fixed.


E10 registers a positive control for `RunningChecker` at a threshold below the
registered grid, with both reading branches and the cost written down **before
the run exists**, and with an explicit clause that it **cannot** remove the
channel from the allocation — E9 §1.4 admitted it on a criterion already
satisfied, and an admission rule is not reopened because its result was
inconvenient.
