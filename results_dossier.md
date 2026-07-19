# RQ1 study — full results dossier (for proposal improvement)

*A complete, honest hand-off of everything this preliminary study found, including a candidate result
that was retracted. All numbers are exact. Intended input for improving a research proposal — treat
the retraction (§6) as central, not as an appendix.*

Repository: `khannoussi-malek/refactoring-review-friction` (private). Corpus: Apache Hadoop.
Analyst note: this was an independent pre-PhD pilot to establish feasibility and demonstrate method.

---

## 1. Research question

**RQ1 (working):** Are architectural refactorings that attract *structural review discussion*
associated with greater development effort, as observed through issue-tracker outcomes?

Originally the intended effort signal was **developer effort estimates** on issue tickets. The pilot
falsified that assumption for this corpus and reframed the signal to **structural review discussion**,
with **ticket resolution time (created→resolved)** as the effort/friction proxy.

## 2. Method and pipeline

- **Corpus:** 8,919 commits across 4 Hadoop release ranges (v3.1.0 → v3.4.3).
- **Refactoring detection:** RefactoringMiner, run in parallel (8–16 cores) via a custom self-healing
  runner that auto-skips commits on which the tool hangs (minified-JavaScript dependency bumps).
  Coverage 90–99% per range. Output: **51,861 refactorings**.
- **Architectural episodes:** package-level + cross-package structural refactorings → **349 episodes**.
- **Signals from Apache Jira (public API):** Apache's `githubbot` mirrors the full GitHub PR review
  (including inline code-review comments) into the Jira ticket, so review discussion is recoverable
  without GitHub credentials. Effort proxy = cycle-time from ticket `created`/`resolutiondate`.
- **Analysis:** Kaplan–Meier + log-rank, then Cox proportional-hazards with covariates.

Environment: RefactoringMiner 3.1.4, JDK 17, Python 3.9, lifelines. All commands in `SLICE_LOG.md`.

## 3. Feasibility results (the solid part)

n = 345 traceable episodes (of 349; 323 unique tickets — some tickets carry >1 architectural commit).

| Filter | Question | Result |
|---|---|---|
| **F3 traceability** | commit cites a Jira key? | **345/349 = 99%** |
| **F1 estimate** | ticket records an effort estimate? | **0/345 = 0%** |
| **F2 structural review** | review argues about structure? | **31%** operational (62% naive keyword) |

Refactoring-type composition of the 349 episodes: Move Class 506, Extract Class 215, Move-and-Rename
Class 77, Extract Superclass 72, Extract Subclass 38, Extract Interface 36, Move Package 11, Rename
Package 10, Merge Package 3, Split Package 2. Cross-module moves: **40**.

**Established facts:**
1. **Effort estimates are absent in Apache** (0/345). The field is unused by the process; scaling
   cannot recover it. This invalidates the estimate-based framing for OSS corpora like Apache.
2. **Traceability is excellent but monorepo-sensitive.** Hadoop cites an issue key in **92.3%** of
   commits — but only when all subproject keys are matched (HADOOP/HDFS/YARN/MAPREDUCE + the
   later-separated HDDS/Ozone/Submarine). A single-`HADOOP`-key probe misleadingly reads 26%.
3. **The structural-review signal is minable** (via the githubbot PR relay) but sparse: of ~1,810
   substantive comments across episode tickets, only 75 contain any structural keyword.

## 3b. PRIMARY FINDING — architectural refactorings are a distinct, higher-friction class

A between-group comparison with a proper control: **323 architectural** vs **400 ordinary**
refactoring tickets (medians; Mann–Whitney U). Chart: `figures/arch_vs_ordinary.png`.

| Measure | Architectural | Ordinary | p |
|---|---|---|---|
| Review discussion (comments) | 14 | 11 | 0.00043 |
| **Triage latency** (days in "Open" before pickup) | **4.6** | **2.1** | 0.0016 |
| Resolution time (days) | 30.2 | 15.5 | 0.00028 |
| Distinct participants | 3 | 3 | 0.18 (n.s.) |

Architectural refactorings draw more review discussion, wait ~2× longer to be picked up, and take
~2× longer to resolve — while engaging the same small core of maintainers (more back-and-forth, not
more people). **Triage latency is the load-bearing result:** it is measured *before* any discussion
begins, so it is not an artifact of discussion volume (the confound that undermines the resolution
comparison — see §6). Architectural work is measurably harder to take on. This is the study's positive
finding and the recommended headline for the proposal.

Caveats: descriptive/associational; groups not matched on module, priority, contributor, or time
period; effect sizes modest though consistent and significant; resolution-time gap partly reflects
discussion volume (hence the emphasis on triage latency).

## 4. Measurement validity: the keyword signal is weak

A first-pass codebook labeling (single rater, applying `codebook.md`) of 40 comments — 20 that the
keyword filter flagged, 20 it did not:

| Bucket | Structural | Incidental | Style/correctness |
|---|---|---|---|
| Keyword-flagged (n=20) | **5** | 5 | 10 |
| Keyword-missed (n=20) | **1** | 1 | 18 |

