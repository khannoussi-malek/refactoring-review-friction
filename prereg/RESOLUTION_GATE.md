# Pre-registered feasibility gate — how violation-symptom comments resolve

**Committed before any comment was drawn.** At the time of this commit no sample
exists: `scripts/gate_sample.py` has not been written, `prereg/gate_sample.json`
and `prereg/gate_labelling.md` do not exist, and no comment body has been read
for the purpose of this gate.

Verify with `git log --diff-filter=A -- prereg/` — every sample and evidence file
must be added in a commit *after* this one, and `scripts/gate_sample.py` must not
exist at this commit. Same check as `predictions/PREDICTIONS.md` `ca076a9`
preceding `48caf14`.

## What this gate decides

RQ1's anchor moved on 07-26 to the **violation-symptom interval**: an
architecture violation symptom raised in code review → a later, *separate*
architectural refactoring of the flagged entity (`paper/ANCHOR_HISTORY.md`).

The design has one load-bearing assumption: **that an interval exists at all.**
If a structural comment is nearly always acted on inside the review that raised
it, there is no waiting period to measure, and the anchor fails the way the tier
rule failed — on measurement, not on argument.

This gate takes 20 comments and asks how each one resolved. It is a feasibility
count, **not a test of the anchor's hypothesis.** No p-value is computed here and
none may be computed from its output (plan §11, R4 exception).

## Corpus and its known limitation

**Hadoop only.** `.jira_cache/` — 323 tickets, Apache Jira REST v2, comment
bodies with ids, authors and `created` timestamps, pulled 2026-07-19 and frozen
(`deposit/MANIFEST-v1.md`). Review discussion reaches Jira through the ASF
`githubbot` relay of GitHub PR threads (`scripts/pr_review_signal.py:5-10`).

Hadoop was chosen because **no network call is permitted** and it is the only
corpus on disk. Two limitations travel with every number this gate produces and
are fixed here so they cannot be discovered afterwards:

1. **No patchset structure.** Gerrit's patchset N → N+1 diff is the natural
   operationalisation of "resolved inside the same review" and does not exist in
   this record. Bucket (a) is approximated against the ticket's own merge commit.
   A Hadoop bucket-(a) count is therefore **not** a Gerrit bucket-(a) count.
2. **The construct is the F2 keyword net, not an external violation-symptom
   scheme.** No external scheme, labelled dataset or detector is present in this
   repository. `codebook.md`'s keyword rule is **≈25% precise** on a 40-comment
   single-rater pass (`codebook_results.md`), so the candidate frame here is a
   recall-first prefilter and roughly fourfold over-inclusive. Recorded now:
   **a bucket-(b) rate measured on this frame is a rate on keyword hits, not on
   validated violation symptoms.**

## Sampling

* **Source:** `.jira_cache/`, all 323 tickets, every comment in each.
* **Candidate filter — both conditions, conjunctively:**
  1. the comment body matches the `codebook.md` keyword net, as implemented in
     `scripts/pr_review_signal.py:32-35` (`STRUCT`), **and**
  2. the comment names at least one **resolvable code entity** — a `.java` path,
     or a `ClassName`, or a `Class#method` form.
* **Excluded before filtering:** bot CI/Yetus reports, per `codebook.md:54`
  decision rule 1, using the `CI` pattern at `scripts/pr_review_signal.py:29-30`,
  and `githubbot` "opened a new pull request" notifications.
* **Random seed: 20260801.** Fixed here, before sampling.
* **Draw:** `random.Random(20260801)`, candidates in sorted `(ticket_key,
  comment_id)` order before the draw, so it is deterministic and re-drawable.
* **n = 20.**

**Extension rule.** If the count in bucket (b) falls **between 2 and 14
inclusive**, the sample is uninformative and extends to **40** under the same
seed, drawn from the same candidate frame. Implied readings, stated now: **≤ 1 in
(b) is a decisive fail**, **≥ 15 in (b) is a decisive pass**, and everything
between is undecided at n=20 rather than a weak answer.

## Buckets

Mutually exclusive. Each case is coded **against the ticket's own merge commit** —
the earliest commit citing the ticket key, from `ticket_first_commit.json`.

| bucket | definition |
|---|---|
| **(a) SAME REVIEW** | the flagged entity changes between the comment timestamp and the ticket's merge commit |
| **(b) LATER SEPARATE** | the flagged entity undergoes an architectural refactoring in a **distinct, later** commit after the merge, within the window. **This is the event the study needs.** Record the interval in days |
| **(c) GONE** | the entity is deleted, or the ticket is abandoned / won't-fix |
| **(d) NOTHING** | no qualifying change within the window |
| **(e) UNCODEABLE** | record the reason. **These leave the denominator** and are reported separately |

"Architectural refactoring" in (b) is the existing repo definition, not a new one:
the type filter in `scripts/filter_architectural.py` — package-level types plus
Move-Class moves whose source and target package differ. **R5 binds: this
definition is not relaxed for this gate.**

## Window

**24 months after the merge commit.**

**Right-censoring — reusing the logic at `scripts/sui/review_value.py:77-91`.**
That code computes `horizon = HORIZON_DAYS * 86400`, excludes any case where
`now - ts < horizon` (`now` = the newest commit timestamp in the corpus), and
counts a later event only where `ts < x <= ts + horizon`. Transposed here with
`HORIZON = 24 months`:

* if **fewer than 24 months of Hadoop history remain** after the merge commit —
  i.e. `now - merge_ts < horizon`, where `now` is Hadoop's HEAD commit date — the
  case is **censored by observation** and goes to **(e)**;
* if the 24-month window **falls outside the commit coverage of
  `refminer_all.json`**, the case is **censored by observation** and goes to
  **(e)**.

