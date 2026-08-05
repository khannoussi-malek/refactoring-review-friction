# Revision log — MSR major revision, 2026-08-05

Response to the simulated MSR review panel and to the independent adversarial
audit in `audit/`. Where the two disagreed the audit was followed, as instructed.

**Read this first: the GATE was not satisfied, and one item is therefore
incomplete.**

---

## GATE — NOT SATISFIED. Neither branch was implemented.

The brief conditioned MAJOR-5 on a written determination from the author in
`paper/BACHMANN_DETERMINATION.md`, to be read directly from Bachmann and Bird,
and instructed: *"If that file does not exist, stop and say so. Do not infer the
answer from abstracts, summaries, or citation counts."*

```
$ ls -la paper/BACHMANN_DETERMINATION.md
ls: paper/BACHMANN_DETERMINATION.md: No such file or directory
$ ls paper/ | grep -i -E "bachmann|determin"
(none)
```

**The file does not exist. No determination was supplied. Neither Branch A nor
Branch B was implemented, and I did not decide the question.**

What was done instead, which I believe is the most that can be done without
deciding it:

* **Bachmann et al. is now cited**, verified, and described factually in §2.4 —
  the review's central finding was that this work was missing, and that gap is
  closed independently of the distinctness question.
* **The distinctness claim is marked, not made.** §2.4 carries a visible
  `[DETERMINATION PENDING]` block stating the argument for distinctness (§3.1.1
  admits all issue types and all statuses and conditions on nothing; Bachmann
  conditions on bugs and bug-fix commits), that it has not been adjudicated, and
  that the naming claim in §3.1 stands or falls with it.
* **§2.2's novelty list was edited to remove the naming claim** from the
  contribution it previously anchored. Item 5 now reads "measured across the
  whole probe", with the *naming* half marked `[PENDING]`.
* `CITATION.cff`'s Bachmann reference carries the same note.

**What the author must do:** read Bachmann and Bird, write the determination, and
then either (A) keep the definition, cite Bachmann as the direct ancestor and add
one distinguishing sentence to §2 and one to §3.1; or (B) withdraw the naming
claim with a dated correction in the manner of §2.1's first-to-measure
withdrawal, leaving the original sentence standing, and reframe the contribution
around eligibility and the taxonomy.

**A second, smaller gap:** the review document itself was not in the repository.
I worked from the summary in the revision brief (MAJOR-1…6, DA-1, DA-2,
Journal-Fit). If the full review contains items not summarised there, they are
unaddressed.

---

## Claim changes — review these first

These change **what the paper says**, not how it says it.

| # | change | from | to |
|---:|---|---|---|
| C1 | **The headline association** | "the two rates are uncorrelated"; commit-side "carries essentially no information" | "no detectable association: rho = −0.010, n = 33, 95% CI [−0.35, +0.34], permutation p = 0.958. A strong positive association is ruled out; **a null is not established.** At 80% power this study detects only \|rho\| ≥ 0.47." |
| C2 | **The flagship example** | Kylin, 83.9% vs 12.0%, "seven of every eight tickets" | **Hive, 97.0% vs 55.8%.** Kylin withdrawn as an example and retained in every table with its truncation flagged (§4.2.1) |
| C3 | **The mechanism** | none — the divergence was reported without one | the arithmetic ceiling `TRR ≤ CSR × commits/tickets` (§3.1.4), which **binds for all twelve** and accounts for a 6.0× spread against 1.19× in what is left |
| C4 | **The passing-group median** | 55.5%, gap "+2.3pp" in the passing group's favour | **52.6%**, gap **−0.64pp** — the passing group is *below* the dropped group, and the difference is not significant (Mann-Whitney p ≈ 0.94) |
| C5 | **The estimator's validation** | 0.45pp mean / 2.14pp max | **1.76pp mean / 11.91pp max** end-to-end. The 0.45pp figure validated a different approximation |
| C6 | **The estimator's scope** | not stated | applied **entirely outside** its validated range: 82.6–98.3% validated, 10.5–78.1% applied, **0 of 21** overlap |
| C7 | **The population finding** | "12 of 38 pass, and all 12 are one ecosystem" | "12 of 38 pass, and no project outside one ecosystem clears the bar" — with the label marked as a hand judgment and two measured alternatives reported as having failed |
| C8 | **Mode 4's evidence** | 4,046 of 7,034 commits, none in 20 sampled | **45.6% of 7,035**, **0 of the most recent 1,000**, **0% every year since 2020**, last used 2019. The published 4,046 **does not reproduce** and is corrected |
| C9 | **A second measurement now contradicts the first in sign** | not reported | live arm rho = **+0.518** (n = 12, exact) against frozen **−0.010** (n = 33). Both reported, neither chosen (`paper/DIRECTION_TENSION.md`) |

