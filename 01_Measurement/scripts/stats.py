#!/usr/bin/env python3
"""
Interval estimation for AAP v3. Every interval in the manuscript comes from
here; nothing is computed in a spreadsheet.

    Wilson score interval   for proportions (recall, precision)
    Block bootstrap         for rates (false alarms per hour)
    Poisson upper limit     for a rate when zero events were observed

RUNBOOK (laptop or Orin, no dependencies beyond the standard library)
    cd 01_Measurement/scripts
    python stats.py --selftest          # verify the formulas, ~1 s
    python stats.py --demo              # show worked examples

The self-test checks the formulas against values worked out by hand, listed
in the test bodies. Run it before trusting any table.

ZERO-EVENT CONVENTION -- read this before quoting a number
    "Rule of three" (3/T) is the ONE-SIDED 95% upper bound: there is a 5%
    chance the true rate exceeds it. The upper end of a two-sided 95%
    interval is 3.6889/T. These answer different questions and differ by 23%.
    Every other interval in this paper is two-sided, so
    ``rate_zero_events()`` returns the two-sided upper limit by default and
    reports the rule-of-three figure alongside it. State which one is quoted;
    do not mix them across tables.
"""

from __future__ import annotations

import argparse
import math
import random
import sys

Z95 = 1.959963984540054          # two-sided 95% normal quantile
RULE_OF_THREE = 3.0              # one-sided 95% upper bound, zero events
POISSON_UPPER_95_TWOSIDED = 3.688879454113936   # chi2(0.975, df=2) / 2


