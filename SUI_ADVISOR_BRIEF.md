# Extending RQ1 to full-stack TypeScript — advisor brief

**Date:** 2026-07-22 · **Corpus:** `BearStudio/start-ui-web` · **Status:** exploratory pilot, one
finding surviving, one retracted

---

## 1. What this is and why

The Hadoop study's stated weakness is external validity: one project, one language, one governance
model. This pilot asks whether the RQ1 apparatus transfers to a different ecosystem — full-stack
TypeScript — and what it finds there.

It is a **pilot, not a test**. The corpus was chosen because it is small enough (26.7k LOC, 1,199
commits) to reconstruct completely and inspect exhaustively, which Hadoop is not. It has almost no
outcome variance (median PR merge 0.80 days; 25% merge within the hour), so it cannot support a
friction claim on its own. Its purpose is to validate the instrument and expose the
operationalisation problems before they are expensive.

## 2. Method

| | |
|---|---|
| Detector | **RefactoringMiner 3.1.4** — the same tool used on Hadoop; TypeScript support completed 2026-05-24 |
| Corpus | 1,199 commits (2019-12 → 2026-07), **93% analysed** after repairing a coverage gap |
| Detected | 2,151 refactorings; 96 architectural commits; 28 architectural PRs |
| Joins | RefactoringMiner → commits → PRs/reviews → files → import-graph tiers |
| Test | each architectural PR matched to a non-refactoring PR of near-identical size (821 vs 818 lines median, p=0.95), then compared |

Using the same detector on both corpora holds the measurement instrument constant, which makes any
future Java/TypeScript comparison meaningfully controlled rather than confounded by tooling.

## 3. Result

**One effect survives every control.**

| size-matched, n=28 pairs | architectural | control | p | |
|---|---|---|---|---|
| **PRs with ≥1 review thread** | **61%** | **29%** | **0.023** | McNemar, paired |
| review thread count | 1.5 | 0.0 | 0.0049 | survives BH FDR (q=0.014) |
| merge latency | 3.20 d | 1.22 d | 0.058 | n.s. |

**Interpretation.** Reviewers open more inline discussion on architectural change at equal change
size — but that scrutiny produces no additional revision and no merge delay. *Attention without
consequence.*

Robustness: survives Benjamini–Hochberg correction across all 28 tests run on the corpus; matching
is stable across 500 bootstrapped orderings; the effect holds when re-tested as a proportion
(guarding against zero-inflation) and under the stricter paired test.

## 4. A result I withdrew

An earlier version reported that architectural PRs require more revision cycles (4.0 vs 2.0
commits, p=0.014). **That is retracted.**

"Commits per PR" is not a rework measure. It correlates with PR size (rho=+0.56) and with how long
the PR stayed open (rho=+0.48, p=2e-24) — a PR left open accrues commits regardless of whether
anything was reworked. Re-measured as *commits pushed after the first review comment*, which is
what rework means:

| same 27 matched pairs | architectural | control | p |
|---|---|---|---|
| total commits (old proxy) | 4.0 | 2.0 | 0.0053 |
| **commits after first review** | 1.0 | 0.0 | **0.150** |
| fraction after review | 0.29 | 0.00 | 0.549 |

This also removes the more interesting story it had supported — that difficulty surfaces as
*waiting* where volunteers queue and as *iteration* where a paid team does not. With rework gone
there is no measured "elsewhere". That hypothesis is recorded as untested, not as a finding.

## 5. Two hypotheses that returned null

- **Client/server contract boundary.** Predicted that architectural work concentrates on files
  shared between frontend and backend. It does not: 11% of architectural refactorings touch a
  shared-contract file against a 10% baseline. The hypothesis was mine; the pilot showed it empty
  before it could be pre-registered.
- **Abstraction vs relocation** (the Hadoop headline). Not testable as originally framed. Java's
  abstraction categories barely fire in React — Extract Interface/Superclass/Class total 8
  instances. React's abstraction mechanism is the **custom hook**, not the class hierarchy (14 of
  21 detected extractions are hooks, several of them context hooks, which is structurally the same
  act as Extract Interface). Re-operationalised, the abstraction arm is n=29 against 219
  relocations — measurable, but too thin here to test.

## 6. Methodological contributions

These do not depend on the corpus size and are usable independently.

1. **Commit messages detect 3% of architectural refactoring.** Precision 30%, recall 3%; 93
   architectural commits never mention it. A stronger version of the Hadoop codebook result
   (keyword rule 25% precise) and a direct argument for AST-level detection over message mining.
2. **A systematic false-positive class in RefactoringMiner's TypeScript mode.** 160 instances of
   `Change Type Declaration Kind`, all reporting "interface to class"; a traced case is a plain
   type alias, and the codebase uses function components exclusively so contains essentially no
   classes. RM's TypeScript support is two months old and has no independent validation in the
   literature; this is the first, and it found something reportable.
3. **Coverage loss in chunked RefactoringMiner runs must be checked for *clustering*, not just
   reported as a percentage.** The first run lost 3 chunks to hangs — 93% of 2024, against 2–8%
   elsewhere — which silently produced "no architectural work in 2024". Repaired; coverage 88% →
   93%. Any study reporting aggregate RM coverage may be concealing a hole like this.
4. **Path-based client/server tier assignment misclassifies 88% of the contract surface.** Tier
   membership must be computed by import-graph reachability: contract files sit inside feature
   folders, not in anything named `shared/`.

## 7. Limitations — stated plainly

- **n=28 architectural PRs, one repository.** Exploratory. Every p-value uncorrected unless stated.
- **Company-owned open source.** BearStudio develops it for public use and internal consumption.
  Architectural decisions are made off-repo; the repository records outcomes, not deliberation.
  This suppresses observable friction and can manufacture a false null.
- **Only 31% of architectural commits are visible at PR level**, so control PRs are contaminated
  with unlabelled architectural work. This biases *toward* the null — the reported effect is
  conservative — but it costs power and raises a selection question about direct-push work.
- **Migration-driven churn.** A starter template's product is tracking the frontend stack.
  Architectural commits co-occurring with a dependency change are 13× larger. Controlled as a
  covariate, never silently filtered.
- **This corpus cannot support a friction claim.** Any such claim requires the replication below.

## 8. In progress

Replication of the surviving finding on three independent full-stack TypeScript corpora —
Documenso, Twenty, cal.diy — using a portable harness (`scripts/sui/replicate.py`) that reproduces
the size-matched test unchanged. Each returns a REPLICATES / no-effect verdict. If the finding
fails there, that is the honest answer and it arrives cheaply.

## 9. Question for review

The surviving result is narrow: reviewers attend more to architectural change, with no downstream
consequence in time or revision. **Is "attention without consequence" a publishable finding in its
own right, or only meaningful as a component of a larger friction argument?** The answer decides
whether the replication is the paper or a robustness section of one.

---

**Reproduce:** `SUI_FINDINGS.md` (full results, including everything that failed) ·
`scripts/sui/` (investigation rounds 1–3, robustness, replication harness)
