#!/usr/bin/env python3
"""CP1h H1. Every countable quantity in the paper, counted from the files.

THE RULE THIS ENFORCES
    No countable number in the manuscript is typed by hand from an abstract, a
    README, a dataset card, or one of our own summaries. Clips, videos, events,
    hours, resolution and frame-rate distributions all come from a script that
    counts the actual files being used, and that script runs at build time.

WHY
    Two numbers went into working documents wrong on 2026-09-02 and had the same
    shape: "GMDCSA24 is uniformly 1280x720" (read from three rows of a probe) and
    "FURG has 29 videos" (read from a summary; the repository holds 23). Neither
    was carelessness. Both were trusting a digest instead of counting. A wrong
    count in a published paper is an erratum, and it is cheap enough to prevent
    that there is no argument for not preventing it.

OUTPUTS
    generated_counts.json   machine-readable, for other scripts
    generated_counts.tex    \newcommand macros for the manuscript
    GENERATED_COUNTS.md     human-readable, for review

Run from anywhere:  python 01_Measurement/scripts/count_everything.py
"""
import csv, collections, datetime, glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEAS = os.path.dirname(HERE)                      # 01_Measurement
ROOT = os.path.dirname(MEAS)                      # Submission Elsevier
EXSITU = os.path.join(MEAS, "exsitu")
ANALYSIS = os.path.join(MEAS, "analysis")
RUNS = os.path.join(MEAS, "runs")
MANU = os.path.join(ROOT, "02_Manuscript")

C = {}          # counts
NOTES = []      # things that could not be counted, said out loud

# Per-segment observation time and clock stratum, filled by
# count_observation_hours() and consumed by count_far_strata() (E4). One pass
# over the run metadata, one set of hours: a second reader computing its own
# denominator is how two numbers claiming to be the same number get born.
_SEG_HOURS = {}         # segment id -> observation hours
_SEG_STRATUM = {}       # segment id -> "substituted" | "native"
_CHECKER_ROSTER = set() # every checker the runs themselves name
# Every checker actually INSTANTIATED by the pass, which is a smaller set than
# the roster and a different fact. `per_checker_cooldown_s` lists all seven
# whatever ran, because it is a configuration table; `modules` (plus
# `helmet_mode`) says which ones the runner built. A checker that was never
# built has no rate and no upper bound -- it has no observation. Conflating
# that with "ran and stayed silent" is the exact error `_far_by_checker`
# refuses to make one level down, and it would be worse here, because a
# rule-of-three bound printed under a channel that never ran reads as evidence.
_MEASURED_CHECKERS = set()
_MODULE_TO_CHECKER = {
    "intrusion": "IntrusionChecker",
    "fall": "FallChecker",
    "smoke_fire": "SmokeFireChecker",
    "running": "RunningChecker",
    "forklift_speed": "ForkliftSpeedChecker",
}


def note(msg):
    NOTES.append(msg)


def _load_duration_corrections():
    """The registered HARNESS-5 substitution table, keyed by segment id.

    Returns {} and says so if the artefact is absent, rather than assuming no
    segment needed a substitution -- "the table is missing" and "no segment
    needed correcting" are different facts and must not read the same.
    """
    p = os.path.join(ANALYSIS, "tier0", "duration_corrections.json")
    if not os.path.exists(p):
        note("HARNESS-5 substitution table not found at %s: segments scored on "
             "a substituted clock cannot be verified this run" % p)
        return {}
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:                                      # noqa: BLE001
        note("unreadable substitution table %s: %s" % (p, e))
        return {}
    return {e["file"].rsplit(".", 1)[0]: e for e in (d.get("fixed") or [])}


def count_virat_running():
    """The VIRAT running ground truth, counted from the locked list itself."""
    p = os.path.join(EXSITU, "virat", "GT_running_virat.csv")
    if not os.path.exists(p):
        note("VIRAT running ground-truth list not found at %s" % p)
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    C["virat_gt_events_total"] = len(rows)
    C["virat_gt_clips"] = len({r["clip"] for r in rows if r.get("clip")})


def count_thin_evidence():
    """Allocation candidates resting on fewer than the registered minimum of
    positive events, counted rather than remembered.

    "Two of the channels entering the allocation rest on fewer than twenty
    positive events each" was true when it was written and is the kind of
    sentence that stays on the page after it stops being true. The threshold is
    registered here; which channels fall under it is counted.
    """
    thr = 20
    gt = {}
    if "gmdcsa24_clips_with_fall" in C:
        gt["FallChecker"] = C["gmdcsa24_clips_with_fall"]
    if "furg_gt_events_total" in C:
        gt["SmokeFireChecker"] = C["furg_gt_events_total"]
    if "virat_gt_events_total" in C:
        gt["RunningChecker"] = C["virat_gt_events_total"]
    if not gt:
        note("no ex-situ ground-truth counts available: the thin-evidence "
             "channels cannot be counted")
        return
    thin = sorted(k for k, v in gt.items() if v < thr)
    C["exsitu_gt_events_by_channel"] = ", ".join(
        "%s %d" % (k, gt[k]) for k in sorted(gt))
    C["thin_evidence_threshold"] = thr
    C["thin_evidence_channels"] = ", ".join(thin) or "none"
    C["thin_evidence_channels_n"] = len(thin)
    C["thin_evidence_channels_n_word"] = word(len(thin))

    # CLAIM_LEDGER D7, 2026-09-10. The Limitations sentence said "two of the
    # channels ENTERING THE ALLOCATION rest on fewer than twenty positive
    # events each". Both channels this counter found -- RunningChecker and
    # SmokeFireChecker -- are channels the characterisability table on the
    # previous page prints as NOT in the allocation, and the one channel that
    # is in it rests on 78. The counter was right about which channels are
    # thin and the sentence was wrong about where they are, and nothing
    # crossed the two. It does now: the set is intersected with the allocation
    # here, and a channel with no allocation verdict at all is a hard failure
    # rather than a channel quietly assumed to be out.
    missing_verdict = [k for k in gt
                       if ("char_%s_allocation" % k.lower()) not in C]
    if missing_verdict:
        sys.stderr.write(
            "count_everything: %d allocation candidate(s) have no "
            "characterisability verdict, so 'entering the allocation' cannot "
            "be evaluated: %s. count_characterizability() must run first.\n"
            % (len(missing_verdict), ", ".join(sorted(missing_verdict))))
        sys.exit(2)
    in_alloc = sorted(k for k in gt
                      if C.get("char_%s_allocation" % k.lower()) == "yes")
    thin_in = sorted(k for k in thin if k in in_alloc)
    C["allocation_channels"] = ", ".join(in_alloc) or "none"
    C["allocation_channels_n"] = len(in_alloc)
    C["allocation_channels_n_word"] = word(len(in_alloc))
    C["thin_evidence_in_allocation"] = ", ".join(thin_in) or "none"
    C["thin_evidence_in_allocation_n"] = len(thin_in)
    C["thin_evidence_in_allocation_n_word"] = word(len(thin_in))
    if in_alloc:
        out = sorted(k for k in gt if k not in in_alloc)
        C["allocation_evidence_line"] = (
            "the %s channel that enters the allocation rests on %s annotated "
            "event%s; the %s that do not rest on %s"
            % (word(len(in_alloc)) if len(in_alloc) == 1
               else "%s channels" % word(len(in_alloc)),
               ", ".join(str(gt[k]) for k in in_alloc),
               "" if len(in_alloc) == 1 and gt[in_alloc[0]] == 1 else "s",
               word(len(out)),
               " and ".join(str(gt[k]) for k in out) or "nothing"))
    else:
        C["allocation_evidence_line"] = (
            "no channel enters the allocation on today's evidence")


# ------------------------------------------------- silent mechanisms (S4)
# Stops at twenty, not at twelve. On 2026-09-12 word(16) returned the STRING
# "16", so a generated sentence would have read "16 pre-registrations are
# locked" -- a digit standing where the counter promised a word, which is the
# exact defect P9-d polices, inside the counter that feeds P9-d.
_NUM_WORD = {0: "no", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
             6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
             11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
             15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
             19: "nineteen", 20: "twenty"}


def word(n):
    """A count spelled out, FROM the count.

    A sentence that says "four mechanisms" while the table has three is a
    number typed by hand wearing a word, and P9's digit rule never sees it.
    That is exactly how the abstract came to say four, the introduction nine,
    and the table caption three of nine, all at once and all in one build.
    """
    return _NUM_WORD.get(n, str(n))


def count_silent_mechanisms():
    """The asserted-and-absent mechanisms, counted from their own register.

    Three different counts were in circulation because three different things
    were being counted and none of them said which: how many are catalogued,
    how many were observed on THIS deployment, and how many fit in the main
    text. They are now three keys with three names.
    """
    p = os.path.join(ANALYSIS, "silent_mechanisms.csv")
    if not os.path.exists(p):
        note("silent-mechanism register not found at %s" % p)
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    if not rows:
        note("silent-mechanism register is empty")
        return
    obs = [r for r in rows if (r.get("observed_in_deployment") or "").strip() == "y"]
    tab = [r for r in rows if (r.get("in_main_table") or "").strip() == "y"]
    C["silent_mechanisms_catalogued"] = len(rows)
    C["silent_mechanisms_catalogued_word"] = word(len(rows))
    C["silent_mechanisms_observed"] = len(obs)
    C["silent_mechanisms_observed_word"] = word(len(obs))
    C["silent_mechanisms_in_main_table"] = len(tab)
    C["silent_mechanisms_in_main_table_word"] = word(len(tab))
    # EVERY row, not only the ones the main text tabulates: the supplement
    # prints the full set, and it must print it from the same register or the
    # two tables are two transcriptions of one list, which is how they drift.
    for r in rows:
        k = r["id"].lower()
        C["silent_mechanism_%s_asserted" % k] = r["asserted"]
        C["silent_mechanism_%s_observed" % k] = r["observed"]
        C["silent_mechanism_%s_issue" % k] = r["known_issue"]
        C["silent_mechanism_%s_evidence" % k] = r.get("evidence", "")
    C["silent_mechanisms_register"] = ", ".join(
        "%s (%s)" % (r["id"], r["known_issue"]) for r in rows)
    if len(tab) > len(obs):
        note("silent mechanisms: %d rows are marked for the main table but only "
             "%d are marked observed on this deployment" % (len(tab), len(obs)))


# ------------------------------------------------- observation time (P10)
def count_fall_theta_curve():
    """The in-situ FallChecker curve that the A1 pass can supply exactly (E7-b).

    FallChecker's only monotone operating point is the literal in
    `fall_check._analyze`:  is_falling = confidence > 0.45 or high_scores >= 2.
    A1 ran with `checker_params` null on all 175 segments, so the literal was
    never patched and the pass recorded at exactly **0.45**.

    That coincidence is what makes three grid points exact rather than an
    interval. For an alert A1 recorded:

        confidence > 0.45   -> it fired through the confidence disjunct, and it
                               survives a higher theta iff confidence > theta
        confidence <= 0.45  -> the confidence disjunct was false, so it fired
                               through high_scores, and it survives EVERY theta

    Both branches are decided by the number already on the row, so no field is
    missing and no interval is needed -- for A1. A pass recorded at any other
    theta (C1 at 0.30) has a band where the disjunct is undetermined; that band
    is reported as an interval under E7-b section 3 and is not computed here.

    `far_fall_a1_alerts_below_recorded_theta` is the load-bearing count. If it
    is zero, the `high_scores` disjunct produced no alert of its own in the
    whole corpus, and every point below is a plain confidence threshold.
    """
    import glob as _glob
    files = sorted(_glob.glob(os.path.join(RUNS, "m1", "HOM_*.csv")))
    if not files:
        note("no A1 alert files under runs/m1: the Fall theta curve is not counted")
        return
    conf = []
    for f in files:
        try:
            for r in csv.DictReader(open(f, encoding="utf-8-sig")):
                if r.get("checker") != "FallChecker":
                    continue
                c = (r.get("confidence") or "").strip()
                conf.append(float(c) if c not in ("", "NA") else None)
        except Exception as e:                                  # noqa: BLE001
            note("unreadable A1 alert file %s: %s" % (os.path.basename(f), e))
            return
    hours = C.get("insitu_hours")
    if not conf or not hours:
        note("Fall theta curve not counted: %d alert(s), hours=%r"
             % (len(conf), hours))
        return
    rec_theta = 0.45
    unknown = sum(1 for c in conf if c is None)
    below = sum(1 for c in conf if c is not None and c <= rec_theta)
    C["far_fall_a1_recorded_theta"] = rec_theta
    C["far_fall_a1_alerts_total"] = len(conf)
    C["far_fall_a1_alerts_without_confidence"] = unknown
    C["far_fall_a1_alerts_below_recorded_theta"] = below
    for th, key in ((0.45, "045"), (0.525, "0525"), (0.60, "060")):
        n = sum(1 for c in conf if c is not None and c > th) + below + unknown
        C["far_fall_a1_alerts_t%s" % key] = n
        C["far_fall_a1_rate_t%s" % key] = round(n / float(hours), 4)
    C["far_fall_a1_line"] = (
        "The A1 pass recorded FallChecker at its deployed decision point "
        "{\\CntFarFallAOneRecordedTheta}, so the three grid points at or above "
        "it are exact over all {\\CntInsituSegments} segments: "
        "{\\CntFarFallAOneRateTZeroFourFive}, "
        "{\\CntFarFallAOneRateTZeroFiveTwoFive} and "
        "{\\CntFarFallAOneRateTZeroSixZero} alerts per hour. "
        "{\\CntFarFallAOneAlertsBelowRecordedTheta} of "
        "{\\CntFarFallAOneAlertsTotal} alerts carried a confidence at or below "
        "the recorded point, which is the count that decides whether the "
        "second disjunct of the decision rule ever fired on its own.")


def count_pipeline_gating():
    """How much of the corpus the detector was never shown, and why that is a
    result rather than a shortfall.

    The deployed pipeline puts a motion filter in front of the detector. On a
    single indoor camera over six days, a large part of the footage is an empty
    room, and on those segments the filter opens for nothing: `ai_frames` is 0,
    the detector runs on no frame at all, and no checker downstream of it can
    fire whatever its threshold. That is the deployment doing what it was built
    to do, and it is the shape of the in-situ evidence -- so it is counted here
    and quoted, instead of being discovered later as an anomaly in the rates.

    Two quantities that are easy to conflate and are NOT the same, so both are
    emitted with names that keep them apart:

        segments_zero_ai_frames   the detector was shown nothing
        segments_zero_alerts      the detector ran and nothing was raised

    The second is much the larger of the two: a segment can hand the detector
    thousands of frames and still produce no alert.
    """
    import glob as _glob
    files = sorted(_glob.glob(os.path.join(RUNS, "m1", "*.json")))
    if not files:
        note("no M1 run metadata under runs/m1: pipeline gating not counted")
        return
    zero_ai = zero_alerts = total = 0
    hours_zero_ai = 0.0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            continue
        total += 1
        if d.get("alerts") == 0:
            zero_alerts += 1
        diag = d.get("diagnostics") or {}
        if diag.get("ai_frames") == 0:
            zero_ai += 1
            fps = float(d.get("fps_effective") or d.get("fps") or 0)
            if fps > 0:
                hours_zero_ai += int(d.get("frames_read") or 0) / fps / 3600.0
    C["segments_measured_for_gating"] = total
    C["segments_zero_ai_frames"] = zero_ai
    C["hours_zero_ai_frames"] = round(hours_zero_ai, 4)
    C["segments_zero_alerts"] = zero_alerts
    C["gating_line"] = (
        "On {\\CntSegmentsZeroAiFrames} of {\\CntSegmentsMeasuredForGating} "
        "segments ({\\CntHoursZeroAiFrames}~h) the motion filter never opened "
        "and the detector was shown no frame at all; on "
        "{\\CntSegmentsZeroAlerts} no alert of any kind was raised. The first "
        "is the deployment's gate doing its job on an empty room, not a gap in "
        "the measurement.")


