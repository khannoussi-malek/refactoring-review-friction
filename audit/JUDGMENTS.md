# Audit — Priority 4: judgment calls presented as findings

---

## 1. The ecosystem classification — the sensitivity analysis examines the wrong project

`paper/manuscript/UNSOURCED.md` §1 identifies the family classification as a hand
judgment and singles out **Atlas** as the exposure: *"Atlas at 78.1% is the
highest-rated dropped project and is classified Hadoop-ecosystem... If a reader
classifies Atlas differently, the sentence changes."*

I extracted the hand-classified set from `scripts/probe_summary.py` (17 projects)
and tested the counterfactual for every plausible member.

| reclassify OUT of "Hadoop-ecosystem" | best rate outside | does anything outside now clear the 0.80 bar? |
|---|---|---|
| **atlas** | atlas 78.1% | **no** |
| hudi / storm / accumulo / parquet-java | james 74.8% | **no** |
| **drill** | drill 84.2% | **YES — drill** |
| **kylin** | kylin 83.9% | **YES — kylin** |
| **sqoop** | sqoop 82.6% | **YES — sqoop** |

**Atlas is the benign case.** Reclassifying it changes a decorative sentence
("the best outside is James at 74.8%" becomes "…is Atlas at 78.1%") and leaves the
load-bearing claim — *no project outside the ecosystem clears the bar* — intact,
because 78.1% < 80%.

**The binding cases are Drill, Kylin and Sqoop**, all of which are *passing*
projects. Reclassifying any one of them out simultaneously falsifies "**all 12 are
Hadoop-ecosystem**" (contribution 2, and a sentence in the abstract) and produces
a non-ecosystem project clearing the bar.

Would a neutral classifier agree with all three?

* **Sqoop** — unambiguous. It is literally *SQL-to-Hadoop*; its entire purpose is
  moving data in and out of Hadoop.
* **Kylin** — solid. An OLAP engine built on Hadoop, Hive and HBase.
* **Drill** — **arguable.** Apache Drill is a schema-free SQL engine modelled on
  Google Dremel that queries HDFS, HBase, MongoDB, S3, Kafka and local files. It
  does **not** require HDFS or YARN. It is commonly listed in "Hadoop ecosystem"
  roundups by association, but architecturally it is deliberately not
  Hadoop-dependent. A reviewer could reasonably place it outside, and if they do,
  the paper's second contribution is false as stated.

**Verdict: the judgment is disclosed but its sensitivity analysis is aimed at the
wrong project.** `UNSOURCED.md` §1 should name Drill, not Atlas, as the case the
claim actually turns on. The word "drill" appears nowhere in `UNSOURCED.md`.

A cheap fix exists and is not taken: adopt an external classification (the ASF
project categories, or the ecosystem list from a cited source) instead of a hand
set defined inside the repository's own analysis script.

---

## 2. The rater contamination — disclosure is adequate; the conclusions should stand

The prior agent disclosed, in `paper/LLM_RATER_PILOT.md` §6.2, that it had read
the human bucket margins (5/5/10 and 1/1/18) **before** rating.

**My assessment: the disclosure is adequate and the pilot's conclusions do not
need to be withdrawn — but for a reason the memo states only weakly.**

The load-bearing output of the pilot is *not* the LLM's labels. It is the pair of
claims:

1. **κ is not computable**, because the human pass kept only margins. This is a
   fact about `codebook_labeling.md`, entirely independent of the rating. I
   verified it against every historical version of the file: A and B are empty in
   all 40 rows, in the only commit that ever touched it. **Contamination cannot
   affect this.**
2. **The attainable κ ceiling on the flagged bucket is 0.491.** This is computed
   from the two margins. The *human* margin is fixed. The *LLM* margin is the
   contaminated quantity — but contamination toward the human's distribution would
   push the ceiling **up**, not down. The reported ceiling is therefore
   conservative against the direction of the bias.

The observed margins also argue against anchoring: the LLM's flagged margin
(3/12/5) is far from the human's (5/5/10), which is not what anchoring to a known
target looks like.

What contamination **could** have affected is the S count (3 vs 5), which feeds
the precision figure of 15%. That figure is reported alongside the human's 25% and
neither is leaned on.

**Verdict: disclosure adequate; no withdrawal warranted.** One sharpening the
memo does not make: it should state that the contamination biases the ceiling
*upward*, so 0.491 is an upper bound on an upper bound.

---

## 3. The rule-ordering diagnosis — the six comments are defensible, but the count lands on the global maximum and this is not disclosed

### 3.1 Do the six genuinely satisfy both rules?

The stated criterion is: *the dominant speech act is one rule 4 names explicitly
(behaviour, tests, naming, bugs, approval) **and** a structural word is present.*

| # | comment | rule 4 trigger | rule 3 trigger | both fire? |
|---:|---|---|---|---|
| 1 | "Good job, very nice **refactor**. Latest patch LGTM, committed to trunk." | approval | "refactor" | **yes, clearly** |
| 3 | "Thanks for the **refactor**. Merged PR 3303 to trunk." | approval / commit notice | "refactor" | yes |
| 12 | "The disk tests are only setting up **structure** to run inline in maven only." | tests | "structure" | yes |
| 17 | "+1 on 001.patch. The **refactoring** is definitely helpful." | approval | "refactoring" | **yes, clearly** |
| 19 | "I have **refactored** OzoneRestClientException to OzoneClientException." | naming | "refactored" | yes |
| 25 | "…none of the above failures are strongly related to my patch as I've been just **moving around code**." | tests | "moving around code" | yes |

