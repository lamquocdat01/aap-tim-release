#!/usr/bin/env python3
"""Where each point of the FallChecker cost axis actually comes from.

WHY
---
`theta_vs_lambda.py` prices the whole allocation on three numbers -- the alert
rate of FallChecker at theta = 0.30, 0.45 and 0.60 on the eight-segment
verification sample. Those three numbers are the x-axis of the only
non-degenerate front the paper has, so every allocation statement rests on
them, and until now nothing recorded how they are distributed WITHIN the
sample.

They are not distributed. At the deployed point theta = 0.45, all sixteen
alerts come from ONE segment, and that segment is the one segment of the eight
that carries the HARNESS-5 recorder defect. A rate computed as
alerts / total-hours reports that as 4.0086 per hour across 3.9914 hours, which
is arithmetically correct and, as an estimate of a rate, badly misleading: the
seven other segments contributed 3.50 hours and nothing at all.

This script reports the per-segment breakdown, a segment-level (block)
bootstrap interval that respects the clustering, and the Poisson interval that
does not -- side by side, because the gap between them IS the finding.

Nothing here changes a measurement. It reads the V-pass outputs already on
disk and the closed manifest, and writes a JSON summary.

NO MACHINE TIME. NOTHING RUNS ON THE DEVICE.
"""
import argparse
import collections
import csv
import glob
import io
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.dirname(HERE)
VER = os.path.join(MEAS, "runs", "verification")
MANIFEST = os.path.join(MEAS, "analysis", "tier0", "manifest_rows_closed.csv")
OUT = os.path.join(MEAS, "analysis", "FALL_FRONT_PROVENANCE.json")

# The three passes that are the front. v4/v5 sweep the detector confidence,
# not the decision threshold, so they are not points of this front.
POINTS = [("v1_loose", 0.30), ("v2_frozen", 0.45), ("v3_tight", 0.60)]
CHECKER = "FallChecker"
SEED = 20260911
REPLICATES = 20000


