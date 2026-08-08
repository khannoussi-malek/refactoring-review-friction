# 4. Results

## 4.1 Corpus eligibility is the binding constraint

**Twelve of 38 Apache candidates clear the pre-registered 0.80 commit-side bar,
and every one of them is Hadoop-ecosystem under the classification set out
below** (Table 1, Figure 1). The bar was fixed before any project
was cloned and never moved.

No project outside the Hadoop ecosystem clears it. The best of them, James,
reaches **74.8%**. The spread runs from ShardingSphere at 0.01% to Ozone at
98.3%, with a median of **63.6%** across all 38 and **44.8%** across the 26 the
bar rejected.

**The ecosystem label is a hand classification, and we tested whether a measured
variable does the same work. It does not.** "Hadoop-ecosystem" is not a field in
any dataset; one of the authors assigned it. The natural replacement is project
generation — free metadata, no judgment, and a mechanism, since projects
predating the 2019–20 migration of ASF development to GitHub pull requests had
longer under the Jira-citation convention. Two generational variables were tried
(`scripts/era_separation.py`):

| variable | coverage | separation |
|---|---|---|
| Hadoop-ecosystem label (hand) | 38 of 38 | accuracy **0.868**, recall 1.000, precision 0.706, Fisher p = 2.3 × 10⁻⁶ |
| repository start year (computed from the clones) | 38 of 38 | AUC **0.611**, p = 0.279, best-threshold accuracy 0.711 |
| Apache Incubator graduation date | **24 of 38** | AUC 0.289, p = 0.098, best-threshold accuracy 0.625 |

Neither generational variable separates the corpus as well as the hand label, and
the graduation date is **missing precisely where it would be needed**: four of the
twelve passing projects — Hive, HBase, ZooKeeper and Ozone — entered the ASF as
Hadoop subprojects rather than as incubator podlings and have no graduation date
at all. The free metadata is not free for the group that matters.

**We therefore keep the hand label and mark it as a judgment.** The claim that
survives without it is the measured one: 12 of 38 pass, and the twelve are
concentrated in a way no available metadata field predicts. Reclassifying **Drill**
— which requires neither HDFS nor YARN and is arguably outside the ecosystem —
would falsify the "all twelve" form of the claim and put a non-ecosystem project
above the bar. Kylin and Sqoop are the same shape of exposure; Atlas is not,
because at 78.1% it fails the bar under either classification.

Ecosystem adjacency is not sufficient
either — **Parquet fails at 29.1% and Accumulo at 43.0%**, both squarely inside
the Hadoop dependency graph. What the bar selects is a specific commit-hygiene
convention, not a dependency relationship and not a quality level.

**The drop reasons are measured rather than inferred**, because both reference
channels are counted per repository. Nine projects are dropped with
`github_issue_references_dominate`, meaning the GitHub-issue count exceeds the
Jira-key count in that repository — ShardingSphere carries 30,746 GitHub-issue
references against 5 Jira keys in 49,111 commits. Four fall in
`below_bar_narrowly` (≥70%) and the remaining thirteen in
`low_commit_message_hygiene`. Across all 26 the commit-side rate runs
**0.0%–78.1%** with a median of **44.8%**; the per-project rows are in the
replication package.
The industry-donated projects are the sharpest case: ShardingSphere 0.01%,
SkyWalking 0.3%, Pinot 5.2%, RocketMQ 5.7%, Dubbo 11.0%. They never adopted the
Jira-citation convention, and the attrition is therefore concentrated in the
newest projects — which is the direction that matters for anyone building a
corpus now.

## 4.2 The channel that is published is not the channel that is needed — and the gap is mostly arithmetic

Across the same twelve projects, the **commit-side rate runs 82.6–98.3%** while
**TRR_live runs 12.0–69.0%, with none above 69.0%**
(Definition 1 and Definition 2, §3.1; Table 1). The headline case:

> **Apache Hive cites a ticket in 97.0% of its 18,213 commits, and 55.8% of its
> 29,635 tickets are ever cited by one — TRR_live.** Nearly perfect commit-side hygiene, and
> still nearly half the tracker is invisible to a ticket-anchored design.

**Most of that gap is not a discipline gap. It is the ceiling (§3.1.4).** Hive
has **0.61 commits per ticket**, so at 97.0% commit-side its ticket-side rate
cannot exceed **59.6%** whatever anyone does — and it reaches **0.94** of that.
The pattern holds across all twelve:

