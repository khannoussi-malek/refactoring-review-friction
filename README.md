# What precedes a developer's decision to refactor?

**Reader's guide (interactive):**
<https://khannoussi-malek.github.io/refactoring-review-friction/>

## 1. What this is

An independent pre-doctoral study. The question is what, if anything, in a
project's own records precedes the decision to restructure code. The corpus is
38 Apache projects probed for eligibility, Hadoop mined in depth (8,919 commits,
51,861 refactorings, 349 architectural episodes), plus the public Jira dataset
(Zenodo 15719919) across 16 organisations and 2,686,282 issues. It was built by
one person in three working sessions, alongside full-time employment, which set
the corpus depth at one project and left no second rater. The committed history
spans 19–25 July 2026.

## 2. Headline

The study looked for signals in issue trackers preceding architectural
refactoring. Those signals are absent or too thin to carry a study, and the data
itself became the finding. Traceability is published one way and needed the
other way: the **commit-side** rate — what fraction of commits cite a ticket —
is what the literature reports and what selection criteria use, while the
**ticket-side** rate — what fraction of tickets ever receive a commit — is what
a ticket-anchored study depends on. They diverge sharply. Kylin cites a ticket
in **83.9%** of commits while only **12.0%** of its tickets are ever touched by
one, and across the 12 eligible projects the ticket-side rate runs
**12.0%–69.0%**, none above 69%.

## 3. What holds

