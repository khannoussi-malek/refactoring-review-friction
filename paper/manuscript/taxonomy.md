# 5. Six ways a project cannot support an issue-linked study

Drafted from `paper/eligibility_failure_modes.md` (`5179907`).

**Every mode below was discovered *after* selecting the project, by probing it.
None is expressible in any published sampling frame.** GHS indexes 735,669
repositories with 35 fields, of which only `totalIssues` and `openIssues` touch
issues, and both are GitHub-issue counts (§2.3). All six were found the same way:
by reading commit messages, project by project.

*Note on mode 6.* `README.md` §5 labels mode 6 "repository migrated across
organisations". That framing was **superseded on 2026-07-25** once id→key
stability was measured (`PROJECT_STATE.md` §2, `5179907`). The current statement
is below, and it is the one this paper uses.

| # | mode | worked example | evidence |
|---:|---|---|---|
| 1 | **GitHub Issues displaced Jira** | ShardingSphere: **5** Jira citations in 49,111 commits, against 30,746 GitHub-issue references | `paper/traceability_probe.json` |
| 2 | **No source repository exists** | RedHat RHBRMS: 86.00% estimate coverage on 2,400 issues — a product/documentation tracker with no code | `estimates_by_org.json`; repo resolution failed |
| 3 | **The tracker is downstream of the upstream repo** | kata-containers: **zero** `KATA-` keys in 19,807 commits; the Red Hat Jira tracks a product built from an upstream nobody asks to cite | `paper/intersection.json` (excluded, not scored) |
| 4 | **Convention changed mid-history** | spring-batch: `BATCH-` in 4,046 of 7,034 commits, and none in the 20 most recent sampled — a single rate averages two regimes | hand-sample + prefix scan |
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

## 5.3 One observed instance inside the eligible corpus

The taxonomy is not confined to the projects it disqualified. Among the 12 that
passed, **Sqoop's commits cite 790 distinct keys of which 122 have no record in
its tracker** (`paper/ticket_coverage.json`) — mode 6 operating inside a project
that clears the bar at 82.6%. Its ticket-side rate is computed over the 668 keys
that do resolve.

## 5.4 What a sampling frame would need

None of the six is derivable from repository metadata. Expressing them requires,
per candidate: the dominant reference channel (Jira keys against GitHub issues,
counted rather than assumed), the tracker's project-key set, the key set actually
appearing in commit messages, and the rate computed separately over recent history
to expose mode 4. All four are cheap. None is in GHS.
