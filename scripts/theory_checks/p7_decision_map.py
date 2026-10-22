#!/usr/bin/env python3
r"""P7 check -- guarded acceptance on interval-valued FAR and coverage.

JCGM 106:2012 8.3.2: an acceptance limit inside the tolerance interval;
w = T_U - A_U > 0. For FAR (upper tolerance limit = alert budget B) the rule
"accept iff the upper 95 % limit U_FAR <= B" is guarded acceptance with
w equal to the upper half-width of the interval. For site coverage (lower
tolerance limit c*) under partial identification the rule is "accept iff the
lower edge of the confidence set for the identified set >= c*", reject iff
its upper edge < c*, otherwise INDETERMINATE (non-binary statement, ILAC-G8).

Per Fall operating point this prints the smallest budget each theta can be
accepted under, and the largest coverage requirement it can be accepted
under. FAR intervals: E12 axis A1 (one estimator for every theta, seed
20260911). theta < 0.45 has no FAR from A1: alerts below the recorded
threshold were never written, so FAR there is not identified FROM THIS
RECORD -- the recording design, not the statistics, is the limit.
"""
import io
import json
import sys

import _common as C


def main():
    e = json.load(io.open(C.E12, encoding="utf-8"))
    p3 = json.load(io.open(C.OUTDIR + "/p3_identified_set.json", encoding="utf-8"))
    rows = []
    cnt = C.counts()
    for th, r in sorted(p3["by_theta"].items(), key=lambda kv: float(kv[0])):
        pt = e["axis_a1"]["points"].get("%g" % float(th))
        far = None if pt is None else {"rate": pt["rate_per_h"], "ci95": pt["block_bootstrap_ci95"],
                                       "alerts": pt["alerts"], "hours": pt["hours"], "source": "E12 axis A1"}
        if far is not None and abs(float(th) - 0.45) < 1e-9:
            # KI-alpha1: one interval per quantity. At the deployed default the
            # printed interval is Table I's (generated_counts.json, E4 seed).
            far["ci95"] = [float(cnt["far_fallchecker_pooled_ci_lo"]), float(cnt["far_fallchecker_pooled_ci_hi"])]
            far["source"] = "Table I (generated_counts far_fallchecker_pooled_ci, KI-alpha1)"
        rows.append({"theta": float(th),
                     "far": far,
                     "far_status": "identified (A1)" if far else
                                   "not identified from the A1 record (below recorded threshold 0.45)",
                     "min_budget_accepted": None if far is None else far["ci95"][1],
                     "guard_band_w": None if far is None else far["ci95"][1] - far["rate"],
                     "cov_CS95": r["CS95"],
                     "max_requirement_accepted": r["CS95"][0],
                     "requirements_indeterminate": [r["CS95"][0], r["CS95"][1]],
                     "min_requirement_rejected_above": r["CS95"][1]})

    def decide(B, cstar):
        out = []
        for r in rows:
            if r["far"] is None:
                f = "FAR not identified"
            else:
                f = "accept" if r["far"]["ci95"][1] <= B else (
                    "reject" if r["far"]["ci95"][0] > B else "indeterminate")
            lo, hi = r["cov_CS95"]
            c = "accept" if lo >= cstar else ("reject" if hi < cstar else "indeterminate")
            out.append({"theta": r["theta"], "far": f, "coverage": c})
        return out

    examples = {"B=1.0/h, c*=0.05": decide(1.0, 0.05), "B=0.5240/h (v5 demonstration), c*=0.10": decide(0.524, 0.10),
                "B=2.0/h, c*=0.01": decide(2.0, 0.01)}
    out = {"check": "P7 decision map", "rule": "JCGM 106:2012 8.3.2 guarded acceptance; 3.3.11 guard band",
           "rows": rows, "examples": examples, "provenance": C.provenance([C.E12, C.COUNTS])}
    C.dump("p7_decision_map.json", out)
    print("P7 decision map (guarded acceptance)")
    for r in rows:
        if r["far"]:
            print("  theta %.3f FAR %.4f [%.4f, %.4f] -> accept iff B >= %.4f (w = %.4f) | coverage CS95 "
                  "[%.4f, %.4f] -> accept iff c* <= %.4f, reject iff c* > %.4f" % (
                      r["theta"], r["far"]["rate"], r["far"]["ci95"][0], r["far"]["ci95"][1],
                      r["min_budget_accepted"], r["guard_band_w"], r["cov_CS95"][0], r["cov_CS95"][1],
                      r["max_requirement_accepted"], r["min_requirement_rejected_above"]))
        else:
            print("  theta %.3f FAR: %s | coverage CS95 [%.4f, %.4f]" % (
                r["theta"], r["far_status"], r["cov_CS95"][0], r["cov_CS95"][1]))
    for k, v in examples.items():
        print("  %-40s %s" % (k, "; ".join("%.3f: %s/%s" % (d["theta"], d["far"], d["coverage"]) for d in v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
