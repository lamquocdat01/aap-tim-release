#!/usr/bin/env python3
"""recall(L) for the fall channel, at every registered operating point.

WHAT THIS IS FOR
----------------
The paper needs a recall-versus-latency curve, and it needs it at more than one
theta, because the allocation argument is about a trade-off surface and a
surface needs two axes. `RECALL_L_gmdcsa24_native.json` (2026-09-02) already
swept L, but only at the deployed point theta = 0.45; the other four registered
points had been scored at the protocol's fixed W = 2.0 s and nowhere else.

THIS COSTS NO MACHINE TIME. The five prediction sets already exist on disk --
X4 wrote them -- and every alert carries its timestamp, so the whole surface is
a re-score of data already measured. Nothing here runs a detector, and nothing
here goes near the Jetson.

WHAT L MEANS, AND WHY IT IS NOT W
---------------------------------
GT_PROTOCOL section 3 fixes the matching window at W = 2.0 s on BOTH sides of a
ground-truth event, and that rule is not negotiable for any number the paper
reports as recall. L is a different question asked of the same data: if an
operator would still accept an alert that arrives up to L seconds after the
event ends, how much recall does the channel have? So L replaces the TRAILING
half of the window and the leading half stays at W:

    hit  <=>  gt_start - W  <=  t_alert  <=  gt_end + L

At L = W = 2.0 this is exactly the protocol rule, which is the check that the
sweep has not quietly redefined the measurement: `--verify` asserts that the
L = 2.0 column reproduces SCORE_X4_t*.json TP for TP. A sweep that disagrees
with the frozen score at its own fixed point is measuring something else.

The strict/extended pair is carried through unchanged from score_exsitu.py:
OmniFall separates `fall` (the descent) from `fallen` (lying there afterwards),
section 4.1 of our protocol describes something between the two, and reporting
only the more favourable of them would be choosing a definition after seeing
the result.
"""
import argparse
import collections
import csv
import glob
import json
import os
import sys

W_LEAD = 2.0            # section 3, fixed, not swept
MERGE_GAP = 30.0        # section 4.1, FallChecker
FALLEN_CAP = 3.0
FALL_ID, FALLEN_ID = 1, 2

L_GRID = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0, 30.0]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "D:/AAP_exsitu_data"
CLIPLIST = os.path.join(HERE, "CLIPLIST_gmdcsa24.csv")
LABELS = os.path.join(DATA, "omnifall_ann", "labels_GMDCSA24.csv")

# The five registered operating points of PREREGISTERED_M3, with the directory
# X4 wrote each one into. The theta values are the registration's, not a
# re-derivation: this file must not be where a grid point gets invented.
POINTS = [
    (0.300,  "preds_x4_t030",  "SCORE_X4_t030.json"),
    (0.375,  "preds_x4_t0375", "SCORE_X4_t0375.json"),
    (0.450,  "preds_x4_t045",  "SCORE_X4_t045.json"),
    (0.525,  "preds_x4_t0525", "SCORE_X4_t0525.json"),
    (0.600,  "preds_x4_t060",  "SCORE_X4_t060.json"),
]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def merge(events, gap):
    if not events:
        return []
    events = sorted(events)
    out = [list(events[0])]
    for s, e in events[1:]:
        if s - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def build_gt(segs, mode):
    segs = sorted(segs, key=lambda s: s[1])
    ev = []
    for i, (lab, s, e) in enumerate(segs):
        if lab != FALL_ID:
            continue
        end = e
        if mode == "extended":
            for lab2, s2, e2 in segs[i + 1:]:
                if lab2 == FALLEN_ID and abs(s2 - e) < 0.5:
                    end = min(e2, e + FALLEN_CAP)
                break
        ev.append((s, end))
    return merge(ev, MERGE_GAP)


def score_clip(gt, alerts, lat):
    """Section 3.2 greedy one-to-one, with the trailing window widened to lat."""
    matched = [False] * len(gt)
    tp = fp = repeat = 0
    for t in sorted(alerts):
        cands = [i for i, (s, e) in enumerate(gt)
                 if s - W_LEAD <= t <= e + lat]
        if not cands:
            fp += 1
            continue
        free = [i for i in cands if not matched[i]]
        if free:
            matched[free[0]] = True
            tp += 1
        else:
            repeat += 1
    return tp, fp, len(gt) - sum(matched), repeat


