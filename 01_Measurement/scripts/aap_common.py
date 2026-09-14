#!/usr/bin/env python3
"""
Shared loading and validation for the AAP v3 measurement scripts.

Every script in this directory reads its inputs through here, so a malformed
CSV fails once, loudly, in one place -- rather than silently producing a table.

The schemas are the ones frozen in
``01_Measurement/GT_protocol/GT_PROTOCOL.md`` section 6. If a schema changes
there, it changes here, the protocol version is bumped, and everything is
re-scored.

Standard library only: this has to run on the Jetson inside the AAP container
without adding dependencies.
"""

from __future__ import annotations

import csv
import json
import os
import sys

# The console on the author's machine is cp1258; a Vietnamese
# character in a warning would otherwise crash the tool that was
# printing the warning. Fail on the data, never on the message
# about the data.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# The seven checkers, frozen. Any other name is a typo and is rejected.
CHECKERS = (
    "FallChecker",
    "IntrusionChecker",
    "SmokeFireChecker",
    "HelmetChecker",
    "EnhancedHelmetChecker",
    "RunningChecker",
    "ForkliftSpeedChecker",
)

LABELS = {
    "FallChecker": ("fall",),
    "IntrusionChecker": ("intrusion",),
    "SmokeFireChecker": ("fire", "smoke"),
    "HelmetChecker": ("no_helmet", "helmet_worn_improperly"),
    "EnhancedHelmetChecker": ("no_helmet", "helmet_worn_improperly"),
    "RunningChecker": ("running",),
    "ForkliftSpeedChecker": ("overspeed",),
}

EXCLUSION_REASONS = ("below_min_duration", "subject_unidentifiable",
                     "no_speed_reference", "occluded", "other")

# GT_PROTOCOL.md section 3: one matching window for every checker, fixed.
MATCH_WINDOW_S = 2.0

# GT_PROTOCOL.md section 4. Merge gaps are annotation-side; the scorer needs
# them only to warn when annotations violate their own definition.
# GT_PROTOCOL.md v1.1 section 4, principle P8:
#   merge gap = max(operational merge, production cooldown)
# Cooldowns read from the deployed image sha256:2f41e503 on 2026-08-20; see
# GT_protocol/production_config_dump_20260820.txt. Changing a cooldown in the
# system means changing the gap here AND re-scoring every affected table.
MERGE_GAP_S = {
    "FallChecker": 30.0,            # op 10 s, module cooldown 30.0 s
    "IntrusionChecker": 30.0,       # op 30 s, no module cooldown
    "SmokeFireChecker": 60.0,       # op 60 s, no_cooldown=True
    "HelmetChecker": 30.0,          # shares GT with A1, larger gap governs
    "EnhancedHelmetChecker": 30.0,  # op 15 s, module cooldown 30.0 s
    "RunningChecker": 20.0,         # op 10 s, module cooldown 20.0 s  <- CP1a fix
    "ForkliftSpeedChecker": 20.0,   # op 20 s, module cooldown 15.0 s
}

# Production cooldowns, kept beside the gaps so a future change is visible.
PRODUCTION_COOLDOWN_S = {
    "FallChecker": 30.0, "IntrusionChecker": None, "SmokeFireChecker": 0.0,
    "HelmetChecker": None, "EnhancedHelmetChecker": 30.0,
    "RunningChecker": 20.0, "ForkliftSpeedChecker": 15.0,
}
PROTOCOL_VERSION = "1.1"

MIN_DURATION_S = {
    "FallChecker": 1.0,
    "IntrusionChecker": 1.0,
    "SmokeFireChecker": 2.0,
    "HelmetChecker": 2.0,
    "EnhancedHelmetChecker": 2.0,
    "RunningChecker": 1.5,
    "ForkliftSpeedChecker": 2.0,
}

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.dirname(HERE)                       # 01_Measurement/
GT_DIR = os.path.join(MEAS, "GT_protocol")
FOOTAGE_DIR = os.path.join(MEAS, "footage_negative")
ANALYSIS_DIR = os.path.join(MEAS, "analysis")
RUNS_DIR = os.path.join(MEAS, "runs")


