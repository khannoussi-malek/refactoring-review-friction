# Traceability paper — verified numbers

Every number below is tagged with the script that produced it and the commit
that script was last changed in. Numbers I could **not** re-derive from a script
are marked ⚠ and listed again in §8.

Verification date: 2026-07-25. Repo state: `abdfb40`.

---

## 1. The 38 probed projects

**RESOLVED 2026-07-25.** The provenance gap this section used to carry is closed.
`scripts/traceability_probe.py` (`da74465`) now re-derives every row from a fresh
`--no-checkout` clone and writes `paper/traceability_probe.json`, one record per
project with the **HEAD sha pinned**. All 38 re-probed rates match the original
hand-transcribed values to within 0.05pp, and **all six previously-lost commit
counts are recovered** (Atlas 4,140; Calcite 6,746; Accumulo 15,069; Helix 4,926;
Flume 2,084; CXF 19,763).

Regenerate with:
```
python3 scripts/traceability_probe.py --work <clonedir>
```

Bar: **≥0.80**, fixed in `predictions/PREDICTIONS.md` (`ca076a9`) before any
project was cloned. Never moved.

| # | project | HEAD | commits | jira_key_refs | github_issue_refs | multi-key rate | verdict | drop reason (measured) |
|---|---|---|---:|---:|---:|---:|---|---|
| 1 | ozone | `4f5ae5454f` | 10,962 | 10,774 | 9,484 | **98.3%** | pass | — |
| 2 | tez | `dd8137f4c1` | 3,123 | 3,043 | 310 | **97.4%** | pass | — |
| 3 | hive | `6730aadd18` | 18,213 | 17,670 | 2,877 | **97.0%** | pass | — |
| 4 | hbase | `4d417aacea` | 21,220 | 19,633 | 4,018 | **92.5%** | pass | — |
| 5 | phoenix | `1b55fb4b33` | 4,264 | 3,923 | 562 | **92.0%** | pass | — |
| 6 | zookeeper | `53a78e36f9` | 2,718 | 2,458 | 1,194 | **90.4%** | pass | — |
| 7 | ranger | `f133c21389` | 5,390 | 4,650 | 482 | **86.3%** | pass | — |
| 8 | oozie | `8bdac8be4f` | 2,412 | 2,054 | 243 | **85.2%** | pass | — |
| 9 | knox | `6bdf64cdfd` | 3,194 | 2,694 | 1,034 | **84.3%** | pass | — |
| 10 | drill | `86e9b82f16` | 4,594 | 3,866 | 1,849 | **84.2%** | pass | — |
| 11 | kylin | `b5b94b51ab` | 968 | 812 | 65 | **83.9%** | pass | — |
| 12 | sqoop | `f8beae32a0` | 969 | 800 | 8 | **82.6%** | pass | — |
| 13 | atlas | `b45faecc96` | 4,140 | 3,234 | 350 | **78.1%** | drop | below_bar_narrowly |
| 14 | james-project | `f4b8d37110` | 17,374 | 12,996 | 1,090 | **74.8%** | drop | below_bar_narrowly |
| 15 | flume | `9acf154361` | 2,084 | 1,540 | 195 | **73.9%** | drop | below_bar_narrowly |
| 16 | karaf | `d3a178529f` | 10,058 | 7,222 | 1,816 | **71.8%** | drop | below_bar_narrowly |
| 17 | calcite | `8447eda2f2` | 6,746 | 4,565 | 1,524 | **67.7%** | drop | low_commit_message_hygiene |
| 18 | flink | `1ea8cb0e4e` | 38,219 | 25,240 | 13,175 | **66.0%** | drop | low_commit_message_hygiene |
| 19 | hudi | `26b1ebc4e9` | 7,659 | 4,997 | 6,983 | **65.2%** | drop | github_issue_references_dominate |
| 20 | oodt | `f3dda2591b` | 2,251 | 1,395 | 51 | **62.0%** | drop | low_commit_message_hygiene |
| 21 | zeppelin | `597652e4c2` | 5,708 | 3,466 | 4,178 | **60.7%** | drop | github_issue_references_dominate |
| 22 | servicecomb-java-chassis | `ac4a6991e6` | 4,668 | 2,622 | 1,676 | **56.2%** | drop | low_commit_message_hygiene |
| 23 | tika | `379b32246f` | 10,543 | 5,778 | 2,496 | **54.8%** | drop | low_commit_message_hygiene |
| 24 | struts | `73f17c1be7` | 8,353 | 4,519 | 1,156 | **54.1%** | drop | low_commit_message_hygiene |
| 25 | storm | `cca249f181` | 11,871 | 5,539 | 1,508 | **46.7%** | drop | low_commit_message_hygiene |
| 26 | accumulo | `5c7d96deb6` | 15,069 | 6,475 | 4,048 | **43.0%** | drop | low_commit_message_hygiene |
| 27 | cxf | `1695c05def` | 19,763 | 7,403 | 2,481 | **37.5%** | drop | low_commit_message_hygiene |
| 28 | syncope | `21d513d1c3` | 9,422 | 3,390 | 802 | **36.0%** | drop | low_commit_message_hygiene |
| 29 | tomee | `a3e8806a9d` | 16,228 | 5,229 | 782 | **32.2%** | drop | low_commit_message_hygiene |
| 30 | wicket | `34ef6da88d` | 22,260 | 6,869 | 892 | **30.9%** | drop | low_commit_message_hygiene |
| 31 | parquet-java | `83c2c80d49` | 2,990 | 869 | 1,553 | **29.1%** | drop | github_issue_references_dominate |
| 32 | jena | `fbe7bfcb1e` | 13,091 | 3,195 | 2,207 | **24.4%** | drop | low_commit_message_hygiene |
| 33 | dubbo | `eb1d8abaeb` | 8,892 | 980 | 5,454 | **11.0%** | drop | github_issue_references_dominate |
| 34 | helix | `0902505fda` | 4,926 | 515 | 1,149 | **10.5%** | drop | github_issue_references_dominate |
| 35 | rocketmq | `b37e2bbacd` | 9,165 | 526 | 4,461 | **5.7%** | drop | github_issue_references_dominate |
| 36 | pinot | `2bcbdfed0a` | 15,639 | 821 | 13,145 | **5.2%** | drop | github_issue_references_dominate |
| 37 | skywalking | `dddc3b51be` | 8,577 | 22 | 5,139 | **0.3%** | drop | github_issue_references_dominate |
| 38 | shardingsphere | `b6ff1fb56d` | 49,111 | 5 | 30,746 | **0.0%** | drop | github_issue_references_dominate |

