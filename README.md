# Asymmetric Evidence, Formalized: What a Deployment Can and Cannot Measure about a Multi-Channel Edge Camera Monitor — reproduction package

Repository: **https://github.com/lamquocdat01/aap-tim-release** · tag **`tim-v3`** (earlier tags `tim-v1`, `tim-v2` are kept).

Author: Dat Lam Quoc, FPT School of Business and Technology, FPT University, Ho Chi Minh City,
Vietnam (ORCID 0009-0004-5432-9343).

> **A GitHub URL is not a persistent identifier.** No DOI-backed archival copy of this package
> exists at the time of submission. The tag `tim-v3` identifies the submitted commit.

## What the article is

A measurement-methodology study of which performance measurands of a deployed multi-channel
edge camera monitor are identifiable from the evidence a deployment can produce: the false-alarm
rate is point-identified from the site's own alert stream; site coverage is not identified when no
site event occurs; ex-situ replay identifies benchmark coverage only, and a declared transfer band
gives a sharp identified set for site coverage. Every number in the article is produced by the
scripts below from the files in this repository.

## What is in this repository

| path | what |
|---|---|
| `scripts/theory_checks/` | **tim-v3.** The propositions' numerical checks (`p1_*`–`p7_*`, `ki_alpha1_two_cis.py`) and `make_theory_numbers.py`, which runs them and writes `theory_numbers.json` / `.tex` — every theory number the article prints |
| `scripts/make_sample_table.py`, `02_Manuscript/tables/sample_table.csv` | **tim-v3.** The in-situ sample table (segments by view, time of day and clock stratum) |
| `scripts/render_silhouette.py` | **tim-v3.** Code only: how in-situ alert frames were reduced to convex-hull masks. No frame, video or mask from the residence is included |
| `scripts/requirements*.txt` | pinned environments for the checks and the figures |
| `01_Measurement/generated_counts.json` | every counted quantity, as emitted by the counter |
| `01_Measurement/PREREGISTERED_*.md` + `.sha256` | all pre-registrations, byte-identical to the hashed files |
| `01_Measurement/runs/` | per-segment alert tables and per-run metadata including the operating point; **no images** |
| `01_Measurement/analysis/` | derived tables (cost axes, per-segment fall table, silent-mechanism registers, view assignment) |
| `01_Measurement/exsitu/` | ex-situ clip lists with their hashes, scoring scripts and scores |
| `01_Measurement/ops/samples`, `ops/lists` | the registered in-situ samples, their lists and hashes |
| `01_Measurement/scripts/` | the counter and the scripts it imports, including the registered sample draw |
| `ledger/` | the claim ledger and its auditor |
| `REDACTIONS.md` | every string replaced in this release, with hashes before and after |
| `SHA256SUMS.txt` | a hash for every file |

## What is not in this repository, and why

- **No video and no image from the residence — ever.** The in-situ corpus is continuous
  recording inside a private home. The step from pixels to the alert tables cannot be re-run by a
  reader; everything after it can.
- **No third-party corpora or annotations.** They are used under their own licences and linked,
  not mirrored (GMDCSA24 CC BY 4.0; FURG Fire CC0-1.0; OmniFall annotations CC BY-NC-SA 4.0).
- **No identifiers of the recording device, the camera or the home network** (see `REDACTIONS.md`).

## Reproducing every theory number (tim-v3)

```
python -m venv .venv
.venv/Scripts/python -m pip install -r scripts/requirements.txt      # numpy 1.26.4
.venv/Scripts/python scripts/theory_checks/make_theory_numbers.py
```

It reruns every check, stops on the first failure, and writes `scripts/theory_checks/theory_numbers.json`.
Compare its `macros` with the released file key by key; it also checks that the keys of the
earlier checkpoint (`theory_numbers.cpalpha1.json`) did not move. The measurement tree is found
at `01_Measurement/` (override with `AAP_MEAS`).

## Reproducing every counted quantity

`python 01_Measurement/scripts/count_everything.py --tex-out out/` rewrites
`01_Measurement/generated_counts.json`; compare it with the released one, ignoring
`_generated_at`. The OmniFall annotation files must be placed where `count_omnifall_annotations()`
in `count_everything.py` looks for them (one line to change on another system).

## Licences (confirmed by the author, 2026-09-14)

- Code (`*.py`): MIT — `LICENSE`.
- Everything else: CC BY 4.0 — `LICENSE-DATA`.
- Third-party material is covered by neither.

## Registered files and their hashes

Each was re-hashed inside this release at build time against its stored `.sha256`: 22 file(s), 0 mismatch(es).

