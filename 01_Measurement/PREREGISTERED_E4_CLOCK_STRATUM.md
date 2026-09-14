# PREREGISTERED E4 — the clock-substituted stratum, and the rule that decides whether it stays in the in-situ FAR

**Registered 2026-09-05, 10:20 +07:00, on the PC.**
**A1 stands at 155/175 and is projected to reach 175/175 at ~22:30 the same day.**
This document is therefore written **before the measurand it governs exists**, which
is the only moment at which writing it is worth anything.

---

## 0. Why this is a pre-registration and not errata E4

`PREREGISTERED_M3_ERRATA.md` carries E1, E2 and E3. This one does **not** go in
there as a fourth entry, and the reason is a rule already on the record.

GT_PROTOCOL section 11:

> An errata attached to a locked pre-registration may correct only a
> **descriptive count of something that already exists** … It may **never**
> change a **decision**: not a θ grid, not a seed, not a sampling rule, not an
> **admission rule**, not ρ. Changing a decision requires a new version of the
> pre-registration with a stated reason and a new hash.

Section 2 below is an **admission rule**: it can remove eleven segments from the
denominator of the reported in-situ false-alarm rate. Filing that as errata would
be using the errata file as the back door section 11 names. So it is registered
here, as its own locked artefact with its own hash and its own row in the section
11 table, and `PREREGISTERED_M3_ERRATA.md` gets a one-paragraph **E4 pointer** so
that a reader working through E1–E3 finds it.

The label **E4** is kept because that is what it is called in the working record.
It is a pre-registration wearing an errata's name, not an errata.

---

## 1. What happened, and why a measurand is at risk

On 2026-09-05 at 09:08 the first of the eleven clock-substituted segments
(`HOM_20260831_0800`) finished its second pass. Two things were true of it at once:

- `check_segment_output.py` **PASS** — the substitution path worked end to end;
- the runner log is full of `[h264] error while decoding MB …`, and the segment
  decoded **9 % slower** than the healthy group (39.7 min/segment against 36.34,
  rtf 0.74 against 0.828).

These eleven files are the ones HARNESS-5 found in 2026-08-31 08:00–13:00: the
recorder stored the camera's own H.264 bitstream with `-c:v copy`, and on these
eleven the bitstream is damaged badly enough that the container's frame rate came
out as 1.3444, ~14 790 and 156.97 fps. The corrupt timing and the decode errors
are **the same defect seen twice**: a damaged bitstream.

**The threat to the measurand.** A decoder recovering from damaged macroblocks
emits frames that are partly reconstructed from the wrong reference — smears,
ghosted blocks, torn regions. A person-detector run over such a frame can fire on
something that was never in the room. An alert produced that way is a property of
**the recorder**, not of **the scene**, and the in-situ false-alarm rate is a
statement about the scene. Eleven segments of 175 is 6.3 % of the corpus and
5.4645 h of 83.94; if their alert rate is not the corpus rate, pooling them moves
the headline number.

This is a threat that must be answered by a rule fixed in advance, because the
alternative — look at the eleven numbers, then decide whether they belong — is
indistinguishable from choosing the answer.

---

## 2. The rule

### 2.1 The two strata

| stratum | definition | n | observation time |
|---|---|---:|---:|
| `clock_substituted` | the segments named in `analysis/tier0/duration_corrections.json` (SHA256 `4a6391e2f5c273e48a3119ab4067d046fb9e38396a1595a23934d2d40af228d1`), the registered HARNESS-5 table | **11** | **5.4645 h** (registered table; the measured value replaces it and must agree to 1 %) |
| `native` | the complement, `|manifest| − |table|` | **164** — **derived count**, per the author's decision of 2026-09-04 | filled by measurement |

Membership of `clock_substituted` is confirmed segment by segment against
`fps_override_applied` in the run metadata, and `count_everything.py` already
refuses to report any rate if the table and the outputs disagree
(`CLOCK PROVENANCE DISAGREES`). Nothing about that changes here.

The eleven segments are:

```
HOM_20260831_0800  HOM_20260831_0830  HOM_20260831_0900  HOM_20260831_0930
HOM_20260831_1000  HOM_20260831_1030  HOM_20260831_1100  HOM_20260831_1130
HOM_20260831_1200  HOM_20260831_1230  HOM_20260831_1300
```

### 2.2 Three numbers, always

