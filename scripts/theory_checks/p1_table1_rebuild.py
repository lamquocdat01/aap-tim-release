#!/usr/bin/env python3
r"""P1 check -- rebuild Table I from the raw per-segment rows, independently.

Recomputes, from runs/m1/<seg>.json (observation clock) and <seg>.csv (one row
per dispatched alert), every number in Table I of FREEZE_TIM_v5: observation
hours, per-checker pooled rate, the segment block-bootstrap interval
(random.Random(20260905), 10 000 replicates, segments in substituted-then-
native order -- the E4 registration) and the zero-count Poisson limit. Then
compares each with generated_counts.json. Tolerance: 0.00005 (the 4 dp the
table prints); hours to 0.0000 h.

Adds what P1 needs beyond Table I: the intrusion FAR as rate x FP fraction,
with a Bonferroni-joint interval, and the one- vs two-sided zero-count limits.
"""
import math
import random
import sys

import _common as C

SEED_E4 = 20260905
ITERS_E4 = 10000
TOL = 0.00005


def block_bootstrap(counts, hours, seed=SEED_E4, iters=ITERS_E4, q=(0.025, 0.975)):
    rng = random.Random(seed)
    n = len(counts)
    idx = range(n)
    out = []
    for _ in range(iters):
        pick = [rng.choice(idx) for _ in range(n)]
        h = sum(hours[i] for i in pick)
        if h > 0:
            out.append(sum(counts[i] for i in pick) / h)
    out.sort()
    return tuple(out[int(x * len(out))] if x < 1 else out[-1] for x in q)