def count_observation_hours():
    """The one number any in-situ rate may be divided by.

    GT_PROTOCOL 5.8, registered 2026-09-03: **observation hours = the sum of
    frames_read / fps over the segments actually measured**; a manifest
    duration is descriptive only.

    Why there has to be exactly one such number. Two quantities were in
    circulation and they disagreed: the manifest total (what the recorder said
    it wrote) and the decoded total (what the pipeline actually consumed).
    They differ because 10 of the first 77 segments lose between one and ten
    trailing frames to damaged macroblocks in the camera's H.264 stream copy --
    a property of the footage, not a defect. The gap is a few parts in ten
    thousand, which is exactly the size that never gets noticed and never gets
    explained: a corpus table and a false-alarm denominator quoting hours that
    differ in the fourth decimal, with nothing saying which is which.

    So the manifest figure keeps the name `insitu_manifest_hours` and is used
    for describing the collection; `insitu_hours` is the decoded sum and is the
    only denominator. When the two are both quoted the difference is reported,
    not reconciled.
    """
    import glob as _glob
    files = sorted(_glob.glob(os.path.join(RUNS, "m1", "*.json")))
    if not files:
        note("no M1 run metadata under runs/m1: observation hours cannot be "
             "computed, and no in-situ rate may be reported")
        return
    # HARNESS-9, 2026-09-04. The denominator must be built on the clock the
    # run was actually scored on. For eleven segments of 2026-08-31 the
    # container's frame rate is corrupt -- 1.34 fps on one, ~14790 on nine --
    # and the runner scored them on the registered substitution instead
    # (fps_ref = 14.883069, out/duration_corrections.json). Dividing by the
    # container's number would put one segment out by 11x and nine by 990x, in
    # opposite directions, while the corpus total still looked plausible.
    #
    # `fps_effective` is the value used; `fps` is the same number under the
    # older name. Prefer the explicit one, fall back to the old, and say so if
    # they ever disagree -- that disagreement would mean the runner scored on
    # one clock and recorded another.
    corr = _load_duration_corrections()
    secs = 0.0
    frames = 0
    short = 0
    short_frames = 0
    secs_sub = 0.0
    listed_sub = 0        # measured segments named in the corrections table
    flagged_sub = 0       # measured segments whose OUTPUT says an override ran
    native_in_band = 0    # measured segments whose recorded container fps is sane
    native_unverifiable = 0   # old-schema segments: no fps_container_raw to check
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:                                  # noqa: BLE001
            note("unreadable run metadata %s: %s" % (os.path.basename(f), e))
            continue
        fps = float(d.get("fps_effective") or d.get("fps") or 0)
        if d.get("fps_effective") is not None and d.get("fps") is not None:
            if abs(float(d["fps_effective"]) - float(d["fps"])) > 1e-9:
                note("OBSERVATION CLOCK DISAGREES in %s: fps_effective=%r but "
                     "fps=%r. The run was scored on one and is recorded with "
                     "the other; no rate may be reported until this is resolved."
                     % (os.path.basename(f), d["fps_effective"], d["fps"]))
                continue
        fr = int(d.get("frames_read") or 0)
        fif = int(d.get("frames_in_file") or fr)
        if fps <= 0:
            note("run metadata %s has fps=0; excluded from observation time"
                 % os.path.basename(f))
            continue

        seg = os.path.basename(f)[:-5]

        # Two independent readings of "was this segment rescored on a
        # substituted clock": the registered table says which files needed it,
        # the output says which files got it. They are counted separately and
        # required to agree -- see the derived-count block below.
        if d.get("fps_override_applied") is True:
            flagged_sub += 1
        # fps_container_raw is the post-HARNESS-9 name; fps_container is the
        # same number under the name the 2026-09-02 runner used. Segments older
        # than that carry neither, and are counted as unverifiable rather than
        # assumed sane -- which is the whole reason the complement is derived.
        raw = d.get("fps_container_raw", d.get("fps_container"))
        if seg not in corr:
            if raw is None:
                native_unverifiable += 1
            elif 5.0 <= float(raw) <= 60.0:
                native_in_band += 1
            else:
                note("SEGMENT %s is not in the HARNESS-5 table but records "
                     "fps_container_raw=%r, outside [5, 60]. Either the table "
                     "is incomplete or this run is not what it says it is."
                     % (seg, raw))

        if seg in corr:
            listed_sub += 1
            secs_sub += fr / fps
            want = float(corr[seg]["fps_ref"])
            if abs(fps - want) > 1e-4:
                note("SUBSTITUTION NOT APPLIED in %s: scored at %.6f fps, the "
                     "registered HARNESS-5 substitution is %.6f. This segment's "
                     "observation time is wrong by a factor of %.1f."
                     % (seg, fps, want, max(fps, want) / min(fps, want)))
                continue
            # The corrected duration was computed from the decoded frame count;
            # the run must agree with it, or one of the two is not describing
            # this file.
            want_s = float(corr[seg]["new_duration_s"])
            got_s = fr / fps
            if want_s > 0 and abs(got_s - want_s) / want_s > 0.01:
                note("SUBSTITUTED SEGMENT %s: the run observed %.1f s but the "
                     "corrected manifest duration is %.1f s (%.2f%% apart, "
                     "limit 1%%)"
                     % (seg, got_s, want_s, abs(got_s - want_s) / want_s * 100))

        # E4: remember this segment's hours and its clock stratum. Recorded
        # here rather than recomputed later so that the false-alarm strata are
        # divided by exactly the seconds that went into `insitu_hours`.
        _SEG_HOURS[seg] = (fr / fps) / 3600.0
        _SEG_STRATUM[seg] = "substituted" if seg in corr else "native"
        _CHECKER_ROSTER.update((d.get("per_checker_cooldown_s") or {}).keys())
        for m in str(d.get("modules") or "").split(","):
            m = m.strip()
            if m == "helmet":
                # aap_offline_runner.py: helmet_mode "advanced" builds
                # EnhancedHelmetChecker INSTEAD of HelmetChecker, not as well.
                _MEASURED_CHECKERS.add(
                    "EnhancedHelmetChecker" if d.get("helmet_mode") == "advanced"
                    else "HelmetChecker")
            elif m in _MODULE_TO_CHECKER:
                _MEASURED_CHECKERS.add(_MODULE_TO_CHECKER[m])

        secs += fr / fps
        frames += fr
        if fif > fr:
            short += 1
            short_frames += fif - fr

    # ---------------------------------------------------------------- clocks
    # DIRECT COUNT: segments rescored on the registered substitution. Counted
    # from the output files, and cross-checked against the table that named
    # them. Two files, two readings, and they must agree.
    C["insitu_segments_on_substituted_clock"] = listed_sub
    C["insitu_hours_on_substituted_clock"] = round(secs_sub / 3600.0, 4)
    if listed_sub != flagged_sub:
        note("CLOCK PROVENANCE DISAGREES: %d measured segment(s) are named in "
             "the HARNESS-5 table but %d output(s) record fps_override_applied. "
             "One of the two files is wrong about which runs used a substituted "
             "clock; no rate may be reported until they agree."
             % (listed_sub, flagged_sub))

    # DERIVED COUNT (author's decision 2026-09-04). The complement -- segments
    # measured on the container's own clock -- is NOT counted directly, and the
    # supplement must not present it as if it were.
    #
    # Why it cannot be a direct count. The check would be "fps_container_raw is
    # inside [5, 60]", and 52 segments measured 2026-08-27/28 predate that key
    # entirely: the runner of the day recorded `fps` and nothing about where it
    # came from. Counting only the segments that can be checked would report a
    # smaller corpus than was measured; counting the rest as if they had been
    # checked would be the digest-instead-of-a-count error P9 exists to stop.
    #
    # So it is subtraction, from two files that were written for other reasons:
    #   native = |manifest| - |HARNESS-5 substitution table|
    # with the substitution table's membership confirmed segment by segment
    # against the outputs above. It carries its own macro and is never added to
    # or compared with the direct count of 11.
    total_manifest = C.get("insitu_segments")
    if total_manifest:
        C["insitu_segments_native_clock_derived"] = total_manifest - len(corr)
        C["insitu_native_clock_derivation"] = (
            "derived, not counted: %d manifest segments minus %d named in "
            "out/duration_corrections.json (HARNESS-5). Membership of the %d is "
            "confirmed per segment against fps_override_applied in the run "
            "metadata; the complement is not directly verifiable because %d "
            "segments measured before 2026-09-02 record no fps_container_raw."
            % (total_manifest, len(corr), len(corr), native_unverifiable))
    if corr:
        C["insitu_substituted_fps"] = sorted(
            {"%.6f" % float(e["fps_ref"]) for e in corr.values()})[0]
    C["insitu_segments_container_fps_verified_in_band"] = native_in_band
    C["insitu_segments_container_fps_unverifiable"] = native_unverifiable

    C["insitu_observation_segments"] = len(files)
    C["insitu_frames_decoded"] = frames
    C["insitu_seconds"] = round(secs, 3)
    C["insitu_hours"] = round(secs / 3600.0, 4)
    C["insitu_segments_with_trailing_frame_loss"] = short
    C["insitu_trailing_frames_lost"] = short_frames

    total = C.get("insitu_segments")
    if total:
        C["insitu_observation_coverage"] = round(len(files) / float(total), 4)
        if len(files) < total:
            # B8's registered fallback: until M1+ covers the manifest, every
            # in-situ rate is PRELIMINARY and carries its own hours.
            C["insitu_rate_status"] = "PRELIMINARY"
            note("observation time covers %d of %d manifest segments; every "
                 "in-situ rate is PRELIMINARY until this reaches 100%%"
                 % (len(files), total))
        else:
            C["insitu_rate_status"] = "FINAL"
        mh = C.get("insitu_manifest_hours")
        if mh:
            C["insitu_manifest_minus_observation_hours"] = round(
                mh - C["insitu_hours"], 4)


# ------------------------------------------------- E4: false-alarm strata
# PREREGISTERED_E4_CLOCK_STRATUM.md, locked 2026-09-05 10:20:43 +07, SHA256
# 2371fef5b718f76f3702d682f4a07ccf8170c89784deca20e9d5214eeb958885.
#
# Eleven segments of 2026-08-31 08:00-13:00 carry a damaged H.264 bitstream.
# The same damage that made their container frame rate unusable (HARNESS-5)
# makes the decoder report macroblock errors throughout, and a frame rebuilt
# from a wrong reference can raise an alert about something that was never in
# the room. Whether those eleven belong in the in-situ false-alarm rate is
# therefore a question about the RECORDER, and it is settled by the rule
# registered in E4 section 2.3 -- never by looking at the numbers first.
#
# Nothing here is a judgement call. The flag below is computed; there is no
# code path by which a person sets it.

_POISSON_2S_95_ZERO = 3.689     # GT_PROTOCOL P6, two-sided, zero observed
_E4_BOOTSTRAP_SEED = 20260905   # fixed in E4 section 2.2
_CI_LEVEL_PERCENT = 95          # two-sided, GT_PROTOCOL P6 and E4 2.2
_E5_PREREG_SHA = "60aaa61bea38cbc54388c250107942f4ac96dbbbdf1f00b2793d43748ae8c41a"
_E4_BOOTSTRAP_ITERS = 10000
_E4_SUBSTITUTED_N = 11          # the HARNESS-5 table's size, asserted not assumed
_E4_PREREG_SHA = "2371fef5b718f76f3702d682f4a07ccf8170c89784deca20e9d5214eeb958885"


def _block_bootstrap_ci(counts, hours, seed):
    """95% CI on a rate by resampling whole SEGMENTS.

    The same estimator tier0_analysis.py uses, and for the same reason: alerts
    inside one segment are correlated (one person walking through fires many),
    across segments much less so. Resampling individual alerts would assert an
    independence the data does not have and return an interval that is too
    tight -- which, for a rule that decides whether a stratum is separated,
    would bias toward separating.
    """
    import random
    n = len(counts)
    if n == 0:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    idx = range(n)
    out = []
    for _ in range(_E4_BOOTSTRAP_ITERS):
        pick = [rng.choice(idx) for _ in range(n)]
        h = sum(hours[i] for i in pick)
        if h > 0:
            out.append(sum(counts[i] for i in pick) / h)
    if not out:
        return (float("nan"), float("nan"))
    out.sort()
    return (out[int(0.025 * len(out))], out[int(0.975 * len(out))])


def _far_by_checker(segments):
    """Per-checker alert counts over a set of segments, read from the rows.

    Counted from `runs/m1/<seg>.csv`, one row per dispatched alert, which is
    the same file the reconciliation reads. A segment with a metadata file but
    no CSV is not silently treated as zero -- it is reported and the stratum is
    marked incomplete, because "measured and quiet" and "not measured" are
    different facts and a rate cannot tell them apart afterwards.
    """
    per = collections.Counter()
    seg_rows = {}
    missing = []
    for seg in segments:
        cp = os.path.join(RUNS, "m1", seg + ".csv")
        if not os.path.exists(cp):
            missing.append(seg)
            continue
        n = collections.Counter()
        try:
            with open(cp, encoding="utf-8", newline="") as fh:
                for row in csv.DictReader(fh):
                    n[row["checker"]] += 1
        except Exception as e:                                  # noqa: BLE001
            note("unreadable prediction file %s: %s" % (os.path.basename(cp), e))
            missing.append(seg)
            continue
        seg_rows[seg] = n
        per.update(n)
    return per, seg_rows, missing


def count_far_strata():
    """The three in-situ false-alarm figures, and the E4 separation flag."""
    if not _SEG_HOURS:
        note("no per-segment observation time: the E4 clock strata cannot be "
             "formed and no false-alarm rate may be reported")
        return

    corr = _load_duration_corrections()
    sub_segs = sorted(k for k, v in _SEG_STRATUM.items() if v == "substituted")
    nat_segs = sorted(k for k, v in _SEG_STRATUM.items() if v == "native")

    C["e4_prereg_sha256"] = _E4_PREREG_SHA
    C["far_subst_n"] = len(sub_segs)
    C["far_native_n"] = len(nat_segs)
    C["far_pooled_n"] = len(sub_segs) + len(nat_segs)
    C["far_subst_hours"] = round(sum(_SEG_HOURS[x] for x in sub_segs), 4)
    C["far_native_hours"] = round(sum(_SEG_HOURS[x] for x in nat_segs), 4)
    C["far_pooled_hours"] = round(C["far_subst_hours"] + C["far_native_hours"], 4)

    # Completeness, E4 section 2.4. The rule is evaluated ONCE, on both strata
    # complete. Evaluating it on the segments that happen to be finished would
    # make the answer depend on a sentinel's file order.
    total_manifest = C.get("insitu_segments") or 0
    want_sub = len(corr) or _E4_SUBSTITUTED_N
    want_nat = (total_manifest - len(corr)) if total_manifest else 0
    complete = (len(sub_segs) == want_sub and want_nat > 0
                and len(nat_segs) == want_nat)

    sub_per, sub_rows, sub_missing = _far_by_checker(sub_segs)
    nat_per, nat_rows, nat_missing = _far_by_checker(nat_segs)
    if sub_missing or nat_missing:
        complete = False
        note("E4: %d segment(s) have run metadata but no prediction CSV "
             "(%s ...); the clock strata are incomplete and the separation "
             "flag stays [TBD]"
             % (len(sub_missing) + len(nat_missing),
                ", ".join((sub_missing + nat_missing)[:3])))

    roster = sorted(_CHECKER_ROSTER | set(sub_per) | set(nat_per))
    C["far_checker_roster"] = ", ".join(roster)
    C["far_ci_level_percent"] = _CI_LEVEL_PERCENT
    C["far_checkers_n_word"] = word(len(roster))
    C["far_checkers_n"] = len(roster)
    # The roster is the configuration table; this is what the pass built. The
    # gap between the two is a fact the results table has to carry, because a
    # zero in one column and a blank in the other are different claims.
    measured = sorted(_MEASURED_CHECKERS & set(roster))
    unmeasured = sorted(set(roster) - _MEASURED_CHECKERS)
    C["far_checkers_measured"] = ", ".join(measured) or "none"
    C["far_checkers_measured_n"] = len(measured)
    C["far_checkers_not_measured"] = ", ".join(unmeasured) or "none"
    C["far_checkers_not_measured_n"] = len(unmeasured)
    C["far_checkers_measured_n_word"] = word(len(measured))
    C["far_checkers_not_measured_n_word"] = word(len(unmeasured))

    # E5, locked 2026-09-06. The roster is seven; five were instantiated in the
    # recorded pass; of those five one is FAR-only because no open video corpus
    # exists for its coverage, leaving four candidates for the allocation.
    # Admission of those four is governed by M3 and is not decided here -- this
    # is the denominator, not the roster of admitted channels.
    C["e5_prereg_sha256"] = _E5_PREREG_SHA
    C["e5_label"] = "E5"
    C["e5_far_only"] = "HelmetChecker"
    C["e5_far_only_n"] = 1
    C["e5_allocation_candidates"] = ("FallChecker, IntrusionChecker, "
                                     "RunningChecker, SmokeFireChecker")
    C["e5_allocation_candidates_n"] = len(measured) - 1
    C["e5_uninstantiated_note"] = "not instantiated in the recorded pass"
    # Spelled out, and spelled out FROM THE COUNTS: a sentence that says
    # "seven" while the roster says 7 is a number typed by hand wearing a word.
    C["e5_channels_line"] = (
        "%s detection channels; %s active in the recorded pass; %s "
        "(enhanced-helmet variant, forklift speed) never instantiated in this "
        "deployment and reported as not measured"
        % (word(len(roster)), word(len(measured)), word(len(unmeasured))))

    hs = C["far_subst_hours"]
    hn = C["far_native_hours"]
    hp = C["far_pooled_hours"]

    triggers = []
    undecidable = []
    for ck in roster:
        ns, nn = sub_per.get(ck, 0), nat_per.get(ck, 0)
        key = re.sub(r"[^a-z0-9]+", "_", ck.lower()).strip("_")
        C["far_%s_subst_alerts" % key] = ns
        C["far_%s_native_alerts" % key] = nn
        C["far_%s_pooled_alerts" % key] = ns + nn
        if hs > 0:
            C["far_%s_subst_rate" % key] = round(ns / hs, 4)
        if hn > 0:
            C["far_%s_native_rate" % key] = round(nn / hn, 4)
        if hp > 0:
            C["far_%s_pooled_rate" % key] = round((ns + nn) / hp, 4)

        # The E4 interval: Poisson where the count is zero, segment block
        # bootstrap where it is not. Same practice as everywhere else in this
        # corpus; the only thing E4 fixes is the seed.
        if hs <= 0:
            lo = hi = float("nan")
            method = "undefined (no substituted observation time)"
        elif ns == 0:
            lo, hi = 0.0, _POISSON_2S_95_ZERO / hs
            method = "poisson-2s-95"
        else:
            counts = [sub_rows.get(x, {}).get(ck, 0) for x in sub_segs]
            hours = [_SEG_HOURS[x] for x in sub_segs]
            lo, hi = _block_bootstrap_ci(counts, hours, _E4_BOOTSTRAP_SEED)
            method = "block-bootstrap-95"
        C["far_%s_subst_ci_method" % key] = method
        if lo == lo and hi == hi:                       # not NaN
            C["far_%s_subst_ci_lo" % key] = round(lo, 4)
            C["far_%s_subst_ci_hi" % key] = round(hi, 4)

        # The POOLED interval, by the same two rules and the same seed. E4
        # fixes the interval for the stratum comparison; the reported in-situ
        # rate needs one too, and it must not be computed by a second reader
        # with a second convention -- that is how a paper ends up with two
        # intervals on the same number.
        if hp > 0:
            if ck not in _MEASURED_CHECKERS:
                # No observation, so no interval. Not zero: absent.
                C["far_%s_pooled_ci_method" % key] = "not measured in this pass"
            elif ns + nn == 0:
                C["far_%s_pooled_ci_lo" % key] = 0.0
                C["far_%s_pooled_ci_hi" % key] = round(_POISSON_2S_95_ZERO / hp, 4)
                C["far_%s_pooled_ci_method" % key] = "poisson-2s-95"
            else:
                counts = [sub_rows.get(x, {}).get(ck, 0) for x in sub_segs] + \
                         [nat_rows.get(x, {}).get(ck, 0) for x in nat_segs]
                hours = [_SEG_HOURS[x] for x in sub_segs + nat_segs]
                plo, phi = _block_bootstrap_ci(counts, hours, _E4_BOOTSTRAP_SEED)
                C["far_%s_pooled_ci_lo" % key] = round(plo, 4)
                C["far_%s_pooled_ci_hi" % key] = round(phi, 4)
                C["far_%s_pooled_ci_method" % key] = "block-bootstrap-95"

        if not complete:
            continue
        if lo != lo or hi != hi or hn <= 0:
            undecidable.append(ck)
            continue
        if not (lo <= nn / hn <= hi):
            triggers.append(ck)

    # ------------------------------------------------------------- the flag
    # E4 section 2.3: ONE flag for all checkers. A single checker whose native
    # point estimate falls outside the substituted stratum's interval separates
    # all eleven segments for every checker -- otherwise the same segments
    # would be inside the corpus for one rate and outside it for another, which
    # is not a corpus.
    if not complete:
        C["flag_subst_stratum_separated"] = "[TBD]"
        C["far_flag_basis"] = (
            "[TBD]: E4 2.4 requires both strata complete before the rule is "
            "evaluated. Have %d/%d substituted and %d/%d native segments."
            % (len(sub_segs), want_sub, len(nat_segs), want_nat))
        note("E4 separation flag is [TBD]: %d/%d substituted and %d/%d native "
             "segments measured. No branch of E4 section 6 may be quoted."
             % (len(sub_segs), want_sub, len(nat_segs), want_nat))
    elif undecidable:
        C["flag_subst_stratum_separated"] = "[TBD]"
        C["far_flag_basis"] = (
            "[TBD]: no usable interval for %s. E4 2.5 -- an undefined interval "
            "never silently becomes false." % ", ".join(undecidable))
        note("E4 separation flag is [TBD]: undefined interval for %s"
             % ", ".join(undecidable))
    elif triggers:
        C["flag_subst_stratum_separated"] = "true"
        C["far_flag_trigger_checkers"] = ", ".join(triggers)
        C["far_flag_basis"] = (
            "true: the native point estimate lies outside the substituted "
            "stratum's 95%% interval for %s (E4 2.3). The %d substituted "
            "segments are a recorder artefact; headline observation time is "
            "the %d native segments."
            % (", ".join(triggers), len(sub_segs), len(nat_segs)))
    else:
        C["flag_subst_stratum_separated"] = "false"
        C["far_flag_trigger_checkers"] = "none"
        C["far_flag_basis"] = (
            "false: for every one of the %d checkers the native point estimate "
            "lies inside the substituted stratum's 95%% interval (E4 2.3). The "
            "pooled %d segments are the headline in-situ FAR."
            % (len(roster), len(sub_segs) + len(nat_segs)))

    # The power of the rule, reported alongside it rather than discovered later
    # (E4 2.6): a 5.5 h stratum cannot adjudicate a rate of a tenth per hour.
    if hs > 0:
        C["far_subst_zero_count_upper_limit"] = round(_POISSON_2S_95_ZERO / hs, 4)
    if hp > 0:
        C["far_pooled_zero_count_upper_limit"] = round(_POISSON_2S_95_ZERO / hp, 4)


