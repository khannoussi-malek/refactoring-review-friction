# 6. Threats to validity

Assembled from `paper/ERA_AUDIT.md` (`e0d76ef`), `paper/ALIASING_HADOOP.md`,
`paper/matcher_validation.md`, `SUI_FINDINGS.md`, `paper/numbers.md` and
`PROJECT_STATE.md` §7. Several of the items below are things this study got wrong
and corrected. **They are stated as the paper's credibility, not as its
embarrassments** — a methods paper about record quality that concealed its own
record would be self-refuting.

## 6.1 Construct validity

**The measure is 97.5% precise, and two of its failure modes were untestable.**
Key matching was validated on a seeded 200-commit manual sample across the 12
eligible projects: precision **195 of 200 = 97.5%** (Wilson 95% CI 94.3–98.9%),
corpus-weighted 97.7%. The residual is 4 reverts and 1 backport. But two of the
five enumerated failure categories **could not have fired**: `version_string` is
near-unreachable given a pattern requiring the upper-case key followed by `-` and
digits, and `foreign_key` is unreachable for 11 of the 12, because each project is
probed with its own key set and only Ozone is multi-key with both keys its own.
**The single-key → multi-key result on Hadoop (26.2% → 92.3% → 97.8%) is therefore
not validated by that sample**, Hadoop being the only true monorepo in the study
and not among the 12 (`paper/matcher_validation.md`).

**A key matched from a branch name is counted as a genuine reference.** Two
mechanisms occur in the sample: merge subjects (`Merge branch 'master' into
KNOX-998-Package_Restructuring`) and svn trailers naming a branch
(`.../branches/TEZ-1@1471779`). The ticket association is correct even though the
commit does not implement the ticket. The five failure categories were fixed
before labelling and do not cover this case, so it was counted genuine and is
recorded here rather than assigned an invented category.

**Ticket-side coverage counts keys that resolve in the tracker.** Sqoop cites 790
distinct keys of which 122 have no tracker record, so its ticket-side rate rests
on the 668 that resolve (§5.3). This is mode 6 inside a passing project, and it
means ticket-side rates are, strictly, coverage of *resolvable* tickets.

**The 38-project extension uses a different denominator source, and the
validation figure the earlier draft quoted was for a different approximation.**
§4.3 measures the ticket realisation rate for all 38 projects against the frozen
public Jira corpus rather than a second live fetch, aligning numerator and
denominator in issue-number space (§3.1.3). **Two approximations are stacked**:
number-capping, and substituting a frozen snapshot for the live tracker. The
0.45pp / 2.14pp figure earlier drafts quoted validates only the first. The
end-to-end error of the combination Table 3 actually uses is **1.76pp mean /
11.91pp max**, the worst case being Kylin; excluding Kylin it is 0.84pp mean and
**2.93pp max, with 11 of 12 inside 3pp**. **Quote the end-to-end figure.**

**And the estimator is applied entirely outside its validated range.** The twelve
validation projects span commit-side **82.6–98.3%**; the twenty-one that carry
the §4.3 association span **10.5–78.1%**. The ranges are **disjoint — 0 of 21**
applied projects fall inside the validated one. The error mechanism is
tracker-numbering density rather than commit hygiene, and within the twelve the
error does not track the commit-side rate (rho = −0.16, n = 12), so there is a
reason to expect the extrapolation to hold — but it is a reason, not a
validation, and **any claim whose margin is smaller than 11.91pp is not safe on
this estimator.** The claims that are: the ceiling identity (exact arithmetic,
not estimated); the eligibility result (commit-side only); the taxonomy. The
claims that are not: any per-project ticket-side comparison in Table 3 closer
than ~12pp, and the passing-versus-dropped median gap of 0.6pp, which is far
inside the noise and is reported as such.

Four further things can break the estimator, and all four occur in this corpus:

