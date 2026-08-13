# Final brief — split, preprint, and outstanding items

Run 2026-08-05. Both gates checked first; two of four tasks were unblocked, one
is blocked, one was done in full.

---

## Gate status

| gate | file | state |
|---|---|---|
| **GATE 1 — Bachmann determination** | `paper/BACHMANN_DETERMINATION.md` | **DOES NOT EXIST. Still open.** |
| **GATE 2 — one paper or two** | `paper/SPLIT_DECISION.md` | **DOES NOT EXIST. No split, no trim.** |

```
$ ls paper/BACHMANN_DETERMINATION.md paper/SPLIT_DECISION.md
ls: paper/BACHMANN_DETERMINATION.md: No such file or directory
ls: paper/SPLIT_DECISION.md: No such file or directory
$ ls paper/ | grep -iE "determin|split|decision"
(none)
```

**GATE 1.** Every `[DETERMINATION PENDING]` marker is left in place, untouched:
`related.md` §2.4, `related.md` §2.2 item 5, and the note on the Bachmann
reference in `CITATION.cff`. Nothing was adjudicated.

**GATE 2.** No split and no trim. Word count by section, as asked:

| section | words | share |
|---|---:|---:|
| abstract | 689 | 4.7% |
| intro | 978 | 6.6% |
| related | 1,812 | 12.3% |
| method | 2,261 | 15.3% |
| results | 2,720 | 18.4% |
| taxonomy | 1,232 | 8.3% |
| **threats (§6, protected)** | **3,102** | **21.0%** |
| discussion | 1,277 | 8.6% |
| acknowledgements (new, §8) | 588 | 4.0% |
| **TOTAL** | **14,659** | |

Against a ~9,500-word limit the overage is **5,159 words**. The brief's reasoning
is confirmed arithmetically: **§6 is 3,102 words and protected; §2 is 1,812.
Deleting all of §2 still leaves 3,347 words over.** Nothing else is individually
large enough. It is a split.

*(The acknowledgements section is new in this pass — Task C required an AI-use
disclosure, and a disclosure belongs in the paper, not only in a checklist. It
adds 671 words to an already-over draft. If that is the wrong call, deleting
`paper/manuscript/acknowledgements.md` and re-running the two assemblers reverses
it cleanly.)*

---

## Task A — Flink truncation check: **the explanation is confirmed to 0.004pp**

`scripts/flink_truncation.py` → `paper/flink_truncation.json`,
`paper/FLINK_TRUNCATION.md`.

```
python3 scripts/flink_truncation.py --work <dir of bare clones> \
    --out paper/flink_truncation.json
```

**Clone depth — Flink is not truncated.** Pinned sha reaches **38,219** commits
of **51,542** across all refs (74.2%); the pinned branch spans **2010-12-15 →
2026-07-24** and the repository's earliest commit on any ref is **2010-12-15**.
No Kylin-shaped defect.

**The truncation test.** Restricting to the earliest **12,419** commits — the
change-set count SEOSS 33 publishes, which is the only quantity the two studies
share:

| | commits | citing | rate |
|---|---:|---:|---:|
| our earliest 12,419 (2010-12-15 → 2017-11-17) | 12,419 | 5,214 | **41.9841%** |
| SEOSS 33, Table 2 | 12,419 | — | **41.98%** |
| our remainder (2017-11-20 → 2026-07-24) | 25,800 | 20,026 | 77.62% |
| our full history | 38,219 | 25,240 | 66.0405% |

**Gap on the matched window: +0.0041pp**, against +24.1pp on full history. The
"scope, not error" explanation holds, and two independently built probes seven
years apart agree on the same project to four decimal places once given the same
commit range.

**The practice change is visible and abrupt**: 0.0% in 2010, 2011, 2012 and 2013;
19.4% in 2014; 66.0% in 2015; 70–88% every year since. Flink graduated the Apache
Incubator in **December 2014**. Consistent, not established — n=1, no test run.

**Other projects with the same signature: none new.** The sweep found the same
four as before — kylin 7.5%, karaf 45.4%, jena 49.0%, james-project 89.4% — and
Flink is not among them. All 38 reproduce their published `commits_scanned`
exactly at the pinned sha.