class DataError(Exception):
    """Raised on any schema or consistency violation. Never caught silently."""


def die(msg):
    raise DataError(msg)


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------
# Filled by the last read_rows() call. A caller that cares -- C2 does -- can
# assert on it instead of trusting that concatenation went the way it hoped.
LAST_READ_STATS = {}


def read_rows(path, required, aliases=None):
    """Read a CSV, skipping '#' comment lines, checking the header.

    HARNESS-19 #4. A file produced by `cat a.csv b.csv c.csv` carries one
    header per input. Those repeats are dropped here, by value, and counted in
    LAST_READ_STATS["repeat_header_rows"]. They are not tolerated silently:
    a header row read as data becomes checker="checker" and dies three
    functions later with a message about an unknown checker, which is a long
    way from the cat.

    HARNESS-19 #1. `aliases` maps a required column to other names that carry
    the same quantity: {"t_alert": ("t_video",)}. aap_offline_runner writes the
    alert stream with t_alert and the --record-candidates stream with t_video,
    and C2 must read the candidate stream. The mapping is declared by the
    caller and reported in LAST_READ_STATS["aliased"] so it appears in a log
    rather than only in someone's memory.
    """
    if not os.path.exists(path):
        die("missing file: %s" % path)
    with open(path, newline="", encoding="utf-8-sig") as fh:
        lines = [ln for ln in fh if not ln.lstrip().startswith("#")]
    if not lines:
        die("empty file: %s" % path)
    rdr = csv.DictReader(lines)
    fields = list(rdr.fieldnames or [])

    applied = {}
    for col in required:
        if col in fields:
            continue
        for alt in (aliases or {}).get(col, ()):
            if alt in fields:
                applied[col] = alt
                break
    missing = [c for c in required if c not in fields and c not in applied]
    if missing:
        die("%s: header is missing column(s): %s" % (path, ", ".join(missing)))

    header_row = {k: k for k in fields}
    rows, repeats = [], 0
    for i, r in enumerate(rdr, start=2):
        if all((v or "").strip() == "" for v in r.values()):
            continue
        if r == header_row:
            repeats += 1
            continue
        for col, alt in applied.items():
            r[col] = r.get(alt)
        r["__line__"] = i
        r["__file__"] = os.path.basename(path)
        rows.append(r)
    LAST_READ_STATS.clear()
    LAST_READ_STATS.update({"path": path, "rows": len(rows),
                            "repeat_header_rows": repeats,
                            "aliased": dict(applied)})
    return rows


def as_float(row, col, path):
    try:
        return float((row.get(col) or "").strip())
    except ValueError:
        die("%s line %s: column %r is not a number: %r"
            % (path, row["__line__"], col, row.get(col)))


def check_checker(row, path):
    c = (row.get("checker") or "").strip()
    if c not in CHECKERS:
        die("%s line %s: unknown checker %r. Must be one of: %s"
            % (path, row["__line__"], c, ", ".join(CHECKERS)))
    return c


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------
MANIFEST_COLS = ["file", "domain", "source", "capture_date", "duration_s",
                 "independent_of_dev", "checkers", "has_events", "notes"]


# The closed 175-segment corpus. HARNESS-19 #2: FOOTAGE_DIR points at
# footage_negative/, which is the layout the v2 scripts were written for and
# does not exist on the measurement device; the copy of it in the submission
# tree holds 52 HOM rows, the corpus as it stood on 2026-08-28, so copying that
# across would make load_predictions die on every C1 segment drawn after it.
# The manifest of record has been ops/manifest_rows_closed.csv since the corpus
# closed on 2026-09-02, in exactly MANIFEST_COLS, with the eleven HARNESS-5
# durations corrected by decoding.
CLOSED_MANIFEST = os.path.join(MEAS, "ops", "manifest_rows_closed.csv")


def default_manifest_path():
    legacy = os.path.join(FOOTAGE_DIR, "footage_manifest.csv")
    if os.path.exists(legacy):
        return legacy
    return CLOSED_MANIFEST


