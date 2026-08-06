# Bibliography, cross-references, and two-column layout

2026-08-06. Four tasks. Everything went into `scripts/make_latex.py`, the Markdown
sources, and a new `paper/preprint/refs.bib`; no generated `.tex` was hand-edited.

**Gate status. Both remain unsatisfied.** `paper/BACHMANN_DETERMINATION.md` and
`paper/SPLIT_DECISION.md` do not exist. Nothing was split and nothing was trimmed.

One note on the brief's line numbers: it asks that the `[DETERMINATION PENDING]`
markers at lines 177 and 194 be left alone. Those lines in `related.md` hold
ordinary prose. The markers are actually at `related.md:101` and `related.md:139`,
plus the `UNDETERMINED` note at `CITATION.cff:102`. All three are untouched, which
is what the instruction intends.

**No numeric value changed.** Checked mechanically across all nine section files:
no number present before this pass is absent after it.

---

## Task 1: the bibliography

`paper/preprint/refs.bib`, 16 entries. Every one is verified against a primary or
canonical record, and the route for each is in `paper/CITATION_VERIFICATION.md`.

The manuscript was swept for sources named in prose. **Nothing was found beyond
the brief's list**, so no entry was added on top of it. The sweep covered all nine
section files and the three table files, looking for venue tags, author-and-year
patterns, arXiv identifiers, DOIs and named artifacts. The only sources the paper
discusses are the sixteen below.

| entry | status |
|---|---|
| Rath & Mäder, SEOSS 33, Data in Brief 25:104005, 2019 | complete |
| Rath, Rendall, Guo, Cleland-Huang & Mäder, ICSE 2018, 834-845 | complete |
| Dabic, Aghajani & Bavota, MSR 2021, 560-564 | complete |
| Bachmann, Bird, Rahman, Devanbu & Bernstein, FSE 2010, 97-106 | complete |
| Bird, Bachmann, Aune, Duffy, Bernstein, Filkov & Devanbu, ESEC/FSE 2009, 121-130 | complete |
| Bird, Bachmann, Rahman & Bernstein, LINKSTER, FSE 2010, 369-370 | complete |
| Nguyen, Adams & Hassan, **WCRE 2010**, 259-268 | complete |
| Herzig, Just & Zeller, ICSE 2013, 392-401 | complete |
| Wu, Zhang, Kim & Cheung, ReLink, ESEC/FSE 2011, 15-25 | complete |
| Iammarino, Zampetti, Aversano & Di Penta, JSS 178:110976, 2021 | complete |
| Esfandiari & **Sami**, ICCKE 2023 | **pages unconfirmed** |
| Vieira, da Silva, Rocha & Gomes, PROMISE 2019, 80-89 | metadata complete, **body unread (403)** |
| Montgomery, **Lüders** & Maalej, Public Jira Dataset, Zenodo 15719919 | complete |
| Tsantalis et al., RefactoringMiner v3.1.4 | **author list abbreviated to "and others"** |
| Sutoyo, Avgeriou & Capiluppi, arXiv:2501.15387 | complete |
| Sutoyo, Avgeriou & Capiluppi, arXiv:2605.16133 | complete |

Both corrections the brief carried were checked against primary records rather
than taken on trust, and both hold. Nguyen, Adams and Hassan is WCRE 2010 per
DBLP. Esfandiari's paper has two authors per the arXiv record.

**Vieira keeps its unverified status.** The bibliography entry is complete because
its metadata is confirmable; the prose in section 2.1 still declines to say what
the paper found, because ACM, ResearchGate and figshare all still return 403. The
citation gives a reader the record without the paper claiming to have read it.

Citations are marked in the Markdown as `[@key]`, which reads as a citation in the
source and becomes `\cite{key}` in the LaTeX. **25 `\cite` commands over 16
works**, placed at first use and wherever the prose leans on a work's findings.
The author names in the prose stay exactly as they were; the citation supplements
them. `IEEEtran` numeric style, so references print as [1], [2].

