# 4. Results

## 4.1 Corpus eligibility is the binding constraint

**Twelve of 38 Apache candidates clear the pre-registered 0.80 commit-side bar,
and all twelve are Hadoop-ecosystem** (Table 1;
`figures/eligibility_funnel.png` panel A). The bar was fixed before any project
was cloned and never moved.

No project outside the Hadoop ecosystem clears it. The best of them, James,
reaches **74.8%**. The spread runs from ShardingSphere at 0.01% to Ozone at
98.3%, with a median of **63.6%** across all 38 and **44.8%** across the 26 the
bar rejected. Ecosystem family is a hand classification and not a field in the
probe, so that first sentence is a reading of the data rather than a measurement
of it; the numbers around it are measurements. Ecosystem adjacency is not sufficient
either — **Parquet fails at 29.1% and Accumulo at 43.0%**, both squarely inside
the Hadoop dependency graph. What the bar selects is a specific commit-hygiene
convention, not a dependency relationship and not a quality level.

**The drop reasons are measured rather than inferred**, because both reference
channels are counted per repository. Nine projects are dropped with
`github_issue_references_dominate`, meaning the GitHub-issue count exceeds the
Jira-key count in that repository — ShardingSphere carries 30,746 GitHub-issue
references against 5 Jira keys in 49,111 commits. Four fall in
`below_bar_narrowly` (≥70%) and the remainder in `low_commit_message_hygiene`.
The industry-donated projects are the sharpest case: ShardingSphere 0.01%,
SkyWalking 0.3%, Pinot 5.2%, RocketMQ 5.7%, Dubbo 11.0%. They never adopted the
Jira-citation convention, and the attrition is therefore concentrated in the
newest projects — which is the direction that matters for anyone building a
corpus now.

## 4.2 The channel that is published is not the channel that is needed

This is the paper's strongest single measurement.

Across the same twelve projects, the **commit-side rate runs 82.6–98.3%** while
the **ticket realisation rate runs 12.0–69.0%, with none above 69.0%**
(Definition 1 and Definition 2, §3.1; Table 1).

> **Apache Kylin cites a ticket in 83.9% of its commits and 12.0% of its tickets
> are ever cited by one.** It clears any commit-side bar one would think to set,
> and leaves seven of every eight tickets in its tracker with no commit at all.

Sqoop is the second case at 82.6% against 21.2%. At the other end Knox, which
clears the bar by the smallest margin among the high group at 84.3%, has the
*best* ticket realisation rate in the corpus at 69.0% — the ordering of the two
rates is not even monotone within the passing twelve.

The consequence for design is direct. A study that samples commits and looks up
their tickets can work in any of these twelve. A study that samples tickets and
looks for the work will, in Kylin, discard seven eighths of its sampling frame
before it starts — and will not know it has done so, because the number reported
in the literature and used for selection is the other one.

## 4.3 The divergence is a property of the population, not of the survivors

Reporting §4.2 on the twelve that passed leaves the obvious objection open: the
range 12.0–69.0% is *within-passing variation*, and says nothing about the 26
projects below the bar, whose ticket realisation rates were never measured. That
objection is answered here by measuring all 38.

**Method.** The ticket realisation rate needs a tracker snapshot. Re-reading the
live tracker for 26 more projects would have dated those denominators weeks after
the twelve already measured, so the extended computation instead takes its
denominators from the frozen public Jira corpus and aligns numerator and
denominator in issue-number space (§3.1.3). **The estimator is validated before it
is used**: run against the live denominators for the twelve projects where the
exact rate is already known, it reproduces that rate to a **mean absolute error of
{VALIDATION_MEAN}pp and a worst case of {VALIDATION_MAX}pp**.

**Result.** {EXTENSION_RESULT}

## 4.4 The measure replicates independently across corpora seven years apart

The commit-side rate is not a novel measure, and its agreement with an
independently constructed dataset is the reason to trust the probe. Four of the
five projects overlapping SEOSS 33 agree within **3.3pp** on corpora seven years
apart: Hadoop 97.13% → 97.8%, Hive 96.34% → 97.0%, HBase 90.06% → 92.5%,
ZooKeeper 87.12% → 90.4%.

Flink differs by **24.1pp** (41.98% → 66.0%). This is almost certainly scope
rather than error — their snapshot holds 12,419 commits against our 38,219, so we
cover a decade in which Flink's citation practice could have changed. **The
truncation check that would confirm it — re-probing Flink's first 12,419 commits —
has not been run**, and the explanation is stated here as untested.

## 4.5 Convergent invisibility across three channels and two ecosystems

Table 2 assembles what each record channel shows in each ecosystem. **Every cell
is a different quantity with a different denominator, and no statistic is computed
across them.** They are assembled because they agree in direction while being
methodologically independent, and independent agreement is the only kind of
evidence a single-corpus critique cannot absorb.

In the TypeScript corpus: **3 of 96** architectural commits mention refactoring in
their message (93 are silent); of ten commits whose message claims refactoring,
**seven are not architectural**; **7%** link an issue, against 7% for other
refactoring and 10% for non-refactoring commits — architectural change is no more
likely to be tracked in advance than anything else and slightly less; and **30 of
96 = 31%** pass through a pull request, leaving **69% unreviewed**.

Two cells are absences of different kinds and the distinction is load-bearing.
**Apache / pull request is a structural `n/a`**: Hadoop's review record lived in
Jira via the githubbot relay during the period studied, so there is nothing to
measure and no amount of mining creates it. The nearest Jira-side proxy
demonstrates the point by terminating rather than thinning — architectural tickets
carrying a CI verdict run 145 of 150 (96.7%) up to 2018, 66 of 130 (50.8%) in
2019–21, and **0 of 43 (0.0%) from 2022**. **Apache / commit message is a gap in
this study**, not a property of Apache: the Hadoop architectural corpus was built
by AST-level detection and the message-text channel was never instrumented against
it, so no figure comparable to the TypeScript column's 3.1% exists here. It is
computable in principle and is the most obvious extension of the table.

## 4.6 The standard sampling frame cannot express the criterion

GHS is the standard sampling tool for MSR studies and indexes **735,669
repositories** with **35 fields** per record. Only `totalIssues` and `openIssues`
touch issues at all, and both are GitHub-issue counts. There is no field for
issue-tracker type, external tracker usage, issue–commit linkage, traceability, or
commit-message convention; the one adjacent feature, filtering by issue label, is
described in the paper itself as still under development.

A researcher sampling with GHS therefore gets stars, commits, contributors and
license, and discovers post hoc that 26 of 38 candidates are unusable. That is
what happened here, and §5 is the taxonomy of the ways it happens.
