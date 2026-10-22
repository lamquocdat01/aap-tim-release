#!/usr/bin/env python3
r"""Run P1-P7 and gather every number the theory section may print (C6).

    python make_theory_numbers.py

Runs each check as a subprocess with this interpreter (so a clean venv
proves the whole chain), stops on the first failure, then writes
  theory_numbers.json   -- every value, with the check that produced it
  theory_numbers.tex    -- \ThN<Name> macros, the only way a theory number
                           may enter the manuscript
P4's time conversion (lambda) is written to the JSON but NOT to the .tex:
it stays out of print until the author decides (CP-alpha1 point a).
"""
import datetime
import io
import json
import os
import platform
import subprocess
import sys

import _common as C

CHECKS = ["p1_table1_rebuild.py", "p3_identified_set.py", "p4_sample_size.py",
          "p5_declared_observed.py", "p6_prediction_interval.py",
          ("p6_prediction_interval.py", "--stratified"), "p7_decision_map.py",
          "ki_alpha1_two_cis.py"]
BASELINE = "theory_numbers.cpalpha1.json"     # CP-alpha1 output; old keys must not move
BS = chr(92)


def run_all():
    log = []
    for c in CHECKS:
        args = list(c) if isinstance(c, tuple) else [c]
        r = subprocess.run([sys.executable, "-B", os.path.join(C.OUTDIR, args[0])] + args[1:],
                           cwd=C.OUTDIR, capture_output=True, text=True)
        c = " ".join(args)
        log.append({"check": c, "exit": r.returncode, "stdout": r.stdout})
        print(r.stdout, end="")
        if r.returncode != 0:
            print(r.stderr)
            print("STOP: %s exited %d" % (c, r.returncode))
            sys.exit(r.returncode)
    return log


def load(name):
    return json.load(io.open(os.path.join(C.OUTDIR, name), encoding="utf-8"))


def f4(x):
    return "%.4f" % x


