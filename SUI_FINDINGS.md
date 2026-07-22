# start-ui-web — exploratory findings

**Corpus:** `BearStudio/start-ui-web` · 1,199 commits (2019-12 → 2026-07) · 26.7k LOC TypeScript
**Detector:** RefactoringMiner 3.1.4 (TypeScript support complete since 2026-05-24)
**Coverage:** 1,121 / 1,199 commits = **93%**
**Date:** 2026-07-22

> **Status: EXPLORATORY.** Every p-value here is uncorrected and hypothesis-*generating*. The
> corpus is one company-owned repository with n=28 architectural PRs. Nothing below may be
> reported as a result without a pre-registered re-test on a held-out corpus. It is recorded
> because it tells us what is worth testing, not what is true.

---

## The headline

**Architectural changes cost more iteration and more review attention — but not more calendar
time — and this survives matching on change size.**

Matching each architectural PR to a non-refactoring PR of near-identical size (801 vs 802 lines
median, p=0.97):

| size-matched, n=28 pairs | architectural | control | p |
|---|---|---|---|
| **commits per PR** (rework) | **4.0** | **1.5** | **0.016** * |
| **review threads** | **1.5** | **0.0** | **0.0058** ** |
| merge latency | 3.25 d | 1.91 d | 0.21 — **dies** |

Raw, unmatched, the same measures give p=2e-05 and p=6e-05 — so size explains much of the effect,
but not all of it. What remains after the control is *iteration* and *attention*, not *time*.

### Why this is interesting against the Hadoop result

Hadoop found friction in **time** — architectural work waited. It also found that the CI-rework
effect **died** under a change-size control (p=0.07): architectural patches needed more attempts
only because they were bigger.

Here the opposite pattern holds. Time shows nothing once size is controlled; rework and review
attention survive. A plausible reading — untested — is that the difference is queueing. Apache
volunteers queue, so difficulty surfaces as waiting. A paid team does not queue, so the same
difficulty surfaces as more revision cycles and more reviewer attention instead.

If that holds up, it is a statement about *how difficulty manifests under different labour
models*, which is a more portable claim than either study alone.

### Adversarial robustness checks (`scripts/sui/robustness.py`)

Five attempts to kill the two surviving effects. Two held, one weakened them, two supported them.

**1 · Multiple comparisons — both survive FDR.** 28 tests were run on this corpus. Under
Benjamini–Hochberg:

| test | raw p | BH q | |
|---|---|---|---|
| independent reviewers | 0.0002 | 0.0007 | survives **Bonferroni** |
| review threads (matched) | 0.0049 | 0.0137 | survives FDR |
| rework (matched) | 0.0140 | 0.0327 | survives FDR |
| merge latency (matched) | 0.0584 | 0.0887 | fails — consistent with the null |
| abstraction vs relocation threads | 0.0426 | 0.0751 | fails — **do not report** |

Only *independent reviewers* clears the Bonferroni threshold (0.00179). The two headline effects
clear FDR but not Bonferroni; at n=28 that is the honest ceiling.

**2 · Matching is stable.** 500 bootstrapped greedy-matching orders give an identical p every
time. This is not a bug: with 28 treated PRs against ~370 controls, near-ideal matches are always
available, so collisions never force a worse pairing and order cannot matter.

**3 · The review-thread effect is not an artefact of zero-inflation.** Threads are mostly 0, so a
rank test could mislead. Re-tested as a proportion it holds, and it holds under the stricter
*paired* test:

| | with ≥1 review thread |
|---|---|
| architectural PRs | 17/28 (**61%**) |
| size-matched controls | 8/28 (**29%**) |

Fisher exact p=0.031; **McNemar paired p=0.023** (11 vs 2 discordant pairs). This is now the
best-supported result in the study.

**4 · The rework measure is confounded — this weakens the finding.** "Commits per PR" correlates
with PR size (rho=+0.56) *and* with how long the PR stayed open (rho=+0.44, p=1e-22). A PR that is
open longer accrues commits regardless of whether anything was reworked. Since architectural PRs
are open longer, part of the rework effect may be duration, not revision.

**The rework result should be treated as provisional until re-measured with a duration-independent
proxy** — commits *after the first review comment*, force-push count, or explicit review rounds.
Recorded as a known weakness rather than quietly retained.

**5 · Control-group contamination biases toward the null.** Only **32%** of commits link to a PR,
and only **30 of 96** architectural commits (31%) are visible at PR level. The other 66 land inside
PRs classified as "none", contaminating the control group with the very thing being tested. That
dilution can only *shrink* the measured difference — so the reported effects are conservative.

It also costs power, and introduces a selection question worth pursuing: unlinked commits are
largely direct pushes, so PR-visible architectural work may be systematically different from the
work the owner pushes straight to main.

---

## Secondary findings

### 1 · Commit messages are useless for detecting refactoring

| | |
|---|---|
| architectural commits whose message says "refactor" | 3 |
| messages claiming refactoring that are not architectural | 7 |
| architectural commits that are **silent** about it | **93** |