Every in-situ false-alarm rate — **FallChecker, HelmetChecker (A0),
IntrusionChecker, and the four checkers observed at zero** (EnhancedHelmetChecker,
SmokeFireChecker, RunningChecker, ForkliftSpeedChecker) — is reported as **three**
figures with their intervals:

| figure | segments | hours |
|---|---:|---|
| pooled | 175 | all |
| native | 164 | native only |
| substituted | 11 | substituted only |

Intervals follow current practice unchanged: **two-sided 95 % Poisson upper limit
`3.689/T` (P6) where the count is zero**, and the **segment block bootstrap**
(whole segments as blocks, 10 000 iterations) where it is not. The bootstrap seed
for the stratum intervals is **20260905**, fixed here.

All three appear whichever branch section 2.3 takes. **Nothing is deleted by the
decision; only the label "the FAR" moves.** That is the property that makes the
rule safe to write when the direction of the answer is not neutral (section 4).

### 2.3 The decision rule — fixed before the numbers exist

> For each checker *c*, compute the 95 % interval of `FAR_c` on the **11**
> substituted segments, and the **point estimate** of `FAR_c` on the **164**
> native segments.
>
> **If, for at least one checker, the native point estimate lies OUTSIDE the
> substituted stratum's interval**, then the eleven segments are a stratum of
> their own:
>
> - they are **removed from the headline in-situ FAR**;
> - the headline observation time becomes the **164 native segments**;
> - GT_PROTOCOL §8.5 gains a row naming the eleven as a **recorder artefact**;
> - their own three-figure row stays in the results, and the supplement carries
>   the comparison that triggered the split.
>
> **Otherwise**, the **pooled 175** figure is the headline in-situ FAR, the
> observation time is all 175 segments, and the eleven appear only in the
> supplement.

**One decision for all checkers, not one per checker.** A single checker whose
native point estimate falls outside the substituted interval separates **all
eleven segments** for **every** checker. Choosing per checker would let the same
eleven segments be inside the corpus for one rate and outside it for another,
which is not a corpus.

**The direction of the comparison is the one written above and is not
reversible.** The substituted stratum supplies the interval because it is the
stratum under suspicion and the smaller one; the native stratum supplies the point
estimate because with 164 segments it is the better-determined of the two. Testing
it the other way round — native interval, substituted point — is a different test
with different power, and picking between them after seeing both is the thing this
document exists to prevent.

### 2.4 When the rule may be evaluated, and what stands until then

The rule is evaluated **once**, and only when **both** strata are complete: all
**11** substituted and all **164** native segments measured, i.e. A1 at 175/175
with `check_segment_output.py` PASS on all of them.

Until that instant the flag is **`[TBD]`** and no branch may be quoted. A
partially-measured stratum is explicitly **not** a permitted input: evaluating on
the 2 of 11 that exist today, or on any other subset, would make the answer depend
on which segments happened to be finished, and the order they are measured in is
an artefact of a sentinel's file list. `count_everything.py` **refuses** to
compute the flag on an incomplete stratum rather than computing it on what it has.

### 2.5 Degenerate cases, decided here rather than when they arise

- **Zero in both strata.** The interval is `[0, 3.689/T_subst]`, the native point
  estimate is 0, 0 is inside — that checker contributes **no** separation. This is
  correct and is stated so that "zero versus zero" is not later argued either way.
- **`T_subst = 0`** (no substituted segment measured): flag `[TBD]`, no branch.
- **Interval undefined** (bootstrap returns NaN): flag `[TBD]`, and the run says
  so. It never silently becomes `false`.
- **A checker present in one stratum and absent from the other** is not a special
  case: absence is a count of zero over a known observation time.

### 2.6 The power of this rule, stated in advance