1. **Trackers with gaps.** Number-capping assumes a tracker holding N issues holds
   approximately the first N numbers. Issues moved or deleted break that, and the
   estimator then undercounts. This is the largest single validation error in the
   set and the direction is always downward.
2. **Repositories whose history does not span the snapshot era.** Where a
   repository has been truncated or re-initialised, almost none of its cited keys
   fall inside the frozen range and the estimated rate collapses towards zero.
   That is a *true* statement about what is recoverable from the repository as it
   now stands, and a badly misleading one if read as a statement about whether the
   project's tickets were ever worked. Affected projects are flagged in Table 3
   with the share of cited keys that postdate the snapshot — **99.72% for Kylin
   (709 of 711), not 100%**; an earlier draft printed 100%, which contradicts the
   non-zero numerator that produces Kylin's 0.04%.

   **This defect is not confined to the frozen arm, and that is the more serious
   finding.** Kylin's pinned commit reaches **968 commits beginning 2022-08-01**,
   **7.5% of the 12,937 on the repository's refs**, against a tracker of 5,931
   issues and a repository that begins 2014-05-13. Its *live* 12.0% is therefore
   also measured over a four-year window against a twelve-year tracker. Earlier
   drafts made that 12.0% the paper's flagship example while dismissing the frozen
   0.04% as an artefact; **both are the same artefact**, and the example has been
   moved to Hive (§4.2.1). Three other projects have a pinned branch starting
   after their repository — Jena (49.0% of refs), Karaf (45.4%), James (89.4%, by
   eight days) — and none approaches Kylin's severity
   (`scripts/revision_metrics.py`).
3. **Denominators too small to carry a rate.** Several trackers hold only a
   handful of issues in the frozen corpus. Projects with fewer than 500 are
   excluded from the association statistic and shown in the table with the
   exclusion marked.
4. **Keys with no tracker record at all.** Some probed keys have no project record
   in the frozen corpus. These are taxonomy modes 1 and 6, not low rates, and they
   are **excluded rather than scored as 0%** — scoring them would put a number
   where a category belongs, which is the error §5.1 exists to prevent.

**The truncation caveat on Table 1 is not withdrawn.** The 12.0–69.0% range from
the live measurement remains within-passing variation, computed on the twelve that
had already cleared the bar. §4.3 does not extend that measurement; it is a
different estimator against a different snapshot, and it is reported alongside
rather than merged into it.

**"345 of 349 episodes traceable to 323 tickets" — the unit matters.** An estimate
is a property of a ticket, not an episode; several episodes share a ticket. An
earlier draft used 0/345 where 0/323 is correct (`PROJECT_STATE.md` §7).

**Two unrelated quantities are both 92.3% and are labelled apart.** 92.3%-A is
traceability (26,125 / 28,290 Hadoop commits citing a key, four-key probe);
92.3%-B is RefactoringMiner chunk coverage (3,175 / 3,440). Different numerators,
denominators, scopes and claims. This paper uses **92.3%-A only**
(`paper/numbers.md` §2).

## 6.2 Internal validity — instruments that decay, and one that terminates

Relevant because it bounds what the Apache column of Table 2 can contain.

| instrument | ≤2018 | 2019–21 | ≥2022 |
|---|---:|---:|---:|
| Jira status transitions — architectural tickets reaching `Patch Available` | 147 of 150 | 98 of 130 | **6 of 43** |
| CI verdicts — architectural tickets carrying ≥1 Hadoop-QA comment | 145 of 150 (**96.7%**) | 66 of 130 (**50.8%**) | **0 of 43 (0.0%)** |

**The CI channel terminates in 2021.** Not decays — there is no architectural
ticket after 2021 with a CI verdict in Jira, so no additional mining extends the
series, and the mid-window is half-blind rather than merely thinner. The common
cause of both is the 2019–20 GitHub migration: work moved to pull requests and the
Jira status field went unmaintained.

