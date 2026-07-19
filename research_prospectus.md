# RQ1 — a feasibility study with a preliminary result
### Do architectural refactorings that attract structural review discussion take longer to resolve?

**Author:** (independent pre-PhD study) · **Date:** 2026-07-19 · **Corpus:** Apache Hadoop
**Status:** exploratory — one project, one release-line window, heuristic signal. Findings are
associational and meant to justify a full study, not to conclude one.

---

## 1. The question and why it was reframed

RQ1 originally asked whether *effort estimates* on issue tickets relate to architectural
refactoring. The first thing this study did was test that assumption on real data — and it fails:

> **Apache records no effort estimates.** 0 of 345 architectural-episode tickets carry one. A
> developer states it outright on HADOOP-18679: *"no actual time allocated to implement it."*

So RQ1 was **reframed** around a signal that *is* in the data: **structural review discussion** —
reviewers arguing about code shape (extract/split/move/interface/coupling). With estimates gone,
**ticket cycle-time (open→resolve)** stands in as the effort/overrun proxy.

## 2. Data & method (fully reproducible — see `SLICE_LOG.md`)

- **Detection:** RefactoringMiner over **8,919 commits** across 4 Hadoop release ranges (3.1.0→3.4.3),
  parallelised 8–16× on a 12-core machine with a self-healing runner (`scripts/run_rm_safe.sh`) that
  auto-skips commits RM hangs on (minified-JS dependency bumps). 90–99% coverage per range.
- **Episodes:** 51,861 refactorings → **349 architectural episodes** (package-level + cross-module
  moves, extract class/interface/superclass) via `scripts/filter_architectural.py`.
- **Signals, mined from public Apache Jira** (`scripts/pr_review_signal.py`): githubbot mirrors the
  full GitHub PR review — including inline code comments — into the ticket, so the review discussion
  is available without a GitHub token.
- **Outcome:** ticket cycle-time (created→resolutiondate), with unresolved tickets right-censored.

## 3. Feasibility results (n = 345 traceable episodes)

| Filter | Result | Meaning |
|---|---|---|
| **Traceability** (commit→ticket) | **99%** (345/349) | excellent — Hadoop is highly minable |
| **Effort estimate present** | **0%** | absent — original framing not viable |
| **Structural review discussion** | **31%** (operational) | present in a substantial minority |

The F2 rate is set at **31%** deliberately. A first-pass codebook labeling (`codebook_results.md`)
found the naive keyword rule is only **25% precise** — most "refactor" mentions are approvals or
task-planning — so the naive 62% is an inflated upper bound. Honest range: **25–35%**.

## 4. Preliminary finding

Splitting the 345 episodes by whether their review discussion is structural:

| Group | n | Median time-to-resolve | Median review size |
|---|---|---|---|
| **Structural review** | 106 | **67 days** | 30 comments |
| Other | 239 | **23 days** | 10 comments |

- **Kaplan–Meier / log-rank: p = 0.0001.** The resolution-time curves differ significantly.
- **Cox regression controlling for change size** (refactoring count, files touched, churn):
  F2 hazard ratio **0.66 → 0.69** (p = 0.003) — the effect is **robust to change size**. Episodes
  with structural review discussion take ~31% longer to resolve *even at comparable change size*.

**In one line:** architectural refactorings that trigger structural review discussion take
significantly longer to resolve, and this is not merely because they are larger changes.

## 5. Threats to validity (honest)

- **Association, not causation.** Unmeasured confounders remain (module, contributor experience,
  review contentiousness). Cox rules out *size*, not everything.
- **Cycle-time ≠ effort** — it includes idle waiting between activity.
- **F2 is a heuristic** (keyword-based, 25% precise); the codebook is drafted but not yet dual-rated
  to κ. The 31% figure will move with a validated classifier.
- **Non-independence:** some episodes share a ticket (clustering not modelled).
- **External validity:** one project, one release-line window.

## 6. Why this is worth a full study

The feasibility gate is passed on a real corpus, and the *first* real analysis already shows a
significant, size-robust association between an architectural-refactoring review signal and an
outcome. The full RQ1 would: (a) validate the codebook (dual-rater κ), (b) replace cycle-time with
better effort proxies from the changelog, (c) add covariates and a proper survival model with
clustering, (d) replicate across Kafka/HBase/Camel for generality.

## 7. Reproduce
```
SLICE_LOG.md            every command, end to end
scripts/                citation probe, parallel + self-healing RM, arch filter, review miner
worksheet.md            the manual 5-episode trace + go/no-go
codebook*.md            F2 definition, labeling set, first-pass results
*_all.json              349 episodes, review signals, outcomes, Cox dataset
```
