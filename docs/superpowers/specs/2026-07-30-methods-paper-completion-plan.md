# Implementation plan — finish and submit the methods paper

**Date:** 2026-07-30
**Status:** ready to execute
**Repo:** `khannoussi-malek/refactoring-review-friction`, branch `version2`
**Intended save path:** `docs/superpowers/specs/2026-07-30-methods-paper-completion-plan.md`
**Predecessor:** `docs/superpowers/specs/2026-07-22-ts-refactoring-friction-pilot-design.md`
**Audience:** an AI coding agent with repo write access, executing task by task

---

## 0. Read before touching anything

Read these in order. Do not skip. Several tasks below will look wrong until you have.

1. `README.md` — the outward account, §3 what holds, §4 what did not, §5 the six failure modes
2. `PROJECT_STATE.md` — the decision log, and especially **§3 what is held out and why**
3. `SUI_FINDINGS.md` — the TypeScript pilot, exploratory
4. `paper/numbers.md` — every published number traced to a script and a commit
5. `paper/traceability_table.md`, `paper/ticket_coverage.json`, `paper/eligibility_failure_modes.md`

This repo was built by one person in three working sessions alongside full-time
employment. Its unusual property is that the record of what was believed when has
been preserved rather than tidied. Preserving that is a requirement, not a
preference.

---

## 1. Hard rules

These override any instruction later in this document and any inference you draw
about what would be helpful. If a task appears to require breaking one of them,
stop and report instead.

**R1 — Do not spend the held-out corpus.**
`PROJECT_STATE.md` §3 defines the rule: *coverage and existence counts are
permitted; outcome data is not.* A citation rate, ticket count, or field count is
permitted. Any timing, latency, resolution time, status duration, or
first-commit-minus-created subtraction is forbidden on these projects:

> Ozone, Tez, ZooKeeper, Ranger, Oozie, Knox, Sqoop

Do not compute such a statistic. Do not print one. Do not write a script capable
of producing one against these projects, even unrun. HBase and Phoenix are
handled in T2.

**R2 — Never rewrite the dated working logs.**
`SLICE_LOG.md`, `worksheet.md`, `advisor_brief.md`, `SUI_ADVISOR_BRIEF.md` are
historical records. Do not correct, reformat, tidy, or update them. Append-only,
and only where a task says so.

**R3 — Do not edit existing result JSON by hand.**
`paper/*.json`, `*_results.json`, `cox_dataset.json` and similar are script
outputs. Change them only by re-running the generating script. If a value looks
wrong, report it; do not fix it in place.

**R4 — Do not add analyses, hypotheses, corpora, or statistical tests.**
No new project clones. No new RefactoringMiner runs. No new p-values. This plan
ships what exists. Every new finding delays the paper, which is the failure mode
being corrected.

**R5 — Do not relax a frozen threshold or definition.**
The vendor-share threshold stays at 0.40. The eligibility bar stays at 0.80. The
fact that lowering them would have rescued results is itself a finding
(`replication/REPLICATION.md`).

**R6 — No claim may depend on manual coding by a single rater.**
`README.md` §8 explains why. The codebook's 25% precision and the commit-message
30%/3% figures are reported **as findings about those instruments**, never as
instruments the paper's own claims rest on.

**R7 — Every number in the manuscript must exist in `paper/numbers.md`** with a
script path and a commit hash. If you need a number that is not there, either
derive it with a committed script and add the provenance row, or do not use it.
Never state a number you cannot trace.

**R8 — Commit granularly, one task per commit**, using the message given in each
task. Do not squash. Do not force-push. Do not rebase.

---

## 2. The thesis the paper must argue

Everything below serves one sentence:

> **Architectural change is systematically absent from the records that empirical
> software engineering studies rely on** — measured across three independent
> record channels (commit messages, issue trackers, pull requests) in two
> ecosystems (Apache/Jira/Java and GitHub/TypeScript), with a taxonomy of six
> mechanisms by which a project silently fails to support an issue-linked study.