Two further consequences, both already disclosed in the source memos and
generalised by the era audit: status-derived timings are **not comparable across
module tiers** at all (cloud connectors drive the Jira workflow in 28.3% of
tickets against 86.2% elsewhere, on n=13 connector tickets — thin enough that the
proportion is quoted and nothing is leaned on it), and the phase decomposition
rests on **6 architectural tickets after 2021**, so any claim that build-versus-
merge behaviour *persists* is unsupported.

**714 / 714 = 100.0% is true by construction and is never reported as
validation.** The analysis frame is built from commits that cite tickets, so a
ticket with no citing commit cannot enter it and the match rate cannot come out at
anything else. What it establishes is that the clock is *applicable* to every
ticket in the frame — a statement about the frame, not about coverage of Hadoop's
tickets. **The real coverage question is unanswered and is not computed anywhere**
(`paper/numbers.md` §4).

## 6.3 Author identity aliasing does not affect the Hadoop measures

The TypeScript pilot found one developer appearing as two email addresses with
opposite workflow habits, which corrupted every author-level statistic in that
pass. The obvious question is whether the Hadoop analysis has the same defect.

**It does not, and this was measured rather than assumed.**
`scripts/social_centrality.py` keys on the git author **name** (`%an`), so the
two-emails-one-person case is merged by construction. Hadoop's *raw* aliasing is
worse than the pilot's — 1,035 emails resolve to 797 identities, and 96 emails
span multiple author names covering 27,307 commits, 35.2% of Hadoop's full
`git log --all` history of 77,529 commits, which is the universe
`scripts/sui/identity.py` scans and is neither the 8,919 mined nor the 28,290
probed on trunk — but the
effect on the derived measures is null: mean `top1_share` 0.1545 by name against
0.1495 by email over 112 modules, **paired Wilcoxon p=0.3651**, no systematic
direction. Aliasing severity scales inversely with contributor count, so the same
defect is critical in a 53-author repository and irrelevant in an 800-author one;
it must be measured per corpus (`paper/ALIASING_HADOOP.md`,
`scripts/sui/ALIASING_NOTE.md`).

**One difference was never verified.** The `reviewer_pool` variable uses a third
identity namespace — Jira comment authors — and the two arms read it by different
paths (`c["author"].get("name")` for architectural tickets, `c.get("author")` for
controls). Immaterial in practice, since `reviewer_pool` is null everywhere
(`triage~reviewer_pool` rho = 0.0010, p = 0.988), but unverified rather than
checked.

## 6.4 Detector coverage was lost non-randomly, and the obvious bias was tested

**A 93%-missing year was found and repaired.** The first RefactoringMiner run lost
three chunks to hangs, and the loss was *clustered*: 75 of 81 commits in 2024
(93%) were absent, against 2–8% in every other year. Every temporal result from
that pass was invalid, including a "zero architectural commits in 2024" that was a
measurement hole. A targeted re-run recovered 68 commits and lifted coverage
88% → 93%. **Coverage loss in chunked detector runs must be checked for
clustering, not merely reported as a percentage.**

**The natural worry that loss is biased toward large commits was tested and
rejected.** Within the detector's actual scope (`root..HEAD`, 1,198 commits; 1,057
analysed, 141 lost), lost commits are *smaller* — median churn 14 lines against 32,
p=0.0022 — with no enrichment in the top churn decile (9.6% against 12.8%,
p=0.23). The mechanism is structural: the watchdog kills a whole chunk, so ~30
commits die because one of them hung, regardless of their own size.

**A first attempt at that test was wrong and is kept as a caution.** It compared
against `git log --all`, so the "missing" set was contaminated with 930 commits on
other branches that were never in scope, and it produced the opposite, spurious
conclusion that lost commits were larger. The comparison set for a coverage-bias
test must be exactly the range the tool was asked to analyse.

## 6.5 Single-rater limits, and the one measure that escapes them

