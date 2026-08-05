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
treated here as such. Flink's 24.1pp gap is scope rather than error, and unlike
in earlier drafts this is now tested rather than asserted: restricting our probe
to the **earliest 12,419 commits** — the change-set count SEOSS publishes, and the
only quantity the two studies share — gives **5,214 / 12,419 = 41.9841%** against
their **41.98%**, a gap of **+0.0041pp**. All five overlapping projects agree once
scope is matched.

**On the exactness of that match, which invites suspicion and should not.** The
quantity is a deterministic count — commits whose message matches a key pattern,
over a fixed and identically bounded commit range — not an estimate, and it
carries no sampling error. Two correct implementations of the same well-specified
count *should* agree exactly; a disagreement would indicate a difference in
specification, not noise. Exact agreement is only suspicious between estimators
that have sampling error, and this has none. The two figures also reach us by
independent paths: SEOSS's 41.98% is transcribed from their published table, and
41.9841% is a fresh scan of a clone at a pinned sha. **What the match confirms is
scope alignment, and nothing beyond it.**

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
2. **The population finding.** 12 of 38 pass and no project outside one
   ecosystem clears the bar. SEOSS's own table contains the ingredients — Apache
   at the top, JBoss at the bottom — but does not draw the inference. The
   ecosystem label is a hand classification and §4.1 reports the measured
   variables that failed to replace it.
3. **Both reference channels measured together.** No prior work counts
   GitHub-issue references alongside Jira keys, which is what shows the bar
   selects a *tracker* rather than a discipline.
4. **The arithmetic ceiling.** The bound TRR ≤ CSR × commits / tickets, the
   decomposition of the ticket-side rate into that ceiling and a residual, and
   the finding that in this corpus the residual is nearly constant while the
   ceiling varies six-fold (§3.1.4, §4.2). No prior work reports commits per
   ticket alongside a linkage rate, which is what makes the two rates look
   commensurable when they are not.
5. **The ticket-side rate measured across the whole probe**, including the 26
   projects the bar **rejected** — Rath 2018 reports it per issue *type*, and only
   for the six projects it selected. *(Whether the quantity is also newly
   **named** depends on the Bachmann determination in §2.4 and is
   **[PENDING]**.)*
6. **The six-mode taxonomy**, and that none of it is expressible in any published
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

## 2.4 The bug-side linkage literature, and what it already settled

The commit-side/ticket-side asymmetry this paper measures was studied on the
bug-side a decade and a half ago, and that literature is the direct ancestor of
§4.2. It is set out here rather than merely listed, because two of its findings
bound what this paper can claim.

**Bachmann et al. (FSE'10), *The Missing Links: Bugs and Bug-fix Commits*** —
Adrian Bachmann, Christian Bird, Foyzur Rahman, Premkumar Devanbu and Abraham
Bernstein — is the closest ancestor. They engaged a core Apache HTTP Server
developer to annotate **493 commits over a six-week period** exhaustively, using
a purpose-built tool (Linkster), to establish ground truth rather than infer it
from commit messages. Against that ground truth they found that **only 47.6% of
bug-fix-related commits are documented in the bug tracking database**. Their
target is the completeness of the *link*, established by expert annotation on one
project over one window; ours is a per-project rate over a whole tracker,
established mechanically. Their design is far stronger on ground truth and far
narrower in scope; ours is the reverse.

> **[DETERMINATION PENDING]** Whether the ticket realisation rate of §3.1 is the
> same quantity Bachmann et al. measured, or a distinct one, is **not settled in
> this draft**. The argument for distinctness is that §3.1.1 admits every issue
> type and every status and conditions on nothing, whereas Bachmann conditions on
> bugs and bug-fix commits. That argument has not been adjudicated against the
> paper's own text, and the naming claim in §3.1 stands or falls with it. See
> `paper/REVISION_LOG.md`, GATE.

**Bird et al. (ESEC/FSE'09), *Fair and Balanced? Bias in Bug-Fix Datasets*** — C.
Bird, A. Bachmann, E. Aune, J. Duffy, A. Bernstein, V. Filkov and P. Devanbu — is
the reason any of this matters. Missing links are not missing at random, so a
dataset built from linked records is a biased sample of the work, and models
fitted to it inherit the bias. **This is the same argument our §7.3 makes for
architectural change**, arrived at independently and seventeen years later, and
we cite it as the prior statement of the principle rather than as a parallel.

**Nguyen, Adams and Hassan (WCRE'10), *A Case Study of Bias in Bug-Fix
Datasets*** replicates that bias analysis. *(The review that prompted this
revision cited this work as MSR'10 and characterised it as a replication on a
system with near-perfect linkage; the venue is WCRE'10, and the
near-perfect-linkage characterisation could not be verified from an accessible
copy, so it is not asserted here — see `paper/REVISION_LOG.md`.)*

**Herzig, Just and Zeller (ICSE'13), *It's not a bug, it's a feature: how
misclassification impacts bug prediction*** bears directly on §3.1.1's decision to
admit all issue types. In a manual examination of **more than 7,000 issue reports
across five open-source projects they found 33.8% misclassified** — filed as bugs
but resolving to a feature, a documentation update or an internal refactoring —
and **39% of files marked defective never had a bug**. Our denominator admits
every type precisely so that no misclassification can move a ticket in or out of
it. That immunises the ticket realisation rate against the Herzig effect, and it
is also why our rate is *not* comparable to any rate computed on a
resolution-filtered or type-filtered population, including Vieira et al.'s.

**Automated link recovery is the standing partial answer to modes 4–6.** ReLink
(Wu, Zhang, Kim and Cheung, ESEC/FSE'11) learns the features of explicit links —
time proximity, author identity, textual similarity between the bug report and
the change — and recovers missing ones at accuracy well above the traditional
regex heuristics, and a substantial literature has followed it. §5.5 and §7.2
argue that a project's key set cannot be recovered from its tracker, which
remains true: ReLink and its successors recover *links*, not *key sets*, and they
operate on a project already known to be a candidate. But the unqualified claim
that missing links are unrecoverable would overstate the gap, and §5.5 is
qualified accordingly.

## 2.5 Refactoring and self-admitted technical debt

Included because it bounds what this paper claims. **Iammarino et al. (2021,
JSS)** and **Esfandiari & Sami (ICCKE 2023)** both study SATD and refactoring
strictly at same-commit co-occurrence — Iammarino over four projects with no
temporal analysis, its tightest cut being same-file at n=201; Esfandiari over 77
projects, already reporting *move class* as the refactoring most associated with
debt activity. Neither measures an interval. An architectural-debt time-to-fix
literature is separately active (arXiv:2605.16133, arXiv:2501.15387).

Two things follow. The record channels this paper measures are the channels that
literature depends on, so its exposure is ours. And the successor design this
study points to is **not proposed here**; it is a separate registered report
gated on external judgment (`paper/SATD_NOVELTY.md`).

## 2.6 Detector validity

RefactoringMiner is the detector. Its TypeScript support was complete
2026-05-24, two months old at measurement, and has no independent validation we
could find in the literature. One defect was traced and reported upstream: 160
`interface → class` false positives in a single commit, from type aliases having
no representation in the tool's class model
([tsantalis/RefactoringMiner#1124](https://github.com/tsantalis/RefactoringMiner/issues/1124),
filed 2026-07-25). That finding is a separate paper and appears here only as a
bound on the TypeScript column of Table 2.
