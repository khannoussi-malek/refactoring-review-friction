# RQ1 anchor history — four anchors, three closed causes, one untested

RQ1 asks which observable signals precede architectural refactorings and how long
they sit unacted upon. The *signal* has been reoperationalised four times. This
file lists all four in order with the named cause and the commit that recorded
it, so the sequence is auditable without re-reading the decision log.

Causes are transcribed from `PROJECT_STATE.md` §2, `README.md` §4 and
`results_dossier.md` §10. No cause is added here that is not already recorded
there.

## The four anchors

| # | anchor | status | named cause | recorded in |
|---|---|---|---|---|
| 1 | **Effort-estimate overruns** in Jira | closed | **Too thin, not absent.** 2.557% Apache-wide (25,949 / 1,014,926); 1.449% in the Hadoop corpus (713 / 49,201); **0 of 323** architectural tickets, expected 4.7, P≈0.009 under a naive binomial. Estimate-rich and traceable projects are near-disjoint: 3 of 27 clear both | `eee902f` (`estimates_by_org.json`, `paper/estimate_field_schema.md`); intersection `63f4231` (`paper/intersection.json`) |
| 2 | **External-wrapper tier rule** (vendor share ≥ 0.40) | killed | **0 of 3 testable projects replicate.** Hive p=0.210, Drill p=1.000 in the *wrong direction*, Kylin p=0.310. Coverage failure on top: the rule flagged 0 modules in HBase and 0 in Phoenix, so 2 of 5 yielded no prediction at all. The 0.40 threshold was **not** lowered afterwards although doing so would have rescued HBase (max 0.33) and Phoenix | `48caf14` (`replication/REPLICATION.md`, `replication/*.test.json`); v2 abandoned `0216b64` (`wrapper_rule_v2_dev.json`) |
| 3 | **SATD interval** — self-admitted technical debt comment → architectural refactoring of the annotated entity | superseded, **never started** | **No test was run and none failed.** It stayed gated on Task 18 (whether an entity survives Move Class / Move Package) and on external judgement of a novelty margin resting on three simultaneous legs — SATD-anchored *and* entity-level *and* refactoring-detected — any one of which collapses it into existing work. A competitor doing survival analysis on architectural-debt repayment appeared in May 2026 (arXiv 2605.16133) | recorded `5b50ef1` (`paper/SATD_NOVELTY.md`); superseded `PROJECT_STATE.md` §2 row 07-26 |
| 4 | **Violation-symptom interval** — architecture violation symptom raised in code review → a later, separate architectural refactoring of the flagged entity | **current**, untested | — | `PROJECT_STATE.md` §2 row 07-26; this file |

Anchor 3 is the one that must not be misread. It is **superseded unstarted**, not
falsified. Nothing in this repository establishes that the SATD interval is
unmeasurable; it was set down before it was tested. Anchors 1 and 2 carry
measured causes and anchor 3 does not.

## What sits between anchors 1 and 2 and is not an anchor

The **F2 structural-review signal** was tested and retracted inside anchor 1's
era and is not a fifth anchor: it was a candidate *predictor within* episodes,
not a reoperationalisation of the RQ1 signal.

> Apparent effect (Cox HR 0.69, p=0.003, robust to change size) **collapsed**
> when discussion volume was added (HR **1.10, p=0.51**). Discussion volume is
> the real predictor (HR 0.70 per log-comment, p≈1e-9); structural *density* is
> null (p=0.26).
> — `results_dossier.md` §10, recorded `b8d1476`

It matters here because anchor 4 also reads code-review comments, which is why
the next section exists.

## Why this is not the retracted F2 signal

**These are claims to be tested, not established.** Every one of the three is a
design intention. None has been measured, and the F2 retraction is the reason the
burden sits this way round: a review-comment signal has already collapsed once in
this repository, so the differences have to be demonstrated rather than asserted.

**1. The construct is categorical and externally validated, not a keyword count.**
F2 fired on any match of a 17-alternative regex over comment text
(`scripts/pr_review_signal.py:32-35`). Single-rater labelling put that rule at
**≈25% precision** (5 of 20 flagged comments genuinely structural) with a **≈5%**
miss rate (`codebook_results.md`), i.e. it over-counts roughly fourfold. Anchor 4
intends instead a categorical *architecture violation symptom*, taken from an
external labelling scheme rather than invented here.