**Inter-rater agreement cannot be computed by one person, so no measure requiring
manual coding carries a claim in this paper.** Two instruments are affected and
both are reported **as findings about the instrument**, never as instruments the
paper's claims rest on:

* the codebook's keyword rule for structural review discussion — **≈25% precise**
  (5 of 20 flagged comments genuinely structural), ≈5% miss (1 of 20 unflagged),
  on a 40-comment single-rater pass, with no κ;
* the TypeScript commit-message rule — **recall 3 of 96 = 3.1%**, **precision 3 of
  10 = 30%**.

Their role is to establish that keyword-based detection over-counts roughly
fourfold and finds 3% of the work, which is a validity result about a method other
studies use.

**The exception is argued rather than asserted.** The 200-commit matcher check is a
mechanical determination against a written rule with categories fixed before
labelling, not a coded judgment where the construct lives in the rater's head. It
is made **auditable rather than agreed**: `paper/matcher_sample.json` carries all
200 messages and `paper/matcher_labels.json` every label, so any reader can
re-check the sample without redrawing it.

**The architectural-episode gold set has no second rater and is therefore not
used** to support any claim here.

**One coincidence in the rater pilot is disclosed because it looks like tuning
and we cannot prove it is not.** `paper/LLM_RATER_PILOT.md` reports that
six comments change label under the opposite ordering of two codebook rules, and
**five of the six fall in the flagged bucket** — the margin moves 3/12/5 to
3/7/10, a swing of exactly five. The kappa ceiling is computed on that bucket, so
five is the count that drives it, and five moves the attainable ceiling from
0.491 to **0.840**. *(Corrected 2026-08-05: this paragraph previously credited the
0.840 to the six re-labelled comments. Six is the total across both buckets; the
ceiling is indexed by flagged-bucket moves alone. No figure changes.)*

**Five is also exactly the count that maximises the ceiling over every possible
count**: four gives 0.765, six gives 0.837, seven gives 0.833. The six were
selected by a stated semantic criterion, they are
individually defensible, and the finding is robust at 0.833–0.840 across plus or
minus two comments — but the criterion was applied by the same party that
reported the resulting number, and it landed on the global maximum. Stated here
rather than left for a reader to find (`audit/JUDGMENTS.md` §3).

## 6.6 Definitions fixed after seeing data, and thresholds held when they hurt

**The abstraction-versus-relocation split was defined post hoc**, after seeing the
triage numbers it was later used to analyse. Three definitions — any-rule,
pure-vs-pure, continuous share — give the same answer, which is reassuring and not
a substitute for pre-registration. Fully adjusted the effect is ×1.54 [0.97,
2.43], p=0.068, n=319.

**The estimate conclusion was drawn at the wrong level of aggregation and is
self-corrected.** "Effort estimates absent in Apache (0%)" was replaced by three
numbers that travel together: **2.557%** Apache-wide (25,949 / 1,014,926),
**1.449%** in the Hadoop corpus (713 / 49,201), **0 of 323** architectural tickets
— expected 4.7, P ≈ 0.009 under a naive binomial. Architectural tickets are not a
random draw and the non-randomness could run either way, so the deficit is
suggestive on thin evidence, not an established effect.

**A threshold was held during a failed replication when lowering it would have
rescued two projects.** The vendor-share tier rule was frozen at ≥0.40 before any
held-out outcome was observed. HBase (maximum share 0.33) and Phoenix flagged
nothing at that cut, so neither could be tested. **The threshold was not lowered.**
The rule then failed 0 of 3 where it could be tested. That the fix was available
and declined is recorded deliberately (`replication/REPLICATION.md`,
`PROJECT_STATE.md` §2 row 07-25).

**The eligibility bar was likewise fixed before any project was cloned** and never
moved. Lowering it to 60% would have added nine projects and widened the family.

## 6.7 External validity