This is a change of framing from the current `README.md`, which leads with
commit-side versus ticket-side traceability divergence. That divergence remains
the strongest single measurement, but it becomes evidence for the broader claim
rather than the claim itself. Reason: a single-dataset critique is dismissible as
an Apache artifact; a two-ecosystem, three-channel result is not.

If a section, table, or paragraph does not serve that sentence, it belongs in the
replication package, not the manuscript.

---

## 3. Phase A — close the loose ends

Estimated half a day. Do all of Phase A before starting Phase B.

### T1 · Resolve the empty artifact

**File:** `prs_twenty.json` (0 bytes)

An empty file in a replication package reads as a broken pipeline. Determine from
`scripts/sui/fetch_prs.py` and `SUI_FINDINGS.md` whether Twenty was fetched and
failed or was never attempted. Then either delete the file, or keep it and add a
short subsection to `SUI_FINDINGS.md` recording that the third TypeScript corpus
was not opened and why.

**Acceptance:** no zero-byte files remain in the repo root. `git status` clean.
**Commit:** `chore: resolve the empty Twenty PR artifact`

### T2 · Resolve the HBase/Phoenix held-out risk

**Files:** `PROJECT_STATE.md` §3, `replication/{hbase,phoenix}.{git,jira}.json`

`PROJECT_STATE.md` §3 states these two are "at risk" — their committed git and
jira JSON are one subtraction away from per-ticket latencies — and that the
decision is pending. Pending decisions in a public artifact are the only thing in
this repo that looks unfinished.

Resolve it by dropping to a seven-project held-out corpus. Move the four files to
`spent/` with a `spent/README.md` explaining that no outcome was ever observed
(the frozen rule flagged zero modules, so the test stage never ran) but that the
files are one operation from an outcome and are therefore quarantined rather than
trusted. Update §3 to describe a seven-project corpus. Add a dated row to the
§2 decision log.

**Acceptance:** §3 lists seven projects, contains no "pending" language, and the
decision log has a new dated row.
**Commit:** `decision: drop to a seven-project held-out corpus; quarantine HBase and Phoenix`

### T3 · Eliminate the undocumented decision

**Files:** `PROJECT_STATE.md` §2, `replication/CORPUS_FEASIBILITY.md`

One row in the decision log is marked `[undocumented]` — the 07-25 refusal to run
ICC on four clusters, whose reasoning exists only in chat. `CORPUS_FEASIBILITY.md`
states the ICC *requirement* but not the refusal.

Write the reasoning into `CORPUS_FEASIBILITY.md`: between-cluster variance is not
estimable at n=4, so an ICC computed there would be a number without a meaning,
and the estimate must come from the pooled study as a first stage. Then replace
`[undocumented]` with the file reference.

**Acceptance:** zero occurrences of `[undocumented]` in `PROJECT_STATE.md`.
**Commit:** `docs: document the ICC refusal in CORPUS_FEASIBILITY`

### T4 · Verify the upstream tool report

`README.md` §3 claims the RefactoringMiner TypeScript false positive is reported
upstream as issue #1124. Verify that issue exists and is about this defect. If it
does not exist, do not file it yourself — report back to the author, since filing
under someone else's name is not yours to do.

Record the outcome in a new stub file `paper/RM_TYPESCRIPT.md`: the 160
`interface → class` instances, the traced counterexample
(`src/features/account/types.ts`, `export type Account = User`), the corroborating
fact that the codebase uses function components exclusively, the detector version
(3.1.4, TypeScript support complete 2026-05-24), and the issue link or its
absence. **Three to ten lines. Then stop.** This is a separate future paper and
must not be developed now.

**Acceptance:** `paper/RM_TYPESCRIPT.md` exists and is under 15 lines.
**Commit:** `docs: stub the RefactoringMiner TypeScript validity finding`

---

## 4. Phase B — build the two tables as paper artifacts

Estimated one day. These two tables *are* the paper. Build them before writing
any prose.

### T5 · Table 1 — corpus eligibility, both channels

