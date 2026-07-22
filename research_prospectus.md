# RQ1 — Where the friction in architectural refactoring actually lives
### Architectural refactorings are harder to *build*, not harder to merge — and they are the one class of work a decade of tooling did not make cheaper

**Author:** (independent pre-PhD study) · **Date:** 2026-07-22 · **Corpus:** Apache Hadoop
**Status:** feasibility established; a mechanism-level finding demonstrated and defended against six
controls; three competing explanations tested and rejected; one earlier claim corrected and one
retracted. Full detail in `results_dossier.md`; every command in `SLICE_LOG.md`.

---

## 1. The question, and how the data reframed it

RQ1 originally asked whether *effort estimates* on issue tickets relate to architectural refactoring.
The first thing this study did was test that assumption, and it fails outright:

> **Apache records no effort estimates.** 0 of 345 architectural-episode tickets carry one. A
> developer says so directly on HADOOP-18679: *"no actual time allocated to implement it."*

That is a property of the process, not a data-collection problem, so the question was reframed around
signals that *are* present: **issue-tracker state transitions, review discussion, and commit history**.
The current question is:

> **Do architectural refactorings carry measurably more development friction than ordinary changes —
> and at which point in the work does that friction actually occur?**

The second half is what makes it answerable rather than rhetorical.

## 2. Method and scale (fully reproducible)

- **Detection:** RefactoringMiner over **8,919 commits**, Hadoop v3.1.0→v3.4.3, parallelised 8–16× with
  a self-healing runner (`run_rm_safe.sh`) that auto-skips the minified-JS commits RM hangs on.
  90–99% coverage → **51,861 refactorings**.
- **Episodes:** package-level and cross-package structural refactorings → **349 architectural episodes**
  (323 tickets). Architectural refactoring is rare: 349 of 51,861.
- **Control:** **400 ordinary refactoring tickets** — the comparison that makes every claim below a
  difference rather than a description.
- **Signals:** public Apache Jira (status changelog, review discussion via the `githubbot` PR relay,
  issue properties) plus git (commit clock, per-ticket change size, authorship).
- **Traceability: 99%** (345/349) — but only when every monorepo subproject key is matched; a
  single-key probe misreads it as 26%.

## 3. Headline finding — the friction is in **abstraction**, and specifically in **building** it

Architectural refactorings are not uniform. Split by what they *do*:

| Measure (medians) | Relocation (move/rename) | **Abstraction** (extract interface/superclass/class) | p |
|---|---|---|---|
| Triage latency (days) | 2.8 | **7.2** | 0.004 |
| Resolution time (days) | 18.0 | **34.5** | 0.0001 |

**Relocating code is no harder than ordinary work** (2.8 vs 2.1 days); **creating a new abstraction is
~2.5× slower to start and ~2× slower to resolve.** The effect survives controls for change size,
discussion volume, contributor experience, module tier, and era.

**Decomposing the status changelog localises it.** Apache's workflow separates *doing the work*
(created → first `Patch Available`) from *getting it accepted* (time held in `Patch Available`):

| Phase | Architectural | Ordinary | p | n |
|---|---|---|---|---|
| Days to first patch | **3.86** | 1.00 | 0.002 | 251 / 294 |
| Days in review | 8.52 | 8.37 | 0.52 (n.s.) | 251 / 294 |
| **Active coding time** (`In Progress`) | **4.87** | 1.13 | 0.037 | 92 / 91 |

*Rows 1–2 use the full-workflow sub-corpus (tickets that reached `Patch Available`); row 3 uses the
tickets that log `In Progress` at all. The review-phase null holds in the whole corpus too
(5.63 vs 4.03, p=0.14), so it does not depend on the restriction.*

Architectural work is **~4× slower to produce a patch and ~4× longer in logged active coding**, yet is
**merged as fast as ordinary work**. Reviewers are not the bottleneck; construction is.

**Why this matters more than the raw timing gap:** time logged as `In Progress` is time somebody is
demonstrably working. It cannot be volunteer queueing. This converts the study's biggest threat —
"maybe Apache timings just measure volunteers being slow" — from an unbounded caveat into a measured
one. The core effect is **intrinsic construction difficulty** and should be expected to replicate
outside open source.

**Abstraction uniquely pays twice.** Within architectural work (full-workflow sub-corpus, n=251):
4.95 vs 1.11 days to build (p=0.009) **and** 12.15 vs 5.46 days in review (p=0.0003). A shared
abstraction is both harder to construct and harder to get others to agree to.

## 4. Second finding — the one class of work that did not get cheaper

Tracked across the decade with a **workflow-independent clock** (ticket → first commit citing it, from
git — necessary because Jira status hygiene collapsed from 93% to 16% at the GitHub migration):

| | Architectural | Ordinary (control) |
|---|---|---|
| Year vs days-to-first-commit | rho = +0.04, p = 0.45 — **flat** | rho = **−0.21**, p = 3e-05 — **improving** |

Difference-in-differences interaction **+0.20, p = 0.003**, controlling for abstraction and
connector-tier composition, and stable at +0.19 under every truncation window. The gap widens from
~1.6× to ~10×.

