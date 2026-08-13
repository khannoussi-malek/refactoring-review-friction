# Six ways a project cannot support an issue-linked study

Every mode below was discovered **after** selecting the project, by probing it.
None is expressible in any published sampling frame: GHS indexes 735,669
repositories with 35 fields, of which only `totalIssues` and `openIssues` touch
issues, both GitHub-issue counts (`paper/PRIOR_WORK.md`).

| # | mode | worked example | evidence |
|---|---|---|---|
| 1 | **GitHub Issues displaced Jira** | ShardingSphere: **5** Jira citations in 49,111 commits, against 30,746 GitHub-issue references | `paper/traceability_probe.json` |
| 2 | **No source repository exists** | RedHat RHBRMS, 86.00% estimate coverage on 2,400 issues — a product/documentation tracker with no code | `estimates_by_org.json`; repo resolution failed |
| 3 | **Tracker is downstream of the upstream repo** | kata-containers: **zero** `KATA-` keys in 19,807 commits; the Red Hat Jira tracks a product built from an upstream nobody asks to cite it | `paper/intersection.json` (excluded, not scored) |
| 4 | **Convention changed mid-history** | spring-batch: `BATCH-` in **45.6%** of 7,035 commits, **0 of the most recent 1,000** (back to 2021-06), and **0% in every year since 2020** — a single rate averages two regimes | `scripts/springbatch_recency.py` |
| 5 | **Monorepo needs multi-key matching** | Hadoop: **26.2%** single-key → **92.3%** four-key → **97.8%** seven-key, same 28,290 commits | `scripts/citation_rate.py` |
| 6 | **The cited key has no project record in the tracker** | Evergreen: commits cite `DEVPROD` (2,785) but the tracker holds only `EVG`. DataLab: commits cite `EPMCDLAB` (3,900) and `DLAB` (3,547); the tracker holds only `DATALAB`. `kiegroup/optaplanner` HTTP-redirects to `apache/incubator-kie-optaplanner` | `paper/intersection.json` |

## Why the taxonomy matters more than the individual rates

Modes 4, 5 and 6 are **silent**: they produce a plausible-looking low number
rather than an error. A single-key probe reads Hadoop as 26.2% and Evergreen as
71.7%, and nothing in either result signals that the key set is wrong. Four of
the 27 projects in `paper/intersection.json` needed multi-key matching —
DATALAB (`DLAB`+`EPMCDLAB`, superseded records — see below), TRINIDAD
(`TRINIDAD`+`ADFFACES`), DAOS (`DAOS`+`CART`), EVG (`EVG`+`DEVPROD`).

Modes 1, 2 and 3 are **disqualifying rather than measurable**: the project is
not a weak candidate, it is not a candidate. Scoring kata-containers as "0%
traceable" would place it on the same axis as a project that tries and fails.

The practical consequence is that project eligibility for issue-linked research
cannot be established from metadata. It requires reading commit messages from
the project itself, per project, before any outcome is measured.

## Mode 6 in detail: two mechanisms that both break single-key probes

Measured across 2,686,282 issues, **project id → key is 1:1**: 0 ids carry more
than one key and 0 keys map to more than one id, against **326 ids carrying more
than one name**. Keys are stable identifiers *within a tracker snapshot*. The
multi-key requirement therefore is not key instability — it has two different
causes, and only one is predictable in advance.

**Concurrent siblings — predictable.** Several live projects share one
repository. Hadoop needs `HADOOP,HDFS,YARN,MAPREDUCE`; IntelDAOS needs
`DAOS,CART`; Spring Batch needs `BATCH,BATCHADM`. All of these project records
exist in the tracker, so the key set can be enumerated from the Jira instance
before touching git.

**Superseded records — not predictable.** The key cited in commit messages has
**no project record in the tracker at all**. DataLab's git history cites
`EPMCDLAB` 3,900 times and `DLAB` 3,547 times; the Jira dump contains neither,
only `DATALAB` with 1,858 issues. Evergreen cites `DEVPROD` 2,785 times; the
dump contains only `EVG`. Enumerating the tracker's projects cannot recover
these keys — they exist only in git.

**Both fail silently.** A single-key probe reads Hadoop as 26.2% and DataLab as
some fraction of its true rate, and neither result carries any signal that the
key set is wrong. This is the same silent-failure property as modes 4 and 5:
commit-to-ticket matching runs on keys, and the key set cannot be derived from
the tracker alone.
