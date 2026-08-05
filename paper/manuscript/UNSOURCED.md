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

## 1. Ecosystem family is a hand classification, not a measured field

**Where:** §4.1 ("all twelve are Hadoop-ecosystem", "no project outside the Hadoop
ecosystem clears it, the best being James at 74.8%"), §1 contribution 2, abstract.

**Status:** the *rates* are measured; the *family* is a judgment. `paper/numbers.md`
§7 records that family "is not even a recorded field", and
`scripts/probe_summary.py` now writes the classification into
`paper/probe_summary.json` so that the judgment is inspectable. Atlas at 78.1% is
the highest-rated dropped project and is classified Hadoop-ecosystem; James at
74.8% is the highest outside it. **If a reader classifies Atlas differently, the
sentence changes.** No independent taxonomy of Apache project families was used.

**Cost to fix:** low. Adopt an external classification (the ASF project
categories, or the Hadoop ecosystem list from a cited source) and re-derive.

## 2. "Flink's 24.1pp gap is scope, not error" is an explanation, not a result

**Where:** §4.4, §2.1.

**Status:** stated as untested in both places, and in `paper/numbers.md` §1b. The
check that would settle it — re-probing Flink's first 12,419 commits to match
SEOSS 33's snapshot — has not been run (`PROJECT_STATE.md` §6, task 16). Until it
is, the reader has our word that the difference is corpus scope rather than a
disagreement between two implementations of the same measure.

**Cost to fix:** low. One clone already on disk, roughly ten minutes.

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

## 9. Mode 4's worked example rests on a 20-commit hand sample

**Where:** §5, taxonomy table row 4.

**Status:** spring-batch cites `BATCH-` in 4,046 of 7,034 commits and in none of
the 20 most recent sampled. The 4,046 is a full scan; the "none of the 20 most
recent" is a hand sample with no confidence interval, and it is the half of the
claim that establishes the convention *changed*.

**Cost to fix:** trivial — a rate computed over the last N commits rather than a
sample of 20. It is exactly the fourth field §5.5 asks sampling frames to expose,
so the paper is recommending a measurement it did not itself make rigorously.

## 10. One identity-namespace difference in the Hadoop analysis is unverified

**Where:** §6.3.

**Status:** the `reviewer_pool` variable reads Jira comment authors by two
different paths in the two arms of the analysis. It is immaterial in practice
because `reviewer_pool` is null everywhere (rho = 0.0010, p = 0.988), but the
paths were never reconciled. Recorded as unverified rather than checked.

**Cost to fix:** trivial, and it changes nothing.

---

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
