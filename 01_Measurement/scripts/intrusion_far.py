#!/usr/bin/env python3
"""FAR of the intrusion channel = alert rate x FP-fraction, with its interval.

    python intrusion_far.py            # prints; writes analysis/INTRUSION_FAR.json

REGISTERED BEFORE THE DRAW (scripts/make_intrusion_pack.py, GT_PROTOCOL 5.7):

  population   production intrusion alerts after the deletion boundary
               2026-09-02T04:50:36Z, drawn seed 20260904, n = 100,
               unstratified, then shuffled so presentation order carries no
               time information; images blinded to 001..100.jpg with the
               mapping withheld from the labeller.
  question     exactly one -- is a person visible in the frame? YES/NO/UNSURE.
  FP rule      technical FP = NO. UNSURE is DROPPED from the denominator and
               its count reported. Neither is decided here.
  scope        the FP-fraction belongs to the PRODUCTION column. Carrying it to
               the offline replay column is a DECLARED TRANSFER ASSUMPTION --
               same detector, same threshold, different deduplication.

TWO THINGS THIS SCRIPT REFUSES TO DO

  1. It does not report the joint bootstrap as the interval when the FP count
     is zero. Every resample of an all-YES sample yields fraction 0, so the
     product collapses to [0, 0] -- an artefact of resampling a boundary, and
     it would be the most confident wrong number in the paper. The interval of
     record is Wilson on the fraction (defined at zero) times the block
     bootstrap on the rate. The degenerate bootstrap is computed and printed
     anyway, labelled, because the reader is entitled to see that it degenerates.

  2. It does not invent the rate for the pack's own 19-hour window. The
     population count recorded by the generator (2,640) could not be reproduced
     from the snapshot volume this script can read: the same predicate now
     yields 3,989, and dropping the calendar-day restriction yields 4,232. Until
     that is reconciled the pack's own window has no trustworthy denominator, so
     the fraction is applied to the CORPUS-WIDE deployed rate, which is a gated
     counted quantity, and the window transfer is declared. See
     KNOWN_ISSUES.md HARNESS-29.
"""
from __future__ import annotations

import csv
import collections
import datetime as dt
import hashlib
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.dirname(HERE)
ANALYSIS = os.path.join(MEAS, "analysis")

PACK = os.path.join(MEAS, "intrusion_label_pack", "labels.csv")
INDEX = os.path.join(ANALYSIS, "live_alert_index_20260902.csv")
MANIFEST = os.path.join(ANALYSIS, "tier0", "manifest_rows_closed.csv")
COUNTS = os.path.join(MEAS, "generated_counts.json")
SEALED = "dea87abb233f3362da467836e6f3fe651cd38a9ddf5c207b0594217fb5ecbb1b"
Z = 1.959963985
SEED = 20260910
B = 20000


def wilson(k, n, z=Z):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(v, q):
    v = sorted(v)
    return v[max(0, min(len(v) - 1, int(round(q * (len(v) - 1)))))]