All six are defensible. None is a stretch.

### 3.2 But the count is the ceiling-maximising one

Five of the six are in the flagged bucket. I computed the attainable κ ceiling as
a function of how many flagged-bucket comments are moved from I to C:

| moved | LLM flagged margin | κ ceiling |
|---:|---|---:|
| 3 | (3, 9, 8) | +0.692 |
| 4 | (3, 8, 9) | +0.765 |
| **5 (used)** | **(3, 7, 10)** | **+0.840 ← global maximum** |
| 6 | (3, 6, 11) | +0.837 |
| 7 | (3, 5, 12) | +0.833 |
| 8 | (3, 4, 13) | +0.745 |

**The chosen count produces the highest ceiling attainable under any
reclassification.** That is a structural conflict of interest: the criterion was
applied by the same agent that reported the resulting number, and it landed
exactly on the maximum.

Two candidates that were *excluded* would each have lowered it:

* **#4** ("Thanks, I've run the **test** and all ok. For the **refactoring** of
  that method, i'd prefer to do it as a separate PR") — opens with a test report,
  contains a structural word.
* **#13** ("It looks like people is mostly positive about this change… I'd
  appreciate if anybody can do the **refactor**") — approval-adjacent, contains a
  structural word.

Including either gives 6 or 7 moved, and a ceiling of 0.837 or 0.833.

### 3.3 How much does this actually matter?

**Very little to the substance, more to the presentation.** The ceiling is
0.833–0.840 across 5, 6 or 7 moved — the finding ("the rule ordering, not the
raters, decides whether the instrument can pass") is robust to ±2 comments. The
paper's story does not depend on hitting the maximum.

`paper/LLM_RATER_PILOT.md` §8 does disclose that the boundary "is itself a
judgment", names the criterion and lists all six comments — genuinely good
practice, and it is why I could run this test at all.

**What it does not disclose is that the chosen set sits at the global maximum, or
that the two nearest excluded candidates would lower the headline.** A hostile
reviewer will find this in ten minutes, as I did.

**Verdict: the six are defensible; the selection is not tuned in any way I can
demonstrate; but the coincidence with the global maximum is undisclosed and
should be stated, along with the 0.833–0.840 robustness range that defuses it.**

---

## 4. `UNSOURCED.md` completeness — six items it does not list

The list of ten is honest and well-ranked. These are what it misses. None appears
anywhere in the file (checked by keyword: "extrapolat", "Drill", "Spearman",
"p-value", "0.86", "930", "99.7", "snapshot substitution" — all zero hits).

| # | missing item | severity | detail |
|---:|---|---|---|
| A | **The headline rho has no CI and no test** | **high** | "uncorrelated" / "essentially no information" on n=33 with 95% CI [−0.35, +0.34]. `NUMBERS.md` §1.3 |
| B | **The estimator is applied entirely outside its validated range** | **high** | 12 validated at commit-side 82.6–98.3%; 21 applied at 10.5–78.1%; **zero overlap**. `NUMBERS.md` §2.3 |
| C | **The reported validation covers the wrong approximation** | **high** | 0.45pp validates number-capping; end-to-end frozen error is 1.76pp mean / 11.91pp max. `NUMBERS.md` §2.2 |
| D | **Drill, not Atlas, is where the family claim breaks** | medium | §1 above |
| E | **`rho = −0.86` and `930` have no provenance row** | medium | both pass `check_provenance.py` only by substring collision. `NUMBERS.md` §7.2 |
| F | **The Kylin "100%" is 99.72%** | low–medium | self-contradicting with the 2/4,989 numerator in the same sentence |

Two further items are *arguably* in scope for such a list and are absent:

* **The provenance gate cannot detect an unsourced number** (`NUMBERS.md` §7.1).
  `UNSOURCED.md` is presented as the companion to `PROVENANCE_CHECK.md`; that the
  companion's own gate is a substring test against a hand-written file belongs in
  one of the two documents.
* **`26.2%`, `0.33`, `1,035 → 797` and `p = 0.3651` are prose-only** — real
  numbers, but nothing machine-readable on disk reproduces them, so a reader
  cannot re-derive them without re-running deleted pipelines.

---

## 5. What I checked here and found nothing wrong with

* The disputed six are genuinely disputable under the codebook's own two rules; I
  read all forty comments and the codebook's decision rule to check.
* The exclusion of the seven *other* `I`-labelled comments is consistent with the
  stated criterion: comments 2, 9, 10, 15 and 16 are task-splitting, recruitment
  or review requests, none of which rule 4 enumerates.
* The pilot's central claim (κ not computable) is a fact about the repository, not
  a judgment, and it is correct.
* The truncated-history exclusion rule in the rho computation is genuinely
  pre-stated and insensitive across its range (`NUMBERS.md` §1.2). I looked hard
  for tuning here and did not find it.
