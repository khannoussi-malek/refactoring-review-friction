# Preliminary Study Summary — Architectural Refactoring Friction in Apache Hadoop

*Proposal-ready synthesis. All figures are exact results; see [results_dossier.md](results_dossier.md)
for full detail, [SLICE_LOG.md](SLICE_LOG.md) for method, and `figures/arch_vs_ordinary.png` for the
headline chart.*

## 1. Motivation and research question

Large systems accumulate architectural debt, and the refactorings that repay it are believed to be
costlier and more contentious than routine changes — but this is rarely quantified against real
project outcomes. **RQ1 asks whether architectural refactorings carry measurably more development
friction than ordinary changes, and what that friction looks like in issue-tracker and review data.**

The pilot first tested — and rejected — the assumption that *effort estimates* could serve as the
friction signal (they are absent in Apache), then measured friction directly from review discussion
and issue-tracker state transitions.

## 2. Method (reproducible pipeline)

- **Corpus:** 8,919 commits across four Hadoop release ranges (v3.1.0 → v3.4.3).
- **Detection:** RefactoringMiner, parallelized 8–16× with a self-healing runner that auto-skips
  commits it hangs on. 90–99% coverage. Output: 51,861 refactorings → **349 architectural episodes**.
- **Control group:** 400 *ordinary* refactoring tickets (commits with non-architectural refactorings)
  for the primary comparison.
- **Signals from Apache Jira (public API):** review discussion (via the githubbot PR relay), ticket
  dates, and the full **status changelog** (Open → In Progress → Patch Available → Resolved), which
  lets us separate *waiting/triage time* from active work — independent of comment volume.

## 3. Feasibility results

n = 345 traceable episodes (of 349): **traceability 99%** (with all monorepo subproject keys —
HADOOP/HDFS/YARN/MAPREDUCE/HDDS/Ozone/Submarine; a single-key probe misreads it as 26%). **Effort
estimates: 0%** — absent in Apache, which rules out the estimate-based framing for this corpus.

## 4. Primary finding — architectural refactorings are a distinct, higher-friction class

Comparing **323 architectural** vs **400 ordinary** refactoring tickets (medians; Mann–Whitney):

| Measure | Architectural | Ordinary | p |
|---|---|---|---|
| Review discussion (comments) | 14 | 11 | **0.0004** |
| **Triage latency** (days in "Open" before pickup) | **4.6** | **2.1** | **0.0016** |
| Resolution time (days) | 30.2 | 15.5 | **0.0003** |
| Distinct participants | 3 | 3 | 0.18 (n.s.) |

*(Chart: `figures/arch_vs_ordinary.png`.)*

**Architectural refactorings draw more review discussion, wait ~2× longer to be picked up, and take
~2× longer to resolve — while engaging the same small core of maintainers.** It is more back-and-forth
among the same people, not broader participation.

**The cleanest evidence is triage latency** — days a ticket sits in "Open" before anyone starts it.
This happens *before* any discussion, so it cannot be an artifact of discussion volume (the confound
that undermines the resolution-time comparison). Architectural work is measurably **harder to take
on**: ~2× longer before a maintainer commits to it. This is the load-bearing result.

## 5. A within-episode signal we tested and retracted (methodological rigor)

We also asked whether, *among* architectural episodes, those with more *structural* review discussion
resolve slower. An apparent effect (3× slower; Cox HR 0.69, p=0.003, robust to change size)
**did not survive controlling for discussion volume** (HR 1.10, p=0.51); discussion volume alone
predicts resolution time (HR 0.70/log-comment, p≈1e-9), and structural *density* is null (p=0.26).
The keyword signal (≥3 structural mentions) is entangled with "how much was said," so it cannot
separate structural content from discussion quantity. Reported deliberately: detecting and retracting
a spurious result before publishing it is part of the contribution.

## 6. Threats to validity

Descriptive/associational, not causal. The architectural vs. ordinary comparison is not matched on
module, priority, or time period (a full study would match or adjust). Effect sizes are modest though
consistent and significant. Resolution-time differences partly reflect discussion volume — hence the
emphasis on triage latency, which does not. One project, one release-line window. The structural
review signal is a 25%-precise heuristic, not yet dual-rated (κ).

## 7. Methodological contributions

A scalable, fault-tolerant refactoring-mining pipeline; recovery of full PR review discussion from
Jira via bot-relay (no GitHub credentials); a monorepo-aware traceability probe; and a status-changelog
method that separates waiting from active work. These lower the cost of scaling the study.

## 8. Proposed full study

(a) Match/adjust the architectural vs. ordinary comparison on module, priority, contributor, and time.
(b) Validate a volume-independent structural signal (dual-rater codebook, κ) and re-test whether
*structural* content adds friction beyond discussion volume. (c) Model triage/startup latency directly
(survival analysis with covariates and clustering). (d) Replicate on Kafka/HBase/Camel. (e) Use the
public Jira dump (Zenodo 15719919) for complete changelog history at scale.

## 9. Significance

The pilot establishes, on real data, that **architectural refactoring is an empirically distinct,
higher-friction class of change** — more reviewed, slower to start, slower to finish than routine
work — with startup/triage latency as clean, volume-independent evidence. It also delivers two
supporting results (estimates absent; issue-tracker friction largely inseparable from discussion
volume) and a reproducible pipeline. Together these motivate and de-risk a full study of what drives
architectural-change friction, with tooling and preliminary evidence already in hand.