| file | SHA256 |
|---|---|
| `01_Measurement/PREREGISTERED_E10B_AMENDMENT.md` | `ba97277117bfa240c43bb8b7128e9035259c0063017899da997a86215fca2243` |
| `01_Measurement/PREREGISTERED_E10_RUNCTL.md` | `d350b51daa883a50f25218d3a401ff60beed8eb31583ffaa9e8a2051c89bbe01` |
| `01_Measurement/PREREGISTERED_E12B.md` | `e1b3e2249c530f1f2fb81589a27077b739c094d28203bcfe89299ba2da8da0e3` |
| `01_Measurement/PREREGISTERED_E12C.md` | `1498fde5a0d37f5d0fa4432b2a0f89ce7907b954a3a538beb6ef1336c30cb063` |
| `01_Measurement/PREREGISTERED_E12_COST_AXIS.md` | `c36865afb79f42d58fd4ac68fe0058c073e48dd3b7287708cb76298529c03b90` |
| `01_Measurement/PREREGISTERED_E4_CLOCK_STRATUM.md` | `2371fef5b718f76f3702d682f4a07ccf8170c89784deca20e9d5214eeb958885` |
| `01_Measurement/PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.md` | `6fd7fdb372fe85b643ab208470815cffbefe9c7cbc5ae23d09030d0ea9d2da15` |
| `01_Measurement/PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md` | `60aaa61bea38cbc54388c250107942f4ac96dbbbdf1f00b2793d43748ae8c41a` |
| `01_Measurement/PREREGISTERED_E7B_AMENDMENT.md` | `6d9bda777f235bc0062bdc52f992ed8ca82f5302d69575e4ee1544bd73d495eb` |
| `01_Measurement/PREREGISTERED_E7C.md` | `2c7a5550474de37f85b9ea38f1c1f6b265f1c5531f819f937bc71a2be984d26e` |
| `01_Measurement/PREREGISTERED_E7D.md` | `4ca3353ed82e27ca04e889cda8c7c3fcc07dd758f9a6516b55aefaa1fdb6732d` |
| `01_Measurement/PREREGISTERED_E7_C1B_PILOT.md` | `78ff9ec16543da647803fa80d99b1126565d340ae63729a0be4ec30e1e854fdf` |
| `01_Measurement/PREREGISTERED_E8_D5_SAMPLE.md` | `ba2112c2fc92cc5d8340f3ca35aa20d56e80cf10d7e07ba56ec58908e0efe605` |
| `01_Measurement/PREREGISTERED_E9_CHANNEL_RECOVERY.md` | `3a9a750199c654ab1b7a31af91604d19111f05d5a1ee3cbca440dfeeac63def8` |
| `01_Measurement/PREREGISTERED_M3.md` | `dac03e1deef408a60707c068fb380a6cdc7afc61bfcd2c414fdc1187a1199d0a` |
| `01_Measurement/PREREGISTERED_M3_ERRATA.md` | `cdf4f2b0857c9558ba93bac446d49c79581cb2d5ba304907c4664ae667eeb76a` |
| `01_Measurement/PREREGISTERED_M5_WITHDRAWAL.md` | `51ab34ebd366a74f6b7ef1019ffbeb523fcbf66476bd2bfed9a4f4b01d2e5bfa` |
| `01_Measurement/exsitu/CLIPLIST_furg.csv` | `3c16a0d792b9e49bcabeb07dbe441c7c104b4b653c8b5033e8d3fb45a3f9efe5` |
| `01_Measurement/exsitu/CLIPLIST_gmdcsa24.csv` | `12f4c34fd78f10704bcbb3dded0d8fe09ac712836daab051f22f3ef9502699ab` |
| `01_Measurement/exsitu/virat/CLIPLIST_virat.csv` | `3ce28c669337bf9f04a508822b673e99d40a7ffd0f9a8714e6a2039b82e5105f` |
| `01_Measurement/ops/samples/sweep_sample_12h.csv` | `2a6a0fa034d6905d988208e71a56fe908d8996b1f137b4183de735530c9e2284` |
| `01_Measurement/ops/samples/verify_sample_4h.csv` | `acc8e39663d845ccb1c40e82e77f3b34c901617a50e51405ae700317ba4d02c9` |

## Reproduction check at build time

`count_everything.py` was run on a copy of this package, with the OmniFall annotation files in place: exit status 0, 1151 quantities compared with the released `generated_counts.json`, **0 differ**.

One caveat, stated rather than left to be discovered: 13 pre-registrations carry no lock stamp inside the file, so the counter reports their lock time from the file's modification time and labels it `(mtime)` (Supplementary Table of pre-registrations). A git clone resets modification times, so on a fresh clone those 13 labels will show the clone time. They are not measurements, and no other quantity depends on them.

## Reproduction check of the theory numbers (tim-v3)

See `C7_REPORT_alpha.md` in the author's package; summary appended at tagging time.
