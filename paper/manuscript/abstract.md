# Abstract

Empirical studies of architectural change read a project's own records and assume
the record traces the work. We measure that assumption in three record channels
across two ecosystems and find it fails in every one.

We probed 38 Apache projects against a traceability bar of 0.80, pre-registered
before any project was cloned and never moved. **Twelve passed, and no project
outside the Hadoop ecosystem cleared the bar** — the best reaching 74.8%, against
a median of 63.6% across all 38 and 44.8% across the 26 rejected. The ecosystem
label is a hand classification; we tested two measured generational variables in
its place and neither separates the corpus as well, so the label is reported as a
judgment rather than a finding. The channel the literature publishes is
not the channel a ticket-anchored study needs. The **commit-side rate** — what
fraction of commits cite a ticket — runs 82.6–98.3% across the eligible twelve,
while the **ticket realisation rate** — what fraction of tickets ever receive a
citing commit — runs 12.0–69.0%. Apache Hive cites a ticket in 97.0% of its
18,213 commits and realises 55.8% of its 29,635 tickets.

**Most of that gap is arithmetic, not discipline.** A citing commit adds at most
one new distinct ticket, so the ticket-side rate cannot exceed
`commit-side × commits / tickets`. That ceiling binds for all twelve eligible
projects, ranging 13.7–81.6%, and every project reaches 80–95% of it: the 5.8×
spread in the ticket-side rate is a 6.0× spread in the ceiling and only a 1.19×
spread in what is left. A tracker accumulates tickets faster than a repository
accumulates commits, and below one commit per ticket the two rates are not
commensurable.

Extending the computation to all 38 projects, including the 26 the bar rejected,
the two rates show **no detectable association** — Spearman rho = −0.010 over the
33 with a usable denominator, 95% CI [−0.35, +0.34], and the study can detect
|rho| ≥ 0.47 at 80% power. **A strong positive relationship is ruled out; a null
is not established.** Median realisation is 52.6% among projects the bar accepted
and 53.2% among those it rejected, and the highest rate in the probe (84.8%)
belongs to a project rejected at 36.0% commit-side. On the twelve projects
measured exactly and live the same correlation is **+0.518**, and we report the
disagreement rather than resolving it.

The same invisibility appears in a second ecosystem and two further channels: in a
TypeScript corpus, 3 of 96 architectural commits mention refactoring, 7% link an
issue, and 69% never pass through code review — and the 31% that do are five times
larger and four times more abstraction-heavy than those that do not, so the
visible minority is not a random sample of the whole.

We give a taxonomy of six mechanisms by which a project silently fails to support
an issue-linked study. Three are disqualifying — the tracker is displaced by
GitHub Issues, no source repository exists, the tracker is downstream of the
repository. Three are **silent**: a convention that changed mid-history, a monorepo
needing multi-key matching, and a cited key with no project record in the tracker
each yield a plausible low number rather than an error. A single-key probe reads
Hadoop at 26.2% where a seven-key probe of the same commits reads 97.8%, and
nothing in the first result signals the key set is wrong.

**None of the six is expressible in any published sampling frame.** GHS indexed
735,669 repositories when it was published in 2021, and a record carries 35
fields today, of which only two touch issues and both are
GitHub-issue counts. Project eligibility for issue-linked research cannot be
established from metadata; it requires reading commit messages from the project
itself, per project, before any outcome is measured.

We make no first-to-measure claim: per-project linkage rates are published by
SEOSS 33 for 33 projects and by Rath et al. (ICSE'18) for six. What is new is a
pre-registered numeric bar with reported attrition and named rejections, both
reference channels counted together, the ticket realisation rate named and
measured across a whole probe rather than its survivors, and the six-mode
taxonomy.