def substituted_segments():
    """Segments rescored on the substituted clock (HARNESS-5)."""
    out = set()
    if not os.path.exists(MANIFEST):
        return out
    with io.open(MANIFEST, encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            blob = " ".join(str(v) for v in r.values())
            if "HARNESS-5" in blob:
                key = list(r.values())[0]
                out.add(os.path.splitext(os.path.basename(key))[0])
    return out


def pass_rows(d):
    """{segment: (hours, fall_alerts)} for one verification pass."""
    out = {}
    for j in sorted(glob.glob(os.path.join(VER, d, "*.json"))):
        name = os.path.basename(j)[:-5]
        if name == "pass_params":
            continue
        meta = json.load(io.open(j, encoding="utf-8"))
        n = 0
        csvp = os.path.join(VER, d, name + ".csv")
        if os.path.exists(csvp):
            with io.open(csvp, encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    if r.get("checker") == CHECKER:
                        n += 1
        out[name] = (meta.get("video_seconds", 0.0) / 3600.0, n)
    return out


def poisson_ci(k, hours, z=1.96):
    """The interval a homogeneous-Poisson reading of the pass would give.

    Printed to be argued with, not to be used: it assumes the events are
    exchangeable across the observation window, which is exactly what the
    per-segment table shows they are not.
    """
    if hours <= 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else 0.5 * chi2_inv(0.025, 2 * k) / hours
    hi = 0.5 * chi2_inv(0.975, 2 * (k + 1)) / hours
    return (lo, hi)


def chi2_inv(p, df):
    """Wilson-Hilferty, adequate for an interval printed as a foil."""
    if df <= 0:
        return 0.0
    z = norm_inv(p)
    return df * (1.0 - 2.0 / (9.0 * df) + z * math.sqrt(2.0 / (9.0 * df))) ** 3


def norm_inv(p):
    """Acklam-style rational approximation; standard library only."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def block_bootstrap(rows, reps=REPLICATES, seed=SEED):
    """Resample SEGMENTS with replacement. The segment is the block because
    the segment is the unit the sample was drawn in, and the alerts inside one
    are plainly not independent of each other."""
    items = list(rows.values())
    if not items:
        return (float("nan"), float("nan"), float("nan"))
    rnd = random.Random(seed)
    n = len(items)
    rates = []
    for _ in range(reps):
        pick = [items[rnd.randrange(n)] for _ in range(n)]
        H = sum(h for h, _k in pick)
        K = sum(k for _h, k in pick)
        if H > 0:
            rates.append(K / H)
    rates.sort()
    if not rates:
        return (float("nan"), float("nan"), float("nan"))
    lo = rates[int(0.025 * len(rates))]
    hi = rates[min(len(rates) - 1, int(0.975 * len(rates)))]
    zero = sum(1 for r in rates if r == 0.0) / float(len(rates))
    return (lo, hi, zero)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    if not os.path.isdir(VER):
        print("FAIL: %s is not on this disk" % VER)
        return 2

    subst = substituted_segments()
    print("segments on the substituted clock (HARNESS-5), corpus-wide: %d"
          % len(subst))
    print()

    summary = {"checker": CHECKER, "seed": SEED, "replicates": REPLICATES,
               "substituted_corpus_n": len(subst), "points": {}}

    for d, theta in POINTS:
        rows = pass_rows(d)
        H = sum(h for h, _k in rows.values())
        K = sum(k for _h, k in rows.values())
        rate = (K / H) if H else float("nan")
        carriers = {s: (h, k) for s, (h, k) in rows.items() if k}
        sub_k = sum(k for s, (h, k) in rows.items() if s in subst)
        sub_h = sum(h for s, (h, k) in rows.items() if s in subst)
        plo, phi = poisson_ci(K, H)
        blo, bhi, pzero = block_bootstrap(rows)

        print("theta = %.2f  (%s)" % (theta, d))
        print("  %d alert(s) in %.4f h over %d segment(s) -> %.4f /h"
              % (K, H, len(rows), rate))
        for s in sorted(carriers, key=lambda x: -carriers[x][1]):
            h, k = carriers[s]
            tag = "  <-- SUBSTITUTED CLOCK (HARNESS-5)" if s in subst else ""
            print("      %-24s %3d alert(s) in %.4f h   %5.1f%% of the pass%s"
                  % (s, k, h, 100.0 * k / K if K else 0.0, tag))
        if not carriers:
            print("      no segment produced an alert")
        print("      segments carrying every alert: %d of %d"
              % (len(carriers), len(rows)))
        print("      from the substituted stratum: %d of %d alert(s) "
              "(%.1f%%), on %.4f of %.4f h (%.1f%% of the time)"
              % (sub_k, K, (100.0 * sub_k / K) if K else 0.0, sub_h, H,
                 100.0 * sub_h / H if H else 0.0))
        print("      Poisson 95%% (assumes exchangeable events): "
              "[%.4f, %.4f]" % (plo, phi))
        print("      segment block bootstrap 95%%:                "
              "[%.4f, %.4f]   %.1f%% of replicates give exactly 0"
              % (blo, bhi, 100.0 * pzero))
        print()

        summary["points"]["t%g" % theta] = {
            "theta": theta, "pass": d, "hours": H, "alerts": K, "rate_per_h": rate,
            "segments": len(rows),
            "segments_carrying_alerts": len(carriers),
            "per_segment": {s: {"hours": h, "alerts": k,
                                "substituted_clock": s in subst}
                            for s, (h, k) in sorted(rows.items())},
            "substituted_alerts": sub_k, "substituted_hours": sub_h,
            "poisson_ci95": [plo, phi],
            "block_bootstrap_ci95": [blo, bhi],
            "bootstrap_fraction_exactly_zero": pzero,
        }

    with io.open(a.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
