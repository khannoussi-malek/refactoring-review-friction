# 2. Related work

Drafted from `paper/PRIOR_WORK.md` (`215b10f`) and `paper/SATD_NOVELTY.md`
(`5b50ef1`). Reorganisation of verified findings, not new argument.

## 2.1 Per-project linkage rates are already published

**This paper makes no first-to-measure claim, and the claim it originally made was
withdrawn.** Two prior works publish per-project issue–commit linkage rates, one
of them as an explicit table column.

**Rath & Mäder 2019, SEOSS 33** (*Data in Brief* 25:104005) publishes, per
project, change-set count and **"Linked Change Sets [%]"** for 33 projects — the
same quantity as our commit-side rate. Their spread is 8.11%–97.13%; ours is
0.01%–98.3% across 38. Four of five overlapping projects agree within **3.3pp**
on corpora seven years apart:

| project | SEOSS 2019 | this probe 2026 | Δ |
|---|---:|---:|---:|
| Hadoop | 97.13% (27,776 commits) | 97.8% (28,290, 7-key) | +0.7pp |
| Hive | 96.34% (11,179) | 97.0% (18,213) | +0.7pp |
| HBase | 90.06% (14,331) | 92.5% (21,220) | +2.5pp |
| ZooKeeper | 87.12% (1,600) | 90.4% (2,718) | +3.3pp |
| Flink | 41.98% (12,419) | 66.0% (38,219) | **+24.1pp** |

That agreement is **independent cross-corpus validation of the measure** and is
treated here as such. Flink's 24.1pp gap is scope rather than error — their
snapshot holds 12,419 commits against our 38,219, so we cover a decade in which
its citation practice could have changed — and **the truncation check that would
confirm this has not been run** (`PROJECT_STATE.md` §6, task 16).

SEOSS's selection criteria matter for our argument: a project must "continuously
capture vertical and horizontal trace links among these artifacts". So a
traceability criterion **is** used for selection — but as a qualitative
requirement. No cut-off is stated, no rejected candidates are reported, and having
selected on trace links the dataset still admits Errai at 8.11%.

**Rath et al., ICSE 2018** (*Traceability in the Wild*, arXiv:1804.02433)
publishes **both directions** for six Git+Jira projects, and is the closest
precedent to our divergence result. Commit side: "approximately 48% of the commits
were not linked to any issue", with a per-project spread from 15% unlinked in
Derby to ~76% in Maven. Ticket side: "approximately 43.3% of improvements and
42.4% of bugs have no commits associated with them" — Derby works out to 51.8%
ticket-side coverage. Our 12 passing projects run 12.0%–69.0% ticket-side,
straddling their figure. Their sentence — "different practices exist across
different projects, leading to huge disparities in the extent to which issue tags
are added to commit messages" — is our corpus-feasibility finding stated
qualitatively in 2018.

Selection there was also informal: the six were chosen because each "largely
followed the practice of tagging commits with issue IDs". Again no threshold.

**Vieira et al. 2019** (PROMISE'19, 55 Apache projects, >70,000 bug reports) may
or may not report per-project linkage. **Unverified:** ACM DL, ResearchGate and
figshare all returned 403 to unauthenticated fetches, so neither the paper body
nor the package manifest could be read. Recorded as unverified rather than
characterised. Note its selection is already conditioned on *resolution = Fixed*,
which pre-selects tickets that were worked, so any rate it reports would not be
comparable to ours without care.

## 2.2 What is therefore new here

Positioned against the above rather than against an assumed gap:

1. **A pre-registered numeric bar applied before any outcome, with reported
   attrition.** Both prior works select on trace links informally and report the
   rate afterwards; neither states a threshold, an attrition count, or which
   candidates were rejected. Ours is fixed in `predictions/PREDICTIONS.md`
   (`ca076a9`) before any project was cloned, and never moved.
2. **The population finding.** 12 of 38 pass and *all 12 are one ecosystem*.
   SEOSS's own table contains the ingredients — Apache at the top, JBoss at the
   bottom — but does not draw the inference.
3. **Both reference channels measured together.** No prior work counts
   GitHub-issue references alongside Jira keys, which is what shows the bar
   selects a *tracker* rather than a discipline.
4. **The commit-side/ticket-side divergence framed as a sampling-frame warning.**
   Rath 2018 reports both directions; nobody frames the divergence as a threat to
   using a high commit-side rate to justify a corpus. Kylin at 83.9% against
   12.0% is the sharpest case.
5. **The six-mode taxonomy**, and that none of it is expressible in any published
   frame.

## 2.3 The standard sampling frame cannot express the criterion

**Dabic et al. 2021, GHS** (*Sampling Projects in GitHub for MSR Studies*,
MSR'21) is the standard sampling tool and indexes **735,669 repositories**. A
record carries **35 fields**, queried from the live API rather than read off the
paper's Table I, which is an image. Only **`totalIssues`** and **`openIssues`**
touch issues at all, and both are GitHub-issue counts. There is no field for
issue-tracker type, external tracker usage, issue–commit linkage, traceability, or
commit-message convention. The one adjacent feature, filtering by issue label, is
described in the paper as "still under development".

The consequence is the actionable one: a researcher sampling with GHS gets stars,
commits, contributors and license, then discovers post hoc that 26 of 38
candidates are unusable. That is what happened here.

## 2.4 Refactoring and self-admitted technical debt

Included because it establishes what the *record-level* literature has not
measured, and it bounds what this paper claims.

**Iammarino et al. 2021** (*J. Syst. Softw.*, on SATD removal and refactoring)
and **Esfandiari 2023** (ICCKE, arXiv:2404.01950, commit tags, 77 projects) both
study SATD and refactoring **strictly at same-commit co-occurrence**. Iammarino
covers four projects with no temporal analysis, its tightest analysis being
same-file at n=201. Esfandiari already reports *move class* as the refactoring
most associated with debt activity. Neither measures an interval.

An architectural-debt time-to-fix literature is active — arXiv:2605.16133 (May
2026) and arXiv:2501.15387 — using Jira issues at file granularity with **no
refactoring detection**.

Two things follow. First, the record channels this paper measures are the same
channels that literature depends on, so its exposure is the same. Second, the
successor design this study points to — a SATD-comment-to-refactoring interval,
entity-level, refactoring-detected — is **not proposed in this paper**; it is a
separate registered report whose novelty margin is a conjunction of three choices
and is recorded as gated on external judgment (`paper/SATD_NOVELTY.md`).

## 2.5 Detector validity

RefactoringMiner is the detector. Its TypeScript support was complete 2026-05-24,
two months old at measurement, and **has no independent validation in the
literature**. One defect was traced and reported upstream: 160
`interface → class` false positives in a single commit, arising from type aliases
having no representation in the tool's class model
([tsantalis/RefactoringMiner#1124](https://github.com/tsantalis/RefactoringMiner/issues/1124),
filed 2026-07-25; `paper/RM_TYPESCRIPT.md`). That finding is a separate paper and
appears here only as a bound on the TypeScript column of Table 2.
