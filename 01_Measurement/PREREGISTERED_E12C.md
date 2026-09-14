# PREREGISTERED E12-c — AMENDMENT TO E12-b ITEM 5: WHERE THE COVERAGE HOLE IS REPORTED

**Written 2026-09-13, before the text it governs was moved.** This file is hashed at the moment
of writing and the hash is recorded in `GT_protocol/GT_PROTOCOL.md` §11 as a new row. The paragraph
it amends was verified still present, unmoved, in `main.tex` at the moment of hashing.

**This amends exactly one clause of one registration. Nothing else in `PREREGISTERED_E12B.md`
is touched, and that file is not edited.**

---

## 1. What is being amended

`PREREGISTERED_E12B.md`, item **5** of §2, locked 2026-09-12 09:11:28,
SHA256 `e1b3e2249c530f1f2fb81589a27077b739c094d28203bcfe89299ba2da8da0e3`:

> **5. The high-coverage end is printed as a stated hole in the evidence**, in the main text and
> not only in the supplement: the most attractive point the instrument offers (coverage 0.6282 at
> θ = 0.30) is priced by **no axis this campaign registered**. The sentence appears next to the
> coverage number, not in a different table from it.

## 2. What changes, and what does not

**Changes — and it is a change of *length*, not of *location*:**

The working-through of the hole — the three axes restated, the comparison between them, and the
consequence drawn out — moves to the supplement. What remains in the main text is **one sentence
that states the hole and carries its number**.

**Does not change. All of it:**

1. The hole is still stated **in the main text**, not only in the supplement.
2. The sentence still appears **next to the coverage number**, in the same subsection, not in a
   different table from it.
3. The sentence still carries **the number**: the factor of **58** between the ends of the only
   in-situ interval that prices the high-coverage end, and the fact that the pass producing it was
   **selected by code and not by any registration**.
4. **No entry is invented at θ = 0.300 or 0.375.** E12 §4's rule stands: no interpolation, no
   bound, no dash.
5. **No number changes.** Not one. This amendment moves prose and nothing else. `generated_counts`
   is untouched by it; every figure in the moved text is the same macro it always was.
6. Items 1, 2, 3, 4, 6, 7 of E12-b §2 are **unaffected** and remain binding.

## 3. Why

Page budget. The author's overage budget is zero (recorded in
`02_Manuscript/PAGE_PRICE_20260912.md` §0, superseding the 2026-09-03 threshold), and the decision
to reach eight pages by **moving content to the supplement rather than paying** was taken by the
author on **2026-09-13, in chat**, after seeing the measured table of every alternative
(`PAGE_PRICE_20260912.md`, §13/09 chiều: no combination of content moves reached the requirement;
the deficit was measured at each step rather than estimated).

This is a **reporting-location rule**, not a measurement decision. It says where a sentence is
printed. It does not say what was measured, how, or what the answer was — so it is the author's to
amend, and the amendment is recorded rather than taken silently.

## 4. The condition that makes this amendment honest

**A reader who reads only the main text must still learn both things: that the high-coverage end of
this instrument is priced by no registered axis, and how wide the only interval that prices it is.**

If the sentence that survives in the main text does not carry both, this amendment is void and the
full paragraph goes back. That is a check, not an intention: `check_method_claims.py` and the
build's placeholder scan both read the rendered page, and the sentence is written with its macro so
it cannot drift from the table it is next to.

## 5. What this amendment does NOT license

- It does not license moving the **A1 hole itself** (item 4) out of the main text.
- It does not license moving **Section IV-D**, which no registration has ever made movable and
  which the cut order names as never cut.
- It does not license the same move for
  `PREREGISTERED_M5_WITHDRAWAL.md` §4. **That paragraph was not touched.** The
  continuous-operation limitation stays in the article's Section III **word for word**, so no
  amendment to M5-withdrawal is needed and none is written. This is stated here so that a future
  reader does not infer a second amendment from the existence of this one.

## 6. Status at writing

| | |
|---|---|
| Written | 2026-09-13 |
| Author decision | 2026-09-13, chat (Cowork) — "cắt xuống 8 trang, còn bao nhiêu thì đưa vô supplementary" |
| Paragraph state at hashing | **still in `main.tex`, unmoved** |
| Numbers changed by this amendment | **none** |
| Registrations amended | `PREREGISTERED_E12B.md` §2 item 5, **only** |
| Registrations explicitly NOT amended | `PREREGISTERED_M5_WITHDRAWAL.md` §4 (paragraph untouched); E12 §4; E12-b items 1–4, 6, 7 |