def load():
    segs = collections.defaultdict(list)
    with open(LABELS, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            segs[r["path"]].append((int(r["label"]), float(r["start"]),
                                    float(r["end"])))
    clips = list(csv.DictReader(open(CLIPLIST, encoding="utf-8")))
    return segs, clips


def alerts_for(pred_dir, clip):
    flat = clip["file_relpath"].replace("/", "_").replace(" ", "_")
    p = os.path.join(DATA, pred_dir, flat.replace(".mp4", "") + ".csv")
    if not os.path.exists(p):
        return None
    out = []
    with open(p, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["checker"] == "FallChecker":
                out.append(float(r["t_alert"]))
    return out


def sweep():
    segs, clips = load()
    res = {}
    for theta, pred_dir, _score in POINTS:
        cell = {}
        for mode in ("strict", "extended"):
            for lat in L_GRID:
                TP = FP = FN = RPT = GT = 0
                n_clip = n_missing = 0
                for c in clips:
                    a = alerts_for(pred_dir, c)
                    if a is None:
                        n_missing += 1
                        continue
                    n_clip += 1
                    gt = build_gt(segs.get(c["clip_id"], []), mode)
                    tp, fp, fn, rp = score_clip(gt, a, lat)
                    TP += tp
                    FP += fp
                    FN += fn
                    RPT += rp
                    GT += len(gt)
                lo, hi = wilson(TP, GT)
                cell["%s_L%g" % (mode, lat)] = {
                    "L": lat, "mode": mode, "clips_scored": n_clip,
                    "clips_missing_prediction": n_missing,
                    "gt": GT, "tp": TP, "fp": FP, "fn": FN, "repeat": RPT,
                    "recall": (TP / GT) if GT else float("nan"),
                    "wilson95": [lo, hi],
                }
        res["t%g" % theta] = {"theta": theta, "pred_dir": pred_dir,
                              "cells": cell}
    return res


def verify(res):
    """The L = W column must reproduce the frozen scores exactly."""
    bad = 0
    for theta, pred_dir, score_name in POINTS:
        p = os.path.join(HERE, score_name)
        if not os.path.exists(p):
            print("  MISSING %s -- cannot verify theta=%g" % (score_name, theta))
            bad += 1
            continue
        frozen = json.load(open(p, encoding="utf-8"))["results"]
        cells = res["t%g" % theta]["cells"]
        for mode in ("strict", "extended"):
            want = frozen[mode]
            got = cells["%s_L%g" % (mode, W_LEAD)]
            same = (want["tp"] == got["tp"] and want["fp"] == got["fp"]
                    and want["gt_events"] == got["gt"])
            print("  %s theta=%-5g %-9s frozen TP=%-3d FP=%-3d GT=%-3d | "
                  "sweep TP=%-3d FP=%-3d GT=%-3d  %s"
                  % ("ok " if same else "BAD", theta, mode, want["tp"],
                     want["fp"], want["gt_events"], got["tp"], got["fp"],
                     got["gt"], "" if same else "<-- DISAGREES"))
            if not same:
                bad += 1
    return bad


def table(res):
    print()
    print("recall(L), fall channel, GMDCSA24, Wilson 95%")
    for mode in ("strict", "extended"):
        print()
        print("  %s GT definition" % mode)
        print("    theta  " + "".join("%9s" % ("L=%g" % l) for l in L_GRID))
        for theta, _d, _s in POINTS:
            cells = res["t%g" % theta]["cells"]
            row = "".join("%9.3f" % cells["%s_L%g" % (mode, l)]["recall"]
                          for l in L_GRID)
            print("    %-6.3f%s" % (theta, row))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "RECALL_L_X4.json"))
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()

    if not os.path.isdir(DATA):
        print("FAIL: the ex-situ prediction store %s is not on this disk."
              % DATA)
        return 2

    res = sweep()
    print("verifying the L = W = %g column against the frozen scores:" % W_LEAD)
    bad = verify(res)
    table(res)

    if bad:
        print("\nFAIL: %d cell(s) disagree with the frozen score. The sweep is "
              "measuring something the protocol did not fix; nothing is "
              "written." % bad)
        return 1
    print("\nthe L = %g column reproduces all %d frozen scores exactly"
          % (W_LEAD, 2 * len(POINTS)))

    if a.verify_only:
        return 0
    meta = {
        "checker": "FallChecker",
        "corpus": "GMDCSA24",
        "W_leading_s": W_LEAD,
        "merge_gap_s": MERGE_GAP,
        "L_grid_s": L_GRID,
        "protocol": "GT_PROTOCOL sections 3, 4.1, 8; L sweeps the TRAILING "
                    "half of the window only",
        "verified_against": [s for _t, _d, s in POINTS],
        "points": res,
    }
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1)
    print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