**New:** `scripts/make_table1.py`, `paper/table1_eligibility.md`
**Inputs:** `paper/traceability_table.md`, `paper/ticket_coverage.json`, `paper/traceability_probe.json`

`traceability_table.md` currently carries commit-side rates only.
`ticket_coverage.json` carries both. Merge them into one table:

* 12 passing projects: project, Jira key, HEAD sha, commits scanned, single-key
  rate, multi-key rate, tickets total, tickets cited, **ticket-side rate**
* 26 dropped projects: project, HEAD sha, commits, multi-key rate, measured drop
  reason

Generate it with a script so it cannot drift from its inputs. Preserve
`head_sha` per row. Keep the existing drop-reason vocabulary
(`below_bar_narrowly`, `low_commit_message_hygiene`,
`github_issue_references_dominate`) unchanged.

The caption must state the divergence explicitly: Kylin cites a ticket in 83.9%
of commits while only 12.0% of its tickets are ever touched by one, and the
ticket-side rate across the 12 eligible projects runs 12.0–69.0% with none above
69%.

**Acceptance:** `python scripts/make_table1.py` regenerates
`paper/table1_eligibility.md` byte-identically on a second run. Every rate in the
table matches its source JSON. R1 is not violated — no timing column exists.
**Commit:** `paper: generate Table 1 with both traceability channels`

### T6 · Table 2 — three-channel visibility

**New:** `paper/table2_visibility.md`
**Inputs:** `SUI_FINDINGS.md`, `results_dossier.md`, `codebook_results.md`, `paper/ticket_coverage.json`

This table does not exist yet and is the paper's novel contribution. Rows are
record channels; columns are ecosystems.

| channel | Apache / Jira / Java | start-ui-web / GitHub / TypeScript |
|---|---|---|
| commit message | codebook keyword rule, 25% precision, single-rater pass | 3 of 96 architectural commits mention refactoring — recall 3%, precision 30% |
| issue tracker | commit-side 82.6–98.3% against ticket-side 12.0–69.0% | 7% of architectural commits link an issue |
| pull request | not applicable — pre-migration Jira workflow | 30 of 96 architectural commits visible at PR level (31%); 69% of architectural work never reviewed |

**Critical requirement.** These cells are *different quantities* with different
denominators. That is the point of the table, not a defect in it. Every cell must
carry its denominator explicitly, and the caption must state that the table
demonstrates convergent invisibility across non-comparable measures rather than a
single metric measured six times. Do not normalise them into a common scale. Do
not compute a summary statistic across cells.

Add the Apache PR cell as an explicit `n/a` with the reason (the 2019–20 GitHub
migration, per `paper/ERA_AUDIT.md`), not as a blank.

**Acceptance:** every cell has a denominator; the caption contains the
non-comparability warning; no cross-cell aggregate appears.
**Commit:** `paper: add Table 2, three-channel visibility across two ecosystems`

### T7 · Regenerate the funnel figure

**File:** `figures/study_funnel.png`

Confirm it reflects the post-retraction state: 38 probed, 12 eligible, all
Hadoop-ecosystem, and the attrition to the six hypotheses that did not hold. If
it predates the 07-25 full-adjustment pass, regenerate it. If the generating
script is missing, note that in the commit message rather than hand-editing the
image.

**Acceptance:** the figure's numbers match `README.md` §3 and §4.
**Commit:** `figures: regenerate the study funnel against post-retraction numbers`

---

## 5. Phase C — the one validation the paper needs

Estimated one day.

### T8 · Matcher precision on a manual sample

**New:** `scripts/validate_matcher.py`, `paper/matcher_validation.md`

The paper's headline numbers are citation rates produced by key matching. The
first objection any reviewer raises is that a rate of 83.9% is a regex artifact.
The SEOSS 33 replication (4 of 5 projects within 3.3pp) is external validation and
should be cited, but it does not establish precision on this corpus.

Draw 200 commits stratified across the 12 eligible projects, seeded and recorded
so the sample is reproducible. For each, record whether the matched key is a
genuine reference to work done in that commit, or one of:

