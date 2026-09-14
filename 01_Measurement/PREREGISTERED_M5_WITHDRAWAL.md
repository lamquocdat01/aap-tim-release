# M5 WITHDRAWN — `SKIPPED-BY-DECISION`, 2026-09-12

**A registration of a withdrawal, not of a result.** It records why the 48 h
soak is not run, what the paper may and may not say in its place, and the
standing rule the failure produced. It changes no θ grid, no sample, no seed,
no matching rule and no interval method.

Prior registrations this one is subordinate to and does not amend:
`PREREGISTERED_M3.md`, `PREREGISTERED_E5_ADDENDUM_M4E_MATRIX.md`.

---

## 1. THE PREMISE OF M5 DOES NOT EXIST IN THE PINNED IMAGE

M5 is registered as *"Soak, at least 48 h, RTSP loop source through a separate
compose override"*. Its source service is `ffmpeg` **from the pinned engine
image**, chosen deliberately so the soak introduces no software the deployment
does not already have, muxing a recorded segment in a loop and **listening** for
the engine to connect:

```
-f rtsp -rtsp_flags listen -rtsp_transport tcp rtsp://0.0.0.0:8554/soak
```

**That capability is not in the image.** Checked on the device, 2026-09-12, in
the pinned image `ghcr.io/lamquocdat01/aap-ai-engine:jetson`:

| probe | result |
|---|---|
| `ffmpeg -version` | `4.4.2-0ubuntu0.22.04.1` |
| `-h muxer=rtsp` | AVOptions are `rtpflags`, `rtsp_transport`, `min_port`, `max_port`, `buffer_size`, `pkt_size`. **There is no `rtsp_flags`.** |
| `-h demuxer=rtsp` | `-rtsp_flags <flags>  .D.........` — **demuxer only**, and `listen` is one of its values |
| the actual invocation | `[tcp @ …] Connection to tcp://0.0.0.0:8554?timeout=0 failed: Connection refused` / `Could not write header for output file #0` |

The RTSP **muxer** in FFmpeg is a *client*: it announces to a server and pushes.
`-rtsp_flags listen` is accepted on input and **silently ignored on output**, so
the option that was supposed to make ffmpeg a server made it a client that
dialled `0.0.0.0` and was refused. Serving RTSP needs a server — `mediamtx`,
`rtsp-simple-server`, or ffmpeg built with one — and there is none in the image.

## 2. WHY THE FIX IS NOT AVAILABLE, IN TWO INDEPENDENT WAYS

1. **It breaks a standing rule.** A real RTSP server means adding a container to
   the pinned set in the middle of a measurement campaign. The frozen-image rule
   exists precisely so that no result is measured against a build the rest of the
   campaign was not measured against. The override file says so in its own
   header: `image:` is not overridden anywhere.
2. **It changes what M5 measures.** With a third-party RTSP server in the loop,
   an endurance result is an endurance result of *engine + that server*, and any
   stall becomes unattributable between them. What could be run is therefore not
   the M5 that was registered, and reporting it under M5's name would be
   answering a different question in the slot reserved for this one.

Either reason alone is sufficient. Together they mean there is nothing to fix:
the job as registered cannot run, and the job that can run is not this job.

## 3. THE DECISION

**M5 → `SKIPPED-BY-DECISION`**, recorded in `ops/RUN_QUEUE.json` as status
`SKIPPED` with an `adjudicated` field naming this file and its hash. **Not
`FAILED`.** A `FAILED` status says the job ran and did not produce what it
promised; that was true of the 2026-09-10 attempt and is not true of the
decision taken today. The distinction is the one `run_queue.py` already draws
between BLOCKED and FAILED at the top of its own source, and it is drawn here
for the same reason.

`M5x` (the 72 h extension) stays `SKIPPED`; it was already, and its dependency
is now permanently unsatisfiable.

## 4. WHAT SECTION III MAY SAY INSTEAD — AND IT IS A WEAKER CLAIM

Section III may report **continuous operation observed during the campaign**,
and must report the limit that comes with it:

> the campaign ran the engine over 175 segments and 83.9626 h of recorded
> footage, plus the ex-situ and ablation passes; **but `run_pass.sh` starts a
> container per segment with `docker run --rm`, so the longest unbroken engine
> lifetime anywhere in this campaign is one segment.** What is demonstrated is
> that the pipeline survives being started, run and torn down several hundred
> times without manual intervention. It is **not** a demonstration that the
> engine survives 48 h without a restart, and the paper does not say it is.

**Registered before the sentence is written:** the words *soak*, *endurance* and
*uptime* are not used for this observation, and no figure plots it against a
time axis longer than one segment. A weaker claim printed as a weaker claim is
the whole subject of this paper; printed as an equivalent one it would be an
instance of what the paper reports.

## 5. THE STANDING RULE THIS PRODUCES — GROUP (a), BINDING FROM NOW

> **Before a measurement is registered, the device must be shown to produce the
> signal that measurement reads. A positive check on the device, not on the
> checker.**

M5 was registered, queued, given 48 h of the budget and launched on a premise
**nobody had ever tried**: that this ffmpeg could serve RTSP. One `docker run`
of eighteen seconds would have said no, on 2026-09-04, when the override was
written and `docker compose config` was accepted as validation. `config`
validates syntax; it cannot know whether a flag does anything.

This is the same family as the rule of 2026-09-10 — *every gate needs a second
independent instrument or a positive control* — one level lower down. That rule
asks whether the **gate** can see. This one asks whether the **signal exists at
all**. SFCTL and RUNCTL are what it looks like when it is obeyed: a control run
at a threshold far below the grid, written down in advance, whose only job is to
prove the path can fire. `--preflight` passing nine of nine checks over a stream
that never existed (HARNESS-30) is what it looks like when it is not.

**Added to `RULE_INVENTORY_20260910.md` group (a)**, with its gate: a registered
job whose `requires_capability` list is non-empty may not leave PENDING until
each capability has a dated positive check on the device recorded in
`ops/CAPABILITY_CHECKS.md`.

## 6. THE ARITHMETIC AFTER THE WITHDRAWAL

| | |
|---|---|
| machine jobs left | **D5s only** |
| D5s estimate | **25.0 h** (`RUN_QUEUE.json`; the 20.8 h in `REMAINING_MEASUREMENTS.md` of 2026-09-10 is stale and is corrected) |
| blocked on | `ops/lists/allocated_theta.json`, an author signature |
| campaign complete | ≈ 26 h after the signature |
| hard deadline | 2026-09-20 23:59 |

## 7. WHAT THIS WITHDRAWAL DOES NOT DO

- It does **not** delete M5 from the queue or from the "Campaign complete"
  milestone. The milestone is satisfied by a job withdrawn on a recorded
  decision, and the dashboard prints **which** job was satisfied that way, so a
  milestone met by withdrawal is never mistaken for one met by measurement.
- It does **not** claim the device would have failed a 48 h soak. Nothing is
  known about that either way, and Section III says nothing about it.
- It does **not** license adding software to the pinned image later in the
  campaign for some other purpose.
