# Independent audit — `refactoring-review-friction`, branch `version2`

Adversarial verification of the work in `3c0c24d..e23b902` (six commits) against
the pre-work state `d0bc98e`. Conducted 2026-08-05. Nothing outside `audit/` was
modified.

---

## Verdict

**Yes, with three exceptions and one caveat — but the caveat is the important
part.** Every load-bearing *number* in `PAPER.md` reproduces. I re-derived the
entity-tracking headline from the raw detector output and the git history with an
independently written implementation and got 89.7%; I brute-forced all 180
feasible contingency tables and confirmed the κ ceiling of 0.4909 exactly; I
recomputed Spearman's rho and got −0.0097; I verified all 2,491 frozen Jira cache
files byte-for-byte; and I confirmed that all 38 pinned upstream commit shas
resolve and reproduce their published commit counts exactly. **No number was
fabricated. No citation was fabricated — every DOI and arXiv identifier resolves
to the work claimed, and every quotation I could check against extracted full text
is verbatim.** All eight hard rules were kept, including the two that are easiest
to break quietly: `predictions/PREDICTIONS.md` has exactly one commit in its
entire history, and the withdrawn "median near 35%" sentence still stands in
place with a dated correction appended below it.

The three things the author **cannot** currently defend are: `rho = −0.86` and
`930`, which appear in the manuscript with no provenance row anywhere and pass the
repository's own gate only by substring collision; and the sentence "100% of the
keys its repository cites are numbered above the snapshot", which the artifact it
describes contradicts (99.72%) and which contradicts its own numerator two clauses
later.

The caveat is larger than any of those. **The paper's headline inference is
stronger than its data support, and the estimator behind it was validated on a
set of projects that does not overlap the set it is applied to.** The 12
validation projects span commit-side 82.6–98.3%; the 21 projects that carry the
headline rho span 10.5–78.1% — **zero overlap**. And the 0.45pp validation figure
covers number-capping, not the frozen-snapshot substitution that actually produces
Table 3; the end-to-end error is 1.76pp mean and 11.91pp max, which is 3.9× and
5.6× larger. Neither fact is stated in the manuscript. On top of that, "the two
rates are uncorrelated" and "the commit-side rate carries essentially no
information about the ticket-side one" rest on n=33 with a 95% CI of
**[−0.35, +0.34]**, and no CI or test appears anywhere.

That is not a fabrication problem. It is an inference problem, and it is the one a
reviewer will find. The author can defend the arithmetic. He cannot, as currently
written, defend the sentence the arithmetic is used to support.

---

## Every claim checked, with its verdict