The generator now fails the build if a `\cite` names a key that is not in the
`.bib`, so a citation cannot quietly degrade into a question mark.

## Task 2: real cross-references

The sources hardcoded section and float numbers as literal text. They are now
real references, resolved by the generator rather than by editing the Markdown,
so the sources stay readable as Markdown.

* **51 `\label{sec:N}`**, one per numbered heading, keyed by the number the prose
  already cites. The sources did not have to learn a key scheme.
* **78 section `\ref`** converted from `§N` and `Section N`.
* **31 float `\ref`**: 7 to Table 1, 5 to Table 2, 18 to Table 3, 1 to Figure 1.
* **Zero** literal `Section N`, `Table N` or `Figure N` remain in either build.

**Two references are deliberately still literal**, both instances of `§11`. They
point at section 11 of `results_dossier.md`, a repository memo, not at a section
of this paper. Pointing them at a paper label would be wrong. The generator
reports any reference it could not resolve rather than silently emitting a
dangling `\ref`, which is how these two were found.

**Links are coloured, not hidden.** `hidelinks` is gone. Internal references are a
dark blue, citations a dark green, external URLs a dark plum, all chosen to print
as near-black on paper while being visibly clickable on screen. An internal link a
reader cannot see is one they will not use.

Zero undefined references in both builds.

One consequence worth knowing: because these are now real references, they track
the document class. The article build prints "§3.1.3"; IEEEtran numbers sections
in Roman, so the same reference prints "§III-A3". Both are correct, and that is
the point of the change. Nothing in the prose now names a number that the
typesetter is not also producing.

## Task 3: two-column IEEE layout

`--class ieee` produces `\documentclass[conference]{IEEEtran}`, two-column, with
the author block as specified:

```
Malek Khannoussi
Independent Researcher
Tunisia
khannoussimalek@gmail.com
```

An `\IEEEkeywords` block carries the five keywords from the hyperref metadata.

**The tables. No data was dropped.** Two strategies, chosen by what each table
actually is.

**The eight body tables use option 1: `table*` spanning both columns.** They are
all small, 3 to 7 rows over 3 to 4 columns, so they fit a float comfortably. One
of them has rows 289 characters wide, which a single 8.8cm column would strangle,
and spanning both columns gives 18cm.

**The three big tables use option 3: a one-column landscape appendix.** Option 1
does not work for them and the reason is mechanical rather than aesthetic:
`longtable` refuses to run in a two-column body, failing with "longtable not in
1-column mode", and Table 3 is 38 rows over 11 columns, which no single-page float
can hold. Option 2, splitting by column group, would have worked but makes the
reader reassemble a row across two floats to compare a project's ceiling against
its fill, which is exactly the comparison the mechanism rests on. The appendix
therefore drops to one column, where `longtable` works and pages break naturally,
and `pdflscape` supplies the measure. **Every row and every column survives**,
including the ceiling and fill columns.

**The document class is a parameter**, as asked. `--class article` is the
single-column arXiv preprint and stays the default; `--class ieee` is the
two-column conference layout. An ACM `acmart` target slots into the same place.
The figure adapts with the class: `figure*` across both columns in IEEE, a
landscape page in the article build.

Two things had to be fixed to make IEEEtran build at all on this machine, and both
are recorded because they will bite anyone rebuilding it. IEEEtran requests
Courier for `\texttt`, which a basic TeX Live does not ship, and the run dies with
"Metric (TFM) file not found"; the preamble now points `\ttdefault` at Latin
Modern Mono. And `IEEEtran.cls` and `IEEEtran.bst` were not installed, with
`tlmgr` unable to fetch them across a release boundary, so both were downloaded
from CTAN into `paper/preprint/`. Keeping them beside the `.tex` also makes an
arXiv upload self-contained.

## Task 4: carried-over fixes

