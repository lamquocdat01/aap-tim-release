#!/usr/bin/env python3
"""Score an ex-situ recall pass. GT_PROTOCOL.md sections 3, 4.1 and 8.

The matching rule is section 3 unchanged and not negotiable: hit-within-window
W = 2.0 s, greedy one-to-one in time, repeat alerts counted separately, TP <= GT
asserted. Nothing here is relaxed because the video came from somewhere else.

ONE MAPPING DECISION HAS TO BE MADE, AND IT IS MADE IN THE OPEN.
OmniFall's taxonomy separates `fall` (the transient descent) from `fallen` (the
static state afterwards). Section 4.1 defines our event as starting when the
subject begins descending involuntarily and ending when they regain an upright
posture *or have been stationary on the ground for 3 s, whichever is first*.
Those two definitions do not coincide, and no choice between them is neutral, so
both are computed and both are reported:

  strict    GT event = the `fall` segment exactly as OmniFall annotates it.
  extended  GT event = the `fall` segment, extended through an immediately
            adjacent `fallen` segment, capped at +3.0 s, which is what 4.1
            actually describes.

Reporting only the more favourable of the two would be choosing a definition
after seeing the result. The gap between them is a property of the taxonomy
mismatch and belongs in the table.
"""
import argparse, csv, collections, json, os, sys

W = 2.0                 # section 3, fixed
MERGE_GAP = 30.0        # section 4.1, FallChecker = max(operational 10, cooldown 30)
FALLEN_CAP = 3.0        # section 4.1 "stationary on the ground for 3 s"

FALL_ID, FALLEN_ID = 1, 2


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def merge(events, gap):
    """Section 4.1 merge gap. Two occurrences closer than `gap` are one event."""
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
    """segs: list of (label_id, start, end) for one clip, in time order."""
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


def score_clip(gt, alerts):
    """Section 3.2, greedy one-to-one in time."""
    matched = [False] * len(gt)
    tp = fp = repeat = 0
    for t in sorted(alerts):
        cands = [i for i, (s, e) in enumerate(gt) if s - W <= t <= e + W]
        if not cands:
            fp += 1
            continue
        free = [i for i in cands if not matched[i]]
        if free:
            best = min(free, key=lambda i: abs(t - gt[i][0]))
            matched[best] = True
            tp += 1
        else:
            repeat += 1
    fn = len(gt) - sum(matched)
    assert tp <= len(gt), "P2 violated: TP > GT"
    assert tp + fn == len(gt), "tp + fn != gt_events"
    return tp, fp, fn, repeat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred-dir", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--cliplist", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # OmniFall annotation, unmodified (section 8.1)
    segs = collections.defaultdict(list)
    with open(a.labels, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            segs[r["path"]].append((int(r["label"]), float(r["start"]), float(r["end"])))

    clips = list(csv.DictReader(open(a.cliplist, encoding="utf-8")))

    results = {}
    for mode in ("strict", "extended"):
        TP = FP = FN = RPT = GT = 0
        n_clip = n_missing = 0
        per_clip = []
        for c in clips:
            cid = c["clip_id"]
            flat = c["file_relpath"].replace("/", "_").replace(" ", "_")
            pred = os.path.join(a.pred_dir, flat.replace(".mp4", "") + ".csv")
            if not os.path.exists(pred):
                n_missing += 1
                continue
            n_clip += 1
            alerts = []
            with open(pred, encoding="utf-8") as fh:
                for r in csv.DictReader(fh):
                    if r["checker"] == "FallChecker":
                        alerts.append(float(r["t_alert"]))
            gt = build_gt(segs.get(cid, []), mode)
            tp, fp, fn, rp = score_clip(gt, alerts)
            TP += tp; FP += fp; FN += fn; RPT += rp; GT += len(gt)
            per_clip.append({"clip_id": cid, "gt": len(gt), "tp": tp,
                             "fp": fp, "fn": fn, "repeat": rp})
        rec = TP / GT if GT else float("nan")
        lo, hi = wilson(TP, GT)
        results[mode] = {"clips_scored": n_clip, "clips_missing_prediction": n_missing,
                         "gt_events": GT, "tp": TP, "fp": FP, "fn": FN,
                         "repeat_alerts": RPT, "recall": rec,
                         "recall_wilson95": [lo, hi], "per_clip": per_clip}

    meta = {"tag": a.tag, "pred_dir": a.pred_dir, "W": W,
            "merge_gap_s": MERGE_GAP, "checker": "FallChecker",
            "annotation": os.path.basename(a.labels),
            "protocol": "GT_PROTOCOL v1.3 sections 3, 4.1, 8",
            "results": results}
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    print("=== %s ===" % a.tag)
    for mode in ("strict", "extended"):
        r = results[mode]
        print("  %-9s clips %3d (missing %d)  GT %3d  TP %3d  FP %4d  FN %3d  repeat %3d"
              % (mode, r["clips_scored"], r["clips_missing_prediction"],
                 r["gt_events"], r["tp"], r["fp"], r["fn"], r["repeat_alerts"]))
        print("            recall %.4f  Wilson95 [%.4f, %.4f]"
              % (r["recall"], r["recall_wilson95"][0], r["recall_wilson95"][1]))


if __name__ == "__main__":
    main()