A decade of process investment — CI, PR review, Yetus automation — made routine change substantially
cheaper and left structural change untouched. That is **architectural debt compounding relative to
everything else**, and it reframes the stakes: the problem is not that architectural work is slow, but
that it is **the one category not getting better**. The ordinary-refactoring control is what makes
this interpretable — a shrinking or ageing community would slow *both* groups.

## 5. Supporting results

- **Entanglement:** architectural tickets link to ~2× more other issues (1.53 vs 0.76, p=0.001), and it
  holds within sub-tasks. Issue-links are a structural ticket property, immune to the volume confound.
- **Quality is a null, twice defended.** Reopen rates are equal (~7%, p=0.97). Under a much stronger
  test — pre-commit CI runs ≈ patch revisions — architectural tickets need more attempts (5 vs 3,
  p<1e-4) and that survives a discussion-volume control, but **not** a change-size control (p=0.07):
  architectural patches are simply far bigger (**1,178 vs 213 java lines churned**). Refined claim:
  architectural work is **not more error-prone per unit of code changed**; it involves more code.

## 6. What was tested and rejected — the method's credibility

Four candidate explanations were constructed and then failed against our own data. Each is reported.

| Claim | Test | Outcome |
|---|---|---|
| Structural review discussion → slower resolution | Cox, + discussion-volume control | **Retracted** — HR 0.69 (p=0.003) → **1.10 (p=0.51)**; it was volume in disguise |
| **Blast radius**: touching a depended-upon module invites hesitation | Maven dependency graph, 117 modules | **Refuted** — centrality does not predict triage (p=0.33); raw association runs *negative* |
| **Maintainer concentration** explains the slow module tier | Prior-window authorship from git | **Failed to establish** — collinear with module size (rho=−0.86); dies under a size control |
| Friction concentrates in foundational `hadoop-common` | Decomposed the Jira-prefix aggregate | **Corrected** — 62% of those tickets are cloud connectors; `hadoop-common` alone is 24.8 days, not 39.1 |

This is the asymmetry the study rests on: the abstraction finding has survived six controls and a
phase decomposition, while **every competing explanation we could construct died.** That is harder to
attack than a study in which everything happened to work.

## 7. A methodological contribution — three instruments that decay at once

Jira status comparability, status hygiene over time, and CI verdict visibility **all collapse at
Hadoop's 2019–20 GitHub migration** (e.g. CI verdicts: 84.6% of pre-2019 tickets carry them, **0%**
after 2022). Status-derived durations therefore change meaning mid-corpus, and are not comparable
across module tiers that drive different workflows. This is one structural fact about mining Apache
Jira rather than three coincidences, and it is why every decade-spanning claim here is built on
**git-derived instruments** instead. Any study mining Apache issue trackers across 2019 inherits this
problem; most will not have checked for it.

## 8. Threats to validity

Descriptive and associational, not causal. Single project, single release-line window; groups are not
matched on module or time. Survivorship bias toward changes that landed, so *abandonment* is not
observable. `In Progress` is logged by only ~25% of tickets, so active-time results rest on that
sub-corpus. Several results are necessarily era-bounded (§7). The self-assignment effect (2.05 vs
31.66 days to patch) is **endogenous** and reported as mechanism description, not causal estimate. The
keyword-based structural signal is only **25% precise** and has no dual-rater κ. 26% of episodes could
not be mapped to a Maven module because Ozone and Submarine left the repository.

## 9. Why this warrants a full study, and what it would do

The feasibility gate is passed on a real corpus, the pipeline is reproducible, and the pilot produced
a defended, mechanism-level finding plus four documented rejections. Three things follow directly:

1. **Separate intrinsic from open-source-specific effects.** §3 shows the *build-phase* cost is
   intrinsic; the *review-phase* cost and the question of who volunteers are not. A
   **commercial/industrial codebase contrast** tests a specific pre-stated prediction rather than the
   whole result. (Identity-firewall tooling for reporting a private subject under pseudonym is
   already in place.)
2. **Break the collinearity.** In one project, "peripheral module" — small, few-authored,
   low-centrality, vendor-specific — is a *single* variable (§6, row 3). Only a **multi-project
   corpus** can separate these, which makes replication on Kafka/HBase/Camel a precondition for any
   attention-based claim rather than optional generality work. It also carries pre-registered
   predictions from this pilot.
3. **Validate the structural signal** (dual-rater κ), then re-test the retracted result properly —
   it is untested, not disproven.

Plus: better effort proxies for the ~75% of tickets that never log `In Progress` (GitHub PR timestamps
give a workflow-independent clock), and reverts/follow-up fixes — the one rework channel that does not
decay at the migration, because it lives in git.

## 10. Reproduce

```
SLICE_LOG.md              every command, end to end
results_dossier.md        full results, including everything retracted or corrected
proposal_summary.md       proposal-ready synthesis with figures
scripts/                  RM pipeline, arch filter, review miner, phase decomposition,
                          blast-radius + social-centrality tests, temporal clock, CI rework
*_all.json, *.json        349 episodes, review signals, outcomes, and every result artifact
```
