# Asymmetric Evidence in Characterizing a Multi-Function Edge Camera Monitor — reproduction package

Repository: **https://github.com/lamquocdat01/aap-tim-release** · tag **`tim-v2`**.

Release **`tim-v2`**: the version submitted to *IEEE Transactions on Instrumentation and
Measurement*. Author: Dat Lam Quoc, FPT School of Business and Technology, FPT University,
Ho Chi Minh City, Vietnam (ORCID 0009-0004-5432-9343).

> **A GitHub URL is not a persistent identifier.** No DOI-backed archival copy of this package
> exists at the time of submission. The tag `tim-v2` identifies the submitted commit.

## What the article is

A measurement study of a deployed multi-channel camera monitor under *asymmetric evidence*:
false-alarm rates measured in situ on the deployment's own recordings, coverage measured ex situ
by replaying open benchmark video through the frozen pipeline, an operating-point allocation
under interval-valued coverage, and a catalogue of mechanisms the system's configuration asserts
but does not enforce.

## What is in this repository

Every artefact that `01_Measurement/scripts/count_everything.py` reads to emit every number
printed in the article and its supplement. The list was not written by hand: it is the set of
files the counter was observed to open (with every write disabled), plus the files its preflight
requires and the scripts that produced those artefacts.

| path | what |
|---|---|
| `01_Measurement/generated_counts.json` | every counted quantity the article prints, as emitted at submission |
| `01_Measurement/PREREGISTERED_*.md` + `.sha256` | all pre-registrations, byte-identical to the hashed files |
| `01_Measurement/runs/` | per-segment alert tables (timestamp, checker, confidence, frame index, track id) and per-run metadata including the operating point; **no images** |
| `01_Measurement/analysis/` | derived tables: cost axes, ablation cells, per-segment fall table, Layer-1 metrics, the two silent-mechanism registers |
| `01_Measurement/exsitu/` | ex-situ clip lists with their hashes, scoring scripts and scores |
| `01_Measurement/ops/samples`, `ops/lists` | the registered in-situ samples and their hashes |
| `01_Measurement/GT_protocol/GT_PROTOCOL.md` | the ground-truth protocol, including the pre-registration registry |
| `01_Measurement/scripts/` | the counter and the scripts it imports or whose outputs it reads |
| `ledger/` | the claim ledger and its auditor |
| `REDACTIONS.md` | every string replaced in this release, with hashes before and after |
| `SHA256SUMS.txt` | a hash for every file |

## What is not in this repository, and why

- **No video and no image from the residence — ever.** The in-situ corpus is continuous
  recording inside a private home; no consent exists that would make publishing it acceptable.
  This was a rule of the campaign from its start. Consequently the step from pixels to the alert
  tables cannot be re-run by a reader; everything after it can.
- **No third-party corpora or annotations.** They are used under their own licences and linked,
  not mirrored. The counter additionally reads six OmniFall annotation files
  (`simplexsigil2/omnifall`, `labels/*.csv`; CC BY-NC-SA 4.0).
- **No identifiers of the recording device, the camera or the home network.** They are replaced
  in the released copies (see `REDACTIONS.md`). No registered file was altered; the build aborts
  if a rule would touch one.

## Reproducing every number

Requirements: Python 3.11, standard library only.

1. Obtain the OmniFall annotation files and place them where the counter looks for them,
   `D:\AAP_exsitu_data\omnifall_ann\` — the path is set in `count_omnifall_annotations()` in
   `count_everything.py`; change that one line on another system. Without them the counter still
   runs and states which quantities it could not count.
2. Run:

   ```
   python 01_Measurement/scripts/count_everything.py --tex-out out/
   ```

   It rewrites `01_Measurement/generated_counts.json` and writes the LaTeX macros the article
   is typeset from into `out/`.
3. Compare the new `generated_counts.json` with the released one, ignoring `_generated_at`.

The result of that comparison at build time is recorded at the end of this file.

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