---

## Priority 0 — irreversible or blocking

### 0a. Staged tooling artifact — unstaged

```
$ git diff --cached --name-status
M	.gitignore          # +.claude/  — added by tooling, not by a human
$ git restore --staged .gitignore
```

**Nothing else was staged.** The change is left in the working tree, not
reverted: whether `.claude/` should be ignored is the author's call. `.claude/`
contains only `settings.local.json` and is untracked, so ignoring it is harmless
and probably right — but all six prior commits used `git add -A`, which is how it
got staged unnoticed in the first place.

### 0b. LICENSE contradiction — resolved

The archive was in two mutually exclusive buckets: heading "TEXT, FIGURES AND
DERIVED DATA" covered all of `deposit/` as CC BY 4.0, while "NOT COVERED BY
EITHER" named `deposit/jira-caches-v1.tar.gz`. `deposit/zenodo.json` stated a
third position.

`LICENSE` now has four headings, each path in exactly one, and adopts the
`zenodo.json` position for the archive: **the compilation, arrangement and
manifest are CC BY 4.0; the underlying ASF issue content is not, and no licence
is claimed over it.** A dated revision-history note at the foot of the file
records what changed and why. **Corrected in place rather than appended**, because
a licence saying two incompatible things is not a record of a past belief — and
the archive is queued for a Zenodo deposit whose licence field cannot be edited
after minting.

Upstream terms re-checked, all verified rather than assumed:

| upstream | licence | verified how | conflict |
|---|---|---|---|
| Apache Jira issue content | ASF public content, contributed under ASF terms | — | none; no licence claimed over it |
| The Public Jira Dataset (Zenodo 15719919) | **CC BY 4.0** | read from the deposit page | none; CC BY permits the derivation and requires attribution, which is now given in `LICENSE`, `CITATION.cff` and `numbers.md` |
| RefactoringMiner | **MIT, © 2019 Nikolaos Tsantalis** | read from the repository's LICENSE file | none; output is data about repositories, not a derivative of the tool |
| Apache project repositories | Apache 2.0 | — | none; not committed |

**Nothing was deposited.**

### 0c. Citations — fixed and re-validated

* **Esfandiari** → now **Esfandiari & Sami**. Verified: two authors, ICCKE 2023
  (13th ICCKE, 1–2 Nov 2023, Ferdowsi University of Mashhad), arXiv:2404.01950.
* **The Public Jira Dataset** → authors added: **Montgomery, Lloyd** (ORCID
  0000-0002-8249-1418); **Lüders, Clara**; **Maalej, Walid** — all University of
  Hamburg, read from the deposit page. *(The brief spelled the second author
  "Lueders"; the record shows "Lüders" and that is what is used.)*
* **`CITATION.cff`** → `type: dataset` was **not in the CFF 1.2.0 enum**; changed
  to `type: data`. `authors` is **required** on every reference and was missing on
  the dataset entry; added. Both defects confirmed against the official schema
  (`citation-file-format/citation-file-format@main/schema.json`): `reference`
  requires `['authors', 'title', 'type']` and the type enum contains `data` and
  `database` but not `dataset`. Licences added per reference; the top-level
  licence is now the list `[MIT, CC-BY-4.0]`, matching the dual licensing.

