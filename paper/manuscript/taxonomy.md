# 5. Six ways a project cannot support an issue-linked study

**Every mode below was discovered *after* selecting the project, by probing it.
None is expressible in any published sampling frame.** GHS indexed 735,669
repositories as published in 2021 and exposes 35 fields per record today, of
which only `totalIssues` and `openIssues` touch issues, and both are
GitHub-issue counts (§2.3). All six were found the same way:
by reading commit messages, project by project.

| # | mode | worked example | evidence |
|---:|---|---|---|
| 1 | **GitHub Issues displaced Jira** | ShardingSphere: **5** Jira citations in 49,111 commits, against 30,746 GitHub-issue references | `paper/traceability_probe.json` |
| 2 | **No source repository exists** | RedHat RHBRMS: 86.00% estimate coverage on 2,400 issues — a product/documentation tracker with no code | `estimates_by_org.json`; repo resolution failed |
| 3 | **The tracker is downstream of the upstream repo** | kata-containers: **zero** `KATA-` keys in 19,807 commits; the Red Hat Jira tracks a product built from an upstream nobody asks to cite | `paper/intersection.json` (excluded, not scored) |
| 4 | **Convention changed mid-history** | spring-batch: `BATCH-` in **45.6%** of 7,035 commits overall, in **0 of the most recent 1,000** (back to 2021-06), and at exactly **0% in every year since 2020** — a single rate averages two regimes | full scan, `scripts/springbatch_recency.py` |
| 5 | **Monorepo needs multi-key matching** | Hadoop: **26.2%** single-key → **92.3%** four-key → **97.8%** seven-key, same 28,290 commits | `scripts/citation_rate.py` |
| 6 | **The cited key has no project record in the tracker** | Evergreen: commits cite `DEVPROD` (2,785) but the tracker holds only `EVG`. DataLab: commits cite `EPMCDLAB` (3,900) and `DLAB` (3,547); the tracker holds only `DATALAB` | `paper/intersection.json` |

## 5.1 The distinction that makes this a taxonomy rather than a list

**Modes 1, 2 and 3 are disqualifying rather than measurable.** The project is not
a weak candidate; it is not a candidate. Scoring kata-containers as "0%
traceable" would place it on the same axis as a project that tries and fails, and
would put a number where a category belongs.

**Modes 4, 5 and 6 are silent.** They produce a plausible-looking low number
rather than an error. A single-key probe reads Hadoop as 26.2% and Evergreen as
71.7%, and **nothing in either result signals that the key set is wrong.** Four of
the 27 projects in `paper/intersection.json` needed multi-key matching — DATALAB
(`DLAB`+`EPMCDLAB`), TRINIDAD (`TRINIDAD`+`ADFFACES`), DAOS (`DAOS`+`CART`), EVG
(`EVG`+`DEVPROD`).

This is the practical consequence, and it is the section's point: **project
eligibility for issue-linked research cannot be established from metadata.** It
requires reading commit messages from the project itself, per project, before any
outcome is measured.

## 5.2 Mode 6 in detail: two mechanisms, only one predictable

Measured across 2,686,282 issues, **project id → key is 1:1**: 0 ids carry more
than one key and 0 keys map to more than one id, against **326 ids carrying more
than one name**. Keys are stable identifiers *within a tracker snapshot*. So the
multi-key requirement is **not** key instability — it has two different causes.

**Concurrent siblings — predictable.** Several live projects share one repository.
Hadoop needs `HADOOP,HDFS,YARN,MAPREDUCE`; IntelDAOS needs `DAOS,CART`; Spring
Batch needs `BATCH,BATCHADM`. All of these project records exist in the tracker,
so the key set can be enumerated from the Jira instance before touching git.

**Superseded records — not predictable.** The key cited in commit messages has
**no project record in the tracker at all.** DataLab's git history cites
`EPMCDLAB` 3,900 times and `DLAB` 3,547 times; the Jira dump contains neither,
only `DATALAB` with 1,858 issues. Evergreen cites `DEVPROD` 2,785 times; the dump
contains only `EVG`. **Enumerating the tracker's projects cannot recover these
keys — they exist only in git.**

Both fail silently, which is the same property as modes 4 and 5: commit-to-ticket
matching runs on keys, and the key set cannot be derived from the tracker alone.

A related instance is a repository that resolves elsewhere:
`kiegroup/optaplanner` HTTP-redirects to `apache/incubator-kie-optaplanner`, with
identical history and PLANNER 1,629 either way. An earlier verdict that this was a
misresolved build-config repository was wrong and is corrected in
`PROJECT_STATE.md` §7.

## 5.3 Mode 6 measured across the whole probe, not just its worked examples

The probed key sets were derived empirically from commit messages (§3.2), and the
frozen public Jira corpus records every Apache project that existed at its
snapshot. Intersecting the two turns mode 6 from an anecdote into a count:
****six** of the keys this study probes have no project record in that corpus
at all**, and five of them are actually cited by commits.

| project | key with no tracker record | distinct keys cited under it |
|---|---|---:|
| pinot | `THIRDEYE` | 327 |
| calcite | `OPTIQ` | 85 |
| rocketmq | `RIP` | 35 |
| skywalking | `SWIP` | 11 |
| shardingsphere | `RS` | 8 |
| ozone | `OZONE` | 0 — probed, never cited |

Calcite is the clearest instance: `OPTIQ` was the project's name before it was
renamed, its keys are cited 85 distinct times in the repository's history,
and **no OPTIQ project exists in the tracker corpus**. Enumerating the tracker's
projects cannot recover that key. It exists only in git, and a probe that derived
its key set from the tracker — the natural thing to do — would silently miss every
commit that cites it.

## 5.4 One observed instance inside the eligible corpus

The taxonomy is not confined to the projects it disqualified. Among the 12 that
passed, **Sqoop's commits cite 790 distinct keys of which 122 have no record in
its tracker** (`paper/ticket_coverage.json`) — mode 6 operating inside a project
that clears the bar at 82.6%. Its ticket-side rate is computed over the 668 keys
that do resolve.

## 5.5 What a sampling frame would need

None of the six is derivable from repository metadata. Expressing them requires,
per candidate: the dominant reference channel (Jira keys against GitHub issues,
counted rather than assumed), the tracker's project-key set, the key set actually
appearing in commit messages, and the rate computed separately over recent history
to expose mode 4. All four are cheap. None is in GHS.

**One qualification, because the unqualified claim overstates the gap.** We say
above that the key set cannot be recovered from the tracker, and that stands: a
key cited only in git — `OPTIQ`, `EPMCDLAB`, `DEVPROD` — is not in the tracker to
be enumerated. But a substantial literature *does* recover missing issue–commit
links without relying on the commit message, beginning with ReLink [@wu2011relink] (Wu et al.,
ESEC/FSE'11) and continuing since, by learning from time proximity, author
identity and textual similarity between report and change (§2.4). Those methods
recover **links**, not **key sets**, and they presuppose a project already known
to be a candidate — which is the step this taxonomy is about. Modes 4–6 make a
project's *measured rate* wrong; link recovery can raise the true rate afterwards.
A sampling frame that exposed the four fields above would tell a researcher which
projects are worth pointing a link-recovery tool at, which is a different and
prior question.
