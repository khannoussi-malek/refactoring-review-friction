# Traceability paper — verified numbers

Every number below is tagged with the script that produced it and the commit
that script was last changed in. Numbers I could **not** re-derive from a script
are marked ⚠ and listed again in §8.

Verification date: 2026-07-25. Repo state: `abdfb40`.

---

## 1. The 38 probed projects

**⚠ Provenance warning for this whole table.** `scripts/citation_rate.py`
(`de657c3`) prints to stdout and writes **no machine-readable artifact**. Every
rate below was transcribed by hand from terminal output into
`replication/CORPUS_FEASIBILITY.md`. The clones were deleted in Task 1, so the
six rows marked ⚠ cannot currently be re-derived at all. Before publication the
probe must be re-run with a `--out traceability.json` flag added, on a fresh set
of clones, and this table regenerated from that file.

Command: `python3 scripts/citation_rate.py --repo <path> --key <KEY[,KEY2]>`
Bar: **≥0.80**, fixed in `predictions/PREDICTIONS.md` (`ca076a9`) before any
project was cloned. Never moved.

| # | project | commits scanned | traceability | verdict | likely reason |
|---|---|---:|---:|---|---|
| 1 | Ozone | 10,962 | 98.3% | pass | Hadoop spin-out, inherited convention |
| 2 | Tez | 3,123 | 97.4% | pass | Hadoop ecosystem |
| 3 | Hive | 18,213 | 97.0% | pass | Hadoop ecosystem |
| 4 | HBase | 21,220 | 92.5% | pass | Hadoop ecosystem |
| 5 | Phoenix | 4,264 | 92.0% | pass | Hadoop ecosystem |
| 6 | ZooKeeper | 2,718 | 90.4% | pass | former Hadoop subproject |
| 7 | Ranger | 5,390 | 86.3% | pass | Hadoop ecosystem |
| 8 | Oozie | 2,412 | 85.2% | pass | Hadoop ecosystem |
| 9 | Knox | 3,194 | 84.3% | pass | Hadoop ecosystem |
| 10 | Drill | 4,594 | 84.2% | pass | Hadoop ecosystem |
| 11 | Kylin | 968 | 83.9% | pass | Hadoop ecosystem; `kylin5` branch only |
| 12 | Sqoop | 969 | 82.6% | pass | Hadoop ecosystem; retired to Attic |
| 13 | Atlas | ⚠ not recorded | 78.1% | drop | just below bar |
| 14 | James | 17,374 | 74.8% ² | drop | general Java |
| 15 | Flume | 2,084 ³ | 73.9% ³ | drop | Hadoop-adjacent but below bar |
| 16 | Karaf | 10,058 | 71.8% ² | drop | general Java |
| 17 | Calcite | ⚠ not recorded | 67.7% ² | drop | general Java |
| 18 | Flink | 38,219 | 66.0% | drop | streaming; heavy GitHub PR use |
| 19 | Hudi | 7,659 | 65.2% | drop | data; GitHub PR use |
| 20 | OODT | 2,251 | 62.0% | drop | general Java |
| 21 | Zeppelin | 5,707 | 60.7% | drop | data |
| 22 | ServiceComb | 4,668 | 56.2% | drop | industry-donated |
| 23 | Tika | 10,543 | 54.8% | drop | general Java |
| 24 | Struts | 8,353 | 54.1% | drop | general Java |
| 25 | Storm | 11,871 | 46.7% | drop | streaming |
| 26 | Accumulo | ⚠ not recorded | 43.0% | drop | **migrated to GitHub Issues** |
| 27 | CXF | ⚠ not recorded | 37.5% | drop | general Java, low commit hygiene |
| 28 | Syncope | 9,422 | 36.0% | drop | general Java |
| 29 | TomEE | 16,228 | 32.2% ² | drop | general Java |
| 30 | Wicket | 22,260 | 30.9% | drop | general Java |
| 31 | Parquet | 2,990 | 29.1% | drop | Hadoop-adjacent; GitHub PR workflow |
| 32 | Jena | 13,091 | 24.4% | drop | general Java; `GH-` keys appear instead |
| 33 | Dubbo | 8,892 | 11.0% | drop | industry-donated; GitHub Issues |
| 34 | Helix | ⚠ not recorded | 10.5% | drop | general Java |
| 35 | RocketMQ | 9,165 | 5.7% | drop | industry-donated; GitHub Issues |
| 36 | Pinot | 15,639 | 5.2% | drop | industry-donated; GitHub Issues |
| 37 | SkyWalking | 8,577 | 0.3% | drop | industry-donated; GitHub Issues |
| 38 | ShardingSphere | 49,109 | 0.0% | drop | industry-donated; GitHub Issues |