### 0d. Provenance checker — rebuilt

The old checker was `if token in numbers.md` — a substring test against a
hand-written file. It never opened a script, ran anything, or checked a hash.

The rebuild grades every token into four tiers and **exits 1** on the bottom two:

* **ARTIFACT** — the value is present in a committed machine-readable artifact,
  matched *numerically*: the JSON is walked, each numeric leaf rendered at the
  token's own precision. **And a `numbers.md` row must also exist.**
* **DOCUMENTED** — standalone in a `numbers.md` section naming a script that
  exists on disk or a commit hash that resolves.
* **EXTERNAL** — attributed to a cited work; the check is `audit/CITATIONS.md`.
* **ARTIFACT-NO-ROW / UNSOURCED** — failure.

**The rebuild immediately caught the audit's two findings and five more.** My
first rebuild reproduced the same defect by a different route — `0.86` matched
`0.86232` rounded to two decimals — which is why the ARTIFACT tier now *also*
requires a row. The report states plainly that a numeric match cannot establish
quantity identity, so ARTIFACT is not a claim of proof.

Rows added at `numbers.md` §10d for `rho = −0.86` (→ `social_centrality.json`
`size_confound.collinearity.rho` = −0.8555, p = 4e-69) and `930`
(→ `SUI_FINDINGS.md`, `c080775`), plus the project-count subsection that named no
script at all. §10e–§10g cover every number this revision introduced.

```
$ python3 scripts/check_provenance.py
  ARTIFACT   192
  DOCUMENTED 48
  EXTERNAL   0
  ARTIFACT_NO_ROW 0
  UNSOURCED  0
```

---

## Priorities 1–10

### P1 — the arithmetic ceiling (DA-1) — done

Derived in §3.1.4 and used to reframe §4.2 and §4.3. Columns
`commits/ticket`, `ceiling` and `TRR/ceiling` added to Tables 1 and 3.
`scripts/revision_metrics.py`.

**Not copied from the review — recomputed.** Sanity check as the review
suggested: back-solving CSR from Sqoop's ceiling gives 0.8256 against the probe's
0.8256.

The ceiling **binds for all 12** (13.7%–81.6%, 6.0× spread) and fill is flat
(median 0.887, 0.801–0.951, 1.19× spread). rho(ceiling, TRR) = **+0.965**.

### P2 — Kylin and Sqoop clone depth (DA-2) — done, and Kylin is truncated

| project | pinned | all refs | share | branch starts | repo starts |
|---|---:|---:|---:|---|---|
| **kylin** | **968** | **12,937** | **7.5%** | **2022-08-01** | 2014-05-13 |
| sqoop | 969 | 2,286 | 42.4% | 2011-06-14 | **2011-06-14 — not truncated** |

Kylin's default branch was re-initialised for Kylin 5. Its live 12.0% is measured
over four years of commits against a twelve-year tracker, so the paper could not
dismiss the frozen 0.04% as an artefact while making the 12.0% its flagship. The
example moved to Hive; abstract, §1, §4.2, §4.3, §7.1 and Table 1's caption
re-cut. Three other projects are mildly affected (Jena, Karaf, James).

**Flag text corrected**: "100% of cited keys postdate the snapshot" → **99.72%
(709 of 711)**, fixed in the generator so it cannot recur. Swept the manuscript
for other absolutes stated as rounded figures; the remaining "100.0%" (the
714/714 clock) is exact and true by construction, and is already labelled as such.

### P3 — the median (MAJOR-1) — confirmed, and it was a code bug

