# Claims in the manuscript that are not fully sourced

Compiled 2026-08-05, as the companion to `PROVENANCE_CHECK.md`. That file checks
**numbers**: every distinctive numeric token in the manuscript resolves to a
section of `paper/numbers.md` naming a script and a commit. This file checks the
other direction — **claims whose support is weaker than the number attached to
them**, or which have no number at all.

Nothing here is hidden elsewhere in the paper. Each item names the section that
carries the claim and what the paper already says about it. The purpose is to make
the list enumerable rather than distributed.

Ordered by how much a reviewer is likely to press on it.

---

## 1. Ecosystem family is a hand classification, and Drill is where it breaks

**Where:** §4.1, §1 contribution 2, abstract.

**Status:** the *rates* are measured; the *family* is a judgment.
`scripts/probe_summary.py` writes the classification into
`paper/probe_summary.json` so it is inspectable, and §4.1 now reports two
measured variables tested in its place — repository start year (AUC 0.611,
p = 0.279) and Apache Incubator graduation date (AUC 0.289, p = 0.098, and
missing for four of the twelve passing projects). **Neither separates the corpus
as well as the hand label (accuracy 0.868), so the judgment is kept and marked.**

**The sensitivity is on Drill, not Atlas.** An earlier version of this list named
Atlas as the exposure. That was wrong in the direction that matters: Atlas is the
highest-rated *dropped* project at 78.1%, and reclassifying it changes only which
project is "best outside the ecosystem" — the load-bearing claim survives, because
78.1% < 80%. The claim actually breaks on three *passing* projects:

| reclassify out of "Hadoop-ecosystem" | best rate outside | anything outside now clears the bar? |
|---|---|---|
| Atlas | Atlas 78.1% | **no** |
| Accumulo / Hudi / Storm / Parquet | James 74.8% | **no** |
| **Drill** | Drill 84.2% | **YES** |
| **Kylin** | Kylin 83.9% | **YES** |
| **Sqoop** | Sqoop 82.6% | **YES** |

Sqoop is unambiguous (it is literally *SQL-to-Hadoop*) and Kylin is solid (an OLAP
engine on Hadoop, Hive and HBase). **Drill is genuinely arguable**: it is a
schema-free SQL engine modelled on Google Dremel that queries HDFS, HBase,
MongoDB, S3, Kafka and local files, and it requires neither HDFS nor YARN. A
reviewer who places Drill outside the ecosystem falsifies the "all twelve" form of
contribution 2.

**Cost to fix:** low, and not taken. Adopting an external classification — ASF
project categories, or an ecosystem list from a cited source — would remove the
judgment. We report the exposure instead.

## 2. "Flink's 24.1pp gap is scope, not error" — CLOSED 2026-08-05

**Where:** §4.4, §2.1.

**Status: resolved, and the item is closed.** The check was run
(`scripts/flink_truncation.py`). Restricting the probe to the earliest 12,419
commits — SEOSS's own change-set count — gives **5,214 / 12,419 = 41.9841%**
against their **41.98%**, a gap of **+0.0041pp**. Flink is also not truncated:
its pinned branch begins at the repository's first commit. The paper now says
five of five overlapping projects agree once scope is matched, and §4.4 explains
why an exact match on a deterministic count is expected rather than suspicious.

**Kept on this list rather than deleted** so the record shows an open item was
closed by measurement, not by dropping the claim.

## 3. The frozen tracker snapshot has no recoverable date

**Where:** §3.1.3, §4.3, §6.1.

**Status:** the extension's denominators come from the Public Jira Dataset, and
the parsed artifact (`estimates_by_org.json`) carries per-project issue *counts*
without a per-project extraction date. That is why membership is defined in
issue-number space rather than by creation date. The equivalence between the two
holds only up to issues moved between projects, and the size of that discrepancy
is measured on the twelve projects where an exact rate exists — it is not measured
for the other 26.

**Cost to fix:** medium. Re-parsing the deposit for a max-creation-date per
project would date the snapshot exactly. The deposit is 5.81 GB and is not on
disk.

## 4. Vieira et al. (PROMISE'19) is characterised as unverified

**Where:** §2.1.

**Status:** ACM DL, ResearchGate and figshare all returned HTTP 403 to
unauthenticated fetches, so neither the paper body nor the replication package
manifest could be read. The paper is therefore **not** claimed to lack per-project
linkage rates; it is recorded as unchecked. If it does report them, §2.2's novelty
list needs re-examining against it.

**Cost to fix:** trivial with institutional library access. Not available here.

## 5. "RefactoringMiner's TypeScript support has no independent validation in the literature"

**Where:** §3.4, §6.7, §2.5.

**Status:** a negative claim resting on a literature search that found nothing,
which is not the same as establishing there is nothing. The positive facts around
it are sourced — support completed 2026-05-24, one defect traced and filed
upstream as issue #1124, 160 false positives in a single commit.

**Cost to fix:** none available. A negative literature claim cannot be closed, only
weakened; the sentence is already hedged to "we found none".

## 6. The Apache commit-message cell of Table 2 is empty

**Where:** §4.5, §6.7.

**Status:** stated as a gap in this study rather than a property of Apache. The
Hadoop architectural corpus was built by AST-level detection and never compared
against message text, so no recall figure comparable to the TypeScript column's
3.1% exists. It is computable from artifacts already on disk.

**Cost to fix:** medium, and it is the most obvious extension of the paper.

## 7. The published project count of the public Jira dataset is not reproducible

**Where:** §6.8.