³ Flume was re-cloned and re-probed from scratch during the Task 4
reproducibility check (2026-07-25): 1,540 / 2,084 = **73.9%**, reproducing the
recorded rate exactly. This is the only row in the table independently
re-derived after the clones were deleted.

² re-probed multi-key: TOMEE+OPENEJB, JAMES+MAILBOX, KARAF+FELIX, CALCITE+OPTIQ.
Single-key rates were TomEE 23.8, James 69.9, Karaf 68.9, Calcite 66.4.
RocketMQ+RIP and Pinot+THIRDEYE were also multi-key probed.

**Pass rate: 12 of 38 (31.6%). All 12 are Hadoop-ecosystem.**

Reasons are inferred from key-prefix distributions and known project history,
**not** measured. "Migrated to GitHub Issues" is verified only for Accumulo
(`GH` prefix dominance) and Jena (932 `GH-` citations). Treat the column as
annotation, not data.

---

## 2. Single-key vs multi-key — 26.2% vs 92.3%

Re-derived 2026-07-25 on `hadoop/` (28,290 commits), `scripts/citation_rate.py` (`de657c3`):

| probe | keys | commits citing | rate |
|---|---|---:|---:|
| single-key | `HADOOP` | 7,404 / 28,290 | **26.2%** |
| four-key | `HADOOP,HDFS,YARN,MAPREDUCE` | 26,125 / 28,290 | **92.3%** |
| seven-key | `+HDDS,OZONE,SUBMARINE` | 27,667 / 28,290 | **97.8%** |

Both figures reproduce exactly against `SLICE_LOG.md` (`de657c3`), which records
92.3% and notes "≈97.7% if you also count HDDS/YETUS" — my seven-key run gives
97.8%, consistent.

**⚠ Collision warning.** `SLICE_LOG.md` contains a *second, unrelated* 92.3%:
RefactoringMiner chunk coverage of 3,175/3,440 commits on the
`rel/release-3.3.0..rel/release-3.4.0` range. Same number, different measurement.
Do not let these merge in the prose.

At episode level the same effect is reported as 26% vs 99% (345/349 episodes
citing a key — verified below), so the paper must state which unit it means.

---

## 3. Three measurement channels that decay at the 2019–20 GitHub migration

| # | channel | early | late | script | commit |
|---|---|---:|---:|---|---|
| 1 | Jira status **comparability across module tiers** — reached `Patch Available` | connectors **28.3%** | everything else **86.2%** | `scripts/friction_decomposition.py` | `986a3ae` |
| 2 | Jira status **hygiene over time** — reached `Patch Available` | ≤2019 **93.5%** | ≥2022 **15.5%** | `scripts/temporal_trend.py` | `a6accaf` |
| 3 | **CI verdict visibility** in Jira | ≤2019 **84.6%** | ≥2022 **0.0%** | `scripts/ci_rework.py` | `47456b1` |

Re-read from committed artifacts: `friction_decomposition.json`
(`workflow_artifact.connector_reached_patch` = 0.28261,
`rest_reached_patch` = 0.86232, `n_connector_full_workflow` = 13);
`temporal_trend.json` (`workflow_drift.early` = 0.9347, `.late` = 0.1553,
`drift` = true); `ci_rework.json` (`instrument.early` = 0.84647,
`instrument.late` = 0.0).

Channel 1 is a *cross-sectional* comparability failure and channels 2–3 are
*longitudinal*; only 2 and 3 are strictly "decay at the migration". Channel 1 is
the same underlying cause (work moved to GitHub PRs, Jira status went
unmaintained) observed across tiers rather than across time. The paper should
say so rather than presenting three parallel time series.

---

## 4. The workflow-independent clock

**Definition.** Days from Jira ticket creation to the **first commit citing that
ticket key**, read from git. Independent of Jira status transitions, so it means
the same thing before and after the migration that breaks channels 2–3 above.

**Match rate: 714 / 714 = 100.0%** — re-derived 2026-07-25 via
`temporal_trend.assemble` (`scripts/temporal_trend.py`, `a6accaf`): the analysis
frame holds 714 tickets in 2016–2025 (320 architectural + 394 ordinary control),
every one of which has a first citing commit.

`ticket_first_commit.json` holds the full map: **30,954** Hadoop tickets → first
citing commit timestamp.

**⚠ Selection caveat, must appear beside the 100%.** The match rate is 100% *by
construction*: the ticket set is built from commits, so a ticket with no commit
cannot enter the frame. It measures the clock's applicability to landed work,
not the coverage of all tickets. Right-censoring is already noted as a threat in
`results_dossier.md` §5c.

---

## 5. Effort estimates in Apache — zero

Re-derived 2026-07-25 directly from `.jira_cache/*.json` (fetch script
`scripts/setup.sh` / Jira API cache):

