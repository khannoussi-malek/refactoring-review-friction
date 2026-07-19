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

## 4. Candidate result and its retraction (the core methodological point)

Splitting the 345 episodes by whether their review discussion is structural gave an apparent effect:

| Group | n | Median time-to-resolve | Median review size |
|---|---|---|---|
| Structural review | 106 | 67 days | 30 comments |
| Other | 239 | 23 days | 10 comments |

Kaplan–Meier/log-rank p = 0.0001; a Cox model controlling for change size (refactoring count, files,
churn) left it apparently intact (hazard ratio 0.66 → 0.69, p = 0.003).

**A further robustness check retracts it.** Adding discussion volume (log comment-count) as a
covariate collapses the structural-review effect to **HR 1.10, 95% CI [0.83–1.46], p = 0.51** — no
independent association. Discussion volume itself is the strong predictor (HR 0.70 per log-comment,
p ≈ 1×10⁻⁹), and a volume-independent operationalization (structural *density*) is also null
(HR 1.50, p = 0.26).

**Interpretation:** the candidate result was an artifact of discussion *quantity*, not structural
*content* — tickets with more review naturally take longer, and the keyword signal (≥3 structural
mentions) is entangled with volume. Once volume is controlled, no structural-specific effect on
resolution time remains. The hypothesis is therefore **untested, not disproven**: the keyword measure
is only 25% precise and volume-confounded, so a validated, volume-independent structural signal is
required to test it. The transferable contribution is the demonstrated ability to detect and retract
a spurious association before it is reported as a result.

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
(estimate availability) fails on Apache, (b) an alternative architectural-friction signal is
*measurable* from review discussion via bot-relayed PR review, and (c) that a candidate association
with a development outcome, once stress-tested, proved to be a discussion-volume confound and was
retracted. The scientific contribution is a reproducible pipeline plus a well-scoped, still-open
question: whether a *validated, volume-independent* measure of structural review discussion carries
an effect that raw discussion volume does not. The pilot supplies the tooling, the feasibility
evidence, and the study design to answer it — and shows the methodological discipline the answer will
require.
