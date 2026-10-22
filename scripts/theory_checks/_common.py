#!/usr/bin/env python3
r"""Shared paths and readers for the P1-P7 checks (CP-alpha1).

The measurement tree is read through the path LINKS.md names and never
written. Every input file's SHA-256 is recorded so theory_numbers.json says
which measurement it describes; where LINKS.md lists the same file, the hash
there is compared and the comparison is reported (not enforced: LINKS.md is
the hash at the last manuscript build, and generated_counts.json is rebuilt
by every build).
"""
import collections
import csv
import hashlib
import io
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
TIM = os.path.dirname(SCRIPTS)
LINKS = os.path.join(TIM, "LINKS.md")
OUTDIR = HERE


def _meas_from_links():
    """The measurement tree: $AAP_MEAS if set; else the path LINKS.md names (the
    authoring workspace); else 01_Measurement at the top of the released
    repository (aap-tim-release), which is where a clean clone has it."""
    if os.environ.get("AAP_MEAS"):
        return os.path.normpath(os.environ["AAP_MEAS"])
    if os.path.exists(LINKS):
        txt = io.open(LINKS, encoding="utf-8").read()
        m = re.search(r"`(\.\./Submission Elsevier/01_Measurement)/", txt)
        if not m:
            raise SystemExit("LINKS.md does not name the measurement tree")
        return os.path.normpath(os.path.join(TIM, m.group(1)))
    rel = os.path.join(TIM, "01_Measurement")
    if os.path.isdir(rel):
        return rel
    raise SystemExit("measurement tree not found: set AAP_MEAS")


MEAS = _meas_from_links()
COUNTS = os.path.join(MEAS, "generated_counts.json")
A1_FALL = os.path.join(MEAS, "analysis", "e12", "A1_FALL_BY_SEGMENT.json")
E12 = os.path.join(MEAS, "analysis", "e12", "E12_COST_AXIS.json")
VERIFY_LIST = os.path.join(MEAS, "ops", "samples", "verify_sample_4h.list")
MECHANISMS = os.path.join(MEAS, "analysis", "silent_mechanisms.csv")
CORRECTIONS = os.path.join(MEAS, "analysis", "tier0", "duration_corrections.json")
RUNS_M1 = os.path.join(MEAS, "runs", "m1")

MANIFEST = os.path.join(MEAS, "analysis", "tier0", "manifest_rows_closed.csv")
FOV = os.path.join(MEAS, "analysis", "fov_segments.csv")
SWEEP_LIST = os.path.join(MEAS, "ops", "samples", "sweep_sample_12h.list")
VERIFY_META = os.path.join(MEAS, "ops", "samples", "verify_sample_4h.meta.json")
LIVE_INDEX = os.path.join(MEAS, "analysis", "live_alert_index_20260902.csv")


def registered_draw():
    """Re-run the REGISTERED sweep/verification draw (scripts/draw_sweep_samples.py
    in the measurement tree, imported read-only, no bytecode written) and return
    its cells. Refuses if the re-draw does not reproduce the stored lists."""
    import sys
    sys.dont_write_bytecode = True
    sys.path.insert(0, os.path.join(MEAS, "scripts"))
    try:
        import draw_sweep_samples as D
    finally:
        sys.path.pop(0)
    rows = D.load_manifest(MANIFEST)
    views = D.load_views(FOV)
    ai = D.load_ai_frames(RUNS_M1)
    pool = [dict(r, cell=D.cell_of(r["seg"], views, ai)) for r in rows]
    sweep, q1, c1 = D.draw(pool, D.N_SWEEP, D.SEED_SWEEP)
    taken = {s["seg"] for s in sweep}
    rest = [s for s in pool if s["seg"] not in taken]
    ver, q2, c2 = D.draw(rest, D.N_VERIFY, D.SEED_VERIFY)
    stored_v = io.open(VERIFY_LIST, encoding="utf-8").read().split()
    stored_s = io.open(SWEEP_LIST, encoding="utf-8").read().split()
    if [s["seg"] for s in ver] != stored_v or [s["seg"] for s in sweep] != stored_s:
        raise SystemExit("registered draw does NOT reproduce the stored lists -- refusing")
    return {"pool": pool, "sweep": [s["seg"] for s in sweep], "verify": stored_v,
            "verify_cells": {c: [s["seg"] for s in sorted(c2[c], key=lambda s: s["seg"])] for c in c2},
            "verify_quota": q2, "sweep_cells": {c: [s["seg"] for s in c1[c]] for c in c1},
            "sweep_quota": q1, "D": D}