def load_manifest(path=None):
    """Return {file_id: dict}. This is the authority on what footage exists."""
    path = path or default_manifest_path()
    rows = read_rows(path, MANIFEST_COLS)
    out = {}
    for r in rows:
        fid = (r["file"] or "").strip()
        if not fid:
            die("%s line %s: empty file id" % (path, r["__line__"]))
        if fid in out:
            die("%s line %s: duplicate file id %r" % (path, r["__line__"], fid))
        dur = as_float(r, "duration_s", path)
        if dur <= 0:
            die("%s line %s: duration_s must be > 0" % (path, r["__line__"]))
        indep = (r["independent_of_dev"] or "").strip().lower()
        if indep not in ("y", "n", "yes", "no"):
            die("%s line %s: independent_of_dev must be y or n, got %r"
                % (path, r["__line__"], r["independent_of_dev"]))
        checkers = [c.strip() for c in (r["checkers"] or "").split(";") if c.strip()]
        if not checkers:
            die("%s line %s: file %r lists no checkers; a file nothing is scored "
                "on contributes to no denominator and should not be in the "
                "manifest" % (path, r["__line__"], fid))
        for c in checkers:
            if c not in CHECKERS:
                die("%s line %s: unknown checker %r in checkers column"
                    % (path, r["__line__"], c))
        out[fid] = {
            "file": fid,
            "domain": (r["domain"] or "").strip(),
            "source": (r["source"] or "").strip(),
            "capture_date": (r["capture_date"] or "").strip(),
            "duration_s": dur,
            "independent": indep.startswith("y"),
            "checkers": checkers,
            "has_events": (r["has_events"] or "").strip().lower().startswith("y"),
            "notes": (r["notes"] or "").strip(),
        }
    return out


# ---------------------------------------------------------------------------
# ground truth
# ---------------------------------------------------------------------------
GT_COLS = ["video_id", "checker", "subject_id", "t_start", "t_end", "label",
           "annotator", "pass"]


def load_gt(path=None, manifest=None, which_pass=1):
    """Return list of event dicts for the given annotation pass."""
    path = path or os.path.join(GT_DIR, "gt_annotations.csv")
    rows = read_rows(path, GT_COLS)
    events = []
    for r in rows:
        try:
            p = int((r.get("pass") or "1").strip())
        except ValueError:
            die("%s line %s: pass must be an integer" % (path, r["__line__"]))
        if p != which_pass:
            continue
        checker = check_checker(r, path)
        ts, te = as_float(r, "t_start", path), as_float(r, "t_end", path)
        if te <= ts:
            die("%s line %s: t_end (%.1f) must exceed t_start (%.1f)"
                % (path, r["__line__"], te, ts))
        dur = te - ts
        if dur < MIN_DURATION_S[checker] - 1e-9:
            die("%s line %s: %s event lasts %.1fs, below the %.1fs minimum "
                "duration fixed in GT_PROTOCOL.md 4. Annotate it as an "
                "exclusion instead."
                % (path, r["__line__"], checker, dur, MIN_DURATION_S[checker]))
        label = (r.get("label") or "").strip()
        if label not in LABELS[checker]:
            die("%s line %s: label %r is not valid for %s (expected one of %s)"
                % (path, r["__line__"], label, checker,
                   ", ".join(LABELS[checker])))
        vid = (r["video_id"] or "").strip()
        if manifest is not None and vid not in manifest:
            die("%s line %s: video_id %r is not in the footage manifest"
                % (path, r["__line__"], vid))
        if manifest is not None and checker not in manifest[vid]["checkers"]:
            die("%s line %s: %s is annotated on %r, but the manifest does not "
                "list that checker for that file" % (path, r["__line__"],
                                                     checker, vid))
        events.append({
            "video_id": vid, "checker": checker,
            "subject_id": (r.get("subject_id") or "").strip(),
            "t_start": ts, "t_end": te, "label": label,
            "annotator": (r.get("annotator") or "").strip(),
            "notes": (r.get("notes") or "").strip(),
            "line": r["__line__"],
        })
    _warn_merge_gap(events)
    return events


