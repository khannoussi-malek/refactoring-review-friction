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
| 4 | **Convention changed mid-history** | spring-batch: `BATCH-` in 4,046 of 7,034 commits, but none in the 20 most recent sampled — a single rate averages two regimes | hand-sample + prefix scan |
| 5 | **Monorepo needs multi-key matching** | Hadoop: **26.2%** single-key → **92.3%** four-key → **97.8%** seven-key, same 28,290 commits | `scripts/citation_rate.py` |
| 6 | **Repository migrated across organisations** | Evergreen: Jira project key is `EVG` (9,191 citations) but recent commits use `DEVPROD` (2,785). `kiegroup/optaplanner` HTTP-redirects to `apache/incubator-kie-optaplanner` | `paper/intersection.json` |

## Why the taxonomy matters more than the individual rates

Modes 4, 5 and 6 are **silent**: they produce a plausible-looking low number
rather than an error. A single-key probe reads Hadoop as 26.2% and Evergreen as
71.7%, and nothing in either result signals that the key set is wrong. Four of
the 27 projects in `paper/intersection.json` needed multi-key matching —
DATALAB (`DLAB`+`EPMCDLAB`, renamed mid-history), TRINIDAD
(`TRINIDAD`+`ADFFACES`), DAOS (`DAOS`+`CART`), EVG (`EVG`+`DEVPROD`).

Modes 1, 2 and 3 are **disqualifying rather than measurable**: the project is
not a weak candidate, it is not a candidate. Scoring kata-containers as "0%
traceable" would place it on the same axis as a project that tries and fails.

The practical consequence is that project eligibility for issue-linked research
cannot be established from metadata. It requires reading commit messages from
the project itself, per project, before any outcome is measured.