| # | claim | verdict |
|---:|---|---|
| **Citations** | | |
| 1 | Rath & Mäder 2019 SEOSS 33 — authors, venue, volume, DOI | CONFIRMED |
| 2 | SEOSS "Linked Change Sets [%]" column exists | CONFIRMED |
| 3 | SEOSS per-project values (Hadoop, Hive, HBase, ZooKeeper, Flink, Maven, Errai) | CONFIRMED — all 7 exact |
| 4 | SEOSS 33-project list and selection criteria quote | CONFIRMED verbatim |
| 5 | Rath et al. ICSE'18 — authors, venue, year correction | CONFIRMED |
| 6 | Rath 48% / 60% / Derby 15% / Maven 76% / 43.3% / 42.4% | CONFIRMED verbatim |
| 7 | Rath Derby table 2,638 / 1,093 / 273 / 1,272 ⇒ 51.8% | CONFIRMED |
| 8 | Rath "different practices exist…" quotation | CONFIRMED — exact string |
| 9 | Dabic et al. 2021 GHS — authors, venue | CONFIRMED |
| 10 | GHS 735,669 repositories | CONFIRMED against the paper |
| 11 | GHS 35 fields, only `totalIssues`/`openIssues` touch issues | CONFIRMED — live API, set-identical |
| 12 | GHS "735,669 repositories with 35 fields" as one present-tense claim | **UNSUPPORTED framing** — 2021 count fused with 2026 schema |
| 13 | Vieira et al. PROMISE'19 exists; linkage rates unverified | CONFIRMED / correctly UNVERIFIABLE |
| 14 | Iammarino 2021 — authors, four projects, n=201, keyword counts | CONFIRMED — all five keyword counts exact |
| 15 | Esfandiari 2023 ICCKE, 77 projects, "move class" finding | CONFIRMED |
| 16 | Esfandiari cited as sole author | **DIVERGENT** — second author Ashkan Sami omitted |
| 17 | arXiv:2605.16133 exists, May 2026, Jira-based | CONFIRMED |
| 18 | arXiv:2501.15387 exists | CONFIRMED |
| 19 | arXiv:2501.15387 characterised as "using Jira issues" | **DIVERGENT** — its abstract says SATD |
| 20 | Zenodo 15719919 — 16 repos, 1,822 projects, 2.7M issues, CC-BY-4.0 | CONFIRMED |
| 21 | Public Jira Dataset cited without authors | **DIVERGENT** |
| 22 | RefactoringMiner 3.1.4 exists, released 2026-05-24 | CONFIRMED |
| 23 | RefactoringMiner issue #1124 exists, content as described | CONFIRMED |
| **Hard rules** | | |
| 24 | `PREDICTIONS.md` never modified | CONFIRMED — one commit in its entire history |
| 25 | Dated logs not rewritten | CONFIRMED — none in the change set |
| 26 | `requirements.txt` unchanged | CONFIRMED — empty diff |
| 27 | No Jira re-fetch | CONFIRMED — 2,491/2,491 files byte-identical to manifest |
| 28 | Correction appended, original left standing | CONFIRMED — insert-only diff |
| 29 | README negatives intact and prominent | CONFIRMED — additive diff; §8 strengthened |
| 30 | Nothing published externally | CONFIRMED — topics unchanged, no DOI, deposit untouched |
| **Numbers** | | |
| 31 | rho = −0.010 over 33 | CONFIRMED |
| 32 | rho = −0.062 over 30 | CONFIRMED |
| 33 | The 0.50 exclusion threshold is not tuned | CONFIRMED — plateau across 0.40–0.60; all thresholds give |rho| < 0.13 |
| 34 | "the two rates are uncorrelated" / "essentially no information" | **UNSUPPORTED** — 95% CI [−0.35, +0.34], never reported |
| 35 | "medians differ by 2.3pp" presented without a test | **UNSUPPORTED** — Mann-Whitney p ≈ 0.94 |
| 36 | Syncope 84.8% / 36.0% | CONFIRMED |
| 37 | Estimator mean 0.45pp / worst 2.14pp | CONFIRMED as arithmetic |
| 38 | That validation covers the Table 3 estimator | **DIVERGENT** — end-to-end 1.76pp mean, 11.91pp max |
| 39 | Estimator validated where applied | **UNSUPPORTED** — 0 of 21 applied projects inside the validated range |
| 40 | Kylin 12.0% live / 0.04% frozen and its mechanism | CONFIRMED |
| 41 | Kylin "100% of cited keys postdate the snapshot" | **DIVERGENT** — 709/711 = 99.72% |
| 42 | Entity coverage 89.7% | CONFIRMED — independently re-derived from raw sources |
| 43 | Sweep 84.4 / 89.7 / 93.7 / 92.6 | CONFIRMED |
| 44 | Move Package 91.6% (185/202) | CONFIRMED |
| 45 | Chains 91.3 / 83.0 / 83.3 | CONFIRMED |
| 46 | Terminals 28.8% at HEAD, 95.1% at own commit | CONFIRMED |
| 47 | Mined window 8,376/10,083 = 83.1% | CONFIRMED |
| 48 | The FQN filter is principled, not tuned | CONFIRMED — definitional; two implementations agree on 1,025 |
| 49 | κ bounds, all five pairs | CONFIRMED — exhaustive enumeration |
| 50 | κ not computable from the recorded evidence | CONFIRMED — A/B empty in the file's only commit |
| 51 | Keyword precision 25% / 15%, recall 83% / 60%, ~4× over-count | CONFIRMED |
| 52 | Matcher precision 195/200 = 97.5% | CONFIRMED from committed labels |
| 53 | All 38 pinned upstream shas resolve and reproduce commit counts | CONFIRMED |
| 54 | "175 sourced, 0 unsourced" | **DIVERGENT** — 2 unsourced, 1 miscounted |
| 55 | `rho = −0.86` | **UNSUPPORTED** — no provenance row |
| 56 | `930` lost commits | **UNSUPPORTED** — no provenance row |
| 57 | `26.2%`, `0.33`, `1,035→797`, `p=0.3651` | traceable to prose only, no artifact |
| **Judgment** | | |
| 58 | Family classification disclosed as a judgment | CONFIRMED |
| 59 | Sensitivity analysis targets the right project | **DIVERGENT** — Atlas is benign; **Drill** is where the claim breaks |
| 60 | Rater contamination disclosed adequately | CONFIRMED — and the bias runs conservative |
| 61 | The six disputed comments genuinely satisfy both rules | CONFIRMED |
| 62 | The disputed-set size was not chosen for the result | **UNVERIFIABLE, and it lands on the global maximum** |
| 63 | `UNSOURCED.md` is complete | **DIVERGENT** — six omissions |
| **Hygiene** | | |
| 64 | Commit authorship is the author's personal identity | CONFIRMED |
| 65 | `CITATION.cff` validates against CFF 1.2.0 | **DIVERGENT** — invalid `type: dataset`; missing required `authors` |
| 66 | `LICENSE` is internally consistent | **DIVERGENT** — the archive is in two mutually exclusive buckets |
| 67 | No upstream licence conflict | CONFIRMED (attribution gap noted) |
| 68 | `deposit/` contains preparation only | CONFIRMED |