**4a. Done.** The abstract and section 1 both said the ceiling binds for all
twelve at 13.7-81.6% without naming the measurement, which Table 3 contradicts
with Ozone at 176.0%, Ranger at 130.4% and Knox at 100.0%. Both now say
`ceiling_live` explicitly, and section 1 adds that three ceilings exceed 100%
under the frozen snapshot and stop binding. No number changed.

**4b. Done.** `\date{\today}` is replaced by a fixed `BUILD_DATE` constant. A
paper built on pinned shas and a SHA-256 manifest should not re-date itself on
every compile.

**4c. Reported, not changed.** The sentence is generated by
`scripts/ticket_side_38.py` and lands at `paper/table3_ticket_side.md:54`:

> **21 dropped projects have a higher ticket realisation rate than the worst
> passing one**: accumulo, atlas, calcite, cxf, flink, flume, helix, hudi,
> james-project, jena, karaf, oodt, parquet-java, servicecomb-java-chassis,
> storm, struts, syncope, tika, tomee, wicket, zeppelin.

Its context is the association paragraph, which immediately before it gives the
passing group as 0.0-68.6% and the dropped group as 29.5-84.8%.

**Why it is vacuous as written.** The worst passing value is Kylin's `TRR_frozen`
of 0.04%, and that figure is the flagged truncation artefact: 99.72% of Kylin's
cited keys postdate the frozen snapshot, so the number cap removes almost the
entire numerator. The sentence therefore says that 21 projects score above 0.04%.
The dropped group's own floor is 29.5%. Every one of the 21 dropped projects with
a usable denominator clears the threshold, so the count is 21 of 21 and carries no
information. Worse, the phrasing invites the reading that dropped projects
systematically beat passing ones, which the medians do not support: 52.6% passing
against 53.2% dropped is not a separation.

**Recommended disposition, for the author to accept or reject.** Keep the
comparison, change its reference point. Compare against the worst passing project
*excluding* Kylin, and say so, which turns a threshold nothing can fail into one
that discriminates. State the count as "21 of 21" so a reader sees immediately
that the criterion is not selective. Keep the project list, which is useful, and
keep the medians beside it since they carry the real message that the two groups
do not separate.

The change belongs in `scripts/ticket_side_38.py` rather than the artifact, and
regenerating that table requires the clone scan, so it is not a change to make
silently in passing. **Nothing was removed.**

---

## Build

Both targets, each with a full bibtex pass.

| | `--class article` | `--class ieee` |
|---|---:|---:|
| pages | **41** | **29** |
| LaTeX errors | **0** | **0** |
| undefined references | **0** | **0** |
| overfull boxes | **0** | **1**, at 1.5pt |
| leaked markdown markers | **0** | **0** |
| section-number drift | none | none |
| cited works / `\cite` commands | 16 / 25 | 16 / 25 |
| float numbers | Fig 1, Tables 1-3 | Fig 1, Tables 1-3 |

The single remaining overfull box in the IEEE build is 1.5pt, about half a
millimetre.

## Files touched

| file | task |
|---|---|
| `paper/preprint/refs.bib` | 1 (new) |
| `paper/preprint/IEEEtran.cls`, `IEEEtran.bst` | 3 (fetched from CTAN) |
| `scripts/make_latex.py` | 1, 2, 3, 4b |
| `paper/manuscript/related.md` | 1 (citation markers only) |
| `paper/manuscript/method.md`, `taxonomy.md` | 1 (citation markers only) |
| `paper/manuscript/abstract.md`, `intro.md` | 1, 4a |
| `paper/CITATION_VERIFICATION.md` | 1 (new) |
| `paper/BIBLIOGRAPHY_PASS.md` | this file (new) |
| `paper/preprint/preprint.tex`, `.pdf`, `preprint-ieee.*` | regenerated |

Not touched: `predictions/PREDICTIONS.md`, every dated log, `requirements.txt`,
`paper/table3_ticket_side.md`, and every `[DETERMINATION PENDING]` marker.
