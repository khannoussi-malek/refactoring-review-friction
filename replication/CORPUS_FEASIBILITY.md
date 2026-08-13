# Corpus feasibility — 12 usable projects exist, and they are all one family

The power analysis (`advisor_followup.py` step 8) concluded that three projects
cannot reach 80% power at any corpus size, and that the registered report needs
**10–20 projects** contributing modest numbers of episodes each. This is what
happened when I went looking for them.

**The corpus exists — just barely — but the projects that qualify are not
independent, and that is what decides whether the study is powered.**

## Method

Every candidate is Apache, Maven-built, Jira-tracked, multi-module. Each was
cloned (`--filter=blob:none`, `--no-checkout` where only the log was needed) and
probed with `scripts/citation_rate.py`: what fraction of commits cite an issue
key. Key prefixes were detected empirically from commit messages rather than
assumed, and projects with a meaningful historical second key were re-probed
multi-key (TOMEE+OPENEJB, JAMES+MAILBOX, KARAF+FELIX, CALCITE+OPTIQ,
ROCKETMQ+RIP, PINOT+THIRDEYE).

The **≥80% bar was fixed before any project was cloned**
(`predictions/PREDICTIONS.md`). It has not been moved.

## Result — 12 of 38 projects pass

| Project | commits | traceability | family |
|---|---|---|---|
| Ozone | 10,962 | **98.3%** | Hadoop |
| Tez | 3,123 | **97.4%** | Hadoop |
| Hive | 18,213 | **97.0%** | Hadoop |
| HBase | 21,220 | **92.5%** | Hadoop |
| Phoenix | 4,264 | **92.0%** | Hadoop |
| ZooKeeper | 2,718 | **90.4%** | Hadoop (former subproject) |
| Ranger | 5,390 | **86.3%** | Hadoop |
| Oozie | 2,412 | **85.2%** | Hadoop |
| Knox | 3,194 | **84.3%** | Hadoop |
| Drill | 4,594 | **84.2%** | Hadoop |
| Kylin | 968 | **83.9%** | Hadoop |
| Sqoop | 969 | **82.6%** | Hadoop |

Below the bar (26 projects): Atlas 78.1, James 74.8, Flume 73.9, Karaf 71.8,
Calcite 67.7, Flink 66.0, Hudi 65.2, OODT 62.0, Zeppelin 60.7, ServiceComb 56.2,
Tika 54.8, Struts 54.1, Storm 46.7, Accumulo 43.0, CXF 37.5, Syncope 36.0,
TomEE 32.2, Wicket 30.9, Parquet 29.1, Jena 24.4, Dubbo 11.0, Helix 10.5,
RocketMQ 5.7, Pinot 5.2, SkyWalking 0.3, **ShardingSphere 0.01** (5 Jira citations in
49,111 commits, against 30,746 GitHub-issue references).

*Correction (2026-07-25): an earlier version of this file said "12 of 34" and
listed TomEE twice — once at 23.8% (single-key `TOMEE`) and once at 32.2%
(multi-key `TOMEE,OPENEJB`). The denominator is **38** probed projects: 22 with
a working tree in `corpora/`, 16 log-only in `probe/`. Only the multi-key rate
counts, per the pre-registered probe definition.*

**Every single passing project is Hadoop-ecosystem.** No general-purpose Java
project clears the bar — the best, James, reaches 74.8%, and the median sits
near 35%. The newer Apache projects donated from industry (ShardingSphere,
SkyWalking, RocketMQ, Dubbo, Pinot) are effectively at zero: they run on GitHub
Issues and never adopted the Jira-citation convention at all.

*Correction (2026-07-25): ShardingSphere is 5 citations in 49,111 commits
(0.01%), not literally none — an earlier version of this file said "not one
Jira citation". See `paper/numbers.md` §6.*

Note that even Hadoop adjacency is not sufficient — **Parquet fails at 29.1%**
and **Accumulo at 43.0%** (it migrated to GitHub Issues). The signal is a
specific commit-hygiene convention, not a dependency relationship.

## What 12 projects buys, quantitatively

From step 8: the fully-adjusted effect needs **769 independent tickets** for 80%
power, and with P projects the effective n is capped at **P/ICC** whatever the
corpus size. At P=12:

| ICC | ceiling n_eff | verdict |
|---|---|---|
| 0.01 | 1,200 | feasible — 177 tickets per project |
| 0.015 | 800 | feasible, barely — 1,629 tickets per project |
| **0.02** | **600** | **infeasible — needs P > 15** |
| **0.05** | **240** | **infeasible — needs P > 38** |

So the entire study hinges on a parameter nobody has measured: how correlated
architectural-refactoring friction is *between projects in the same ecosystem*.
And the direction of the bias is bad. These twelve projects share contributors,
committers, review norms, release processes, and in several cases the same
build and CI infrastructure. Whatever the true ICC of a random project sample
is, **the ICC of this sample is higher**, and the feasibility table above says
the difference between 0.015 and 0.02 is the difference between a powered study
and an impossible one.