def main():
    log = run_all()
    p1, p3, p4 = load("p1_table1_rebuild.json"), load("p3_identified_set.json"), load("p4_sample_size.json")
    p5, p6, p7 = load("p5_declared_observed.json"), load("p6_prediction_interval.json"), load("p7_decision_map.json")
    p6s, ki1 = load("p6_stratified.json"), load("ki_alpha1_two_cis.json")
    sc = p6s["universes"]["conditional"]
    r45 = [r for r in p7["rows"] if abs(r["theta"] - 0.45) < 1e-9][0]
    r525 = [r for r in p7["rows"] if abs(r["theta"] - 0.525) < 1e-9][0]
    r60 = [r for r in p7["rows"] if abs(r["theta"] - 0.6) < 1e-9][0]
    demo = p3["demo"]
    t = p1["table"]
    num = {
        # P1
        "CorpusHours": f4(p1["hours"]), "CorpusSegments": str(p1["segments"]),
        "ZeroLimitTwoSided": f4(p1["zero_count_conventions"]["two_sided_95"]),
        "ZeroLimitRuleOfThree": f4(p1["zero_count_conventions"]["one_sided_95_rule_of_three"]),
        "HelmetReplayRate": f4(t["HelmetChecker"]["rate"]),
        "HelmetReplayLo": f4(t["HelmetChecker"]["interval"][0]),
        "HelmetReplayHi": f4(t["HelmetChecker"]["interval"][1]),
        "FallReplayRate": f4(t["FallChecker"]["rate"]),
        "FallReplayLo": f4(t["FallChecker"]["interval"][0]),
        "FallReplayHi": f4(t["FallChecker"]["interval"][1]),
        "IntrusionAlertRate": f4(t["IntrusionChecker"]["rate"]),
        "IntrusionFpLabelled": str(p1["intrusion_far"]["fp_labelled"]),
        "IntrusionFpHi": f4(p1["intrusion_far"]["fp_wilson95"][1]),
        "IntrusionFarHiNinety": f4(p1["intrusion_far"]["far_upper_product_of_95"]),
        "IntrusionFarHiJoint": f4(p1["intrusion_far"]["far_upper_joint95_bonferroni"]),
        "TableOneComparisons": str(len(p1["comparisons"])),
        # P3
        "RhoLo": "%.3f" % p3["rho_band"][0], "RhoHi": "%.3f" % p3["rho_band"][1],
        "CovBDemo": f4(demo["cov_B"]), "CovBDemoK": demo["k_over_n"],
        "CovBDemoLo": f4(demo["wilson95"][0]), "CovBDemoHi": f4(demo["wilson95"][1]),
        "HPluginLo": f4(demo["H_plugin"][0]), "HPluginHi": f4(demo["H_plugin"][1]),
        "CSLo": f4(demo["CS95"][0]), "CSHi": f4(demo["CS95"][1]),
        # P4 (counts only; lambda conversion withheld)
        "NWilsonTenth": str(p4["precision"][1]["wilson_p0.5"]),
        "NWilsonFifth": str(p4["precision"][2]["wilson_p0.5"]),
        "NWaldTenth": str(p4["precision"][1]["wald_p0.5"]),
        "NZeroMissTenth": str(p4["certification"][1]["exact_two_sided95"]),
        "NZeroMissTwentieth": str(p4["certification"][0]["exact_two_sided95"]),
        "CorpusPersonYears": "%.4f" % p4["corpus_years"],
        # P5
        "MechanismsN": str(p5["n_mechanisms"]),
        "MechanismsExporting": str(p5["n_exporting_a_distinguishing_signal"]),
        "HelmetLogPzero": "%.0f" % p5["probe_b"]["HelmetChecker"]["log10_P0_poisson_at_lower_limit"],
        "FallLogPzero": "%.0f" % p5["probe_b"]["FallChecker"]["log10_P0_poisson_at_lower_limit"],
        "HelmetAzeroMargin": "%.0f" % p5["probe_b"]["HelmetChecker"]["overstatement_margin_alpha05"],
        "FallAzeroMargin": "%.1f" % p5["probe_b"]["FallChecker"]["overstatement_margin_alpha05"],
        # P6
        "PsixCorpusRate": f4(p6["corpus_rate"]),
        "PsixCILo": "%.3f" % p6["corpus_ci95"][0], "PsixCIHi": "%.3f" % p6["corpus_ci95"][1],
        "PsixPILo": "%.3f" % p6["pi95_8seg"][0], "PsixPIHi": "%.3f" % p6["pi95_8seg"][1],
        "PsixObserved": "%.4f" % p6["observed_d5s_oos"],
        "PsixPge": "%.2f" % p6["p_rate_ge_observed_pct"], "PsixPzero": "%.2f" % p6["p_rate_zero_pct"],
        "PsixAoneVerify": "%.3f" % p6["a1_on_verify_sample"]["rate"],
        "PsixInOut": p6["observed_in_PI"],
        # --- CP-alpha2 additions (new keys only) ---
        # P3 under their correct names (same values as HPlugin*/CS*)
        "IdentifiedSetLo": f4(demo["H_plugin"][0]), "IdentifiedSetHi": f4(demo["H_plugin"][1]),
        "IdentifiedSetConfLo": f4(demo["CS95"][0]), "IdentifiedSetConfHi": f4(demo["CS95"][1]),
        # P1(b): the zero-count limit bounds the EPISODE rate; alert rate only under Poisson
        "ZeroLimitEpisode": f4(p1["zero_count_conventions"]["two_sided_95"]),
        # P6 under the registered stratified design (primary: conditional on the realised sweep)
        "PsixStratPILo": "%.3f" % sc["pi95"][0], "PsixStratPIHi": "%.3f" % sc["pi95"][1],
        "PsixStratPge": "%.2f" % sc["p_rate_ge_observed_pct"],
        "PsixStratPzero": "%.2f" % sc["p_rate_zero_pct"],
        "PsixStratInOut": sc["observed_in_PI"],
        "PsixStratUncondPIHi": "%.3f" % p6s["universes"]["unconditional"]["pi95"][1],
        # P7 at the deployed default, with the KI-alpha1 single interval
        "PsevenFallZfFARHi": f4(r45["far"]["ci95"][1]), "PsevenFallZfGuard": f4(r45["guard_band_w"]),
        "KIalphaOneMCsdHi": "%.3f" % ki1["monte_carlo_spread_tableI_method"]["hi_sd"],
        # --- P3 additions (new keys only): manuscript prose needs these as macros ---
        "PsixSeed": str(p6["seed"]), "PsixReps": "{:,}".format(p6["replicates"]).replace(",", "{,}"),
        "PsixStratPool": str(sum(p6s["verify_cell_sizes"].values())),
        "PsixVarFactor": "%.2f" % ((p6["segments"] / 8.0 - 1) ** 0.5),
        "PsevenDemoFARHi": f4(r525["far"]["ci95"][1]), "PsevenDemoGuard": f4(r525["guard_band_w"]),
        "PsevenSixFARHi": f4(r60["far"]["ci95"][1]),
        "PsevenSixCSHi": f4(r60["cov_CS95"][1]),
        "PsevenFallZfCSLo": f4(r45["cov_CS95"][0]), "PsevenFallZfCSHi": f4(r45["cov_CS95"][1]),
        "PthreeLowCSLo": f4(p3["by_theta"]["0.3"]["CS95"][0]), "PthreeLowCSHi": f4(p3["by_theta"]["0.3"]["CS95"][1]),
        "PfourNZeroMissFifth": str(p4["certification"][2]["exact_two_sided95"]),
        "PfourNWilsonThird": str(p4["precision"][3]["wilson_p0.5"]),
        # --- P3b: intrusion FAR on the DEPLOYED alert rate (the FP sample is of production alerts) ---
        "IntrusionDepRate": f4(p1["intrusion_far"]["deployed_basis"]["deployed_rate"]),
        "IntrusionDepFarHiNinety": f4(p1["intrusion_far"]["deployed_basis"]["far_upper_product_of_95"]),
        "IntrusionDepFarHiJoint": f4(p1["intrusion_far"]["deployed_basis"]["far_upper_joint95_bonferroni"]),
        "IntrusionVfiveFarUpper": f4(p1["intrusion_far"]["deployed_basis"]["v5_printed_upper"]),
    }
    notes = {"ZeroLimitEpisode": "two-sided 95 % limit at k = 0 on the alert-EPISODE rate; on the alert rate only under the Poisson model (P1b)",
             "IdentifiedSetLo": "plug-in identified set of COV(S), fall theta 0.525 (P3)",
             "IdentifiedSetConfLo": "95 % confidence set FOR the identified set (not the identified set)",
             "PsixStratPILo": "PI95 of the 8-segment rate under the registered stratified draw, conditional on the realised sweep"}
    withheld = {"P4_time_years": p4["time"], "lambda_grid": p4["lambda_grid_per_person_year"],
                "status": p4["lambda_status"]}
    stamp = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    base_path = os.path.join(C.OUTDIR, BASELINE)
    regress = {"baseline": BASELINE, "checked": 0, "changed": [], "new": []}
    if os.path.exists(base_path):
        old = json.load(io.open(base_path, encoding="utf-8"))["macros"]
        for k, v in num.items():
            if k in old:
                regress["checked"] += 1
                if old[k] != v:
                    regress["changed"].append({"key": k, "cp_alpha1": old[k], "now": v})
            else:
                regress["new"].append(k)
        missing = [k for k in old if k not in num]
        regress["missing"] = missing
        print("regression vs CP-alpha1: %d keys checked, %d changed, %d missing, %d new" % (
            regress["checked"], len(regress["changed"]), len(missing), len(regress["new"])))
        for ch in regress["changed"]:
            print("  CHANGED", ch)
    payload = {"generated": stamp, "regression_vs_cp_alpha1": regress, "notes": notes, "python": platform.python_version(),
               # file name only: the full path names the local user (published file)
               "executable": os.path.basename(sys.executable),
               "checks": {c["check"]: c["exit"] for c in log},
               "verdicts": {"P1": p1["verdict"], "P3": p3["verdict"], "P6": p6["verdict"],
                            "P6_observed_in_PI": p6["observed_in_PI"]},
               "macros": num, "withheld_from_tex": withheld,
               "provenance": sorted({json.dumps(p, sort_keys=True) for d in (p1, p3, p4, p5, p6, p7)
                                     for p in d.get("provenance", [])})}
    payload["provenance"] = [json.loads(x) for x in payload["provenance"]]
    io.open(os.path.join(C.OUTDIR, "theory_numbers.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(payload, indent=1, ensure_ascii=False))
    lines = ["%% theory_numbers.tex -- generated by scripts/theory_checks/make_theory_numbers.py, %s" % stamp,
             "% Do not edit. Every theory number enters the manuscript through these macros (C6).",
             "% P4 lambda-to-years conversion deliberately absent (author decision pending)."]
    for k in sorted(num):
        v = num[k].replace("%", BS + "%")
        lines.append("%snewcommand{%sThN%s}{%s}" % (BS, BS, k, v))
    io.open(os.path.join(C.OUTDIR, "theory_numbers.tex"), "w", encoding="utf-8", newline="\n").write(
        "\n".join(lines) + "\n")
    print("wrote theory_numbers.json (%d macros) and theory_numbers.tex" % len(num))
    if regress.get("changed") or regress.get("missing"):
        print("FAIL: CP-alpha1 keys moved")
        return 1
    print("PASS: every CP-alpha1 key unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