def deployed_per_segment(order, hours):
    """Deployed (operator) alerts per segment and event type, mapped with
    tier0_analysis.py's own rule: first segment j with start_j <= t <= end_j,
    end = start + decoded seconds. Returns {seg: Counter(event_type)}; the
    caller asserts the totals against tier0_results.json."""
    import datetime as dt
    tz = dt.timezone(dt.timedelta(hours=7))
    segs = []
    for s in order:
        _, d, hm = s.split("_")
        st = dt.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), int(hm[:2]), int(hm[2:4]), tzinfo=tz)
        segs.append((st, st + dt.timedelta(hours=hours[s]), s))
    segs.sort()
    out = {s: collections.Counter() for s in order}
    alerts = []
    with io.open(LIVE_INDEX, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            alerts.append((dt.datetime.fromisoformat(r["ts_site"]), r["event_type"]))
    alerts.sort()
    w0, w1 = segs[0][0], segs[-1][1]
    si = 0
    for t, ev in alerts:
        if t < w0 or t > w1:
            continue
        while si < len(segs) and segs[si][1] < t:
            si += 1
        j = si
        while j < len(segs) and segs[j][0] <= t:
            if segs[j][0] <= t <= segs[j][1]:
                out[segs[j][2]][ev] += 1
                break
            j += 1
    return out


MODULE_TO_CHECKER = {"intrusion": "IntrusionChecker", "fall": "FallChecker",
                     "smoke_fire": "SmokeFireChecker", "running": "RunningChecker",
                     "forklift_speed": "ForkliftSpeedChecker"}

POISSON_2S_95_ZERO = -math.log(0.025)     # 3.6889: two-sided 95 %, k = 0
POISSON_1S_95_ZERO = -math.log(0.05)      # 2.9957: one-sided 95 % ("rule of three")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def links_hashes():
    if not os.path.exists(LINKS):          # released repository: no LINKS.md
        return {}
    txt = io.open(LINKS, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"`\.\./Submission Elsevier/(01_Measurement/[^`]+)`.*?\|\s*`([0-9a-f]{64})`", txt):
        out[os.path.normpath(os.path.join(MEAS, os.pardir, m.group(1)))] = m.group(2)
    return out


def provenance(paths):
    lk = links_hashes()
    rows = []
    for p in paths:
        h = sha256(p)
        rel = os.path.relpath(p, os.path.dirname(MEAS)).replace(os.sep, "/")
        listed = lk.get(os.path.normpath(p))
        rows.append({"file": rel, "sha256": h,
                     "links_md": ("not listed" if listed is None else
                                  ("matches LINKS.md" if listed == h else
                                   "differs from LINKS.md (%s...)" % listed[:12]))})
    return rows


def counts():
    return json.load(io.open(COUNTS, encoding="utf-8"))


def wilson(k, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def load_insitu():
    """Per-segment observation hours and per-checker alert counts, read the
    way count_everything.py reads them (runs/m1/<seg>.json + <seg>.csv)."""
    corr = {}
    if os.path.exists(CORRECTIONS):
        d = json.load(io.open(CORRECTIONS, encoding="utf-8"))
        corr = {e["file"].rsplit(".", 1)[0]: e for e in (d.get("fixed") or [])}
    hours, stratum, measured = {}, {}, set()
    for name in sorted(os.listdir(RUNS_M1)):
        if not name.endswith(".json"):
            continue
        d = json.load(io.open(os.path.join(RUNS_M1, name), encoding="utf-8"))
        fps = float(d.get("fps_effective") or d.get("fps") or 0)
        fr = int(d.get("frames_read") or 0)
        if fps <= 0:
            continue
        seg = name[:-5]
        hours[seg] = (fr / fps) / 3600.0
        stratum[seg] = "substituted" if seg in corr else "native"
        for m in str(d.get("modules") or "").split(","):
            m = m.strip()
            if m == "helmet":
                measured.add("EnhancedHelmetChecker" if d.get("helmet_mode") == "advanced"
                             else "HelmetChecker")
            elif m in MODULE_TO_CHECKER:
                measured.add(MODULE_TO_CHECKER[m])
    per_seg = {}
    for seg in hours:
        n = collections.Counter()
        cp = os.path.join(RUNS_M1, seg + ".csv")
        if os.path.exists(cp):
            with io.open(cp, encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    n[row["checker"]] += 1
        else:
            n = None
        per_seg[seg] = n
    sub = sorted(s for s in hours if stratum[s] == "substituted")
    nat = sorted(s for s in hours if stratum[s] == "native")
    return {"hours": hours, "order": sub + nat, "per_seg": per_seg,
            "measured": measured, "n_sub": len(sub), "n_nat": len(nat)}


def dump(name, payload):
    p = os.path.join(OUTDIR, name)
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    return p