def main():
    got = hashlib.sha256(open(PACK, "rb").read()).hexdigest()
    if got != SEALED:
        sys.exit("label pack is not the sealed file.\n  sealed %s\n  found  %s\n"
                 "Seal: GT_protocol/LABEL_PACK_SEAL_20260910.md." % (SEALED, got))

    rows = list(csv.DictReader(open(PACK, encoding="utf-8-sig")))
    verdicts = [(r["verdict"] or "").strip().upper() for r in rows]
    bad = sorted({v for v in verdicts if v not in ("YES", "NO", "UNSURE")})
    if bad:
        sys.exit("off-vocabulary verdict(s) %s; the README admits YES/NO/UNSURE "
                 "and nothing else. Not interpreted here." % bad)
    n_yes, n_no = verdicts.count("YES"), verdicts.count("NO")
    n_unsure = verdicts.count("UNSURE")
    n_den = n_yes + n_no
    if not n_den:
        sys.exit("every cell is UNSURE: no denominator.")
    fp = n_no / n_den
    fp_lo, fp_hi = wilson(n_no, n_den)
    rule3 = (3.0 / n_den) if n_no == 0 else None

    # ---- the deployed rate the fraction multiplies -------------------------
    C = json.load(open(COUNTS, encoding="utf-8"))
    alerts = int(C["far_deployed_intrusionchecker_alerts"])
    hours = float(C["insitu_hours"])
    rate = alerts / hours

    # Per-segment counts, for the SHAPE of the interval only. Reconstructed by
    # placing each indexed alert in the segment window that contains it; that
    # reconstruction finds 11,255 where the gated count is 11,257, a two-alert
    # disagreement at segment boundaries. The point estimate therefore uses the
    # GATED count and only the bootstrap uses the reconstruction -- a
    # reconstruction good enough to describe dispersion is not automatically
    # good enough to replace a counted total.
    segs = []
    for r in csv.DictReader(open(MANIFEST, encoding="utf-8-sig")):
        m = re.match(r"HOM_(\d{8})_(\d{4})", r["file"])
        if not m:
            continue
        st = dt.datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
        dur = float(r["duration_s"])
        segs.append([r["file"], st, st + dt.timedelta(seconds=dur), dur / 3600.0])
    segs.sort(key=lambda s: s[1])
    per = collections.Counter()
    for x in csv.DictReader(open(INDEX, encoding="utf-8-sig")):
        if (x.get("event_type") or "").strip() != "intrusion":
            continue
        t = dt.datetime.fromisoformat(x["ts_site"]).replace(tzinfo=None)
        for f, a, b, h in segs:
            if a <= t < b:
                per[f] += 1
                break
    recon = sum(per.values())
    pairs = [(per[f], h) for f, _, _, h in segs]

    rng = random.Random(SEED)
    n_s = len(pairs)
    b_rate, b_far, b_frac = [], [], []
    for _ in range(B):
        idx = [rng.randrange(n_s) for _ in range(n_s)]
        k = sum(pairs[i][0] for i in idx)
        hh = sum(pairs[i][1] for i in idx)
        r_star = k / hh if hh else 0.0
        f_star = sum(1 for _ in range(n_den)
                     if verdicts[rng.randrange(len(verdicts))] == "NO") / n_den
        b_rate.append(r_star)
        b_frac.append(f_star)
        b_far.append(r_star * f_star)
    r_lo, r_hi = pct(b_rate, 0.025), pct(b_rate, 0.975)

    out = {
        "sealed_sha256": SEALED,
        "provenance": "author, pass 1, direct human labelling; no machine-assisted proposal step",
        "n": len(rows), "yes": n_yes, "no": n_no, "unsure": n_unsure,
        "denominator": n_den,
        "fp_fraction": round(fp, 6),
        "fp_fraction_wilson95": [round(fp_lo, 6), round(fp_hi, 6)],
        "fp_fraction_rule_of_three_upper": round(rule3, 6) if rule3 else None,
        "deployed_alerts_counted": alerts,
        "corpus_hours": hours,
        "deployed_rate_per_h": round(rate, 4),
        "deployed_rate_ci95_block_bootstrap": [round(r_lo, 4), round(r_hi, 4)],
        "deployed_rate_reconstructed_alerts": recon,
        "reconstruction_gap_alerts": alerts - recon,
        "far_point_per_h": round(rate * fp, 6),
        "far_upper_per_h": round(r_hi * fp_hi, 4),
        "far_upper_rule_of_three_per_h": round(r_hi * rule3, 4) if rule3 else None,
        "far_joint_bootstrap_ci95_DEGENERATE": [round(pct(b_far, 0.025), 6),
                                                round(pct(b_far, 0.975), 6)],
        "bootstrap_replicates": B, "bootstrap_seed": SEED,
        "window_transfer_assumption": (
            "the pack was drawn from production alerts of 2026-09-02 after "
            "04:50:36Z; the rate it multiplies is the corpus-wide deployed rate "
            "over %d segments and %.4f h. Applying the fraction across that "
            "wider window is a declared assumption about the production stream, "
            "not a measurement." % (len(segs), hours)),
        "computed_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    os.makedirs(ANALYSIS, exist_ok=True)
    p = os.path.join(ANALYSIS, "INTRUSION_FAR.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=2)

    print("pack          : sealed hash matches (%s...)" % SEALED[:16])
    print("verdicts      : YES %d   NO %d   UNSURE %d   denominator %d"
          % (n_yes, n_no, n_unsure, n_den))
    print("FP-fraction   : %.4f    Wilson 95%% [%.4f, %.4f]" % (fp, fp_lo, fp_hi))
    if rule3:
        print("                rule of three upper %.4f (zero NO in %d)" % (rule3, n_den))
    print("deployed rate : %.4f /h  (%d counted alerts / %.4f h)" % (rate, alerts, hours))
    print("                block bootstrap 95%% [%.4f, %.4f]  (reconstruction "
          "placed %d of %d)" % (r_lo, r_hi, recon, alerts))
    print()
    print("FAR intrusion : %.4f /h" % out["far_point_per_h"])
    print("                upper bound %.4f /h   (rate_hi x Wilson_hi)" % out["far_upper_per_h"])
    if rule3:
        print("                upper bound %.4f /h   (rate_hi x rule-of-three)"
              % out["far_upper_rule_of_three_per_h"])
    print("                joint bootstrap [%.4f, %.4f]  <-- DEGENERATE, not reported"
          % tuple(out["far_joint_bootstrap_ci95_DEGENERATE"]))
    print("wrote %s" % os.path.relpath(p, MEAS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