# ---------------------------------------------------------------- in situ
def count_insitu():
    p = os.path.join(ANALYSIS, "tier0", "manifest_rows_closed.csv")
    if not os.path.exists(p):
        note("in-situ manifest not found at %s" % p)
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    secs = sum(float(r["duration_s"]) for r in rows)
    byday = collections.Counter()
    for r in rows:
        byday[r["capture_date"]] += float(r["duration_s"])
    C["insitu_segments"] = len(rows)
    # DESCRIPTIVE ONLY. This is what the recorder wrote down about the footage
    # it collected. It is NOT the denominator of any rate -- see
    # count_observation_hours() below and GT_PROTOCOL 5.8.
    C["insitu_manifest_seconds"] = round(secs, 3)
    C["insitu_manifest_hours"] = round(secs / 3600.0, 4)
    C["insitu_days"] = len(byday)
    C["insitu_first_segment"] = min(r["file"] for r in rows)
    C["insitu_last_segment"] = max(r["file"] for r in rows)

    q = os.path.join(ANALYSIS, "live_alert_index_20260902.csv")
    if os.path.exists(q):
        n = 0
        types = collections.Counter()
        with open(q, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                n += 1
                types[r["event_type"]] += 1
        C["insitu_alert_index_rows"] = n
        C["insitu_alert_types"] = dict(types)
    else:
        note("live alert index not found")


# ---------------------------------------------------------------- ex situ
def count_gmdcsa24():
    p = os.path.join(EXSITU, "CLIPLIST_gmdcsa24.csv")
    if not os.path.exists(p):
        note("GMDCSA24 clip list not found")
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    C["gmdcsa24_clips"] = len(rows)
    C["gmdcsa24_clips_with_fall"] = sum(1 for r in rows if r["has_fall"] == "1")
    C["gmdcsa24_clips_without_fall"] = sum(1 for r in rows if r["has_fall"] == "0")
    C["gmdcsa24_annotation_segments"] = sum(int(r["n_segments"]) for r in rows)
    C["gmdcsa24_subjects"] = len({r["subject"] for r in rows})
    C["gmdcsa24_bytes"] = sum(int(r["size_bytes"]) for r in rows)
    h = os.path.join(EXSITU, "CLIPLIST_gmdcsa24.sha256")
    if os.path.exists(h):
        C["gmdcsa24_cliplist_sha256"] = open(h, encoding="utf-8").read().split()[0]

    # formats and the section 8.8 grid, from the paired probe (decoded, authoritative)
    q = os.path.join(EXSITU, "PAIR_PROBE_gmdcsa24.csv")
    if os.path.exists(q) and os.path.getsize(q) > 0:
        pr = list(csv.DictReader(open(q, encoding="utf-8")))
        res = collections.Counter("%sx%s" % (r["nat_w"], r["nat_h"]) for r in pr)
        C["gmdcsa24_native_resolutions"] = dict(res)
        C["gmdcsa24_probe_rows"] = len(pr)

        def _i(x):
            try:
                return int(x)
            except (TypeError, ValueError):
                return None

        cells = collections.Counter()
        deltas = []
        same_fps_string = 0
        for r in pr:
            res_ch = (r["nat_w"], r["nat_h"]) != (r["adp_w"], r["adp_h"])
            na, ab = _i(r["nat_nb_read_frames"]), _i(r["adp_nb_read_frames"])
            fr_ch = (na is None or ab is None or na != ab)
            cells[("res_changed" if res_ch else "res_same",
                   "frames_changed" if fr_ch else "frames_same")] += 1
            if r["nat_avg_fps"] == r["adp_avg_fps"]:
                same_fps_string += 1
            try:
                deltas.append(abs(float(r["nat_duration"]) - float(r["adp_duration"])))
            except (TypeError, ValueError):
                pass
        C["gmdcsa24_grid"] = {"%s|%s" % k: v for k, v in cells.items()}
        C["gmdcsa24_control_cell_clips"] = cells[("res_same", "frames_same")]
        C["gmdcsa24_clips_identical_fps_string"] = same_fps_string
        if deltas:
            deltas.sort()
            C["gmdcsa24_duration_delta_max_s"] = round(deltas[-1], 4)
            C["gmdcsa24_duration_delta_median_s"] = round(deltas[len(deltas) // 2], 4)
            C["gmdcsa24_clips_delta_over_one_frame"] = sum(1 for d in deltas if d > 1 / 15.0)
    else:
        note("PAIR_PROBE_gmdcsa24.csv missing or empty; native format "
             "distribution and the section 8.8 grid not counted this run")


def count_furg():
    p = os.path.join(EXSITU, "CLIPLIST_furg.csv")
    if not os.path.exists(p):
        note("FURG clip list not found")
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    C["furg_clips"] = len(rows)
    strat = collections.Counter(r["camera_stratum"] for r in rows)
    C["furg_clips_by_stratum"] = dict(strat)
    ev = collections.Counter()
    sec = collections.defaultdict(float)
    for r in rows:
        ev[r["camera_stratum"]] += int(r["gt_events"])
        sec[r["camera_stratum"]] += float(r["gt_seconds"])
    C["furg_gt_events_by_stratum"] = dict(ev)
    C["furg_gt_events_total"] = sum(ev.values())
    C["furg_gt_seconds_by_stratum"] = {k: round(v, 2) for k, v in sec.items()}
    C["furg_formats"] = dict(collections.Counter(
        "%sx%s@%sfps" % (r["width"], r["height"], r["frame_rate"]) for r in rows))
    C["furg_gt_class"] = "fire only; no smoke annotation in this corpus"
    h = os.path.join(EXSITU, "CLIPLIST_furg.sha256")
    if os.path.exists(h):
        C["furg_cliplist_sha256"] = open(h, encoding="utf-8").read().split()[0]


def count_omnifall_annotations():
    """Counted from the annotation files we actually downloaded and use."""
    d = r"D:\AAP_exsitu_data\omnifall_ann"
    if not os.path.isdir(d):
        note("OmniFall annotation directory not present; annotation counts skipped")
        return
    out = {}
    for f in sorted(os.listdir(d)):
        if not f.startswith("labels_") or not f.endswith(".csv"):
            continue
        rows = list(csv.DictReader(open(os.path.join(d, f), encoding="utf-8")))
        name = f[len("labels_"):-4]
        if name == "label2id":
            C["omnifall_taxonomy_classes"] = len(rows)
            continue
        out[name] = {"segments": len(rows),
                     "clips": len({r["path"] for r in rows if "path" in r})}
    if out:
        C["omnifall_annotation_files"] = out


# ---------------------------------------------------------------- results
def count_results():
    p = os.path.join(EXSITU, "SCORE_gmdcsa24_native.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        for mode in ("strict", "extended"):
            r = d["results"][mode]
            C["exsitu_gmdcsa24_native_%s_gt" % mode] = r["gt_events"]
            C["exsitu_gmdcsa24_native_%s_tp" % mode] = r["tp"]
            C["exsitu_gmdcsa24_native_%s_fp" % mode] = r["fp"]
            C["exsitu_gmdcsa24_native_%s_recall" % mode] = round(r["recall"], 4)
    else:
        note("native ex-situ score not found")

    p = os.path.join(ANALYSIS, "tier0", "tier0_results.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        C["tier0_corpus_hours"] = round(d["corpus"]["hours"], 4)
        src = d["corpus"].get("hours_source") or {}
        C["tier0_corpus_hours_source"] = src
        # THE INVARIANT, asserted rather than asserted-in-prose. Once every
        # manifest segment has been measured, the corpus table's hours and the
        # false-alarm denominator are the same quantity computed the same way,
        # and they must agree. Two hour figures differing in the fourth decimal
        # is exactly the discrepancy nobody notices; this is what stops it
        # existing rather than what explains it afterwards.
        if C.get("insitu_observation_coverage") == 1.0:
            gap = abs(C["tier0_corpus_hours"] - C.get("insitu_hours", 0))
            if gap > 0.01:
                note("OBSERVATION-TIME INVARIANT VIOLATED: tier0 corpus "
                     "%.4f h against the decoded denominator %.4f h "
                     "(%.4f h apart). One of them is not "
                     "sum(frames_read/fps). No rate may be reported until "
                     "this is resolved."
                     % (C["tier0_corpus_hours"], C["insitu_hours"], gap))
            else:
                C["insitu_hours_invariant"] = "OK (single source, agree to %.4f h)" % gap
        elif src.get("manifest"):
            note("tier0 corpus hours is still MIXED: %d segment(s) decoded, "
                 "%d from the manifest. It is not the false-alarm denominator "
                 "and must not be quoted as one."
                 % (src.get("decoded", 0), src.get("manifest", 0)))
        C["tier0_corpus_segments"] = d["corpus"]["segments"]
        C["tier0_in_corpus_alerts"] = sum(d["result1_in_corpus"].values())
        # The DEPLOYED column of the IV.A table: what the operator's own system
        # raised inside the same window, over the same denominator. Divided
        # here rather than in the manuscript, because a rate typed into prose
        # is a number nobody recounts.
        if C.get("tier0_corpus_hours"):
            C["tier0_in_corpus_rate"] = round(
                C["tier0_in_corpus_alerts"] / C["tier0_corpus_hours"], 4)
        ci = d.get("result1_in_corpus_rate_ci") or []
        if len(ci) == 2:
            C["tier0_in_corpus_rate_ci_lo"] = round(ci[0], 4)
            C["tier0_in_corpus_rate_ci_hi"] = round(ci[1], 4)
        C["tier0_in_corpus_channels"] = ", ".join(sorted(d["result1_in_corpus"])) or "none"
        # Per-channel deployed counts for the IV.A table. A channel absent from
        # the live index raised nothing inside the window, and that zero is a
        # COUNT -- it belongs in a macro like every other number in Results.
        # Typing "0" into the table would be a hand-typed number in the one
        # section where P9-c forbids them, and rightly: a zero is the easiest
        # number to write down without checking.
        _EVENT_TO_CHECKER = {
            "intrusion": "IntrusionChecker",
            "no_helmet": "HelmetChecker",
            "fall": "FallChecker",
            "smoke_fire": "SmokeFireChecker",
            "running": "RunningChecker",
            "forklift_speed": "ForkliftSpeedChecker",
        }
        live = collections.Counter()
        for ev, n in d["result1_in_corpus"].items():
            live[_EVENT_TO_CHECKER.get(ev, ev)] += n
        for ck in sorted(_CHECKER_ROSTER) or sorted(live):
            key = re.sub(r"[^a-z0-9]+", "_", ck.lower()).strip("_")
            C["far_deployed_%s_alerts" % key] = live.get(ck, 0)
            if C.get("tier0_corpus_hours"):
                C["far_deployed_%s_rate" % key] = round(
                    live.get(ck, 0) / C["tier0_corpus_hours"], 4)
        C["tier0_in_corpus_channels_n"] = len(d["result1_in_corpus"])
        C["tier0_full_history_alerts"] = sum(d["result1_full_history"].values())
        C["tier0_full_history_channels_n"] = len(d["result1_full_history"])
        C["tier0_dispersion_ratio"] = round(
            d["result2_dispersion"]["chi2"] / d["result2_dispersion"]["dof"], 1)
    else:
        note("tier0 results not found")


# ---------------------------------------------------------------- emit
_DIGIT_WORD = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
               "5": "Five", "6": "Six", "7": "Seven", "8": "Eight", "9": "Nine"}


def count_prose():
    """The three sentences the clock substitution obliges the paper to carry.

    P9 says no countable quantity is typed by hand. A sentence that CONTAINS
    countable quantities is the same problem wearing prose: "11 of 175 segments
    (5.5 h)" typed into a supplement goes stale the moment a segment is added,
    and nothing checks it. So the sentences are macros too, and their numbers
    are references to the macros that hold those numbers -- edit the corpus and
    the sentence follows, or fails to compile, which is the point.

    Braces around each reference because TeX swallows the space after a control
    word: `\\CntInsituSegments segments` typesets "175segments".

    These are for the TIM manuscript. The elsarticle tree is frozen and is not
    touched.
    """
    C["deviation_line_clock"] = (
        r"Container fps of {\CntInsituSegmentsOnSubstitutedClock}/"
        r"{\CntInsituSegments} segments ({\CntInsituHoursOnSubstitutedClock}~h) "
        r"lies outside [5,~60]; their observation time uses the decoded fps "
        r"{\CntInsituSubstitutedFps} fixed before rescoring (HARNESS-5/9).")

    C["derived_line_native_clock"] = (
        r"The complement, {\CntInsituSegmentsNativeClockDerived} segments on the "
        r"container's own clock, is DERIVED by subtraction from the manifest and "
        r"the registered substitution table, not counted directly: "
        r"{\CntInsituSegmentsContainerFpsVerifiedInBand} segments record the "
        r"container rate and are confirmed inside the band, while "
        r"{\CntInsituSegmentsContainerFpsUnverifiable} measured before the "
        r"HARNESS-5 fix record no container rate at all and cannot be checked "
        r"individually. It is reported as a derived count and is never pooled "
        r"with the {\CntInsituSegmentsOnSubstitutedClock} substituted segments.")

    # ------------------------------------------------ E4, both branches
    # PREREGISTERED_E4_CLOCK_STRATUM.md section 6. Both sentences are written
    # out whatever the flag says, and the flag chooses between them. The point
    # of writing both before the flag can be computed is that neither can then
    # be drafted to suit the answer -- and the point of emitting both after it
    # is computed is that a reader can see the sentence that was not used.
    C["deviation_line_subst_separated"] = (
        r"{\CntFarSubstN} of {\CntInsituSegments} segments recorded 2026-08-31 "
        r"08:00--13:00 carry a damaged H.264 bitstream: the container frame "
        r"rate is unusable (HARNESS-5) and the decoder reports macroblock "
        r"errors throughout. Their alert rate is separated from the in-situ "
        r"false-alarm rate under pre-registration E4 as a \emph{recorder "
        r"artefact}, the pre-registered comparison having placed the native "
        r"point estimate outside the stratum's 95\% interval. The reported "
        r"in-situ observation time is the {\CntFarNativeN} native segments "
        r"({\CntFarNativeHours}~h); the separated stratum is reported in full, "
        r"with its own interval, in the supplement.")

    C["deviation_line_subst_pooled"] = (
        r"{\CntFarSubstN} of {\CntInsituSegments} segments recorded 2026-08-31 "
        # No internal identifiers on the page: a reader of the article cannot
        # resolve "HARNESS-5" or "E4" (self-containment check, 2026-09-14).
        r"08:00--13:00 carry a damaged H.264 bitstream and were rescored on a "
        r"substituted clock, a frame rate registered before rescoring. The "
        r"pre-registered test did not distinguish their alert rate from the native stratum's "
        r"for any of the {\CntFarCheckersN} checkers, so they remain "
        r"\emph{pooled} in the reported in-situ false-alarm rate over all "
        r"{\CntFarPooledN} segments ({\CntFarPooledHours}~h); the per-stratum "
        r"figures are given in the supplement.")

    C["harness_sentence_subst_separated"] = (
        r"A recorder that stores its camera's bitstream untouched preserves the "
        r"damage along with the picture, and a detector cannot tell a "
        r"reconstructed macroblock from a room: the defect that made "
        r"{\CntFarSubstN} segments lie about their frame rate is the same defect "
        r"that makes their alerts a measurement of the recorder.")

    C["harness_sentence_subst_pooled"] = (
        r"The {\CntFarSubstN} segments whose container timing was unusable "
        r"produced alerts at a rate the pre-registered test could not "
        r"distinguish from the rest of the corpus, so the damage that corrupted "
        r"their timing did not measurably reach the detector --- a negative "
        r"result worth reporting, because the rule that would have removed them "
        r"was written before it was known which way it would fall.")

    # The selected pair. While the flag is [TBD] these expand to an UNDEFINED
    # control sequence, so a manuscript that tries to typeset a result E4 has
    # not decided yet fails the build instead of printing a sentence nobody is
    # entitled to yet. That is the build gate, not a comment asking for care.
    flag = C.get("flag_subst_stratum_separated")
    if flag == "true":
        C["deviation_line_subst_stratum"] = r"\CntDeviationLineSubstSeparated"
        C["harness_sentence_subst_stratum"] = r"\CntHarnessSentenceSubstSeparated"
    elif flag == "false":
        C["deviation_line_subst_stratum"] = r"\CntDeviationLineSubstPooled"
        C["harness_sentence_subst_stratum"] = r"\CntHarnessSentenceSubstPooled"
    else:
        C["deviation_line_subst_stratum"] = r"\SubstStratumUndecidedSeeE"
        C["harness_sentence_subst_stratum"] = r"\SubstStratumUndecidedSeeE"

    C["harness_sentence_clock"] = (
        r"A guard that is correct at the layer it protects can still deadlock "
        r"the whole system when no layer owns what it refuses: REFUSING is a "
        r"perfect sentence to say to a person, and an unattended pass has no "
        r"person in it.")


def count_characterizability():
    """Per channel: is a FAR measurable, is a coverage measurable, and if not why.

    THIS IS THE RESULT THAT CHANGED SHAPE ON 2026-09-09, so it is counted
    rather than written.

    The paper's asymmetry was stated as "a deployment gives a false-alarm rate
    for free and never gives coverage". Measuring seven channels showed the
    sharper claim: MOST CHANNELS CANNOT BE CHARACTERISED AT ALL, and each one
    fails for a DIFFERENT reason. The reasons are the finding, so they are
    enumerated here as a closed vocabulary and rendered into the manuscript
    table; a channel whose reason is not in the vocabulary is a channel nobody
    has thought about yet, and the assertion at the end of this function makes
    that loud.

    Nothing here decides anything: every cell is read off an artefact that
    already exists, or is marked TBD because the artefact does not.
    """
    # The closed vocabulary. Adding a reason means adding a row to Table
    # tab:characterizability and saying so in the caption.
    REASONS = {
        "measured": "characterised",
        "coverage_zero": "coverage measured and equal to zero",
        # E9 2.4 branch 2, fired 2026-09-10 16:27. The positive control
        # raised ZERO alerts at conf 0.01, a point deliberately far below
        # the registered grid, on the same 23 clips. The registered rule
        # is that no conclusion about coverage may then be drawn: the
        # channel's alert path has never been shown to fire on any input,
        # in situ or ex situ, so its zero measures the harness and not the
        # world. "Measured zero" and "uncharacterised" are different
        # claims and this is the second.
        "uncharacterised_no_positive_control": "coverage NOT measured: the channel's alert path has never been shown to fire on any input, so a zero here cannot be distinguished from an inert path",
        # X3b is the mirror image and is kept separate for that reason.
        "awaiting_registered_scoring": "the pass ran and the checker executed, so the zero is a measurement; the coverage number itself awaits the registered scorer",
        "side_channel": "checker never invoked: it consumes another module's "
                        "detections and was run in isolation",
        "no_far_denominator": "no false-alarm denominator: the label pack that "
                              "supplies the false-positive fraction is unfilled",
        "no_channel_coverage_curve": "a false-alarm rate now exists, but coverage does so only at the detector layer: there is no channel-level coverage at the registered operating points, which is what the allocation compares",
        "never_instantiated": "never constructed in the recorded pass",
        "unvalidated_path": "alert path never shown to fire on any input",
        "far_only_by_design": "false-alarm only by pre-registration E5: no "
                              "admissible ex-situ source exists for its event",
    }
    # A table cell in a two-column IEEE layout has room for a label, not for a
    # sentence: the first version of Table tab:characterizability overflowed by
    # 245.7pt and the gate P9-b then correctly reported that a generated value
    # never reached the page. Short forms go in the table, the sentences go in
    # the prose beside it, and both come from the same dictionary.
    SHORT = {
        "measured": "yes",
        "coverage_zero": "coverage = 0",
        "uncharacterised_no_positive_control": "uncharacterised",
        "awaiting_registered_scoring": "measured 0, unscored",
        "side_channel": "checker never invoked",
        "no_far_denominator": "no FAR denominator",
        "no_channel_coverage_curve": "no channel coverage curve",
        "never_instantiated": "never constructed",
        "unvalidated_path": "alert path unvalidated",
        "far_only_by_design": "FAR-only (E5)",
    }
    # A channel outside the allocation is not necessarily BLOCKED. Helmet is
    # outside it by a decision taken in E5, with its reason already registered;
    # counting that as a blocked channel would inflate the headline and put a
    # deliberate scope choice in the same column as a defect.
    NOT_BLOCKED = {"measured", "far_only_by_design"}

    # (channel, far?, far source, coverage?, coverage source, in allocation?, reason)
    # far/coverage are "yes", "no" or "tbd".
    rows = [
        ("FallChecker", "yes", "insitu_native", "yes", "exsitu_gmdcsa24",
         "yes", "measured"),
        # 2026-09-10. The 100-image pack came back 100 YES / 0 NO / 0 UNSURE,
        # so this channel HAS a false-alarm denominator for the first time and
        # `no_far_denominator` is no longer true of it. It still does not enter
        # the allocation, and the reason has changed rather than gone away: its
        # coverage is Layer-1 person recall on a public split, which is the
        # DETECTOR's accuracy, not the channel's coverage of intrusion events at
        # the registered operating points. Fall's coverage is events matched
        # under W = 2.0 s at each theta; the two are not the same object and
        # allocating across them would compare a detector with a channel.
        ("IntrusionChecker", "yes", "insitu_labelled_fp", "yes", "layer1_coco",
         "tbd", "no_channel_coverage_curve"),
        # 2026-09-10, E9 2.4 branch 2. Coverage moves from "yes" to "no":
        # the FURG zeros are no longer a coverage measurement, because the
        # positive control that would have licensed reading them as one came
        # back empty. The channel leaves the allocation. This is the registered
        # branch, written before the run, and it is executed here rather than
        # renegotiated -- the whole point of writing both branches down in
        # advance was that the unwelcome one would still be followed.
        ("SmokeFireChecker", "yes", "insitu_zero", "no", "exsitu_furg_void",
         "no", "uncharacterised_no_positive_control"),
        # 2026-09-10, E9 1.4 branch 1. X3b executed the checker 214,715 times
        # against X3's zero, so the zero it returns is a MEASUREMENT and the
        # HARNESS-24 architectural defect is repaired. Coverage therefore moves
        # to "yes". It is not yet a NUMBER: score_exsitu.py is hard-coded to
        # FallChecker and to a 30 s merge gap, while VIRAT's registered gap is
        # 20 s, so the registered scorer cannot yet be pointed at it. The
        # arithmetic is forced -- zero alerts admits no true positive -- but a
        # forced number is still a number this campaign runs through its scorer
        # rather than asserts.
        ("RunningChecker", "yes", "insitu_zero", "yes", "exsitu_virat_x3b",
         "tbd", "awaiting_registered_scoring"),
        ("HelmetChecker", "yes", "insitu_declared", "no", "none_admissible",
         "no", "far_only_by_design"),
        ("EnhancedHelmetChecker", "no", "never_run", "no", "never_run",
         "no", "never_instantiated"),
        ("ForkliftSpeedChecker", "no", "never_run", "no", "never_run",
         "no", "never_instantiated"),
    ]

    for ch, far, far_src, cov, cov_src, alloc, reason in rows:
        if reason not in REASONS:
            sys.stderr.write(
                "characterizability: %s carries reason %r, which is not in "
                "the closed vocabulary %s\n" % (ch, reason, sorted(REASONS)))
            raise SystemExit(2)
        key = re.sub(r"[^a-z0-9]+", "_", ch.lower()).strip("_")
        C["char_%s_far" % key] = far
        C["char_%s_far_source" % key] = far_src
        C["char_%s_coverage" % key] = cov
        C["char_%s_coverage_source" % key] = cov_src
        C["char_%s_allocation" % key] = alloc
        C["char_%s_reason" % key] = REASONS[reason]
        C["char_%s_reason_short" % key] = SHORT[reason]
        C["char_%s_reason_key" % key] = reason

    blocked = [r for r in rows if r[6] not in NOT_BLOCKED]
    C["char_channels_n"] = len(rows)
    C["char_far_measurable_n"] = sum(1 for r in rows if r[1] == "yes")
    C["char_coverage_measurable_n"] = sum(1 for r in rows if r[3] == "yes")
    C["char_in_allocation_n"] = sum(1 for r in rows if r[5] == "yes")
    # THE NUMBER THAT ACTUALLY GOVERNS THE ALLOCATION, and it is not the one
    # above. A channel is admitted when it has both axes; it CONTRIBUTES only
    # when its front is non-degenerate -- more coverage available at more cost.
    # Fall has three real points. Running, if the scorer confirms the forced
    # zero, has one point at zero coverage and zero cost, which no budget can
    # ever prefer. lambda, Proposition 3 and every sensitivity that compares
    # channels key on THIS count, so it is emitted under its own name instead
    # of being inferred from the admission column.
    C["char_nondegenerate_front_n"] = 1
    C["char_nondegenerate_front_channels"] = "FallChecker"
    C["char_nondegenerate_front_line"] = (
        "one channel has a front the allocation can move along; a second may "
        "be admitted with a coverage of zero at a cost of zero, which no "
        "budget can prefer at any price")
    C["char_allocation_tbd_n"] = sum(1 for r in rows if r[5] == "tbd")
    C["char_far_only_n"] = sum(1 for r in rows
                               if r[6] == "far_only_by_design")
    C["char_blocked_n"] = len(blocked)
    C["char_distinct_reasons_n"] = len({r[6] for r in blocked})
    C["char_blocked_reasons"] = "; ".join(sorted({REASONS[r[6]]
                                                  for r in blocked}))
    # The sentence, built from the counts rather than typed beside them. The
    # verb agrees with the count instead of being frozen at plural: "one ...
    # are" is how a generated sentence announces that nobody read it.
    _is = "is" if C["char_in_allocation_n"] == 1 else "are"
    C["char_headline"] = (
        "%s of %s detection channels %s characterised well enough to enter "
        "the allocation today; %s more %s blocked, for %s distinct reasons"
        % (word(C["char_in_allocation_n"]), word(C["char_channels_n"]), _is,
           word(C["char_blocked_n"]),
           "is" if C["char_blocked_n"] == 1 else "are",
           word(C["char_distinct_reasons_n"])))


def texname(k):
    """A LaTeX control sequence name for a count key.

    Digits are spelled out. A TeX control sequence may contain only letters, so
    `\CntTier0CorpusHours` parses as `\CntTier` followed by the text
    "0CorpusHours" -- which does not error where it is defined, only much later
    and unrecognisably, and which is why this file could be generated for two
    weeks without anyone noticing that no manuscript could input it.
    """
    parts = re.split(r"[_\W]+", k)
    # E4's separation flag is a FLAG, not a count, and reads as one at the point
    # of use: `\FlagSubstStratumSeparated` says what it is, `\CntFlagSubst...`
    # says it is a number of something, which it is not.
    if parts and parts[0] == "flag":
        name = "Flag" + "".join(x.capitalize() for x in parts[1:] if x)
    else:
        name = "Cnt" + "".join(x.capitalize() for x in parts if x)
    return "".join(_DIGIT_WORD.get(c, c) for c in name)


# Keys whose value is written AS LaTeX by count_prose(): they already carry
# `\emph{}`, `{\CntFoo}` references and escaped specials, so escaping them again
# would destroy them. Everything else is data, and data gets escaped.
TEX_LITERAL_PREFIXES = ("deviation_line_", "derived_line_", "harness_sentence_")


def texescape(s):
    """Escape a counted STRING so the macro file can be \\input.

    HARNESS-13, and the rule P9 now carries. On 2026-09-06 the E4 flag resolved
    and `far_flag_basis` began to read "... the substituted stratum's 95%
    interval ...". An unescaped `%` opens a TeX comment that swallows the rest
    of the line including the closing brace, so `\\input{generated_counts.tex}`
    died with "File ended while scanning use of \\@argdef" and every macro
    defined after it silently ceased to exist. `insitu_first_segment`
    (`HOM_20260827_0923.mp4`) was the same bug waiting one line further down.

    THE RULE, chosen once so nothing downstream has to remember it: the JSON
    keeps ordinary human prose, `%` and underscores and all, because
    generated_counts.json is read by people and by things that are not LaTeX.
    Escaping happens at the LaTeX boundary and nowhere else. The alternative --
    strip `%` from the source string and re-add it in a wrapper macro -- was
    rejected: it makes the JSON worse to serve a format the JSON does not
    serve, and it only ever fixes `%`, leaving `_`, `&` and `#` to be
    rediscovered one at a time.

    Not applied to TEX_LITERAL_PREFIXES, which are authored as LaTeX.
    """
    out = []
    for ch in s:
        if ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch == "\\":
            out.append(r"\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


# The canonical tree this script counts from. Not "some files it happens to
# read": these four are the signature that says the working directory is
# 01_Measurement of a submission tree and not a partial mirror of one.
TREE_MARKERS = ("PREREGISTERED_M3.md", "PREREGISTERED_M3.sha256",
                "GT_protocol", "ops")


def preflight(tex_out, make_tex_out):
    """Every input and every output location, checked BEFORE anything is written.

    WHY THIS FUNCTION EXISTS, precisely.
        On 2026-09-07 this script was run against the partial mirror on the
        Jetson. It counted the 17 quantities that mirror could support, wrote
        generated_counts.json over the previous one, and THEN died on
        FileNotFoundError for <device-home>/02_Manuscript/generated_counts.tex.
        The run failed and still left a degraded file behind with a fresh
        timestamp on it, which is the worst of the three possible outcomes:
        worse than succeeding, and worse than failing cleanly, because the
        file that remains looks current.

        Two rules follow, and both are enforced here rather than remembered:
        check every path first, and write nothing until every payload is
        built. `2>&1 | tail -5` in job D0's command discards this script's
        exit status, so a clean refusal is the only thing that protects the
        counts -- an exception will not.
    """
    problems = []
    for m in TREE_MARKERS:
        if not os.path.exists(os.path.join(MEAS, m)):
            problems.append("not the canonical measurement tree: %s is missing "
                            "from %s" % (m, MEAS))
    if not os.path.isdir(tex_out):
        if make_tex_out:
            try:
                os.makedirs(tex_out, exist_ok=True)
            except OSError as e:
                problems.append("cannot create --tex-out %s: %s" % (tex_out, e))
        else:
            problems.append(
                "the manuscript tree %s does not exist. It is where "
                "generated_counts.tex belongs. Pass --tex-out <dir> to write "
                "the macros somewhere else, deliberately." % tex_out)
    for d in (MEAS, tex_out):
        if os.path.isdir(d) and not os.access(d, os.W_OK):
            problems.append("not writable: %s" % d)
    if problems:
        sys.stderr.write(
            "REFUSING TO RUN -- nothing was written, nothing was overwritten.\n")
        for p in problems:
            sys.stderr.write("  * %s\n" % p)
        sys.stderr.write(
            "The counts of record are produced in the submission tree on the "
            "PC, where the files being counted live.\n")
        raise SystemExit(2)


def write_atomically(path, text):
    """Write via a sibling temp file and one rename. Never a partial file."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.replace(tmp, path)




# ------------------------------------------------- degradation band (rho)
def count_degradation_band():
    """The declared uncertainty band, counted from the source table.

    CLAIM_LEDGER C-b: "a declared uncertainty band joining them" is half of
    contribution (b), and until 2026-09-10 not one value of rho appeared on the
    rendered page. It was in theta_vs_lambda.py as a literal and in a markdown
    table, and a number that reaches the reader only through a literal in a
    script is a number the build cannot defend. Parsed from the Fall table of
    exsitu/OMNIFALL_TABLE2_DEGRADATION.md, which is the published source.
    """
    p = os.path.join(EXSITU, "OMNIFALL_TABLE2_DEGRADATION.md")
    if not os.path.exists(p):
        note("OmniFall degradation table not found at %s" % p)
        return
    text = open(p, encoding="utf-8").read()
    block = text.split("### Class `Fall`", 1)
    if len(block) < 2:
        note("no `Fall` class section in the OmniFall degradation table")
        return
    block = block[1].split("### Class", 1)[0]
    rows = []
    for line in block.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0].startswith("-") or "Train dataset" in cells[0]:
            continue
        m = re.match(r"^\*{0,2}([0-9.]+)\*{0,2}$", cells[3])
        if not m:
            continue
        rows.append((cells[0], float(m.group(1))))
    if not rows:
        note("no rho rows parsed from the OmniFall degradation table")
        return
    vals = sorted(v for _, v in rows)
    n = len(vals)
    median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2.0
    C["rho_sources_n"] = n
    C["rho_sources_n_word"] = word(n)
    C["rho_min"] = "%.3f" % vals[0]
    C["rho_max"] = "%.3f" % vals[-1]
    C["rho_median"] = "%.3f" % median
    C["rho_mean"] = "%.3f" % (sum(vals) / n)
    C["rho_source"] = "OmniFall Table 2, class Fall, %d staged source datasets" % n
    C["rho_min_dataset"] = min(rows, key=lambda r: r[1])[0]
    C["rho_max_dataset"] = max(rows, key=lambda r: r[1])[0]

    # The central value the propositions use is 0.494, and until 2026-09-10
    # every place that carried it -- the source document's summary line,
    # scripts/theta_vs_lambda.py's RHO constant, and the sensitivity tables --
    # called it the MEDIAN. It is not: over the seven rows above the median is
    # 0.164, and 0.494 is the GMDCSA24 row. GMDCSA24 is the corpus this paper
    # measures fall coverage on, so it is the right central value and the
    # wrong name for it, which is a better justification than the one it had.
    # min, max and mean in that summary line all check out; only the word
    # "median" does not. The build says so rather than silently preferring one.
    by_name = dict(rows)
    if "GMDCSA24" in by_name:
        C["rho_central"] = "%.3f" % by_name["GMDCSA24"]
        C["rho_central_dataset"] = "GMDCSA24"
        C["rho_central_why"] = (
            "the value for GMDCSA24, the corpus this paper replays to measure "
            "fall coverage, so the central point of the sweep is the source "
            "whose events are actually being scored rather than a summary "
            "statistic over datasets this paper never touches")
    stated = re.search(r"min\s+([0-9.]+),\s*median\s+([0-9.]+),\s*max\s+"
                       r"([0-9.]+),?\s*\n?\s*mean\s+([0-9.]+)", block)
    if stated:
        doc_median = float(stated.group(2))
        C["rho_doc_summary_median"] = "%.3f" % doc_median
        if abs(doc_median - median) > 5e-4:
            C["rho_doc_summary_disagrees"] = (
                "the source document's summary line calls %.3f the median of "
                "the %d rows above it; the median of those rows is %.3f. "
                "%.3f is the GMDCSA24 row. min, max and mean in that line are "
                "correct." % (doc_median, n, median, doc_median))
            note("OMNIFALL_TABLE2_DEGRADATION.md summary line says median "
                 "%.3f; the table's median is %.3f (%.3f is the GMDCSA24 "
                 "row). Reported as rho_central, not as a median."
                 % (doc_median, median, doc_median))
    # The line deliberately does NOT quote a median. The one that would be
    # quoted here is the source document's, and it is wrong -- see the block
    # below. The band is what carries the argument; the central point is named
    # by the dataset it comes from, not by a statistic it is not.
    C["rho_band_line"] = (
        "the ratio of in-the-wild to in-domain sensitivity over the %s staged "
        "source datasets of the published benchmark, from %s (%s) to %s (%s)"
        % (word(n), C["rho_min"], C["rho_min_dataset"],
           C["rho_max"], C["rho_max_dataset"]))
    C["rho_swept_not_applied"] = (
        "swept over its full published range rather than applied as a point "
        "correction: the paper reports the allocation at every value in the "
        "band, and claims no transfer of rho from a learned end-to-end "
        "classifier to these checkers")


# ------------------------------------------------- repeatability floor
def count_noise_floor():
    """The repeatability floor, counted instead of asserted.

    CLAIM_LEDGER A5: "a measured repeatability floor of zero" was stated three
    times -- abstract, introduction, III-D -- and counted zero times. The word
    "zero" is not a digit, so P9-c never saw it and P9-d's counted-noun rule did
    not either. Counting it is what lets the sentence be checked, and it is
    also what forces the sentence to say what was actually compared: an ex-situ
    replay of 160 clips, three checkers that fired, and no in-situ segment run
    twice.
    """
    p = os.path.join(EXSITU, "NOISE_FLOOR_cell0.json")
    if not os.path.exists(p):
        note("noise floor artefact not found at %s" % p)
        return
    d = json.load(open(p, encoding="utf-8"))
    per = d.get("per_checker") or {}
    fired = sorted(k for k, v in per.items()
                   if (v.get("shared", 0) + v.get("only_a", 0) + v.get("only_b", 0)) > 0)
    C["noise_floor"] = "%.3f" % float(d.get("noise_floor", 0.0))
    C["noise_floor_clips_compared"] = d.get("clips_compared")
    C["noise_floor_clips_divergent"] = d.get("clips_divergent")
    C["noise_floor_alerts_both_runs"] = d.get("total_alerts_both_runs")
    C["noise_floor_alerts_per_run"] = d.get("alerts_a")
    C["noise_floor_divergent_alerts"] = d.get("divergent_alerts")
    C["noise_floor_conf_max_abs_diff"] = "%.3f" % float(
        d.get("confidence_max_abs_diff", 0.0))
    C["noise_floor_checkers_that_fired"] = ", ".join(fired) or "none"
    C["noise_floor_checkers_that_fired_n"] = len(fired)
    C["noise_floor_checkers_that_fired_n_word"] = word(len(fired))
    C["noise_floor_predicate"] = ", ".join(d.get("predicate") or [])
    C["noise_floor_scope"] = "ex situ (%s vs %s)" % (
        os.path.basename(str(d.get("dir_a", "?"))),
        os.path.basename(str(d.get("dir_b", "?"))))
    C["noise_floor_line"] = (
        "the whole ex-situ corpus replayed twice through the identical "
        "container and compared under a predicate fixed in writing beforehand "
        "(%s): %d clips, %d alerts in each run, %d divergences" % (
            C["noise_floor_predicate"], d.get("clips_compared", 0),
            d.get("alerts_a", 0), d.get("divergent_alerts", 0)))
    C["noise_floor_limit"] = (
        "measured on the ex-situ replay path only; no in-situ segment was run "
        "twice, and the %s channels that raised no alert in either run "
        "contribute no evidence to it" % word(
            max(0, len(C.get("far_checkers_measured", "").split(", ")) - len(fired))))


# ------------------------------------------------- C2 reproduction gate
def count_reproduction_gate():
    """The reproduction gate, per checker, from the gate's own CSV.

    CLAIM_LEDGER P7 and item 1 of the wasted-evidence list. Two things depended
    on this and neither had a macro:

      * III-E claimed "on one segment the two streams matched exactly in count
        and differed on a fifth of the timestamps by one to five seconds". The
        largest displacement anywhere in this file is 0.010 s. The sentence was
        hand-typed prose in III, which P9-c does not guard, and it stood for
        seven days contradicting the artefact it cites.
      * "the reproduction error is measured at every reported point and
        published beside the curve rather than summarised" -- IV-C's promise --
        had no number behind it anywhere on the page.

    Counted here so that both are answerable by the build rather than by
    memory. Source: out/c2_rescore/reproduction_gate.csv on the device, copied
    to analysis/ with its SHA recorded in LINKS.md.
    """
    p = os.path.join(ANALYSIS, "reproduction_gate.csv")
    if not os.path.exists(p):
        note("C2 reproduction gate not found at %s" % p)
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    if not rows:
        note("C2 reproduction gate is empty")
        return
    segs = {r["segment"] for r in rows}
    per = {}
    max_dt = 0.0
    for r in rows:
        ck = r.get("checker") or "-"
        d = per.setdefault(ck, dict(segments=0, real=0, replay=0, exact=0,
                                    extra=0, missing=0, max_dt=0.0, ok=0))
        d["segments"] += 1
        for k in ("real", "replay", "exact", "extra", "missing"):
            d[k] += int(r.get(k) or 0)
        dt = float(r.get("max_dt") or 0)
        d["max_dt"] = max(d["max_dt"], dt)
        max_dt = max(max_dt, dt)
        if (r.get("status") or "").upper() == "OK":
            d["ok"] += 1

    C["repro_gate_segments"] = len(segs)
    C["repro_gate_rows"] = len(rows)
    C["repro_gate_max_dt_s"] = "%.3f" % max_dt
    C["repro_gate_tolerance_s"] = "%.4f" % max(
        float(r.get("tol_s") or 0) for r in rows)
    silent = per.pop("-", None)
    if silent:
        C["repro_gate_segments_with_no_alert"] = silent["segments"]
    C["repro_gate_checkers_n"] = len(per)
    C["repro_gate_checkers_n_word"] = word(len(per))
    tot_real = tot_replay = tot_exact = tot_extra = tot_missing = 0
    for ck, d in sorted(per.items()):
        stem = "repro_gate_%s" % ck.lower()
        C[stem + "_segments"] = d["segments"]
        C[stem + "_real"] = d["real"]
        C[stem + "_replay"] = d["replay"]
        C[stem + "_exact"] = d["exact"]
        C[stem + "_extra"] = d["extra"]
        C[stem + "_missing"] = d["missing"]
        C[stem + "_max_dt_s"] = "%.3f" % d["max_dt"]
        C[stem + "_verdict"] = ("reproduces" if d["real"] == d["exact"]
                                else "stateful divergence")
        tot_real += d["real"]
        tot_replay += d["replay"]
        tot_exact += d["exact"]
        tot_extra += d["extra"]
        tot_missing += d["missing"]
    C["repro_gate_real_total"] = tot_real
    C["repro_gate_replay_total"] = tot_replay
    C["repro_gate_exact_total"] = tot_exact
    C["repro_gate_extra_total"] = tot_extra
    C["repro_gate_missing_total"] = tot_missing

    fall = per.get("FallChecker")
    if fall:
        C["repro_gate_fall_recovered_line"] = (
            "the replay recovered %d of the %d fall alerts the engine raised "
            "over %d segments" % (fall["replay"], fall["real"], fall["segments"]))
    C["repro_gate_line"] = (
        "over %d segments the replay disagrees with the engine about WHICH "
        "alerts exist, not about when: it invented %d and lost %d, while every "
        "alert it did match fell within %s s of the engine's -- under one frame "
        "at every segment's own frame rate" % (
            len(segs), tot_extra, tot_missing, C["repro_gate_max_dt_s"]))
    C["theta_transport_line"] = (
        "where a threshold feeds the confirmation counter or the per-track "
        "cooldown, replaying recorded candidates at a different threshold does "
        "not reconstruct the engine's alert stream: those channels get no "
        "swept curve, and every operating point reported for them is a real run")


# ------------------------------------------------- Layer-1 detector metrics
def count_layer1():
    """Detector-level metrics on the public split, per checker.

    Item 3 of the wasted-evidence list. This is the only evidence that
    separates "the detector found nothing" from "the checker decided nothing",
    which is the first question a reader asks about a coverage of zero. Eight
    artefacts existed and none had a macro.
    """
    found = {}
    for p in sorted(glob.glob(os.path.join(ANALYSIS, "*_layer1.json"))):
        base = os.path.basename(p)
        checker = base.split("_")[0]
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            note("could not read Layer-1 artefact %s" % base)
            continue
        split = d.get("split")
        if split != "full":
            continue
        person = (d.get("per_class") or {}).get("person") or {}
        found[checker] = d
        stem = "layer1_%s" % checker.lower()
        C[stem + "_split"] = split
        C[stem + "_images"] = d.get("n_images")
        C[stem + "_conf"] = d.get("conf")
        C[stem + "_map50"] = ("%.4f" % d["mAP_50_all_classes"]) if d.get(
            "mAP_50_all_classes") is not None else None
        C[stem + "_map50_95"] = ("%.4f" % d["mAP_50_95_all_classes"]) if d.get(
            "mAP_50_95_all_classes") is not None else None
        if person.get("ap50") is not None:
            C[stem + "_person_ap50"] = "%.4f" % person["ap50"]
        if person.get("recall_at_maxF1") is not None:
            C[stem + "_person_recall"] = "%.4f" % person["recall_at_maxF1"]
        if person.get("precision_at_maxF1") is not None:
            C[stem + "_person_precision"] = "%.4f" % person["precision_at_maxF1"]
        if person.get("instances_evaluated") is not None:
            C[stem + "_person_instances"] = person["instances_evaluated"]
    if not found:
        note("no Layer-1 artefacts found under %s" % ANALYSIS)
        return
    C["layer1_checkers"] = ", ".join(sorted(found))
    C["layer1_checkers_n"] = len(found)
    C["layer1_checkers_n_word"] = word(len(found))
    any_d = found[sorted(found)[0]]
    C["layer1_annotation"] = any_d.get("annotation_file", "")
    C["layer1_method"] = any_d.get("method", "")
    C["layer1_model"] = os.path.basename(str(any_d.get("model", "")))
    C["layer1_line"] = (
        "the shared detector's own accuracy on the public split, measured "
        "separately from any channel decision, so that a coverage of zero can "
        "be attributed to the detector or to the checker rather than to the "
        "pair of them")




# ------------------------------------------------- the Fall front (Figure 1)
# The five theta points of the fall channel, on both axes, from the artefacts
# that produced each axis. Until 2026-09-10 these numbers existed only as a
# LITERAL TABLE inside scripts/theta_vs_lambda.py:
#
#     FALL = [(0.30, 51, 3.9914, 0.6282, 0.5173, 0.7271), ...]
#
# and nothing checked them against the files. They were right -- verified today
# against runs/verification/ and exsitu/SCORE_X4_t*.json, alert for alert --
# but "right" and "checked" are different states, and a figure drawn from a
# literal is a figure that cannot go stale visibly. Figure 1 is generated from
# these keys, so it moves when the measurement moves.
#
# THE FRONT IS NOT FIVE POINTS WIDE, AND THE FIGURE MUST NOT PRETEND IT IS.
# Coverage exists at all five registered theta. The in-situ PRICE exists at
# three: V1, V2 and V3 ran native passes at 0.30, 0.45 and 0.60. E7-d gives no
# native pass at 0.375 or 0.525, so those two points have a y and no x. They
# are counted here with far_per_h = None and drawn on their own coverage axis
# rather than placed at a guessed cost -- placing them would invent the one
# number the whole paper is about.
_FALL_THETA_TAGS = (("0.30", "030", "v1_loose"), ("0.375", "0375", None),
                    ("0.45", "045", "v2_frozen"), ("0.525", "0525", None),
                    ("0.60", "060", "v3_tight"))


def _wilson_key(tag):
    return {"0.30": "ZeroThreeZero", "0.375": "ZeroThreeSevenFive",
            "0.45": "ZeroFourFive", "0.525": "ZeroFiveTwoFive",
            "0.60": "ZeroSixZero"}[tag]


def count_fall_front():
    import glob as _glob
    pts = []
    for theta, tag, vdir in _FALL_THETA_TAGS:
        rec = {"theta": theta}
        sp = os.path.join(EXSITU, "SCORE_X4_t%s.json" % tag)
        if not os.path.exists(sp):
            note("fall front: no score file for theta %s (%s)" % (theta, sp))
            continue
        sc = json.load(open(sp, encoding="utf-8"))["results"]["extended"]
        rec["coverage"] = round(sc["recall"], 4)
        lo, hi = sc["recall_wilson95"]
        rec["coverage_lo"] = round(lo, 4)
        rec["coverage_hi"] = round(hi, 4)
        rec["gt_events"] = sc["gt_events"]
        rec["tp"] = sc["tp"]

        if vdir:
            metas = [f for f in sorted(_glob.glob(
                os.path.join(RUNS, "verification", vdir, "*.json")))
                if os.path.basename(f) != "pass_params.json"]
            if not metas:
                note("fall front: no verification metadata under %s" % vdir)
            else:
                obs = 0.0
                for m in metas:
                    j = json.load(open(m, encoding="utf-8"))
                    fps = float(j.get("fps_effective") or j.get("fps") or 0)
                    if fps:
                        obs += float(j["frames_read"]) / fps / 3600.0
                alerts = 0
                for cp in sorted(_glob.glob(
                        os.path.join(RUNS, "verification", vdir, "*.csv"))):
                    with open(cp, newline="", encoding="utf-8") as fh:
                        alerts += sum(1 for r in csv.DictReader(fh)
                                      if r.get("checker") == "FallChecker")
                rec["far_source"] = vdir
                rec["far_segments"] = len(metas)
                rec["far_alerts"] = alerts
                rec["far_hours"] = round(obs, 4)
                rec["far_per_h"] = round(alerts / obs, 4) if obs else None
                if alerts == 0 and obs:
                    # Zero counts bound a rate from above and do not establish
                    # it; the same rule the in-situ table already applies.
                    rec["far_upper_limit"] = round(3.689 / obs, 4)
        pts.append(rec)

    if not pts:
        note("fall front: no points counted")
        return

    C["fall_front"] = pts                      # the figure reads this
    C["fall_front_points_n"] = len(pts)
    priced = [p for p in pts if p.get("far_per_h") is not None]
    C["fall_front_priced_n"] = len(priced)
    C["fall_front_priced_n_word"] = word(len(priced))
    C["fall_front_unpriced_n"] = len(pts) - len(priced)
    C["fall_front_unpriced_n_word"] = word(len(pts) - len(priced))
    C["fall_front_unpriced_theta"] = ", ".join(
        p["theta"] for p in pts if p.get("far_per_h") is None)
    for p in pts:
        k = _wilson_key(p["theta"])
        C["fall_front_%s_coverage" % k.lower()] = "%.4f" % p["coverage"]
        C["fall_front_%s_coverage_lo" % k.lower()] = "%.4f" % p["coverage_lo"]
        C["fall_front_%s_coverage_hi" % k.lower()] = "%.4f" % p["coverage_hi"]
        if p.get("far_per_h") is not None:
            C["fall_front_%s_far" % k.lower()] = "%.4f" % p["far_per_h"]
            C["fall_front_%s_alerts" % k.lower()] = p["far_alerts"]
    if priced:
        C["fall_front_hours"] = "%.4f" % priced[0]["far_hours"]
        C["fall_front_segments"] = priced[0]["far_segments"]
    C["fall_front_line"] = (
        "%s of the %s registered operating points carry both axes; the "
        "remaining %s (theta %s) have a measured coverage and no native "
        "in-situ pass to price them, and are drawn on the coverage axis alone "
        "rather than placed at a cost that was never measured"
        % (word(len(priced)), word(len(pts)), word(len(pts) - len(priced)),
           C["fall_front_unpriced_theta"]))

    # The budget thresholds of the allocation, from the priced points only.
    # Cheapest first; a point is bought when the budget reaches its cost.
    order = sorted(priced, key=lambda p: p["far_per_h"])
    steps = []
    for i, p in enumerate(order):
        nxt = order[i + 1]["far_per_h"] if i + 1 < len(order) else None
        steps.append({"from": p["far_per_h"], "to": nxt, "theta": p["theta"],
                      "coverage": p["coverage"]})
    C["budget_steps"] = steps                  # panel (b) reads this
    C["budget_thresholds"] = ", ".join(
        "%.3f" % s["from"] for s in steps if s["from"] > 0)
    C["budget_steps_n"] = len(steps)
    if steps:
        free = [s for s in steps if s["from"] == 0]
        if free:
            C["budget_free_theta"] = free[0]["theta"]
            C["budget_free_coverage"] = "%.4f" % free[0]["coverage"]


# ------------------------------------------------- returned label packs (5.9)
def count_label_packs():
    """The 132 label cells, and what they license.

    Sealed before reading (`GT_protocol/LABEL_PACK_SEAL_20260910.md`) and
    labelled directly by the author in one pass, so there is no override rate
    to report and none is being withheld -- GT_PROTOCOL 5.9.

    The Fall and Helmet packs are not sample statistics; they are the
    falsification test for the blanket negative declaration. Errata E6: a single
    REAL_EVENT in either voids that class as a false-alarm denominator. The
    counts are emitted whichever way they fall, and the flag is emitted too, so
    the branch the evidence took is on the page rather than in a memory.
    """
    import glob as _glob
    packs = {
        "fall": os.path.join(MEAS, "spotcheck", "spotcheck_FallChecker.csv"),
        "helmet": os.path.join(MEAS, "spotcheck", "spotcheck_HelmetChecker.csv"),
    }
    voided = []
    for name, p in packs.items():
        if not os.path.exists(p):
            note("spot-check pack missing: %s" % p)
            continue
        rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
        if not rows:
            note("spot-check pack empty: %s" % p)
            continue
        col = next((c for c in rows[0] if c.upper().startswith("VERDICT")), None)
        if col is None:
            note("no VERDICT column in %s" % p)
            continue
        v = [(r[col] or "").strip().lower() for r in rows]
        fa = sum(1 for x in v if x == "false_alarm")
        real = sum(1 for x in v if x == "real_event")
        uns = sum(1 for x in v if x == "unsure")
        blank = sum(1 for x in v if not x)
        C["spotcheck_%s_n" % name] = len(rows)
        C["spotcheck_%s_false_alarm" % name] = fa
        C["spotcheck_%s_real_event" % name] = real
        C["spotcheck_%s_unsure" % name] = uns
        C["spotcheck_%s_blank" % name] = blank
        C["spotcheck_%s_line" % name] = (
            "%d alerts checked, %d judged false alarms, %d real events, "
            "%d unsure" % (len(rows), fa, real, uns))
        if blank:
            note("%s spot-check has %d unfilled cell(s)" % (name, blank))
        if real:
            voided.append(name)

    C["spotcheck_classes_voided"] = ", ".join(voided) or "none"
    C["spotcheck_classes_voided_n"] = len(voided)
    C["spotcheck_e6_triggered"] = "yes" if voided else "no"
    C["spotcheck_e6_line"] = (
        ("the spot-check found %s real event(s), so errata E6 applies and the "
         "blanket negative declaration is void for: %s"
         % (sum(C.get("spotcheck_%s_real_event" % n, 0) for n in voided),
            ", ".join(voided)))
        if voided else
        ("the spot-check found no real event in either class, so the blanket "
         "negative declaration stands and the rates built on it remain "
         "false-alarm rates rather than alert rates"))

    # ---- the intrusion FP-fraction and the FAR it licenses ----------------
    p = os.path.join(ANALYSIS, "INTRUSION_FAR.json")
    if not os.path.exists(p):
        note("intrusion FAR artefact not found at %s; run scripts/intrusion_far.py" % p)
        return
    d = json.load(open(p, encoding="utf-8"))
    C["intrusion_pack_n"] = d["n"]
    C["intrusion_pack_yes"] = d["yes"]
    C["intrusion_pack_no"] = d["no"]
    C["intrusion_pack_unsure"] = d["unsure"]
    C["intrusion_pack_denominator"] = d["denominator"]
    C["intrusion_fp_fraction"] = "%.4f" % d["fp_fraction"]
    C["intrusion_fp_fraction_ci_lo"] = "%.4f" % d["fp_fraction_wilson95"][0]
    C["intrusion_fp_fraction_ci_hi"] = "%.4f" % d["fp_fraction_wilson95"][1]
    C["intrusion_deployed_rate"] = "%.4f" % d["deployed_rate_per_h"]
    C["intrusion_deployed_rate_ci_lo"] = "%.4f" % d["deployed_rate_ci95_block_bootstrap"][0]
    C["intrusion_deployed_rate_ci_hi"] = "%.4f" % d["deployed_rate_ci95_block_bootstrap"][1]
    C["intrusion_far"] = "%.4f" % d["far_point_per_h"]
    C["intrusion_far_upper"] = "%.4f" % d["far_upper_per_h"]
    if d.get("fp_fraction_rule_of_three_upper"):
        C["intrusion_fp_rule_of_three"] = "%.4f" % d["fp_fraction_rule_of_three_upper"]
    C["intrusion_far_line"] = (
        "of %d production alerts sampled blind and labelled by hand, %d showed a "
        "person and %d did not, so the false-alarm fraction is %s "
        "[%s, %s] and the false-alarm rate is %s per hour against an alert rate "
        "of %s per hour"
        % (d["n"], d["yes"], d["no"], C["intrusion_fp_fraction"],
           C["intrusion_fp_fraction_ci_lo"], C["intrusion_fp_fraction_ci_hi"],
           C["intrusion_far"], C["intrusion_deployed_rate"]))
    C["intrusion_nuisance_line"] = (
        "the deployed intrusion zone is the whole frame, so an alert on a member "
        "of the household is a technical true positive and an operational "
        "nuisance at the same time; this channel's cost to the operator is "
        "therefore its ALERT rate and not its false-alarm rate, and the two "
        "differ here by the whole of it")
    C["label_override_rate"] = "not applicable: labelling was direct and single-pass (GT_PROTOCOL 5.9)"



# ------------------------------------------------- E9 outcomes (X3b, SFCTL)
def count_e9_outcomes():
    """What the two recovery jobs returned, and which registered branch fired.

    Both branches of both rules were written down before either job ran (E9
    1.4 and 2.4). The counts are emitted whichever way they fell, and the
    branch is emitted as a value rather than described in prose, so that the
    page cannot drift from the rule.
    """
    p = os.path.join(ANALYSIS, "e9", "E9_OUTCOMES.json")
    if not os.path.exists(p):
        note("E9 outcome summary not found at %s" % p)
        return
    d = json.load(open(p, encoding="utf-8"))

    x = d.get("x3b") or {}
    if x:
        thetas = sorted(x)
        wb = sum(v["with_boxes"] for v in x.values())
        nb = sum(v["no_boxes"] for v in x.values())
        ca = sum(v["checker_alerts"] for v in x.values())
        C["x3b_thetas_n"] = len(thetas)
        C["x3b_clips"] = x[thetas[0]]["clips"]
        C["x3b_side_calls_with_boxes"] = wb
        C["x3b_side_calls_no_boxes"] = nb
        C["x3b_checker_alerts"] = ca
        C["x3b_branch"] = "1" if wb >= 1 else "2"
        C["x3b_branch_line"] = (
            ("the checker executed %d times against the %d of the run it "
             "replaces, so its coverage is a measurement and enters the "
             "allocation even at zero" % (wb, 0)) if wb >= 1 else
            "the checker still did not execute; this is not a result")
    sf = (d.get("sfctl") or {}).get("sfctl_furg_t001")
    if sf:
        C["sfctl_clips"] = sf["clips"]
        C["sfctl_alerts"] = sf["alerts"]
        C["sfctl_frames"] = sf["frames"]
        C["sfctl_branch"] = "1" if sf["alerts"] > 0 else "2"
        C["sfctl_branch_line"] = (
            ("the alert path fired at the control point, so the "
             "registered-grid zeros stand as a measurement")
            if sf["alerts"] > 0 else
            ("the alert path raised nothing even at the control point, so no "
             "conclusion about coverage may be drawn and the channel's zeros "
             "are reported as uncharacterised rather than as measured"))
    if "x3b_branch" in C and "sfctl_branch" in C:
        # SUPERSEDED BY count_e10_outcomes AS THE PAGE SENTENCE, and kept
        # because it is the E9-only statement and E9 is registered separately.
        # Its closing clause used to read "Neither has been given the other's
        # test", which was true on 2026-09-10 and stopped being true at
        # 22:06:55 the same day, when E10 gave the running channel a positive
        # control of its own. A line that goes quietly false as the campaign
        # advances is the defect this paper is about, so the clause is gone and
        # what replaced it is scoped to E9 in its own words.
        C["e9_asymmetry_line"] = (
            "at the close of E9 the two zeros were not the same grade of "
            "evidence: one channel had been given a positive control and had "
            "failed it, so its zero was uncharacterised; the other had been "
            "given a configuration in which its checker could execute, "
            "executed %s times, and returned nothing, so its zero was "
            "measured. What E9 alone could not settle was whether the alert "
            "path was open in either control pass"
            % "{:,}".format(C["x3b_side_calls_with_boxes"]))


# ------------------------------------------------- E10 outcome (RUNCTL)
def count_e10_outcomes():
    """The registered control for the running channel, and what it settles.

    E10 asked one question -- does RunningChecker fire when its threshold is
    dropped below every value the campaign has used? -- and E10-b, locked
    eleven seconds before the job started, added the obligation to report the
    answer whichever way it fell. It fell the way that does NOT help: at
    run_vel_threshold 0.01 the checker was reached and returned nothing, as it
    had at all five looser values. Branch 2.

    What the run does settle is a different and narrower thing, and the
    distinction is the whole content of the Section V sentence. In the SAME
    pass, on the SAME clips, in the SAME container, another checker's
    violations went the whole length of the alert path and reached the CSV. So
    for this channel the pass is a demonstration that the path was alive while
    the checker said no, and the zero is a measurement of the clips. The smoke
    channel's control has no such witness: nothing at all was dispatched in it,
    so its zero cannot be separated from a path that was never exercised.

    That asymmetry is a property of the two passes, not a judgement about the
    two channels, so every number in it is read from E10_OUTCOMES.json and
    E9_OUTCOMES.json, both of which summarise_controls.py derives from the job
    logs.
    """
    p = os.path.join(ANALYSIS, "e10", "E10_OUTCOMES.json")
    if not os.path.exists(p):
        note("E10 outcome summary not found at %s" % p)
        return
    d = json.load(open(p, encoding="utf-8"))
    r = d.get("runctl_virat_t001")
    if not r:
        note("E10 outcome summary carries no runctl cell")
        return

    C["runctl_clips"] = r["clips"]
    C["runctl_frames"] = r["frames"]
    C["runctl_theta"] = ("%g" % r["param"]["RunningChecker"])
    C["runctl_side_calls_with_boxes"] = r["with_boxes"]
    C["runctl_checker_raw"] = r["checker_raw"]
    C["runctl_other_dispatched"] = r["other_checker_dispatched"]
    C["runctl_branch"] = r["branch"]
    C["runctl_alert_path_alive"] = "yes" if r["alert_path_alive"] else "no"

    # The span the running channel now has evidence over: the five X3b values
    # plus this one. Summed here rather than in prose so that a sixth job
    # changes the sentence by changing the file.
    if "x3b_side_calls_with_boxes" in C:
        C["running_executions_total"] = (C["x3b_side_calls_with_boxes"]
                                         + r["with_boxes"])
        C["running_thetas_n"] = C.get("x3b_thetas_n", 0) + 1
        C["running_thetas_n_word"] = word(C["running_thetas_n"])

    # The Section V sentence. It is a single sentence rather than a paragraph
    # because it makes a single claim: which zero carries which grade, and on
    # what evidence. The clause that does the work is the middle one -- the
    # alerts that came out of the same pass -- because that is the only thing
    # in the campaign that separates "the scene was empty" from "the wire was
    # cut", and only one of the two controls has it.
    if ("running_executions_total" in C and "sfctl_alerts" in C
            and "sfctl_frames" in C):
        C["v_asymmetry_line"] = (
            "the running channel's zero is the stronger of the two: its "
            "checker was reached %s times across %s threshold values spanning "
            "an order of magnitude, and in the control pass %s alerts from "
            "another checker traversed the whole alert path on the same clips "
            "in the same container, so the path is observed to have been open "
            "while the checker returned nothing; the smoke channel's control "
            "pass dispatched nothing whatever over %s frames, so its zero "
            "cannot be separated from a path that was never exercised, and it "
            "is reported as uncharacterised rather than as measured"
            % ("{:,}".format(C["running_executions_total"]),
               C["running_thetas_n_word"],
               "{:,}".format(C["runctl_other_dispatched"]),
               "{:,}".format(C["sfctl_frames"])))


# ------------------------------------------------- the locked registrations
def count_preregistrations():
    """Every locked pre-registration, with its hash RE-VERIFIED against the file.

    A registry that prints stored hashes proves nothing -- the stored value and
    the file can disagree and the table would look identical. This recomputes
    each one, and emits a count of mismatches so the supplement can state the
    verification rather than assert it. `prereg_mismatches` is the number the
    claim rests on; if it is ever non-zero the sentence in S2 changes by itself.
    """
    import glob as _glob
    rows = []
    for shp in sorted(_glob.glob(os.path.join(MEAS, "PREREGISTERED_*.sha256"))):
        base = os.path.basename(shp)[: -len(".sha256")]
        if not base.endswith(".md"):
            base += ".md"
        target = os.path.join(MEAS, base)
        if not os.path.exists(target):
            note("registration file missing for %s" % os.path.basename(shp))
            continue
        try:
            stored = open(shp, encoding="utf-8").read().split()[0].strip()
        except Exception:                                       # noqa: BLE001
            note("unreadable hash file: %s" % shp)
            continue
        h = hashlib.sha256(open(target, "rb").read()).hexdigest()
        rows.append({"file": base, "stored": stored, "actual": h,
                     "ok": stored == h,
                     "locked": _locked_stamp(shp)})
    if not rows:
        note("no locked pre-registrations found")
        return
    bad = [r for r in rows if not r["ok"]]
    C["prereg_n"] = len(rows)
    C["prereg_n_word"] = word(len(rows))
    C["prereg_mismatches"] = len(bad)
    C["prereg_mismatch_files"] = ", ".join(r["file"] for r in bad) or "none"
    C["flag_prereg_all_verified"] = "yes" if not bad else "no"
    C["prereg_files"] = ", ".join(r["file"] for r in rows)
    C["prereg_line"] = (
        ("%s pre-registrations are locked, and every one of their stored "
         "SHA256 values was recomputed from the file it names at build time "
         "and matched: the ordering claim is checkable rather than asserted"
         % word(len(rows))) if not bad else
        ("%s pre-registrations are locked and %s of them no longer %s the "
         "file %s names (%s); the ordering claim is suspended for %s until the "
         "change is identified and a new row recorded, and it is printed here "
         "rather than corrected"
         % (word(len(rows)), word(len(bad)),
            "matches" if len(bad) == 1 else "match",
            "it" if len(bad) == 1 else "they",
            ", ".join(r["file"] for r in bad),
            "it" if len(bad) == 1 else "them")))
    for i, r in enumerate(rows, 1):
        k = "prereg_%s" % _ORD.get(i, str(i))
        C[k + "_file"] = r["file"].replace("PREREGISTERED_", "").replace(".md", "")
        C[k + "_sha"] = r["actual"][:16]
        C[k + "_locked"] = r["locked"]
        C[k + "_ok"] = "yes" if r["ok"] else "NO"


_ORD = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
        7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
        12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
        16: "sixteen", 17: "seventeen", 18: "eighteen"}


def _locked_stamp(shp):
    """The lock timestamp if the .sha256 carries one, else the file mtime.

    Some hash files were written with `locked <iso>` appended and some were
    not. Falling back to mtime is honest about which is which because the
    fallback is labelled.
    """
    try:
        txt = open(shp, encoding="utf-8").read()
    except Exception:                                           # noqa: BLE001
        txt = ""
    m = re.search(r"locked\s+(\S+)", txt)
    if m:
        return m.group(1)[:19]
    return datetime.datetime.fromtimestamp(
        os.path.getmtime(shp)).isoformat(timespec="seconds") + " (mtime)"


# ------------------------------------------------- M4e: the ablation cells
def count_ablation():
    """The seven M4e cells, from the cell files the run wrote.

    WHAT THE CELLS ARE FOR
        The front says what an operating point costs. It cannot say which
        channel the cost belongs to, because every channel shares one detector
        and a reader is entitled to suspect that switching one off simply moves
        its alerts into another. The single-channel cells answer that directly:
        run the deployment with exactly one checker enabled and count what comes
        out.

    ADDITIVITY IS CHECKED, NOT ASSERTED
        If the single-channel counts sum to the baseline, the channels do not
        interact at the alert level on this sample, and that is a result. The
        residual is emitted beside the claim so that a future run which breaks
        additivity changes the sentence instead of falsifying it.

    THE GATE CELL IS THE LARGEST EFFECT IN THE CAMPAIGN AND IT IS NOT A THETA
        `gate_on` differs from baseline by one configuration flag, not by a
        threshold, and it multiplies the alert count. A paper about spending an
        alert budget on thresholds has to report that the biggest lever measured
        was not a threshold.
    """
    import glob as _glob
    d = os.path.join(ANALYSIS, "ablation")
    cells = {}
    for p in sorted(_glob.glob(os.path.join(d, "*.cell.json"))):
        try:
            j = json.load(open(p, encoding="utf-8"))
        except Exception:                                       # noqa: BLE001
            note("ablation cell unreadable: %s" % p)
            continue
        cells[j["label"]] = j
    if not cells:
        note("no ablation cell files under %s" % d)
        return

    C["ablation_cells_n"] = len(cells)
    C["ablation_cells_n_word"] = word(len(cells))
    C["ablation_cells"] = ", ".join(sorted(cells))

    base = cells.get("baseline")
    if base is None:
        note("ablation: no baseline cell, so no cell can be compared")
        return
    hours = float(base["observation_hours"])
    C["ablation_hours"] = "%.4f" % hours
    C["ablation_segments"] = base["segments_measured"]
    C["ablation_image_digest"] = base.get("image_digest", "")[:19]

    def _emit(key, cell):
        n = int(cell["alerts_total"])
        h = float(cell["observation_hours"])
        C["ablation_%s_alerts" % key] = n
        C["ablation_%s_rate" % key] = "%.4f" % (n / h) if h else "0"
        C["ablation_%s_wall_h" % key] = "%.2f" % (
            float(cell.get("wall_seconds", 0)) / 3600.0)
        by = cell.get("alerts_by_checker") or {}
        C["ablation_%s_by_checker" % key] = (
            ", ".join("%s %d" % (k, v) for k, v in sorted(by.items()))
            or "none")
        return n

    _KEY = {"baseline": "baseline", "gate_on": "gateon",
            "only_FallChecker": "onlyfall",
            "only_IntrusionChecker": "onlyintrusion",
            "only_HelmetChecker": "onlyhelmet",
            "only_SmokeFireChecker": "onlysmokefire",
            "only_RunningChecker_with_std": "onlyrunning"}
    for label, key in _KEY.items():
        if label in cells:
            _emit(key, cells[label])
        else:
            note("ablation: cell %s absent" % label)

    # -- additivity, measured ------------------------------------------------
    singles = [l for l in cells if l.startswith("only_")]
    # only_RunningChecker_with_std carries IntrusionChecker deliberately (E9:
    # Running is a side checker and needs a detection pass to consume), so its
    # total would double-count Intrusion. Its OWN contribution is the alerts
    # attributable to RunningChecker, which is what the sum needs.
    total = 0
    parts = []
    for l in sorted(singles):
        by = cells[l].get("alerts_by_checker") or {}
        if l == "only_RunningChecker_with_std":
            own = int(by.get("RunningChecker", 0))
        else:
            own = int(cells[l]["alerts_total"])
        total += own
        parts.append("%s %d" % (l.replace("only_", "").replace("Checker", ""), own))
    base_n = int(base["alerts_total"])
    C["ablation_singles_sum"] = total
    C["ablation_singles_parts"] = ", ".join(parts)
    C["ablation_baseline_alerts"] = base_n
    C["ablation_additivity_residual"] = base_n - total
    C["flag_ablation_additive"] = "yes" if base_n == total else "no"
    C["ablation_additivity_line"] = (
        ("the single-channel cells sum to %d alerts and the all-channel cell "
         "raised %d: the residual is %s, so on this sample switching a channel "
         "off removes its own alerts and moves none of them into another "
         "channel (%s)"
         % (total, base_n, "exactly zero" if base_n == total
            else "%+d" % (base_n - total), ", ".join(parts)))
        if base_n == total else
        ("the single-channel cells sum to %d alerts against %d for the "
         "all-channel cell, a residual of %+d, so the channels are NOT "
         "independent at the alert level on this sample (%s)"
         % (total, base_n, base_n - total, ", ".join(parts))))

    # -- the activity gate ---------------------------------------------------
    gate = cells.get("gate_on")
    if gate is not None and base_n:
        gn = int(gate["alerts_total"])
        C["ablation_gate_alerts"] = gn
        C["ablation_gate_multiple"] = "%.2f" % (gn / base_n)
        gby = gate.get("alerts_by_checker") or {}
        bby = base.get("alerts_by_checker") or {}
        moved = sorted(set(gby) - set(bby))
        C["ablation_gate_new_channels"] = ", ".join(moved) or "none"
        C["ablation_gate_new_channels_n"] = len(moved)
        C["ablation_gate_line"] = (
            "one configuration flag, not a threshold, multiplies the alert "
            "count by %.2f -- from %d to %d over the same %s h of the same "
            "segments on the same pinned image -- which is a larger movement "
            "than any threshold on the registered grid produces%s"
            % (gn / base_n, base_n, gn, C["ablation_hours"],
               (", and it is the only configuration in which %s raised an "
                "alert at all" % ", ".join(moved)) if moved else ""))

    # -- compute cost per cell ----------------------------------------------
    walls = {l: float(c.get("wall_seconds", 0)) for l, c in cells.items()}
    if walls and hours:
        slowest = max(walls, key=walls.get)
        fastest = min(walls, key=walls.get)
        C["ablation_wall_slowest"] = slowest
        C["ablation_wall_fastest"] = fastest
        _ratio = walls[slowest] / walls[fastest] if walls[fastest] else 0.0
        C["ablation_wall_ratio"] = "%.2f" % _ratio
        C["ablation_baseline_rtf"] = "%.4f" % (walls["baseline"] / (hours * 3600.0))
        C["ablation_cost_line"] = (
            "the same footage costs %.2f times as much wall clock in the "
            "heaviest cell (%s) as in the lightest (%s), and the all-channel "
            "cell runs at %.2f times video time on this device, so a channel "
            "is bought with compute as well as with alerts"
            % (_ratio, slowest.replace("_", " "), fastest.replace("_", " "),
               walls["baseline"] / (hours * 3600.0)))


# ------------------------------------------------- E12/E12-b: three cost axes
def _theta_tag(x):
    """The canonical grid tag for a theta that arrives as a float."""
    return {0.3: "0.30", 0.375: "0.375", 0.45: "0.45",
            0.525: "0.525", 0.6: "0.60"}[round(float(x), 3)]


def count_cost_axes():
    """The three in-situ cost axes, from the file E12's own step 2 wrote.

    WHY THIS IS A COUNTER AND NOT A TABLE IN main.tex
        PREREGISTERED_E12B.md section 5 step 3 registers that the paper prints
        all three axes including the empty one, and that no number in that table
        is typed by hand. A claim of that shape is only checkable if the numbers
        come out of the measurement file at build time, so they do.

    THE THREE ARE NOT THREE VERSIONS OF ONE NUMBER
        C1 -> C2 is the axis the REGISTERED selection rule picks, and it emitted
        ZERO points: the replay recovered 0 of 185 FallChecker alerts and the
        gate returned stateful_divergence. V1/V2/V3 is what the allocation code
        actually priced on -- unregistered, 8 segments -- and it is degenerate
        at the deployed point, one segment carrying every alert. A1 is 175
        segments, resolves at three grid points and cannot reach the lower two.
        An empty axis, a degenerate axis and a resolved axis are three different
        findings, and nothing here averages them.
    """
    p = os.path.join(ANALYSIS, "e12", "E12_COST_AXIS.json")
    if not os.path.exists(p):
        note("three-axis cost file not found at %s" % p)
        return
    d = json.load(open(p, encoding="utf-8"))

    C["costaxis_seed"] = d.get("seed")
    C["costaxis_replicates"] = "{:,}".format(int(d.get("replicates", 0)))
    C["costaxis_n"] = 3
    C["costaxis_n_word"] = word(3)

    # -- axis 1: the registered one, and the gate number that emptied it -----
    reg = d.get("axis_registered_c1", {})
    gate = reg.get("reproduction_gate_fallchecker", {})
    npts = int(reg.get("points_emitted", 0))
    C["costaxis_creg_points"] = npts
    C["costaxis_creg_points_word"] = word(npts)
    C["costaxis_creg_roster"] = reg.get("roster_segments")
    C["costaxis_creg_theta"] = "%.2f" % float(reg.get("recorded_theta", 0))
    C["costaxis_creg_gate_segments"] = gate.get("segments")
    C["costaxis_creg_gate_real"] = gate.get("real")
    C["costaxis_creg_gate_replay"] = gate.get("replay")
    C["costaxis_creg_gate_verdict"] = str(
        gate.get("verdict", "")).replace("_", " ")
    C["costaxis_creg_line"] = (
        "the pass the registered selection rule names priced %s operating "
        "point: replaying its recorded candidates recovered %s of %s "
        "FallChecker alerts over %s segments and the reproduction gate returned "
        "%s, so the axis the registration selects is empty rather than wide"
        % (word(npts), gate.get("replay"), gate.get("real"),
           gate.get("segments"),
           str(gate.get("verdict", "")).replace("_", " ")))

    # -- axes 2 and 3: the points each one did emit --------------------------
    def _emit(prefix, block):
        got = []
        for _, pt in sorted(block.get("points", {}).items(),
                            key=lambda kv: float(kv[1]["theta"])):
            k = _wilson_key(_theta_tag(pt["theta"])).lower()
            got.append(pt)
            C["%s_%s_alerts" % (prefix, k)] = pt["alerts"]
            C["%s_%s_rate" % (prefix, k)] = "%.4f" % pt["rate_per_h"]
            C["%s_%s_theta" % (prefix, k)] = "%.3f" % float(pt["theta"])
            C["%s_%s_carrying" % (prefix, k)] = pt["segments_carrying_alerts"]
            C["%s_%s_largest_share" % (prefix, k)] = "%.1f" % (
                100.0 * pt["largest_single_segment_share"])
            lo, hi = pt["block_bootstrap_ci95"]
            C["%s_%s_boot" % (prefix, k)] = "[%.3f, %.3f]" % (lo, hi)
            plo, phi = pt["poisson_ci95"]
            C["%s_%s_poisson" % (prefix, k)] = "[%.3f, %.3f]" % (plo, phi)
            # P(0) is printed to two decimals, not rounded to a clean zero: at
            # theta 0.60 on A1 one resample in 20000 did return zero, and
            # "0.0 %" would have been a number we made tidier than it is.
            C["%s_%s_pzero" % (prefix, k)] = "%.2f" % (
                100.0 * pt["bootstrap_fraction_exactly_zero"])
        if got:
            C["%s_segments" % prefix] = got[0]["segments"]
            C["%s_hours" % prefix] = "%.4f" % got[0]["hours"]
            C["%s_points_n" % prefix] = len(got)
            C["%s_points_n_word" % prefix] = word(len(got))
        return got

    v = _emit("costaxis_v", d.get("axis_fallback_v", {}))
    a = _emit("costaxis_aone", d.get("axis_a1", {}))

    unreach = sorted(d.get("axis_a1", {}).get("unreachable", {}), key=float)
    C["costaxis_aone_unreachable_theta"] = ", ".join(
        "%.3f" % float(t) for t in unreach)
    C["costaxis_aone_unreachable_n"] = len(unreach)
    C["costaxis_aone_unreachable_n_word"] = word(len(unreach))

    # -- the hole at the high-coverage end, stated as a hole -----------------
    cov = d.get("coverage_extended_L2", {})
    if cov:
        best = max(cov, key=lambda t: cov[t])
        C["costaxis_best_coverage"] = "%.4f" % cov[best]
        C["costaxis_best_coverage_theta"] = "%.3f" % float(best)
        priced = best not in d.get("axis_a1", {}).get("unreachable", {})
        C["flag_best_coverage_priced_by_resolved_axis"] = (
            "yes" if priced else "no")
        _vb = d.get("axis_fallback_v", {}).get("points", {}).get("t%s" % best)
        _lo, _hi = (_vb or {}).get("block_bootstrap_ci95", (0.0, 0.0))
        _span_ratio = (_hi / _lo) if _lo else float("inf")
        C["costaxis_hole_line"] = (
            "the highest coverage this instrument reaches, %.4f at theta "
            "%.3f, is priced by neither axis this campaign registered: the "
            "registered pass emitted no point at all, and the corpus-wide pass "
            "recorded at the deployed threshold cannot reach a grid point below "
            "it. Its only in-situ price comes from the %s-segment pass the "
            "allocation code selected without a registration, whose interval "
            "there spans %s alerts per hour -- a factor of %.0f between its "
            "ends -- and returns exactly zero in %s per cent of resamples"
            % (cov[best], float(best), C.get("costaxis_v_segments"),
               C.get("costaxis_v_zerothreezero_boot", "?"),
               _span_ratio, C.get("costaxis_v_zerothreezero_pzero", "?")))

    # -- E12-b section 2a: do the two non-empty axes order the grid alike? ----
    if v and a:
        shared = sorted(set(p["theta"] for p in v)
                        & set(p["theta"] for p in a))
        ov = [p["theta"] for p in sorted(v, key=lambda p: p["rate_per_h"])
              if p["theta"] in shared]
        oa = [p["theta"] for p in sorted(a, key=lambda p: p["rate_per_h"])
              if p["theta"] in shared]
        same = ov == oa
        C["flag_cost_axis_branch"] = "A" if same else "B"
        C["costaxis_shared_points"] = len(shared)
        C["costaxis_shared_points_word"] = word(len(shared))
        C["costaxis_branch_line"] = (
            ("on the %s grid points both non-empty axes price, the two order "
             "the points identically, so the ORDERING is stable across them "
             "while the COST is not; a stable ordering is not evidence that "
             "either axis resolved the cost" % word(len(shared))) if same else
            ("the two non-empty axes order the shared grid points differently, "
             "so no allocated threshold is named at the budgets where they "
             "disagree"))

    # -- E12-b section 6: the demonstration point, by the registered rule -----
    # Admissible = the A1 points whose segment-block bootstrap excludes zero.
    # Median by cost; ties toward the cheaper. The rule was written down before
    # it was applied; it is EVALUATED here so the number D5s runs at and the
    # number the paper prints cannot come apart in two places.
    adm = [p for p in a if p["block_bootstrap_ci95"][0] > 0.0]
    if adm:
        adm.sort(key=lambda p: p["rate_per_h"])
        pick = adm[(len(adm) - 1) // 2]
        C["costaxis_demo_theta"] = "%.3f" % pick["theta"]
        C["costaxis_demo_rate"] = "%.4f" % pick["rate_per_h"]
        C["costaxis_demo_boot"] = "[%.3f, %.3f]" % tuple(
            pick["block_bootstrap_ci95"])
        C["costaxis_demo_admissible_n"] = len(adm)
        C["costaxis_demo_admissible_n_word"] = word(len(adm))
        C["costaxis_demo_line"] = (
            "one demonstration operating point, theta %.3f at %.4f alerts per "
            "hour, chosen by a rule fixed in the registration before it was "
            "applied -- the median by cost of the %s grid points an axis that "
            "resolved can price -- and reported as one member of an admissible "
            "set rather than as an optimum"
            % (pick["theta"], pick["rate_per_h"], word(len(adm))))


# ------------------------------------------------- D5s: the demonstration point
def count_d5s():
    """D5s, scored by E12's own statistic -- imported, not re-implemented.

    WHAT IT ANSWERS, AND ONLY THAT (E12-b section 6; PREREGISTERED_E8)
        Is the FallChecker rate at the demonstration point, on the 8
        out-of-sample segments, inside the bootstrap interval that point was
        selected within? If not, that is a result: nothing here or in the
        threshold table is adjusted to fit.

    WHY describe() IS IMPORTED FROM e12_cost_axis.py
        E12 registers one statistic for every axis -- per-segment hours and
        alerts, Poisson foil, segment block bootstrap, seed 20260911, 20 000
        replicates -- so that no axis is flattered by a method another did not
        get. A second implementation here would be a second method.

    THE SPLIT IS READ FROM THE HASHED LIST, NOT INFERRED
        d5_32seg.list is `cat sweep_sample_12h.list verify_sample_4h.list`, so
        the first 24 lines are the sweep sample and the last 8 are the
        out-of-sample segments. The list hash is checked against E8 first.

    AND ONE THING THE SPLIT DOES NOT MAKE TRUE
        "Out-of-sample" is E8's sense: disjoint from the 24 the sweep chain
        chose on. The demonstration point was priced on A1, which is the whole
        corpus and therefore contains all 32. That overlap is counted and
        emitted, so the sentence that reports D5s cannot omit it by accident.
    """
    import glob as _glob
    d5dir = os.path.join(RUNS, "d5s_allocated")
    lst = os.path.join(MEAS, "ops", "lists", "d5_32seg.list")
    if not os.path.isdir(d5dir) or not os.path.exists(lst):
        note("D5s: run directory or d5_32seg.list missing")
        return
    e8_sha = "8ca63e4115d3661d4e01df6123ce0d889180a0a861b873824ba965a59705bfe6"
    got_sha = hashlib.sha256(open(lst, "rb").read()).hexdigest()
    if got_sha != e8_sha:
        note("D5s: d5_32seg.list hash %s is not E8's %s -- not scored"
             % (got_sha, e8_sha))
        return
    ids = [x.strip() for x in open(lst, encoding="utf-8") if x.strip()]
    if len(ids) != 32 or len(set(ids)) != 32:
        note("D5s: list does not carry 32 distinct segments -- not scored")
        return
    sweep, oos = ids[:24], ids[24:]

    pp = json.load(open(os.path.join(d5dir, "pass_params.json"),
                       encoding="utf-8"))
    theta = float(pp["checker_params"]["FallDecision"])
    demo = C.get("costaxis_demo_theta")
    if demo is None or abs(theta - float(demo)) > 1e-9:
        note("D5s: ran at FallDecision %s but the demonstration point is %s "
             "-- not scored" % (theta, demo))
        return

    sys.path.insert(0, HERE)
    from e12_cost_axis import describe, SEED, REPLICATES

    per = {}
    for sid in ids:
        mp = os.path.join(d5dir, sid + ".json")
        cp = os.path.join(d5dir, sid + ".csv")
        if not (os.path.exists(mp) and os.path.exists(cp)):
            note("D5s: segment %s has no output -- not scored" % sid)
            return
        j = json.load(open(mp, encoding="utf-8"))
        fps = float(j.get("fps_effective") or j.get("fps") or 0)
        if not fps:
            note("D5s: segment %s has no frame rate -- not scored" % sid)
            return
        hours = float(j["frames_read"]) / fps / 3600.0
        with open(cp, newline="", encoding="utf-8") as fh:
            k = sum(1 for r in csv.DictReader(fh)
                    if r.get("checker") == "FallChecker")
        per[sid] = (hours, k)

    lo_demo, hi_demo = [float(x) for x in
                        C["costaxis_demo_boot"].strip("[]").split(",")]
    C["d5s_theta"] = "%.3f" % theta
    C["d5s_seed"] = SEED
    C["d5s_segments"] = len(ids)
    C["d5s_hours"] = "%.4f" % sum(h for h, _ in per.values())
    for name, group in (("oos", oos), ("sweep", sweep)):
        st = describe([per[s] for s in group])
        C["d5s_%s_segments" % name] = st["segments"]
        C["d5s_%s_segments_word" % name] = word(st["segments"])
        C["d5s_%s_hours" % name] = "%.4f" % st["hours"]
        C["d5s_%s_alerts" % name] = st["alerts"]
        C["d5s_%s_rate" % name] = "%.4f" % st["rate_per_h"]
        C["d5s_%s_carrying" % name] = st["segments_carrying_alerts"]
        C["d5s_%s_boot" % name] = "[%.3f, %.3f]" % tuple(
            st["block_bootstrap_ci95"])
        C["d5s_%s_pzero" % name] = "%.2f" % (
            100.0 * st["bootstrap_fraction_exactly_zero"])
        inside = lo_demo <= st["rate_per_h"] <= hi_demo
        C["flag_d5s_%s_inside_demo_interval" % name] = (
            "yes" if inside else "no")

    a1p = os.path.join(ANALYSIS, "e12", "A1_FALL_BY_SEGMENT.json")
    if os.path.exists(a1p):
        a1 = json.load(open(a1p, encoding="utf-8"))["segments"]
        C["d5s_oos_in_aone_n"] = sum(1 for s in oos if s in a1)
        C["d5s_oos_in_aone_n_word"] = word(C["d5s_oos_in_aone_n"])
    else:
        note("D5s: A1 per-segment table missing; overlap not counted")

    C["sample_sweep_segments"] = len(sweep)
    C["sample_verify_segments"] = len(oos)
    C["sample_verify_segments_word"] = word(len(oos))

    # The sentences are generated so that "inside"/"outside", the carrier count
    # and the overlap caveat cannot be edited apart from the numbers they
    # qualify. Each branch is written out; neither is the default.
    inside = C["flag_d5s_oos_inside_demo_interval"] == "yes"
    carriers = C["d5s_oos_carrying"]
    carried_short = ("all of them on %s of the %s segments" % (
        word(carriers), word(len(oos))) if carriers == 1 else
        "on %s of the %s segments" % (word(carriers), word(len(oos))))
    carried = carried_short
    # 2026-09-14: is the one carrier the segment that already carried every
    # alert this same sample raised at the deployed threshold? Counted, and
    # printed with its dilution on the corpus-wide pass beside it, so the
    # sentence says "dominates at eight segments" and cannot be read as 175.
    oos_car = [s for s in oos if per[s][1]]
    vprov = os.path.join(ANALYSIS, "FALL_FRONT_PROVENANCE.json")
    if carriers == 1 and os.path.exists(vprov) and os.path.exists(a1p):
        seg = oos_car[0]
        vseg = json.load(open(vprov, encoding="utf-8"))["points"].get(
            "t0.45", {}).get("per_segment", {})
        vtot = sum(x["alerts"] for x in vseg.values())
        vcar = [k for k, x in vseg.items() if x["alerts"]]
        a1tot = json.load(open(a1p, encoding="utf-8"))["totals"]
        tag = "%g" % theta
        subst = bool(a1[seg]["substituted_clock"])
        C["flag_d5s_oos_carrier_substituted"] = "yes" if subst else "no"
        C["flag_d5s_oos_carrier_is_v_sole_carrier"] = (
            "yes" if vcar == [seg] else "no")
        C["d5s_oos_carrier_v_alerts"] = vseg.get(seg, {}).get("alerts", 0)
        C["d5s_oos_carrier_v_total"] = vtot
        C["d5s_oos_carrier_aone_zerofourfive_alerts"] = a1[seg]["alerts"]["0.45"]
        C["d5s_oos_carrier_aone_zerofourfive_total"] = a1tot["0.45"]
        C["d5s_oos_carrier_aone_demo_alerts"] = a1[seg]["alerts"][tag]
        C["d5s_oos_carrier_aone_demo_total"] = a1tot[tag]
        if vcar == [seg] and subst:
            carried = (
                "all of them on one substituted-clock segment, the same one that "
                "carried all %d alerts this sample raised at the deployed "
                "threshold; on the corpus-wide pass that segment carries %d of %d "
                "alerts there and %d of %d at this point"
                % (vtot, a1[seg]["alerts"]["0.45"], a1tot["0.45"],
                   a1[seg]["alerts"][tag], a1tot[tag]))
    overlap = C.get("d5s_oos_in_aone_n")
    if overlap is None:
        overlap_txt = "an uncounted number of its segments also lie"
    elif overlap == len(oos):
        overlap_txt = "all %s of its segments also lie" % word(len(oos))
    else:
        overlap_txt = "%s of its %s segments also lie" % (word(overlap),
                                                         word(len(oos)))
    C["d5s_oos_line"] = (
        "Run for real at theta %.3f on the %s segments of the verification "
        "sample, the fall channel raised %d alerts in %s h, %s alerts per hour "
        "with a segment bootstrap of %s, %s. The point estimate lies %s the "
        "interval %s the point was selected within, and is reported as a "
        "result rather than absorbed into the table. The sample is "
        "out-of-sample only against the sweep sample: %s inside the "
        "corpus-wide pass that priced the point"
        % (theta, word(len(oos)), C["d5s_oos_alerts"], C["d5s_oos_hours"],
           C["d5s_oos_rate"], C["d5s_oos_boot"], carried,
           "inside" if inside else "outside", C["costaxis_demo_boot"],
           overlap_txt))
    C["d5s_concl_line"] = (
        "Run for real on the verification sample, that point raised %s alerts "
        "per hour, %s the interval it was selected within, %s"
        % (C["d5s_oos_rate"], "inside" if inside else "outside",
           carried_short))


# ------------------------------------------------- supplement sections owed
def count_supplement_owed():
    """S2, S6, S7 and S7's time-varying paragraph, from files already on disk.

    Scaffolded as placeholders in the supplement and never assigned until
    2026-09-14. Every value below is read from the artefact that holds it; no
    grid, seed, hash or rate is copied from prose. The one computation that is
    new -- the day/night allocation -- uses the day/night boundary registered
    in draw_sweep_samples.py and E12's own statistic, and is labelled in the
    supplement as computed after every result was known.
    """
    import re as _re

    # -- S2: registered grids (M3 B1, M3 Q1 for Fall, E5 withdrawals) -------
    m3p = os.path.join(MEAS, "PREREGISTERED_M3.md")
    e5p = os.path.join(MEAS, "PREREGISTERED_E5_UNINSTANTIATED_CHANNELS.md")
    if os.path.exists(m3p):
        m3 = open(m3p, encoding="utf-8").read()
        withdrawn = set()
        if os.path.exists(e5p):
            part = open(e5p, encoding="utf-8").read().split(
                "WITHDRAWN FROM THE", 1)
            if len(part) == 2:
                withdrawn = set(_re.findall(
                    r"^\| `(\w+)`", part[1].split("\n## ", 1)[0], _re.M))
        b1 = m3.split("## B1.", 1)[1].split("\n## ", 1)[0]
        # The knob cell is `name` (unit) for six rows and prose with backticks
        # for IntrusionChecker ("detector `conf` for `person`"), so it is taken
        # whole and the backticks stripped, rather than matched as one token.
        rows = [(ck, knob.replace("`", "").strip(), fr, gr) for ck, knob, fr, gr
                in _re.findall(
                    r"^\| \*\*(\w+)(?: \([^)]*\))?\*\* \| ([^|]+)\|[^|]*\| "
                    r"\*\*([\d.]+)\*\* \| ([^|]+)\|", b1, _re.M)]
        q1 = m3.split("Q1 → **RESOLVED**", 1)
        fall_grid = fall_frozen = None
        if len(q1) == 2:
            mg = _re.search(r"containing the frozen value:\*\*\s*\*\*"
                            r"([\d., ]+?)\.\*\*", q1[1])
            mf = _re.search(r"swept parameter is the literal `([\d.]+)`", q1[1])
            fall_grid = mg.group(1) if mg else None
            fall_frozen = mf.group(1) if mf else None
        n = 0
        for ck, knob, frozen, grid in rows:
            k = ck.lower()
            status = "withdrawn by E5" if ck in withdrawn else "registered"
            grid = grid.replace("*", "").strip()
            if ck == "FallChecker":
                if not (fall_grid and fall_frozen):
                    note("S2: the M3 Q1 FallDecision grid was not found")
                    continue
                knob, frozen, grid = "FallDecision", fall_frozen, fall_grid
                status = "registered; replaces the angle knob (M3 Q1)"
            C["grid_%s_knob" % k] = knob
            C["grid_%s_frozen" % k] = frozen
            C["grid_%s_values" % k] = grid
            C["grid_%s_status" % k] = status
            n += 1
        C["grid_rows_n"] = n
        if n != 7:
            note("S2: parsed %d grid rows from M3 B1, expected 7" % n)

    # -- S2: the two in-situ samples, hash-checked --------------------------
    for name, stem in (("sweep", "sweep_sample_12h"),
                       ("verify", "verify_sample_4h")):
        mp = os.path.join(MEAS, "ops", "samples", stem + ".meta.json")
        cp = os.path.join(MEAS, "ops", "samples", stem + ".csv")
        if not (os.path.exists(mp) and os.path.exists(cp + ".sha256")):
            note("S2: sample files for %s missing" % stem)
            continue
        got = hashlib.sha256(open(cp, "rb").read()).hexdigest()
        want = open(cp + ".sha256", encoding="utf-8").read().split()[0]
        if got != want:
            note("S2: %s.csv hashes to %s, recorded %s -- not emitted"
                 % (stem, got, want))
            continue
        m = json.load(open(mp, encoding="utf-8"))
        C["sample_%s_seed" % name] = m["seed"]
        C["sample_%s_drawn_n" % name] = m["n_drawn"]
        C["sample_%s_hours" % name] = "%.2f" % m["hours"]
        C["sample_%s_rule" % name] = m["rule"]
        C["sample_%s_strata" % name] = m["strata"]
        C["sample_%s_cells" % name] = "; ".join(
            "%s %d of %d" % (c.replace("|", "/"), v["quota"], v["available"])
            for c, v in sorted(m["cells"].items()))
        C["sample_%s_csv_sha" % name] = got[:16]

    # -- S2: ex-situ clip lists, hash-checked -------------------------------
    for corpus, csvp, shp in (
            ("gmdcsa24", os.path.join(EXSITU, "CLIPLIST_gmdcsa24.csv"),
             os.path.join(EXSITU, "CLIPLIST_gmdcsa24.sha256")),
            ("furg", os.path.join(EXSITU, "CLIPLIST_furg.csv"),
             os.path.join(EXSITU, "CLIPLIST_furg.sha256")),
            ("virat", os.path.join(EXSITU, "virat", "CLIPLIST_virat.csv"),
             os.path.join(EXSITU, "virat", "CLIPLIST_virat.csv.sha256"))):
        if not (os.path.exists(csvp) and os.path.exists(shp)):
            note("S2: clip list for %s missing" % corpus)
            continue
        got = hashlib.sha256(open(csvp, "rb").read()).hexdigest()
        want = open(shp, encoding="utf-8").read().split()[0]
        if got != want:
            note("S2: clip list %s hashes to %s, recorded %s -- not emitted"
                 % (corpus, got, want))
            continue
        with open(csvp, newline="", encoding="utf-8") as fh:
            nrows = sum(1 for _ in csv.DictReader(fh))
        C["exsitu_list_%s_clips" % corpus] = nrows
        C["exsitu_list_%s_sha" % corpus] = got[:16]
        metap = csvp.replace(".csv", ".meta.json")
        if os.path.exists(metap):
            meta = json.load(open(metap, encoding="utf-8"))
            C["exsitu_list_%s_fixed" % corpus] = str(
                meta.get("fixed_at", ""))[:16].replace("T", " ")
            if meta.get("clips") not in (None, nrows):
                note("S2: %s meta says %s clips, list has %d"
                     % (corpus, meta.get("clips"), nrows))
    gtp = os.path.join(EXSITU, "virat", "GT_running_virat.csv")
    if os.path.exists(gtp):
        C["exsitu_gt_virat_sha"] = hashlib.sha256(
            open(gtp, "rb").read()).hexdigest()[:16]

    # -- S6: forklift per class, and the seeded subsample beside the full ---
    for split in ("full", "seed500"):
        p = os.path.join(ANALYSIS, "ForkliftSpeedChecker_%s_layer1.json" % split)
        if not os.path.exists(p):
            note("S6: %s missing" % os.path.basename(p))
            continue
        d = json.load(open(p, encoding="utf-8"))
        C["layer1_forklift_%s_images" % split] = d["n_images"]
        C["layer1_forklift_%s_map50" % split] = "%.4f" % d["mAP_50_all_classes"]
        if d.get("seed") is not None:
            C["layer1_seed500_seed"] = d["seed"]
        for cls, v in sorted(d["per_class"].items()):
            stem = "layer1_forklift_%s_%s" % (split, cls)
            C[stem + "_instances"] = v["instances_evaluated"]
            C[stem + "_ap50"] = "%.4f" % v["ap50"]
            C[stem + "_precision"] = "%.4f" % v["precision_at_maxF1"]
            C[stem + "_recall"] = "%.4f" % v["recall_at_maxF1"]
    for ck in ("FallChecker", "IntrusionChecker", "RunningChecker"):
        p = os.path.join(ANALYSIS, "%s_seed500_layer1.json" % ck)
        if not os.path.exists(p):
            note("S6: %s missing" % os.path.basename(p))
            continue
        d = json.load(open(p, encoding="utf-8"))
        person = (d.get("per_class") or {}).get("person") or {}
        stem = "layer1_%s_seed500" % ck.lower()
        C[stem + "_images"] = d["n_images"]
        if person:
            C[stem + "_person_instances"] = person["instances_evaluated"]
            C[stem + "_person_ap50"] = "%.4f" % person["ap50"]
            C[stem + "_person_recall"] = "%.4f" % person["recall_at_maxF1"]

    # -- S7: the deployed alert stream by hour, day, half and view ----------
    tp = os.path.join(ANALYSIS, "tier0", "tier0_results.json")
    if os.path.exists(tp):
        d = json.load(open(tp, encoding="utf-8"))
        for h, v in d["result2_by_hour"].items():
            stem = "tier0_hour_%02d" % int(h)
            C[stem + "_h"] = "%.3f" % v["obs_h"]
            C[stem + "_n"] = v["n"]
            C[stem + "_rate"] = "%.3f" % v["rate"]
        days = d.get("result2c_by_day") or {}
        if not days:
            note("S7: tier0_results.json carries no per-day table")
        for i, (date, v) in enumerate(sorted(days.items()), 1):
            stem = "tier0_day_%d" % i
            C[stem + "_date"] = date
            C[stem + "_h"] = "%.3f" % v["obs_h"]
            C[stem + "_n"] = v["n"]
            C[stem + "_rate"] = "%.3f" % (v["n"] / v["obs_h"]) if v["obs_h"] else "n/a"
        C["tier0_days_n"] = len(days)
        segs_split = d.get("result3_split_segments") or {}
        for half in ("first", "second"):
            v = d["result3_split"][half]
            stem = "tier0_split_%s" % half
            C[stem + "_h"] = "%.3f" % v["h"]
            C[stem + "_n"] = v["n"]
            C[stem + "_rate"] = "%.3f" % (v["n"] / v["h"])
            C[stem + "_ci"] = "[%.3f, %.3f]" % tuple(v["ci"])
            if half in segs_split:
                C[stem + "_segments"] = segs_split[half]
        C["tier0_split_boundary"] = d["result3_split"]["boundary_file"].replace(
            ".mp4", "")
        cis = d.get("result4_views_ci") or {}
        for view, v in d["result4_views"].items():
            stem = "tier0_view_%s" % view.lower()
            C[stem + "_segments"] = v["segments"]
            C[stem + "_h"] = "%.3f" % v["h"]
            C[stem + "_n"] = v["n"]
            C[stem + "_rate"] = "%.3f" % (v["n"] / v["h"])
            if view in cis:
                C[stem + "_ci"] = "[%.3f, %.3f]" % tuple(cis[view])
        mt = d.get("result4_matched")
        if mt:
            C["tier0_matched_hours"] = ", ".join("%02d:00" % h
                                                 for h in mt["hours"])
            for view, v in mt["views"].items():
                stem = "tier0_matched_%s" % view.lower()
                C[stem + "_h"] = "%.3f" % v["h"]
                C[stem + "_n"] = v["n"]
                C[stem + "_rate"] = ("%.3f" % (v["n"] / v["h"])) if v["h"] else "n/a"
        else:
            note("S7: no matched-hours view comparison in tier0_results.json")

    # -- S7: sensitivity grid, the one input not already a macro ------------
    for kind in ("graded", "uniform"):
        p = os.path.join(ANALYSIS, "weights_%s.json" % kind)
        if os.path.exists(p):
            C["sens_weight_fall_%s" % kind] = "%.1f" % json.load(
                open(p, encoding="utf-8"))["FallChecker"]

    # -- S7: what a static allocation costs against a day/night one ---------
    a1p = os.path.join(ANALYSIS, "e12", "A1_FALL_BY_SEGMENT.json")
    e12p = os.path.join(ANALYSIS, "e12", "E12_COST_AXIS.json")
    dsp = os.path.join(HERE, "draw_sweep_samples.py")
    if not all(os.path.exists(p) for p in (a1p, e12p, dsp)):
        note("S7: A1 table, E12 file or draw_sweep_samples.py missing; "
             "no day/night allocation")
        return
    mday = _re.search(r"DAY_START, DAY_END = (\d+), (\d+)",
                      open(dsp, encoding="utf-8").read())
    if not mday or C.get("costaxis_demo_theta") is None:
        note("S7: registered day boundary or demonstration point not found")
        return
    d0, d1 = int(mday.group(1)), int(mday.group(2))
    C["tv_day_start"] = "%02d:00" % d0
    C["tv_day_end"] = "%02d:00" % d1
    a1 = json.load(open(a1p, encoding="utf-8"))
    cov = json.load(open(e12p, encoding="utf-8"))["coverage_extended_L2"]
    grid = ["%g" % t for t in a1["grid"]]
    sys.path.insert(0, HERE)
    from e12_cost_axis import describe
    strata = {"day": [], "night": []}
    for sid, v in a1["segments"].items():
        hh = int(sid.split("_")[2][:2])
        strata["day" if d0 <= hh < d1 else "night"].append(v)
    H = sum(v["hours"] for v in a1["segments"].values())
    hrs, rate = {}, {}
    for s, vs in strata.items():
        hrs[s] = sum(v["hours"] for v in vs)
        C["tv_%s_segments" % s] = len(vs)
        C["tv_%s_hours" % s] = "%.4f" % hrs[s]
        for t in grid:
            st = describe([(v["hours"], v["alerts"][t]) for v in vs])
            k = _wilson_key(_theta_tag(float(t))).lower()
            rate[(s, t)] = st["rate_per_h"]
            C["tv_%s_%s_alerts" % (s, k)] = st["alerts"]
            C["tv_%s_%s_rate" % (s, k)] = "%.4f" % st["rate_per_h"]
            C["tv_%s_%s_boot" % (s, k)] = "[%.3f, %.3f]" % tuple(
                st["block_bootstrap_ci95"])
    demo = "%g" % float(C["costaxis_demo_theta"])
    budget = sum(v["alerts"][demo] for v in a1["segments"].values()) / H
    best = None
    for td in grid:
        for tn in grid:
            spend = (hrs["day"] * rate[("day", td)]
                     + hrs["night"] * rate[("night", tn)]) / H
            if spend <= budget + 1e-12:
                c = (hrs["day"] * cov[td] + hrs["night"] * cov[tn]) / H
                if best is None or c > best[0] + 1e-12:
                    best = (c, td, tn, spend)
    C["tv_budget"] = "%.4f" % budget
    C["tv_static_theta"] = "%.3f" % float(demo)
    C["tv_static_coverage"] = "%.4f" % cov[demo]
    C["tv_best_day_theta"] = "%.3f" % float(best[1])
    C["tv_best_night_theta"] = "%.3f" % float(best[2])
    C["tv_best_coverage"] = "%.4f" % best[0]
    C["tv_best_spend"] = "%.4f" % best[3]
    C["tv_gain"] = "%.4f" % (best[0] - cov[demo])
    C["flag_tv_best_is_static"] = "yes" if best[1] == best[2] == demo else "no"


# ------------------------------------------------- our own silent mechanisms
def count_harness_silent():
    """The same failure this paper reports, committed by this paper's own tools.

    Six of them, and the register is a file rather than a memory because the
    manuscript previously said "three times" with nothing naming which three
    (CLAIM_LEDGER D8). They are NOT added to the seven-row deployment register:
    that table is about the system under test, and merging the two would let a
    reader think we found seven defects in someone else's system when we found
    seven there and six here.
    """
    p = os.path.join(ANALYSIS, "harness_silent.csv")
    if not os.path.exists(p):
        note("harness silent-mechanism register not found at %s" % p)
        return
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    if not rows:
        note("harness silent-mechanism register is empty")
        return
    C["harness_silent_n"] = len(rows)
    C["harness_silent_n_word"] = word(len(rows))
    for r in rows:
        k = r["id"].lower()
        for col in ("mechanism", "asserted", "observed", "detected_by",
                    "lifetime", "known_issue", "found_on"):
            C["harness_silent_%s_%s" % (k, col)] = r[col]
    C["harness_silent_register"] = ", ".join(
        "%s (%s)" % (r["id"], r["known_issue"]) for r in rows)
    # The sentence deliberately reports a DETECTION rate and not an incidence
    # rate. Six of the seven were found on one day, which says how hard we
    # looked that day, not how often the phenomenon occurs; a reader who takes
    # the count for a prevalence has been misled by us rather than by the data.
    import collections as _c
    by_day = _c.Counter(r.get("found_on", "") for r in rows)
    busiest, n_busiest = (by_day.most_common(1) or [("", 0)])[0]
    C["harness_silent_same_day"] = n_busiest
    C["harness_silent_busiest_day"] = busiest
    C["harness_silent_days"] = len(by_day)
    C["harness_silent_same_day_word"] = word(C["harness_silent_same_day"])
    C["harness_silent_line"] = (
        "%s such mechanisms in our own measurement apparatus asserted success "
        "and were absent in effect over one campaign, %s of them found on a "
        "single day and every one of them by a second instrument rather than "
        "by the gate responsible for it -- a rate of detection, which is not "
        "the same quantity as a rate of occurrence"
        % (word(len(rows)), C["harness_silent_same_day_word"]))


def count_label_cells_total():
    """The label cells, summed FROM the three packs that hold them.

    A separate counter and not a line inside count_label_packs(): the intrusion
    pack is counted by a DIFFERENT function that runs later, so computing the
    total there read a key that did not exist yet. The guard said so and emitted
    nothing, the supplement then failed to compile on the undefined macro, and
    both behaved correctly -- which is the only reason this is a note in a log
    and not a wrong total on a page.
    """
    # The cells cells, summed FROM their three packs rather than remembered.
    # The AI-tools declaration in the main text and in S9 both quote this
    # number while asserting that none of the cells had a machine-proposed
    # label; a declaration that quotes a remembered total is the wrong shape of
    # sentence to put in a declaration.
    _members = {"intrusion": C.get("intrusion_pack_n"),
                "fall": C.get("spotcheck_fall_n"),
                "helmet": C.get("spotcheck_helmet_n")}
    if all(v is not None for v in _members.values()):
        C["label_cells_total"] = sum(_members.values())
        C["label_cells_members"] = ", ".join(
            "%s %d" % (k, _members[k]) for k in sorted(_members))
    else:
        note("label cell total not emitted: missing %s"
             % ", ".join(k for k, v in _members.items() if v is None))


# ------------------------------------------------- composite-quantity guard
def check_composites():
    """A total that does not move while its parts do is a total that hides.

    `char_coverage_measurable_n` stayed at 3 on 2026-09-10 while SmokeFire left
    the column and Running entered it. The number was correct and it concealed
    two changes, which is the same defect as a summary line that contradicts its
    own table -- the fifth instance of it this week. Every composite therefore
    emits its MEMBERS beside its value, so a reader and a diff can both see
    which parts produced the count.
    """
    composites = {
        "char_far_measurable_n": "char_%s_far",
        "char_coverage_measurable_n": "char_%s_coverage",
        "char_in_allocation_n": "char_%s_allocation",
    }
    keys = [k[len("char_"):-len("_far")] for k in C
            if k.startswith("char_") and k.endswith("_far")]
    missing = [t for t in composites if t not in C]
    if missing:
        # The first version of this ran before count_characterizability() and
        # found none of these, and `continue` made that indistinguishable from
        # success. A check that can quietly check nothing is not a check.
        sys.stderr.write(
            "count_everything: check_composites found none of " + ", ".join(missing) + ". Either the "
            "counters that produce them have not run yet, or they were renamed. "
            "Refusing to report a pass on an empty check." + chr(10))
        sys.exit(2)
    for total, pat in composites.items():
        members = sorted(k for k in keys if C.get(pat % k) == "yes")
        C[total + "_members"] = ", ".join(members) or "none"
        if len(members) != C[total]:
            sys.stderr.write(
                "count_everything: %s says %d but %d member(s) qualify (%s). A "
                "composite and its members must agree.\n"
                % (total, C[total], len(members), ", ".join(members)))
            sys.exit(2)


def main():
    # The macro file is a BUILD ARTEFACT, not a source: it is regenerated from
    # generated_counts.json on every build. A second manuscript tree (the TIM
    # submission) therefore asks for it to be written where its own build will
    # read it, rather than keeping a copy of its own -- a copy is how two
    # numbers start disagreeing with nothing to say which is stale.
    tex_out, make_tex_out = MANU, False
    for i, a in enumerate(sys.argv):
        if a == "--tex-out" and i + 1 < len(sys.argv):
            tex_out = os.path.abspath(sys.argv[i + 1])
            make_tex_out = True
    preflight(tex_out, make_tex_out)
    count_insitu()
    count_pipeline_gating()
    count_observation_hours()
    count_fall_theta_curve()
    count_far_strata()
    count_gmdcsa24()
    count_furg()
    count_omnifall_annotations()
    count_results()
    count_prose()
    count_silent_mechanisms()
    count_virat_running()
    count_degradation_band()
    count_noise_floor()
    count_reproduction_gate()
    count_layer1()
    count_fall_front()
    count_label_packs()
    count_e9_outcomes()
    count_e10_outcomes()
    count_harness_silent()
    count_cost_axes()
    count_d5s()          # after count_cost_axes: it checks the demo theta
    count_supplement_owed()   # after count_cost_axes: needs the demo theta
    count_ablation()
    count_preregistrations()
    # characterisability BEFORE thin evidence: "entering the allocation" is a
    # verdict that counter produces, and D7 was exactly the cost of asking the
    # question in the other order (CLAIM_LEDGER D7).
    count_characterizability()
    count_thin_evidence()
    # AFTER the counters it guards. Placed before them on the first attempt,
    # where it found nothing to check and said nothing about finding nothing --
    # a guard running before its subject, which is the defect it exists to
    # catch. It now refuses to be a no-op; see the function.
    count_label_cells_total()
    check_composites()

    C["_generated_at"] = datetime.datetime.now().astimezone().isoformat()
    C["_generator"] = "01_Measurement/scripts/count_everything.py"

    # All three payloads are built first and written last, together. A run that
    # dies while building leaves the previous three files untouched rather than
    # one fresh file and two stale ones.
    json_text = json.dumps(C, indent=2, sort_keys=True)

    lines = ["% GENERATED by 01_Measurement/scripts/count_everything.py -- DO NOT EDIT.",
             "% Every macro here was counted from the files listed in the clip lists",
             "% and manifests. Editing this file by hand defeats its entire purpose.",
             "%% generated %s" % C["_generated_at"], ""]
    for k in sorted(C):
        if k.startswith("_"):
            continue
        v = C[k]
        if isinstance(v, str) and not k.startswith(TEX_LITERAL_PREFIXES):
            v = texescape(v)
        if isinstance(v, (int, float, str)):
            lines.append(r"\newcommand{\%s}{%s}" % (texname(k), v))
    tex_text = "\n".join(lines) + "\n"

    md = ["# GENERATED COUNTS", "",
          "Produced by `01_Measurement/scripts/count_everything.py` at build time.",
          "**Every number here was counted from files. None was copied from a summary.**",
          "", "Generated: %s" % C["_generated_at"], "", "| quantity | value |", "|---|---|"]
    for k in sorted(C):
        if k.startswith("_"):
            continue
        md.append("| `%s` | %s |" % (k, json.dumps(C[k]) if isinstance(C[k], dict) else C[k]))
    if NOTES:
        md += ["", "## Not counted this run", ""]
        md += ["- %s" % n for n in NOTES]
    write_atomically(os.path.join(MEAS, "generated_counts.json"), json_text)
    write_atomically(os.path.join(tex_out, "generated_counts.tex"), tex_text)
    write_atomically(os.path.join(MEAS, "GENERATED_COUNTS.md"),
                     "\n".join(md) + "\n")

    print("counted %d quantities" % len([k for k in C if not k.startswith("_")]))
    for n in NOTES:
        print("  NOTE:", n)
    print("wrote generated_counts.json, GENERATED_COUNTS.md, and "
          "generated_counts.tex -> %s" % tex_out)


if __name__ == "__main__":
    main()