The review is right. `rng()` used `v[len(v)//2]`, the **upper** middle value at
even n. `statistics.median` gives **52.60%**. 55.53% is indeed the median of the
eleven non-Kylin projects. The gap is **−0.64pp**, not +2.3pp, and its sign
reverses. Fixed in `scripts/ticket_side_38.py`; the legacy value is retained in
the JSON under `median_upper_middle_legacy` so the correction is auditable.

### P4 — the headline claim (MAJOR-2 / audit 1) — done. **Claim change C1.**

CI, permutation p and a power statement added to §4.3 and carried into the
abstract, §1 and §7.1. 200,000 relabellings, seed 20260805.

### P5 — the direction disagreement — **surfaced, not resolved**

`paper/DIRECTION_TENSION.md`. Both computed: **+0.518** (live, n=12) and
**−0.010** (frozen, n=33). Both in §4.3. Neither chosen.

The brief's observation about DA-1(b) is confirmed and sharpened: **the swamping
argument does not transfer.** CSR spread is 1.19× over the twelve but **9.40×**
over the 33, so CSR is not the near-constant factor where the null is observed —
the argument predicts rho ≈ 0 more strongly on the twelve, where +0.518 is
observed.

The mechanism found: **rho(CSR, commits-per-ticket) is +0.455 over the twelve and
−0.717 over the 33.** Since TRR is nearly the ceiling in both arms, the composite
inherits that sign flip.

### P6 — the missing literature (MAJOR-5) — added, all verified

Bachmann FSE'10 · Bird ESEC/FSE'09 · Nguyen WCRE'10 · Herzig ICSE'13 · Wu
ESEC/FSE'11. New §2.4, and `paper/PRIOR_WORK.md` §5. Each distinguished from this
work rather than listed. §5.5 and §7.2 qualified: the key set still cannot be
recovered from the tracker, but link-recovery methods recover *links*, and the
unqualified claim overstated the gap.

**One correction to the brief.** Nguyen, Adams & Hassan is **WCRE'10**, not
MSR'10. And the "replication on a system with near-perfect linkage"
characterisation **could not be verified** from an accessible copy, so it is not
asserted — the citation carries only what was checked.

### P7 — incubation era vs the hand classification (MAJOR-6) — **the era hypothesis fails**

| variable | coverage | separation |
|---|---|---|
| Hadoop-ecosystem (hand) | 38/38 | **accuracy 0.868**, recall 1.000, Fisher p = 2.29e-06 |
| repository start year | 38/38 | AUC 0.611, p = 0.279, accuracy 0.711 |
| Incubator graduation | **24/38** | AUC 0.289, p = 0.098, accuracy 0.625 |

Graduation is **missing for four of the twelve passing projects** — Hive, HBase,
ZooKeeper, Ozone entered as Hadoop subprojects, not podlings — so it is
missing-not-at-random with respect to the outcome. **The free metadata is not free
for the group that matters.** The judgment is kept and marked; the abstract and
Contribution 2 are softened.

**The brief is right that the panel named the wrong project.** Atlas is benign at
78.1%. **Drill** is where it breaks, and Drill is now in `UNSOURCED.md` §1 with
the counterfactual table.

### P8 — Table 3 (Journal-Fit) — done

Introduced in §4.3, described, added to the front-matter table map, and its inline
summary labelled.

### P9 — the estimator (MAJOR-4 / audit 2 and 3) — done. **Claim changes C5, C6.**

Both figures now reported wherever the estimator is used, with the favourable
reading led (11 of 12 within 2.93pp) and the 11.91pp maximum named along with the
project that produces it. The disjoint-range finding is in §4.3, §6.1 and Table
3's caption.

**P9c — claims with margins under 11.91pp**, enumerated as instructed:

* **Not safe on this estimator:** any per-project ticket-side comparison in Table
  3 closer than ~12pp; the passing-vs-dropped median gap of 0.64pp; the
  sensitivity rho of −0.062 versus −0.010.
* **Safe, because they do not use it:** the ceiling identity (exact arithmetic);
  the eligibility result (commit-side only); Table 1's live ticket-side rates; the
  taxonomy; the entity-tracking and kappa results.

