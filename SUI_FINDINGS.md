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

**One effect survives every control: architectural changes attract more reviewer attention at
equal change size. Nothing else does.**

Matching each architectural PR to a non-refactoring PR of near-identical size:

| size-matched, n=28 pairs | architectural | control | p | |
|---|---|---|---|---|
| **PRs with ≥1 review thread** | **61%** | **29%** | **0.023** | McNemar, paired |
| review threads (count) | 1.5 | 0.0 | 0.0049 | survives BH FDR (q=0.014) |
| merge latency | 3.20 d | 1.22 d | 0.058 | not significant |
| ~~commits per PR (rework)~~ | ~~4.0~~ | ~~2.0~~ | ~~0.014~~ | **RETRACTED — see below** |

### Retraction: the rework finding does not stand

An earlier version of this document reported that architectural PRs need more revision cycles
(4.0 vs 2.0 commits, p=0.014). **That result is withdrawn.**

"Commits per PR" is not a rework measure. It correlates with PR size (rho=+0.56) and with how long
the PR stayed open (rho=+0.48, p=2e-24) — a PR left open accrues commits whether or not anything
was reworked. Re-measured as *commits pushed after the first review comment*, which is what rework
actually means, the effect vanishes:

| size-matched, n=27 pairs | architectural | control | p |
|---|---|---|---|
| total commits (the old, confounded measure) | 4.0 | 2.0 | 0.0053 ** |
| **commits after first review** | 1.0 | 0.0 | **0.150** |
| fraction of commits after review | 0.29 | 0.00 | 0.549 |

Architectural PRs accumulate more commits because they are larger and stay open longer, not
because reviewers send them back. The rework claim was an artefact of a bad proxy.

### What the surviving finding means

Reviewers *look harder* at architectural change — they open more inline threads on it — but that
extra scrutiny does not translate into more revision, and does not delay the merge. Attention
without consequence.

This is a narrower claim than the one it replaces, and it is the only one the data supports.

### Second leg: review does not measurably protect the work either

Because 69% of architectural work here bypasses PRs entirely, the corpus offers a natural
experiment — do reviewed architectural changes survive better than unreviewed ones?
(`scripts/sui/review_value.py`; 180-day horizon, right-censored commits excluded, matched on
number of files touched.)

| size-matched, 24 pairs | reviewed | unreviewed | p |
|---|---|---|---|
| fraction of files deleted | 0.050 | 0.211 | 0.109 |
| fraction re-refactored | 0.333 | 0.528 | 0.233 |
| any file deleted | 58% | 79% | 0.212 |
| any file re-refactored | 75% | 83% | 0.724 |

**Null on all four**, raw and matched. Review attention buys neither revision nor durability.

Two honest caveats in opposite directions. All four measures lean the same way — reviewed work
survives somewhat better — which is suggestive; but they are two outcomes measured two ways, not
four independent tests, so the agreement is weaker evidence than it appears. And at n=24 pairs the
test is underpowered: a real effect of this size would not be detectable here. **This is "no
evidence of an effect", not "evidence of no effect".**

### Against the Hadoop result

Hadoop found friction in **time** — architectural work waited. Here, once size is controlled,
time shows nothing (p=0.058) and neither does rework. Only review attention differs.

The tempting reading is that Apache volunteers queue so difficulty surfaces as waiting, whereas a
paid team does not queue so it surfaces elsewhere. **The data no longer supports the second half
of that story** — with rework retracted, there is no measured "elsewhere" beyond reviewer
attention. The queueing hypothesis remains interesting and untested; it should not be presented as
a finding.

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

**6 · But PR routing is NOT arbitrary — this bounds what the finding can claim.**
(`scripts/sui/selection_bias.py`)

| architectural commits | PR-routed (n=30) | direct-push (n=66) | p |
|---|---|---|---|
| churn | 777 lines | 151 lines | 0.0037 ** |
| files touched | 22 | 9 | 0.0038 ** |
| **abstraction share** | **37%** | **9%** | 0.0027 (Fisher) |

Work that goes through a PR is five times larger and four times more abstraction-heavy than work
pushed straight to main. The matched comparison remains internally valid — architectural PRs are
still compared to same-size non-architectural PRs *within* the PR population — but the finding
**cannot generalise beyond reviewed work**. It says: *among changes routed through review,
architectural ones draw more threads.* It is silent on the majority that never gets reviewed.

### The substantive finding hiding inside the bias

**69% of architectural work in this repository never passes through code review at all.**

That is arguably more interesting than the review-thread result. In a company-owned project, the
structural changes are largely made by pushing to main. Any friction study restricted to PR data
is, in this setting, measuring the minority of architectural work that someone chose to expose.

### Author identity aliasing — a data-quality error I was making

The author table shows `ivan@dalmet.fr` routing through PRs **0%** of the time (59 commits) and
`ivan-dalmet@users.noreply.github` **100%** of the time (16 commits). These are the **same person**:
`ivan-dalmet` is the GitHub username, `dalmet.fr` his own domain, and the `noreply` form is what
GitHub attributes to commits made through its web flow.

One human, two identities, two different workflows — and every earlier author-level statistic in
this document treated them as two people. Author aliasing must be resolved (by GitHub login, not
email) before any social or ownership variable is computed. This also explains the apparent
"bimodal routing habit", which is a workflow artefact rather than a person-level preference.

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

**Chunk loss is clustered in time but NOT biased by commit size — hypothesis tested and rejected.**
The stall watchdog kills chunks containing slow commits, so the natural worry is that it
preferentially destroys large, complex commits — precisely where architectural refactorings live.
That would bias the study against its own subject.

Tested within RefactoringMiner's actual scope (`root..HEAD`, 1,198 commits; 1,057 analysed, 141
lost):

| | analysed | lost | p |
|---|---|---|---|
| churn | 32 lines | **14 lines** | 0.0022 |
| top-decile-churn share | 9.6% | 12.8% | 0.23 (n.s.) |

Lost commits are *smaller*, and there is no enrichment for the largest ones. The mechanism is
structural: the watchdog kills a whole **chunk**, so ~30 commits die because one of them hung,
regardless of their own size. Loss is a temporal accident, not a complexity effect.

*A first attempt at this test was wrong and is recorded as a caution: it compared against
`git log --all`, so the "missing" set was contaminated with 930 commits on other branches that
were never in scope, and it produced the opposite (spurious) conclusion that lost commits were
larger. The comparison set for a coverage-bias test must be exactly the range the tool was asked
to analyse.*

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