**A limit of the sweep, stated because it is not obvious.** It detects only one
truncation shape: a default branch whose first commit postdates the repository's.
A repository whose *entire* history was re-imported later is undetectable this
way, because every ref would start at the same late point. Kylin was caught only
because its old branches survived.

### CLAIM CHANGE — recorded, not applied

Three places in the manuscript and one in `numbers.md` say the check has not been
run. The correct statement is now **"5 of 5 overlapping projects agree once scope
is matched, the fifth to within 0.004pp"**:

* `related.md` §2.1 — "the truncation check that would confirm this has not been run"
* `results.md` §4.4 — "and the truncation check has not been run. State it as untested."
* `paper/numbers.md` §1b — "**This is untested**"
* `paper/manuscript/UNSOURCED.md` §2 — the item can be closed
* `PROJECT_STATE.md` §6 task 16 — can be marked done

**Not applied, deliberately.** Editing §2.1, §4.4 and the abstract now would
collide with whatever split GATE 2 specifies. Provenance rows are at
`paper/numbers.md` §10h so the numbers are committed and traceable; the prose
edits are a one-pass job once the split is settled.

---

## Task B — split execution: **BLOCKED**

`paper/SPLIT_DECISION.md` does not exist. Nothing was split, moved, cut or
reorganised. The review panel's view that §5 and §7.2 are the natural boundary is
noted in the brief and is not mine to act on.

---

## Task C — arXiv preprint: prepared, **not submitted**

| deliverable | state |
|---|---|
| `scripts/make_latex.py` | Markdown → LaTeX, driven off the same section files as `assemble_manuscript.py` |
| `paper/preprint/preprint.tex` | 2,090 lines, generated |
| `paper/preprint/preprint.pdf` | **35 pages, 0 errors, 0 undefined references, 0 overfull boxes** |
| `paper/preprint/arxiv_abstract.txt` | **1,850 characters, plain ASCII** |
| `paper/manuscript/acknowledgements.md` | §8, including the AI-use disclosure |
| `deposit/ARXIV_CHECKLIST.md` | 8 manual steps and 5 known limits of the generated LaTeX |

All three tables are in the .tex, Table 3 in landscape because it is eleven
columns, plus the front-matter table map. One build fix was needed:
`microtype`'s font expansion is unavailable in this TeX installation, so it is
loaded with `expansion=false`.

**Primary category: `cs.SE` recommended**, with reasoning in the checklist §1, and
**no cross-list** — `cs.DL`, `stat.AP` and `cs.DB` were each considered and each
fits superficially at best.

**Licence: CC BY 4.0 recommended**, because `paper/` is already CC BY 4.0 and a
preprint narrower than the artifacts it describes is an odd signal; the arXiv
default licence is the right conservative alternative. All five options are
tabulated with consequences.

**One correction to the brief.** It describes the `LICENSE` contradiction on
`jira-caches-v1.tar.gz` as unresolved. **It was resolved in the preceding
revision** (`REVISION_LOG.md` item 0b): `LICENSE` now has four headings with each
path in exactly one, and heading 3 gives the compilation/content split that
matches `deposit/zenodo.json`. The Zenodo interaction the brief flags is real and
unchanged: a Zenodo licence cannot be altered after minting, so the order must be
settle-licence → mint DOI → post preprint.

**AI-use disclosure** (§8.2) is drafted factually against `REVISION_LOG.md` and
the git history: code, prose, literature verification, and the adversarial audit;
what the tools did not do; and the errors assistance introduced that review caught
— the median bug, the mis-scoped validation figure, and a provenance checker that
could not fail. **The checklist flags that only the author can verify the earlier
sessions of 19–25 July 2026**, which predate any record I can read.

---

## Task D — dataset-authors query: finalised as a draft, **not sent**

`docs/DRAFT_dataset_authors_query.md`.

**Recipients verified from a primary source** — the title page of arXiv:2201.08368,
*An Alternative Issue Tracking Dataset of Public Jira Repositories*, Montgomery,
Lüders & Maalej, MSR 2022 (doi:10.1145/3524842.3528486), not from a search
summary:

* `lloyd.montgomery@uni-hamburg.de`
* `clara.marie.lueders@uni-hamburg.de`
* `walid.maalej@uni-hamburg.de`

The Zenodo record itself carries **no** contact route, repository link or
corresponding author, which is why the paper was used. The paper also confirms the
dataset's own figures: 16 Jiras, 1,822 projects, 2.7M issues.