def main():
    cnt = C.counts()
    ins = C.load_insitu()
    order = ins["order"]
    H = sum(ins["hours"][s] for s in order)
    hours = [ins["hours"][s] for s in order]
    missing = [s for s in order if ins["per_seg"][s] is None]
    rows, fails = [], []

    def check(name, mine, theirs, tol=TOL):
        ok = theirs is not None and abs(mine - float(theirs)) <= tol
        rows.append({"quantity": name, "rebuilt": round(mine, 6), "generated_counts": theirs,
                     "abs_diff": None if theirs is None else round(abs(mine - float(theirs)), 6),
                     "ok": ok})
        if not ok:
            fails.append(name)

    check("segments", len(order), cnt["far_pooled_n"], tol=0)
    check("pooled hours", H, cnt["far_pooled_hours"])
    check("insitu hours (corpus table)", H, cnt["insitu_hours"])
    check("zero-count upper limit (two-sided 95 %)", C.POISSON_2S_95_ZERO / H,
          cnt["far_pooled_zero_count_upper_limit"])

    table = {}
    for ck in ("IntrusionChecker", "HelmetChecker", "FallChecker", "SmokeFireChecker",
               "RunningChecker", "EnhancedHelmetChecker", "ForkliftSpeedChecker"):
        key = ck.lower()
        k = [ins["per_seg"][s].get(ck, 0) for s in order]
        K = sum(k)
        check("%s alerts" % ck, K, cnt["far_%s_pooled_alerts" % key], tol=0)
        check("%s rate" % ck, K / H, cnt["far_%s_pooled_rate" % key])
        ent = {"alerts": K, "rate": K / H, "measured": ck in ins["measured"],
               "deployed_alerts": cnt.get("far_deployed_%s_alerts" % key),
               "deployed_rate": cnt.get("far_deployed_%s_rate" % key)}
        if ent["deployed_alerts"] is not None:
            check("%s deployed rate" % ck, ent["deployed_alerts"] / H, ent["deployed_rate"])
        if ck not in ins["measured"]:
            ent["interval"] = None
            ent["zero_kind"] = "Z1: not instantiated -- no rate, no bound"
        elif K == 0:
            ent["interval"] = [0.0, C.POISSON_2S_95_ZERO / H]
            ent["interval_one_sided_rule_of_three"] = C.POISSON_1S_95_ZERO / H
            ent["zero_kind"] = "Z2: instantiated, 0 alerts -- Poisson bound"
            check("%s CI hi" % ck, ent["interval"][1], cnt["far_%s_pooled_ci_hi" % key])
        else:
            lo, hi = block_bootstrap(k, hours)
            ent["interval"] = [lo, hi]
            check("%s CI lo" % ck, lo, cnt["far_%s_pooled_ci_lo" % key])
            check("%s CI hi" % ck, hi, cnt["far_%s_pooled_ci_hi" % key])
        table[ck] = ent

    # P1(b): intrusion events occurred, so FAR = alert rate x FP fraction.
    n_lab = 100                                     # label_cells_members: intrusion 100
    k_fp = round(float(cnt["intrusion_fp_fraction"]) * n_lab)
    w95 = C.wilson(k_fp, n_lab)
    check("intrusion FP fraction Wilson hi", w95[1], cnt["intrusion_fp_fraction_ci_hi"])
    k_int = [ins["per_seg"][s].get("IntrusionChecker", 0) for s in order]
    lo975, hi975 = block_bootstrap(k_int, hours, q=(0.0125, 0.9875))
    w975 = C.wilson(k_fp, n_lab, z=2.241402727604947)
    # The FP fraction was labelled on PRODUCTION (deployed) alerts
    # (analysis/INTRUSION_FAR.json: "drawn from production alerts of 2026-09-02"),
    # so the false-alarm rate it licenses is the DEPLOYED rate x fraction. The
    # replay-based figures below are kept for the record and are NOT printed (P3b).
    dep = C.deployed_per_segment(order, ins["hours"])
    k_dep = [dep[s].get("intrusion", 0) for s in order]
    assert sum(k_dep) == cnt["far_deployed_intrusionchecker_alerts"], (sum(k_dep), cnt["far_deployed_intrusionchecker_alerts"])
    dlo95, dhi95 = block_bootstrap(k_dep, hours)
    dlo975, dhi975 = block_bootstrap(k_dep, hours, q=(0.0125, 0.9875))
    dep_far = {
        "deployed_alerts": sum(k_dep), "deployed_rate": sum(k_dep) / H,
        "deployed_rate_ci95": [dlo95, dhi95], "deployed_rate_ci97_5": [dlo975, dhi975],
        "far_point": sum(k_dep) / H * k_fp / n_lab,
        "far_upper_product_of_95": dhi95 * w95[1],
        "far_upper_joint95_bonferroni": dhi975 * w975[1],
        "v5_printed_upper": float(cnt.get("intrusion_far_upper", "nan")),
        "v5_method": "deployed-rate 95 % upper (block bootstrap, seed 20260910) x Wilson 95 % upper: joint coverage >= 90 % only",
    }
    intr = {
        "deployed_basis": dep_far,
        "fp_labelled": n_lab, "fp_count": k_fp, "fp_fraction": k_fp / n_lab,
        "fp_wilson95": list(w95), "fp_wilson97_5": list(w975),
        "far_point": table["IntrusionChecker"]["rate"] * k_fp / n_lab,
        "far_upper_product_of_95": table["IntrusionChecker"]["interval"][1] * w95[1],
        "far_upper_joint95_bonferroni": hi975 * w975[1],
        "rate_bootstrap_97_5": [lo975, hi975],
        "note": ("Product of two 95 % upper limits covers jointly at >= 90 %; the "
                 "Bonferroni version uses 97.5 % components and covers at >= 95 %."),
    }

    out = {
        "check": "P1 Table I rebuild", "segments": len(order), "hours": H,
        "substituted_segments": ins["n_sub"], "native_segments": ins["n_nat"],
        "segments_without_csv": missing, "table": table, "intrusion_far": intr,
        "comparisons": rows, "fails": fails, "verdict": "MATCH" if not fails else "MISMATCH",
        "zero_count_conventions": {
            "two_sided_95": C.POISSON_2S_95_ZERO / H,
            "one_sided_95_rule_of_three": C.POISSON_1S_95_ZERO / H,
            "literal_3_over_T": 3.0 / H},
        "provenance": C.provenance([C.COUNTS, C.CORRECTIONS]),
    }
    C.dump("p1_table1_rebuild.json", out)
    print("P1 Table I rebuild: %s (%d comparisons, %d fail) over %d segments / %.4f h"
          % (out["verdict"], len(rows), len(fails), len(order), H))
    for r in rows:
        if not r["ok"]:
            print("  FAIL", r)
    print("  zero-count limit: two-sided %.4f /h, rule-of-three %.4f /h, 3/T %.4f /h"
          % (out["zero_count_conventions"]["two_sided_95"],
             out["zero_count_conventions"]["one_sided_95_rule_of_three"], 3.0 / H))
    print("  intrusion FAR: point %.4f, upper %.4f (>=90%% joint) / %.4f (>=95%% joint)"
          % (intr["far_point"], intr["far_upper_product_of_95"], intr["far_upper_joint95_bonferroni"]))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