**Pass rate: 12 of 38 (31.6%). All 12 are Hadoop-ecosystem.**

The drop reason is **measured, not inferred**: the probe counts GitHub-issue
references (`#NNN`, `GH-NNN`) alongside Jira keys, so
`github_issue_references_dominate` means one count exceeds the other in that
repo. Nine projects qualify. `below_bar_narrowly` (≥70%), `low_commit_message_hygiene`
and `jira_effectively_unused` (<15%) are threshold labels on the measured rate.

## 1b. Cross-corpus validation of the measure (Rath & Mäder 2019, SEOSS 33)

The commit-side rate is not a novel measure. SEOSS 33 publishes it per project
as "Linked Change Sets [%]" for 33 projects (`paper/PRIOR_WORK.md` `215b10f`).
Our probe reproduces it on a corpus seven years later:

| project | SEOSS 2019 | this probe 2026 | Δ |
|---|---:|---:|---:|
| Hadoop | 97.13% (27,776 commits) | **97.8%** (28,290, 7-key) | +0.7pp |
| Hive | 96.34% (11,179) | **97.0%** (18,213) | +0.7pp |
| HBase | 90.06% (14,331) | **92.5%** (21,220) | +2.5pp |
| ZooKeeper | 87.12% (1,600) | **90.4%** (2,718) | +3.3pp |
| Flink | 41.98% (12,419) | **66.0%** (38,219) | **+24.1pp** |

