# When do developers decide to refactor?

## 1. What this is

An independent pre-doctoral feasibility study. The question is when developers
decide to restructure code, and what — if anything — precedes that decision in
the project's own records. The corpus is Apache: 38 projects probed for
eligibility, Hadoop mined in depth (8,919 commits, 51,861 refactorings, 349
architectural episodes). It was built by one person in three working sessions
across one week, which set the corpus depth at one project and left no second
rater for anything requiring manual coding.

## 2. Headline

The study set out to find signals in issue trackers that precede architectural
refactoring. Those signals are largely absent — effort estimates do not exist in
this corpus, and the review-discussion signal collapsed under a volume control —
and the data itself became the finding. Traceability is reported one way and
needed the other way: the **commit-side** rate (what fraction of commits cite a
ticket) is what the literature publishes and what project-selection criteria
use, while the **ticket-side** rate (what fraction of tickets ever receive a
commit) is what any ticket-anchored study actually depends on. They diverge
sharply. Kylin cites a ticket in **83.9%** of commits and yet only **12.0%** of
its tickets are ever touched by one. Across the 12 eligible projects the
ticket-side rate runs **12.0%–69.0%** — not one exceeds 69%.

## 3. What holds

| Finding | Number | Bound | Source |
|---|---|---|---|
| Corpus eligibility is the binding constraint | **12 of 38** projects clear a pre-registered 0.80 commit-side bar; **all 12 are Hadoop-ecosystem** | Apache + Maven + Jira only; bar fixed before any clone | `scripts/traceability_probe.py` `da74465` |
| Commit-side and ticket-side traceability diverge | Kylin **83.9% vs 12.0%**; range **12.0–69.0%** | Ticket-side computed only for the 12 that pass, so this is within-passing variation, not a general correlation | `scripts/ticket_coverage.py` `e0d76ef` |
| The measure cross-validates against prior work | 4 of 5 overlapping projects within **3.3pp** of SEOSS 33, corpora 7 years apart (Hadoop 97.13→97.8, Hive 96.34→97.0, HBase 90.06→92.5, ZooKeeper 87.12→90.4) | Flink differs by 24.1pp; scope, not error — their snapshot is 12,419 commits, ours 38,219 | `paper/PRIOR_WORK.md` `215b10f` |
| Monorepo key matching decides the answer | Hadoop reads **26.2%** single-key, **92.3%** four-key, **97.8%** seven-key | Same 28,290 commits in all three | `scripts/citation_rate.py` `de657c3` |
| Jira status hygiene decays at the 2019–20 GitHub migration | tickets reaching `Patch Available`: **93.5% → 15.5%** | ≤2019 vs ≥2022 | `scripts/temporal_trend.py` `a6accaf` |
| CI verdicts in Jira terminate rather than decay | **96.7% → 50.8% → 0 of 43** | ≤2018 / 2019–21 / ≥2022; no ticket after 2021 carries one | `paper/ERA_AUDIT.md` `e0d76ef` |
| Effort estimates are absent | **0 of 323** architectural tickets carry any of four time-tracking fields | Apache convention, not a property of software | `paper/numbers.md` `9b4e384` |
| The standard MSR sampling frame cannot express the criterion | GHS indexes 735,669 repositories with **35 fields**; only `totalIssues`/`openIssues` touch issues, both GitHub-issue counts | No tracker type, no linkage, no commit-message convention | `paper/PRIOR_WORK.md` `215b10f` |
| RefactoringMiner mislabels TypeScript type aliases | **160** `interface → class` false positives in one commit; 3rd most frequent type in that corpus | TypeScript mode; reported upstream as [issue #1124](https://github.com/tsantalis/RefactoringMiner/issues/1124) | `SUI_FINDINGS.md` |

## 4. What did not hold

| Hypothesis | Result | Why it failed |
|---|---|---|
| Structural review discussion predicts slower resolution | Retracted. Cox HR 0.69 (p=0.003) → **HR 1.10 (p=0.51)** | Discussion *volume* is the real predictor; structural density is null |
| Blast radius — depended-upon modules invite hesitation | **p=0.33** with tier controlled; raw association runs *negative* | Centrality does not predict triage; the apparent effect was the connector tier |
| Maintainer concentration replaces the hand-drawn tier | Collapses once module size enters | Collinear with size, **rho = −0.86** |
| Abstraction is harder than relocation | **×1.54 [0.97, 2.43], p=0.068** fully adjusted (n=319) | Three definitions — any-rule, pure-vs-pure, continuous share — give the same answer; the split was defined post-hoc |
| Architectural refactoring did not share a decade of process improvement | Holds to 2019 (+0.192, p=0.021); **post-2020 p=0.44** | The ordinary control arm collapses to <5 tickets/year |
| A portable tier rule generalises | **0 of 3** projects replicate (Hive p=0.210, Drill p=1.000 wrong direction, Kylin p=0.310) | Vendor share selects large modules, not thin adapters; threshold left at 0.40 although lowering it would have rescued HBase and Phoenix |

The tier effect was never established at module level anywhere: run the same
pre-registered test on Hadoop, where the split is 43.6 vs 3.1 days, and it
returns **p=0.133** — the floor attainable with 2 flagged against 4 unflagged
modules.

## 5. What this cost

Eligibility is a design consequence, not an inconvenience. A ticket-anchored
study on Apache loses at least a third of its tickets and up to seven eighths:
best case Knox at 69.0% ticket-side, worst case Kylin at 12.0%. Studies built on
this frame inherit that loss silently, including current ones —
[arXiv:2605.16133](https://arxiv.org/html/2605.16133v1) (May 2026) measures
architectural-debt time-to-fix by tracing Jira issues to version-control history
across 10 Apache projects.

## 6. The three research questions

**RQ1 — signals preceding refactoring.** First operationalisation tested and
closed: the effort-estimate signal does not exist in this corpus (0/323), and
the review-discussion signal is confounded by volume. Current candidate: the
interval from a self-admitted technical debt comment to a detected architectural
refactoring of the entity it annotates. Prior work is same-commit co-occurrence
only — Iammarino 2021 (commit-level, four projects, no temporal analysis) and
Esfandiari 2023 (commit tags, 77 projects) — with no intervals measured. Novelty
risk, stated: distinctness rests on three simultaneous choices (SATD-anchored,
entity-level, refactoring-detected), and dropping any one collapses it into
existing work. Detail in `paper/SATD_NOVELTY.md` `5b50ef1`.

**RQ2 — why the delay, human factors.** Untouched, and strengthened by RQ1's
outcome. The artifact evidence is thin enough that what remains as explanation
is knowledge held by people rather than recorded in the tracker. That is now an
evidenced argument rather than an assumption.

**RQ3 — tooling implications.** Untouched. Scope depends on what RQ1 and RQ2
establish.

## 7. What ships next

- Methods paper on traceability as a corpus-eligibility constraint — near complete.
- Registered report proposing the SATD-interval design.
- Entity-tracking feasibility: whether a rename chain is recoverable across
  Move Class and Move Package, which the design requires.
- Zenodo deposit of the frozen Jira caches.

## 8. What this needs that one person cannot supply

- **A second rater.** Inter-rater agreement cannot be computed alone, so no
  measure requiring manual coding is currently defensible — including the
  architectural-episode gold set and the codebook, whose keyword rule is 25%
  precise on a single-rater pass.
- **Field judgment on whether the SATD gap is real.** A literature search
  establishes that no one has measured the interval; it cannot establish whether
  that absence is an opportunity or a known dead end.
- **Corpus breadth.** Module-level tests need many modules, and effective n is
  capped at P/ICC by between-project correlation regardless of corpus size — at
  12 projects the ceiling is 600 against the 769 the effect needs, if ICC is
  0.02. Depth beyond Hadoop was not reachable in three working sessions.

## 9. Reproducibility

`requirements.txt` is pinned to the versions the results were produced with. The
Jira caches are frozen as a 2,491-file archive with a per-file SHA-256 manifest
and **no rebuild script**, because Jira is live and a re-fetch returns a
different state (`scripts/freeze_caches.py` `ce4bf7d`).
`paper/traceability_probe.json` pins `head_sha` per project, so any re-run is
exactly diffable. The traceability probe itself is stdlib-only and needs no
virtualenv.

## 10. Repository map

| File | What it is |
|---|---|
| `results_dossier.md` | Full Hadoop results, including retractions and corrections |
| `replication/CORPUS_FEASIBILITY.md` | The 12-of-38 eligibility result and its power consequences |
| `replication/REPLICATION.md` | Held-out test of the tier rule; 0 of 3 |
| `paper/numbers.md` | Every paper number traced to script and commit |
| `paper/ERA_AUDIT.md` | Which results depend on instruments that decay at 2019–20 |
| `paper/PRIOR_WORK.md` | SEOSS 33, Rath ICSE'18, GHS — what is already published |
| `paper/SATD_NOVELTY.md` | Whether the SATD-interval gap is open |
| `paper/ENTITY_IDENTIFIERS.md` | Whether RefactoringMiner entities survive the pipeline |
| `paper/REPRODUCIBILITY.md` | Fresh-clone check and what it exposed |
| `predictions/PREDICTIONS.md` | Pre-registered predictions, committed before outcomes |
| `SUI_FINDINGS.md` | TypeScript pilot; exploratory |
| `deposit/MANIFEST-v1.md` | Frozen cache archive manifest |
| `SLICE_LOG.md` | Command-level log of the original mining runs |
