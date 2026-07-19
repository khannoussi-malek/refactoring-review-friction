# Preliminary Study Summary — Architectural Refactoring and Review Friction in Apache Hadoop

*Proposal-ready synthesis. All figures are exact results from this study; see
[research_prospectus.md](research_prospectus.md) and [SLICE_LOG.md](SLICE_LOG.md) for method and
[worksheet.md](worksheet.md) for the manual trace.*

## 1. Motivation and research question

Large software systems accumulate architectural debt, and the refactorings that address it are
widely believed to be costlier and more contentious than routine changes — yet this is rarely
quantified against real project outcomes. **RQ1 asks whether architectural refactorings that attract
structural design discussion during review are associated with greater development effort**, measured
through issue-tracker outcomes.

The original formulation assumed *developer effort estimates* on issue tickets as the effort signal.
A first empirical check invalidated this assumption and motivated a reframing (§3), which is itself a
finding: the study now centers on **review discussion about code structure** as the signal, with
**ticket resolution time** as the effort/friction proxy.

## 2. Method (reproducible pipeline)

I built and ran an end-to-end mining pipeline on Apache Hadoop:

- **Corpus:** 8,919 commits across four release ranges (v3.1.0 → v3.4.3).
- **Refactoring detection:** RefactoringMiner, parallelized 8–16× across cores with a custom
  self-healing runner that detects and skips commits on which the tool hangs (minified-JavaScript
  dependency bumps), achieving 90–99% commit coverage per range. Output: **51,861 refactorings**.
- **Architectural episode identification:** package-level and cross-package structural refactorings
  (Move/Rename/Split/Merge Package, Move Class across packages, Extract Class/Interface/Superclass),
  yielding **349 candidate architectural episodes**.
- **Signal mining:** issue-ticket review discussion retrieved from the public Apache Jira API. A key
  enabler is that Apache's `githubbot` mirrors the entire GitHub pull-request review — including
  inline code-review comments — into the Jira ticket, so review discussion is recoverable without
  GitHub API credentials.
- **Analysis:** Kaplan–Meier survival estimation and log-rank testing on time-to-resolution, followed
  by a Cox proportional-hazards model with change-size covariates.

## 3. Feasibility findings (n = 345 traceable episodes)

| Filter | Question | Result |
|---|---|---|
| **Traceability** | Does the commit cite a Jira ticket? | **99%** (345/349) |
| **Effort estimate** | Does the ticket record an estimate? | **0%** (0/345) |
| **Structural review** | Does the review discussion argue about structure? | **~31%** (operational) |

Three empirical results emerged:

1. **The estimate-based framing is not viable on Apache data.** No architectural-episode ticket
   records an effort estimate; the field is unused by the project's process. This is a corpus property
   that scaling cannot fix and redirects the research away from estimate-based signals for open-source
   subjects.
2. **A structural-review signal exists and is minable.** Structural review discussion is present in
   roughly 31% of episodes. This is a deliberately conservative operationalization: a first-pass
   codebook calibration found that a naive structural-keyword heuristic is only **25% precise** (most
   keyword matches are approvals or task-planning, not design arguments), so the naive 62% rate is
   treated as an inflated upper bound.
3. **Traceability is excellent but requires care.** Hadoop cites an issue key in 92.3% of commits —
   but only when all monorepo subproject keys (HADOOP/HDFS/YARN/MAPREDUCE and the later-separated
   HDDS/Ozone/Submarine) are matched; a single-key probe misleadingly reports 26%. A practical
   measurement lesson for monorepo corpora.

## 4. Preliminary result (the core contribution)

Splitting the 345 episodes by whether their review discussion is structural:

| Group | n | Median time-to-resolve | Median review size |
|---|---|---|---|
| **Structural review** | 106 | **67 days** | 30 comments |
| Other | 239 | **23 days** | 10 comments |

- **Kaplan–Meier / log-rank test: p = 0.0001** — the two groups' resolution-time distributions differ
  significantly.
- **Cox proportional-hazards model controlling for change size** (log refactoring count, files
  touched, and code churn): the structural-review hazard ratio is **0.66 unadjusted → 0.69 adjusted
  (p = 0.003)**. The effect is essentially unchanged after controlling for size.

**Interpretation:** architectural refactorings that trigger structural review discussion resolve
roughly three times more slowly, and this is **not** explained by such changes simply being larger —
the association holds among changes of comparable size. This provides quantitative, size-robust
evidence that structural-change friction is measurable through review-and-issue data, supporting the
case for a full study.

## 5. Threats to validity

- **Association, not causation.** The Cox model rules out change size but not other confounders
  (module criticality, contributor experience, review contentiousness).
- **Proxy limitations.** Resolution time includes idle waiting and is not pure effort; the
  structural-review signal is a heuristic pending codebook validation.
- **Measurement validity.** The F2 rate depends on a keyword classifier (25% precise); the codebook is
  drafted but not yet dual-rated (Cohen's κ).
- **Non-independence.** Some episodes share a ticket; clustering is not yet modeled.
- **External validity.** Single project, single release-line window.

## 6. Methodological contributions

Beyond the finding, the study produced reusable methodological assets: a scalable, fault-tolerant
refactoring-mining pipeline that survives tool pathologies at scale; a technique for recovering full
PR review discussion from Jira via bot-relay (no GitHub credentials); and a monorepo-aware
traceability probe. These lower the cost of scaling the study to additional corpora.

## 7. Proposed full study (roadmap)

1. **Validate the signal:** complete dual-rater codebook labeling and compute inter-rater agreement
   (κ); replace the keyword heuristic with the validated classifier.
2. **Strengthen the outcome model:** derive effort proxies from the Jira changelog (status-transition
   timing rather than raw open→close), add covariates (module, contributor, priority), and model
   ticket-level clustering.
3. **Establish generality:** replicate across Kafka, HBase, and Camel to test whether the association
   is project-specific or a broader property of open-source architectural work.
4. **Full survival analysis:** episode↔signal interval tables with censoring feeding Kaplan–Meier and
   Cox models, using the public Jira dump (Zenodo record 15719919) for complete changelog history.

## 8. Significance

The study demonstrates, on real data, that (a) a common assumption about open-source effort data
(estimate availability) fails, (b) an alternative architectural-friction signal is measurable from
review discussion, and (c) that signal is significantly and robustly associated with a development
outcome. Together these justify a full empirical investigation of architectural refactoring cost
through review-and-issue data — with a working pipeline and a positive preliminary result already in
hand.
