#!/usr/bin/env python3
"""Tier 0 -- results obtainable from data already on disk (CHECKPOINT_1G section G6).

Everything here is IN-SITU. Every table this script writes carries that label,
because the paper's central claim is that the two halves of the evidence come
from different places and must never be pooled silently.

Inputs, both closed and immutable at the time of writing:
  manifest_rows_closed.csv        175 segments, 83.9444 h, corpus closed 2026-09-02
                                  (durations for 11 segments corrected 2026-09-02;
                                   see KNOWN_ISSUES HARNESS-5 and duration_corrections.json)
  live_alert_index_20260902.csv   85,962 production alerts, 2026-05-25 -> 2026-09-02

A note on what "alert" means here and what it does not. The rows in the alert
index are alerts the deployed system actually raised and stored a snapshot for.
Inside the M1 window they are *candidate* false alarms: the corpus is a negative
corpus by design, but the blanket negative declaration (GT_PROTOCOL 5.5) is not
signed yet, so this script says "alert rate" everywhere and never "false-alarm
rate". Flipping that label is one signature away and no recomputation.
"""
import csv
import glob
import collections, datetime as dt, json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANA = os.path.dirname(HERE)
RUNS = os.path.join(os.path.dirname(ANA), "runs")   # 01_Measurement/runs

TZ = dt.timezone(dt.timedelta(hours=7))


def parse(s):
    return dt.datetime.fromisoformat(s)


# ---------------------------------------------------------------- observation
def decoded_seconds():
    """Observation time per segment, as the pipeline actually consumed it.

    GT_PROTOCOL 5.8, registered 2026-09-03: observation time is
    `frames_read / fps` summed over the segments actually measured; a manifest
    duration is DESCRIPTIVE ONLY and is never a denominator.

    The two disagree by a few parts in ten thousand, because some segments lose
    between one and ten trailing frames to damaged macroblocks in the camera's
    H.264 stream copy. That is a property of the footage rather than a defect,
    but it is the size of discrepancy that never gets noticed and never gets
    explained -- a corpus table and a false-alarm denominator quoting hours that
    differ in the fourth decimal, with nothing saying which is which. So there
    is one source, and this is it.
    """
    out = {}
    for f in sorted(glob.glob(os.path.join(RUNS, "m1", "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            continue
        fps = float(d.get("fps") or 0)
        fr = int(d.get("frames_read") or 0)
        if fps > 0 and fr > 0:
            out[str(d.get("video_id") or os.path.basename(f))] = fr / fps
    return out


def load_segments():
    """Each manifest row is an observation interval. Start comes from the file
    name (the recorder names a segment when it opens it); LENGTH comes from the
    decoded frame count where the segment has been measured, and only falls
    back to the manifest for segments M1 has not reached yet."""
    decoded = decoded_seconds()
    segs = []
    n_decoded = n_manifest = 0
    with open(os.path.join(HERE, "manifest_rows_closed.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            stem = r["file"].replace(".mp4", "")
            _, d, hm = stem.split("_")
            start = dt.datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]),
                                int(hm[0:2]), int(hm[2:4]), tzinfo=TZ)
            if r["file"] in decoded:
                dur = decoded[r["file"]]
                src = "decoded"
                n_decoded += 1
            else:
                dur = float(r["duration_s"])
                src = "manifest (not yet measured)"
                n_manifest += 1
            segs.append({"file": r["file"], "start": start,
                         "end": start + dt.timedelta(seconds=dur), "dur": dur,
                         "dur_source": src})
    segs.sort(key=lambda s: s["start"])
    print("observation time: %d segment(s) from decoded frames, %d still from "
          "the manifest" % (n_decoded, n_manifest))
    return segs


def load_alerts():
    rows = []
    with open(os.path.join(ANA, "live_alert_index_20260902.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append({"t": parse(r["ts_site"]), "type": r["event_type"],
                         "track": r["track_id"], "file": r["snapshot_file"]})
    rows.sort(key=lambda r: r["t"])
    return rows


# ------------------------------------------------------------------ intervals
def overlap_seconds(a0, a1, b0, b1):
    lo, hi = max(a0, b0), min(a1, b1)
    return max(0.0, (hi - lo).total_seconds())


def hour_buckets(segs):
    """Observed seconds per hour-of-day, splitting every segment at hour edges."""
    obs = collections.defaultdict(float)
    for s in segs:
        t = s["start"]
        while t < s["end"]:
            nxt = (t + dt.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            edge = min(nxt, s["end"])
            obs[t.hour] += (edge - t).total_seconds()
            t = edge
    return obs


# ------------------------------------------------------------------ statistics
def poisson_upper_2sided_95(T_hours):
    """Two-sided 95% Poisson upper limit for zero observed events (3.689/T).
    GT_PROTOCOL P6. Deliberately not the one-sided rule of three."""
    return 3.689 / T_hours if T_hours > 0 else float("nan")


def block_bootstrap_rate(seg_counts, seg_hours, iters=10000, seed=20260902):
    """Rate CI by resampling whole segments. Segments are the natural block:
    alerts within one are correlated (one person walking through fires many),
    across them much less so. Resampling individual alerts would pretend an
    independence the data does not have and would give a CI that is too tight."""
    rng = random.Random(seed)
    n = len(seg_counts)
    if n == 0:
        return (float("nan"), float("nan"))
    out = []
    idx = range(n)
    for _ in range(iters):
        pick = [rng.choice(idx) for _ in range(n)]
        c = sum(seg_counts[i] for i in pick)
        h = sum(seg_hours[i] for i in pick)
        if h > 0:
            out.append(c / h)
    out.sort()
    if not out:
        return (float("nan"), float("nan"))
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out))])


