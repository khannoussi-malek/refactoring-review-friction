# Abstract

Empirical studies of architectural change read a project's own records and assume
the record traces the work. We measure that assumption in three record channels
across two ecosystems and find it fails in every one.

We probed 38 Apache projects against a traceability bar of 0.80, pre-registered
before any project was cloned and never moved. **Twelve passed, and all twelve are
Hadoop-ecosystem**; no project outside that ecosystem cleared the bar, the best
reaching 74.8%, against a median of 63.6% across all 38 and 44.8% across the 26
rejected. The channel the literature publishes is
not the channel a ticket-anchored study needs. The **commit-side rate** — what
fraction of commits cite a ticket — runs 82.6–98.3% across the eligible twelve,
while the **ticket realisation rate** — what fraction of tickets ever receive a
citing commit, a quantity we name and define here — runs 12.0–69.0% and reaches
69.0% at best. Apache Kylin cites a ticket in 83.9% of its commits and 12.0% of
its tickets are ever cited by one. Extending the ticket-side computation to all 38
projects, including the 26 the commit-side bar rejected, shows the two rates are uncorrelated: Spearman rho = −0.010 over the 33 projects with a usable denominator, with a median of 55.5% among those the bar accepted and 53.2% among those it rejected. The highest ticket realisation rate in the probe, 84.8%, belongs to a project the bar dropped at 36.0% commit-side. The commit-side rate carries essentially no information about the rate a ticket-anchored study depends on.

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
Hadoop at 26.2% where the true rate is 92.3%, and nothing in that result signals
the key set is wrong.

**None of the six is expressible in any published sampling frame.** GHS indexes
735,669 repositories with 35 fields, of which only two touch issues and both are
GitHub-issue counts. Project eligibility for issue-linked research cannot be
established from metadata; it requires reading commit messages from the project
itself, per project, before any outcome is measured.

We make no first-to-measure claim: per-project linkage rates are published by
SEOSS 33 for 33 projects and by Rath et al. (ICSE'18) for six. What is new is a
pre-registered numeric bar with reported attrition and named rejections, both
reference channels counted together, the ticket realisation rate named and
measured across a whole probe rather than its survivors, and the six-mode
taxonomy.

---

*Drafting note, to be deleted before submission.* Word budget: MSR technical
track — check the call. Every number here appears in `paper/numbers.md` with a
script and a commit. The §4.3 figures are filled in.
