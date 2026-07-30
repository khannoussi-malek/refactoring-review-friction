# 1. Introduction

**Status: to write** (writing order 6 — last but one). Write only once the
paper's actual content is fixed.

## What must be here

**The problem.** Empirical work on architectural change reads the project's own
records — commit messages, issue trackers, pull requests — and assumes the record
is a reasonably faithful trace of the work. This paper measures that assumption
and finds it false in every channel it tests.

**The motivating paragraph, and it appears exactly once — here.** We set out to
measure signal-to-action latency: what in a project's records precedes the
decision to restructure code. Six operationalisations were tested and closed,
each with a named cause (`README.md` §4, `figures/eligibility_funnel.png` panel
B). The sampling frame itself turned out to be the finding. **Keep this to one
paragraph. The six killed hypotheses are not results of this paper and must not
reappear in `results.md`.**

**Contributions**, stated against `paper/PRIOR_WORK.md` so the novelty claim is
the surviving one and not the retracted one:

1. A **pre-registered numeric** traceability bar applied before any outcome, with
   reported attrition and the rejected candidates named. Prior work selects on
   trace links informally and reports rates afterwards.
2. The **population finding**: 12 of 38 pass and all 12 are one ecosystem.
3. **Both reference channels measured together** — Jira keys and GitHub-issue
   references — which is what shows the bar selects a *tracker*, not a discipline.
4. The **commit-side / ticket-side divergence framed as a sampling-frame
   warning**, not merely reported.
5. The **six-mode taxonomy**, none of it expressible in any published frame.
6. The **second ecosystem and two further channels**, which is what makes the
   result more than an Apache artifact.

**Do NOT claim first-to-measure.** SEOSS 33 publishes per-project linkage as a
column for 33 projects and Rath et al. ICSE'18 publishes both directions for six.
`paper/PRIOR_WORK.md` records that this claim was checked and withdrawn.