---

## Findings in full

### DIVERGENT-1 — the reported validation does not cover the estimator that produced Table 3

Two approximations are stacked: number-capping, and substituting a frozen tracker
snapshot for a live one. §4.3 reports **0.45pp mean / 2.14pp max**, which
validates *only* number-capping (it compares `τ̂` at `N_live` against the
published exact rate at `N_live`). Table 3's numbers use `N_frozen`.

The end-to-end error is computable from committed artifacts and I computed it:

```
|TRR_frozen - TRR_published| over the same 12 projects
mean 1.76pp   max 11.91pp (kylin)   mean excluding kylin 0.84pp
vs reported   0.45pp        2.14pp
ratio          3.9x          5.6x
```

`threats.md` §6.1 discloses the *mechanism* (failure mode 2, snapshot truncation)
and Table 3 flags affected projects — so this is not concealment. But the reader
is handed the smaller of two clearly distinguishable numbers immediately after the
words "the estimator is validated before it is used".

**Ironically, the frozen substitution comes out well:** 11 of 12 projects agree
within 2.93pp. That is a genuine, favourable validation of exactly the step in
question, and it is absent from the paper.

### UNSUPPORTED-1 — the estimator is applied entirely outside its validated range

```
validated  (12 projects): commit-side 82.6% .. 98.3%
applied    (21 projects): commit-side 10.5% .. 78.1%
overlap: 0 of 21
```

Every project carrying the headline rho lies outside the range where the estimator
was checked, and all 12 validation projects share one ecosystem and one commit
convention. A defensible argument exists — the error mechanism is tracker
numbering density, which has no obvious dependence on commit hygiene, and within
the 12 the error does not track the commit-side rate (rho = −0.16) — but the paper
makes neither the argument nor the disclosure.

### UNSUPPORTED-2 — the headline inference exceeds what n=33 supports

95% CI on rho: **[−0.352, +0.335]** (n=33); **[−0.413, +0.305]** (n=30). The
paper asserts "uncorrelated" and "essentially no information" in the abstract, the
§4.3 heading and the §4.3 body. What the data support is "no association
detected". A true rho of 0.3 is inside the interval and would not be "essentially
no information". No CI, no p-value and no power statement appears in `PAPER.md`,
`table3_ticket_side.md` or `numbers.md` §10c. The median comparison (55.5% vs
53.2%) is likewise untested; Mann-Whitney gives p ≈ 0.94.

### DIVERGENT-2 — "100%" where the artifact says 99.72%

`results.md` line 89 and `numbers.md` line 620: *"…because 100% of the keys its
repository cites are numbered above the snapshot."* The artifact says
**709 of 711 = 99.72%**. The sentence contradicts itself: if it were 100% the
numerator would be 0, not the 2 that produces 0.04%. Table 3's cell shows "100%"
through `:.0f` formatting, which is defensible in a table but is then repeated in
prose as an exact claim.

### DIVERGENT-3 — two manuscript numbers have no provenance at all

`scripts/check_provenance.py` tests `if token in numbers.md` — a raw substring
search against a hand-written file. It never opens a script, never runs anything,
never checks a commit hash. Three tokens pass only by collision:

| token | manuscript claim | what it matched |
|---|---|---|
| `0.86` | "collinear with module size, **rho = −0.86**" | `0.86232` — an unrelated proportion |
| `930` | "contaminated with **930** commits on other branches" | commit hash `93056ae` |
| `5.5` | section heading `## 5.5` | `15.5%` / `55.5%` |