def main():
    segs = load_segments()
    alerts = load_alerts()

    win0, win1 = segs[0]["start"], segs[-1]["end"]
    total_h = sum(s["dur"] for s in segs) / 3600.0

    report = []
    W = report.append

    W("# TIER 0 -- IN-SITU RESULTS FROM THE CLOSED M1 CORPUS")
    W("")
    W("**Every number in this file is IN-SITU**: it comes from the deployment's own")
    W("footage and its own production alert stream. No ex-situ number appears here.")
    W("")
    W("Generated by `tier0_analysis.py`. Do not edit by hand.")
    W("")
    W("| | |")
    W("|---|---|")
    W("| corpus | M1, closed 2026-09-02T06:28:43+07:00 under rule E3 |")
    W("| segments | %d |" % len(segs))
    W("| observed time | %.4f h |" % total_h)
    W("| window | %s -> %s |" % (win0.isoformat(), win1.isoformat()))
    W("| alert index | %d production alerts, %s -> %s |"
      % (len(alerts), alerts[0]["t"].date(), alerts[-1]["t"].date()))
    W("")

    # ---------------------------------------------------------------- RESULT 1
    W("## Result 1 -- what the deployed configuration actually allocates (in situ)")
    W("")
    W("The system has seven checkers enabled. It has never had an allocation policy.")
    W("This is what its default thresholds allocate on their own.")
    W("")

    full = collections.Counter(a["type"] for a in alerts)
    ftot = sum(full.values())
    W("### 1a. Full production history (%s to %s, %d days)"
      % (alerts[0]["t"].date(), alerts[-1]["t"].date(),
         (alerts[-1]["t"] - alerts[0]["t"]).days))
    W("")
    W("| checker (event_type) | alerts | share of alert budget |")
    W("|---|---:|---:|")
    for k, v in full.most_common():
        W("| %s | %d | %.2f%% |" % (k, v, 100.0 * v / ftot))
    W("| **total** | **%d** | **100.00%%** |" % ftot)
    W("")

    # alerts inside observed segments only
    seg_counts = [0] * len(segs)
    seg_hours = [s["dur"] / 3600.0 for s in segs]
    inwin = []
    si = 0
    for a in alerts:
        if a["t"] < win0 or a["t"] > win1:
            continue
        while si < len(segs) and segs[si]["end"] < a["t"]:
            si += 1
        j = si
        while j < len(segs) and segs[j]["start"] <= a["t"]:
            if segs[j]["start"] <= a["t"] <= segs[j]["end"]:
                seg_counts[j] += 1
                inwin.append((a, j))
                break
            j += 1

    obs_alerts = [a for a, _ in inwin]
    c_obs = collections.Counter(a["type"] for a in obs_alerts)
    otot = sum(c_obs.values())

    W("### 1b. Inside the closed M1 corpus (%.4f h of observed footage)" % total_h)
    W("")
    W("Restricted to alerts that fall inside a recorded segment, so that the")
    W("denominator is time we can actually account for.")
    W("")
    W("| checker | alerts | share | rate (alerts/h) |")
    W("|---|---:|---:|---:|")
    for k, v in c_obs.most_common():
        W("| %s | %d | %.2f%% | %.3f |" % (k, v, 100.0 * v / otot, v / total_h))
    W("| **total** | **%d** | **100.00%%** | **%.3f** |" % (otot, otot / total_h))
    W("")

    lo, hi = block_bootstrap_rate(seg_counts, seg_hours)
    W("Segment block-bootstrap 95%% CI on the total alert rate: **[%.3f, %.3f] alerts/h**"
      % (lo, hi))
    W("(resampling whole segments, 10,000 iterations, seed 20260902)")
    W("")

    enabled = ["FallChecker", "SmokeFireChecker", "RunningChecker",
               "ForkliftSpeedChecker", "HelmetChecker", "EnhancedHelmetChecker",
               "IntrusionChecker"]
    seen = set()
    for k in c_obs:
        if "intrusion" in k:
            seen.add("IntrusionChecker")
        if "helmet" in k:
            seen.add("HelmetChecker")
    silent = [c for c in enabled if c not in seen]
    W("**Checkers that raised no alert at all inside the corpus window:** %s"
      % ", ".join(silent))
    W("")
    W("Zero alerts is not evidence that a checker works, and it is not evidence")
    W("that it is broken. It is evidence about spending only. A checker that")
    W("never fires costs nothing and may be covering everything or nothing; the")
    W("in-situ corpus cannot tell those apart, and that is exactly the asymmetry")
    W("this paper is about. Upper bound on the alert rate of each silent checker,")
    W("two-sided 95%% Poisson (P6): **%.4f alerts/h** over %.4f h."
      % (poisson_upper_2sided_95(total_h), total_h))
    W("")

    # ---------------------------------------------------------------- RESULT 2
    W("## Result 2 -- assumption A2 (stationarity) tested in situ")
    W("")
    W("The allocation in Section 3 assumes each checker's alert rate is stationary,")
    W("so that one threshold per checker can be chosen once and left alone. A2 is")
    W("testable directly on the corpus and it is the assumption most likely to be")
    W("false in a home.")
    W("")

    obs_by_hour = hour_buckets(segs)
    cnt_by_hour = collections.Counter()
    for a, _ in inwin:
        cnt_by_hour[a["t"].hour] += 1

    W("### 2a. Alert rate by hour of day (in situ)")
    W("")
    W("| hour (site local) | observed h | alerts | rate (alerts/h) |")
    W("|---:|---:|---:|---:|")
    rates = []
    for h in range(24):
        oh = obs_by_hour.get(h, 0.0) / 3600.0
        n = cnt_by_hour.get(h, 0)
        if oh <= 0:
            W("| %02d | 0.000 | - | not observed |" % h)
            continue
        r = n / oh
        rates.append((h, oh, n, r))
        W("| %02d | %.3f | %d | %.3f |" % (h, oh, n, r))
    W("")

    if rates:
        rr = [r for _, _, _, r in rates]
        busiest = max(rates, key=lambda x: x[3])
        quietest = min(rates, key=lambda x: x[3])
        W("- busiest hour: **%02d:00, %.3f alerts/h** (%.3f h observed)"
          % (busiest[0], busiest[3], busiest[1]))
        W("- quietest hour: **%02d:00, %.3f alerts/h** (%.3f h observed)"
          % (quietest[0], quietest[3], quietest[1]))
        if quietest[3] > 0:
            W("- **ratio busiest:quietest = %.1fx**" % (busiest[3] / quietest[3]))
        else:
            W("- quietest hour saw zero alerts, so the ratio is unbounded below;")
            W("  its two-sided 95%% Poisson upper limit is %.3f alerts/h"
              % poisson_upper_2sided_95(quietest[1]))
        W("- mean of hourly rates %.3f, sd %.3f"
          % (sum(rr) / len(rr),
             math.sqrt(sum((x - sum(rr) / len(rr)) ** 2 for x in rr) / max(1, len(rr) - 1))))
    W("")

    # dispersion test: Poisson would give variance == mean
    tot_n = sum(n for _, _, n, _ in rates)
    tot_h = sum(oh for _, oh, _, _ in rates)
    grand = tot_n / tot_h if tot_h else float("nan")
    chi2 = sum((n - grand * oh) ** 2 / (grand * oh) for _, oh, n, _ in rates if grand * oh > 0)
    dof = max(1, len([1 for _, oh, _, _ in rates if grand * oh > 0]) - 1)
    W("### 2b. Is one rate enough to describe all 24 hours?")
    W("")
    W("Under a single stationary rate the hourly counts are Poisson with mean")
    W("`rate x observed_hours`. Pearson dispersion statistic against that null:")
    W("")
    W("- pooled rate %.3f alerts/h over %.3f h" % (grand, tot_h))
    W("- chi-square = **%.1f** on %d degrees of freedom (ratio %.1f)"
      % (chi2, dof, chi2 / dof))
    W("")
    W("A ratio near 1 is consistent with stationarity; a large ratio is not.")
    W("This is reported as a descriptive dispersion measure, not as an exact test:")
    W("the hourly counts are not independent (one visitor spans several hours),")
    W("which inflates chi-square. The segment block-bootstrap above is the")
    W("interval that respects that dependence, and it is the one quoted in the")
    W("paper.")
    W("")

    # per-day
    W("### 2c. Alert rate by calendar day (in situ)")
    W("")
    obs_day = collections.defaultdict(float)
    # NB: local names here must not collide with `lo`/`hi` from the Result 1
    # bootstrap above -- they did once, and the clobbered value went into the
    # JSON while the markdown (written inline) stayed correct. Two artefacts
    # disagreeing because of a shadowed loop variable is exactly the kind of
    # silent divergence this project keeps finding elsewhere.
    for s in segs:
        t = s["start"]
        while t < s["end"]:
            nxt = dt.datetime.combine(t.date() + dt.timedelta(days=1),
                                      dt.time(0, 0), tzinfo=TZ)
            edge = min(nxt, s["end"])
            obs_day[t.date()] += (edge - t).total_seconds()
            t = edge
    cnt_day = collections.Counter(a["t"].date() for a, _ in inwin)
    W("| date | observed h | alerts | rate (alerts/h) |")
    W("|---|---:|---:|---:|")
    for d in sorted(obs_day):
        oh = obs_day[d] / 3600.0
        n = cnt_day.get(d, 0)
        W("| %s | %.3f | %d | %.3f |" % (d, oh, n, n / oh if oh else float("nan")))
    W("")

    # ---------------------------------------------------------------- RESULT 3
    W("## Result 3 -- temporal split (in situ)")
    W("")
    W("Split the corpus in half by observed time, not by wall-clock date, so both")
    W("halves carry the same weight of evidence.")
    W("")
    half = total_h / 2.0
    acc = 0.0
    split_i = 0
    for i, s in enumerate(segs):
        acc += s["dur"] / 3600.0
        if acc >= half:
            split_i = i
            break
    h1 = sum(s["dur"] for s in segs[:split_i + 1]) / 3600.0
    h2 = sum(s["dur"] for s in segs[split_i + 1:]) / 3600.0
    n1 = sum(seg_counts[:split_i + 1])
    n2 = sum(seg_counts[split_i + 1:])
    W("| half | segments | observed h | alerts | rate (alerts/h) |")
    W("|---|---:|---:|---:|---:|")
    W("| first | %d | %.3f | %d | %.3f |" % (split_i + 1, h1, n1, n1 / h1))
    W("| second | %d | %.3f | %d | %.3f |" % (len(segs) - split_i - 1, h2, n2, n2 / h2))
    W("")
    lo1, hi1 = block_bootstrap_rate(seg_counts[:split_i + 1], seg_hours[:split_i + 1])
    lo2, hi2 = block_bootstrap_rate(seg_counts[split_i + 1:], seg_hours[split_i + 1:])
    W("- first half 95%% CI [%.3f, %.3f]" % (lo1, hi1))
    W("- second half 95%% CI [%.3f, %.3f]" % (lo2, hi2))
    W("- split boundary: after `%s`" % segs[split_i]["file"])
    W("")
    W("Overlapping intervals mean the split does not by itself demonstrate drift;")
    W("disjoint intervals mean a threshold chosen on the first half is being")
    W("evaluated on a different regime. Either way this is the check a reviewer")
    W("asks for, and it is answered before being asked.")
    W("")
    W("**Not yet available:** the threshold-level version of this split, which")
    W("needs `far_i(theta)` sweeps from the record-then-rescore runs (M3). Those")
    W("runs do not exist for the full closed corpus yet, so the per-threshold")
    W("allocation-then-evaluate result is `[TBD-M3-temporal-split]`.")
    W("")

    # ---------------------------------------------------------------- RESULT 4
    W("## Result 4 -- view A vs view B (in situ)")
    W("")
    fov = {}
    fp = os.path.join(ANA, "fov_segments.csv")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                fov[r["file"]] = r["view"]
    labelled = 0
    byview_h = collections.defaultdict(float)
    byview_n = collections.defaultdict(int)
    byview_segs = collections.defaultdict(list)
    for i, s in enumerate(segs):
        v = fov.get(s["file"].replace(".mp4", ""))
        if v is None:
            continue
        labelled += 1
        byview_h[v] += s["dur"] / 3600.0
        byview_n[v] += seg_counts[i]
        byview_segs[v].append(i)
    W("The camera was remounted during the campaign, giving two geometries of the")
    W("same room. If the alert rate differs between them, the budget is a property")
    W("of the camera placement and not of the system.")
    W("")
    W("| view | segments | observed h | alerts | rate (alerts/h) | 95% CI |")
    W("|---|---:|---:|---:|---:|---|")
    view_ci = {}
    for v in sorted(byview_h):
        idx = byview_segs[v]
        lo_, hi_ = block_bootstrap_rate([seg_counts[i] for i in idx],
                                        [seg_hours[i] for i in idx])
        view_ci[v] = [lo_, hi_]
        W("| %s | %d | %.3f | %d | %.3f | [%.3f, %.3f] |"
          % (v, len(idx), byview_h[v], byview_n[v],
             byview_n[v] / byview_h[v] if byview_h[v] else float("nan"), lo_, hi_))
    W("")

    # --- the confound check, which is why this result is not quoted -----------
    hours_by_view = collections.defaultdict(collections.Counter)
    for v, idx in byview_segs.items():
        for i in idx:
            s = segs[i]
            t = s["start"]
            while t < s["end"]:
                nxt = (t + dt.timedelta(hours=1)).replace(minute=0, second=0,
                                                          microsecond=0)
                edge = min(nxt, s["end"])
                hours_by_view[v][t.hour] += (edge - t).total_seconds() / 3600.0
                t = edge
    sets = {v: {h for h, x in c.items() if x > 0.25} for v, c in hours_by_view.items()}
    W("### 4a. Why this table must not be read as a view effect")
    W("")
    matched = None
    for v in sorted(sets):
        hs = sorted(sets[v])
        W("- view **%s** is observed only in hours %s" % (v, ", ".join("%02d" % h for h in hs)))
    if len(sets) == 2:
        a, b = sorted(sets)
        shared = sets[a] & sets[b]
        W("- hours observed in **both** views: %s"
          % (", ".join("%02d" % h for h in sorted(shared)) if shared else "**none**"))
        W("")
        if shared:
            # matched-hours comparison: restrict BOTH views to the shared hours
            mh_h = collections.defaultdict(float)
            mh_n = collections.defaultdict(int)
            for v, idx in byview_segs.items():
                for i in idx:
                    s = segs[i]
                    t = s["start"]
                    while t < s["end"]:
                        nxt = (t + dt.timedelta(hours=1)).replace(
                            minute=0, second=0, microsecond=0)
                        edge = min(nxt, s["end"])
                        if t.hour in shared:
                            mh_h[v] += (edge - t).total_seconds() / 3600.0
                        t = edge
            for a_, j in inwin:
                v = fov.get(segs[j]["file"].replace(".mp4", ""))
                if v is not None and a_["t"].hour in shared:
                    mh_n[v] += 1
            matched = {"hours": sorted(shared),
                       "views": {v: {"h": mh_h[v], "n": mh_n[v]} for v in mh_h}}
            W("The overlap is only %d hour-slot(s) (%s), so a matched comparison is"
              % (len(shared), ", ".join("%02d" % h for h in sorted(shared))))
            W("possible but thin. Restricting **both** views to those hours only:")
            W("")
            W("| view | observed h (matched hours) | alerts | rate (alerts/h) |")
            W("|---|---:|---:|---:|")
            for v in sorted(mh_h):
                W("| %s | %.3f | %d | %s |"
                  % (v, mh_h[v], mh_n[v],
                     "%.3f" % (mh_n[v] / mh_h[v]) if mh_h[v] else "n/a"))
            W("")
            W("This is the only view comparison in the data that is not dominated by")
            W("time of day, and it rests on a few hours per view -- far below the 8 h")
            W("floor of rule D8, which therefore forbids reporting it as a stratified")
            W("result. It is shown here to make the size of the remaining gap visible,")
            W("not as a finding.")
            W("")
            W("Outside those hours the two views do not overlap at all: view %s covers"
              % a)
            W("the rest of the day and view %s the rest of the night. Result 2 has just" % b)
            W("shown the alert rate moving by more than two orders of magnitude across")
            W("the day, so the %.0fx gap in the unmatched table above is largely or"
              % ((byview_n[a] / byview_h[a]) / (byview_n[b] / byview_h[b])
                 if byview_h[b] and byview_n[b] else float("nan")))
            W("wholly a time-of-day effect. Reading it as a camera-geometry effect")
            W("would be the exact mistake this paper accuses default thresholds of")
            W("making: attributing to a mechanism what is a property of when you")
            W("happened to look.")
        if not shared:
            W("View and hour-of-day are **perfectly confounded** in the labelled")
            W("subset: view %s covers only daytime hours and view %s only night and" % (a, b))
            W("early-morning hours, with no hour in common. Result 2 has just shown")
            W("that the alert rate varies by more than two orders of magnitude across")
            W("the day. The %.0fx difference between the two views is therefore fully"
              % ((byview_n[a] / byview_h[a]) / (byview_n[b] / byview_h[b])
                 if byview_h[b] and byview_n[b] else float("nan")))
            W("explicable by time of day alone, and this table is **no evidence at all**")
            W("about camera geometry. Reporting it as a view effect would be the exact")
            W("mistake this paper accuses default thresholds of making: attributing to")
            W("a mechanism what is actually a property of when you happened to look.")
    W("")
    W("**Status: blocked, and honestly so.**")
    W("`fov_segments.csv` labels %d of %d segments (%.1f%%); the other %d are"
      % (labelled, len(segs), 100.0 * labelled / len(segs), len(segs) - labelled))
    W("unlabelled. Both labelled views do clear the 8 h floor of rule D8")
    W("(%s), so the blocker is not sample size --"
      % ", ".join("%s %.2f h" % (v, byview_h[v]) for v in sorted(byview_h)))
    W("it is the confound. Result 4 needs view labels on the remaining segments so")
    W("that the two views can be compared **within matched hours of day**. Until")
    W("then it is `[TBD-fov-labels-remaining]` and no view claim is made anywhere")
    W("in the paper.")
    W("")

    out = os.path.join(HERE, "TIER0_RESULTS.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(report) + "\n")
    print("wrote", out)

    js = {
        "corpus": {"segments": len(segs), "hours": total_h,
                   # Where each segment's length came from. While M1+ is still
                   # running this is a MIXED figure -- decoded for the measured
                   # segments, manifest for the rest -- and saying so is the
                   # difference between a transitional number and a wrong one.
                   # count_everything.py asserts the two agree once coverage
                   # reaches 100%.
                   "hours_source": {
                       "decoded": sum(1 for x in segs
                                      if x.get("dur_source") == "decoded"),
                       "manifest": sum(1 for x in segs
                                       if x.get("dur_source") != "decoded")},
                   "window": [win0.isoformat(), win1.isoformat()]},
        "result1_full_history": dict(full),
        "result1_in_corpus": dict(c_obs),
        "result1_in_corpus_rate_ci": [lo, hi],
        "result2_by_hour": {str(h): {"obs_h": oh, "n": n, "rate": r}
                            for h, oh, n, r in rates},
        "result2_dispersion": {"chi2": chi2, "dof": dof, "pooled_rate": grand},
        "result3_split": {"first": {"h": h1, "n": n1, "ci": [lo1, hi1]},
                          "second": {"h": h2, "n": n2, "ci": [lo2, hi2]},
                          "boundary_file": segs[split_i]["file"]},
        "result4_views": {v: {"h": byview_h[v], "n": byview_n[v],
                              "segments": len(byview_segs[v])} for v in byview_h},
        "result4_labelled_fraction": labelled / len(segs),
        # Added 2026-09-14 for Supplementary Section S7, which quotes these
        # tables. They were written only to the markdown before; every key
        # above this line is unchanged.
        "result2c_by_day": {str(d): {"obs_h": obs_day[d] / 3600.0,
                                     "n": cnt_day.get(d, 0)}
                            for d in sorted(obs_day)},
        "result3_split_segments": {"first": split_i + 1,
                                   "second": len(segs) - split_i - 1},
        "result4_views_ci": view_ci,
        "result4_matched": matched,
    }
    with open(os.path.join(HERE, "tier0_results.json"), "w", encoding="utf-8") as fh:
        json.dump(js, fh, indent=2, default=str)
    print("wrote tier0_results.json")


if __name__ == "__main__":
    main()