**Precision 30%, recall 3%.** A message-mining approach would find 3% of the architectural work in
this repo. This is a stronger version of the Hadoop codebook result (keyword rule 25% precise) and
is a direct argument for AST-level detection over message mining.

### 2 · Architectural work is not planned

| | links an issue | labelled |
|---|---|---|
| architectural | 7% | 39% |
| other refactoring | 7% | 34% |
| non-refactoring | 10% | 33% |

Architectural change is no more likely to be tracked in advance than anything else — slightly less.
It appears to be emergent and opportunistic rather than planned. Combined with finding 1, it is
largely *invisible* in the project's own records: not announced in the message, not tracked in an
issue.

### 3 · Review participation is higher

| | self-merged | independently reviewed | median independent reviewers |
|---|---|---|---|
| architectural | 32% | **96%** | **2.0** |
| other refactoring | 48% | 96% | 1.0 |
| non-refactoring | 23% | 73% | 1.0 |

2.0 vs 1.0 independent reviewers, p=0.0002. Architectural work pulls in a second pair of eyes.

### 4 · Migration-driven work dominates the size story

Architectural commits co-occurring with a dependency-manifest change are **13× larger**
(1,372 vs 104 lines, p<0.0001), n=21 vs 69. Since size drives merge latency, re-platforming churn
accounts for much of the apparent friction. This repo is a starter template whose product *is*
tracking the frontend stack — V3 rewrite, Next→TanStack Start, Chakra→shadcn→base-ui,
ESLint→oxlint. `migration_driven` must be a covariate in any model.

### 5 · The client/server contract hypothesis gets no support

Predicted: architectural work concentrates on the shared client/server contract files.

| | touches a shared-contract file |
|---|---|
| architectural refactorings | 11% |
| baseline (share of codebase) | 10% |

No enrichment. The hypothesis is empty in this corpus and should not be pre-registered on the
strength of intuition. (Tier membership computed by import-graph reachability, not paths — a
path rule misclassifies 88% of the contract surface, since files like
`src/features/book/schema.ts` sit in feature folders yet are imported by both tiers.)

### 6 · Total code replacement, and what survives it

| | |
|---|---|
| TypeScript files ever created | 992 |
| deleted since | 537 (54%) |
| **files created before Sep-2020 still alive** | **0** |
| median lifespan of a deleted file | 431 days |

Across the V3 reset, only **4 of 37** i18n keys survived:

```
survived:  common.actions · common.languages
           components.errorBoundary · components.searchInput
destroyed: account.* · auth.* · admin.* (all domain vocabulary)
```

Everything domain-specific was destroyed; everything generic survived. This **inverts** the premise
of Domain-Driven Design and Clean Architecture, which hold that the business domain is stable and
technology churns. A likely explanation specific to this artefact: it is a *template*, so the
domain features are demo content showcasing the current stack, and the generic infrastructure is
the real product. Testable against the 165 forks — if true, adopters should delete the demo domain
and keep the infrastructure.

---

## Threats and corrections

**A 93%-missing year, found and repaired.** The first RefactoringMiner run lost 3 chunks to hangs,
and the loss was *clustered*, not random: 75 of 81 commits in 2024 (93%) were absent, against 2–8%
in every other year. Every temporal result from the first pass was therefore invalid — including
"zero architectural commits in 2024", which was a measurement hole. A targeted re-run recovered 68
commits, 120 refactorings, 24 architectural, lifting coverage 88% → 93%. **Coverage loss in
chunked RefactoringMiner runs must be checked for clustering, not just reported as a percentage.**

**The survival result is length-biased and is NOT reported as a finding.** Files touched by
architectural refactoring appear to live longer (431 vs 298 days, p<0.0001) — but a file must
survive long enough *to be* refactored. The comparison is partly tautological. It requires a Cox
model with refactoring as a time-varying covariate before it means anything.

**`Change Type Declaration Kind` excluded as a suspected false positive.** 160 instances, all
reporting "interface to class". A traced case (`src/features/account/types.ts`) is
`export type Account = User` — a plain type alias, neither interface nor class. Independently
corroborated by the fact that this codebase uses function components exclusively and so contains
essentially no classes at all. Reported upstream-worthy: RefactoringMiner's TypeScript support is
two months old and has no independent validation in the literature.

**No temporal trend.** Architectural share of refactoring commits ranges 13–44% by year with no
significant trend (rho=−0.54, p=0.215) on the repaired corpus.

**Small n throughout.** 28 architectural PRs, 28 matched pairs. One repository. One company.

---

## Reproduce

```
scripts/sui/investigate.py    round 1 — commit-level joins across all layers
scripts/sui/investigate2.py   round 2 — PR-level, size-matched, survival, import-graph tiers
scripts/sui/investigate3.py   round 3 — repaired corpus, temporal, review participation
bash scripts/run_rm_safe.sh <repo> <start> <end> 32 120 refminer_sui.json
```