**273 words.** One question. No biography, positions, supervision or
circumstances. Both figures framed as failures to reproduce, nothing attributed,
nothing alleged, and the parsing script offered.

### A judgment call to check

The brief asked for **two** findings in the email. **I included one.**

The second — "the published 4,046 does not reproduce" — is **our figure, not
theirs**: it counts `BATCH-` keys in spring-batch's *git commit messages*, a
measurement this study made against a clone. Nothing in the Public Jira Dataset
produces it. Telling the dataset's authors we could not reproduce our own number
would confuse a request the brief also asked to keep to "one question, plainly
asked".

The spring-batch result *is* relevant to them — BATCH is a project in the Spring
Jira they distribute — so the draft carries a ready-to-paste paragraph framing it
as an **observation** rather than a failure to reproduce their work. Adding it
takes the email to roughly 350 words. **If you want it in, it is one paste.**

---

## Verification

```
$ python3 scripts/check_provenance.py
  ARTIFACT   195     DOCUMENTED 45     EXTERNAL 0
  ARTIFACT_NO_ROW 0  UNSOURCED 0
```

Protected files across the whole brief: `predictions/PREDICTIONS.md`,
`SLICE_LOG.md`, `worksheet.md`, `advisor_brief.md` and `requirements.txt` are
**untouched**. The frozen archive still matches its manifest
(`fcb705b664c248d0c4d3…`). No Jira was fetched: `scripts/flink_truncation.py` sets
`GIT_NO_LAZY_FETCH=1` and reads commit messages and dates only.

**Nothing was published.** No arXiv submission, no Zenodo deposit, no email sent,
no GitHub API write.

---

## Not completed

1. **GATE 1** — the Bachmann determination. Markers left in place.
2. **GATE 2 / Task B** — the split. Word counts reported; nothing cut.
3. **The Flink claim change is recorded, not applied**, for the reason above.
4. **`.gitignore`** still carries an unstaged `+.claude/` line added by tooling in
   an earlier session. Left unstaged and uncommitted across this pass too; it is
   the author's call whether to keep it.

## Uncertainties

* **The Flink match is exact to four decimal places, which is almost too good.**
  I checked it is not circular: SEOSS's 41.98% comes from `paper/PRIOR_WORK.md`
  (transcribed from their Table 2 and independently re-verified against the PMC
  copy during the audit), and 41.9841% comes from a fresh scan of a clone at a
  pinned sha. Two paths, no shared input beyond the project itself. I can see no
  mechanism by which one contaminated the other, but a reader will raise it and
  the honest answer is that the agreement is stronger than a measurement of this
  kind usually produces.
* **The Incubator-graduation corroboration is n=1 and untested.** Flink graduating
  in December 2014 and adopting the convention in 2014 is consistent with a causal
  story and is not evidence for one. §3 of `FLINK_TRUNCATION.md` says so.
* **The AI-use disclosure covers what I can see.** The commits from `3c0c24d`
  onward are in the record; the sessions of 19–25 July 2026 are not, and I have
  described them only as far as the repository documents them.

---

# Appendix — unblocked items, 2026-08-05 (second pass)

## Gate status: both still unsatisfied

```
$ ls paper/BACHMANN_DETERMINATION.md paper/SPLIT_DECISION.md
ls: paper/BACHMANN_DETERMINATION.md: No such file or directory
ls: paper/SPLIT_DECISION.md: No such file or directory
```

Nothing was adjudicated, split, trimmed, or resolved. Every
`[DETERMINATION PENDING]` marker is intact — `related.md` §2.4, `related.md` §2.2
item 5, and the `UNDETERMINED` note on the Bachmann reference in `CITATION.cff`.

## Task 1 — the "too good" objection, answered in the paper

**CLAIM CHANGE.** The Flink result is now *in* the manuscript, not only in its
memo. This is the edit deferred in the first pass; the brief unblocked it, and the
edits are local sentence replacements that survive any split.

| file | change |
|---|---|
| `related.md` §2.1 | "the truncation check ... has not been run" replaced by the matched-window result and the defence |
| `results.md` §4.4 | "**has not been run** ... stated here as untested" replaced by "five of five agree once scope is matched", the by-year series, and the defence |
| `paper/numbers.md` §1b | marked **RESOLVED 2026-08-05**; the superseded sentence is quoted, not deleted |
| `paper/manuscript/UNSOURCED.md` §2 | **CLOSED**, kept on the list so the record shows it closed by measurement |
| `paper/FLINK_TRUNCATION.md` | new §3.1, and §7 rewritten from "not applied" to "applied" |