# ---------------------------------------------------------------------------
# proportions
# ---------------------------------------------------------------------------
def wilson(k, n, z=Z95):
    """Wilson score interval for k successes in n trials.

    Used rather than the normal approximation because the event counts here
    are small and the estimates sit near 0 and 1, where the normal interval
    misbehaves badly (at k=n it has zero width).

    Returns (point, low, high). For n == 0 returns (None, 0.0, 1.0): a
    proportion with no trials is undefined, and the caller must print it as
    undefined rather than as a number.
    """
    if n < 0 or k < 0:
        raise ValueError("k and n must be non-negative")
    if k > n:
        raise ValueError("k=%r exceeds n=%r; TP cannot exceed GT" % (k, n))
    if n == 0:
        return (None, 0.0, 1.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = p + z * z / (2.0 * n)
    margin = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    return (p, max(0.0, (center - margin) / denom), min(1.0, (center + margin) / denom))


def fmt_proportion(k, n, pct=True, decimals=1):
    """Render a proportion the way the manuscript must: value, CI and N."""
    point, lo, hi = wilson(k, n)
    if point is None:
        return "undefined (N=0)"
    s = 100.0 if pct else 1.0
    u = "%" if pct else ""
    return "%.*f%s (%.*f--%.*f%s, N=%d)" % (
        decimals, point * s, u, decimals, lo * s, decimals, hi * s, u, n)


# ---------------------------------------------------------------------------
# rates
# ---------------------------------------------------------------------------
def make_blocks(segments, block_hours=1.0):
    """Cut observation segments into blocks for the bootstrap.

    ``segments`` is a list of (count, duration_hours) -- typically one entry
    per (checker, footage file). Each is cut into blocks of ``block_hours``;
    the tail keeps its real duration. Events are apportioned to blocks in
    proportion to block duration, which is the correct expectation under the
    working assumption that the rate is constant within a file.

    Blocks, not individual alarms, are the resampling unit because false
    alarms cluster in time -- one bad lighting transition produces a burst.
    Resampling alarms independently would treat a burst as many independent
    observations and report an interval far narrower than the data supports.
    """
    blocks = []
    for count, hours in segments:
        if hours <= 0:
            raise ValueError("segment duration must be positive, got %r" % hours)
        n_full = int(hours // block_hours)
        tail = hours - n_full * block_hours
        parts = [block_hours] * n_full + ([tail] if tail > 1e-12 else [])
        if not parts:
            parts = [hours]
        # Apportion the count across the parts, largest-remainder so the
        # integer total is preserved exactly.
        shares = [count * (p / hours) for p in parts]
        base = [int(math.floor(s)) for s in shares]
        left = count - sum(base)
        order = sorted(range(len(parts)), key=lambda i: shares[i] - base[i],
                       reverse=True)
        for i in order[:left]:
            base[i] += 1
        blocks.extend(zip(base, parts))
    return blocks


def rate_bootstrap(segments, block_hours=1.0, resamples=10000, seed=20260820,
                   alpha=0.05):
    """Percentile block-bootstrap CI for a rate (events per hour).

    Returns a dict. When no event was observed the bootstrap is degenerate --
    every resample gives zero -- so the interval is replaced by the Poisson
    upper limit, which is the honest answer for that case.
    """
    blocks = make_blocks(segments, block_hours)
    total_count = sum(c for c, _ in blocks)
    total_hours = sum(h for _, h in blocks)
    if total_hours <= 0:
        raise ValueError("no observation time")
    point = total_count / total_hours

    if total_count == 0:
        z = rate_zero_events(total_hours)
        z.update({"point": 0.0, "count": 0, "hours": total_hours,
                  "n_blocks": len(blocks), "zero_observed": True,
                  "method": "poisson-upper (bootstrap degenerate at zero)"})
        return z

    rng = random.Random(seed)
    nb = len(blocks)
    draws = []
    for _ in range(resamples):
        c = h = 0.0
        for _ in range(nb):
            bc, bh = blocks[rng.randrange(nb)]
            c += bc
            h += bh
        if h > 0:
            draws.append(c / h)
    draws.sort()
    lo = draws[int(math.floor((alpha / 2.0) * len(draws)))]
    hi = draws[min(len(draws) - 1, int(math.ceil((1 - alpha / 2.0) * len(draws))) - 1)]
    return {"point": point, "low": lo, "high": hi, "count": total_count,
            "hours": total_hours, "n_blocks": nb, "zero_observed": False,
            "method": "block bootstrap, %d resamples, %.2f h blocks, seed %d"
                      % (resamples, block_hours, seed)}


def rate_zero_events(hours):
    """Upper confidence limit on a rate when zero events were observed.

    Reports both conventions explicitly so a table can never quietly mix them.
    Never returns a point estimate of zero dressed up as a measurement: no
    events in a finite window does not mean the rate is zero.
    """
    if hours <= 0:
        raise ValueError("hours must be positive")
    return {
        "point": 0.0,
        "low": 0.0,
        "high": POISSON_UPPER_95_TWOSIDED / hours,   # two-sided 95% upper end
        "rule_of_three": RULE_OF_THREE / hours,      # one-sided 95% bound
        "hours": hours,
        "zero_observed": True,
        "method": "zero events observed; two-sided 95% Poisson upper limit "
                  "3.689/T (one-sided rule of three is 3/T)",
    }


def fmt_rate(res, decimals=2, unit="/h"):
    """Render a rate the way the manuscript must, never as a bare zero."""
    if res.get("zero_observed"):
        return ("no alarms in %.1f h; 95%% upper limit %.*f%s"
                % (res["hours"], decimals, res["high"], unit))
    return ("%.*f%s (%.*f--%.*f, %d in %.1f h)"
            % (decimals, res["point"], unit, decimals, res["low"],
               decimals, res["high"], res["count"], res["hours"]))


# ---------------------------------------------------------------------------
# precision guard
# ---------------------------------------------------------------------------
def precision(tp, fp):
    """Precision, or None when it is undefined.

    Returning None is the point of this function. The previous version of
    this work printed 100% where TP+FP was zero, which is undefined, and a
    reviewer used that single cell to discount every number in the paper.
    """
    if tp + fp == 0:
        return None
    return wilson(tp, tp + fp)


def fmt_precision(tp, fp, decimals=1):
    r = precision(tp, fp)
    if r is None:
        return "no positive predictions"
    point, lo, hi = r
    return "%.*f%% (%.*f--%.*f%%, N=%d)" % (decimals, point * 100, decimals,
                                            lo * 100, decimals, hi * 100, tp + fp)


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def _close(a, b, tol=5e-4):
    return abs(a - b) <= tol


def selftest():
    """Check every formula against values worked out by hand."""
    fails = []

    def check(name, got, want, tol=5e-4):
        ok = _close(got, want, tol)
        print("  %-52s %-12.6f %s %.6f" % (name, got, "==" if ok else "!=", want))
        if not ok:
            fails.append(name)

    print("Wilson score interval")
    # k=3, n=3, z=1.96. denom = 1 + 3.8416/3 = 2.280534
    #   center = 1 + 3.8416/6 = 1.640267 ; margin = 1.96*sqrt(3.8416/36) = 0.640267
    #   low = (1.640267-0.640267)/2.280534 = 0.438486 ; high = 1
    p, lo, hi = wilson(3, 3)
    check("3/3 point", p, 1.0)
    check("3/3 low", lo, 0.438486)
    check("3/3 high", hi, 1.0)
    # k=1, n=1: low = 1/(1+z^2) = 1/4.841579 = 0.206543. This is the value the
    # previous version quoted as [20.7%, 100%] -- a cross-check on both.
    p, lo, hi = wilson(1, 1)
    check("1/1 low", lo, 0.206543)
    # k=5, n=10: the textbook symmetric case, [0.236600, 0.763400]
    p, lo, hi = wilson(5, 10)
    check("5/10 point", p, 0.5)
    check("5/10 low", lo, 0.236600)
    check("5/10 high", hi, 0.763400)
    # k=0, n=10: point 0, high = (z^2/20 + z^2/20)/(1+z^2/10) = 0.277540
    p, lo, hi = wilson(0, 10)
    check("0/10 point", p, 0.0)
    check("0/10 low", lo, 0.0)
    check("0/10 high", hi, 0.277540)
    # k=22, n=100 -- the fire/smoke recall the previous version reported as
    # a bare "22%". The interval is what that number actually supports.
    p, lo, hi = wilson(22, 100)
    check("22/100 low", lo, 0.150263)
    check("22/100 high", hi, 0.310218)

    print("\n  guards")
    try:
        wilson(4, 3)
        print("  %-52s %s" % ("wilson(4,3) rejected", "NO -- did not raise"))
        fails.append("wilson TP>GT guard")
    except ValueError:
        print("  %-52s %s" % ("wilson(4,3) raises (TP cannot exceed GT)", "ok"))
    if wilson(0, 0)[0] is not None:
        fails.append("wilson n=0 must return None")
    else:
        print("  %-52s %s" % ("wilson(0,0) point is None (undefined)", "ok"))
    if precision(0, 0) is not None:
        fails.append("precision(0,0) must be None")
    else:
        print("  %-52s %s" % ("precision(0,0) is None (no positive preds)", "ok"))
    if fmt_precision(0, 0) != "no positive predictions":
        fails.append("fmt_precision(0,0) wording")
    else:
        print("  %-52s %s" % ('fmt_precision(0,0) == "no positive predictions"', "ok"))

    print("\nZero-event upper limits")
    z = rate_zero_events(10.0)
    check("0 in 10 h, two-sided 95% upper", z["high"], 0.368888)
    check("0 in 10 h, rule of three", z["rule_of_three"], 0.300000)
    z = rate_zero_events(72.0)
    check("0 in 72 h, two-sided 95% upper", z["high"], 0.051234)
    # The previous version's evidence base: 10 minutes with no false alarm
    # bounds the rate only below 22.1/h. This is the arithmetic behind the
    # reject, so it is checked here.
    z = rate_zero_events(10.0 / 60.0)
    check("0 in 10 min, two-sided 95% upper", z["high"], 22.133277, tol=1e-3)
    check("0 in 10 min, rule of three", z["rule_of_three"], 18.0, tol=1e-3)

    print("\nBlock construction")
    # 2.5 h with 10 events -> blocks [1,1,0.5] h carrying [4,4,2] events
    blocks = make_blocks([(10, 2.5)], block_hours=1.0)
    got_h = [round(h, 6) for _, h in blocks]
    got_c = [c for c, _ in blocks]
    print("  %-52s %s / %s" % ("2.5 h, 10 events -> durations / counts",
                               got_h, got_c))
    if got_h != [1.0, 1.0, 0.5]:
        fails.append("block durations")
    if sum(got_c) != 10:
        fails.append("block counts must total the input count")
    if got_c != [4, 4, 2]:
        fails.append("block apportionment")

    print("\nBootstrap")
    # 24 blocks of 1 h, 2 events each: rate is exactly 2/h and every resample
    # must also give exactly 2/h, so the interval collapses to a point.
    r = rate_bootstrap([(2, 1.0)] * 24, resamples=500, seed=1)
    check("uniform 2/h point", r["point"], 2.0)
    check("uniform 2/h low", r["low"], 2.0)
    check("uniform 2/h high", r["high"], 2.0)
    # Clustered: 47 quiet hours, one hour with 20 alarms. Point rate is
    # 20/48 = 0.4167/h, but the interval must be wide because almost every
    # resample misses the burst entirely -- this is precisely why the
    # resampling unit is the block.
    r = rate_bootstrap([(0, 1.0)] * 47 + [(20, 1.0)], resamples=4000, seed=7)
    check("clustered point", r["point"], 20.0 / 48.0)
    lo_ok = r["low"] == 0.0
    hi_ok = r["high"] > 0.8
    print("  %-52s low=%.4f high=%.4f" % ("clustered interval is wide and "
                                          "reaches zero", r["low"], r["high"]))
    if not (lo_ok and hi_ok):
        fails.append("clustered bootstrap interval")
    # Determinism: same seed, same answer.
    a = rate_bootstrap([(3, 1.0), (0, 1.0), (7, 2.0)], resamples=800, seed=42)
    b = rate_bootstrap([(3, 1.0), (0, 1.0), (7, 2.0)], resamples=800, seed=42)
    if (a["low"], a["high"]) != (b["low"], b["high"]):
        fails.append("bootstrap is not reproducible for a fixed seed")
    else:
        print("  %-52s %s" % ("same seed gives the same interval", "ok"))
    # Zero events routes to the Poisson limit, not to a zero interval.
    r = rate_bootstrap([(0, 8.0)] * 3, resamples=100, seed=3)
    if not r.get("zero_observed") or not _close(r["high"], 3.688879 / 24.0):
        fails.append("zero-event bootstrap must route to the Poisson limit")
    else:
        print("  %-52s %s" % ("0 events in 24 h -> Poisson upper limit", "ok"))

    print("\nFormatting")
    for s in (fmt_proportion(3, 3), fmt_proportion(0, 0),
              fmt_rate(rate_zero_events(30.0)), fmt_precision(0, 0)):
        print("  %s" % s)
    if "undefined" not in fmt_proportion(0, 0):
        fails.append("fmt_proportion must say undefined at N=0")
    if "no alarms" not in fmt_rate(rate_zero_events(30.0)):
        fails.append("fmt_rate must not print a bare zero")

    print()
    if fails:
        print("SELFTEST FAILED: %d check(s): %s" % (len(fails), ", ".join(fails)))
        return 1
    print("SELFTEST PASSED")
    return 0


def demo():
    print("Recall 3 of 3 events      : %s" % fmt_proportion(3, 3))
    print("Recall 22 of 100 events   : %s" % fmt_proportion(22, 100))
    print("Precision with no preds   : %s" % fmt_precision(0, 0))
    print("FAR, 14 alarms in 26.5 h  : %s"
          % fmt_rate(rate_bootstrap([(9, 12.0), (5, 14.5)])))
    print("FAR, 0 alarms in 26.5 h   : %s" % fmt_rate(rate_zero_events(26.5)))
    print("FAR, 0 alarms in 10 min   : %s" % fmt_rate(rate_zero_events(10 / 60)))


def main():
    ap = argparse.ArgumentParser(description="AAP v3 interval estimation")
    ap.add_argument("--selftest", action="store_true",
                    help="check every formula against hand-worked values")
    ap.add_argument("--demo", action="store_true", help="worked examples")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.demo:
        demo()
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
