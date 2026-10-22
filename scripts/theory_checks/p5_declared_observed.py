#!/usr/bin/env python3
r"""P5 check -- declared vs observed, and the probe that separates Z1 from Z2.

Part 1. The seven silent mechanisms (analysis/silent_mechanisms.csv, the S3
table of v5) with two columns added for alpha:
  * exported -- did the instrument export, through any interface the operator
    or an auditor could read, a signal that distinguished the declared state
    from the observed one? Read from the CSV's own evidence column; the
    justification is printed next to each answer.
  * breaks   -- which additional observation would break the equivalence
    (P5 condition (a): an exported signal independent of the alert stream;
    condition (b): a probe with known positives through the same pipeline),
    and which measurand the mechanism threatens.
The two added columns are the analyst's classification, made explicit so a
reviewer can disagree with a row rather than with a paragraph.

Part 2. The probe of P5(b) for the two channels whose deployed stream is
zero while the frozen pipeline, replaying the SAME footage at shipped
thresholds, is not: the probability of a zero deployed count over T under
"instantiated at the shipped operating point" (Z2-default), by
  - Poisson at the replay rate's lower 95 % limit: exp(-r_L * T)
  - segment block bootstrap of the replay counts: fraction of resampled
    corpora with zero alerts (20 000 replicates, seed 20260911).
"""
import csv
import io
import math
import random
import sys

import _common as C

CLASSIFY = {
    "SM1": ("no", "liveness 'true' and a rising frame counter were the exported signals, and both "
            "stayed healthy through the outage, so what was exported could not tell 'running' "
            "from 'running on no frames'",
            "(a) a decoded-frame counter tied to frames actually decoded, not to a clock",
            "observation time T, hence every FAR denominator"),
    "SM2": ("no", "no timestamp, no audit entry; per-camera setting while the UI shows per-module; "
            "87 days silent with nothing distinguishing off from broken",
            "(a) per-channel instantiation flag + config-change log; (b) replay with known "
            "positives (Part 2)", "the Z1/Z2 status of every zero channel"),
    "SM3": ("no", "the audit table exists but never received a row; the bulk delete was invisible",
            "(a) append-only audit with a row counter exported", "integrity of the alert record (counts)"),
    "SM4": ("no", "configuration present, binary absent; nothing reports the mismatch",
            "(a) runtime self-report of installed components", "retention of the raw logs the counts are rebuilt from"),
    "SM5": ("no", "two copies written, neither deleted; no retention metric exported",
            "(a) retention / disk metric with policy echo", "instrument availability (disk exhaustion ends observation)"),
    "SM6": ("no", "camera row stayed 'online' with last_seen NULL; no notification sent",
            "(a) reachability probe independent of the DB row", "observation time T"),
    "SM7": ("no", "four dashboard labels contradicted tegrastats, /proc, df and the logs",
            "(a) runtime config hash + operating-point echo", "identity of the instrument the numbers describe"),
}


def block_zero_fraction(k, h, seed=20260911, reps=20000):
    rnd = random.Random(seed)
    n = len(k)
    zero = 0
    for _ in range(reps):
        pick = [rnd.randrange(n) for _ in range(n)]
        if sum(k[i] for i in pick) == 0:
            zero += 1
    return zero / reps


def main():
    rows = []
    with io.open(C.MECHANISMS, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            exp, why, brk, threat = CLASSIFY[r["id"]]
            rows.append({"id": r["id"], "known_issue": r["known_issue"], "declared": r["asserted"],
                         "observed": r["observed"], "evidence": r["evidence"],
                         "in_main_table_v5": r["in_main_table"],
                         "signal_exported": exp, "why": why, "breaks_equivalence_by": brk,
                         "threatens": threat})
    cnt = C.counts()
    ins = C.load_insitu()
    order = ins["order"]
    H = sum(ins["hours"][s] for s in order)
    hours = [ins["hours"][s] for s in order]
    probes = {}
    for ck in ("HelmetChecker", "FallChecker"):
        key = ck.lower()
        k = [ins["per_seg"][s].get(ck, 0) for s in order]
        rL = float(cnt["far_%s_pooled_ci_lo" % key])
        logp = -rL * H
        pz = block_zero_fraction(k, hours)
        probes[ck] = {
            "deployed_alerts": cnt["far_deployed_%s_alerts" % key],
            "replay_alerts": sum(k), "replay_rate": sum(k) / H,
            "replay_ci95": [rL, float(cnt["far_%s_pooled_ci_hi" % key])],
            "segments_carrying": sum(1 for x in k if x),
            "log10_P0_poisson_at_lower_limit": logp / math.log(10),
            "bootstrap_P0": pz, "bootstrap_reps": 20000,
            # Robustness to A0 (replay reproduces the deployed instance at the shipped
            # operating point; reproduction_gate.csv shows it does so only approximately):
            # the factor by which replay may OVERSTATE that rate while a zero deployed
            # count still rejects at alpha = 0.05 (Poisson at the lower limit).
            "overstatement_margin_alpha05": rL * H / -math.log(0.05),
            "bootstrap_P0_bound": ("< %.0e" % (1 / 20000)) if pz == 0 else pz,
            "verdict": "Z2-at-shipped-operating-point rejected" if pz == 0 and logp / math.log(10) < -3
                       else "not rejected"}
    out = {"check": "P5 declared vs observed", "mechanisms": rows,
           "n_mechanisms": len(rows),
           "n_exporting_a_distinguishing_signal": sum(1 for r in rows if r["signal_exported"] == "yes"),
           "probe_b": probes, "hours": H,
           "reading": ("Probe (b) rejects 'instantiated at the shipped operating point' for both "
                       "channels; it cannot separate 'not instantiated' (Z1) from 'instantiated at "
                       "some other operating point' (Z2'). Only an exported operating-point echo or "
                       "instantiation flag -- condition (a) -- can, and SM2 shows none exists."),
           "provenance": C.provenance([C.MECHANISMS, C.COUNTS])}
    C.dump("p5_declared_observed.json", out)
    print("P5: %d mechanisms, %d export a distinguishing signal" % (len(rows), out["n_exporting_a_distinguishing_signal"]))
    for r in rows:
        print("  %s %-6s exported=%s | breaks by %s | threatens %s" % (
            r["id"], r["known_issue"], r["signal_exported"], r["breaks_equivalence_by"][:50], r["threatens"]))
    for ck, p in probes.items():
        print("  probe %-13s deployed %d | replay %d alerts = %.4f/h CI [%.4f, %.4f], %d seg carry | "
              "log10 P0(Poisson@lower) = %.1f | bootstrap P0 %s -> %s | A0 margin x%.1f" % (
                  ck, p["deployed_alerts"], p["replay_alerts"], p["replay_rate"], p["replay_ci95"][0],
                  p["replay_ci95"][1], p["segments_carrying"], p["log10_P0_poisson_at_lower_limit"],
                  p["bootstrap_P0_bound"], p["verdict"], p["overstatement_margin_alpha05"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