**The argument, as written into §2.1, §4.4 and §3.1 of the memo.** The quantity is
a **deterministic count** — commits whose message matches `\b(?:FLINK)-\d+\b`, over
a commit range both studies bound identically — not an estimate, and carrying no
sampling error. Two correct implementations of the same well-specified count
*should* agree exactly; a disagreement would indicate a specification difference
(different key pattern, different range, different merge handling), not noise.
**Exact agreement is only suspicious between estimators that have sampling error.**
The residual 0.0041pp is what survives SEOSS rounding to two decimals.

Stated alongside the independence argument that already existed: SEOSS's 41.98% is
transcribed from their published table and was re-verified against the PMC copy in
the audit; 41.9841% is a fresh scan of a clone at a pinned sha by code that has
never read their table.

**Not overclaimed.** All three places say the match confirms scope alignment and
nothing further; §4.4 adds explicitly that it does **not** validate the ticket-side
estimator of §4.3, which is a genuine estimator with error (1.76pp mean, 11.91pp
max) validated separately and less comfortably.

**Still outstanding and not ours:** `PROJECT_STATE.md` §6 task 16 still lists the
Flink check as open. That file is the author's decision log.

## Task 2 — within-project temporal observation, recorded and not built on

`paper/WITHIN_PROJECT_TEMPORAL.md`, plus `paper/numbers.md` §10i.

| quantity | value | source | commit |
|---|---|---|---|
| flink by year | **0.0%** in 2010, 2011, 2012, 2013; **19.4%** 2014; **66.0%** 2015; **70–88%** every year 2016–2026 | `scripts/flink_truncation.py` → `paper/flink_truncation.json` | `b720c4e` |
| flink Incubator graduation | **December 2014** | `scripts/era_separation.py` → `paper/era_separation.json` | `1c5add6` |
| spring-batch, the mirror case | **45.6%** of 7,035; **0** of the most recent 1,000; **0.0%** every year from 2020; last used **2019** | `scripts/springbatch_recency.py` | `1c5add6` |

**Written up as a distinct unit of analysis.** The failed corpus-level test
compares 38 projects at one point each; this compares one project against itself
over time. A between-project null neither establishes nor excludes a
within-project effect, and the memo says so in those terms. The §4.1 era result
stands unchanged.

**Bounded as instructed.** n = 1, no control, no test, no p-value — the memo states
that computing one on a series selected *after* it looked interesting would present
a post-hoc test as a prospective one. Five alternative explanations are named and
none was checked. §5 of the memo lists what a real test would require.

**Verified not promoted:** `grep -ci "graduat" paper/manuscript/abstract.md
paper/manuscript/intro.md` → **0, 0**. Not in the abstract, not in the
contributions, no claim rests on it. The only claim either series supports is
taxonomy mode 4, which the paper already made.

## Task 3 — recipients corrected

**Maalej has moved, and the address on the paper is stale.** Verified from HPI's
own site (`hpi.de/en/research/research-groups/software-engineering-and-ai/`, page
last changed 28/05/2026): **Prof. Dr. Walid Maalej, Head of Software Engineering
and AI**, W3 Professor and Chair at the joint HPI / University of Potsdam Digital
Engineering Faculty, in post since 1 February. The only address HPI publishes is
**`office-maalej@hpi.de`** — the group office mailbox, shared with the office
assistant Anne Klonower (+49 331-5509-4900). There is no personal address on the
page, and the draft notes that a technical query will therefore arrive via an
assistant.

Restructured as instructed:

* **To:** Lloyd Montgomery — `lloyd.montgomery@uni-hamburg.de`
* **Cc:** Clara Marie Lüders — `clara.marie.lueders@uni-hamburg.de`
* **Cc:** Walid Maalej — `office-maalej@hpi.de`

Salutation now "Dear Dr Montgomery," with one added clause, "I have copied your
co-authors."

**Body unchanged otherwise: 273 words**, one question, framed as a reproduction
that does not match, attributing nothing and alleging nothing. The spring-batch
paragraph remains an optional paste in the notes, not in the body. **Still a
draft. Not sent.**