| field | non-null |
|---|---|
| `fields.timeoriginalestimate` | **0 / 323** |
| `fields.timeestimate` | **0 / 323** |
| `fields.timespent` | **0 / 323** |
| `fields.aggregatetimeoriginalestimate` | **0 / 323** |

**⚠ Denominator mismatch.** The brief and `results_dossier.md` §3 say **0/345**.
345 is the number of *episodes* citing a Jira key (verified: 349 episodes, 345
with an `issue_key`). The number of *unique tickets* is **323**. Both are zero,
so no claim changes, but the paper must pick a unit: 0/345 episodes ≡ 0/323
tickets.

**HADOOP-18679** — "Add BulkDelete API for paged delete of files and objects".
Verified: `timeoriginalestimate`, `timeestimate`, `timespent` all `null`, and
**zero non-null `customfield_*`** of any kind. Cited in `SLICE_LOG.md`
(`de657c3`) as the illustrative case — a substantial interface-design ticket
carrying no estimate anywhere.

---

## 6. Industry-donated projects

| project | commits | Jira citation rate | script |
|---|---:|---:|---|
| ShardingSphere | 49,109 | **0.0%** | `citation_rate.py` (`de657c3`) |
| SkyWalking | 8,577 | **0.3%** | same |
| RocketMQ | 9,165 | **5.7%** ² | same |
| Dubbo | 8,892 | 11.0% | same |
| Pinot | 15,639 | 5.2% ² | same |
| ServiceComb | 4,668 | 56.2% | same |

² multi-key (ROCKETMQ+RIP, PINOT+THIRDEYE).

ShardingSphere is the strongest single datapoint in the paper: **49,109 commits,
not one Jira citation.** Same ⚠ provenance caveat as §1 — transcribed from
stdout, clones deleted.

---

## 7. Figures and tables: what exists as code

**Exists as code** (regenerable):

| artifact | script | commit |
|---|---|---|
| `figures/study_funnel.png` | `scripts/filter_architectural.py` | `de657c3` |
| `figures/arch_vs_ordinary.png` | `scripts/blast_radius_model.py` pipeline | `6d1ed8d` |
| `figures/abstraction_gradient.png` | same | `6d1ed8d` |
| `figures/friction_phases.png` | `scripts/friction_decomposition.py` | `986a3ae` |
| `figures/temporal_trend.png` | `scripts/temporal_trend.py` | `a6accaf` |
| `figures/ci_rework.png` | `scripts/ci_rework.py` | `47456b1` |
| `figures/blast_radius.png`, `module_hotspots.png` | `scripts/blast_radius_model.py` | `6d1ed8d` |
| `figures/social_centrality.png` | `scripts/social_centrality.py` | `93056ae` |
| `figures/retraction.png` | `scripts/filter_architectural.py` pipeline | `b8d1476` |
| joint-model table (§5 dossier) | `scripts/full_adjustment.py` | `4b8c3af` |
| power / P-ICC table | `scripts/advisor_followup.py` | `4b8c3af` |
| frozen-rule flags + Hadoop split | `scripts/external_wrapper_tier.py` | `314845c` |
| held-out module test | `scripts/replication/outcomes.py` | `48caf14` |

**Would need writing** (currently hand-assembled markdown only):

1. **The 38-project traceability table (§1)** — no script emits it. Needs
   `citation_rate.py --out` plus a table generator. *Highest priority: it is the
   paper's central table and is currently untraceable.*
2. **Single vs multi-key comparison (§2)** — three manual runs; needs a driver.
3. **The three-channel decay figure (§3)** — the three numbers live in three
   separate JSONs; no combined figure exists.
4. **Pass-rate-by-project-family chart** — the "all 12 are Hadoop-ecosystem"
   result has no visual; family is not even a recorded field.
5. **Estimate-coverage table across 16 Jiras** — `scripts/jira_estimates.py`
   exists but has not been run to completion (Task 2 in progress).

---

## 8. Numbers I cannot fully trace

| number | problem | fix |
|---|---|---|
| Traceability rates for **Atlas, Flume, Calcite, Accumulo, CXF, Helix** | commits-scanned never recorded; clones deleted in Task 1 | re-clone those six, re-run probe with an `--out` artifact |
| **All 38 rates** | produced by stdout only, hand-transcribed to markdown | add `--out traceability.json` to `citation_rate.py`, re-run sweep |
| **"Reason" column (§1)** | inferred from key-prefix distributions and project history, not measured | either measure (count `GH-`/`#NNN` citations per repo) or label as annotation |
| **0/345 vs 0/323** | episode vs ticket unit mismatch between dossier and this file | pick one unit in the prose |
| **92.3%** | collides with an unrelated 92.3% (RM chunk coverage) in `SLICE_LOG.md` | disambiguate explicitly |

Nothing in §2–§6 other than the above is unverified: every figure there was
re-derived today from either a committed JSON artifact or a live script run.