def _warn_merge_gap(events):
    """Two events for one subject closer than the merge gap should be one."""
    by = {}
    for e in events:
        by.setdefault((e["video_id"], e["checker"], e["subject_id"], e["label"]),
                      []).append(e)
    for key, evs in by.items():
        evs.sort(key=lambda e: e["t_start"])
        gap = MERGE_GAP_S[key[1]]
        for a, b in zip(evs, evs[1:]):
            if b["t_start"] - a["t_end"] < gap:
                sys.stderr.write(
                    "WARNING: %s/%s subject %s: events at line %d and %d are "
                    "%.1fs apart, under the %.1fs merge gap. By GT_PROTOCOL.md "
                    "2 these are one event. Merge them.\n"
                    % (key[0], key[1], key[2], a["line"], b["line"],
                       b["t_start"] - a["t_end"], gap))


EXCL_COLS = ["video_id", "checker", "t_start", "t_end", "reason"]


def load_exclusions(path=None):
    path = path or os.path.join(GT_DIR, "gt_exclusions.csv")
    if not os.path.exists(path):
        return []
    rows = read_rows(path, EXCL_COLS)
    out = []
    for r in rows:
        checker = check_checker(r, path)
        reason = (r.get("reason") or "").strip()
        if reason not in EXCLUSION_REASONS:
            die("%s line %s: reason %r not in %s"
                % (path, r["__line__"], reason, ", ".join(EXCLUSION_REASONS)))
        ts, te = as_float(r, "t_start", path), as_float(r, "t_end", path)
        if te <= ts:
            die("%s line %s: t_end must exceed t_start" % (path, r["__line__"]))
        out.append({"video_id": (r["video_id"] or "").strip(), "checker": checker,
                    "t_start": ts, "t_end": te, "reason": reason})
    return out


# ---------------------------------------------------------------------------
# predictions
# ---------------------------------------------------------------------------
PRED_COLS = ["run_id", "video_id", "checker", "t_alert", "confidence",
             "frame_idx", "track_id", "event_type"]


# HARNESS-19 #1. The candidate stream names the same quantity t_video.
PRED_ALIASES = {"t_alert": ("t_video",)}


def load_predictions(path, manifest=None, run_id=None):
    rows = read_rows(path, PRED_COLS, aliases=PRED_ALIASES)
    out = []
    for r in rows:
        rid = (r["run_id"] or "").strip()
        if run_id is not None and rid != run_id:
            continue
        checker = check_checker(r, path)
        vid = (r["video_id"] or "").strip()
        if manifest is not None and vid not in manifest:
            die("%s line %s: video_id %r is not in the footage manifest"
                % (path, r["__line__"], vid))
        conf_raw = (r.get("confidence") or "").strip()
        out.append({
            "run_id": rid, "video_id": vid, "checker": checker,
            "t_alert": as_float(r, "t_alert", path),
            "confidence": float(conf_raw) if conf_raw not in ("", "NA") else None,
            "frame_idx": (r.get("frame_idx") or "").strip(),
            "track_id": (r.get("track_id") or "").strip(),
            "event_type": (r.get("event_type") or "").strip(),
            "line": r["__line__"],
        })
    return out


# ---------------------------------------------------------------------------
# run configuration
# ---------------------------------------------------------------------------
def write_run_config(run_id, cfg, runs_dir=None):
    runs_dir = runs_dir or RUNS_DIR
    os.makedirs(runs_dir, exist_ok=True)
    path = os.path.join(runs_dir, "%s.json" % run_id)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2, sort_keys=True)
    return path


def read_run_config(run_id, runs_dir=None):
    runs_dir = runs_dir or RUNS_DIR
    path = os.path.join(runs_dir, "%s.json" % run_id)
    if not os.path.exists(path):
        die("run %r has no configuration at %s. Every predictions row must be "
            "traceable to the configuration that produced it." % (run_id, path))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    return path