**An open item I could not close.** The brief flagged only Maalej as having moved,
and Maalej is now verified. **Montgomery's and Lüders's addresses are four years
old and I could not confirm either from a current institutional page** — the
Hamburg group page I fetched lists none of the three, which is consistent with the
chair having moved. Google Scholar still shows Montgomery at `uni-hamburg.de`, but
a Scholar profile is not an institutional source and I have not treated it as one.
**The draft says so and asks for both to be checked before sending**, because a
bounced primary recipient wastes the request.

## Task 4 — disclosure verification checklist

`paper/DISCLOSURE_VERIFICATION.md`. **30 assertions**, one line each, each marked
OBSERVED or INFERRED, with tick boxes for TRUE / FALSE / INCOMPLETE.

| | count |
|---|---:|
| OBSERVED — checkable in the record, and checked | 9 |
| INFERRED — not observed | 12 |
| Mixed — outcome observed, attribution inferred | 7 |
| Partly observed | 1 |
| Author's to state, not verifiable by anyone else | 1 |

**The four lines flagged as needing the closest reading:**

* **B1** — "*every* script in `scripts/` was drafted with assistance". The strongest
  claim in §8, and inferred: nine named scripts predate any session I can see.
* **C3–C6** — that the 0.80 bar, the decision to hold it, the 0.40 threshold and
  the six retractions were the author's. In each case the *outcome* is in the
  record and the *authorship of the decision* is not.
* **D5** — that the four-error list is complete. Complete as to what review
  *caught*; nothing establishes nothing else was introduced and missed.
* **A3** — silence about any other tool. An omitted tool is the failure mode
  reviewers penalise.

§8 now carries a one-line pointer to the checklist.

## Verification

```
$ python3 scripts/check_provenance.py
  ARTIFACT   201     DOCUMENTED 45     EXTERNAL 0
  ARTIFACT_NO_ROW 0  UNSOURCED 0
$ pdflatex preprint.tex   # x2
  Output written on preprint.pdf (36 pages, 419194 bytes)
```

Protected files untouched: `predictions/PREDICTIONS.md`, `SLICE_LOG.md`,
`worksheet.md`, `advisor_brief.md`, `requirements.txt`. Frozen archive still
matches its manifest. No Jira fetched.

**Nothing published.** No arXiv submission, no Zenodo deposit, no email sent, no
GitHub API write. The only network access was reading HPI's public research-group
page and the dataset paper on arXiv.

## Not completed

1. **Both gates.** Unchanged.
2. **Montgomery's and Lüders's addresses** could not be verified as current.
3. **`PROJECT_STATE.md` §6 task 16** still lists the Flink check as outstanding.
4. **`.gitignore`** still carries the unstaged tooling `+.claude/` line.

## Uncertainty

The Flink defence rests on the claim that both studies bounded the range
identically. **Ours is exact — the earliest 12,419 commits reachable from a pinned
sha. Theirs is inferred**: SEOSS publishes a change-set count, not a definition of
which 12,419. If they counted something slightly different — excluding merges,
say, or counting a different branch — then the agreement is a coincidence after
all rather than the expected behaviour of a deterministic count. I cannot rule
that out from their published table, and the argument in §2.1 and §4.4 assumes it.

---

# Evidence-extraction brief — 2026-08-05

**Scope: retrieval only.** Get the two papers, quote what they say against nine
items, trace ReLink's 54%, lay it out side by side. **No determination was made.**

## Outputs

| file | state |
|---|---|
| `paper/PRIOR_ART_EVIDENCE.md` | new — side-by-side table, 9 items × 2 papers, verbatim + locations, the 54% trace, alignments, differences, what could not be established |
| `paper/DETERMINATION_WORKSHEET.md` | new — blank. 52 questions across four sections plus a branch A/B/C block. Every answer field empty |

## Sources obtained

All three **in full text**, not abstracts:

| source | via | pages | chars |
|---|---|---:|---:|
| Bachmann et al., FSE'10, *The Missing Links* | Microsoft Research open copy | 10 | 58,418 |
| Bird et al., ESEC/FSE'09, *Fair and Balanced?* | UC Davis (Filkov) open copy | 10 | 85,602 |
| Wu et al., ESEC/FSE'11, *ReLink* | MIT (Kim) open copy | 11 | 62,464 |

