#!/usr/bin/env python3
"""CP1h H2/H3: the noise floor, and the 2x2 grid read through it.

Implements the predicate registered in PREREGISTERED_CP1H.md section 1.3 BEFORE
any of these numbers existed. Two runs agree on a clip when their alert sets are
identical as multisets of

    (checker, event_type, t_alert, frame_idx, track_id)

`confidence` is deliberately NOT in the predicate and is reported separately: an
alert that appears or disappears is a different kind of event from a float that
moved in its seventh decimal, and pooling them would hide that.

Nothing here reports pass/fail. Section 1.4 requires a rate:

    noise floor = alerts present in exactly one of the two runs
                  / total alerts across both runs

Three comparisons, in the order they must be read:

  cell 0   native run 1  vs  native run 2   -> pipeline non-determinism alone
  cell 4   native        vs  adapted, on clips where neither fps nor resolution
                             changed        -> re-encode sensitivity, net of cell 0
  cells1-3 native        vs  adapted, on the clips E-2 and/or E-3 actually touched

Usage:
    python noise_floor.py --a <dirA> --b <dirB> --label "..." [--only-clips file]
    python noise_floor.py --grid       (runs all of the above from PAIR_PROBE)
"""
import argparse, collections, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = ("checker", "event_type", "t_alert", "frame_idx", "track_id")


def load_alerts(path):
    """-> (multiset of predicate keys, {key: [confidence,...]})"""
    keys = collections.Counter()
    conf = collections.defaultdict(list)
    if not os.path.exists(path):
        return None, None
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            k = tuple(r[c] for c in KEY)
            keys[k] += 1
            try:
                conf[k].append(float(r["confidence"]))
            except (KeyError, ValueError):
                pass
    return keys, conf


def compare(dir_a, dir_b, clips=None):
    names = sorted(f for f in os.listdir(dir_a) if f.endswith(".csv"))
    if clips is not None:
        names = [n for n in names if n[:-4] in clips]
    tot_a = tot_b = only_a = only_b = shared = 0
    conf_diff = 0
    conf_max = 0.0
    per_checker = collections.defaultdict(lambda: {"only_a": 0, "only_b": 0, "shared": 0})
    clips_compared = clips_missing = clips_divergent = 0
    divergent_examples = []

    for n in names:
        ka, ca = load_alerts(os.path.join(dir_a, n))
        kb, cb = load_alerts(os.path.join(dir_b, n))
        if ka is None or kb is None:
            clips_missing += 1
            continue
        clips_compared += 1
        tot_a += sum(ka.values())
        tot_b += sum(kb.values())
        # multiset difference
        da = ka - kb
        db = kb - ka
        sh = ka & kb
        only_a += sum(da.values())
        only_b += sum(db.values())
        shared += sum(sh.values())
        for k, v in da.items():
            per_checker[k[0]]["only_a"] += v
        for k, v in db.items():
            per_checker[k[0]]["only_b"] += v
        for k, v in sh.items():
            per_checker[k[0]]["shared"] += v
        if da or db:
            clips_divergent += 1
            if len(divergent_examples) < 8:
                divergent_examples.append(
                    {"clip": n,
                     "only_a": [list(k) for k in list(da.elements())[:4]],
                     "only_b": [list(k) for k in list(db.elements())[:4]]})
        # confidence drift on alerts that DO match
        for k in sh:
            va, vb = sorted(ca.get(k, [])), sorted(cb.get(k, []))
            for x, y in zip(va, vb):
                if x != y:
                    conf_diff += 1
                    conf_max = max(conf_max, abs(x - y))

    denom = tot_a + tot_b
    return {
        "clips_compared": clips_compared, "clips_missing": clips_missing,
        "clips_divergent": clips_divergent,
        "alerts_a": tot_a, "alerts_b": tot_b,
        "alerts_only_a": only_a, "alerts_only_b": only_b,
        "alerts_shared": shared,
        "divergent_alerts": only_a + only_b,
        "total_alerts_both_runs": denom,
        "noise_floor": (only_a + only_b) / denom if denom else float("nan"),
        "confidence_mismatched_on_matching_alerts": conf_diff,
        "confidence_max_abs_diff": conf_max,
        "per_checker": {k: dict(v) for k, v in per_checker.items()},
        "divergent_examples": divergent_examples,
    }


def grid_cells():
    """H3: classify clips by what the adaptation ACTUALLY changed, using decoded
    frame counts and durations rather than the container's fps hint."""
    p = os.path.join(HERE, "PAIR_PROBE_gmdcsa24.csv")
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    cells = collections.defaultdict(list)
    detail = []
    for r in rows:
        stem = r["clip"][:-4]
        res_changed = (r["nat_w"], r["nat_h"]) != (r["adp_w"], r["adp_h"])

        def n(x):
            try:
                return int(x)
            except (TypeError, ValueError):
                return None

        na, ab = n(r["nat_nb_read_frames"]), n(r["adp_nb_read_frames"])
        frames_changed = (na is None or ab is None or na != ab)
        try:
            nd, ad = float(r["nat_duration"]), float(r["adp_duration"])
            dur_delta = abs(nd - ad)
        except (TypeError, ValueError):
            nd = ad = None
            dur_delta = float("nan")
        cell = ("res_changed" if res_changed else "res_same",
                "frames_changed" if frames_changed else "frames_same")
        cells[cell].append(stem)
        detail.append({"clip": stem, "res_changed": res_changed,
                       "nat_frames": na, "adp_frames": ab,
                       "frames_changed": frames_changed,
                       "nat_duration": nd, "adp_duration": ad,
                       "duration_delta_s": dur_delta})
    return cells, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a")
    ap.add_argument("--b")
    ap.add_argument("--label", default="comparison")
    ap.add_argument("--only-cell", default=None,
                    help="res_same:frames_same etc, from PAIR_PROBE")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    clips = None
    if a.only_cell:
        cells, _ = grid_cells()
        key = tuple(a.only_cell.split(":"))
        clips = set(cells.get(key, []))
        print("cell %s -> %d clips" % (a.only_cell, len(clips)))

    res = compare(a.a, a.b, clips)
    res["label"] = a.label
    res["dir_a"], res["dir_b"] = a.a, a.b
    res["predicate"] = list(KEY)
    print(json.dumps({k: v for k, v in res.items() if k != "divergent_examples"},
                     indent=2))
    if res["divergent_examples"]:
        print("\nfirst divergent clips:")
        for d in res["divergent_examples"]:
            print("  ", d["clip"], "onlyA", d["only_a"], "onlyB", d["only_b"])
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        print("\nwrote", a.out)


if __name__ == "__main__":
    main()
