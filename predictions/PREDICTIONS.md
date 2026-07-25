# Pre-registered predictions — external-system wrapper tier

**Committed before any outcome data was pulled.** At the time of this commit, no
Jira ticket data for any project below had been fetched. The only project data
read so far is git commit *messages* (for the traceability probe) and `pom.xml`
files (for the rule). `replication/` does not exist yet.

Verify with `git log --diff-filter=A -- replication/` — every outcome file must
be added in a commit *after* this one.

## The rule (frozen at commit `314845c`, `scripts/external_wrapper_tier.py`)

> A third-party groupId is **rare** if at most **5%** of the project's own modules
> declare it, counting compile- and runtime-scope dependencies only.
> A module's **vendor share** is the fraction of its declared dependencies that are
> rare third-party groupIds.
> A module is an **external-system wrapper** if **vendor share ≥ 0.40** *and* its
> transitive in-tree dependent count is below the project's **90th percentile**.

Applied to `mvn help:effective-pom` output, not raw `pom.xml`, so that inherited
and BOM-managed dependencies are counted. Verified on Hadoop that this input
change does not move the result: effective poms give the same 42.0 vs 3.1 days
(p=1.7e-07) and the same precision 0.75 / recall 1.00 as raw poms.

## The prediction

**In each project below, the flagged modules will show a higher median
days-from-ticket-creation-to-first-citing-commit than the unflagged modules.**

Test: one median per module (≥10 tickets), Mann-Whitney across **modules**, not
tickets, two-sided, α = 0.05. A project *replicates* if p < 0.05 **and** the
flagged median is the higher one.

### Candidate selection and attrition (decided before any outcome data)

| Project | commits | traceability | verdict |
|---|---|---|---|
| Hive | 18,213 | **97.0%** | included |
| HBase | 21,220 | **92.5%** | included |
| Phoenix | 4,264 | **92.0%** | included |
| Drill | 4,594 | **84.2%** | included |
| Kylin | 968 | **83.9%** | included, with a caveat (below) |
| Flink | 38,219 | **66.0%** | **DROPPED** — below the 80% traceability bar |

Camel and NiFi were excluded a priori: they are almost entirely connectors, so
they offer no core-vs-periphery contrast for the rule to separate.

*Kylin caveat:* its default branch (`kylin5`) carries only 968 commits — the 5.x
line is a rewritten history and there is no `origin/master`. Its corpus is an
order of magnitude smaller than the others and may not survive the ≥10-tickets-
per-module filter.

### Hive — 9 of 58 modules flagged

`hive-druid-handler`, `hive-exec`, `hive-kubernetes-operator`,
`hive-metastore-benchmarks`, `hive-serde`, `hive-service`,
`hive-standalone-metastore-rest-catalog`, `hive-standalone-metastore-server`,
`hive-testutils`

### Drill — 3 of 60 modules flagged

`drill-java-exec`, `drill-paimon-format`, `drill-udfs`

### Kylin — 10 of 47 modules flagged

`kylin-common-service`, `kylin-core-job`, `kylin-core-metrics`,
`kylin-datasource-sdk`, `kylin-it`, `kylin-jdbc`, `kylin-query-common`,
`kylin-query-service`, `kylin-server`, `kylin-server-it`

### HBase — 0 of 55 modules flagged → **NO PREDICTION**

The maximum vendor share in HBase is **0.33** (`hbase-rest`), below the frozen
0.40 cut. This is not a parsing failure: 55 modules parsed, 302 distinct
dependency groups, only 4 modules with no dependencies at all. HBase spreads its
third-party dependencies evenly enough that no module is vendor-dominated.

Recorded now, before outcomes, because it is a **coverage failure of the rule**
and must not be reinterpreted afterwards. Note that `hbase-external-blockcache`
(memcached client, `net.spy`) is an external-system wrapper by any reading and
the rule misses it at 0.25.

### Phoenix — 0 of 15 modules flagged → **NO PREDICTION**

Same situation, on a much smaller module set.

## What each outcome would mean

- **Replicates in 3 of 3 testable projects** — the tier is a real, portable
  property and the registered report has its independent variable.
- **Replicates in some** — the rule is project-dependent; the next question is
  what distinguishes the projects where it holds.
- **Replicates in none** — the Hadoop tier effect is a Hadoop fact, and the
  attention-rationing framing loses its empirical basis.
- **Two projects yielding no prediction at all** is already a result: the rule's
  0.40 threshold was set on Hadoop and does not fire on projects whose
  dependency structure is flatter. Whatever the outcomes say, the rule's
  *coverage* is 3 of 5.

## Anti-hindsight commitments

1. The rule will not be re-tuned after outcomes are seen. If 0.40 is wrong, that
   is a finding, not a parameter to fix.
2. HBase and Phoenix will not be rescued by lowering the threshold post hoc.
3. The Kylin caveat above is registered *now* so that dropping it later for thin
   data cannot be mistaken for a judgement made after seeing its result.
4. The module-level test (not ticket-level) is fixed here, because ticket-level
   n would manufacture significance from module-size differences.
