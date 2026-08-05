# The direction disagreement — two measurements, opposite signs, not resolved

**Status: unresolved by design. This file exists so the author decides, not the
draft.** The revision brief was explicit: compute both, present both, choose
neither. Everything below is measurement and mechanism; the closing section lists
what a decision would have to turn on and does not take it.

Computed 2026-08-05 by `scripts/revision_metrics.py`, output
`paper/revision_metrics.json`.

---

## 1. The two numbers

| | population | how the ticket side is measured | Spearman(CSR, TRR) | 95% CI | permutation *p* | detectable at 80% power |
|---|---|---|---:|---|---:|---:|
| **LIVE** | the **12** eligible projects | exact: every issue key fetched from the tracker on 2026-07-25 and intersected with the cited set | **+0.518** | [−0.080, +0.841] | 0.088 | \|rho\| ≥ 0.732 |
| **FROZEN** | the **33** projects with a usable frozen denominator | estimated: number-capping against the frozen public-corpus issue count | **−0.010** | [−0.352, +0.335] | 0.958 | \|rho\| ≥ 0.471 |

Permutation *p* from 200,000 relabellings, seed 20260805.

**They are not formally contradictory.** The intervals overlap over
[−0.080, +0.335], so no test rejects the hypothesis that both are estimating the
same parameter. Neither is individually significant at 0.05. What they are is
*differently signed point estimates on which the paper's headline sentence
depends*, and the sentence cannot be written from both.

---

## 2. Three candidate explanations, and what each predicts

### 2a. The populations differ, and the mechanism flips with them

This one is measured rather than hypothesised, and it accounts for the sign
change on its own.

| quantity | over the 12 (live) | over the 33 (frozen) |
|---|---:|---:|
| rho(CSR, TRR) | **+0.518** | **−0.010** |
| rho(commits-per-ticket, TRR) | +0.937 | +0.476 |
| rho(ceiling, TRR) | **+0.965** | +0.671 |
| **rho(CSR, commits-per-ticket)** | **+0.455** | **−0.717** |
| rho(CSR, fill) | +0.329 | +0.319 |
| CSR spread (max/min) | 1.19× | 9.40× |
| commits-per-ticket spread | 5.79× | 30.15× |
| fill: median | 0.887 | 0.579 |
| fill: spread | 1.19× | 378× |

TRR is very nearly the ceiling in both arms (rho 0.965 and 0.671), and the
ceiling is `CSR × commits/tickets`. So the sign of rho(CSR, TRR) is largely the
sign of **rho(CSR, commits-per-ticket)** — and that flips: **+0.455** among the
eligible twelve, **−0.717** across the 33.

Read plainly: *within* the group that already cites tickets diligently, the
projects that cite most also happen to have more commits per ticket. *Across* the
full probe, the relationship reverses — the projects with the highest commit-side
rates are Hadoop-ecosystem projects with large trackers and comparatively few
commits per ticket, while several low-CSR projects (Accumulo, Wicket, Jena) have
many commits per ticket. The composite inherits the flip.

**This explanation predicts** that the disagreement is real, is about
populations, and would persist if both arms were measured with the same
estimator.

### 2b. The estimator differs, and the frozen one is noisier

The frozen arm stacks two approximations on the live one (number-capping, and
substituting an older tracker snapshot). Its end-to-end error against the twelve
known-exact rates is **1.76pp mean / 11.91pp max**, and its `fill` column — which
should be bounded in [0, 1] and tightly clustered — has a spread of **378×** and a
minimum of 0.002, against 1.19× on the live arm. That is a signature of noise,
not of signal.

**Critically, the frozen estimator has never been validated anywhere near the
range where the disagreement lives.** The twelve validation projects span
commit-side 82.6–98.3%; the twenty-one projects that only the frozen arm covers
span 10.5–78.1%. **Zero overlap.**

**This explanation predicts** that the −0.010 is attenuated toward zero by
measurement error, that the true population value is closer to the live +0.518,
and that a live measurement over all 38 would resolve it. **It cannot be tested
without a Jira fetch, which the repository's standing rule forbids.**

### 2c. The swamping argument, and why it does not transfer cleanly

The reviewer's suggestion was that rho ≈ 0 is arithmetically *expected*, because
CSR's spread is swamped by the spread in commits-per-ticket: if TRR ≈ CSR × k and
k varies far more than CSR, the correlation with CSR washes out.

That holds on the twelve, where CSR spans only **1.19×** against **5.79×** for
commits-per-ticket. **It does not transfer unexamined to the 33**, where CSR
spans **9.40×** — CSR is no longer the near-constant factor. The ratio of spreads
is 4.9× on the twelve and 3.2× on the 33, so swamping is *relatively* weaker
where the null is observed, which is the opposite of what the argument needs.

**This explanation predicts** rho ≈ 0 wherever commits-per-ticket dominates, and
therefore predicts it *more strongly* on the twelve than on the 33 — where the
observed value is +0.518. On these numbers the swamping argument argues against
itself.

---

## 3. What a decision would have to turn on

Not taken here. The considerations, in the order they seem to matter:

1. **Which population the paper's claim is about.** "A commit-side bar does not
   select for ticket-side coverage" is a claim about *candidate projects*, which
   is the 33. "Among projects that pass, the two rates move together" is a claim
   about the eligible corpus, which is the 12. Both are defensible papers; they
   are not the same paper.
2. **Whether an unvalidated estimator can carry a headline.** §2b's zero-overlap
   finding is the strongest argument against leading with −0.010.
3. **Whether n = 12 can carry one either.** The live arm detects only
   \|rho\| ≥ 0.732 at 80% power; +0.518 is inside its own noise floor, and its
   interval crosses zero.
4. **Whether the ceiling decomposition makes the question secondary.** §2a
   suggests the interesting quantity is not rho(CSR, TRR) at all but `fill`,
   which is flat at 0.89 ± on the live arm across a 5.8× spread in TRR. If the
   paper's finding is "the ticket-side rate is mostly arithmetic", then the
   correlation between the two rates is a corollary and need not be a headline.

**The current draft (§4.3) reports both, states that a strong positive
association is ruled out and a null is not established, and points here.** That
is the position until the author replaces it.

---

## 4. What is not in dispute

* Both rho values are reproducible from committed artifacts.
* The ceiling identity `TRR ≤ CSR × commits/tickets` is exact, not statistical,
  and binds for all twelve eligible projects.
* `fill` on the live arm is flat: median 0.887, range 0.801–0.951.
* Neither correlation is statistically significant at 0.05.
* Neither arm has the power to establish a null.