## Sources unavailable

None needed for the brief. Not obtained, and not required: Bachmann's or Bird's
replication packages (would settle whether their denominators admit non-bug issue
types — recorded as open question 1 and 2 in `PRIOR_ART_EVIDENCE.md`), and any
correspondence with the ReLink authors (open question 3).

## Verification of my own extractions

272 quotations, each searched for in the source file:

| verdict | n |
|---|---:|
| EXACT — character-for-character | 216 |
| WS — matches after collapsing PDF line breaks | 39 |
| DEHYPH — plus rejoining a hyphenated line break | 1 |
| SILENT — nothing to check | 12 |
| needed elision of an interpolated figure/footnote/page break | 4 |
| **fabricated** | **0** |

The 4 elisions are marked ⚠ in the evidence file; every word was verified present
and in order, only interpolated PDF furniture was removed. Two adversarial passes
run against the extractions returned 184 CONFIRMED and 39 QUOTE_NOT_VERBATIM of
which all 39 were labelled whitespace-only. Their three substantive findings are
carried into the evidence file rather than suppressed — see below.

**One defect in my own harness, caught and fixed.** Routing quotations to a source
by the block's `paper` field sent 98 Bird quotes to the Bachmann file, because
Bird is a co-author of Bachmann and the completeness pass covers both papers in
one block. It produced 98 false fabrication flags. Fixed to route by the page
marker in the `location` field first. The counts above are post-fix.

## The 54%

Traced. **Neither cited paper contains the string "54%" or "46%".** The figure is
exactly derivable from Bachmann's Table 1, Original Dataset column: 559 fixed bug
reports, 256 linked, (559−256)/559 = **54.20%**. Bird's equivalent, computed from
its Table 1, is 63.38% pooled and never 54% for any of its seven columns; closest
is Apache at 50.40%. So ReLink's number is right, its denominator matches
Bachmann's `#Fixed bug reports` as defined by that paper's footnote 4, and its
joint attribution to "[6, 7]" is loose — it is Bachmann's figure, from one project
(Apache HTTP Server, 2004-06-18 – 2008-04-25), never printed as a percentage in
the source.

## Item 9 — where the two SILENTs are not alike

Item 9 (linkage rate as a corpus-selection criterion) was called the most
important. Both papers came back SILENT, but the two silences differ and the file
says so:

* **Bachmann's is clean.** The searches covered select / criteri / exclud /
  threshold / suitable / eligib / candidate / generaliz. The paper's only stated
  reason for its project is popularity among researchers; its other selection
  language governs the six-week window inside the already-chosen project.
* **Bird's is not.** Both adversarial passes independently flagged it as
  over-broad, citing p. 9 §7: *"we hope to use commercial datasets that have
  nearly 100% linking to conduct monte-carlo simulations"* — a linkage figure
  attached to dataset choice, though framed as the authors' own future work.
  Bird also drops one dataset (PROMISE) for a data-availability reason, not a
  linkage rate. Both passages are quoted in full in the evidence file, and
  **which reading matters is left as a worksheet judgment.**

## Statement

**No determination was made.** `paper/PRIOR_ART_EVIDENCE.md` contains no sentence
concluding that the ticket realisation rate is or is not the quantity Bachmann or
Bird measured. Its "alignments" and "differences" sections are quotation lists,
each headed *no conclusion drawn*.

**No manuscript file was modified.** `paper/manuscript/` is untouched — all nine
section files, `PAPER.md`, and the LaTeX preprint are byte-identical to their
state before this brief. `paper/BACHMANN_DETERMINATION.md` was not written. No
`[DETERMINATION PENDING]` marker was edited: they remain in `related.md` §2.4,
`related.md` §2.2 item 5, and the `UNDETERMINED` note in `CITATION.cff`. Both
gates are unchanged, nothing was split or trimmed, and nothing was published.

## Uncertainty

The nine items were searched with fixed keyword sets plus a completeness pass
asking what was missed. That is thorough but not a guarantee of exhaustiveness: a
paper can address an item in language none of the search terms reach. A **SILENT**
in the evidence file means *the searches described there did not find it*, and
Bird's item 9 is the demonstration that a SILENT can be wrong — it was overturned
by adversarial review, not by the original search.