* **ceiling_live binds for every one of them**, running 13.7% (Kylin) to 81.6%
  (Ranger) — a 6.0× spread;
* **fill_live is flat**: median **0.89**, range **0.80** (Ranger) to **0.95**
  (Drill), a spread of only **1.19×**;
* so the 5.8× spread in TRR_live is **6.0× ceiling and 1.19× fill**.

**Every ceiling in this section is ceiling_live, and the frozen estimator does
not agree that the bound binds.** Table 3 computes ceiling_frozen against the
frozen Jira snapshot and puts three of the twelve at or above 100% — Ozone
**176.0%**, Ranger **130.4%**, Knox **100.0%** — where a bound above 100% does not
constrain anything. That is not a disagreement about the projects. It is what a
2026 commit window measured against an older tracker produces: the repository
holds more citing commits than the snapshot holds tickets, so the arithmetic
ceiling exceeds one and stops being a ceiling. The two estimators bound different
denominators, and the note accompanying that measurement says so.
Neither figure is withdrawn.

Ranked by fill rather than by rate, the ordering changes almost completely: Drill
(43.2%, fill 0.95) sits above Ranger (65.4%, fill 0.80). *Every project in the
corpus is reaching most of what its commit supply permits.*

**This is a mechanism, and it replaces the reading the divergence invites.** The
tempting story — "these projects file tickets they never work on" — is not what
the numbers show. What they show is that **a tracker accumulates tickets faster
than a repository accumulates commits**, and once fewer than one commit exists per
ticket the ticket-side rate is capped below the commit-side rate by construction.
The two rates were never commensurable, and reporting one as though it licensed
the other is the error, not the projects' behaviour.

**The consequence for design is unchanged and now has a reason.** A study that
samples commits and looks up their tickets can work in any of these twelve. A
study that samples tickets and looks for the work is bounded by
`commit-side × commits / tickets` before it begins, and that quantity is not
reported anywhere in the literature — including by us, until now.

### 4.2.1 Kylin: the sharpest number in the corpus, and why it is withdrawn as the example

Earlier drafts led with Kylin — 83.9% commit-side against 12.0% ticket-side,
"seven of every eight tickets with no commit at all". **That example is
withdrawn.** The pinned commit reaches **968 commits beginning 2022-08-01**,
which is **7.5% of the 12,937 commits on the repository's refs**, and the
repository itself begins 2014-05-13. The `apache/kylin` default branch was
re-initialised for Kylin 5; the earlier history is on other branches.

So Kylin's 12.0% is measured over a **four-year commit window against a
twelve-year, 5,931-issue tracker**, and its 0.16 commits per ticket — the lowest
in the corpus by a factor of two — is a fact about the branch, not about Kylin's
traceability. Its fill_live is **0.87**, squarely at the corpus median: *by the
measure that isolates discipline, Kylin is unremarkable.*

Table 3 reports the same project at **fill_frozen 0.00**, and the two are not in
conflict. Under the frozen snapshot Kylin's TRR_frozen is **0.04%** — two cited
keys against a tracker of 4,989 — because **99.72% of its cited keys postdate the
snapshot**, so the number cap removes almost the whole numerator. Its
ceiling_frozen is 16.3%, well under the bound. The frozen estimator is registering
the same truncated branch this section is about, from the other side: live, the
window is too short for the tracker; frozen, the tracker is too old for the
window. Kylin is the worst end-to-end case in the corpus at 11.91pp (Table 3), and
it is flagged in both tables for that reason.

Three other projects have a pinned branch that starts after their repository does
— Jena (49.0% of refs), Karaf (45.4%) and James (89.4%, by eight days) — and none
is near Kylin's severity. The clone-depth column is in
`paper/revision_metrics.json`; the check is `scripts/revision_metrics.py`.

**Kylin is retained in every table**, because the bar was applied to it before any
of this was known and removing it now would be selection on the outcome. It is
flagged wherever it appears, and no claim in this paper rests on it.

## 4.3 The divergence is a property of the population, not of the survivors