The second clause is not optional bookkeeping. `refminer_all.json` covers **8,919
commits** and the `hadoop/` clone holds **28,290**, so a window can sit entirely
inside real history and entirely outside detector coverage. A case where the
detector never looked is **not** evidence of (d). Every case carries a coverage
flag (`scripts/gate_evidence.py`, Step 5) and an uncovered window may **never**
be coded (d).

## Decision rule — stated as an event count, not a proportion

The eventual model is a Cox regression carrying **five controls**: discussion
volume, churn, component age, module size, contributor experience. At the
conventional ten events per covariate that is **≈ 50 events** required.

Discussion volume is named here, before any outcome is seen, and that is
deliberate: it entered the 07-19 F2 analysis *after* the effect was reported and
became the finding that retracted it (`results_dossier.md` §10). It is a
pre-committed control this time, not a robustness check.

**The arithmetic:**

```
expected events  =  observed bucket-(b) rate  ×  eligible violation-symptom population
                 =  r  ×  P
required         =  50
```

**`r` — the observed bucket-(b) rate.** Fixed now as

```
r  =  n_b / (n_coded)        where  n_coded = n_sampled − n_e
```

i.e. bucket (e) leaves the denominator, per the bucket table. At n=20 with no
uncodeable cases the denominator is 20; with 5 uncodeable it is 15.

**`P` — the eligible violation-symptom population.** Fixed now as **the count of
candidate comments emitted by the filter above**, written to
`prereg/gate_sample.json` as `n_candidates` by `scripts/gate_sample.py`. Its
value is not known at this commit and is not guessed here; its **source and
definition are fixed**, which is what pre-registration requires.

Two bounds on `P` from already-committed figures, so the rule is not open-ended:

* **Ceiling: 1,810.** `codebook_results.md:37` gives ~1,810 substantive comments
  across the 323 tickets. The candidate filter is strictly narrower than
  "substantive", so `P ≤ 1810`.
* **Ceiling on the ticket frame: 323** tickets (`.jira_cache/`, and 323 keys in
  `review_signal_all.json`); 345 traceable episodes, 349 total
  (`architectural_episodes_all.json`). Only relevant if the gate is later
  re-expressed per ticket rather than per comment; **it is not, the unit is the
  comment**, matching `codebook.md:14-16`.

**What clears 50 events and what does not**, written down before any result:

| if `P` is | `r` clears 50 events at | `r` fails at |
|---:|---|---|
| 1,810 (the ceiling) | **≥ 2.8%** | < 2.8% |
| 1,000 | **≥ 5.0%** | < 5.0% |
| 500 | **≥ 10.0%** | < 10.0% |
| 300 | **≥ 16.7%** | < 16.7% |
| 200 | **≥ 25.0%** | < 25.0% |
| 100 | **≥ 50.0%** | < 50.0% |

Read as: **the gate clears if `r × P ≥ 50` using the measured `P` from
`gate_sample.json` and the measured `r` from the completed labelling sheet.** At
n=20 the finest resolution `r` can have is 5 percentage points, so a `P` below
~200 cannot be settled by this gate at all and would itself be a feasibility
finding.

**A Hadoop `P` is not the study's `P`.** The real study's eligible population is
violation-symptom comments in the target corpus (OpenStack, and Qt if it were
viable). That figure is **NOT COMPUTABLE** from local data: no OpenStack or Qt
data of any kind is on disk, neither was among the 38 projects probed
(`paper/traceability_probe.json`), and `paper/RM_LANGUAGE_SUPPORT.md` establishes
that RefactoringMiner 3.1.4 as built here cannot detect refactorings in C or C++
at all, so **Qt is not a viable corpus for the refactoring-detected leg
regardless of its population.** The Hadoop `P` is a feasibility proxy and is
reported as one.

## Anti-hindsight commitments

Mirroring `predictions/PREDICTIONS.md`.

1. **The seed will not be changed.** 20260801 is fixed above. If the draw looks
   unhelpful, that is a result, not a parameter to re-roll.
2. **The window will not be extended after seeing results.** 24 months is fixed.
   If bucket (b) is thin at 24 months and would fill at 36, that is a finding
   about the interval's length and is reported as one.
3. **Bucket definitions will not be revised mid-coding.** The five buckets above
   are final. A case that fits none goes to (e) with its reason recorded, and (e)
   is reported rather than absorbed.
4. **The candidate filter will not be loosened to raise `P`.** Keyword net plus
   named entity, both required. If too few comments name a resolvable entity,
   that is the feasibility finding — a structural comment with no named entity
   cannot enter this design at all.
5. **The extension rule fires on the count, not on judgement.** 2–14 in bucket
   (b) extends to 40 under seed 20260801, whatever the distribution looks like.
6. **The 50-event requirement will not be renegotiated downward** by dropping
   controls after seeing `r`. The five controls are named above.
7. **No bucket is assigned by tooling.** R6 binds: `scripts/gate_sample.py` and
   `scripts/gate_evidence.py` prepare inputs; a human coder assigns every bucket.
   A single-rater pass produces a feasibility count, **never a claim**
   (`README.md` §8).

## What each outcome means

* **`r × P` ≥ 50** — the interval exists in usable quantity on Hadoop, and the
  anchor survives its first gate. It does **not** establish the anchor; it
  establishes that the event is countable.
* **`r × P` < 50** — the anchor cannot power the model it needs on a corpus of
  this shape, and RQ1 moves for a fifth time.
* **Bucket (a) dominant** — symptoms are absorbed inside their own review. This
  is the specific failure the gate was built to detect.
* **Bucket (e) large** — the *record*, not the phenomenon, is the binding
  constraint, which is the finding the methods paper already argues
  (`paper/table2_visibility.md`). Reported separately from (a)–(d) for exactly
  this reason.
