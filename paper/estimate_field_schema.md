# Estimate field schema across 16 public Jira instances

Derived from the field catalogues shipped with the Public Jira Dataset
(Zenodo 15719919): `0. DataDefinition/jira_field_information.json`, plus
`May2021/jira_field_information_MAY_2021.json` for MariaDB and Mindville, which
are absent from the primary file. Snapshots are **not merged**.

## Why this is a finding and not a lookup table

Jira's six time-tracking fields have fixed ids. Story points do not: every
organisation allocates its own `customfield_*` number. Counting story points by
guessing an id, or by reusing one organisation's, returns zeros that look like
absence of estimation.

| normalised field name | distinct customfield ids across orgs |
|---|---:|
| story points | **15** |
| original story points | **7** |
| story point estimate | **2** |
| actual story points | **2** |

Ten of sixteen organisations carry **more than one** story-point field; Jira's
own instance carries two both literally named "Story Points"
(`customfield_10623`, `customfield_10571`). Mojang carries none.

## Per-organisation schema

| org | snapshot | fields | time-tracking | story-point custom fields |
|---|---|---:|---|---|
| Apache | 2023 | 211 | 6/6 | `customfield_12314523` Original story points; `customfield_12310293` Story Points |
| Hyperledger | 2023 | 81 | 6/6 | `customfield_10002` Story Points |
| IntelDAOS | 2023 | 79 | 6/6 | `customfield_10026` Story Points; `customfield_10016` Story point estimate |
| JFrog | 2023 | 178 | 6/6 | `customfield_14600` Story Points |
| Jira | 2023 | 218 | 6/6 | `customfield_10623` Story Points; `customfield_10571` Story Points; `customfield_19232` Original story points; `customfield_10653` Story Points |
| JiraEcosystem | 2023 | 516 | 6/6 | `customfield_19406` Story point estimate; `customfield_10133` Story Points |
| MariaDB | MAY_2021 | 66 | 6/6 | `customfield_11602` Original story points |
| Mindville | MAY_2021 | 59 | 6/6 | `customfield_10006` Story Points |
| Mojang | 2023 | 65 | 0/6 — **none** | **none by name** |
| MongoDB | 2023 | 220 | 0/6 — **none** | `customfield_19950` Actual Story Points; `customfield_10555` Story Points; `customfield_18952` Original story points |
| Qt | 2023 | 76 | 6/6 | `customfield_10183` Story Points |
| RedHat | 2023 | 270 | 6/6 | `customfield_12314040` Original story points; `customfield_12310243` Story Points |
| Sakai | 2023 | 160 | 6/6 | `customfield_10026` Story Points; `customfield_10016` Story point estimate |
| SecondLife | 2023 | 163 | 6/6 | `customfield_13174` Original story points; `customfield_10163` Story Points |
| Sonatype | 2023 | 102 | 6/6 | `customfield_10132` Story Points; `customfield_12702` Original story points |
| Spring | 2023 | 68 | 6/6 | `customfield_10142` Story Points; `customfield_10781` Actual Story Points |

## Three states, never two

`absent_from_catalogue` and `present_null` are different facts and are kept
apart in `estimates_by_org.json`:

| org | time-tracking fields | any-estimate rate | reading |
|---|---|---:|---|
| Mojang | absent from catalogue | 0.000% | the Jira has no such field |
| JFrog | all six present | 0.000% | fields exist; every issue leaves them null |

Collapsing the two would report that Mojang tracks estimates and never fills
them, which is false.

## Measured coverage

| population | issues | any estimate |
|---|---:|---:|
| Apache-wide, 646 projects | 1,014,926 | **2.557%** |
| Hadoop corpus (HADOOP+HDFS+YARN+MAPREDUCE) | 49,201 | **1.449%** |
| architectural subset (this study) | 323 | **0.000%** (expected 4.7, P≈0.009) |

Estimate use is a **per-project convention inside Apache**, not an Apache-wide
one: MESOS 32.94% of 10,197 issues, STDCXX 38.70%, USERGRID 37.51%, against
2.557% overall. The original "estimates are absent in Apache" conclusion was
drawn at the wrong level of aggregation.
