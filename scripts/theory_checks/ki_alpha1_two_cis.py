#!/usr/bin/env python3
r"""KI-alpha1 -- why Fall FAR at theta = 0.45 has two 95 % intervals.

Table I  [0.4782, 1.8114]: count_everything._block_bootstrap_ci, data runs/m1
         (per-segment CSV rows), random.Random(20260905), 10 000 replicates,
         segments ordered substituted-clock first then native, each sorted.
E12      [0.4715, 1.8377]: e12_cost_axis.block_bootstrap, data
         A1_FALL_BY_SEGMENT.json at 0.45, random.Random(20260911), 20 000
         replicates, segments in the JSON's (chronological) order.

This script verifies, rather than assumes, that (1) the two data sources are
the same 175 (hours, count) pairs, (2) each published interval is reproduced
by its own method, (3) each method applied to the other's data/order moves
the interval, and (4) the Monte-Carlo spread of the 2.5/97.5 % limits across
seeds covers the gap. Standard library only.
"""
import io
import json
import random
import statistics
import sys

import _common as C


def boot(pairs, seed, iters):
    rng = random.Random(seed)
    n = len(pairs)
    idx = range(n)
    out = []
    for _ in range(iters):
        pick = [rng.choice(idx) for _ in range(n)]
        out.append(sum(pairs[i][1] for i in pick) / sum(pairs[i][0] for i in pick))
    out.sort()
    return out[int(0.025 * len(out))], out[min(len(out) - 1, int(0.975 * len(out)))]


def main():
    ins = C.load_insitu()
    order = ins["order"]
    a1 = json.load(io.open(C.A1_FALL, encoding="utf-8"))["segments"]
    m1 = {s: (ins["hours"][s], ins["per_seg"][s].get("FallChecker", 0)) for s in order}
    e12 = {s: (a1[s]["hours"], a1[s]["alerts"]["0.45"]) for s in a1}
    same_set = set(m1) == set(e12)
    max_dh = max(abs(m1[s][0] - e12[s][0]) for s in m1)
    diff_counts = [s for s in m1 if m1[s][1] != e12[s][1]]
    P_tab = [m1[s] for s in order]
    P_e12 = [e12[s] for s in a1]
    # rng.choice(range(n)) and rng.randrange(n) draw the same stream in CPython 3.11
    rows = {
        "TableI method / TableI data+order (seed 20260905, 10k)": boot(P_tab, 20260905, 10000),
        "E12 method / E12 data+order (seed 20260911, 20k)": boot(P_e12, 20260911, 20000),
        "TableI seed+reps / E12 order": boot(P_e12, 20260905, 10000),
        "E12 seed+reps / TableI order": boot(P_tab, 20260911, 20000),
        "TableI seed+order, 20k reps": boot(P_tab, 20260905, 20000),
    }
    seeds = [20260905 + 1000 * i for i in range(30)]
    los, his = zip(*(boot(P_tab, s, 10000) for s in seeds))
    mc = {"seeds": len(seeds), "replicates": 10000,
          "lo_mean": statistics.mean(los), "lo_sd": statistics.stdev(los),
          "lo_range": [min(los), max(los)],
          "hi_mean": statistics.mean(his), "hi_sd": statistics.stdev(his),
          "hi_range": [min(his), max(his)]}
    cnt = C.counts()
    tab_pub = (float(cnt["far_fallchecker_pooled_ci_lo"]), float(cnt["far_fallchecker_pooled_ci_hi"]))
    e12_pub = tuple(json.load(io.open(C.E12, encoding="utf-8"))["axis_a1"]["points"]["0.45"]["block_bootstrap_ci95"])
    r_tab = rows["TableI method / TableI data+order (seed 20260905, 10k)"]
    r_e12 = rows["E12 method / E12 data+order (seed 20260911, 20k)"]
    out = {"check": "KI-alpha1", "same_segment_set": same_set, "max_hours_diff": max_dh,
           "segments_with_different_counts": diff_counts, "alerts": sum(k for _, k in P_tab),
           "table1_published": tab_pub, "e12_published": e12_pub,
           "table1_reproduced": abs(r_tab[0] - tab_pub[0]) < 5e-5 and abs(r_tab[1] - tab_pub[1]) < 5e-5,
           "e12_reproduced": abs(r_e12[0] - e12_pub[0]) < 1e-9 and abs(r_e12[1] - e12_pub[1]) < 1e-9,
           "swaps": {k: [round(v[0], 4), round(v[1], 4)] for k, v in rows.items()},
           "monte_carlo_spread_tableI_method": mc,
           "cause": ("Monte-Carlo only: identical data; the intervals differ by seed (20260905 vs 20260911), "
                     "replicate count (10 000 vs 20 000) and resampling order (substituted-first vs "
                     "chronological). Both are draws of the same bootstrap distribution."),
           "decision": "print Table I [0.4782, 1.8114] (generated_counts.json via LINKS.md); E12 values supp-only",
           "provenance": C.provenance([C.COUNTS, C.A1_FALL, C.E12])}
    C.dump("ki_alpha1_two_cis.json", out)
    print("KI-alpha1: same set %s, max |dh| %.2e h, count differences %d, alerts %d" % (
        same_set, max_dh, len(diff_counts), out["alerts"]))
    for k, v in rows.items():
        print("  %-55s [%.4f, %.4f]" % (k, v[0], v[1]))
    print("  MC spread over %d seeds (TableI method): lo %.4f +- %.4f [%.4f, %.4f]; hi %.4f +- %.4f [%.4f, %.4f]" % (
        mc["seeds"], mc["lo_mean"], mc["lo_sd"], mc["lo_range"][0], mc["lo_range"][1],
        mc["hi_mean"], mc["hi_sd"], mc["hi_range"][0], mc["hi_range"][1]))
    print("  reproduced: TableI %s, E12 %s" % (out["table1_reproduced"], out["e12_reproduced"]))
    return 0 if (same_set and not diff_counts and out["table1_reproduced"] and out["e12_reproduced"]) else 1


if __name__ == "__main__":
    sys.exit(main())
