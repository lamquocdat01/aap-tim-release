#!/usr/bin/env python3
r"""P3 check -- the identified set of site coverage under a declared rho-band.

For each Fall operating point theta with an ex-situ coverage COV_B (GMDCSA24,
78 events, extended mapping L = W = 2 s, Wilson 95 %) and the declared band
rho in [rho_lo, rho_hi] (OmniFall Table 2, seven staged sources):

  H(theta)    = [rho_lo * COV_B, min(1, rho_hi * COV_B)]     population identified set
  H_hat       = same with the point estimate                  plug-in estimate
  CS95(theta) = [rho_lo * L, min(1, rho_hi * U)]              >= 95 % confidence set for H

CS95 covers H whenever [L, U] covers COV_B (monotonicity of the map), hence
with probability >= 0.95. It is NOT the identified set; the 22-10 draft
called it that. Also prints the nested-band sequence (law of decreasing
credibility) at the demonstration point.
"""
import io
import json
import sys

import _common as C


def main():
    e = json.load(io.open(C.E12, encoding="utf-8"))
    cnt = C.counts()
    rho_lo, rho_hi = float(cnt["rho_min"]), float(cnt["rho_max"])
    n_gt = int(cnt["exsitu_gmdcsa24_native_extended_gt"])
    rows = {}
    for th, cov in sorted(e["coverage_extended_L2"].items(), key=lambda kv: float(kv[0])):
        L, U = e["coverage_wilson95"][th]
        k = round(cov * n_gt)
        wl, wu = C.wilson(k, n_gt)
        rows[th] = {
            "theta": float(th), "cov_B": cov, "k_over_n": "%d/%d" % (k, n_gt),
            "wilson95": [L, U], "wilson95_recomputed": [round(wl, 4), round(wu, 4)],
            "wilson_match": abs(wl - L) < 5e-5 and abs(wu - U) < 5e-5,
            "H_plugin": [rho_lo * cov, min(1.0, rho_hi * cov)],
            "CS95": [rho_lo * L, min(1.0, rho_hi * U)],
            "no_assumption": [0.0, 1.0],
        }
    demo = rows["0.525"]
    nested = []
    central = float(cnt["rho_central"])
    for lo, hi, label in ((central, central, "point (rho = GMDCSA24 row)"),
                          (float(cnt["rho_median"]), central, "inner (median..central)"),
                          (rho_lo, rho_hi, "registered band"),
                          (0.0, 1.0, "rho <= 1 only"),
                          (0.0, float("inf"), "no assumption")):
        cs = [lo * demo["wilson95"][0], min(1.0, hi * demo["wilson95"][1])]
        nested.append({"band": [lo, hi if hi != float("inf") else "inf"], "label": label,
                       "CS95": cs, "width": cs[1] - cs[0]})
    widths = [n["width"] for n in nested]
    out = {"check": "P3 identified set", "rho_band": [rho_lo, rho_hi],
           "rho_source": cnt["rho_source"], "n_events_B": n_gt, "by_theta": rows,
           "demo_theta": "0.525", "demo": demo, "nested_bands_demo": nested,
           "monotone_in_band": all(widths[i] <= widths[i + 1] + 1e-12 for i in range(len(widths) - 1)),
           "expected_CS95_demo": [0.0050, 0.1164],
           "matches_expected": (round(demo["CS95"][0], 4) == 0.0050 and round(demo["CS95"][1], 4) == 0.1164),
           "provenance": C.provenance([C.E12, C.COUNTS])}
    out["verdict"] = "MATCH" if out["matches_expected"] and all(r["wilson_match"] for r in rows.values()) \
        and out["monotone_in_band"] else "MISMATCH"
    C.dump("p3_identified_set.json", out)
    print("P3 identified set: %s" % out["verdict"])
    for th, r in rows.items():
        print("  theta %-5s COV_B %.4f (%s) Wilson [%.4f, %.4f] | H_plugin [%.4f, %.4f] | CS95 [%.4f, %.4f]"
              % (th, r["cov_B"], r["k_over_n"], r["wilson95"][0], r["wilson95"][1],
                 r["H_plugin"][0], r["H_plugin"][1], r["CS95"][0], r["CS95"][1]))
    for n in nested:
        print("  nested %-28s CS95 [%.4f, %.4f] width %.4f" % (n["label"], n["CS95"][0], n["CS95"][1], n["width"]))
    return 0 if out["verdict"] == "MATCH" else 1


if __name__ == "__main__":
    sys.exit(main())
