# 4. Results

**Status: to write** (writing order 1 — write this first). Prose around Tables 1
and 2; the tables carry the numbers and this section carries the argument.

## Structure

**4.1 Corpus eligibility is the binding constraint.** → `paper/table1_eligibility.md`,
`figures/eligibility_funnel.png` panel A. 12 of 38 clear the bar; all 12 are
Hadoop-ecosystem; no general-purpose Java project clears it, the best being James
at 74.8% with the median near 35%. Hadoop adjacency is not sufficient — Parquet
fails at 29.1% and Accumulo at 43.0%. The signal is a specific commit-hygiene
convention, not a dependency relationship.

**4.2 The channel that is published is not the channel that is needed.** The
paper's strongest single measurement. Commit-side 82.6–98.3% against ticket-side
12.0–69.0% on the same 12 projects. **Kylin: 83.9% of commits cite a ticket while
12.0% of tickets ever receive one** — it clears the bar comfortably and leaves
seven of every eight tickets with no commit at all. Carry the truncation caveat
in the same breath: ticket-side was computed **only** for the 12 that already
passed, so the range is within-passing variation and licenses nothing about the
26 dropped projects.

**4.3 The measure replicates independently.** 4 of 5 overlapping projects within
3.3pp of SEOSS 33 across corpora seven years apart. Flink differs by 24.1pp and
that is scope, not error — their snapshot 12,419 commits against our 38,219 —
**and the truncation check has not been run** (`PROJECT_STATE.md` §6, task 16).
State it as untested.

**4.4 Convergent invisibility across three channels and two ecosystems.**
→ `paper/table2_visibility.md`. The cells are non-comparable by construction and
that is the point; every cell carries its denominator; **no aggregate across
cells.** Two cells are absences of different kinds: Apache/pull-request is a
structural `n/a`, Apache/commit-message is a gap in this study.

**4.5 The standard sampling frame cannot express the criterion.** GHS: 735,669
repositories, 35 fields, only `totalIssues`/`openIssues` touch issues and both are
GitHub-issue counts. No tracker type, no linkage, no commit convention.

## Do not put here

The six killed hypotheses (they live in `intro.md`, one paragraph). The Hadoop
friction results — this paper is about whether the corpus can support such a
study, not what such a study found.