*Untested here, and the gap is specific:* **no external violation-symptom scheme,
labelled dataset, codebook or detector is present anywhere in this repository.**
`codebook.md` is the only comment codebook on disk, it is the F2 codebook, its
three labels are STRUCTURAL / INCIDENTAL / STYLE-CORRECTNESS, and it has **never
been dual-rated — no κ exists** (`README.md` §8, plan rule R6). Until an external
scheme is actually obtained and applied, "categorical and externally validated"
describes an intention and the operative instrument on disk is still the 25%
keyword net.

**2. The outcome is an interval, not a hazard on signal presence.**
F2 asked whether the *presence* of structural discussion predicted the hazard of
an episode resolving — signal and outcome measured on the same episode, within
the same review. Anchor 4 asks how long it is from a symptom to a **later,
separate** architectural refactoring of the flagged entity: the outcome event is
a different commit from the one carrying the signal.

*Untested here:* whether such intervals exist in quantity is the entire content
of the feasibility gate (`prereg/RESOLUTION_GATE.md`). If nearly every symptom
resolves inside its own review, there is no interval and anchor 4 fails the same
way anchor 2 did, on measurement rather than on argument.

**3. Discussion volume is a pre-committed control, not a discovered confound.**
Volume killed F2 *after* the effect was reported — it entered as a robustness
check and became the finding (`results_dossier.md` §10). For anchor 4 it is named
in the model before any outcome is seen: `prereg/RESOLUTION_GATE.md` fixes
discussion volume as one of five controls in the eventual Cox model, which is
what sets that gate's event-count requirement.

*Untested here:* pre-committing a control prevents the specific 07-19 failure — a
confound found after publication — and prevents nothing else. It does not make
the structural signal volume-independent. That remains the open question
`results_dossier.md` §11 and `SLICE_LOG.md` both close on: *"a validated,
volume-independent codebook signal is required."* It is still required.

## Scope exception to rule R4

`docs/superpowers/specs/2026-07-30-methods-paper-completion-plan.md` §1 rule R4
reads: *"Do not add analyses, hypotheses, corpora, or statistical tests. No new
project clones. No new RefactoringMiner runs. No new p-values."* The feasibility
gate is an analysis and would be blocked. A narrow exception is recorded in that
plan's §10 execution log, dated 2026-08-01, and is repeated here so it travels
with the anchor:

- **Permitted:** the 20-comment resolution gate, run on **existing local data
  only** — `.jira_cache/` (323 Hadoop tickets), `refminer_all.json`, the
  `hadoop/` clone, `ticket_first_commit.json`.
- **Not permitted:** new corpora, new clones, new RefactoringMiner runs, new
  p-values, any network call.
- **Unchanged:** R1 (the seven held-out projects — the gate touches only Hadoop,
  which is already fully spent, `PROJECT_STATE.md` §4), R2, R3, R5, R6, R7, R8.
- **R6 in particular still binds.** The gate produces a *labelling sheet for a
  human coder*. No bucket in it is assigned by this repository's tooling, and a
  single-rater result cannot become a claim.

The methods paper is unaffected: the gate adds no number to it, and
`paper/manuscript/PROVENANCE_CHECK.md` is not touched.

## Known limitation of the gate corpus

The gate runs on **Hadoop — Java, Jira, `githubbot`-relayed GitHub PR review.**
The anchor as stated targets code review on Gerrit. Hadoop was chosen because it
is the only corpus on disk and no network call is permitted; it is a deliberate
substitution, not an oversight. Two consequences travel with any gate result:

- **No patchset structure.** Gerrit's patchset N → N+1 diff, which is the natural
  operationalisation of "resolved inside the same review", does not exist in
  Hadoop's record. The gate approximates it against the ticket's own merge commit
  (`prereg/RESOLUTION_GATE.md`, bucket (a)).
- **Corpus viability for the real study is decided elsewhere.**
  `paper/RM_LANGUAGE_SUPPORT.md` establishes that RefactoringMiner 3.1.4 as built
  here detects refactorings in Java, Python, TypeScript and Kotlin, and **not in
  C or C++**. OpenStack (Python) is therefore detectable; **Qt (C++) is not**.
  Neither was among the 38 projects probed for traceability
  (`paper/traceability_probe.json`, all 38 `github.com/apache/*`), so neither has
  a measured commit-side rate against the 0.80 bar.