* a version string or release number resembling a key
* a key pasted from a changelog, release note, or copied file
* a backport or cherry-pick mention referring to other work
* a revert referencing the reverted commit's key
* a key belonging to a different project in the monorepo

Report precision with a binomial confidence interval, broken down by failure
category and by project where n permits.

This is a **mechanical check against a written rule, not a coded judgment**, so
R6 does not apply and a single rater is sufficient. State that distinction
explicitly in the file — it is the reason this measure is defensible where the
architectural-episode gold set is not.

**Acceptance:** the sample is seeded and reproducible; precision is reported with
an interval; the single-rater justification is stated; provenance rows are added
to `paper/numbers.md`.
**Commit:** `validation: measure key-matcher precision on a 200-commit manual sample`

### T9 · Check whether author aliasing contaminated the Hadoop social measure

**Files:** `scripts/social_centrality.py`, `social_centrality.json`, `scripts/sui/identity.py`, `scripts/sui/ALIASING_NOTE.md`

`SUI_FINDINGS.md` records that `ivan@dalmet.fr` and
`ivan-dalmet@users.noreply.github` are one person, and that author identity must
be resolved by GitHub login rather than email before any social or ownership
variable is computed.

Determine whether the Hadoop social-centrality computation keyed on email. The
maintainer-concentration hypothesis is already dead (collinear with module size,
rho = −0.86), so the likely outcome is that nothing depends on it — but the
threats section must say so from evidence rather than leaving a reader to wonder
whether the same bug ran twice.

Do not re-run the analysis. Read the script, determine the key, and record the
answer.

**Acceptance:** a short subsection in `paper/manuscript/threats.md` (created in
T10) or a note file states whether the Hadoop measure shares the defect.
**Commit:** `threats: determine whether author aliasing affected the Hadoop social measure`

---

## 6. Phase D — the manuscript

Estimated two weeks of the author's part-time writing. The agent's job here is
scaffolding and assembly, not authorship of argument.

### T10 · Create the manuscript skeleton

**New:** `paper/manuscript/` containing `abstract.md`, `intro.md`, `related.md`,
`method.md`, `results.md`, `taxonomy.md`, `threats.md`, `discussion.md`,
`README.md`

One file per section so sections can be written out of order. `README.md` in that
directory records the intended writing order and the thesis sentence from §2 of
this plan verbatim, so it stays visible during drafting.

**Writing order, which is not the reading order:**

1. `results.md` — prose around Tables 1 and 2
2. `method.md` — corpus construction, the pre-registered 0.80 bar, key matching, the detector and its version
3. `taxonomy.md` — the six failure modes, compressed from `paper/eligibility_failure_modes.md`, each with its worked example
4. `threats.md` — assembled from `paper/ERA_AUDIT.md`, the chunk-loss test, T9's aliasing result, the single-rater limitation, the three-working-sessions provenance, and n=28 for the TypeScript pilot
5. `related.md` — largely `paper/PRIOR_WORK.md`: SEOSS 33, Rath ICSE'18, GHS's 35 fields, Iammarino 2021, Esfandiari 2023
6. `intro.md` — last, once the paper's actual content is known
7. `discussion.md` and `abstract.md` — last

**Commit:** `paper: scaffold the manuscript with sections and writing order`

### T11 · Assemble the sections that are transcription rather than composition

Draft `related.md`, `taxonomy.md`, and `threats.md` by compressing the existing
memos. These are reorganisation tasks, not argument tasks.

Rules while assembling:

* Preserve every named cause in `README.md` §4. The six killed hypotheses appear
  in `intro.md` as motivation in a single paragraph — *we set out to measure
  signal-to-action latency, six operationalisations failed, and the sampling
  frame itself turned out to be the finding* — and nowhere else. They are not
  results of this paper.
* `taxonomy.md` must retain that modes 4–6 are silent (they yield a plausible low
  number rather than an error), that modes 1–3 are disqualifying rather than
  measurable, and that all six were discovered post hoc by reading commit
  messages project by project.
