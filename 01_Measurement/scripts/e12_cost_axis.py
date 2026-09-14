#!/usr/bin/env python3
"""E12 — the three candidate in-situ cost axes for the FallChecker front.

RUN ONLY AFTER `PREREGISTERED_E12_COST_AXIS.md` IS HASHED. The registration
fixes the reporting rule before these numbers exist; this script is step 2 of
its section 5 and reports whichever branch the numbers fall in.

There are three axes, not two, and the registration's fourth fact is the reason:

  1. REGISTERED (C1 -> C2 rescore, 24 segments, recorded theta 0.30).
     E7 section 3's tie-break selects this pass. Its curve is
     `out/c2_rescore/sweep_curve.json`.
  2. FALLBACK IN USE (V1/V2/V3, 8 segments). What `theta_vs_lambda.py` actually
     prices on, by its own source comment. Not registered as the axis.
  3. A1 (175 segments, 83.9626 h). Exact at three grid points by
     PREREGISTERED_E7B_AMENDMENT 2b; cannot reach 0.30 or 0.375.

The statistics are the same for every axis that has numbers, so that no axis is
flattered by a method the others did not get: the per-segment breakdown, a
Poisson interval that assumes exchangeable events, and a SEGMENT BLOCK bootstrap
that does not. Where the two intervals disagree, the disagreement is the point.

Standard library only. Reads; writes one JSON.
"""
import argparse
import io
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.dirname(HERE)
OUT = os.path.join(MEAS, "analysis", "e12", "E12_COST_AXIS.json")
A1_TABLE = os.path.join(MEAS, "analysis", "e12", "A1_FALL_BY_SEGMENT.json")
C2_CURVE = os.path.join(MEAS, "runs", "c2", "sweep_curve.json")
V_PROV = os.path.join(MEAS, "analysis", "FALL_FRONT_PROVENANCE.json")

SEED = 20260911
REPLICATES = 20000

# Coverage is the ex-situ axis and is unchanged by E12. Quoted here only so the
# front can be printed as a front; source exsitu/RECALL_L_X4.json, extended
# mapping at the protocol window L = W = 2.0 s.
COVERAGE = {"0.3": 0.6282, "0.375": 0.4872, "0.45": 0.2436,
            "0.525": 0.1154, "0.6": 0.0128}
COVERAGE_CI = {"0.3": (0.5173, 0.7271), "0.375": (0.3795, 0.5961),
               "0.45": (0.1619, 0.3494), "0.525": (0.0619, 0.2050),
               "0.6": (0.0023, 0.0691)}