**The first analysis the registered report should run is an ICC estimate**, on
data already collected: `replication/*.test.json` holds per-module medians for
Hive, Drill and Kylin, and Hadoop's are recoverable from `blast_radius_model`.
A variance-components model on those four gives a defensible prior, and it
decides the design before any more mining happens. If ICC lands above 0.02, no
corpus of Apache-Jira projects can power this effect and the outcome measure has
to change.

### Correction (2026-07-25): the four-cluster ICC was proposed here and refused

**The paragraph above is right about the requirement and wrong about where the
estimate can come from. It was not run, and it should not be.**

An ICC is a ratio of between-cluster variance to total variance. At **n=4
clusters** — Hadoop, Hive, Drill, Kylin — the between-cluster component has 3
degrees of freedom, and its sampling distribution is so wide that the point
estimate carries essentially no information about the parameter. The interval
would span most of the feasible range, and the whole decision this section turns
on is the difference between ICC 0.015 and 0.02. A four-cluster estimate cannot
resolve a distinction that fine; it would be a number without a meaning, and
worse than no number, because it would look like evidence.

Two further reasons specific to these four:

* **They are the least representative four available.** Hadoop is the project the
  design was built on, and Hive, Drill and Kylin were selected into the
  replication precisely because they cleared a traceability bar that only
  Hadoop-ecosystem projects clear. Their between-project variance is a lower
  bound on a random sample's, which biases ICC *down* — the direction that makes
  the study look feasible when it is not.
* **The outcome is already spent on all four.** An estimate drawn from them
  cannot be validated against anything held out.

**Where the estimate must come from instead:** the pooled study itself, as a
first stage. Fit the variance-components model on the full corpus as collected,
report the ICC with its interval as a result of stage one, and let it set the
stopping rule for stage two. That is the only design in which the parameter is
estimated at an n where it means something.

Recorded because the refusal is a decision, not an omission: see
`PROJECT_STATE.md` §2, row 07-25.

## The three ways out

1. **Drop the traceability bar and model the measurement error.** At 60% another
   nine projects qualify and the family widens (Flink, Hudi, Zeppelin, Storm,
   Tika, Calcite). The cost is a biased sample of *tickets* within each project:
   commits that cite tickets differ systematically from those that do not — the
   start-ui-web pilot found 69% of architectural work never passed through
   review at all, and the same selection applies here.
2. **Change the outcome so it needs no tickets.** Anything computed purely from
   git — commit-to-commit intervals, revert rates, recurrence of churn in the
   same files — frees the corpus entirely and dissolves both the traceability
   filter and the ecosystem clustering. The cost is losing the
   creation-to-first-commit clock that made the decade-trajectory result
   possible, and with it the ability to measure *waiting* at all.
3. **Accept ecosystem-bounded scope and say so.** Register as "architectural
   refactoring friction in the Hadoop data-infrastructure ecosystem", 12
   projects, and state the boundary as a finding rather than discovering it in
   review.

Option 2 is the strongest study and the largest rebuild. Option 3 is honest and
immediately actionable. Option 1 is the one to avoid drifting into silently.

## Cost note

For a project that passes, everything downstream is automated and cheap:
`scripts/replication/prepare.sh` runs the probe, `mvn help:effective-pom` and the
frozen rule in about three minutes; `outcomes.py` pulls the git and Jira sides.
Finding the projects was the expensive part — 38 clones, 4.3 GB, to keep 12.
The clones have since been deleted; `REPLICATION.md` carries the commands to
recreate all 38.

---

## Correction (2026-08-05): "the median sits near 35%" is not reproducible

The sentence above — *"the best, James, reaches 74.8%, and the median sits near
35%"* — is left in place because this file records what was believed when. The
median claim does not reproduce from `paper/traceability_probe.json` under any
grouping tried:

| grouping | n | median |
|---|---:|---:|
| all probed projects | 38 | **63.6%** |
| projects the bar dropped | 26 | **44.8%** |
| projects below 60% | 17 | 30.9% |
| projects clearing the bar | 12 | 88.4% |

Computed by `scripts/probe_summary.py` → `paper/probe_summary.json`. No grouping
lands near 35%, so the figure is treated as **unsourced and withdrawn**; the
manuscript quotes 63.6% and 44.8% instead. The most likely origin is the earlier
"12 of 34" state of the probe, before the denominator was corrected to 38 and
before TomEE's single-key rate was replaced by its multi-key rate
(`PROJECT_STATE.md` §7) — but that is a hypothesis, not a reconstruction, and the
earlier state is not recoverable.

**What does reproduce**, from the same script: James at **74.8%** is the highest
rate outside the Hadoop ecosystem; Atlas at **78.1%** is the highest among all
dropped projects and *is* Hadoop-ecosystem, so the two statements are consistent
only under the family classification, which is a hand judgment and not a field in
the probe. Lowering the bar to 60% raises the pass count from **12 to 21** — the
"another nine projects qualify" claim in this file and in `paper/numbers.md` §9g
is confirmed exactly.
