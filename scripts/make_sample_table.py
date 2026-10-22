#!/usr/bin/env python3
r"""R1.3 -- the sample table: segments x view x time-of-day x clock stratum.

    python make_sample_table.py

Reads (through LINKS.md, read-only):
  analysis/tier0/manifest_rows_closed.csv   segment list, start time from the name
  runs/m1/<seg>.json                        decoded observation time, clock stratum,
                                            ai_frames (motion gate) from diagnostics
  runs/m1/<seg>.csv                         replay alerts per checker, shipped defaults
  analysis/e12/A1_FALL_BY_SEGMENT.json      Fall at theta = 0.525
  analysis/live_alert_index_20260902.csv    DEPLOYED (operator) alerts, mapped to
                                            segments with tier0_analysis.py's own rule
  analysis/fov_segments.csv                 view A / B
Asserts: 175 segments, 83.9626 h, deployed in-corpus total and per-view totals equal
tier0_results.json, replay totals equal generated_counts.json.

Writes 02_Manuscript/tables/sample_table.csv (full, one row per stratum),
sample_table_full.tex (supplement S3), sample_table.tex (body, <= 8 rows).
N+ (observed positive events) is 0 for every channel except Intrusion by the
signed blanket negative declaration (A1); Intrusion events occurred and were not
counted, so its N+ is reported as "> 0 (not counted)", never as a number.
The motion gate is reported as the registered occupancy variable: segments with
ai_frames == 0 ("gate never opened"). No other gate column exists in the data.
"""
import collections
import csv
import datetime as dt
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "theory_checks"))
import _common as C  # noqa: E402

TIM = C.TIM
OUT = os.path.join(TIM, "02_Manuscript", "tables")
TZ = dt.timezone(dt.timedelta(hours=7))
CHK = ["IntrusionChecker", "HelmetChecker", "FallChecker", "SmokeFireChecker", "RunningChecker"]
SHORT = {"IntrusionChecker": "Intr", "HelmetChecker": "Helm", "FallChecker": "Fall",
         "SmokeFireChecker": "Smk", "RunningChecker": "Run"}
EVENT_TO_CHECKER = {"intrusion": "IntrusionChecker", "no_helmet": "HelmetChecker",
                    "fall": "FallChecker", "smoke_fire": "SmokeFireChecker",
                    "running": "RunningChecker", "forklift_speed": "ForkliftSpeedChecker"}
BINS = [(0, 4), (4, 8), (8, 12), (12, 16), (16, 20), (20, 24)]


def seg_start(seg):
    _, d, hm = seg.split("_")
    return dt.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]), int(hm[:2]), int(hm[2:4]), tzinfo=TZ)


