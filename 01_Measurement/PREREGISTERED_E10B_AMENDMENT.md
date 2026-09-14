# PREREGISTERED E10-b — the reporting rule for E10, amended before E10 runs

**Locked 2026-09-10, evening, author decision, BEFORE the `RUNCTL` job starts.**
The daemon is stopped at the moment of writing; `out/runctl_virat_t001` does not
exist; `RUNCTL` is in `RUN_QUEUE.json` as `PENDING` and has never been launched.
This file must be hashed before the daemon is restarted, and it was.

Amends the **reporting rule** of `PREREGISTERED_E10_RUNCTL.md`
(`d350b51daa883a50f25218d3a401ff60beed8eb31583ffaa9e8a2051c89bbe01`), which is
**not edited**. It amends no decision, no grid, no clip list, no ground truth,
no matching rule and no admission rule.

---

## 1. The defect in E10 as written

E10 §1 contains a self-binding clause:

> **E10 cannot remove RunningChecker from the allocation.** E9 §1.4 branch 1
> admitted it on a criterion … that is already satisfied and is not reopened.

The clause is **correct** about §11: a locked decision is not amendable by a
later file, and E9 §1.4 admitted the channel on `side_calls_with_boxes ≥ 1`,
which is satisfied and stays satisfied whatever E10 returns.

But the clause as phrased produces a control that can **confirm and never
disconfirm**. On the favourable branch it strengthens the channel's evidence; on
the unfavourable branch it changes nothing that reaches the reader. That is the
same shape `HARNESS-27` taught this project on the same day: *an instrument that
can only err towards accepting never produces the observation that would expose
it.* A one-sided control is not a control. Registering one and calling it a
positive control would be worse than not running it.

## 2. The amendment: separate the decision from the evidence

Two things were fused and are hereby separated.

**The decision stands.** RunningChecker remains in the allocation under E9 §1.4.
Nothing below withdraws it, and §11 is respected exactly.

**The evidence is reported in full, on either branch.** E10's result is printed
whichever way it falls, beside the decision it bears on, and the reader is left
to weigh them. Specifically, on the unfavourable branch the manuscript prints a
sentence of this form:

> The registered admission rule was satisfied — the checker executed
> \CntXThreebSideCallsWithBoxes{} times and returned no event, which is a
> measurement — and a later positive control at a threshold below the registered
> grid **could not confirm** that this channel's alert path is capable of firing
> on any input. The admission decision was fixed before that control existed and
> is not withdrawn here; the evidence that qualifies it is printed with it.

That is not a retraction and it is not a hedge. It is the two facts, adjacent,
in the order they occurred.

## 3. The reporting rule, fixed before the run

| branch | decision | what the manuscript prints |
|---|---|---|
| **alerts > 0** at 0.01 | unchanged (in) | the path is demonstrably capable of firing; X3b's zeros carry a positive control; the Limitations asymmetry sentence is **removed** |
| **alerts = 0** at 0.01 | unchanged (in) | the path has never been shown to fire on any input; the admission rule was satisfied on a criterion that does not test this; the asymmetry sentence becomes a statement about **both** zero-coverage channels, and §S5 records that this control was registered, run, and did not confirm |

**Both branches are printed.** A control reported only when it flatters is a
lottery ticket, and the temptation to omit is strongest on exactly the branch
that carries information.

**No third branch.** A zero at 0.01 may not be rescued with a lower threshold, a
different corpus, a different module list, or a synthetic clip, without a new
pre-registration carrying its own stated reason. E10 §5's limit also stands:
this cannot separate "the deployed vertical-motion rule is insensitive to
VIRAT's lateral running" from "the path is inert", and no sentence may claim it
does.

## 4. Why this is an amendment and not a new decision

`GT_PROTOCOL.md` §11 forbids changing a **decision** after seeing the result it
governs. Nothing here changes a decision:

- the admission rule is untouched and its outcome is unchanged;
- the θ grids, clip lists, ground truth, matching rule and interval method are
  untouched;
- what changes is **what gets printed**, and it changes in the direction of
  printing *more* on the branch where the temptation is to print less.

An amendment that makes the unfavourable branch louder cannot be a device for
flattering the result, which is the property that makes it admissible under §11
while the run is still unstarted. Had it been written after seeing E10's output,
it would not be admissible on any argument, which is why it is being written
tonight and hashed before the daemon is restarted.
