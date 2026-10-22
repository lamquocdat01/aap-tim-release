#!/usr/bin/env python3
r"""P6 check -- a confidence interval is not a prediction interval.

Exactly the computation of the 22-10 check, now pinned:
  rng = numpy.random.default_rng(20260911)
  1. corpus CI: 20 000 x 175 segment indices drawn with replacement in one
     call (rng.integers), rate = sum(alerts)/sum(hours), 2.5/97.5 % quantiles;
  2. PI for a random 8-segment sample: then, on the SAME generator, 20 000
     draws of rng.choice(175, 8, replace=False); 2.5/97.5 % quantiles;
     P(rate >= 1.7538) and P(rate = 0);
  3. the A1 rate on the 8 verification segments (verify_sample_4h.list).
Data: A1_FALL_BY_SEGMENT.json at theta = 0.525.

Expected (22-10): CI [0.254, 0.841], PI [0, 2.281], 6.1 %, 45.9 %, 1.503 /h.
Any deviation at the printed precision => exit 2 and STOP (prompt 4.8).
"""
import io
import os
import json
import sys

import numpy as np

import _common as C

SEED = 20260911
REPS = 20000
THETA = "0.525"
OBSERVED = 1.7538
EXPECTED = {"ci": (0.254, 0.841), "pi": (0.0, 2.281), "p_ge": 6.1, "p0": 45.9, "a1_verify": 1.503}


