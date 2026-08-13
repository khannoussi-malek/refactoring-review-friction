# 1. Introduction

Empirical work on architectural change reads a project's own records — commit
messages, issue trackers, pull requests — and assumes the record is a reasonably
faithful trace of the work. Studies of refactoring motivation, of technical-debt
repayment, of architectural erosion and of review effort are all built on that
assumption, and it is rarely stated, still more rarely measured. This paper
<!-- only: preprint -->
measures it, in three record channels across two ecosystems, and finds it false in
every channel tested.
<!-- /only -->
<!-- only: msr2027 -->
measures it on 38 Apache projects, and finds that the record traces the work far
less often than a ticket-anchored design needs, for a reason that is arithmetic
rather than cultural.
<!-- /only -->

<!-- only: msr2027 -->
**How we arrived at a methods paper.** This study set out to measure
signal-to-action latency: what in a project's records precedes a decision to
restructure code. Six operationalisations were tried and closed, and Figure 1
records them. The sampling frame turned out to be the finding, and this paper
reports that rather than the latency result it went looking for.

<!-- /only -->

<!-- only: preprint -->
**How we arrived at a methods paper.** The study began as an attempt to measure
signal-to-action latency: what, if anything, in a project's records precedes the
decision to restructure code. Six operationalisations were tested and closed, each
with a named cause — a Cox model on review discussion, retracted as a
discussion-volume confound; module centrality as a predictor of hesitation, null
once the module tier is controlled; maintainer concentration, collinear with
module size at rho = −0.86; an abstraction-versus-relocation split, ×1.54 [0.97,
2.43] fully adjusted; a decade-long process-improvement trend that holds to 2019
and dissolves after 2020; and a portable module-tier rule that replicated 0 of 3
in a held-out corpus. The details are in the replication package and are not
results of this paper. What survived is the observation that made all six fragile:
**the sampling frame itself is the finding.** We could not assemble a corpus that
could carry any of those tests, and the reasons why turned out to be measurable,
general, and absent from every published sampling tool.

**The core measurement.** Traceability between issues and commits is published one
way and needed the other way. The **commit-side rate** — what fraction of a
project's commits cite a ticket — is what the literature reports and what
selection criteria use. The **ticket realisation rate** — what fraction of a
project's tickets ever receive a citing commit — is what a ticket-anchored study
actually depends on, because such a study samples tickets and then looks for the
work. The two diverge sharply and in a direction that flatters the corpus. Apache
Hive cites a ticket in **97.0%** of its 18,213 commits — nearly perfect by any
selection criterion — and realises **55.8%** of its 29,635 tickets (TRR_live).

**And most of that gap turns out to be arithmetic.** A commit that cites a ticket
adds at most one *new* distinct ticket, so the ticket-side rate is capped at
`commit-side × commits / tickets`. Under the live measurement ceiling_live binds
for every eligible project, running 13.7–81.6%, and every one of them reaches
80–95% of it. Under the frozen snapshot three ceilings exceed 100% and stop
binding (§4.2, Table 3). What reads as a
discipline gap is mostly a tracker accumulating tickets faster than a repository
accumulates commits — which is a fact about the two artifacts, not about the
people using them, and which no published linkage rate exposes.

<!-- /only -->


**Contributions.** Stated against what is already published rather than against an
assumed gap. We make **no first-to-measure claim**: Rath & Mäder's SEOSS 33 [@rath2019seoss]
publishes per-project linkage as an explicit table column for 33 projects, and
Rath et al. (ICSE'18) [@rath2018traceability] publishes both directions for six. An earlier version of
this work claimed novelty on that ground; the claim was checked, found false, and
withdrawn (§2.1).

1. **A pre-registered numeric eligibility bar, applied before any outcome, with
   reported attrition and the rejected candidates named.** Prior work selects on
   trace links informally — "a project shall continuously capture trace links",
   "each largely followed the practice of tagging commits with issue IDs" — and
   reports rates afterwards. Neither states a threshold, an attrition count, or
   which candidates were rejected. Ours is fixed at 0.80, committed before any
   project was cloned, and never moved.
2. **A population finding: 12 of 38 pass, and no project outside one ecosystem
   clears the bar.** The best outside it, James, reaches 74.8%, against a median
   of 63.6% across all 38 and 44.8% across the 26 rejected. The ecosystem label
   is a hand classification and we say so: two measured generational variables
   were tested in its place and neither separates the corpus as well (§4.1).
   SEOSS's own table contains the ingredients —
   Apache projects at the top, JBoss at the bottom — but the inference is not
   drawn there.
3. **Both reference channels measured together.** Counting GitHub-issue
   references alongside Jira keys is what shows that the bar selects a *tracker*
   rather than a discipline: seven of the dropped projects cite GitHub issues in
   more than half of their commits.
4. **The arithmetic ceiling that bounds the ticket-side rate**, and the
   decomposition of that rate into a ceiling set by commits-per-ticket and a
   residual that measures citation discipline. In this corpus the residual is
   nearly constant, which is what the divergence actually consists of.
5. **The ticket-side rate measured across the whole probe rather than only the
   survivors** — including the 26 projects that failed the commit-side bar. A
   strong positive association between the two rates is ruled out; a null is not
   established, and the live and frozen measurements disagree in sign
   (`paper/DIRECTION_TENSION.md`).
6. **A six-mode taxonomy of the ways a project silently fails to support an
   issue-linked study**, three of them disqualifying and three of them producing a
   plausible wrong number rather than an error.
<!-- only: preprint -->
7. **A second ecosystem and two further channels**, which is what makes the
   result more than an Apache artifact: in a TypeScript corpus, 3 of 96
   architectural commits mention refactoring, 7% link an issue, and 69% never
   pass through code review at all.
<!-- /only -->

<!-- only: preprint -->
**What this paper is not.** It is not a study of refactoring friction; the
exploratory Hadoop results live in the replication package and none of them is
claimed here. It does not propose the successor design the corpus limits point
towards. And it does not argue that the projects it drops are badly run — a
project that moved to GitHub Issues is not failing at anything except a
convention this kind of research happens to need.

<!-- /only -->
