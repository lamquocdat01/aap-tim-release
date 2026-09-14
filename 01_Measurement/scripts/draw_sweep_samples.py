#!/usr/bin/env python3
"""
Draw the registered sweep (24 segments) and verification (8 segments) samples.

    python3 draw_sweep_samples.py --manifest manifest_rows_closed.csv \\
        --m1-dir <device-root>/out/m1 \\
        --fov analysis/fov_segments.csv --out-dir analysis

WHY THIS IS A SCRIPT AND NOT A ONE-OFF
    PREREGISTERED_M3 B2 registers the design -- 24 + 8 disjoint, stratified,
    seeded -- before the numbers exist. A registration only means something if
    the draw it describes can be reproduced from the manifest alone by someone
    who does not have our shell history. So the rule lives here, the seeds are
    literals, and the output carries its own SHA256.

THE STRATA, and where each one comes from

    view          A / B, from analysis/fov_segments.csv (phase-correlation
                  against the first frame of the corpus). Segments with no FOV
                  row form their own stratum U rather than being guessed into
                  A or B; how many there are is printed, because a large U
                  would mean the stratification is mostly fictional.

    daynight      from the segment's own timestamp in its filename. 06:00-17:59
                  is day. This is the deployment's local clock, not sunrise.

    occupancy     ai_frames == 0 against ai_frames > 0, read from the M1 run
                  metadata. Registered in Checkpoint 2a A2, and the reason is
                  worth restating: this is NOT ground truth about whether
                  anyone was home. A stratification variable only has to divide
                  the corpus reproducibly; it does not have to mean what its
                  name suggests. "The motion gate never opened in this segment"
                  is measured, objective and already in the metadata, whereas
                  an occupancy diary reconstructed from memory is none of those.

ALLOCATION
    Every non-empty cell gets 2 segments if it has 2; the remainder is handed
    out proportionally to cell hours, largest remainder first. The verification
    draw uses the same rule with a different seed over the segments the sweep
    draw did not take, so the two are disjoint by construction rather than by
    a later check.

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
import os
import random
import sys

SEED_SWEEP = 20260902
SEED_VERIFY = 20260903
N_SWEEP = 24
N_VERIFY = 8
MIN_PER_CELL = 2
DAY_START, DAY_END = 6, 18          # [06:00, 18:00) is "day"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stem(name):
    return name[:-4] if name.endswith(".mp4") else name


def seg_time(s):
    """HOM_20260831_0530 -> datetime. Returns None if the name does not parse."""
    parts = s.split("_")
    if len(parts) < 3:
        return None
    try:
        return dt.datetime.strptime(parts[1] + parts[2][:4], "%Y%m%d%H%M")
    except ValueError:
        return None


def load_manifest(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            f = r.get("file") or r.get("filename") or ""
            if not f:
                continue
            try:
                dur = float(r.get("duration_s") or 0)
            except ValueError:
                dur = 0.0
            rows.append({"seg": stem(f), "dur_s": dur})
    return rows


def load_views(path):
    views = {}
    if path and os.path.exists(path):
        with open(path, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                views[stem(r["file"])] = (r.get("view") or "U").strip() or "U"
    return views


def load_ai_frames(m1_dir):
    """ai_frames per segment, from the M1 run metadata the pipeline wrote."""
    out = {}
    for p in sorted(glob.glob(os.path.join(m1_dir, "*.json"))):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            continue
        vid = d.get("video_id") or os.path.basename(p)
        diag = d.get("diagnostics") or {}
        if "ai_frames" in diag:
            out[stem(vid)] = int(diag["ai_frames"])
    return out


def cell_of(seg, views, ai):
    t = seg_time(seg)
    dn = "unk"
    if t is not None:
        dn = "day" if DAY_START <= t.hour < DAY_END else "night"
    occ = "nomotion" if ai.get(seg, 1) == 0 else "motion"
    return "%s|%s|%s" % (views.get(seg, "U"), dn, occ)


def allocate(cells, n_total):
    """MIN_PER_CELL first, then largest-remainder proportional to cell hours."""
    quota = {}
    left = n_total
    for c, segs in cells.items():
        take = min(MIN_PER_CELL, len(segs))
        quota[c] = take
        left -= take
    if left < 0:
        # More cells than the sample can cover at 2 each. Drop from the cells
        # with the fewest hours first: an under-covered thin cell is better
        # than a sample that silently exceeds its registered size.
        order = sorted(cells, key=lambda c: sum(s["dur_s"] for s in cells[c]))
        for c in order:
            while left < 0 and quota[c] > 0:
                quota[c] -= 1
                left += 1
    if left > 0:
        hours = {c: sum(s["dur_s"] for s in cells[c]) for c in cells}
        tot = sum(hours.values()) or 1.0
        raw = {c: left * hours[c] / tot for c in cells}
        base = {c: int(raw[c]) for c in cells}
        for c in cells:
            room = len(cells[c]) - quota[c]
            base[c] = min(base[c], max(0, room))
        assigned = sum(base.values())
        rem = sorted(cells, key=lambda c: (-(raw[c] - int(raw[c])), c))
        i = 0
        while assigned < left and i < len(rem) * 4:
            c = rem[i % len(rem)]
            if len(cells[c]) - quota[c] - base[c] > 0:
                base[c] += 1
                assigned += 1
            i += 1
        for c in cells:
            quota[c] += base[c]
    return quota


def draw(pool, n_total, seed):
    cells = {}
    for s in pool:
        cells.setdefault(s["cell"], []).append(s)
    quota = allocate(cells, n_total)
    rng = random.Random(seed)
    picked = []
    for c in sorted(cells):
        segs = sorted(cells[c], key=lambda s: s["seg"])
        k = min(quota.get(c, 0), len(segs))
        if k:
            picked.extend(rng.sample(segs, k))
    picked.sort(key=lambda s: s["seg"])
    return picked, quota, cells


def write_sample(path, rows, seed, n_target, cells, quota):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["seg", "duration_s", "view", "daynight", "occupancy",
                    "cell", "ai_frames"])
        for r in rows:
            v, dn, occ = r["cell"].split("|")
            w.writerow([r["seg"], "%.3f" % r["dur_s"], v, dn, occ, r["cell"],
                        r.get("ai_frames", "")])
    meta = {
        "seed": seed,
        "n_target": n_target,
        "n_drawn": len(rows),
        "hours": round(sum(r["dur_s"] for r in rows) / 3600.0, 4),
        "rule": ("min %d per non-empty cell, remainder proportional to cell "
                 "hours, largest remainder first; random.Random(seed).sample "
                 "over segments sorted by name" % MIN_PER_CELL),
        "strata": "view x daynight x occupancy(ai_frames==0)",
        "cells": {c: {"available": len(cells[c]), "quota": quota.get(c, 0)}
                  for c in sorted(cells)},
        "drawn": iso_now(),
        # On the record at the moment of drawing, because the obvious question
        # about a sample drawn after M1+ finished is "you saw the numbers
        # first". PREREGISTERED_M3_ERRATA.md E2 carries the same sentence.
        "provenance": (
            "Drawn by scripts/draw_sweep_samples.py from seeds registered "
            "before any of this existed (20260902 sweep, 20260903 verification). "
            "The only inputs are the manifest and the three registered "
            "stratification variables -- view, day/night, and ai_frames == 0. "
            "The false-alarm rate is NOT an input, is not read by this script, "
            "and no segment is chosen or rejected by hand. The draw is "
            "reproducible from the manifest and the run metadata alone, which "
            "is the property that makes the timing irrelevant."),
    }
    with open(path.replace(".csv", ".meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    sha = sha256_file(path)
    with open(path + ".sha256", "w", encoding="utf-8") as fh:
        fh.write("%s  %s\n" % (sha, os.path.basename(path)))
    return sha, meta


def iso_now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).isoformat(
        timespec="seconds")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--m1-dir", required=True)
    ap.add_argument("--fov", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--require-full-m1", type=int, default=175,
                    help="refuse to draw until this many segments have M1 "
                         "metadata; the occupancy stratum is undefined without it")
    a = ap.parse_args()

    rows = load_manifest(a.manifest)
    views = load_views(a.fov)
    ai = load_ai_frames(a.m1_dir)

    print("manifest segments : %d" % len(rows))
    print("FOV view rows     : %d (segments without a view go to stratum U)"
          % len(views))
    print("M1 ai_frames rows : %d" % len(ai))

    if len(ai) < a.require_full_m1:
        # This is the honest failure. Drawing now would put every unmeasured
        # segment in the "motion" stratum by default, which is not a
        # stratification, it is a coin flip wearing a label.
        print("REFUSING to draw: ai_frames known for %d/%d segments. The "
              "occupancy stratum registered in Checkpoint 2a A2 is not "
              "defined until M1+ finishes." % (len(ai), a.require_full_m1),
              file=sys.stderr)
        return 3

    pool = []
    for r in rows:
        r = dict(r)
        r["cell"] = cell_of(r["seg"], views, ai)
        r["ai_frames"] = ai.get(r["seg"], "")
        pool.append(r)

    os.makedirs(a.out_dir, exist_ok=True)

    sweep, q1, c1 = draw(pool, N_SWEEP, SEED_SWEEP)
    taken = {s["seg"] for s in sweep}
    rest = [s for s in pool if s["seg"] not in taken]
    verify, q2, c2 = draw(rest, N_VERIFY, SEED_VERIFY)

    overlap = taken & {s["seg"] for s in verify}
    if overlap:
        print("DISJOINTNESS VIOLATED: %s" % sorted(overlap), file=sys.stderr)
        return 4

    p1 = os.path.join(a.out_dir, "sweep_sample_12h.csv")
    p2 = os.path.join(a.out_dir, "verify_sample_4h.csv")
    s1, m1 = write_sample(p1, sweep, SEED_SWEEP, N_SWEEP, c1, q1)
    s2, m2 = write_sample(p2, verify, SEED_VERIFY, N_VERIFY, c2, q2)

    # The runner takes a bare list of basenames.
    for path, rowset in ((p1.replace(".csv", ".list"), sweep),
                         (p2.replace(".csv", ".list"), verify)):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("".join(r["seg"] + "\n" for r in rowset))

    print("\nsweep  : %d segments, %.2f h  SHA256 %s" % (len(sweep), m1["hours"], s1))
    print("verify : %d segments, %.2f h  SHA256 %s" % (len(verify), m2["hours"], s2))
    print("disjoint: yes (%d overlapping segments)" % len(overlap))
    print()
    print("PROVENANCE (also written into both .meta.json files):")
    for sentence in m1["provenance"].split(". "):
        print("  " + sentence.strip())
    print("\ncells (available / sweep quota):")
    for c in sorted(c1):
        print("  %-24s %3d / %d" % (c, len(c1[c]), q1.get(c, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