* `threats.md` must state that the abstraction-versus-relocation split was
  defined post hoc, that the estimate conclusion was self-corrected after being
  drawn at the wrong aggregation level, and that the 0.40 threshold was held
  during a failed replication when lowering it would have rescued two projects.
  These are the paper's credibility, not its embarrassments.

**Acceptance:** every claim traces to `paper/numbers.md` per R7. No new numbers.
**Commit:** one per section: `paper: draft <section> from existing memos`

### T12 · Provenance audit before submission

Walk every number in `paper/manuscript/` against `paper/numbers.md`. Produce
`paper/manuscript/PROVENANCE_CHECK.md` listing each number, the file it appears
in, and its script plus commit hash. Any number without a row is either given one
or removed from the manuscript.

Confirm specifically that 1,822 never appears beside a per-project number
(`PROJECT_STATE.md`, 07-25: report 1,276 key-based / 2,506 name-union / 1,822
published-and-not-reproducible).

**Acceptance:** zero unsourced numbers.
**Commit:** `paper: provenance audit of every manuscript number`

---

## 7. Out of scope — do not start these

* The SATD-interval registered report. Gated on the entity-tracking feasibility
  task and on external field judgment about the novelty margin. Not now.
* A third TypeScript corpus, or opening the tier-3 holdout (cal.diy, Twenty).
* The RefactoringMiner TypeScript paper beyond the T4 stub.
* Any new RefactoringMiner run, clone, or statistical test.
* Rewriting `README.md` wholesale. It is the outward account and stays; the
  reframing in §2 lives in the manuscript.

---

## 8. Definition of done

* No zero-byte files, no `[undocumented]` rows, no "pending" decisions
* `paper/table1_eligibility.md` and `paper/table2_visibility.md` exist and
  regenerate cleanly
* `paper/matcher_validation.md` reports precision with an interval
* `paper/manuscript/` contains eight drafted sections
* `paper/manuscript/PROVENANCE_CHECK.md` shows zero unsourced numbers
* The held-out corpus is intact: no timing statistic exists for any of the seven
  projects, in any file, run or unrun
* A target venue and date are recorded in `paper/manuscript/README.md`

---

## 9. Note to the executing agent

The unusual thing about this repository is its epistemic discipline: six
hypotheses killed with named causes, one claim self-corrected, a threshold held
when moving it would have helped, and a refusal to write a rebuild script for
caches that cannot be rebuilt. That discipline is the paper's actual contribution
and it is easy to damage by being helpful.

If you find something that looks like an error, report it rather than fixing it.
If a task seems to need a number that does not exist, stop rather than estimating
one. If a rule in §1 appears to block a task, the rule wins.

---

## 10. Execution log — deviations authorised at start (2026-07-30)

Two tasks did not match the repository as found. Both were raised before
execution and ruled on by the author.

**T8 — the corpora no longer exist.** `replication/CORPUS_FEASIBILITY.md`
records "The clones have since been deleted"; only `hadoop/` is on disk, and
Hadoop is not one of the 12. `replication/*.git.json` hold ticket→(ts, sha,
module) maps with no commit messages. **Ruling: re-clone the 12 log-only**
(`--filter=blob:none --no-checkout`) into a scratch directory outside the repo.
The validation script reads `%H` and `%B` only — no commit timestamp is fetched,
stored or derivable — so R1 holds for the seven held-out projects and the script
is incapable of producing a timing statistic. R4's "no new project clones" is
read as "no new corpora", not "never re-materialise the 12 already probed".

**T7 — the figure does not show what T7 describes.** `figures/study_funnel.png`
is the Hadoop *mining* funnel (8,919 commits → 3,949 → 51,861 refactorings → 349
episodes), which matches `README.md` §1 and is not stale. It has never shown "38
probed, 12 eligible" or hypothesis attrition, and it has **no generating
script** — `paper/numbers.md` §7 credits `scripts/filter_architectural.py`,
which contains no plotting code. **Ruling: leave `study_funnel.png` untouched
and author a new `figures/eligibility_funnel.png` from a committed script**;
report the `numbers.md` provenance error rather than fixing it, per §9.