<!-- only: msr2027 -->
Extending the ticket-side measurement to all 38 probed projects, against a frozen
tracker snapshot and with an estimator whose end-to-end error is **1.76pp mean
and 11.91pp maximum**, gives **no detectable association** between the two rates:
rho = **−0.010** over the 33 projects with a usable denominator, 95% CI
**[−0.35, +0.34]**, permutation p = 0.958. That rules out the strong positive
relationship a selection bar implicitly assumes, but at 80% power this study
detects only |rho| ≥ **0.47**, so **a null is not established**. On the twelve
projects measured exactly and live the same correlation is **+0.518**, a
disagreement in sign we report rather than resolve, and the per-project rows,
the estimator's validation and the sensitivity analyses are in the replication
package.
<!-- /only -->

<!-- only: preprint -->

Reporting §4.2 on the twelve that passed leaves the obvious objection open: the
range 12.0–69.0% is *within-passing variation* in TRR_live, and says nothing about the 26
projects below the bar, whose ticket realisation rates were never measured. That
objection is answered here by measuring all 38. **Table 3
(`paper/table3_ticket_side.md`) is the result**: one row per probed project, with
the commit-side rate, commits per ticket, the §3.1.4 ceiling, the ticket
realisation rate, and the fill, plus a note column recording every reason a row
should not be read at face value.