### P10 — cleanup

| item | state |
|---|---|
| spring-batch recent-history rate | **done** — `scripts/springbatch_recency.py`; and the published 4,046 does not reproduce, corrected at §10e |
| Ozone's OZONE key | **done** — §3.2 now records that it is cited zero times and is retained because the key set was fixed before the counts were read; §5.3 counts it separately as a key with no tracker record |
| rounding | **done** — one `pct()` helper; 0.04% and 0.01% no longer render as 0.0% |
| Hadoop not among the 38 | **done** — stated in §3.2 |
| 92.3% vs 97.8% double use | **done** — §3.2 now presents 26.2 / 92.3 / 97.8 as one measurement under three key sets |
| vacuous "twenty-one of the 21" sentence | **done** — removed |
| drafting note at PAPER.md:66-69 | **done** — removed from `abstract.md` |
| marginal cost per field in §7.2 | **done** — 228 MB for 38 clones, mean 6.0 MB, a 19× reduction on the original sweep |
| kappa coincidence | **done** — `LLM_RATER_PILOT.md` §4.1 and threats §6.5, with the neighbouring values |
| GHS vintage mixing (audit finding) | **done** — 735,669 (2021, published) and 35 fields (2026, live API) now kept apart |
| trim to 10 pages | **partial — see below** |

---

## Not completed

1. **The GATE.** Above.
2. **The 10-page trim.** §2.5, §2.6 and §7.4 were trimmed as instructed and §6 was
   not touched. But the revision *added* substantially more than it removed —
   §3.1.4, §4.1's separation table, §4.2's ceiling analysis, §4.2.1, §4.3's
   inference and estimator material, §2.4's five new citations. **PAPER.md is
   ~14,150 words against ~9,500 before.** It will not fit MSR's ten pages, and
   deciding what else goes is an authorial call that a reviewer's instruction to
   "not trim §6" does not settle. My recommendation, not acted on: move §4.1's
   separation table and §4.2.1 to the replication package and cite them, which is
   worth roughly 900 words without losing a claim.
3. **The Flink truncation check** (`UNSOURCED.md` §2) is still not run.
4. **The near-perfect-linkage characterisation of Nguyen et al.** could not be
   verified and is therefore not in the paper.

## Uncertainties

* **The end-to-end estimator error is measured on the twelve projects where it
  can be measured, all of which are inside the validated range.** The 11.91pp
  maximum is therefore itself an in-range figure; the error outside the range is
  unmeasured and unmeasurable without a Jira fetch.
* **`fill` on the frozen arm is not interpretable.** It has a 378× spread and a
  minimum of 0.002, against 1.19× on the live arm. The ceiling decomposition is
  reported for the live twelve; on the frozen 33 it is diagnostic only, and §4.2's
  claims rest on the live arm.
* **The Drill classification is genuinely arguable in both directions** and I have
  not resolved it. §4.1 and `UNSOURCED.md` §1 state the exposure.
* **The 4,046 spring-batch figure is not reproducible under any of five readings**
  and I could not reconstruct where it came from.

## Commands run

```
git restore --staged .gitignore
python3 scripts/revision_metrics.py --work <clones> --out paper/revision_metrics.json
python3 scripts/era_separation.py --out paper/era_separation.json
python3 scripts/springbatch_recency.py --repo <sb.git> --out paper/springbatch_recency.json
python3 scripts/ticket_side_38.py --work <clones> --out paper/ticket_side_38.json
python3 scripts/make_table1.py
python3 scripts/assemble_manuscript.py
python3 scripts/check_provenance.py
```

The 38 pinned clones and the spring-batch clone are `--filter=tree:0 --bare`
mirrors in a scratch directory outside the repository; every read is `git log`
over commit messages, with `GIT_NO_LAZY_FETCH=1` so nothing can touch the network
silently.
