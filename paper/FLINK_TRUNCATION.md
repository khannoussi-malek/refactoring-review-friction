# The Flink truncation check — the untested explanation is confirmed to 0.004pp

**Verdict: the "scope, not error" explanation holds, and holds more exactly than
the claim it was defending.** Restricting our probe to the same number of commits
SEOSS 33 reports reproduces their published rate to **four decimal places**.

Run 2026-08-05. `scripts/flink_truncation.py`, output `paper/flink_truncation.json`.

```
python3 scripts/flink_truncation.py --work <dir of bare clones> \
    --out paper/flink_truncation.json
```

---

## 1. What was outstanding

`paper/numbers.md` §1b, `related.md` §2.1 and `paper/manuscript/UNSOURCED.md` §2
all carry the same open item. Four of the five projects overlapping SEOSS 33
agree within 3.3pp; Flink differs by **24.1pp** (41.98% there, 66.0% here). The
repository asserted this was scope rather than error — their snapshot holds
12,419 commits against our 38,219 — and flagged the assertion as **untested** in
all three places.

Two things had to be checked, because Kylin taught the lesson that a rate can be
measured over a window nobody noticed:

1. **Is the probed clone truncated?** Kylin's pinned sha reached 968 commits from
   2022-08-01 — 7.5% of its repository — which moved the paper's flagship example.
2. **Does the rate over a matched commit count reproduce SEOSS?**

---

## 2. Clone depth — Flink is not truncated

| quantity | value |
|---|---|
| commits at the pinned sha `1ea8cb0e4e` | **38,219** |
| commits across all refs | 51,542 |
| share on the pinned branch | 74.2% |
| pinned branch spans | **2010-12-15 → 2026-07-24** |
| repository's earliest commit, any ref | **2010-12-15** |
| **branch starts after the repository?** | **NO** |

The pinned branch begins at the repository's first commit. The 26% of commits on
other refs are release and feature branches, which is ordinary. **Flink carries no
Kylin-shaped defect**, and the 66.0% is a rate over Flink's whole history.

The probe's published `commits_scanned` was also re-derived: **38 of 38 projects
reproduce their published commit count exactly at the pinned sha.**

---

## 3. The truncation test — a 0.004pp match

Aligning on **commit count** rather than on a date, because SEOSS publishes a
change-set count and no cutoff date, so the count is the only quantity the two
studies share. The earliest 12,419 commits reachable from the pinned sha:

| | commits | citing a Jira key | rate |
|---|---:|---:|---:|
| **our earliest 12,419** (2010-12-15 → 2017-11-17) | 12,419 | 5,214 | **41.9841%** |
| **SEOSS 33, Table 2** | 12,419 | — | **41.98%** |
| our remainder (2017-11-20 → 2026-07-24) | 25,800 | 20,026 | 77.62% |
| our full history | 38,219 | 25,240 | 66.0405% |

> **Gap on the matched window: +0.0041pp.** Against +24.1pp on full history.

This is not merely consistent with the scope explanation. It is the strongest
single piece of cross-corpus validation in the repository: two independently
implemented probes, built seven years apart by different people from different
clones, agree on the same project to **four decimal places** once they are given
the same commit range.

## 4. And the practice change is visible

The scope explanation asserted that Flink's citation practice changed over the
decade we cover and SEOSS does not. It did, and the change is abrupt:

| year | commits | citing | rate |
|---|---:|---:|---:|
| 2010 | 37 | 0 | **0.0%** |
| 2011 | 1,880 | 0 | **0.0%** |
| 2012 | 1,518 | 0 | **0.0%** |
| 2013 | 509 | 0 | **0.0%** |
| 2014 | 2,084 | 404 | **19.4%** |
| 2015 | 2,146 | 1,416 | **66.0%** |
| 2016 | 2,035 | 1,595 | 78.4% |
| 2017 | 2,541 | 2,036 | 80.1% |
| 2018 | 2,703 | 1,888 | 69.8% |
| 2019 | 4,588 | 3,215 | 70.1% |
| 2020 | 5,235 | 4,109 | 78.5% |
| 2021 | 4,213 | 3,318 | 78.8% |
| 2022 | 3,092 | 2,472 | 79.9% |
| 2023 | 2,085 | 1,740 | 83.5% |
| 2024 | 1,657 | 1,457 | 87.9% |
| 2025 | 1,064 | 886 | 83.3% |
| 2026 | 832 | 704 | 84.6% |

