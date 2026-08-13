# RQ1 on Apache Hadoop — decision memo

> **Superseded 2026-08-08.** This document records the state of the work as of
> its date. Several of its conclusions were later retracted or corrected. The
> current account is `README.md` §3 and §4; the retraction record is
> `PROJECT_STATE.md` §2.
>
> Specifically: the one-line finding below — *harder to build, not harder to
> merge* — was **withdrawn on 2026-07-25** (`4b8c3af`); the review-phase half is
> p=0.61 fully adjusted. The body is left exactly as written, per the 07-25
> decision not to rewrite dated working logs (`PROJECT_STATE.md` §2, `eee902f`).

**For:** Maalej group meeting · **From:** independent pre-PhD study · **Date:** 2026-07-22
**One line:** Feasibility is settled and a defended finding exists — architectural refactorings are
harder to **build**, not harder to merge, and they are the one class of work a decade of tooling did
not make cheaper. Three decisions needed, all about *what to do next*, not whether it works.

*(Supersedes the 2026-07-19 week-1 memo, whose open questions — which signal, module depth, F2
threshold — are now settled or overtaken. That memo recommended the review-discussion signal as
primary; that recommendation was subsequently **retracted**, see §3 below.)*

---

## 1. Where the study stands

Ran on **8,919 Hadoop commits** (v3.1.0→3.4.3) → 51,861 refactorings → **349 architectural episodes**
(323 tickets), against a **400-ticket ordinary refactoring control**.

| Filter | Result | Verdict |
|---|---|---|
| Traceability (commit → ticket) | **99%** (345/349) | ✅ non-issue |
| Effort estimate present | **0%** (0/345) | ❌ dead — a property of Apache's process |
| Structural review discussion | 31–62%, keyword rule only **25% precise** | ⚠️ needs κ before use |

**The estimate framing is dead and is not coming back.** That conclusion has held up.

## 2. The finding, and why it is defensible

**Friction is specific to *abstraction*, and it sits in *construction*.** Extracting
interfaces/superclasses/classes is ~2.5× slower to start and ~2× slower to resolve than moving or
renaming code — which is itself no harder than ordinary work.

Decomposing the status changelog localises it: architectural work is **~4× slower to produce a patch**
(3.86 vs 1.00 days) and **~4× longer in logged active coding time** (4.87 vs 1.13 days, p=0.037), yet
is **merged as fast as ordinary work** (8.5 vs 8.4 days, n.s.).

That last row is the important one. Time logged `In Progress` is time someone is demonstrably
working, so it **cannot** be volunteer queueing. This bounds the open-source confound that would
otherwise limit every timing result to ASF-specific behaviour.

**Second finding — a trajectory.** Across the decade (measured on a git-derived clock, because Jira
status hygiene collapsed 93%→16% at the GitHub migration), ordinary refactoring got steadily faster
(rho=−0.21, p=3e-05) while architectural refactoring did not improve at all (rho=+0.04, p=0.45).
Difference-in-differences interaction **+0.20, p=0.003**. A decade of CI and review tooling made
routine change cheaper and left structural change where it was.

## 3. What we tested and rejected — please scrutinise this part

Four candidate explanations were built and then failed against our own data:

- **Structural review discussion → slower resolution:** HR 0.69 (p=0.003) → **HR 1.10 (p=0.51)** once
  discussion volume is controlled. **Retracted.** (This was the week-1 memo's recommended signal.)
- **Blast radius** (touching a depended-upon module invites hesitation): tested against Hadoop's Maven
  graph, 117 modules. Centrality does not predict triage (p=0.33); the raw association runs *negative*.
  **Refuted.**
- **Maintainer concentration** as the explanation for the slow module tier: collinear with module size
  (rho=−0.86), dies under a size control. **Failed to establish.**
- **"Friction concentrates in `hadoop-common`"**: that 39.1-day figure was a Jira-*prefix* aggregate,
  62% of it cloud-connector tickets. `hadoop-common` alone is 24.8 days. **Corrected.**

The abstraction finding survived five controls (change size, discussion volume, contributor
experience, module tier, era), the full-workflow restriction, and a phase decomposition while every competing
explanation died. That asymmetry is the argument, and it is the part most worth attacking in the
meeting.

## 4. Decisions needed

1. **Which finding leads the proposal?** The mechanism result (abstraction friction is in
   construction, and is intrinsic rather than an OSS artifact) or the trajectory result (structural
   work is the one category not getting cheaper). The trajectory is the more striking thesis
   statement; the mechanism is the better-defended claim. *My lean: mechanism leads, trajectory as the
   motivating stake.*
2. **Second corpus — commercial contrast or OSS replication first?** These answer different
   objections. A commercial codebase separates intrinsic from OSS-specific effects (the §2 caveat);
   OSS replication on Kafka/HBase/Camel is what breaks a **collinearity we cannot break in one
   project** — "peripheral module" (small, few-authored, low-centrality, vendor-specific) is a single
   variable in Hadoop. Both now carry pre-registered predictions. *Ask: is an industrial partner
   realistically available? Pseudonymisation tooling is already built.*
3. **Is a second rater available for the κ validation?** The structural-discussion signal is 25%
   precise and cannot be used until dual-rated. A 40-comment labelling set is ready
   (`codebook_labeling.md`). This is a **people** blocker, not a compute one — it needs someone in the
   group, or it stays out of the full study.

## 5. Caveats I would not want you to hear from someone else first

- Descriptive/associational; single project; groups not matched on module or time.
- Survivorship bias toward changes that landed — *abandonment* is not observable here.
- **Three independent measurement channels** (Jira status comparability, status hygiene, CI verdict
  visibility) all decay at Hadoop's 2019–20 GitHub migration, so several results are era-bounded. This
  is a reusable warning for anyone mining ASF Jira across that boundary.
- 26% of episodes could not be mapped to a Maven module — Ozone and Submarine left the repository.
- `In Progress` is logged by only ~25% of tickets, so the active-coding result rests on that subset.

## 6. Reproduce

`research_prospectus.md` (2-page write-up) · `results_dossier.md` (everything, including what was
retracted) · `proposal_summary.md` (with figures) · `SLICE_LOG.md` (every command) · `scripts/`
(pipeline + each mechanism test, each with a self-check).