The substituted stratum is **5.4645 h**. For a checker with zero alerts there, the
two-sided 95 % Poisson upper limit is **0.675 alerts/h**. Any native rate below
that is inside the interval and cannot separate the stratum. So the rule is, by
construction, **conservative toward pooling** for the low-rate checkers, and can
realistically only fire on a high-rate one (HelmetChecker's last reported figure
was 8.0468/h, IntrusionChecker's higher still).

This is a limitation, not a defect to be tuned away, and it is written down now so
that it cannot be presented later as a finding. **A stratum of 5.5 h cannot
adjudicate a rate of a tenth per hour, and this rule does not claim to.**

### 2.7 Relationship to D8 (GT_PROTOCOL 5.6), which says the opposite

D8 says a stratum with **< 8 h** is **pooled**, with a footnote naming it. The
substituted stratum is 5.4645 h and would be pooled under D8. This document can
still separate it, and the distinction is not a loophole:

- **D8 governs presentation of scene strata** — camera view, domain, time band —
  where every stratum is a valid observation of the world and the only question is
  whether it has the resolution to earn its own row. Its 8 h threshold is a
  statistical-resolution threshold.
- **E4 governs admissibility** — whether eleven segments are an observation of the
  *scene* at all, or partly an observation of a *decoder*. That question is not
  about resolution, and a stratum that fails it does not become admissible by
  being small.

D8 continues to govern, unchanged, how the surviving segments are broken into
view and day/night rows under either branch. And D8's substantive protection —
that no stratum silently disappears into a total — is honoured more strictly here
than D8 requires: section 2.2 reports the eleven **as their own row with their own
interval in every branch**, which is more than the footnote D8 asks for.

Where E4 and D8 would give different answers, **the reason is recorded in the
results text, not resolved silently.**

---

## 3. Ex-situ: the rule does not apply, and that is a fact about the data

There is **no clock-substituted stratum ex situ**. Every ex-situ source —
GMDCSA24, FURG, VIRAT — is downloaded from its publisher, not recorded by our
recorder, and none of the 11 substituted segments is ex-situ material. `--fps-override`
has never been passed on an ex-situ run, and `fps_override_applied` is absent or
false in every ex-situ run's metadata.

The ex-situ branch has its own, **different** clock deviation, already registered
and unaffected by this document: **E-7** in GT_PROTOCOL §8.5, VFR → CFR
normalisation over 160/160 GMDCSA24 clips. E-7 is a deliberate normalisation
applied uniformly by us; the substitution here is a repair of damage done by the
recorder to 11 of our own files. They are not the same kind of thing and are not
pooled, compared, or reported together.

**No ex-situ number changes under either branch of section 2.3.**

---

## 4. Honest declaration — what had already been seen when this was written

A pre-registration whose honesty clause is wrong is worse than none. The claim
originally drafted for this section was *"output for 1 of the 11 exists and nobody
has read its alert count; only metadata was checked."* **Both halves of that are
false**, and the true position is set out here instead.

### 4.1 Two of the eleven have output, not one

| segment | `.csv` written | SHA256 `.csv` | SHA256 `.json` |
|---|---|---|---|
| `HOM_20260831_0800` | 2026-09-05 **09:08:09** | `9d1a20711fcca3263a3bc4d5b69a1bff94b02b1ab489ade9d0dced24e7d8af62` | `7513277dbfccc855488dd790451741cfe5f55e7d1f9d7ff8b99b3239c03132c8` |
| `HOM_20260831_0830` | 2026-09-05 **09:48** | `00479dfcb882ac9024ff0b4d54859a0f995b62c3fccb79b969243e6344e99496` | `349fd6d1d31da9c59f118d75846afba98f8141753882f0f93ee072174d757192` |

Hashes taken on the Jetson at 2026-09-05 10:16 +07, before this file was written.

### 4.2 The alert total of one of them has already been read and published

`STATUS_CHECKPOINT.md` line 3104, written **2026-09-05 09:09** — an hour before
this registration and seven minutes before the instruction to write it — records
of `HOM_20260831_0800`:

> **163 alert, 3404 ai_frames.**

That file is SHA256 `3b116f7aad2ddb251919ba0d0fac5bd5b3784b4c7767f5830d5e21d8c6a3e2bb`.
So **this rule is registered by people who already knew the alert total of 1 of
the 11 segments it governs.** 163 alerts over 1770.8 s is **331 alerts/h**, and
that is a large number next to any per-checker in-situ rate reported so far.

**What is still unread**, and is stated so it can be checked against the record:

- **no per-checker breakdown** of those 163 has been read — only the total;
- **no alert number of `HOM_20260831_0830`** has been read, in total or per
  checker; only its file size, mtime and hashes;
- **no alert number of the other nine** exists yet;
- the native stratum's per-checker totals have not been recomputed since the
  corpus grew past the 52 segments behind the last published FAR figures.

One further partial leak, recorded because it is the kind that goes unrecorded:
a directory listing taken while preparing this document showed `.csv` sizes —
16 138 and 16 274 bytes for the two substituted segments against 74 bytes for
three recently-finished native segments. 74 bytes is a header row alone. That is
not an alert count, but it is **correlated with one**, and pretending a size
listing is neutral metadata would be the same self-deception as the sentence
struck from section 4.

### 4.3 Why the rule is still worth registering, and what the leak costs it

It costs it the word *blind*. What it does not cost:

- the rule is **mechanical** — a comparison of a point estimate against an
  interval, computed by `count_everything.py` from the files, with **no
  hand-set constant and no per-checker discretion** (section 5);
- the rule is fixed **before ten of the eleven numbers exist**, and before **any**
  per-checker number in the stratum exists;
- both branches are written out in full, in advance, in section 6, so neither can
  be drafted to suit the outcome.

**The conflict of interest, named.** Separating the stratum **lowers** the reported
headline false-alarm rate — it removes segments suspected of being alert-rich from
the numerator and 5.46 h from the denominator. That is the direction that
flatters the system, it is the direction the one number already seen points in,
and a rule with that property must not be assessed on its author's good faith.
The three guards against it are: the three-figure rule (2.2), which keeps the
substituted numbers in the paper under every branch; the single global flag (2.3),
which stops the split being applied only where it helps; and the fact that both
result sentences are written below before the flag is computed.

---

## 5. What the machine does — P9 macros and the flag

Implemented in `01_Measurement/scripts/count_everything.py`. Under P9 no countable
quantity is typed by hand, and **that includes this flag**: it is derived by the
script from section 2.3, and there is no code path by which a person sets it.

| macro | meaning |
|---|---|
| `\CntFarNativeN` | segments in the native stratum contributing to the FAR |
| `\CntFarSubstN` | segments in the clock-substituted stratum contributing to the FAR |
| `\FlagSubstStratumSeparated` | `true` / `false` / `[TBD]`, from section 2.3 |

Supporting quantities, also generated: per-stratum hours, per-checker counts and
rates on each of the three figures, the interval bounds, the identity of the
checker(s) that triggered a separation, and the interval method used for each
(`poisson-2s-95` or `block-bootstrap-95`).

`\FlagSubstStratumSeparated` is `[TBD]` until section 2.4's condition is met, and
a `[TBD]` flag makes both branch sentences unusable — the build gate fails on any
attempt to typeset a result that depends on it.

---

## 6. Both sentences, written now, before the flag is computed

Whichever branch the flag selects, the sentence used is the one below it. Numbers
inside them are macro references, never digits, so the sentence follows the corpus
or fails to compile.

### 6.1 §8.5 sentence — if `\FlagSubstStratumSeparated` is **true**

> `\CntFarSubstN` of `\CntInsituSegments` segments recorded 2026-08-31 08:00–13:00
> carry a damaged H.264 bitstream: the container's frame rate is unusable
> (HARNESS-5) and the decoder reports macroblock errors throughout. Their alert
> rate is separated from the in-situ false-alarm rate under pre-registration E4 as
> a **recorder artefact**, the pre-registered comparison having placed the native
> point estimate outside the stratum's 95 % interval. The reported in-situ
> observation time is the `\CntFarNativeN` native segments; the separated stratum
> is reported in full, with its own interval, in the supplement.

### 6.2 §8.5 sentence — if `\FlagSubstStratumSeparated` is **false**

> `\CntFarSubstN` of `\CntInsituSegments` segments recorded 2026-08-31 08:00–13:00
> carry a damaged H.264 bitstream (HARNESS-5) and were rescored on the registered
> substituted clock. The pre-registered test of E4 did not distinguish their alert
> rate from the native stratum's for any checker, so they remain **pooled** in the
> reported in-situ false-alarm rate over all `\CntInsituSegments` segments; the
> per-stratum figures are given in the supplement.

### 6.3 Harness sentence — if **true**

> A recorder that stores its camera's bitstream untouched preserves the damage
> along with the picture, and a detector cannot tell a reconstructed macroblock
> from a room: the defect that made eleven segments lie about their frame rate is
> the same defect that makes their alerts a measurement of the recorder.

### 6.4 Harness sentence — if **false**

> The eleven segments whose container timing was unusable produced alerts at a
> rate the pre-registered test could not distinguish from the rest of the corpus,
> so the damage that corrupted their timing did not measurably reach the
> detector — a negative result worth reporting, because the rule that would have
> removed them was written before it was known which way it would fall.

---

## 7. Lock

This file is locked at the SHA256 recorded in its `.sha256` sidecar and in
GT_PROTOCOL section 11. It is not edited. If the rule turns out to be wrong, it is
**superseded by a new version with a stated reason**, and this text is kept.

Nothing in the eleven segments' output is opened for its alert content until this
lock exists.
