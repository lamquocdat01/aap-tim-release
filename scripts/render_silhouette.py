#!/usr/bin/env python3
r"""F3 bottom row -- in-situ alert frames rendered as CONVEX HULLS only (rule P2b-2).

Author's rules: no home frame is ever published as an image (CP-alpha1 decision 2);
in-situ masks are drawn as the CONVEX HULL of each foreground component with a
thin bounding box, on white, with no outline detail, no background, no text
(P2b decision 2). Frames live in memory only; nothing raw is written.

Video: THS_DATASETS (default <datasets root>) \ AAP_home \ video -- 52 of the 175
segments (27-28/08), moved there from the Drive area on 22-10-2026.

Selection (deterministic). For each channel, take the replay alerts
(runs/m1/<seg>.csv, shipped defaults) of the segments present locally, in
descending confidence, and keep the first whose mask is non-empty (>= 0.3 % of
the frame) and passes the channel's admissibility test:
  Intrusion, Fall : no extra test;
  Helmet          : every kept component's bbox height < 25 % of the frame height
                    (person far from the camera; P2b decision 2). If none of the
                    first MAX_TRIES candidates passes, no in-situ helmet image is
                    produced and F3 falls back to ex-situ for that cell.
The helmet frame rejected on 22-10 (HOM_20260827_1800 / 10239) is excluded explicitly.

Mask: per-pixel median background over 31 frames in [t-90 s, t+90 s] excluding
|dt| < 5 s; |frame - bg| max over channels, blur, threshold 30; open 3x3,
close 9x9; components < 0.3 % of the frame dropped. Rendering: each component
-> filled convex hull (grey 40) + 1 px bbox (grey 120), scaled to 320 x 180.
"""
import csv
import hashlib
import io
import json
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "theory_checks"))
import _common as C  # noqa: E402

DATASETS = os.environ.get("THS_DATASETS", "datasets")
VIDEO = os.path.join(DATASETS, "AAP_home", "video")
OUT = os.path.join(C.TIM, "02_Manuscript", "figures", "_review")
W, H = 320, 180
CHECKERS = ["IntrusionChecker", "HelmetChecker", "FallChecker"]
REJECTED = {("HelmetChecker", "HOM_20260827_1800", 10239)}
MAX_TRIES = 80
HELMET_MAX_H = 0.25


def frame_at(cap, idx):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
    ok, f = cap.read()
    return f if ok else None


def components(path, idx, fps):
    """Foreground components at frame idx: list of (hull points, bbox) in
    full-resolution pixels, plus the frame size. No pixel data is returned."""
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    f0 = frame_at(cap, idx)
    if f0 is None:
        cap.release()
        return None, None
    span, excl = int(90 * fps), int(5 * fps)
    cand = [i for i in np.linspace(max(0, idx - span), min(n - 1, idx + span), 41).astype(int)
            if abs(i - idx) >= excl][:31]
    stack = [s for s in (frame_at(cap, i) for i in cand) if s is not None]
    cap.release()
    bg = np.median(np.stack(stack), axis=0).astype(np.uint8)
    d = cv2.GaussianBlur(cv2.absdiff(f0, bg).max(axis=2), (5, 5), 0)
    m = (d > 30).astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    shape = m.shape
    k, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    comps = []
    for i in range(1, k):
        if stats[i, cv2.CC_STAT_AREA] >= 0.003 * m.size:
            pts = cv2.findNonZero((lab == i).astype(np.uint8))
            hull = cv2.convexHull(pts)
            comps.append((hull, cv2.boundingRect(hull)))
    del f0, stack, bg, d, m, lab                  # no raw pixels survive
    return comps, shape


def render(comps, shape):
    sy, sx = H / shape[0], W / shape[1]
    img = np.full((H, W, 3), 255, np.uint8)
    for hull, (x, y, w, h) in comps:
        hp = np.round(hull.reshape(-1, 2) * [sx, sy]).astype(np.int32)
        cv2.fillPoly(img, [hp], (40, 40, 40))
        cv2.rectangle(img, (int(x * sx) - 2, int(y * sy) - 2),
                      (int((x + w) * sx) + 2, int((y + h) * sy) + 2), (120, 120, 120), 1)
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    local = {f[:-4] for f in os.listdir(VIDEO) if f.endswith(".mp4")}
    cands = {c: [] for c in CHECKERS}
    for s in sorted(local):
        p = os.path.join(C.RUNS_M1, s + ".csv")
        if not os.path.exists(p):
            continue
        fps = json.load(io.open(os.path.join(C.RUNS_M1, s + ".json"), encoding="utf-8"))["fps"]
        with io.open(p, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                if r["checker"] in cands:
                    cands[r["checker"]].append((float(r["confidence"]), s, int(r["frame_idx"]),
                                                float(r["t_alert"]), fps))
    log = {"rule": "convex hull + thin bbox per foreground component (P2b-2); see script docstring",
           "video_dir": "THS_DATASETS/AAP_home/video", "local_segments": len(local), "images": [],
           "tried": {}}
    for ck in CHECKERS:
        tried = 0
        for conf, s, idx, t, fps in sorted(cands[ck], reverse=True):
            if (ck, s, idx) in REJECTED:
                continue
            if tried >= MAX_TRIES:
                break
            tried += 1
            comps, shape = components(os.path.join(VIDEO, s + ".mp4"), idx, fps)
            if not comps:
                continue
            hmax = max(b[3] for _, b in comps) / shape[0]
            if ck == "HelmetChecker" and hmax >= HELMET_MAX_H:
                continue
            img = render(comps, shape)
            name = "f3_insitu_%s_hull.png" % ck.replace("Checker", "").lower()
            path = os.path.join(OUT, name)
            cv2.imwrite(path, img)
            sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
            area = float((img[..., 0] == 40).mean())
            log["images"].append({"checker": ck, "segment": s, "frame_idx": idx, "t_alert_s": t,
                                  "confidence": conf, "components": len(comps),
                                  "max_bbox_height_fraction": round(hmax, 3),
                                  "hull_area_fraction": round(area, 4), "png": "figures/_review/" + name,
                                  "sha256": sha, "status": "PENDING AUTHOR REVIEW -- do not embed"})
            print("%-17s %s frame %6d conf %.3f -> %s (%d comp, max bbox h %.0f %%, tried %d)" % (
                ck, s, idx, conf, name, len(comps), 100 * hmax, tried))
            break
        else:
            print("%-17s no admissible frame in %d tries" % (ck, tried))
        log["tried"][ck] = tried
        if not any(i["checker"] == ck for i in log["images"]):
            log.setdefault("none_found", []).append(ck)
            print("%-17s NONE admissible (tried %d) -> F3 uses ex-situ for this cell" % (ck, tried))
    io.open(os.path.join(OUT, "f3_insitu_log.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(log, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