def main():
    ins = C.load_insitu()
    views = {}
    with io.open(C.FOV, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            views[r["file"].replace(".mp4", "")] = r["view"]
    a1 = json.load(io.open(C.A1_FALL, encoding="utf-8"))["segments"]
    segs = []
    with io.open(C.MANIFEST, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            s = r["file"].replace(".mp4", "")
            d = json.load(io.open(os.path.join(C.RUNS_M1, s + ".json"), encoding="utf-8"))
            # tier0_analysis.py uses d["fps"]; the FAR denominator uses fps_effective.
            # They are equal for every measured segment (asserted below).
            dur_t0 = int(d["frames_read"]) / float(d["fps"])
            segs.append({"seg": s, "start": seg_start(s), "dur_t0": dur_t0,
                         "hours": ins["hours"][s], "view": views.get(s, "U"),
                         "clock": "substituted" if s in ins["order"][:ins["n_sub"]] else "native",
                         "ai_frames": int((d.get("diagnostics") or {}).get("ai_frames", -1)),
                         "replay": ins["per_seg"][s], "fall0525": a1[s]["alerts"]["0.525"],
                         "deployed": collections.Counter()})
    segs.sort(key=lambda x: x["start"])
    assert len(segs) == 175, len(segs)
    H = sum(x["hours"] for x in segs)
    assert abs(H - 83.9626) < 5e-5, H
    assert max(abs(x["dur_t0"] / 3600 - x["hours"]) for x in segs) < 1e-6

    # deployed alerts -> segments, tier0_analysis.py rule: first segment j with
    # start_j <= t <= end_j, end = start + decoded seconds; alerts outside the window dropped
    for x in segs:
        x["end"] = x["start"] + dt.timedelta(seconds=x["dur_t0"])
    w0, w1 = segs[0]["start"], segs[-1]["end"]
    alerts = []
    with io.open(C.LIVE_INDEX, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            alerts.append((dt.datetime.fromisoformat(r["ts_site"]), r["event_type"]))
    alerts.sort()
    si = 0
    for t, ev in alerts:
        if t < w0 or t > w1:
            continue
        while si < len(segs) and segs[si]["end"] < t:
            si += 1
        j = si
        while j < len(segs) and segs[j]["start"] <= t:
            if segs[j]["start"] <= t <= segs[j]["end"]:
                segs[j]["deployed"][EVENT_TO_CHECKER.get(ev, ev)] += 1
                break
            j += 1
    t0 = json.load(io.open(os.path.join(C.MEAS, "analysis", "tier0", "tier0_results.json"), encoding="utf-8"))
    dep_tot = collections.Counter()
    for x in segs:
        dep_tot.update(x["deployed"])
    want = collections.Counter({EVENT_TO_CHECKER[k]: v for k, v in t0["result1_in_corpus"].items()})
    assert dep_tot == want, (dep_tot, want)
    for v in ("A", "B"):
        n_v = sum(sum(x["deployed"].values()) for x in segs if x["view"] == v)
        assert n_v == t0["result4_views"][v]["n"], (v, n_v)
    cnt = C.counts()
    for ck in CHK:
        assert sum(x["replay"].get(ck, 0) for x in segs) == cnt["far_%s_pooled_alerts" % ck.lower()], ck

    # strata
    def tbin(x):
        h = x["start"].hour
        return next("%02d-%02d" % b for b in BINS if b[0] <= h < b[1])

    def daynight(x):
        return "day" if 6 <= x["start"].hour < 18 else "night"

    def agg(group):
        r = {"n": len(group), "hours": sum(x["hours"] for x in group),
             "gate_never_open": sum(1 for x in group if x["ai_frames"] == 0),
             "fall0525": sum(x["fall0525"] for x in group),
             "subst": sum(1 for x in group if x["clock"] == "substituted")}
        for ck in CHK:
            r["dep_" + ck] = sum(x["deployed"].get(ck, 0) for x in group)
            r["rep_" + ck] = sum(x["replay"].get(ck, 0) for x in group)
        return r

    full = collections.OrderedDict()
    for x in segs:
        full.setdefault((x["view"], tbin(x), x["clock"]), []).append(x)
    full = collections.OrderedDict(sorted(full.items()))
    compact = collections.OrderedDict()
    for x in segs:
        compact.setdefault((x["view"], daynight(x)), []).append(x)
    compact = collections.OrderedDict(sorted(compact.items()))

    os.makedirs(OUT, exist_ok=True)
    cols = (["view", "time_of_day", "clock_stratum", "segments", "hours", "gate_never_open_segments"]
            + ["deployed_" + SHORT[c] for c in CHK] + ["replay_" + SHORT[c] for c in CHK]
            + ["fall_theta0525_A1", "N_plus_intrusion", "N_plus_other"])
    rows_csv = []
    for (v, b, clk), g in full.items():
        a = agg(g)
        rows_csv.append([v, b, clk, a["n"], "%.4f" % a["hours"], a["gate_never_open"]]
                        + [a["dep_" + c] for c in CHK] + [a["rep_" + c] for c in CHK]
                        + [a["fall0525"], ">0 (not counted)", 0])
    tot = agg(segs)
    rows_csv.append(["all", "all", "all", tot["n"], "%.4f" % tot["hours"], tot["gate_never_open"]]
                    + [tot["dep_" + c] for c in CHK] + [tot["rep_" + c] for c in CHK]
                    + [tot["fall0525"], ">0 (not counted)", 0])
    with io.open(os.path.join(OUT, "sample_table.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows_csv)

    BS = chr(92)

    def tex_rows(groups, label_fn):
        out = []
        for key, g in groups.items():
            a = agg(g)
            out.append(" & ".join([label_fn(key), str(a["n"]), "%.2f" % a["hours"], str(a["gate_never_open"]),
                                   str(a["subst"]),
                                   str(a["dep_IntrusionChecker"]), str(a["rep_IntrusionChecker"]),
                                   str(a["rep_HelmetChecker"]), str(a["rep_FallChecker"]),
                                   str(a["fall0525"]), str(a["rep_SmokeFireChecker"] + a["rep_RunningChecker"])])
                       + " " + BS + BS)
        return out

    head = [BS + "begin{tabular}{@{}lrrrrrrrrrr@{}}", BS + "toprule",
            "Stratum & Seg & h & G$_0$ & Sub & Intr$_{\\mathrm{dep}}$ & Intr & Helm & Fall & Fall$_{.525}$ & S+R "
            + BS + BS, BS + "midrule"]
    total_row = " & ".join([BS + "textbf{All}", str(tot["n"]), "%.2f" % tot["hours"], str(tot["gate_never_open"]),
                            str(tot["subst"]), str(tot["dep_IntrusionChecker"]), str(tot["rep_IntrusionChecker"]),
                            str(tot["rep_HelmetChecker"]), str(tot["rep_FallChecker"]), str(tot["fall0525"]),
                            str(tot["rep_SmokeFireChecker"] + tot["rep_RunningChecker"])]) + " " + BS + BS
    foot = [BS + "midrule", total_row, BS + "bottomrule", BS + "end{tabular}"]
    gen = "% generated by scripts/make_sample_table.py -- do not edit"
    body = [gen] + head + tex_rows(compact, lambda k: "%s, %s" % k) + foot
    supp = [gen] + head + tex_rows(full, lambda k: "%s, %s h, %s" % (k[0], k[1], "sub" if k[2] == "substituted" else "nat")) + foot
    io.open(os.path.join(OUT, "sample_table.tex"), "w", encoding="utf-8", newline="\n").write("\n".join(body) + "\n")
    io.open(os.path.join(OUT, "sample_table_full.tex"), "w", encoding="utf-8", newline="\n").write("\n".join(supp) + "\n")
    print("sample table: %d segments, %.4f h; full %d strata, compact %d rows" % (tot["n"], tot["hours"], len(full), len(compact)))
    print("  deployed in-corpus %s == tier0 %s; views A %d / B %d == tier0" % (
        dict(dep_tot), dict(want), t0["result4_views"]["A"]["n"], t0["result4_views"]["B"]["n"]))
    print("  replay totals == generated_counts for %s" % ", ".join(SHORT[c] for c in CHK))
    for (v, d_), g in compact.items():
        a = agg(g)
        print("  %s %-5s seg %3d  %6.2f h  gate0 %3d  sub %2d  dep-intr %5d  rep: intr %4d helm %3d fall %3d f.525 %2d s+r %d" % (
            v, d_, a["n"], a["hours"], a["gate_never_open"], a["subst"], a["dep_IntrusionChecker"],
            a["rep_IntrusionChecker"], a["rep_HelmetChecker"], a["rep_FallChecker"], a["fall0525"],
            a["rep_SmokeFireChecker"] + a["rep_RunningChecker"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