Flink cited **no Jira keys at all** for its first four years, adopted the
convention during 2014, and has run at 70–88% ever since. SEOSS's window is
2010-12 → 2017-11, so it averages four zero years against three high ones and
lands at 42%. Ours averages four zero years against twelve high ones and lands at
66%.

**A corroboration worth noting, and one this repository is positioned to make:**
Flink **graduated from the Apache Incubator in December 2014**
(`scripts/era_separation.py`, from https://incubator.apache.org/projects/, read
2026-08-05) — the same year the convention appears. That is consistent with
graduation bringing ASF process conventions with it, and it is a hypothesis this
check happens to be consistent with rather than a result it establishes: n = 1,
and no test was run.

---

## 5. This is mode 4 inside the validation set

Flink is a clean instance of taxonomy **mode 4, "convention changed
mid-history"** — the mode the paper illustrates with spring-batch, which went the
other way (45.6% overall, 0% every year since 2020). Flink is the mirror image:
0% for four years, then 70–88%.

Both make the same point and the paper should say so: **a single lifetime rate
averages two regimes, and which number you get depends on where your snapshot
stops.** SEOSS and this study disagreed by 24.1pp on the same project without
either being wrong.

That is also, uncomfortably, a caution about **our own** 0.80 bar. Every rate in
Table 1 is a lifetime rate at a pinned sha. A project whose convention started
late is penalised; one that abandoned it recently is flattered. The bar was
pre-registered on the lifetime rate and is not moved — but §5.5's fourth
recommended field, "the rate recomputed over recent history", is a
recommendation this study did not apply to itself, and that is now demonstrated
twice rather than argued once.

---

## 6. Other projects with the same signature

Sweeping all 38 for a pinned branch that starts after the repository does:

| project | pinned | all refs | share | branch from | repo from |
|---|---:|---:|---:|---|---|
| **kylin** | **968** | **12,937** | **7.5%** | **2022-08-01** | 2014-05-13 |
| karaf | 10,058 | 22,138 | 45.4% | 2007-11-26 | 2005-07-19 |
| jena | 13,091 | 26,732 | 49.0% | 2012-05-08 | 2002-12-19 |
| james-project | 17,374 | 19,424 | 89.4% | 2006-09-30 | 2006-09-22 |

**No new cases.** These four are the same set `scripts/revision_metrics.py`
found, and Flink is not among them. Kylin remains the only severe instance;
James's eight-day offset is noise; Karaf and Jena lose early history to
pre-migration repositories but both retain more than a decade.

**A caveat on this sweep.** It detects only one truncation shape — a default
branch whose first commit postdates the repository's. It cannot detect a
repository whose *entire* history was re-imported at some later date, because
then every ref starts at the same late point and there is nothing to compare
against. Neither could the Kylin check; Kylin was caught because its old branches
survived. Nothing here rules that shape out for any of the 38.

---

## 7. What changes in the paper

**This is a claim change, and it strengthens rather than weakens.** Three places
carry "the truncation check has not been run" and must now carry the result:

* `related.md` §2.1 — "**and the truncation check that would confirm this has not
  been run**" → the check was run and the matched-window rate is 41.98% against
  SEOSS's 41.98%.
* `results.md` §4.4 — "**and the truncation check has not been run**. State it as
  untested." → same.
* `paper/numbers.md` §1b — "**This is untested** — the truncation check ... has
  not been run."
* `paper/manuscript/UNSOURCED.md` §2 — the item can be closed.
* `PROJECT_STATE.md` §6, task 16 — can be marked done.

The headline for §4.4 moves from *"4 of 5 overlapping projects agree within
3.3pp, and the fifth is explained but untested"* to **"5 of 5 agree once scope is
matched, the fifth to within 0.004pp."**

**These edits are not made here.** They change what the paper claims, and the
manuscript is currently frozen pending GATE 2 (the split decision) — editing
§2.1, §4.4 and the abstract now would collide with whatever split the author
specifies. The change is recorded here and in `paper/FINAL_BRIEF_LOG.md` for the
author to apply, or for a follow-up pass once the split is decided.
