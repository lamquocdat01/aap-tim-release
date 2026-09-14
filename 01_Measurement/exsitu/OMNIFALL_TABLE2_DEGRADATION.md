# PUBLISHED STAGED-TO-WILD DEGRADATION — the evidence behind the Proposition 3 interval

**Purpose.** Rule G5 requires that the *lower* bound of the recall interval come from
independently published degradation factors, never from our own numbers. This file
records that published evidence, verbatim, with its provenance, so that the
pre-registered rule in `GT_PROTOCOL.md` §9 can be checked against its source.

**Source (verified by opening the paper, 2026-09-02):**

- Sadhukhan *et al.* / Schneider *et al.*, **"OmniFall: From Staged Through Synthetic
  to Wild, A Unified Multi-Domain Dataset for Robust Fall Detection"**,
  arXiv:2505.19889. Version history: v1 2025-05-26, v2 2026-02-27, **v3 2026-07-01**.
  Numbers below are from **v3**, retrieved from `https://arxiv.org/html/2505.19889v3`.
- The table quoted is the paper's **Table 2**, captioned: *"Per-dataset in-domain (ID)
  vs. in-the-wild (ItW) generalization. A VideoMAE-K400 model is trained on each staged
  dataset and tested on its own test split (ID) and on OF-ItW. Sensitivity, Specificity,
  F1 score."*
- OF-ItW is 818 manually verified OOPS clips (2.65 h, ~1.3k segments), used **test-only**.

## The measurement that matters

One architecture (VideoMAE-K400), one training recipe, one class definition. The only
thing that changes between the two blocks is **where the test video came from**. That
is precisely the quantity this paper needs and cannot measure for itself.

### Class `Fall`

| Train dataset | Se (in-domain) | Se (in-the-wild) | **ρ = Se_ItW / Se_ID** | Sp (ID) | Sp (ItW) |
|---|---:|---:|---:|---:|---:|
| CMDFall   |  91.2 | 51.1 | **0.560** | 99.3 | 86.9 |
| UP-Fall   |  57.9 |  9.5 | **0.164** | 99.8 | 99.6 |
| Le2i      | 100.0 | 56.8 | **0.568** | 100.0 | 94.8 |
| GMDCSA24  |  76.5 | 37.8 | **0.494** | 93.4 | 96.7 |
| EDF       | 100.0 | 15.6 | **0.156** | 100.0 | 98.6 |
| OCCU      | 100.0 |  8.7 | **0.087** | 97.7 | 98.4 |
| CAUCAFall | 100.0 |  8.0 | **0.080** | 94.7 | 98.9 |

Summary of ρ over the seven staged sources: **min 0.080 (CAUCAFall), median 0.164 (UP-Fall), max 0.568 (Le2i), mean 0.301**.

> **Corrected 2026-09-10 (errata E7).** This line previously read "median 0.494". It is not the median: sorted, the seven ratios are 0.080, 0.087, 0.156, 0.164, 0.494, 0.560, 0.568, and 0.494 is the row for **GMDCSA24** — the corpus this campaign replays to measure fall coverage, which is why it is the right central value and was the wrong name for one. min, max and mean were correct. The registered bound and its swept range [0.080, 0.568] are unchanged; see `PREREGISTERED_M3_ERRATA.md` E7.

### Class `Fallen`

| Train dataset | Se (ID) | Se (ItW) | ρ |
|---|---:|---:|---:|
| CMDFall   |  92.0 | 10.0 | 0.109 |
| UP-Fall   |  40.4 |  1.6 | 0.040 |
| Le2i      | 100.0 | 50.5 | 0.505 |
| GMDCSA24  |  76.5 | 12.3 | 0.161 |
| EDF       |  65.0 | 18.9 | 0.291 |
| OCCU      | 100.0 |  1.5 | 0.015 |
| CAUCAFall | 100.0 | 11.2 | 0.112 |

## The two facts this table establishes

**1. Sensitivity collapses; specificity does not.** Across all seven sources, specificity
stays in 86.9–99.6 going from staged to wild, while `Fall` sensitivity falls to between
8% and 57% of its in-domain value. A model can look almost unchanged on the metric that
counts false alarms while losing most of its coverage. This is the same asymmetry the
present paper measures from the opposite direction — we can see our spending precisely
and cannot see our coverage at all — and it is independent confirmation that the
asymmetry is a property of the problem, not of our instrument.

**2. The degradation is large and highly variable.** A factor of seven separates the
best-transferring source (Le2i, 0.568) from the worst (CAUCAFall, 0.080). An allocation
that assumes a point estimate of recall is therefore not merely imprecise, it is
choosing an arbitrary point inside an interval an order of magnitude wide. This is the
justification for treating recall as an interval in Proposition 3 rather than a scalar.

## The assumption that must be declared, not hidden

OmniFall's ρ is measured on a **learned end-to-end video classifier**. The checkers in
this paper are **hand-tuned rule modules stacked on a frozen detector and tracker**.
Nothing guarantees the two degrade by the same factor, and it is entirely possible that
a threshold rule on a person detector degrades *less* (it depends on a simpler cue) or
*more* (it has no capacity to adapt) than a fine-tuned VideoMAE.

We therefore do **not** claim ρ transfers. We claim only this: the published evidence
shows staged-to-wild sensitivity degradation of this magnitude is normal rather than
exceptional, which makes a wide pre-registered interval the defensible modelling choice
and a point estimate the indefensible one. The sensitivity analysis required by G5 —
how wrong may the recall curves be before the allocation *order* changes — is what
carries the argument, and it is reported over the whole range, not at a single ρ.

## Licence note

The numbers above are facts from a published paper, cited normally. They are not
data reuse and carry no licence obligation. The OmniFall *annotations* are
CC BY-NC-SA 4.0 and are handled separately in `EXSITU_SOURCES.md`.