True count: **172 sourced, 2 unsourced, 1 miscounted**, not "175 sourced, 0
unsourced". A further four numbers (`26.2%`, `0.33`, `1,035→797`, `p=0.3651`) are
traceable only to prose in other repository files, with no machine-readable
artifact.

### DIVERGENT-4 — the family sensitivity analysis targets the benign case

Reclassifying **Atlas** out of "Hadoop-ecosystem" changes a decorative sentence
and leaves the load-bearing claim intact (Atlas is 78.1% < 80%). Reclassifying
**Drill** (84.2%), **Kylin** (83.9%) or **Sqoop** (82.6%) out simultaneously
falsifies "all 12 are Hadoop-ecosystem" and puts a non-ecosystem project above the
bar. Of the three, **Drill is genuinely arguable** — it requires neither HDFS nor
YARN. `UNSOURCED.md` §1 analyses Atlas and never mentions Drill.

### DIVERGENT-5 — citation attribution defects

* **Esfandiari 2023** is cited as a single-author paper; it has two authors
  (Shima Esfandiari, **Ashkan Sami**).
* **The Public Jira Dataset** is cited in `CITATION.cff` with no authors at all
  (Lloyd Montgomery, Clara Lüders, Walid Maalej). It is CC-BY-4.0 and supplies
  every Table 3 denominator.
* **arXiv:2501.15387** is characterised in `related.md` §2.4 as "using Jira
  issues"; its abstract describes SATD items. Moderate confidence — abstract only.

### DIVERGENT-6 — `CITATION.cff` fails CFF 1.2.0

Checked against the official schema: `type: dataset` is not in the enum (valid:
`data`, `database`), and `references` requires `authors`, which the dataset entry
lacks. The file exists to make the work citable and will be rejected by
`cffconvert` and degraded by GitHub's citation widget.

### DIVERGENT-7 — `LICENSE` contradicts itself on the deposit archive

`LICENSE` line 10 places all of `deposit/` under CC-BY-4.0; line 19 places
`deposit/jira-caches-v1.tar.gz` under "NOT COVERED BY EITHER"; `zenodo.json` says
CC-BY covers the compilation but not the Apache issue content. **A Zenodo record's
licence cannot be changed after minting.**

### Undisclosed coincidence — the disputed-six lands on the global maximum

Moving 5 flagged-bucket comments from I to C gives κ_max = **0.840**, the highest
attainable under *any* reclassification count (4 → 0.765; 6 → 0.837; 7 → 0.833).
Two excluded borderline candidates (#4, #13) would each have lowered it. The six
comments are individually defensible and I could not demonstrate tuning; the
finding is robust at 0.833–0.840 across ±2 comments. But the coincidence is
undisclosed and a hostile reviewer will find it.

---

## Unverifiable

| item | what would resolve it |
|---|---|
| Whether Vieira et al. PROMISE'19 reports per-project linkage rates | institutional access to ACM DL |
| Zampetti et al. 2018 method (AST detection or not) | institutional access to ACM DL |
| Whether arXiv:2501.15387 covers 103 Apache projects, and whether it is SATD- or Jira-anchored in full | full-text access |
| Whether the entity-tracking filter was added before or after seeing 26.8% | not recoverable — the script entered git in one commit already containing the filter; the memo's account is the only record |
| Whether the disputed-six criterion was formed before or after observing that C=10 matches the human margin | not recoverable from the repository |
| Whether the frozen public-Jira snapshot date makes `TRR_frozen` comparable across projects with different tracker growth | needs the 5.81 GB deposit, not on disk; partially bounded by the 12-project gap table in `NUMBERS.md` §2.2 |

---

## Ranked: what must be fixed before this is posted anywhere

**Blocking — the paper is wrong or overstated as written**

1. **Add a CI and a test to the headline rho, and soften the claim.** Replace
   "the two rates are uncorrelated" and "carries essentially no information" with
   "we could not detect an association (rho = −0.01, 95% CI [−0.35, +0.34],
   n=33)". This is the single most likely reason a reviewer rejects the paper.
2. **State that the estimator is applied entirely outside its validated range**,
   and report the end-to-end error (1.76pp mean, 11.91pp max) alongside the
   0.45pp number-capping figure. Use the 12-project frozen-vs-live comparison —
   it is favourable and it is already computable.
3. **Fix "100% of cited keys postdate the snapshot" → 99.7% (709 of 711)** in
   `results.md` and `numbers.md`. It contradicts its own numerator.
4. **Source or remove `rho = −0.86` and `930`.** Both are in `PAPER.md` with no
   provenance row.

