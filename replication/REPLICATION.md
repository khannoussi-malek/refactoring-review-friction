# Held-out replication — result

**The frozen tier rule does not replicate. 0 of 3 testable projects.**

Predictions were committed in `ca076a9`, before any Jira data was fetched;
everything in this directory was created after it.

## The pipeline that ran

| Step | Outcome |
|---|---|
| 6 candidates | Hive, HBase, Flink, Phoenix, Drill, Kylin |
| traceability ≥80% | **Flink dropped** (66.0%) |
| frozen rule fires | **HBase and Phoenix flag nothing** — no prediction possible |
| testable | Hive, Drill, Kylin |
| **replicate** | **none** |

## The test (pre-registered)

One median per module (≥10 tickets), outcome = days from ticket creation to
first citing commit, Mann-Whitney across **modules**, two-sided, α=0.05.
Replication = p<0.05 **and** flagged median higher.

| Project | tickets | modules (flagged / not) | flagged median | unflagged median | p | verdict |
|---|---|---|---|---|---|---|
| Hive | 13,903 | 40 (6 / 34) | **12.7 d** | 7.8 d | 0.210 | right direction, n.s. |
| Drill | 3,503 | 17 (2 / 15) | 8.8 d | **9.7 d** | 1.000 | **wrong direction** |
| Kylin | 527 | 15 (5 / 10) | 6.2 d | 5.9 d | 0.310 | right direction, n.s. |

## The test itself is very weak — Hadoop cannot pass it either

Run the *same* pre-registered test on Hadoop, where the effect is largest:

| | modules | median-of-medians | p |
|---|---|---|---|
| flagged | 2 | **51.1 d** | |
| unflagged | 4 | 6.5 d | **0.133** |

An **8× separation** on the project the rule was built from, and it still fails,
because with 2 versus 4 groups the smallest attainable two-sided Mann-Whitney
p-value is 2/C(6,2) = **0.133**. Hadoop could not have passed at any effect size.

This does not rescue the held-out result — Hive (6 v 34), Drill (2 v 15) and
Kylin (5 v 10) were all capable of reaching p<0.05 and did not. But it does mean
**the module-level design is near-useless as specified**, and that the ~10–20
project corpus §15 called for is needed for the *tier* question too, not only for
the abstraction question. The design fixed in advance was the right kind of test
and the wrong size, and that is worth more than the p-values above.

## What the data shows instead (POST-HOC — hypothesis, not finding)

The slowest modules in both large projects are external-system connectors, and
**the rule did not flag any of them**:

| Project | slowest modules by median days | flagged? |
|---|---|---|
| Hive | `hive-accumulo-handler` 16.4, `hive-webhcat-java-client` 16.2, `hive-jdbc` 15.1, `kafka-handler` 14.4 | no, no, no, no |
| Drill | `drill-mongo-storage` 39.7, `drill-jdbc-all` 28.2, `drill-storage-kafka` 20.5 | no, no, no |

Accumulo, WebHCat, JDBC, Kafka, MongoDB — every one of these wraps an external
system, which is exactly the concept the rule was meant to capture. What the
rule flagged instead was `drill-java-exec` (the core execution engine, 2,525
tickets) and `hive-exec`.

So the honest reading is: **the concept is not refuted, the operationalisation
is.** Vendor share computed from Maven dependencies picks out modules with
*many unusual libraries*, which in these projects means the big core engine, not
the thin adapters. Hadoop's connectors happened to be both — vendor-heavy and
peripheral — which is why the rule looked portable when it was not.

This observation is post-hoc and must be pre-registered before it counts. The
obvious next candidate operationalisations, in order of how hard they are to
game:

1. **Does the module implement a plugin/SPI interface** for an external system
   (`StoragePlugin`, `FileSystem`, `Handler`, `Serde`)? Structural, from code.
2. **Does the module's dependency set include a network/protocol client** rather
   than merely rare libraries? Needs a classifier for "is this artifact a client
   for something remote", which is where the hand-drawing would creep back in.
