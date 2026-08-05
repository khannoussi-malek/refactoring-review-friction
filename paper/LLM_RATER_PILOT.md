# LLM-as-second-rater pilot on the F2 codebook

**This is not a second rater. It does not unblock the codebook, it does not
substitute for a human, and no claim in this repository may cite it as
validation.** `README.md` §8 says inter-rater agreement cannot be computed alone;
that is still true after this pilot, and for a reason the pilot discovered rather
than the one §8 assumed.

Run 2026-08-05. Labels: `paper/llm_rater_labels.json`. Arithmetic:
`scripts/llm_rater_pilot.py` (`7cc485b`), output `paper/llm_rater_pilot.json`.

```
python3 scripts/llm_rater_pilot.py --labels paper/llm_rater_labels.json
```

---

## 1. What was asked, and the blocker found on the way

The task was: rate the 40 comments in `codebook_labeling.md` with `codebook.md`
as the instrument, compute Cohen's κ against the existing human labels, and
analyse the disagreements.

**The existing human labels do not exist at the item level.** Columns `A` and `B`
in `codebook_labeling.md` are empty for all 40 rows. `codebook_results.md`
(`de657c3`) records only two 3-cell margins:

| bucket | S | I | C |
|---|---:|---:|---:|
| comments the keyword filter **flagged** (rows 1–20) | 5 | 5 | 10 |
| comments it **missed** (rows 21–40) | 1 | 1 | 18 |

κ needs paired labels — which comment got which code from which rater. Margins
cannot supply that, and nothing a second rater does now recovers a first pass
that was never written down. **κ is not computable from what exists**, and this
is a defect in the repository's own evidence chain, not a limitation of the
method.

The single-rater constraint in §8 was recorded as *"no second rater is
available"*. It should also read *"the first rater's per-item labels were not
retained"*, because that is the binding failure here and it is cheaper to fix:
retaining item-level labels costs nothing and would have made this pilot
answerable.

## 2. What is computable instead — the bounds κ must lie within

Cohen's expected-agreement term depends only on the margins, which *are*
recorded. So while κ itself is unavailable, the interval it must fall in is
determined:

```
Pe     = Σ_k p1_k · p2_k                    (fixed by the two margins)
Po_max = Σ_k min(p1_k, p2_k)                (the most agreeable pairing)
Po_min = max(0, max_k (p1_k + p2_k − 1))    (the least agreeable pairing)
```

`Po_min` is the diagonal mass no pairing can avoid: row *k* holds `p1_k` and the
columns other than *k* hold only `1 − p2_k` of capacity, so `p1_k + p2_k − 1` is
forced onto the diagonal. Both endpoints are attainable, so the interval is
tight, not conservative.

## 3. Result

| bucket | human | LLM | Pe | **κ must lie in** |
|---|---|---|---:|---|
| flagged (n=20) | 5 / 5 / 10 | **3 / 12 / 5** | 0.3125 | **[−0.455, +0.491]** |
| unflagged (n=20) | 1 / 1 / 18 | **2 / 1 / 17** | 0.7725 | [−0.099, +0.780] |
| pooled (n=40) | 6 / 6 / 28 | **5 / 13 / 22** | 0.4525 | **[−0.370, +0.680]** |

Read the flagged row first, because it is the bucket the codebook exists to
adjudicate — the comments the keyword rule fires on.

> **Even under the pairing most favourable to agreement, κ on the flagged bucket
> cannot exceed 0.491.** No assignment of the human's 5/5/10 to specific comments
> reaches the 0.80 conventionally required, or the 0.60 usually treated as a
> floor. The recorded evidence is not merely silent about agreement; it excludes
> acceptable agreement.

The unflagged bucket looks better (κ ≤ 0.780) and means less: both raters put
17–18 of 20 comments in one category, so Pe is 0.77 and κ is measuring almost
nothing. That is the standard high-prevalence κ artefact and it is why the
flagged bucket is the one to quote.

## 4. Where the divergence is, and it is the instrument

The S margin agrees closely — 5 against 6 pooled, 3 against 5 on the flagged
bucket. **The entire gap is between I and C**, and it is one rule.

`codebook.md`'s decision rule is applied *in order*:

> 3. Does a structural *word* appear only as a fact, a trivial edit, or a
>    different meaning? → **INCIDENTAL**
> 4. Otherwise it's review about behaviour/tests/naming/approval →
>    **STYLE / CORRECTNESS**

Both fire on a comment that is an approval, a test remark or a naming report
*and* contains a structural word. Six of the 40 are exactly that:

| # | comment, abridged | why both rules fire |
|---:|---|---|
| 1 | "Good job, very nice **refactor**. Latest patch LGTM, committed to trunk." | approval + structural word |
| 3 | "Thanks for the **refactor**. Merged PR 3303 to trunk." | commit notice + structural word |
| 12 | "The disk tests are only setting up **structure** to run inline in maven only." | about how tests are run |
| 17 | "+1 on 001.patch. The **refactoring** is definitely helpful for future development." | approval + structural word |
| 19 | "I have **refactored** OzoneRestClientException to OzoneClientException." | a naming report |
| 25 | "none of the above failures are strongly related to my patch as I've been just **moving around code**." | explains test failures |

Ordering makes rule 3 win, so this rater coded all six **I**. The codebook's own
worked examples for INCIDENTAL are all keyword *collisions* — "too big" meaning a
thread count, "refactored" meaning import order — which reads as an author who
intended I for collisions and C for approvals, and never noticed that the ordered
rule sends approvals to I as well.