**Status:** 1,822 published, 1,276 by final-state keys, 2,506 by the dataset's own
name-union method. 326 project ids carry more than one name and 0 keys do, which
explains part of the overshoot and not all of it. The standing rule is that the
three figures travel together and 1,822 is never quoted beside a per-project
number. A query to the dataset's authors is drafted and **unsent**
(`docs/DRAFT_dataset_authors_query.md`).

**Cost to fix:** out of our hands. It needs an answer from the dataset authors.

## 8. The ICC that decides feasibility is unmeasured

**Where:** §7.4, §6.7.

**Status:** the P/ICC ceiling is arithmetic and sourced; the ICC itself is not
estimated, and was deliberately **not** estimated from the four clusters available
because between-cluster variance has 3 degrees of freedom at n=4 and cannot
resolve 0.015 from 0.02. The paper states the ceiling conditionally on an ICC
value it does not have.

**Cost to fix:** requires the pooled study this paper argues cannot currently be
assembled. That circularity is the point of §7.4 and is not concealed.

## 9. Mode 4's worked example rested on a 20-commit hand sample

**Where:** §5, taxonomy table row 4.

**Status:** **fixed in this revision, and the result is stronger than the sample
suggested.** `scripts/springbatch_recency.py` scans spring-batch's whole default
branch: `BATCH-` appears in **45.6% of 7,035 commits** overall, in **0 of the most
recent 1,000** (back to 2021-06), and at exactly **0% in every year from 2020
onward**; the last year the convention was used at all is **2019**. The convention
did not decay — it stopped.

**One figure did not reproduce and is recorded as a correction.** The published
"4,046 of 7,034" is not reproducible: scanning the default branch gives
**3,210/7,020** for `BATCH-` alone and **3,263/7,020** including `BATCHADM`, and
scanning all refs gives 3,494 and 3,547. None of five readings reaches 4,046. See
`paper/numbers.md` §10e.

## 10. One identity-namespace difference in the Hadoop analysis is unverified

**Where:** §6.3.

**Status:** the `reviewer_pool` variable reads Jira comment authors by two
different paths in the two arms of the analysis. It is immaterial in practice
because `reviewer_pool` is null everywhere (rho = 0.0010, p = 0.988), but the
paths were never reconciled. Recorded as unverified rather than checked.

**Cost to fix:** trivial, and it changes nothing.

---

## 11. The headline association has no confidence interval in earlier drafts

**Where:** §4.3, §1, abstract — as they stood before this revision.

**Status:** **fixed in this revision, listed because the fix is a claim change.**
Earlier drafts said the two rates are "uncorrelated" and that the commit-side rate
"carries essentially no information", on n = 33 with a 95% CI of [−0.35, +0.34]
and no interval, p-value or power statement anywhere. At 80% power this study
detects only |rho| ≥ 0.47. The claim is now "a strong positive association is
ruled out; a null is not established".

## 12. The estimator's reported validation covered a different approximation

**Where:** §4.3, §6.1, Table 3 caption — as they stood before this revision.

**Status:** **fixed in this revision.** The 0.45pp / 2.14pp figure validates
number-capping; Table 3 also substitutes a frozen snapshot, and the end-to-end
error is 1.76pp mean / 11.91pp max. The favourable version (11 of 12 within
2.93pp) existed in the data and was not reported.

## 13. The estimator is applied entirely outside its validated range

**Where:** §4.3, §6.1, Table 3 caption.

**Status:** **now stated, not fixed** — it cannot be fixed without a live Jira
fetch, which the repository's standing rule forbids. Validated at commit-side
82.6–98.3%, applied at 10.5–78.1%, **0 of 21** applied projects inside the
validated range.

## 14. Two manuscript numbers had no provenance row at all

**Where:** `rho = −0.86` (§1) and `930` (§6.4).

**Status:** **fixed in this revision.** Both passed the old provenance checker
only by substring collision — `0.86` against an unrelated `0.86232`, and `930`
against the commit hash `93056ae`. Rows added at `paper/numbers.md` §10d; the
checker was rebuilt so that a numeric match without a `numbers.md` row now
fails.

## 15. The live and frozen measurements disagree in sign

**Where:** §4.3, `paper/DIRECTION_TENSION.md`.

**Status:** **open, and deliberately unresolved.** Spearman(CSR, TRR) is +0.518
on the twelve measured live and exactly, and −0.010 on the 33 measured with the
frozen estimator. The intervals overlap and neither is significant, so they are
not formally contradictory — but the paper's headline sentence cannot be written
from both, and the author has not chosen.

## 16. The kappa ceiling lands on a global maximum

**Where:** `paper/LLM_RATER_PILOT.md` §4.1, §6.5.

**Status:** **now disclosed.** Reclassifying five flagged-bucket comments gives
the highest attainable ceiling of any count (0.840; four gives 0.765, six 0.837,
seven 0.833). The six comments are individually defensible and the result is
robust across ±2, but the coincidence was undisclosed.

## Not on this list, and why

**The six killed hypotheses.** They are not claims of this paper; they appear once
in §1 as motivation, each with its named cause, and are documented in full in the
replication package.

**The 25% codebook precision and the TypeScript 30%/3.1% figures.** These are
single-rater instrument results, and the paper reports them **as findings about
those instruments** rather than as instruments any claim rests on (§6.5). They are
weakly supported by design and saying so is the claim.

**The matcher's 97.5% precision.** Single rater, but a mechanical determination
against a rule fixed before labelling, with the sample and every label committed.
The argument for why that is admissible where coded judgment is not is made in
§6.5 rather than assumed.