**High — credibility damage disproportionate to the effort**

5. **Add Ashkan Sami to the Esfandiari citation.**
6. **Add the Public Jira Dataset's three authors to `CITATION.cff`** and change
   `type: dataset` → `data`. The file currently fails schema validation.
7. **Re-check the arXiv:2501.15387 characterisation** in `related.md` §2.4
   against its full text before submission.
8. **Reconcile `LICENSE` and `zenodo.json`** on `jira-caches-v1.tar.gz` — before
   the DOI is minted, because it cannot be changed after.

**Medium — will be found by a careful reviewer**

9. **Rewrite `UNSOURCED.md` §1 around Drill**, not Atlas, and consider adopting an
   external ecosystem classification.
10. **Disclose in `LLM_RATER_PILOT.md`** that 5-moved is the ceiling-maximising
    count, and give the 0.833–0.840 robustness range that defuses it.
11. **Add the six missing items to `UNSOURCED.md`** (`JUDGMENTS.md` §4).
12. **Move the "median near 35%" correction inline**, beneath the sentence it
    corrects in `CORPUS_FEASIBILITY.md`, matching that file's own convention — and
    annotate `numbers.md` §9g, which still carries the withdrawn figure.
13. **Separate the GHS vintages**: "735,669 repositories (as indexed in 2021)"
    and "35 fields (live API, 2026)".

**Low — hygiene**

14. Add `## 5.5` to `NOT_MEASUREMENTS` in `check_provenance.py`.
15. Add a provenance/attribution header to `estimates_by_org.json` (CC-BY-4.0
    requires attribution in adapted material).
16. State plainly in `PROVENANCE_CHECK.md` what the check does and does not
    establish — it is a textual consistency check, not a provenance check, and its
    "0 unsourced" verdict currently reads as stronger than it is.
17. Note in `LLM_RATER_PILOT.md` §6.2 that the contamination biases the κ ceiling
    *upward*, so 0.491 is conservative.
18. Be aware that the `gh` credential in this environment belongs to
    `malek-ci-hub`, not the author's personal account.
19. **Inspect the staged `.gitignore` change before the next commit.** A
    `+.claude/` line is sitting in the index, added during the audit session by
    tooling rather than by me or by the prior work. `git add -A` — which all six
    prior commits used — will sweep it into the next commit unannounced. Left
    staged and untouched (`HYGIENE.md` §6).

---

## What I checked and found nothing wrong with

Stated plainly so the author can judge whether the checks were searching enough.

* **Hard rules.** All eight kept. `PREDICTIONS.md` has one commit in its entire
  history. The three dated logs are absent from the change set. `requirements.txt`
  diff is empty. All 2,491 frozen cache files match their SHA-256 digests. The
  README diff is insert-only and every negative result — the retracted Cox model,
  the six failed hypotheses with named causes, the held 0.40 threshold, §8 — is
  intact and unsoftened.
* **Fabrication.** I looked specifically for invented references and invented
  numbers, which is the highest-risk category in AI-assisted writing. **I found
  none.** Every DOI and arXiv ID resolves. Every quotation I could check against
  extracted full text is verbatim, including all seven SEOSS per-project values,
  all six Rath figures, the Rath "different practices" sentence, Iammarino's 201
  cases, and Iammarino's five keyword counts — which the prior work reported to the
  hit and which I reproduced exactly.
* **The entity-tracking GO/NO-GO.** I re-implemented the whole measurement from
  `refminer_all.json` and the `hadoop` clone with a deliberately different
  path→FQN rule and a different description parser. I got 89.7% coverage,
  1,025 FQN-preserving renames and 26.7% unfiltered — matching to within ±1 record
  on every count. **The filter that flips the verdict is definitional, not tuned.**
* **The κ bounds.** Not spot-checked — exhaustively enumerated, all 180 / 8 / 574
  / 230 / 504 feasible tables. Every bound matches to four decimal places.
* **The rho exclusion rule.** Swept across its whole range; every threshold gives
  a near-zero rho and the chosen one is on a plateau. I looked hard for tuning
  here and there is none.
* **Corpus provenance.** All 38 pinned upstream `head_sha` values resolve to real
  commits in the Apache repositories and reproduce their published
  `commits_scanned` exactly. This is the strongest single provenance result in the
  repository and, as far as I can tell, nobody had run it before.
* **Authorship and publication.** One personal identity on all six commits. No
  external write landed; the GitHub topics are unchanged and the deposit is
  untouched.