Four of five agree within 3.3pp across corpora seven years apart — independent
cross-corpus validation of the measure. Flink's 24.1pp gap is scope, not error:
their snapshot holds 12,419 commits against our 38,219, so we cover a decade in
which its citation practice could have changed. **This is untested** — the
truncation check (re-probing Flink's first 12,419 commits) has not been run.

**Do not claim per-project linkage rates are unreported.** They are, by
Rath & Mäder 2019 (SEOSS 33, 33 projects) and Rath et al. ICSE 2018 (six
projects, both directions). What is new here is a pre-registered numeric bar
with reported attrition, both reference channels measured together, and the
commit-side/ticket-side divergence below.

## 1c. Commit-side is what gets published; ticket-side is what studies need

| project | commit-side | ticket-side |
|---|---:|---:|
| **Kylin** | **83.9%** | **12.0%** |
| Sqoop | 82.6% | 21.2% |
| Knox | 84.3% | 69.0% |
| Ozone | 98.3% | 63.9% |

Kylin is the worked example: it clears the 0.80 commit-side bar comfortably and
leaves seven in eight of its tickets with no commit at all. Source:
`scripts/ticket_coverage.py` `e0d76ef`.

**Truncation caveat, load-bearing.** Ticket-side was computed **only for the 12
projects that already cleared the commit-side bar**. The 12.0–69.0% range is
therefore *within-passing variation*, not evidence of a general correlation
between the two rates across all projects. Nothing here licenses a claim about
projects below the bar, whose ticket-side rates were never measured.

## 1d. The key matcher is 97.5% precise — measured, not assumed

Added 2026-07-30. The rates in §1 and §1c are produced by matching
`\b(?:KEY|KEY2)-\d+\b` against commit messages, and the first objection to any of
them is that the regex catches text that is not a reference. Measured on a
**200-commit manual sample**, equal allocation across the 12 eligible projects,
seed `20260730`, drawn from each project's **pinned `head_sha`**:

| quantity | value | source |
|---|---|---|
| precision, pooled sample | **195 / 200 = 97.5%** (Wilson 95% CI 94.3–98.9%) | `scripts/validate_matcher.py` |
| precision, corpus-weighted | **97.7%** (±2.8pp, stratified) | same |
| `revert` — sole matched key is the reverted work | 4 of 200 | same |
| `backport` — key refers to work ported from elsewhere | 1 of 200 | same |
| `version_string`, `changelog_paste`, `foreign_key` | 0 of 200 | same |

**The matcher is not the weak link in this paper.** The failure modes a reviewer
would expect — version strings, changelog pastes, foreign monorepo keys — did not
appear at all, and the residual 2.5% is reverts and one backport.

**Two zeros that are structural, and must be quoted with the caveat.**
`version_string` is near-unreachable because the pattern demands the upper-case
key followed by `-` and digits, which release identifiers in these projects
(`1.116.0-kylin-4.x-r028`, `4.1.89.Final`) do not produce. `foreign_key` is
unreachable for 11 of the 12, because each project is probed with its own key set
and only Ozone is multi-key (`HDDS,OZONE`, both its own). **The §2 single-key →
multi-key result on Hadoop is therefore NOT validated by this sample** — Hadoop
is the only true monorepo in the study and is not among the 12.

**Method verification.** Before sampling, the scan reproduces every project's
published `commits_scanned` and `jira_key_refs` exactly, for all 12, and aborts
otherwise. That is what establishes the validated matcher is the matcher that
produced §1 — without editing `citation_rate.py` and disturbing its provenance.

**Single rater, and why that is admissible here.** This is a mechanical check
against a written rule with categories fixed before labelling, not a coded
judgment, so §8's constraint (no κ available) does not bind it. The sample and
every label are committed — `paper/matcher_sample.json`,
`paper/matcher_labels.json` — so the check is auditable rather than agreed.
Full write-up and the adjudication rules: `paper/matcher_validation.md`.

## 2. Single-key vs multi-key — 26.2% vs **92.3%-A**

**Label discipline.** Two unrelated quantities in this repo are both 92.3%.
They are labelled **92.3%-A** and **92.3%-B** throughout, and the bare number is
never used again:

| label | quantity | value | source |
|---|---|---|---|
| **92.3%-A** | *Traceability*: Hadoop commits citing a Jira key, four-key probe | 26,125 / 28,290 | `scripts/citation_rate.py` (`de657c3`) |
| **92.3%-B** | *Tool coverage*: RefactoringMiner chunk coverage on `rel/release-3.3.0..3.4.0` | 3,175 / 3,440 | `SLICE_LOG.md` (`de657c3`) |

**92.3%-A** is about whether tickets can be found from commits. **92.3%-B** is
about how much of a commit range the detector actually analysed after
watchdog-killed chunks. They share a value by coincidence and nothing else; they
have different numerators, different denominators, different scopes, and support
different claims. The traceability paper uses **92.3%-A only**.

Re-derived 2026-07-25 on `hadoop/` (28,290 commits), `scripts/citation_rate.py` (`de657c3`):

| probe | keys | commits citing | rate |
|---|---|---:|---:|
| single-key | `HADOOP` | 7,404 / 28,290 | **26.2%** |
| four-key | `HADOOP,HDFS,YARN,MAPREDUCE` | 26,125 / 28,290 | **92.3%** |
| seven-key | `+HDDS,OZONE,SUBMARINE` | 27,667 / 28,290 | **97.8%** |

Both figures reproduce exactly against `SLICE_LOG.md` (`de657c3`), which records
92.3%-A and notes "≈97.7% if you also count HDDS/YETUS" — my seven-key run gives
97.8%, consistent.

At episode level the same effect is reported as 26% vs 99% (345/349 episodes
citing a key — verified below), so the paper must state which unit it means.

---

## 3. Measurement channels — TWO longitudinal, ONE cross-sectional

**Corrected claim.** These are not three parallel time series. Presenting them
as "three channels that decay at the migration" overstates the evidence, because
one of them has no time axis at all.

### 3a. Two channels that decay over time (longitudinal)

| # | channel | ≤2019 | ≥2022 | script | commit |
|---|---|---:|---:|---|---|
| L1 | Jira status hygiene — tickets reaching `Patch Available` | **93.5%** | **15.5%** | `scripts/temporal_trend.py` | `a6accaf` |
| L2 | CI verdict visibility in Jira | **84.6%** | **0.0%** | `scripts/ci_rework.py` | `47456b1` |

Source values: `temporal_trend.json` → `workflow_drift.early` = 0.9347,
`.late` = 0.1553, `drift` = true. `ci_rework.json` → `instrument.early` =
0.84647, `instrument.late` = 0.0.

These two are genuine decay: the same measurement, taken before and after the
2019–20 GitHub migration, on the same project.

### 3b. One channel that varies across module tiers (cross-sectional)

| # | channel | connectors | everything else | script | commit |
|---|---|---:|---:|---|---|
| X1 | Jira status comparability — tickets reaching `Patch Available` | **28.3%** | **86.2%** | `scripts/friction_decomposition.py` | `986a3ae` |

Source: `friction_decomposition.json` → `workflow_artifact.connector_reached_patch`
= 0.28261, `rest_reached_patch` = 0.86232, `n_connector_full_workflow` = 13.

This is **not** a time series. It is a single-period comparison between two
groups of modules, and it has **n = 13** connector tickets driving the full
workflow — thin enough that the paper should quote the proportion and not lean
on it further.

### The claim, restated

> Jira-derived measures in Hadoop degrade in two independent ways. **Over time**,
> two instruments decay sharply at the 2019–20 GitHub migration: status hygiene
> (93.5% → 15.5%) and CI verdict visibility (84.6% → 0%). **Across module
> tiers**, status-derived timings are additionally not comparable at all: cloud
> connectors drive the Jira workflow in 28.3% of tickets against 86.2%
> elsewhere. The common cause is the same — work moved to GitHub pull requests
> and the Jira status field went unmaintained — but the two are separate
> threats, and only the first is a decay.

---

## 4. The workflow-independent clock

**Definition.** Days from Jira ticket creation to the **first commit citing that
ticket key**, read from git. Independent of Jira status transitions, so it means
the same thing before and after the migration that breaks channels 2–3 above.

**714 / 714 = 100.0% is TRUE BY CONSTRUCTION. It is not a validation result and
must never be reported as one.**

The analysis frame is *built from commits that cite tickets*. A ticket with no
citing commit cannot enter the frame, so the match rate cannot come out at
anything other than 100%. Quoting it as evidence that the clock "works" would be
circular.

What it does establish, and all it establishes: for the 714 tickets in the
2016–2025 frame (320 architectural + 394 ordinary control), the clock is
*applicable* — every one has a definable creation→first-commit interval. That is
a statement about the frame, not about coverage of Hadoop's tickets.

Re-derived 2026-07-25 via `temporal_trend.assemble` (`scripts/temporal_trend.py`,
`a6accaf`). `ticket_first_commit.json` holds the underlying map: **30,954**
Hadoop tickets → first citing commit timestamp.

**The real coverage question is unanswered.** What fraction of *all* Hadoop
tickets in the period ever receive a citing commit? That number would be a
validation result, it is not 100%, and it is not currently computed anywhere.
Right-censoring — tickets that stalled and never got a commit — is noted as a
threat in `results_dossier.md` §5c and biases recent years toward *fast*,
making the divergence result conservative.

**Suggested phrasing for the paper:** "the clock is defined for every ticket in
the analysis frame by construction; coverage against all filed tickets is not
established."

---

## 5. Effort estimates — a deficit against a measured base rate, not an absence

Re-derived 2026-07-25 from `.jira_cache/*.json` (all four time-tracking fields
non-null in **0 of 323** architectural tickets), and the base rate measured
across the Public Jira Dataset.

**Estimate coverage is three numbers, never one** (`scripts/jira_estimates.py`,
Zenodo 15719919):

| population | issues | any estimate |
|---|---:|---:|
| Apache-wide, 646 projects | 1,014,926 | **2.557%** (25,949) |
| Hadoop corpus (HADOOP+HDFS+YARN+MAPREDUCE) | 49,201 | **1.449%** (713) |
| architectural subset (this study) | 323 | **0.000%** (0) |

Architectural tickets carry estimates at a **lower** rate than the surrounding
population: 0/323 against a 1.449% base rate gives an expected 4.7 and
P ≈ 0.009 under a naive binomial. Architectural tickets are not a random draw
and the non-randomness could run in either direction, so this is a deficit
suggestive on thin evidence, not an established effect. Estimate use is also a
per-project convention rather than an Apache-wide one — MESOS 32.94%,
STDCXX 38.70%, USERGRID 37.51% against 2.557% overall.

**Superseded claim.** Earlier versions of this file and `results_dossier.md`
said estimates are "absent in Apache". That was drawn at the wrong level of
aggregation: Apache records an estimate on 2.557% of a million issues, and the
four Hadoop-corpus projects on 1.449% of 49,201. The field is in use; the
architectural subset drew none of it.

**Denominator.** 345 counts *episodes*; several share a ticket. An estimate is a
property of a ticket, so the unit is **323 tickets**. State the episode count
separately as "345 of 349 episodes traceable to 323 tickets".

**HADOOP-18679** — "Add BulkDelete API for paged delete of files and objects".
Verified: `timeoriginalestimate`, `timeestimate`, `timespent` all `null`, and
zero non-null `customfield_*`.


### Validation note — the project count, and why 1,822 is not usable

Three figures, which must travel together:

| definition | count |
|---|---:|
| final-state, **key**-based — what every per-project number here uses | **1,276** |
| final-state ∪ changelog history, **name**-based — the dataset's own method | **2,506** |
| published in the dataset README | **1,822** (not reproducible) |

The dataset's notebook defines the count as
`set.union(unique_projects_final, unique_projects_history)`, i.e. project
*names* in the issue's final state unioned with names appearing in its
changelog. Implementing that overshoots by 684; counting final-state keys
undershoots by 546. Neither reproduces 1,822.

**Measured cause, partial:** across 2,686,282 issues, **326 project ids carry
more than one distinct name; 0 project keys do.** `Jira/12910` appears as
*SourceTree*, *SourceTree For Mac* and *Sourcetree For Mac* — three names for
one project, one of them a capitalisation-only variant. `Mojang/10400` is
*Minecraft* and *Minecraft: Java Edition*.

**Project keys are stable identifiers; project names are not, and the published
count is name-based.** Measured on the same pass: **0 project ids carry more
than one key and 0 keys map to more than one id**, against 326 ids carrying
multiple names. Within a tracker snapshot the id↔key mapping is exactly 1:1.
(That does not make key-based commit matching safe — commits can cite keys that
have no project record in the tracker at all; see
`paper/eligibility_failure_modes.md` mode 6.) Removing the ~326 surplus names lands near 2,180, still
above 1,822, so renaming explains part of the overshoot and not all of it. The
remainder is unidentified and the hypothesis is recorded as *consistent with
rename inflation, unverified*.

**Standing rule: 1,822 is never quoted next to a per-project number.** Issue
counts are unaffected — 2,686,282 parsed against ~2.7M published, −0.5%.

## 5b. Era bounds on the dossier's status- and CI-based results

Two bounds that must travel with the results they qualify
(`paper/ERA_AUDIT.md` `e0d76ef`):

**§5a phase decomposition is bounded to 2013–2021.** The reached-`Patch
Available` sub-corpus nominally spans 2013–2024, but the post-2021 tail is **6
architectural tickets**. Any claim that build-vs-merge behaviour *persists* is
unsupported; the result is a statement about 2013–2021.

**§8a is termination, not decay.** Architectural tickets carrying a CI verdict:
**96.7%** (145/150) ≤2018, **50.8%** (66/130) 2019–21, **0 of 43** ≥2022. The
verdicts are not sparse after 2021, they are absent, so no additional mining
extends the series. The mid-window is half-blind rather than merely thinner.

**Decade-trend control arm, corrected.** The ordinary control collapses across
truncation windows: **394 tickets (2016+) → 145 (2020+) → 101 (2021+)**. The
post-2020 result (interaction +0.102, p=0.44) is the 2020+ window with 145
controls; the 101 figure belongs to 2021+. Earlier drafts paired 394→101 with
the 2020+ p-value, mixing two windows. Source `scripts/full_adjustment.py`
`4b8c3af`.

## 6. Industry-donated projects

Re-derived 2026-07-25, `scripts/traceability_probe.py` (`da74465`):

| project | commits | jira_key_refs | github_issue_refs | Jira rate |
|---|---:|---:|---:|---:|
| ShardingSphere | 49,111 | **5** | 30,746 | **0.01%** |
| SkyWalking | 8,577 | 29 | 5,138 | 0.3% |
| RocketMQ | 9,165 | 526 | 4,461 | 5.7% |
| Pinot | 15,639 | 821 | 13,145 | 5.2% |
| Dubbo | 8,892 | 976 | 5,449 | 11.0% |
| ServiceComb | 4,668 | 2,624 | 1,674 | 56.2% |

**⚠ CORRECTION — ShardingSphere is not zero.** Earlier write-ups (including
`replication/CORPUS_FEASIBILITY.md` and the commit message of `0a81339`) said
"49,109 commits, not one Jira citation". The true figure is **5 Jira citations
in 49,111 commits** = 0.0102%, which renders as 0.0% at one decimal place. The
commit count also moved by 2 as HEAD advanced. Do not write "not one" — write
"5 of 49,111 (0.01%)". The point survives intact and is stronger stated
precisely: 30,746 GitHub-issue references against 5 Jira keys.

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

| number | status |
|---|---|
| Traceability rates for Atlas, Flume, Calcite, Accumulo, CXF, Helix | ✅ **RESOLVED** — all six re-derived, commit counts recovered (§1) |
| All 38 rates produced by stdout only | ✅ **RESOLVED** — `paper/traceability_probe.json`, HEAD sha pinned per record |
| "Reason" column inferred, not measured | ✅ **RESOLVED** — GitHub-issue references now counted per repo; 9 projects confirmed |
| 0/345 vs 0/323 unit mismatch | ✅ **RESOLVED** — paper uses 0/323 tickets (§5) |
| Two unrelated 92.3% figures | ✅ **RESOLVED** — labelled 92.3%-A and 92.3%-B (§2) |
| 714/714 presented as validation | ✅ **RESOLVED** — restated as true by construction (§4) |
| Three "decay channels" | ✅ **RESOLVED** — split into two longitudinal, one cross-sectional (§3) |
| ShardingSphere "not one Jira citation" | ✅ **CORRECTED** — 5 of 49,111 (§6) |
| **Coverage of the git clock against all filed tickets** | ❌ **OPEN** — not computed anywhere; the real validation number for §4 |
| **Estimate coverage across the 16 public Jiras** | ⏳ **PENDING** — `scripts/jira_estimates.py` written, dataset download paused at 1.31/5.81 GB |

Everything else in §2–§6 was re-derived from a committed artifact or a live
script run on the verification date.

---

## 9. Manuscript provenance — numbers the draft uses that §1–§8 did not carry

Added 2026-07-30 for `paper/manuscript/PROVENANCE_CHECK.md`. Sections §1–§8 cover
the traceability and estimate results; drafting `related.md`, `taxonomy.md` and
`threats.md` pulled in numbers from memos that had no row here. Each is listed
with the artifact it comes from and the commit that artifact was last changed in.
**No number below is new**: every one was already committed somewhere in the
repository, and this section gives it a provenance row so R7 holds.

### 9a. Second ecosystem — start-ui-web (TypeScript)

Corpus: `BearStudio/start-ui-web`, **1,199** commits 2019-12→2026-07, detector
coverage **1,121 / 1,199 = 93%**, **n=28** architectural PRs. Exploratory
throughout; only counts and proportions are used in the manuscript, never a test.

| quantity | value | source | commit |
|---|---|---|---|
| commit-message recall | **3 of 96 = 3.1%**; 93 of 96 silent | `SUI_FINDINGS.md` secondary 1 | `c080775` |
| commit-message precision | **3 of 10 = 30%** | same | `c080775` |
| architectural commits linking an issue | **7%** (other refactoring 7%, non-refactoring 10%) | `SUI_FINDINGS.md` secondary 2 | `c080775` |
| PR-visible architectural commits | **30 of 96 = 31%**; 66 of 96 = **69%** unreviewed | `scripts/sui/selection_bias.py` | `8dc2cdd` |
| PR routing is not arbitrary | churn 777 vs 151 lines p=0.0037; files 22 vs 9 p=0.0038; abstraction share 37% vs 9% p=0.0027 | same | `8dc2cdd` |
| migration-driven churn | **13×** larger (1,372 vs 104 lines, p<0.0001), n=21 vs 69 | `SUI_FINDINGS.md` secondary 4 | `c080775` |
| detector false positive | **160** `interface → class`, RefactoringMiner **3.1.4**, TS support complete **2026-05-24**, upstream **#1124** | `paper/RM_TYPESCRIPT.md` | `ac4a9cf` |

### 9b. Detector coverage loss — clustered, and the size-bias test

| quantity | value | source | commit |
|---|---|---|---|
| scope of the test | `root..HEAD` **1,198** commits; **1,057** analysed, **141** lost | `SUI_FINDINGS.md` threats | `c080775` |
| churn, analysed vs lost | **32** vs **14** lines, **p=0.0022** — lost commits are *smaller* | same | `c080775` |
| top-decile-churn share | 9.6% vs 12.8%, **p=0.23** n.s. | same | `c080775` |
| the clustered hole | **75 of 81** commits in 2024 (**93%**) absent, against 2–8% elsewhere | same | `c080775` |
| repair | **68** commits, 120 refactorings, 24 architectural recovered; coverage **88% → 93%** | same | `c080775` |

### 9c. Author identity aliasing

| quantity | value | source | commit |
|---|---|---|---|
| Hadoop keys on git author **name** (`%an`) | — | `scripts/social_centrality.py` | `93056ae` |
| Hadoop raw aliasing | **1,035** emails → **797** identities (**238** merged) | `scripts/sui/ALIASING_NOTE.md`, `scripts/sui/identity.py` | `50bb6df` |
| emails spanning multiple names | **96**, covering **27,307** commits = **35.2%** of the corpus | same | `50bb6df` |
| impact on the measures — **null** | mean `top1_share` **0.1545** by name vs **0.1495** by email; `bus_factor` 8.46 vs 8.56; `n_authors` 87.2 vs 91.0; **112** modules ≥20 commits; paired Wilcoxon **p=0.3651** | same | `50bb6df` |
| start-ui-web, by contrast | 59 → 50 identities; top-author share **58.1% → 67.2%** | same | `50bb6df` |
| `reviewer_pool` is null | `triage~reviewer_pool` rho **0.0010**, p **0.988** | `social_centrality.json` | `93056ae` |
| collected for the manuscript | — | `paper/ALIASING_HADOOP.md` | `b7f6d43` |

### 9d. Era audit — the status instrument alongside the CI instrument

§5b already carries the CI series (96.7% / 50.8% / 0 of 43). The status series it
did not:

| quantity | ≤2018 | 2019–21 | ≥2022 | source | commit |
|---|---|---|---|---|---|
| architectural tickets reaching `Patch Available` | **147 of 150** | **98 of 130** | **6 of 43** | `paper/ERA_AUDIT.md` | `eee902f` |

### 9e. Taxonomy worked examples

| mode | quantity | source | commit |
|---|---|---|---|
| 2 | RHBRMS **86.00%** estimate coverage on **2,400** issues, no code | `estimates_by_org.json` | `dcea7c0` |
| 3 | kata-containers: **0** `KATA-` keys in **19,807** commits | `paper/eligibility_failure_modes.md` | `5179907` |
| 4 | spring-batch: `BATCH-` in **4,046 of 7,034** commits, none in the 20 most recent sampled | same | `5179907` |
| 6 | Evergreen cites `DEVPROD` **2,785**× , tracker holds only `EVG`; DataLab cites `EPMCDLAB` **3,900**× and `DLAB` **3,547**×, tracker holds only `DATALAB` (**1,858** issues) | same | `5179907` |
| 6 | a single-key probe reads Evergreen as **71.7%** | same | `5179907` |
| 6 | `kiegroup/optaplanner` redirects to `apache/incubator-kie-optaplanner`, PLANNER **1,629** either way | `paper/intersection.json` | `63f4231` |
| 6 | Sqoop cites **790** distinct keys, **122** with no tracker record, **668** resolving | `paper/ticket_coverage.json` | `e0d76ef` |

### 9f. Prior work

| quantity | value | source | commit |
|---|---|---|---|
| GHS | **735,669** repositories, **35** fields; only `totalIssues`/`openIssues` touch issues | `paper/PRIOR_WORK.md` §4 | `215b10f` |
| SEOSS 33 spread | **8.11%** (Errai) → **97.13%** (Hadoop), 33 projects | `paper/PRIOR_WORK.md` §1 | `215b10f` |
| Rath ICSE'18, commit side | ~**48%** of commits unlinked; ~**60%** linked on average; **15%** unlinked in Derby vs ~**76%** in Maven | `paper/PRIOR_WORK.md` §2 | `215b10f` |
| Rath ICSE'18, ticket side | **43.3%** of improvements and **42.4%** of bugs have no commits; Derby 2,638 bugs, 1,093 1:1, 273 1:n, 1,272 unlinked ⇒ **51.8%** | same | `215b10f` |
| Vieira PROMISE'19 | >**70,000** bug reports, 55 ASF projects — **linkage rates unverified, 403 on every source** | `paper/PRIOR_WORK.md` §3 | `215b10f` |
| Iammarino 2021 | four projects, same-commit only, tightest analysis same-file **n=201** | `paper/SATD_NOVELTY.md` | `5b50ef1` |
| Esfandiari 2023 | commit tags, **77** projects, same-commit only | same | `5b50ef1` |

### 9g. Corpus limits and frozen thresholds

| quantity | value | source | commit |
|---|---|---|---|
| commit-side range, 12 eligible | **82.6–98.3%** | `paper/table1_eligibility.md` ← `scripts/make_table1.py` | `8d9f8ad` |
| power requirement | **769** independent tickets for 80% power; effective n capped at **P/ICC**; at P=12 and ICC **0.02** the ceiling is **600** | `scripts/advisor_followup.py`, `replication/CORPUS_FEASIBILITY.md` | `4b8c3af`, `f07d976` |
| ICC not estimated from four clusters | 3 df on the between-cluster component; must come from the pooled study | `replication/CORPUS_FEASIBILITY.md` | `f07d976` |
| lowering the bar | at **60%** another nine projects qualify; median candidate near **35%** | same | `f07d976` |
| frozen tier threshold | vendor share **≥0.40**, held; HBase max **0.33** and Phoenix flagged nothing; rule then failed **0 of 3** | `scripts/external_wrapper_tier.py`, `replication/REPLICATION.md` | `314845c`, `abdfb40` |
| bar pre-registered before any clone | **≥0.80**, never moved | `predictions/PREDICTIONS.md` | `ca076a9` |
| joint model, abstraction | **×1.54 [0.97, 2.43], p=0.068, n=319** | `scripts/full_adjustment.py` | `4b8c3af` |
| codebook keyword precision | **≈25%** (5 of 20 flagged), miss ≈5% (1 of 20), 40-comment single-rater sample, no κ — **an instrument result, not an instrument** | `codebook_results.md`, `results_dossier.md` §11, `codebook.md` | `de657c3` |
| frozen cache archive | **2,491** files, per-file SHA-256, **no rebuild script** | `scripts/freeze_caches.py`, `deposit/MANIFEST-v1.md` | `ce4bf7d` |

---

## 10. Numbers added 2026-08-05

Two loose tokens the manuscript used that §1–§9 did not carry, then the
ticket-realisation extension.

### 10a. Two provenance rows §1–§9 was missing

| quantity | value | source | commit |
|---|---|---|---|
| Hadoop commits analysed by RefactoringMiner | **8,919** commits, **51,861** refactorings, **248,336** location records | `paper/ENTITY_IDENTIFIERS.md`, `refminer_all.json` | `2259129` |
| the ICC value the feasibility table turns on | **0.015** → ceiling n_eff **800**, "feasible, barely"; **0.02** → **600**, infeasible. The whole design decision is the gap between these two, which is why a four-cluster estimate was refused | `replication/CORPUS_FEASIBILITY.md` | `f07d976` |

### 10b. Distribution of the 38 probed rates — and one figure withdrawn

`scripts/probe_summary.py` → `paper/probe_summary.json`. Written because the
manuscript wanted "the median sits near 35%" and that figure does not reproduce.

| quantity | value | source | commit |
|---|---|---|---|
| commit-side rate, all 38 probed | median **63.6%**, mean 57.2%, min 0.0%, max 98.3% | `scripts/probe_summary.py` | `152a477` |
| commit-side rate, the 26 the bar dropped | median **44.8%**, mean 42.2%, max **78.1%** (atlas) | same | `152a477` |
| commit-side rate, the 12 that cleared it | median 88.4%, mean 89.5% | same | `152a477` |
| pass count as the bar moves | 0.80 → **12**; 0.70 → 16; 0.60 → **21**; 0.50 → 24 | same | `152a477` |
| highest rate outside the Hadoop ecosystem | **74.8%** (james-project); **0** non-Hadoop projects clear the bar | same | `152a477` |

**⚠ WITHDRAWN — "the median sits near 35%".** Carried by
`replication/CORPUS_FEASIBILITY.md` and by §9g of this file ("median candidate
near **35%**"). It does not reproduce from `paper/traceability_probe.json` under
any grouping tried: all 38 gives 63.6%, the 26 dropped give 44.8%, the 17 below
60% give 30.9%. **Do not quote 35%.** The manuscript uses 63.6% and 44.8%. The
original sentence is left in place in `CORPUS_FEASIBILITY.md` with a dated
correction appended beneath it, per the additive-correction rule; the likely
origin is the earlier "12 of 34" probe state, but that is a hypothesis and the
earlier state is not recoverable.

**Confirmed on the same pass:** "at 60% another nine projects qualify" is exact —
12 at 0.80, 21 at 0.60.

**Family is a hand classification.** "All 12 are Hadoop-ecosystem" and "the best
outside it is James" both depend on a project→family judgment that is **not a
field in the probe** (§7 of this file records that). `probe_summary.py` writes the
classification into the artifact so the judgment is inspectable rather than
implicit.

### 10c. The ticket realisation rate across all 38 probed projects

`scripts/ticket_side_38.py` → `paper/ticket_side_38.json`, `paper/table3_ticket_side.md`.
Numerators from commit messages at each project's **pinned `head_sha`**;
denominators from the frozen public Jira corpus via `estimates_by_org.json`;
numerator and denominator aligned in issue-number space. **No Jira fetch.**

| quantity | value | source | commit |
|---|---|---|---|
| projects measured | **38 of 38**; 33 with a usable denominator | `scripts/ticket_side_38.py` | `45aebc8` |
| estimator validation, against the 12 published exact rates | mean absolute error **0.45pp**, worst **2.14pp** (kylin: 9.81% estimated vs 11.95% published) | same | `45aebc8` |
| commit-side vs ticket realisation, Spearman | **rho = −0.010** over 33; **−0.062** over 30 excluding hudi, kylin, ozone | same | `45aebc8` |
| cleared the bar, n=12 | 0.04–68.6%, **median 55.5%** | same | `45aebc8` |
| the bar dropped, n=21 | 29.5–84.8%, **median 53.2%** | same | `45aebc8` |
| highest rate in the whole probe | **syncope 84.8%** — commit-side **36.0%**, dropped by the bar | same | `45aebc8` |
| excluded, denominator < 500 | pinot (**14** tracker issues), dubbo (**78**), rocketmq (**384**) | same | `45aebc8` |
| excluded, no tracker record for the probed key | shardingsphere, skywalking | same | `45aebc8` |
| probed keys with no project record in the frozen tracker corpus | **6** keys, **5** of them cited, across **5** projects: THIRDEYE **327** distinct keys, OPTIQ **85**, RIP **35**, SWIP **11**, RS **8**; OZONE probed and never cited | same | `45aebc8` |
| flagged: most cited keys postdate the snapshot | kylin **100%**, dubbo **88%**, hudi **68%**, ozone **60%**, pinot **100%** | same | `45aebc8` |

**What this does and does not do to §1c.** The truncation caveat on §1c and on
Table 1 stands: the **12.0–69.0%** live range is within-passing variation. §10c is
a *different estimator against a different snapshot* and is reported alongside it,
never merged into it. What it adds is the population claim §1c could not make —
the commit-side rate carries essentially no information about the ticket-side one.

**Kylin appears twice with different values and both are correct.** Live snapshot
(2026-07-25): **12.0%**. Frozen snapshot: **0.04%**, because 100% of the keys
`apache/kylin` cites are numbered above the frozen tracker's issue count — the
repository's history does not reach back into the snapshot era. The frozen figure
is a statement about what is recoverable from that repository today and must not
be read as a traceability rate.