**Re-labelling only those six under the opposite order:**

| bucket | LLM, rule 3 first | LLM, rule 4 first | κ bound, rule 3 first | κ bound, rule 4 first |
|---|---|---|---|---|
| flagged | 3 / 12 / 5 | 3 / 7 / **10** | [−0.455, **+0.491**] | [−0.600, **+0.840**] |
| pooled | 5 / 13 / 22 | 5 / 7 / **28** | [−0.370, **+0.680**] | [−0.290, **+0.946**] |

Under the opposite reading the C margin matches the human pass *exactly* in both
buckets — 10 and 28 — and the attainable κ ceiling moves from "cannot reach
acceptable" to "could be near-perfect". **Six comments out of forty, decided by
the order of two rules that were never disambiguated, control whether this
instrument can pass.**

That is the substantive finding of this pilot. It is not "the model disagrees
with the human". It is that the codebook does not determine a label for a
recognisable class of comment, and any κ computed on it would be measuring the
raters' private tie-breaks.

## 5. The keyword rule, measured twice

`README.md` and `paper/numbers.md` §9g quote the keyword rule as ≈25% precise on
a single-rater pass. This is the second measurement of the same quantity:

| | human pass | this pass |
|---|---:|---:|
| precision — flagged comments that are genuinely STRUCTURAL | **25%** (5/20) | **15%** (3/20) |
| recall — structural comments the filter catches | **83%** (5 of 6) | **60%** (3 of 5) |

Both agree on the direction and the magnitude of the problem: the keyword rule
over-counts structural review by roughly four to six times. **The published
"over-counts ~4×" claim survives this pass and is not weakened by it.** Precision
differs by 2 comments and recall by a denominator of 5 or 6, which is noise at
this sample size; neither figure should be quoted to more precision than "under a
third, and probably nearer a sixth".

## 6. What this pilot is, stated so it cannot be mis-cited

**It is a measurement of whether an LLM can operate this instrument.** The answer
is: it can produce a label and a written rationale for every comment
(`paper/llm_rater_labels.json` carries both), and where the instrument is
determinate the two passes land in the same place. Where the instrument is
indeterminate the model exposes the indeterminacy rather than silently absorbing
it, which is useful — but exposing it is not resolving it.

**It is not validation of the codebook.** Nothing here licenses replacing
`f2_structural_review = struct_hits > 0` with a coded judgment, and F2 remains
what `codebook_results.md` made it: an operational 31% with the keyword count
flagged as a ~4× inflated upper bound.

**It is not a second human rater**, for four reasons that hold regardless of how
good the model is:

1. **Non-independence.** The rater had read `codebook.md`, `README.md`,
   `results_dossier.md` and this repository's framing before labelling. A human
   second rater is normally given the instrument and the data and nothing else.
2. **Contamination, disclosed.** The rater had also seen the human bucket margins
   (5/5/10 and 1/1/18) in `codebook_results.md` *before* rating, while
   establishing that item-level labels did not exist. There were no item labels
   to be blind to, but knowing the target distribution is a real contamination
   and the resulting margins must be read with it in mind. The rater's margins
   diverge sharply from the ones it had seen, which is weak evidence against
   anchoring — weak, not absent, and not a substitute for having been blind.
3. **One pass, no reliability of its own.** The model was not run twice, so its
   *intra*-rater consistency is unmeasured. A rater whose own reliability is
   unknown cannot establish anyone else's.
4. **κ against a model is not κ.** Cohen's κ assumes two raters drawing on a
   shared construct. A model's errors are correlated with the text in ways a
   second human's are not, so even a computable κ here would not carry the
   inference the statistic is used for.

## 7. What would actually unblock this

In order of cost:

1. **Retain item-level labels.** Free, and the reason this pilot could not do
   what it was asked. `paper/llm_rater_labels.json` now carries 40 labels with
   rationales, so a human second rater can produce κ against *this* pass
   immediately — which is a measurement of human-model agreement, not of the
   codebook.
2. **Disambiguate rules 3 and 4.** One sentence: *an approval, a test remark or a
   naming report is STYLE/CORRECTNESS even when it contains a structural word;
   INCIDENTAL is reserved for a structural word used in a different sense.* Six
   of forty comments change, and the attainable κ ceiling moves from 0.49 to
   0.84 on the bucket that matters.
3. **A human second rater on the amended codebook**, 40 comments, one sitting.
   That is what §8 asks for and it is still what is needed.

## 8. Threats

**n = 40, 20 per bucket.** Every proportion here has a confidence interval wider
than the differences discussed. The S counts are 3–6 out of 20; one comment moves
precision by 5pp.

**The bounds are exact but wide.** [−0.370, +0.680] pooled is not a κ estimate
and must never be quoted as one. Its only load-bearing use is the upper endpoint:
what the recorded evidence *cannot* reach.

**Single rater on this side too.** These 40 labels are one model's single pass,
committed so they are auditable rather than agreed — the same standard argued for
`paper/matcher_validation.md`, and with the same limit: auditability is not
agreement.

**The disputed-set boundary is itself a judgment.** Which six comments count as
"both rules fire" was decided by this rater, using a stated criterion (the
dominant speech act is one rule 4 names explicitly, and a structural word is
present). A different reader might draw that line at four comments or at nine.
The criterion is written down and the six are named above so the line can be
argued with.