# ---------------------------------------------------------------- statistics
def norm_inv(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    pl, ph = 0.02425, 1 - 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > ph:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def chi2_inv(p, df):
    if df <= 0:
        return 0.0
    z = norm_inv(p)
    return df * (1.0 - 2.0 / (9.0 * df) + z * math.sqrt(2.0 / (9.0 * df))) ** 3


def poisson_ci(k, hours):
    """The interval a homogeneous reading gives. Printed as a foil."""
    if hours <= 0:
        return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else 0.5 * chi2_inv(0.025, 2 * k) / hours
    return (lo, 0.5 * chi2_inv(0.975, 2 * (k + 1)) / hours)


def block_bootstrap(pairs, reps=REPLICATES, seed=SEED):
    """Resample SEGMENTS. The segment is the unit the sample was drawn in."""
    if not pairs:
        return (float("nan"), float("nan"), float("nan"))
    rnd = random.Random(seed)
    n = len(pairs)
    rates = []
    for _ in range(reps):
        pick = [pairs[rnd.randrange(n)] for _ in range(n)]
        H = sum(h for h, _k in pick)
        if H > 0:
            rates.append(sum(k for _h, k in pick) / H)
    if not rates:
        return (float("nan"), float("nan"), float("nan"))
    rates.sort()
    return (rates[int(0.025 * len(rates))],
            rates[min(len(rates) - 1, int(0.975 * len(rates)))],
            sum(1 for r in rates if r == 0.0) / float(len(rates)))


def describe(pairs):
    H = sum(h for h, _k in pairs)
    K = sum(k for _h, k in pairs)
    carriers = [(h, k) for h, k in pairs if k]
    plo, phi = poisson_ci(K, H)
    blo, bhi, pz = block_bootstrap(pairs)
    top = max((k for _h, k in pairs), default=0)
    return {
        "segments": len(pairs), "hours": H, "alerts": K,
        "rate_per_h": (K / H) if H else float("nan"),
        "segments_carrying_alerts": len(carriers),
        "largest_single_segment_share": (top / K) if K else 0.0,
        "poisson_ci95": [plo, phi],
        "block_bootstrap_ci95": [blo, bhi],
        "bootstrap_fraction_exactly_zero": pz,
    }


# ------------------------------------------------------------------ the axes
def axis_registered():
    """C1 -> C2. Reported even if it is empty, because empty IS the finding."""
    if not os.path.exists(C2_CURVE):
        return {"status": "artefact missing", "path": C2_CURVE}
    d = json.load(io.open(C2_CURVE, encoding="utf-8"))
    rg = d.get("reproduction_gate", {})
    fall = (rg.get("per_checker") or {}).get("FallChecker", {})
    return {
        "pass": "C1 -> C2 rescore",
        "selected_by": "E7 section 3 tie-break: lowest recorded theta",
        "roster_segments": len(d.get("roster") or []),
        "recorded_theta": (d.get("pass_config") or {}).get("conf_threshold"),
        "points_emitted": len(d.get("points") or []),
        "reproduction_gate_fallchecker": fall,
        "usable": bool(d.get("points")),
    }


def axis_v():
    if not os.path.exists(V_PROV):
        return {"status": "artefact missing", "path": V_PROV}
    d = json.load(io.open(V_PROV, encoding="utf-8"))
    out = {"pass": "V1/V2/V3", "note": "unregistered fallback actually priced on",
           "points": {}}
    for key, p in (d.get("points") or {}).items():
        pairs = [(v["hours"], v["alerts"]) for v in p["per_segment"].values()]
        st = describe(pairs)
        st["theta"] = p["theta"]
        st["substituted_alerts"] = p.get("substituted_alerts")
        out["points"][key] = st
    return out


def axis_a1():
    if not os.path.exists(A1_TABLE):
        return {"status": "artefact missing", "path": A1_TABLE}
    d = json.load(io.open(A1_TABLE, encoding="utf-8"))
    segs = d["segments"]
    out = {"pass": "A1", "exact_by": "PREREGISTERED_E7B_AMENDMENT 2b",
           "points": {}, "unreachable": {}}
    for t in ("0.3", "0.375"):
        out["unreachable"][t] = ("below A1's recorded threshold 0.45; the "
                                 "alerts that would price it were never written")
    for t in d["grid"]:
        key = "%g" % t
        pairs = [(v["hours"], v["alerts"][key]) for v in segs.values()]
        st = describe(pairs)
        st["theta"] = t
        st["substituted_alerts"] = sum(
            v["alerts"][key] for v in segs.values() if v["substituted_clock"])
        out["points"][key] = st
    return out


# ----------------------------------------------------------------- reporting
def line(key, st):
    return ("  theta=%-6s %4d alert / %8.4f h = %7.4f /h | carriers %3d/%-3d "
            "| top %5.1f%% | Poisson [%6.3f,%7.3f] | bootstrap [%6.3f,%7.3f] "
            "| P(0)=%4.1f%%"
            % (key, st["alerts"], st["hours"], st["rate_per_h"],
               st["segments_carrying_alerts"], st["segments"],
               100 * st["largest_single_segment_share"],
               st["poisson_ci95"][0], st["poisson_ci95"][1],
               st["block_bootstrap_ci95"][0], st["block_bootstrap_ci95"][1],
               100 * st["bootstrap_fraction_exactly_zero"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    reg, v, a1 = axis_registered(), axis_v(), axis_a1()

    print("=" * 78)
    print("E12 -- the in-situ cost axis of the Fall front. THREE candidates.")
    print("=" * 78)

    print()
    print("AXIS 1 -- REGISTERED (%s), selected by %s"
          % (reg.get("pass"), reg.get("selected_by")))
    if reg.get("usable"):
        print("  usable: yes")
    else:
        fall = reg.get("reproduction_gate_fallchecker", {})
        print("  roster %s segments, recorded conf %s"
              % (reg.get("roster_segments"), reg.get("recorded_theta")))
        print("  POINTS EMITTED: %s   <-- the registered axis is EMPTY"
              % reg.get("points_emitted"))
        print("  reproduction gate, FallChecker: %s" % fall)
        print("  => record-then-rescore did not reproduce ANY of the %s live"
              % fall.get("real"))
        print("     Fall alerts on replay (%s), verdict '%s'. Rescoring upward"
              % (fall.get("replay"), fall.get("verdict")))
        print("     is not valid for this checker on this pass, so the pass the")
        print("     registered rule selects cannot price the front at all.")

    print()
    print("AXIS 2 -- FALLBACK ACTUALLY IN USE (%s). %s" % (v.get("pass"), v.get("note")))
    for key in sorted(v.get("points", {}), key=lambda k: v["points"][k]["theta"]):
        print(line(key, v["points"][key]))

    print()
    print("AXIS 3 -- A1, exact at three grid points (%s)" % a1.get("exact_by"))
    for key in sorted(a1.get("points", {}), key=lambda k: a1["points"][k]["theta"]):
        print(line(key, a1["points"][key]))
    for t, why in sorted(a1.get("unreachable", {}).items()):
        print("  theta=%-6s UNREACHABLE -- %s" % (t, why))

    payload = {"seed": SEED, "replicates": REPLICATES,
               "registration": "PREREGISTERED_E12_COST_AXIS.md",
               "coverage_extended_L2": COVERAGE,
               "coverage_wilson95": {k: list(v) for k, v in COVERAGE_CI.items()},
               "axis_registered_c1": reg, "axis_fallback_v": v, "axis_a1": a1}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with io.open(a.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    print()
    print("wrote %s" % a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
