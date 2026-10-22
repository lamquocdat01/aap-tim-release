#!/usr/bin/env python3
r"""P4 check -- how many site positives verification of site coverage needs.

(i)  Precision: smallest N such that the 95 % Wilson interval at observed
     proportion p has half-width <= w. Reported exactly (search over N) and
     by the Wald approximation N >= z^2 p(1-p)/w^2 for comparison. At p = 1/2
     the Wilson half-width is z / (2 sqrt(N + z^2)), so N >= z^2 (1/(4w^2) - 1).
(ii) Certification with zero misses: smallest N such that, when all N site
     events are detected, the exact (Clopper-Pearson) lower confidence limit
     is >= 1 - eps:  (alpha)^(1/N) >= 1 - eps  <=>  N >= ln(alpha)/ln(1-eps).
     alpha = 0.025 (two-sided 95 %, the paper's single convention, same as
     the zero-count FAR limit 3.689/T); alpha = 0.05 and 3/eps for comparison.
(iii) Time: with site events arriving as Poisson(lambda) per year, expected
     time N/lambda, and the time T95 by which P(at least N events) >= 0.95,
     i.e. the 0.95 quantile of Gamma(N, 1/lambda). lambda in {0.5, 1, 3}
     per monitored person per year is a PARAMETER grid; its sources are in
     03_Dossier/INCIDENCE_SOURCES.md and it is NOT printed in the paper
     until the author decides (CP-alpha1 point a).
Standard library only.
"""
import math
import sys

import _common as C

Z = 1.959963984540054


def wilson_halfwidth(p, n, z=Z):
    den = 1 + z * z / n
    return z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den


def n_wilson(p, w):
    n = 1
    while wilson_halfwidth(p, n) > w:
        n += 1
    return n


def n_wald(p, w):
    return math.ceil(Z * Z * p * (1 - p) / (w * w) - 1e-9)


def n_zero_miss(eps, alpha):
    return math.ceil(math.log(alpha) / math.log(1 - eps) - 1e-12)


def poisson_cdf(k, mu):
    """P(X <= k), X ~ Poisson(mu)."""
    term = math.exp(-mu)
    s = term
    for i in range(1, k + 1):
        term *= mu / i
        s += term
    return s


def t95_years(N, lam):
    """Smallest T with P(Poisson(lam*T) >= N) >= 0.95."""
    lo, hi = 0.0, 10.0 * (N + 10) / lam
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - poisson_cdf(N - 1, lam * mid) >= 0.95:
            hi = mid
        else:
            lo = mid
    return hi


def main():
    ws = (0.05, 0.10, 0.20, 0.30)
    ps = (0.5, 0.8, 0.9)
    prec = []
    for w in ws:
        row = {"w": w}
        for p in ps:
            row["wilson_p%.1f" % p] = n_wilson(p, w)
            row["wald_p%.1f" % p] = n_wald(p, w)
        row["closed_form_p0.5"] = math.ceil(Z * Z * (1 / (4 * w * w) - 1) - 1e-9)
        prec.append(row)
    cert = []
    for eps in (0.05, 0.10, 0.20):
        cert.append({"eps": eps,
                     "exact_two_sided95": n_zero_miss(eps, 0.025),
                     "exact_one_sided95": n_zero_miss(eps, 0.05),
                     "rule_of_three": math.ceil(3 / eps - 1e-9)})
    lambdas = (0.5, 1.0, 3.0)
    targets = [("w=0.20 @p=0.5 (Wilson)", prec[2]["wilson_p0.5"]),
               ("w=0.10 @p=0.5 (Wilson)", prec[1]["wilson_p0.5"]),
               ("eps=0.10, 0 miss (two-sided)", cert[1]["exact_two_sided95"]),
               ("eps=0.05, 0 miss (two-sided)", cert[0]["exact_two_sided95"])]
    time = []
    for label, N in targets:
        row = {"target": label, "N": N}
        for lam in lambdas:
            row["expected_years_lambda%g" % lam] = N / lam
            row["T95_years_lambda%g" % lam] = t95_years(N, lam)
        time.append(row)
    # observed: the corpus itself
    cnt = C.counts()
    H = float(cnt["far_pooled_hours"])
    out = {"check": "P4 sample size", "z": Z, "precision": prec, "certification": cert,
           "time": time, "lambda_grid_per_person_year": list(lambdas),
           "lambda_status": "PARAMETER -- sources in INCIDENCE_SOURCES.md; not for print until author decides",
           "corpus_hours": H, "corpus_years": H / (24 * 365.25),
           "expected_site_falls_in_corpus": {("lambda%g" % l): l * H / (24 * 365.25) for l in lambdas},
           "draft_table_check": {
               "wald_matches_draft": [prec[0]["wald_p0.5"], prec[0]["wald_p0.8"], prec[0]["wald_p0.9"],
                                      prec[1]["wald_p0.5"], prec[1]["wald_p0.8"], prec[1]["wald_p0.9"]]
               == [385, 246, 139, 97, 62, 35]},
           "provenance": C.provenance([C.COUNTS])}
    C.dump("p4_sample_size.json", out)
    print("P4 sample size")
    print("  half-width w | Wilson N (p=.5,.8,.9) | Wald N (p=.5,.8,.9) | closed form p=.5")
    for r in prec:
        print("  %4.2f         | %4d %4d %4d        | %4d %4d %4d        | %d" % (
            r["w"], r["wilson_p0.5"], r["wilson_p0.8"], r["wilson_p0.9"],
            r["wald_p0.5"], r["wald_p0.8"], r["wald_p0.9"], r["closed_form_p0.5"]))
    for r in cert:
        print("  eps %.2f: N = %d (two-sided 95%%), %d (one-sided), %d (3/eps)" % (
            r["eps"], r["exact_two_sided95"], r["exact_one_sided95"], r["rule_of_three"]))
    for r in time:
        print("  %-30s N=%3d | " % (r["target"], r["N"]) + " | ".join(
            "lam %g: E %.1f y, T95 %.1f y" % (l, r["expected_years_lambda%g" % l], r["T95_years_lambda%g" % l])
            for l in lambdas))
    print("  corpus = %.4f h = %.5f person-years -> expected site falls %s" % (
        H, out["corpus_years"], {k: round(v, 4) for k, v in out["expected_site_falls_in_corpus"].items()}))
    print("  Wald column reproduces the 22-10 draft table: %s" % out["draft_table_check"]["wald_matches_draft"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
