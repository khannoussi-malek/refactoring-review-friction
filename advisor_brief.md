# RQ1 feasibility on Apache Hadoop — decision memo

**For:** Maalej group meeting · **From:** week-1 feasibility slice · **Date:** 2026-07-19
**One line:** The *estimate* framing of RQ1 is dead on Apache data; the *review-discussion*
framing is alive but selective. Traceability is a non-issue. Decision needed on which signal.

---

## What RQ1 needs, and what we measured

RQ1 links a chain: **architectural refactoring happened → traceable to a ticket → ticket carries a
signal**. We ran that chain on Hadoop over **8,919 commits** (4 release ranges, 3.1.0 → 3.4.3),
detecting refactorings with RefactoringMiner and mining tickets from the public Apache Jira API.

| Filter | Question | Result (n = 345 traceable episodes) | Verdict |
|---|---|---|---|
| **F3** traceability | commit → Jira ticket? | **345/349 = 99%** | ✅ non-issue |
| **F1** estimate | ticket carries an effort estimate? | **0/345 = 0%** | ❌ dead (data gap) |
| **F2** structural review | review discussion argues about structure? | **31%–62%** (see below) | ⚠️ selective |

- **349 architectural episodes** detected (Move/Extract Class, Extract Interface/Superclass, and
  40 cross-module moves + package-level Move/Rename/Merge/Split).
- **F2 is a range, not a point:** 62% of episodes have *some* structural keyword in their review
  discussion; 31% show a *strong* signal (≥3 mentions). The true rate depends on the codebook
  (below) — that is the one open measurement decision.

## The two findings that decide RQ1

1. **Effort estimates do not exist in Apache Jira.** Every one of 345 tickets has an empty estimate
   field; one developer wrote it plainly: *"no actual time allocated to implement it."* No amount of
   scaling fixes this — it is a property of Apache's process. **If RQ1 requires explicit estimates,
   Hadoop (and ASF generally) is the wrong corpus.**

2. **The review signal lives on the GitHub PR, not the Jira ticket** — but Apache's `githubbot`
   mirrors the whole PR review (including inline "commented on code" comments) *into* the Jira
   ticket. So it is minable from the same public API, no GitHub token needed. This is what makes the
   review framing feasible without new infrastructure.

## Recommendation

**Adopt the review-discussion signal as RQ1's primary signal**, with a changelog **cycle-time**
proxy (ticket open→resolve) as the "overrun" measure in place of estimates. Evidence supports it:
99% traceable, signal present in a third to two-thirds of episodes, hundreds of usable episodes
across full history. **Do not** build RQ1 around effort estimates on this corpus.

## The one thing blocking a single number: the codebook

F2 swings from 31% to 62% purely on where we draw *"structural argument"* vs *"incidental keyword."*
A draft codebook + a 40-comment labeling set (real Hadoop review comments) are ready
(`codebook.md`, `codebook_labeling.md`). Two raters + Cohen's κ pins F2 to one defensible number.
Note the signal is genuinely sparse: only **75 of 1,810** substantive comments contain any
structural keyword — so precision of the rule matters a lot.

## Decisions to settle in the meeting
1. **Primary signal:** review-discussion (recommended) vs. estimate-elsewhere vs. cycle-time proxy.
2. **Module-boundary depth** for "architectural" (depth 3/4/5 barely moved episode counts; only the
   cross-module flag changes).
3. **Codebook threshold** for F2 (any-mention vs. strong) — drives the headline rate.

## How to reproduce / method caveats
- Full pipeline + commands: `SLICE_LOG.md`. Parallelised RefactoringMiner (12-core), 90%+ coverage.
- **Coverage caveat:** RefactoringMiner hangs on `*.min.js` dependency-bump commits; those are
  auto-skipped (they contain no architectural refactorings). ~90–99% of each range covered.
- **F2 caveat:** current F2 = keyword heuristic, pending the codebook. Treat 31–62% as bounds.