def half_up(x, nd):
    """The 22-10 note printed P(rate >= 1.7538) = 1210/20000 = 6.05 % as 6.1 %:
    round-half-up, not Python's round-half-even on a binary float. Explicit."""
    from decimal import Decimal, ROUND_HALF_UP
    return float(Decimal(repr(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def stratified():
    """PI under the REGISTERED verification design (P2a.1).

    The verification sample was not a simple random sample: draw_sweep_samples.py
    took 24 sweep segments (seed 20260902), then 8 verification segments from the
    remaining 151 with quotas per cell view x day/night x occupancy(ai_frames==0)
    (seed 20260903). The registered rule has no clock stratum. Two universes:
      conditional   -- sweep fixed as realised; each replicate redraws the 8 from
                       the 151 with the registered quotas (the PI for the sample
                       as actually designed);
      unconditional -- each replicate redraws sweep AND verification with the
                       registered allocation (design-level variability).
    numpy default_rng(20260911), 20 000 replicates each, fresh generator per universe.
    """
    a1 = json.load(io.open(C.A1_FALL, encoding="utf-8"))["segments"]
    reg = C.registered_draw()
    hk = {s: (a1[s]["hours"], a1[s]["alerts"][THETA]) for s in a1}
    res = {}
    # conditional on the realised sweep
    rng = np.random.default_rng(SEED)
    cells = sorted(reg["verify_cells"])
    arrs = {c: (np.array([hk[s][0] for s in reg["verify_cells"][c]]),
                np.array([hk[s][1] for s in reg["verify_cells"][c]])) for c in cells}
    rates = np.empty(REPS)
    for i in range(REPS):
        h = k = 0.0
        for c in cells:
            q = reg["verify_quota"].get(c, 0)
            if q:
                j = rng.choice(len(arrs[c][0]), q, replace=False)
                h += arrs[c][0][j].sum()
                k += arrs[c][1][j].sum()
        rates[i] = k / h
    res["conditional"] = rates
    # unconditional: redraw the sweep too (allocation recomputed by the registered rule)
    D = reg["D"]
    pool = reg["pool"]
    rng = np.random.default_rng(SEED)
    cells_all = {}
    for s in pool:
        cells_all.setdefault(s["cell"], []).append(s)
    q_s = D.allocate(cells_all, D.N_SWEEP)
    rates_u = np.empty(REPS)
    for i in range(REPS):
        taken = set()
        for c in sorted(cells_all):
            segs = sorted(cells_all[c], key=lambda s: s["seg"])
            if q_s.get(c, 0):
                for j in rng.choice(len(segs), q_s[c], replace=False):
                    taken.add(segs[j]["seg"])
        rest = {}
        for s in pool:
            if s["seg"] not in taken:
                rest.setdefault(s["cell"], []).append(s)
        q_v = D.allocate(rest, D.N_VERIFY)
        h = k = 0.0
        for c in sorted(rest):
            segs = sorted(rest[c], key=lambda s: s["seg"])
            if q_v.get(c, 0):
                for j in rng.choice(len(segs), q_v[c], replace=False):
                    h += hk[segs[j]["seg"]][0]
                    k += hk[segs[j]["seg"]][1]
        rates_u[i] = k / h
    res["unconditional"] = rates_u
    out = {"check": "P6 stratified PI", "seed": SEED, "replicates": REPS, "theta": float(THETA),
           "registered_rule": json.load(io.open(C.VERIFY_META, encoding="utf-8"))["rule"],
           "strata": "view x daynight x occupancy(ai_frames==0); no clock stratum in the registered rule",
           "draw_reproduced": True, "verify_quota": reg["verify_quota"],
           "verify_cell_sizes": {c: len(v) for c, v in reg["verify_cells"].items()},
           "observed": OBSERVED, "universes": {}}
    simple = json.load(io.open(C.OUTDIR + "/p6_prediction_interval.json", encoding="utf-8"))
    for name, r in res.items():
        pi = np.quantile(r, [0.025, 0.975])
        out["universes"][name] = {
            "pi95": [float(pi[0]), float(pi[1])],
            "p_rate_ge_observed_pct": float((r >= OBSERVED).mean()) * 100,
            "p_rate_zero_pct": float((r == 0).mean()) * 100,
            "observed_in_PI": "IN" if pi[0] <= OBSERVED <= pi[1] else "OUT"}
    out["simple_pi95_for_comparison"] = simple["pi95_8seg"]
    out["primary"] = "conditional"
    out["observed_in_primary_PI"] = out["universes"]["conditional"]["observed_in_PI"]
    np.save(os.path.join(C.OUTDIR, "p6_rates_stratified.npy"), res["conditional"])
    out["provenance"] = C.provenance([C.A1_FALL, C.VERIFY_LIST, C.SWEEP_LIST, C.VERIFY_META,
                                      C.MANIFEST, C.FOV])
    C.dump("p6_stratified.json", out)
    print("P6 stratified (registered design reproduced: sweep 24 + verify 8 lists match)")
    for name, u in out["universes"].items():
        print("  %-13s PI95 [%.4f, %.4f]  P(>= %.4f) = %.2f %%  P0 = %.2f %%  -> %s" % (
            name, u["pi95"][0], u["pi95"][1], OBSERVED, u["p_rate_ge_observed_pct"],
            u["p_rate_zero_pct"], u["observed_in_PI"]))
    print("  simple (SRS) PI95 for comparison [%.4f, %.4f]" % tuple(simple["pi95_8seg"]))
    return 0


def main():
    if "--stratified" in sys.argv[1:]:
        return stratified()
    a1 = json.load(io.open(C.A1_FALL, encoding="utf-8"))["segments"]
    names = list(a1)
    H = np.array([a1[s]["hours"] for s in names])
    K = np.array([a1[s]["alerts"][THETA] for s in names])
    n = len(names)
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, (REPS, n))
    ci_rates = K[idx].sum(1) / H[idx].sum(1)
    ci = np.quantile(ci_rates, [0.025, 0.975])
    pi_rates = np.empty(REPS)
    for i in range(REPS):
        j = rng.choice(n, 8, replace=False)
        pi_rates[i] = K[j].sum() / H[j].sum()
    pi = np.quantile(pi_rates, [0.025, 0.975])
    np.save(os.path.join(C.OUTDIR, "p6_rates_simple.npy"), pi_rates)
    p_ge = float((pi_rates >= OBSERVED).mean()) * 100
    p0 = float((pi_rates == 0).mean()) * 100
    ver = [l.strip() for l in io.open(C.VERIFY_LIST, encoding="utf-8") if l.strip()]
    vk = sum(a1[s]["alerts"][THETA] for s in ver)
    vh = sum(a1[s]["hours"] for s in ver)
    cnt = C.counts()
    got = {"ci": (round(float(ci[0]), 3), round(float(ci[1]), 3)),
           "pi": (round(float(pi[0]), 3), round(float(pi[1]), 3)),
           "p_ge": half_up(p_ge, 1), "p0": half_up(p0, 1), "a1_verify": round(vk / vh, 3)}
    diffs = {k: (got[k], EXPECTED[k]) for k in EXPECTED if tuple(np.atleast_1d(got[k])) != tuple(np.atleast_1d(EXPECTED[k]))}
    inside = bool(pi[0] <= OBSERVED <= pi[1])
    out = {"check": "P6 CI vs PI", "seed": SEED, "replicates": REPS, "theta": float(THETA),
           "numpy": np.__version__, "segments": n, "corpus_alerts": int(K.sum()),
           "corpus_hours": float(H.sum()), "corpus_rate": float(K.sum() / H.sum()),
           "corpus_ci95": [float(ci[0]), float(ci[1])],
           "registered_ci95_e12": json.load(io.open(C.E12, encoding="utf-8"))["axis_a1"]["points"][THETA]["block_bootstrap_ci95"],
           "pi95_8seg": [float(pi[0]), float(pi[1])],
           "observed_d5s_oos": OBSERVED, "observed_from_counts": cnt["d5s_oos_rate"],
           "d5s_oos_alerts": cnt["d5s_oos_alerts"], "d5s_oos_hours": cnt["d5s_oos_hours"],
           "d5s_oos_boot": cnt["d5s_oos_boot"], "d5s_oos_pzero": cnt["d5s_oos_pzero"],
           "p_rate_ge_observed_pct": p_ge, "p_rate_zero_pct": p0,
           "a1_on_verify_sample": {"segments": len(ver), "alerts": int(vk), "hours": float(vh), "rate": vk / vh},
           "observed_in_PI": "IN" if inside else "OUT",
           "expected_22_10": EXPECTED, "got_rounded": got, "deviations": {k: list(map(list, [np.atleast_1d(a).tolist(), np.atleast_1d(b).tolist()])) for k, (a, b) in diffs.items()},
           "provenance": C.provenance([C.A1_FALL, C.VERIFY_LIST, C.E12, C.COUNTS])}
    out["verdict"] = "REPRODUCED" if not diffs else "DEVIATION -- STOP"
    C.dump("p6_prediction_interval.json", out)
    print("P6: corpus %d alerts / %.4f h = %.4f /h" % (K.sum(), H.sum(), K.sum() / H.sum()))
    print("  CI95 corpus      [%.4f, %.4f]   (registered E12: [%.4f, %.4f], stdlib RNG)" % (
        ci[0], ci[1], *out["registered_ci95_e12"]))
    print("  PI95 8-segment   [%.4f, %.4f]" % (pi[0], pi[1]))
    print("  P(rate >= %.4f) = %.2f %%   P(rate = 0) = %.2f %%" % (OBSERVED, p_ge, p0))
    print("  A1 on verification sample: %d alerts / %.4f h = %.4f /h; D5s ran %s alerts / %s h = %s /h"
          % (vk, vh, vk / vh, cnt["d5s_oos_alerts"], cnt["d5s_oos_hours"], cnt["d5s_oos_rate"]))
    print("  observed %.4f is %s the PI" % (OBSERVED, out["observed_in_PI"]))
    print("  verdict: %s %s" % (out["verdict"], diffs if diffs else ""))
    return 0 if not diffs else 2


if __name__ == "__main__":
    sys.exit(main())
