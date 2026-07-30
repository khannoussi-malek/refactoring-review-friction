# Table 2 — three-channel visibility of architectural change, two ecosystems

Rows are **record channels** — the three places an empirical software engineering
study can look for evidence that architectural work happened. Columns are
**ecosystems**. Each cell reports how much architectural change is visible in
that channel, with its denominator.

| channel | Apache / Jira / Java (Hadoop) | start-ui-web / GitHub / TypeScript |
|---|---|---|
| **commit message** | **not measured** — no commit-message keyword instrument was built for this corpus. Architectural episodes were detected from ASTs (RefactoringMiner over 8,919 commits), never from message text, so no recall or precision figure against message text exists. See the note below: the 25%-precision codebook figure is a *review-comment* instrument and does not belong in this cell. | **recall 3 of 96 = 3.1%** of architectural commits mention refactoring; **93 of 96 are silent**. **Precision 3 of 10 = 30%** — of 10 commits whose message claims refactoring, 7 are not architectural. Denominators: 96 architectural commits (recall), 10 refactoring-claiming messages (precision). |
| **issue tracker** | **commit-side 82.6%–98.3%** of commits cite a ticket, across 12 eligible projects; denominator = commits scanned per project, 968–21,220. **Ticket-side 12.0%–69.0%** of tickets ever receive a citing commit, same 12 projects; denominator = tickets in the tracker per project, 3,152–30,063. Kylin: **83.9%** against **12.0%**. | **7 of 96 = 7%** of architectural commits link an issue. Denominator = 96 architectural commits. For comparison in the same corpus: other refactoring 7%, non-refactoring 10% — architectural change is no more likely to be tracked in advance than anything else, and slightly less. |
| **pull request** | **n/a** — pre-migration Jira workflow. Hadoop's review record lived in Jira via the githubbot relay, not in pull requests, so there is no PR-level architectural-visibility measurement to make. The Jira-side proxy for it does not survive the 2019–20 GitHub migration either: architectural tickets carrying a CI verdict run **145 of 150 (96.7%) ≤2018 → 66 of 130 (50.8%) 2019–21 → 0 of 43 (0.0%) ≥2022** (`paper/ERA_AUDIT.md`). The channel is absent by workflow, not merely thin. | **30 of 96 = 31%** of architectural commits are visible at PR level; **66 of 96 = 69% never pass through code review at all**. Denominator = 96 architectural commits. |

## Caption

**This table demonstrates convergent invisibility across non-comparable
measures. It is not a single metric measured six times.**

Every cell is a *different quantity* with a *different denominator*, and that is
the point of the table rather than a defect in it. A recall rate over
architectural commits, a citation rate over commits, a coverage rate over
tickets, and a review-exposure rate over commits are four distinct
operationalisations of "visible", answering four distinct questions, on two
corpora that share no scale, no language, no governance model and no tracker.
They are assembled here because they **agree in direction while being
methodologically independent** — and independent agreement is the only kind of
evidence a single-corpus critique cannot absorb.

Consequently: **the cells are not normalised to a common scale and no summary
statistic is computed across them.** Any average, ratio or aggregate over this
table would be meaningless, and a reader who wants "the overall invisibility
rate" is asking for a number that does not exist. The claim the table supports is
qualitative in form and quantitative in each cell: *in every channel measured, in
both ecosystems, most architectural change leaves no usable record.*

**The strongest single measurement is the issue-tracker row of the Apache
column** — the commit-side/ticket-side divergence, 12 projects, pre-registered
bar, both channels measured together (Table 1). It is reported as evidence for
the broader claim rather than as the claim itself, because a single-dataset
critique is dismissible as an Apache artifact and a two-ecosystem, three-channel
result is not.

## Two cells that are absences, and what kind of absence each is

**Apache / pull request is a structural `n/a`, not a missing measurement.**
Hadoop did not use pull requests as its review record during the period studied.
There is nothing to measure, and no amount of additional mining creates it. The
CI-verdict series is given as the nearest available proxy precisely to show that
it terminates: 0 of 43 after 2021 is absence, not sparsity.

**Apache / commit message is a gap in this study, not a property of Apache.**
The Hadoop architectural corpus was built by AST-level detection, and the
message-text channel was never instrumented against it. A recall figure
comparable to the TypeScript column's 3.1% is computable in principle and is not
computed here. Stated as a limitation in `paper/manuscript/threats.md`; it is the
most obvious extension of this table.

## Note — where the 25% codebook figure actually belongs

`codebook_results.md` and `results_dossier.md` §11 report a keyword rule that is
**≈25% precise** (5 of 20 flagged genuinely structural) with a **≈5% miss rate**
(1 of 20 unflagged), on a **40-comment single-rater sample**. That instrument
measures **review comments** — `codebook.md` fixes the unit of coding as "one
review comment on the episode's PR, as relayed into Jira" — and it is a fourth
channel, review discussion, not the commit-message channel. It is therefore not
placed in the Apache commit-message cell above.

It is also reported **as a finding about the instrument, never as an instrument
this paper's claims rest on**: it is a single-rater pass with no κ, and
`README.md` §8 records that no measure requiring manual coding is currently
defensible in this repository. Its role in the paper is to establish that
keyword-based detection of structural discussion over-counts roughly fourfold,
which is a validity result about a method other studies use — the same role the
TypeScript column's 30% precision plays for commit messages.

## Sources

| cell | source | script / artifact |
|---|---|---|
| Apache, issue tracker (commit-side) | `paper/table1_eligibility.md`, `paper/traceability_probe.json` | `scripts/traceability_probe.py` `da74465` |
| Apache, issue tracker (ticket-side) | `paper/table1_eligibility.md`, `paper/ticket_coverage.json` | `scripts/ticket_coverage.py` `e0d76ef` |
| Apache, pull request (CI verdict series) | `paper/ERA_AUDIT.md` | `scripts/ci_rework.py` `47456b1` |
| TypeScript, commit message | `SUI_FINDINGS.md` "Secondary findings 1" | `scripts/sui/investigate3.py` |
| TypeScript, issue tracker | `SUI_FINDINGS.md` "Secondary findings 2" | `scripts/sui/investigate3.py` |
| TypeScript, pull request | `SUI_FINDINGS.md` robustness checks 5–6 | `scripts/sui/selection_bias.py` |
| codebook note | `codebook_results.md`, `results_dossier.md` §11, `codebook.md` | `scripts/pr_review_signal.py` `de657c3` |

**Corpus bounds that travel with the TypeScript column.** One repository, one
company: `BearStudio/start-ui-web`, 1,199 commits 2019-12 → 2026-07, 93%
detector coverage, **n=28 architectural PRs**. `SUI_FINDINGS.md` is marked
EXPLORATORY throughout and every p-value in it is uncorrected and
hypothesis-generating. The three cells used here are **counts and proportions,
not tests**, which is why they are usable in a results table where the pilot's
p-values are not.