**Method.** The ticket realisation rate needs a tracker snapshot. Re-reading the
live tracker for 26 more projects would have dated those denominators weeks after
the twelve already measured, so the extended computation instead takes its
denominators from the frozen public Jira corpus and aligns numerator and
denominator in issue-number space (§3.1.3). **The estimator is validated before it
is used**: run against the live denominators for the twelve projects where the
exact rate is already known, it reproduces that rate to a **mean absolute error of
0.45pp** across all twelve, with a **worst case of 2.14pp** (Kylin, where the
tracker's issue numbering has enough gaps that number-capping undercounts). All
38 projects were then measured at their pinned shas.

**The estimator, and the honest version of its validation.** Two approximations
are stacked here: *number-capping* (using `|{cited keys ≤ N}| / N` rather than
intersecting with the real key set) and *snapshot substitution* (using the frozen
tracker's N rather than a live one). Earlier drafts reported **0.45pp mean /
2.14pp max**, which validates only the first. **Table 3 uses both**, and the
end-to-end error against the twelve published exact rates is:

| | mean | max | within 3pp |
|---|---:|---:|---:|
| number-capping alone | 0.45pp | 2.14pp | 12 of 12 |
| **number-capping + snapshot substitution (what Table 3 uses)** | **1.76pp** | **11.91pp** (Kylin) | 11 of 12 |
| the same, excluding Kylin | 0.84pp | 2.93pp | 11 of 11 |

**Quote 1.76pp / 11.91pp for anything in Table 3.** The favourable reading is
also true and is the one to lead with: eleven of twelve land within 2.93pp, and
the twelfth is Kylin, whose branch truncation (§4.2.1) is the same defect showing
up a second time.

**And the estimator is applied entirely outside the range it was validated on.**
The twelve validation projects span commit-side **82.6–98.3%**; the twenty-one
projects that carry the association below span **10.5–78.1%**. The ranges are
**disjoint — 0 of 21** applied projects fall inside the validated one. There is a
plausible argument that this does not matter, since the error mechanism is
tracker-numbering density rather than commit hygiene, and within the twelve the
error does not track the commit-side rate (rho = −0.16). That is an argument, not
a validation, and we make it as such. **Any claim below whose margin is smaller
than 11.91pp is not safe on this estimator.**

**Result.** Over the 33 projects with a usable denominator, Spearman's rho
between the commit-side rate and the ticket realisation rate is **−0.010**
(95% CI **[−0.352, +0.335]**, permutation p = **0.958**, 200,000 relabellings).
Excluding the three projects whose repositories barely overlap the snapshot era,
it is **−0.062** on 30 (95% CI [−0.413, +0.305]).

| | n | ticket realisation rate |
|---|---:|---|
| cleared the 0.80 bar | 12 | 0.04–68.6%, **median 52.6%** (TRR_frozen) |
| the bar dropped | 21 | 29.5–84.8%, **median 53.2%** |

The passing group's median is **0.6pp below** the dropped group's — the bar
selects for nothing on this axis (Mann-Whitney p = 0.94). **The highest ticket
realisation rate in the entire probe — Syncope at 84.8% — belongs to a project
the bar rejected at 36.0% commit-side.**

> **What this does and does not establish.** At n = 33 this study can detect
> |rho| ≥ **0.47** at 80% power. The interval admits everything from a moderate
> negative to a moderate positive association. **A strong positive relationship —
> the assumption that a high commit-side rate implies a usable ticket-side rate —
> is ruled out. A null is not established.** Earlier drafts said the two rates
> are "uncorrelated" and that commit-side "carries essentially no information";
> both overstate what n = 33 supports and are withdrawn.

**And the live measurement points the other way.** On the twelve projects where
both rates are measured exactly and live — no frozen snapshot, no number-capping —
Spearman's rho is **+0.518** (95% CI [−0.080, +0.841], permutation p = 0.088).
That is the opposite sign from the frozen estimate on 33. The two intervals
overlap and the pair is not formally contradictory, but **the paper does not have
one answer to give here**, and manufacturing one would be worse than saying so.
`paper/DIRECTION_TENSION.md` sets out both measurements, the populations they are
taken over, and the decomposition that explains the difference — the correlation
between commit-side rate and commits-per-ticket is **+0.455** within the eligible
twelve and **−0.717** across the 33, so the sign of the composite flips with the
population rather than with the estimator.

**What the extension converts, and what it does not.** §4.2's range was
*within-passing variation* and licensed no claim about the projects below the
bar. It now licenses a bounded one: across the whole probe, a high commit-side
rate does not predict a high ticket-side rate, and the bar selects for neither.
**The caveat on Table 1 is not withdrawn** — it remains true of the live
measurement, and this is a different estimator against a different snapshot,
reported alongside rather than merged into it.

Five projects have no usable rate and are excluded rather than scored zero, which
is itself the taxonomy at work. Pinot (14 tracker issues), Dubbo (78) and RocketMQ
(384) have denominators too small to carry a rate. ShardingSphere and SkyWalking
have **no project record for their probed key at all** — mode 1 and mode 6, a
category rather than a low number (§5.3).

<!-- /only -->
## 4.4 The measure replicates independently across corpora seven years apart

The commit-side rate is not a novel measure, and its agreement with an
independently constructed dataset is the reason to trust the probe. Four of the
five projects overlapping SEOSS 33 agree within **3.3pp** on corpora seven years
apart: Hadoop 97.13% → 97.8%, Hive 96.34% → 97.0%, HBase 90.06% → 92.5%,
ZooKeeper 87.12% → 90.4%.

Flink differed by **24.1pp** on full history (41.98% → 66.0%), and the scope
explanation for it has now been tested. Re-probing the **earliest 12,419
commits** — SEOSS's own change-set count — gives **5,214 / 12,419 = 41.9841%**
against their **41.98%**: a gap of **+0.0041pp**, where full history gives
+24.1pp. **Five of five overlapping projects agree once scope is matched.** The
remaining 25,800 commits run at 77.62%, and Flink's by-year series shows why:
0.0% in each of 2010, 2011, 2012 and 2013, 19.4% in 2014, 66.0% in 2015, and
70–88% every year since (`paper/FLINK_TRUNCATION.md`).

**The exactness of that match is not a warning sign.** The quantity is a
deterministic count over a fixed, identically bounded commit range — not an
estimate, and with no sampling error. Two correct implementations of the same
well-specified count should agree exactly, and a disagreement would indicate a
specification difference rather than noise; exact agreement is only suspicious
between estimators that *have* sampling error. The two numbers also arrive by
independent paths, one transcribed from a published table and one scanned fresh
from a clone at a pinned sha. **It confirms scope alignment and nothing more** —
in particular it does not validate the ticket-side estimator of §4.3, which is a
different measurement with its own error, reported there.

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

GHS is the standard sampling tool for MSR studies. Its 2021 publication reports
**735,669 repositories**; a record returned by the live API in 2026 carries
**35 fields**. (The two figures are of different vintages and are kept apart
deliberately: the index has certainly grown since 2021, and the 2021 paper
describes 25 characteristics rather than 35.) Only `totalIssues` and `openIssues`
touch issues at all, and both are GitHub-issue counts. There is no field for
issue-tracker type, external tracker usage, issue–commit linkage, traceability, or
commit-message convention; the one adjacent feature, filtering by issue label, is
described in the paper itself as still under development.

A researcher sampling with GHS therefore gets stars, commits, contributors and
license, and discovers post hoc that 26 of 38 candidates are unusable. That is
what happened here, and §5 is the taxonomy of the ways it happens.