| Finding | Number | Bound | Source |
|---|---|---|---|
| Corpus eligibility is the binding constraint | **12 of 38** clear a pre-registered 0.80 commit-side bar; **all 12 are Hadoop-ecosystem** | Apache + Maven + Jira only; bar fixed before any clone | `scripts/traceability_probe.py` `da74465` |
| Commit-side and ticket-side diverge | Kylin **83.9% vs 12.0%**; range **12.0–69.0%** | Computed only for the 12 that passed, so this is within-passing variation, not a general correlation | `scripts/ticket_coverage.py` `e0d76ef` |
| The measure replicates independently | 4 of 5 overlapping projects within **3.3pp** of SEOSS 33 (Hadoop 97.13→97.8, Hive 96.34→97.0, HBase 90.06→92.5, ZooKeeper 87.12→90.4) | Corpora 7 years apart; Flink differs 24.1pp, scope not error — their snapshot 12,419 commits, ours 38,219 | `paper/PRIOR_WORK.md` `215b10f` |
| Monorepo key matching decides the answer | **26.2%** single-key → **92.3%** four-key → **97.8%** seven-key | Same 28,290 Hadoop commits in all three | `scripts/citation_rate.py` `de657c3` |
| Jira status hygiene decays; CI verdicts terminate | status `Patch Available` **93.5% → 15.5%**; CI verdicts **96.7% → 50.8% → 0 of 43** | ≤2018 / 2019–21 / ≥2022; no ticket after 2021 carries a CI verdict | `paper/ERA_AUDIT.md` `e0d76ef` |
| Estimate use is a per-project convention inside Apache, not Apache-wide | **2.557%** overall (25,949 / 1,014,926); MESOS **32.94%**, STDCXX **38.70%**, USERGRID **37.51%** | Presence counts only; no claim about estimate quality | `scripts/jira_estimates.py` `eee902f` |
| Story points have no portable schema | "Story Points" maps to **15 distinct customfield ids** across 14 orgs; **10 orgs carry more than one**; Mojang has none | `absent_from_catalogue` and `present_null` are different facts: Mojang has no fields, JFrog has all six and leaves them null | `paper/estimate_field_schema.md` `eee902f` |
| Project keys are stable identifiers, names are not | **326 project ids carry multiple names; 0 ids carry multiple keys; 0 keys map to multiple ids** — `Jira/12910` is *SourceTree*, *SourceTree For Mac*, *Sourcetree For Mac* | id↔key is 1:1 *within a tracker snapshot*; keys cited in commits may have no project record in it at all (§5 mode 6) | `paper/numbers.md` `0f116aa` |
| The standard sampling frame cannot express eligibility | GHS: 735,669 repositories, **35 fields**, only `totalIssues`/`openIssues` touch issues | Both are GitHub-issue counts; no tracker type, no linkage, no commit convention | `paper/PRIOR_WORK.md` `215b10f` |
| Estimate-rich and traceable projects barely intersect | **3 of 27** clear both (≥10% estimates, ≥0.80 traceability): DAOS 80.1%/93.4%, EVG 56.9%/91.6%, SLIDER 15.3%/83.1% | Only **4 of 27** clear traceability at all; OPENNLP joins at a 5% estimate floor | `paper/intersection.json` `63f4231` |
| Selecting on estimate coverage biases toward retired projects | **9 of 23** estimate-ranked Apache projects are in the Attic (39%); among those with ≥10% estimates, **5 of 8** (STDCXX, USERGRID, MESOS, MXNET, SHINDIG) | Traceability selection shows no significant skew: 2/12 passes vs 1/26 drops, Fisher p=0.229 | `paper/intersection.json` `63f4231` |
| RefactoringMiner mislabels TypeScript type aliases | **160** `interface → class` false positives in one commit; 3rd most frequent type in that corpus | TypeScript mode; reported upstream, [issue #1124](https://github.com/tsantalis/RefactoringMiner/issues/1124) | `SUI_FINDINGS.md` |

## 4. What did not hold

| Hypothesis | Result | Named cause |
|---|---|---|
| Structural review discussion predicts slower resolution | Retracted: Cox HR 0.69 (p=0.003) → **HR 1.10 (p=0.51)** | Discussion-volume confound; structural density is null |
| Blast radius — depended-upon modules invite hesitation | **p=0.33** with tier controlled; raw association *negative* | The apparent effect was the connector tier, not centrality |
| Maintainer concentration replaces the hand-drawn tier | Collapses once module size enters | Collinear with module size, **rho = −0.86** |
| Abstraction is harder than relocation | **×1.54 [0.97, 2.43], p=0.068** fully adjusted, n=319 | Three definitions — any-rule, pure-vs-pure, continuous share — give the same answer; split defined post-hoc |
| Architectural refactoring missed a decade of process improvement | Holds to 2019 (+0.192, p=0.021); **post-2020 p=0.44** | Ordinary control arm collapses: 394 tickets (2016+) → 145 (2020+) → 101 (2021+) |
| A portable tier rule generalises | **0 of 3** replicate (Hive p=0.210, Drill p=1.000 wrong direction, Kylin p=0.310) | Vendor share selects large modules, not thin adapters; threshold left at 0.40 although lowering it would have rescued HBase and Phoenix |

The tier effect was never established at module level anywhere: the same
pre-registered test on Hadoop, where the split is 43.6 vs 3.1 days, returns
**p=0.133** — the floor attainable with 2 flagged against 4 unflagged modules.

The original estimate conclusion was drawn at the wrong level of aggregation and
is self-corrected. Three numbers now travel together: **2.557%** Apache-wide,
**1.449%** in the Hadoop corpus (713 / 49,201), **0 of 323** architectural
tickets — expected 4.7, P ≈ 0.009 under a naive binomial. Architectural tickets
are not a random draw and the non-randomness could run either way, so the
deficit is suggestive on thin evidence.

## 5. Six ways a project cannot support an issue-linked study

| # | mode | worked example |
|---|---|---|
| 1 | GitHub Issues displaced Jira | ShardingSphere: 5 Jira citations in 49,111 commits, 30,746 GitHub refs |
| 2 | No source repository exists | RedHat RHBRMS: 86.00% estimates, product tracker, no code |
| 3 | Tracker downstream of the upstream repo | kata-containers: zero `KATA-` keys in 19,807 commits |
| 4 | Convention changed mid-history | spring-batch: `BATCH-` in 4,046 of 7,034 commits, none in the recent 20 sampled |
| 5 | Monorepo needs multi-key matching | Hadoop: 26.2% → 92.3% on the same commits |
| 6 | Repository migrated across organisations | Evergreen: Jira key `EVG`, recent commits use `DEVPROD` |

Modes 4–6 are silent — they yield a plausible low number, not an error. Modes
1–3 are disqualifying rather than measurable. **None is expressible in any
published sampling frame, and all six were discovered post hoc**, by reading
commit messages project by project. Detail: `paper/eligibility_failure_modes.md`.

## 6. The three research questions

**RQ1 — signals preceding refactoring.** The first operationalisation is tested
and closed. The effort-estimate signal is not absent but too thin: 1.449% in the
Hadoop corpus cannot carry the study. Estimate-rich and traceable projects are
close to disjoint — 3 of 27 clear both, and among Apache specifically the
estimate-rich projects are exactly those that moved to GitHub PR workflows
(MESOS 32.94% estimates against 7.4% traceability) or predate the citation
convention. The two strong passes, DAOS and EVG, are corporate projects running both
trackers; the third, SLIDER, is retired — and retirement is systematic here, not
incidental: 5 of the 8 Apache projects with ≥10% estimate coverage are in the
Attic. Current candidate: the
interval from a self-admitted technical debt comment to a detected architectural
refactoring of the annotated entity. Prior work is same-commit co-occurrence
only — Iammarino 2021 (commit-level, four projects, zero temporal analysis) and
Esfandiari 2023 (commit tags, 77 projects). Distinctness rests on three
simultaneous choices — SATD-anchored, entity-level, refactoring-detected — and
dropping any one collapses it into existing work (`paper/SATD_NOVELTY.md`).

**RQ2 — why the delay, human factors.** Untouched, and strengthened by RQ1's
outcome. The artifact evidence is thin enough that what remains as explanation
is knowledge held by people rather than recorded in the tracker. That is now an
evidenced argument rather than an assumption.

**RQ3 — tooling implications.** Untouched. Scope depends on RQ1 and RQ2.

## 7. What ships next

- Methods paper on traceability and estimate coverage as corpus-eligibility
  constraints — **complete draft as of 2026-08-05**, `paper/manuscript/PAPER.md`.
- Registered report proposing the SATD-interval design. **Superseded 2026-07-26**
  before it was started; the current RQ1 anchor is the violation-symptom interval
  and it is at the feasibility-gate stage (`paper/ANCHOR_HISTORY.md`,
  `prereg/RESOLUTION_GATE.md`). Its novelty margin is recorded as *not assessed*.
- Entity-tracking feasibility: whether a rename chain is recoverable across Move
  Class and Move Package. **Answered 2026-08-05 — go, with a stated ceiling**
  (`paper/ENTITY_TRACKING_FEASIBILITY.md`). Class identity is recoverable at 89.7%
  per operation and 91.6% across package moves; the binding constraint turned out
  to be the completeness of the mined commit range, at 83.1%, not the detector.
- Zenodo deposit of the frozen Jira caches. **Metadata prepared, nothing
  published** (`deposit/zenodo.json`, `deposit/DEPOSIT_CHECKLIST.md`).

## 8. What this needs that one person cannot supply

- **A second rater.** Inter-rater agreement cannot be computed alone, so no
  measure requiring manual coding is currently defensible — the
  architectural-episode gold set and the codebook, whose keyword rule is 25%
  precise on a single-rater pass, both sit behind this.
  **Sharpened 2026-08-05.** A second-rater pilot found a further problem: the
  first pass kept only the two 3-cell margins, not the per-comment labels, so κ
  is not computable *even if a second rater appears now*. What the margins do
  determine is the interval κ must lie in, and on the bucket that matters — the
  comments the keyword filter flags — **no pairing reaches κ above 0.491**. Six
  of the 40 comments turn on an undisambiguated ordering between two codebook
  rules, and resolving it the other way moves the attainable ceiling to 0.840.
  An LLM was used as the second rater and **that is not a substitute for a human
  one**; the reasons are stated in `paper/LLM_RATER_PILOT.md` §6.
- **Field judgment on whether the SATD gap is real.** A literature search
  establishes that no one has measured the interval; it cannot establish whether
  that absence is an opportunity or a known dead end.
- **Corpus breadth.** Module-level tests need many modules, and effective n is
  capped at P/ICC by between-project correlation regardless of corpus size — at
  12 projects the ceiling is 600 against the 769 the effect needs at ICC 0.02.
  Depth beyond Hadoop was not reachable in three working sessions.

## 9. Two open questions

**(a) Is a normalisation step being missed in the published project count?** The
dataset reports 1,822 projects. Counting final-state project *keys* gives
**1,276**; implementing the notebook's `set.union(final, history)` on project
*names* gives **2,506**. Across 2,686,282 issues, **326 project ids carry more
than one distinct name and 0 keys do** — `Jira/12910` appears as *SourceTree*,
*SourceTree For Mac* and *Sourcetree For Mac*, one variant differing only in
capitalisation. Removing the surplus names lands near 2,180, so renaming
explains part of the gap and not all of it. Is there a normalisation or
deduplication step between the two figures that I have not reproduced?

**(b) Is the three-legged SATD novelty margin sufficient to build on?** The
design is distinct only as the conjunction of SATD-anchored, entity-level and
refactoring-detected. An architectural-debt time-to-fix literature is active
(arXiv 2605.16133, May 2026) using Jira issues, file granularity and no
refactoring detection. Is that margin worth a registered report?

## 10. Reproducibility

`requirements.txt` is pinned to the versions that produced the results. The Jira
caches are frozen as a 2,491-file archive with a per-file SHA-256 manifest and
**no rebuild script**, because Jira is live and a re-fetch returns different
state (`scripts/freeze_caches.py` `ce4bf7d`). `paper/traceability_probe.json`
and `paper/intersection.json` pin `head_sha` per record, so any re-run is
exactly diffable. The dated working logs (`SLICE_LOG.md`, `worksheet.md`,
`advisor_brief.md`) are left unrewritten, so the record of what was believed when
stays intact. The traceability probe is stdlib-only and needs no virtualenv.

## 11. Repository map

| File | What it is |
|---|---|
| `results_dossier.md` | Full Hadoop results, including retractions and corrections |
| `replication/CORPUS_FEASIBILITY.md` | The 12-of-38 eligibility result and its power consequences |
| `replication/REPLICATION.md` | Held-out test of the tier rule; 0 of 3 |
| `paper/numbers.md` | Every paper number traced to script and commit |
| `paper/intersection.json` | Estimate coverage × traceability, 27 projects, HEAD pinned |
| `paper/eligibility_failure_modes.md` | The six-mode taxonomy with worked examples |
| `paper/estimate_field_schema.md` | Story-point field ids per organisation; the three-state distinction |
| `paper/ERA_AUDIT.md` | Which results depend on instruments that decay at 2019–20 |
| `paper/PRIOR_WORK.md` | SEOSS 33, Rath ICSE'18, GHS — what is already published |
| `paper/SATD_NOVELTY.md` | Whether the SATD-interval gap is open |
| `paper/ENTITY_IDENTIFIERS.md` | Whether RefactoringMiner entities survive the pipeline |
| `paper/REPRODUCIBILITY.md` | Fresh-clone check and what it exposed |
| `predictions/PREDICTIONS.md` | Pre-registered predictions, committed before outcomes |
| `estimates_by_org.json` | Estimate coverage, 16 orgs, three states per field |
| `SUI_FINDINGS.md` | TypeScript pilot; exploratory |
| `deposit/MANIFEST-v1.md` | Frozen cache archive manifest |
| `SLICE_LOG.md` | Dated command-level log of the original mining runs |
| `paper/manuscript/PAPER.md` | The methods paper, assembled from the section files |
| `paper/table3_ticket_side.md` | Ticket realisation rate across all 38 probed projects |
| `paper/ENTITY_TRACKING_FEASIBILITY.md` | Whether class identity survives Move Class and Move Package — go/no-go |
| `paper/LLM_RATER_PILOT.md` | Second-rater pilot, the κ that cannot be computed, and the bounds that can |
| `deposit/DEPOSIT_CHECKLIST.md` | Zenodo metadata prepared; what remains manual |
| `docs/DRAFT_dataset_authors_query.md` | Unsent draft of the §9(a) question to the dataset authors |
| `LICENSE`, `CITATION.cff` | MIT for code, CC-BY-4.0 for text and derived data; citation record |