→ **Keyword precision for "structural" ≈ 25%**; miss rate ≈ 5% (noisy at n=20). Most keyword hits are
approvals ("nice refactor") or work-planning ("split into subtasks"), not design arguments. The naive
62% F2 rate is inflated; the operational figure was set conservatively to **31%** (episodes with ≥3
structural keyword mentions). Not yet dual-rated (no Cohen's κ).

## 5. Candidate outcome result (before scrutiny)

Splitting the 345 episodes by F2 (strong ≥3 structural mentions):

| Group | n | Median time-to-resolve | Median review size (comments) |
|---|---|---|---|
| Structural review | 106 | 67 days | 30 |
| Other | 239 | 23 days | 10 |

- Kaplan–Meier / **log-rank p = 0.0001**.
- Cox controlling for change size (log refactoring count, log files touched, log churn):
  F2 hazard ratio **0.66 (alone) → 0.69 (size-adjusted), p = 0.003**. HR < 1 ⇒ slower resolution.
  Appeared robust to change size.

## 6. **Retraction: the result is a discussion-volume confound**

Structural episodes also have far more review comments (median 30 vs 10; correlation of F2 with
log-comment-count = 0.52). Adding discussion volume as a covariate:

| Cox model (n=330, events=327) | F2 hazard ratio | 95% CI | p |
|---|---|---|---|
| A. F2 alone | 0.66 | [0.52, 0.84] | 0.0006 |
| B. + change size | 0.69 | [0.55, 0.88] | 0.0029 |
| **C. + discussion volume (log comments)** | **1.10** | **[0.83, 1.46]** | **0.51** |

- In model C, **discussion volume is the real predictor**: HR = 0.70 per log-comment, **p ≈ 1×10⁻⁹**.
- Volume-independent test (structural *density* = structural comments ÷ total comments, controlling
  for volume): **HR 1.50, p = 0.26 — also null.**

**Conclusion:** the candidate "structural review → slower resolution" association is explained by
*how much* was discussed, not by the *structural nature* of the discussion. Once volume is
controlled, no structural-specific effect on resolution time remains, and structural density adds
nothing. The result does not stand.

**Important framing:** the hypothesis is **untested, not disproven.** The keyword signal is only 25%
precise and is mechanically entangled with volume (a ≥3-mention threshold requires many comments), so
it *cannot* separate structural content from discussion quantity. A validated, volume-independent
structural measure is required to test the hypothesis at all.

## 7. What is / isn't established

**Established:** (a) **architectural refactorings are a distinct, higher-friction class** — more
review, ~2× longer triage, ~2× longer resolution than ordinary refactorings, with triage latency as
volume-independent evidence (§3b); (b) estimate framing fails on Apache; (c) traceability excellent
(99%, multi-key); (d) review discussion is minable via PR relay; (e) discussion volume predicts
resolution time (partly mechanical); (f) the keyword structural signal is 25% precise and
volume-confounded.

**Not established:** whether structural review discussion, *as such* (vs. discussion volume), adds
friction. No structural-specific effect survives volume control with the current keyword measure —
untested rather than disproven (needs a validated, volume-independent signal).

## 8. Threats to validity

- Association, not causation; unmeasured confounders (module criticality, contributor experience,
  priority, issue type) beyond size and volume.
- Cycle-time ≠ effort (includes idle waiting); only 3/330 episodes censored, so the survival framing
  is barely exercised (≈ a regression on log-duration would be similar).
- F2 is a heuristic (25% precise), single-rater, no κ.
- Non-independence: 349 episodes → 323 tickets (clustering unmodeled).
- Cox proportional-hazards assumption not formally checked (no Schoenfeld test).
- External validity: one project, one release-line window (v3.1–v3.4), ~90% coverage.

## 9. Open questions and candidate directions (for the proposal)

1. **Does a validated, volume-independent structural signal carry any effect beyond discussion
   volume?** This is now the crux. Requires dual-rater codebook (κ), quality-based not count-based,
   then re-running model C with that signal. May be null.
2. **Is the outcome the right one?** Consider effort proxies from the Jira changelog (time in
   "In Progress", status-transition timing), or rework signals (reopened tickets, reverts, patch
   iterations, review rounds) instead of raw cycle-time.
3. **Cleaner comparative design:** architectural vs. non-architectural refactorings — do architectural
   ones attract more review / take longer? A built-in control group may be more tractable than the
   within-episode split.
4. **Generality:** replicate on Kafka / HBase / Camel.
5. **Theory:** ground in literature on refactoring effort, code review, and architectural/technical
   debt; position within the broader RQ2 (human factors) / RQ3 (survival modeling) arc.

## 10. Reusable assets (methodological contribution)

- Fault-tolerant, parallel refactoring-mining pipeline that survives tool pathologies at scale
  (`scripts/run_rm_safe.sh`, `run_rm_parallel.sh`).
- PR-review-discussion recovery from Jira via bot-relay, no GitHub credentials (`pr_review_signal.py`).
- Monorepo-aware traceability probe (`citation_rate.py`).
- Full reproducible log (`SLICE_LOG.md`); data artifacts committed (`*_all.json`, `cox_dataset.json`,
  `episode_outcomes.json`).

## 11. One-paragraph honest abstract

> On 8,919 Apache Hadoop commits we detected 349 architectural refactoring episodes, 99% traceable to
> Jira. Compared against 400 ordinary refactoring tickets, architectural refactorings draw more review
> discussion (14 vs 11 comments, p=0.0004), wait ~2× longer to be picked up (4.6 vs 2.1 days in
> triage, p=0.002), and take ~2× longer to resolve (30 vs 15 days, p=0.0003), while engaging the same
> small core of maintainers — establishing architectural refactoring as a distinct, higher-friction
> class of change; triage latency, measured before any discussion, provides volume-independent
> evidence. The originally assumed effort signal (estimates) is absent in Apache (0%). A separate
> within-episode signal (structural review discussion → slower resolution; Cox HR 0.69, p=0.003) was
> retracted as a discussion-volume confound (HR 1.10, p=0.51). The contribution is a reproducible
> pipeline, the feasibility findings, a positive between-group finding, and a well-scoped design for
> testing whether structural content adds friction beyond discussion volume.