3. **Module name matching a service vocabulary** — cheap, works in this data,
   and almost certainly overfits English naming conventions.

## Coverage failure (recorded before outcomes, in `predictions/PREDICTIONS.md`)

HBase (max vendor share 0.33) and Phoenix flag nothing at the frozen 0.40 cut.
The threshold was calibrated on Hadoop. It was not lowered afterwards, and the
`hbase-external-blockcache` miss (a memcached client at 0.25) is a second
instance of the same operationalisation problem as above.

## Attrition and threats

- **Flink** dropped at 66% traceability, as expected.
- **Kylin** is thin: its default branch `kylin5` is a rewritten history with 968
  commits, and there is no `origin/master`. 527 tickets over 15 modules. The
  caveat was registered in advance.
- **Module attribution rate** varies: Drill 95%, Phoenix 88%, Hive 84%, Kylin
  74%, HBase 68%. Unattributed tickets are those whose first citing commit
  touched no module directory (root configs, docs, `dev-support`).
- Outcome is days-to-first-commit, which conflates queueing with building — the
  same caveat as §5c. It was chosen because it survives workflow migrations,
  which all five projects underwent.

## Reproduce

### Toolchain

Maven was **not installed system-wide**. It was a local binary unpacked into a
scratch directory and invoked by absolute path:

```
curl -L -o mvn.tgz https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz
tar xzf mvn.tgz
export MVN_BIN="$PWD/apache-maven-3.9.9/bin/mvn"     # Apache Maven 3.9.9
```

`Apache Maven 3.9.9 (8e8579a9e76f7d015ee5ec7bfcdc97d260186937)`, running on the
JDK at `~/.sdkman/candidates/java/current`. Nothing was added to the system
package manager, so a reproducer must set `MVN_BIN` (or put `mvn` on `PATH`);
`scripts/replication/prepare.sh` reads `MVN_BIN` and falls back to `mvn`.

### Clones — all 38 probed projects

`corpora/` was deleted after the sweep (3.7 GB). Everything is re-derivable:

```bash
# 22 projects needing a working tree (effective-pom or outcome extraction)
mkdir -p corpora && cd corpora
for r in accumulo atlas calcite cxf drill flink flume hbase helix hive hudi \
         karaf knox kylin oozie ozone parquet-java phoenix ranger tez tika zookeeper; do
  git clone --filter=blob:none "https://github.com/apache/$r.git" "$r"
done
cd ..

# 16 probed for traceability only -- no working tree needed, much smaller
mkdir -p probe && cd probe
for r in dubbo james-project jena oodt pinot rocketmq servicecomb-java-chassis \
         shardingsphere skywalking sqoop storm struts syncope tomee wicket zeppelin; do
  git clone --filter=blob:none --no-checkout "https://github.com/apache/$r.git" "$r"
done
```

`--no-checkout` is what makes the traceability sweep cheap: `git log` needs no
working tree, and the probe reads nothing else.

**`--no-renames` is required** for any `git log --name-only` over these clones.
Rename detection compares blob *content*, which `--filter=blob:none` does not
have locally, so git tries to fetch every candidate blob from the promisor
remote and eventually dies with `could not fetch ... from promisor remote`.

### Pipeline

```
scripts/replication/prepare.sh <project> <JIRA_KEY> <xmldir>   # probe + effective-pom + frozen rule
python3 scripts/replication/outcomes.py git  --project <p> --repo corpora/<p> --key <KEY>
python3 scripts/replication/outcomes.py jira --project <p>
python3 scripts/replication/outcomes.py test --project <p>
```

Jira keys used per project are listed in `CORPUS_FEASIBILITY.md`; four projects
were re-probed multi-key (TOMEE+OPENEJB, JAMES+MAILBOX, KARAF+FELIX,
CALCITE+OPTIQ, and additionally ROCKETMQ+RIP, PINOT+THIRDEYE).