**One mined project, one ecosystem.** All 12 eligible projects are
Hadoop-ecosystem, and depth beyond Hadoop was not reachable. The corpus bound is
therefore a finding and a limit at once: results about Apache/Jira/Java
traceability generalise to Apache/Jira/Java.

**At 12 projects the design is not powered, whatever the corpus size.** Effective n
is capped at P/ICC by between-project correlation — a ceiling of 600 at ICC 0.02
against the 769 the effect needs. The direction of the bias is bad: these twelve
share contributors, committers, review norms and in several cases build and CI
infrastructure, so this sample's ICC is higher than a random sample's. **The ICC
itself is unmeasured, and was deliberately not estimated from the four available
clusters**, because between-cluster variance is not estimable at n=4 and the
estimate must come from the pooled study as a first stage
(`replication/CORPUS_FEASIBILITY.md`).

**The TypeScript column is one repository, one company, and exploratory.**
`BearStudio/start-ui-web`, 1,199 commits, 93% detector coverage, **n=28
architectural PRs**. `SUI_FINDINGS.md` is marked EXPLORATORY throughout and every
p-value in it is uncorrected and hypothesis-generating. **Only counts and
proportions from it are used here** — 3 of 96, 7%, 30 of 96 — never a test. The
repository is also a starter template whose product is tracking the frontend
stack, so migration-driven churn is unusually large (architectural commits
co-occurring with a dependency-manifest change are 13× larger).

**PR routing there is not arbitrary**, which bounds what the 31% means:
architectural commits that go through a PR are five times larger and four times
more abstraction-heavy than those pushed to main. The 69%-unreviewed figure is a
statement about that repository's workflow, not a general rate.

**The Apache commit-message cell of Table 2 is empty because this study did not
instrument it.** The Hadoop architectural corpus was built by AST-level detection
and never compared against message text, so no recall figure comparable to the
TypeScript column's 3.1% exists. It is computable in principle and is the most
obvious extension. Note also that the 25%-precision codebook figure measures
**review comments**, a fourth channel, and is not a commit-message result
(`paper/table2_visibility.md`).

## 6.8 Provenance of the work itself

**Built by one person in three working sessions alongside full-time employment**,
with a committed history spanning 19 July – 8 August 2026: the three sessions of
19–25 July, a completion pass on 30 July, the MSR major revision of 5 August and
a correction pass on 8 August. That is what set corpus depth at one project and
left no second rater; it
is stated because it explains the shape of the limitations above rather than
excusing them.

**The Jira caches are frozen with no rebuild script**, deliberately. Jira is live
and a re-fetch returns different state, so a rebuild script would imply a
reproducibility that does not exist. The archive is 2,491 files with a per-file
SHA-256 manifest (`scripts/freeze_caches.py`, `deposit/MANIFEST-v1.md`).

**The dated working logs are left unrewritten** (`SLICE_LOG.md`, `worksheet.md`,
`advisor_brief.md`, `SUI_ADVISOR_BRIEF.md`), so the record of what was believed
when stays intact and can be checked against what is claimed now.

**Held-out discipline is mechanical, not merely intended.** Seven projects
contribute coverage counts only; `paper/ticket_coverage.json` records the Jira
fields screened out, and the matcher validation requests `%H`, `%s` and `%b` from
git and nothing else, so it *cannot* compute a duration. HBase and Phoenix were
dropped from the held-out corpus on 2026-07-30 and quarantined, because their
committed artifacts are one subtraction from per-ticket latency even though no
outcome was ever observed for either (`spent/README.md`).

**One published figure is not reproducible and is never quoted beside a
per-project number.** The public Jira dataset reports 1,822 projects; counting
final-state keys gives **1,276** and implementing the dataset's own name-union
method gives **2,506**. 326 project ids carry more than one name and 0 keys do, so
rename inflation explains part of the gap and not all of it. The three figures
travel together or not at all.
