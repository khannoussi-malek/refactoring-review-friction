# Prior-art evidence — Bachmann FSE'10 and Bird ESEC/FSE'09, side by side

**This file draws no conclusion.** It is retrieval: what the two papers say, in
their own words, with locations, so the author can read efficiently and decide.
The decision sheet is `paper/DETERMINATION_WORKSHEET.md`. **Nothing here states or
implies whether the quantity defined in `method.md` §3.1 is or is not the quantity
these papers measured**, and the `[DETERMINATION PENDING]` markers are untouched.

Compiled 2026-08-05.

---

## Provenance and how the quotations were checked

| source | obtained from | pages | state |
|---|---|---:|---|
| Bachmann, Bird, Rahman, Devanbu & Bernstein, *The Missing Links: Bugs and Bug-fix Commits*, FSE'10, pp. 97–106 | Microsoft Research open copy | 10 | **full text** |
| Bird, Bachmann, Aune, Duffy, Bernstein, Filkov & Devanbu, *Fair and Balanced? Bias in Bug-Fix Datasets*, ESEC/FSE'09, pp. 121–130 | UC Davis (Filkov) open copy | 10 | **full text** |
| Wu, Zhang, Kim & Cheung, *ReLink*, ESEC/FSE'11, pp. 15–25 | MIT (Kim) open copy | 11 | **full text** |

**All three were worked from full text.** Nothing here rests on an abstract or a
summary.

**Every quotation was mechanically checked against the source.** 272 extracted
quotations; each was searched for in the source file at three levels of
strictness:

| | count | meaning |
|---|---:|---|
| **EXACT** | 216 | appears character-for-character |
| **WS** | 39 | appears after collapsing line breaks inside sentences — a PDF layout artefact, not an alteration |
| **DEHYPH** | 1 | additionally required rejoining a word hyphenated across a line break |
| **SILENT** | 12 | the agent reported the paper is silent; nothing to check |
| **needed elision** | 4 | see below |
| **fabricated** | **0** | |

The 4 requiring elision are sentences the PDF text layer interrupts: two by a
figure caption and its data labels, one by two footnote lines, one by a page
break. In each case **every word was verified present, in order, in the source**;
only the interpolated figure/footnote material was elided. They are marked ⚠ in
the tables below.

Two independent adversarial passes were run against the extractions, instructed to
refute rather than confirm: 184 CONFIRMED, 9 INCOMPLETE, 3 SILENT_IS_WRONG, and 39
QUOTE_NOT_VERBATIM of which **all 39 were "whitespace-only"** — line-break
collapsing that the mechanical check already accounts for. The three
SILENT_IS_WRONG findings are incorporated below and flagged.

---

## The side-by-side table

Each cell is a verbatim quotation with its location. Longer supporting evidence
for each item follows in §"Item detail". **SILENT** means the paper does not
address the item; it is never an inference.

| # | item | **Bachmann et al. FSE'10** | **Bird et al. ESEC/FSE'09** |
|---:|---|---|---|
| **1** | **quantity measured** (defining sentence) | "This means, that only<br>47.6% of bug ﬁx related commits ( 32+7<br>82 ) are documented<br>in the bug tracking database."<br><br>*p. 6, §6.1 "Bugs Incognito"* | "Figure 2 shows the proportion of ﬁxed bugs that can be<br>linked to speciﬁc commits broken down by severity level."<br><br>*p. 6, §5 "Bug Type Feature: Severity"* |
| **1b** | **numerator / denominator in the paper's words** | "As shown in Table 2, we have 82 bug ﬁx related com-<br>mits in our evaluation dataset. 32 of them (bug report)<br>are directly related to the bug tracking database. 7 other<br>commits contain a bug-ﬁx, but are not the initial bug ﬁx<br>commit rather than a merge of versions"<br><br>*p. 6, §6.1* | "1 Total ﬁxed bugs 24119 113877 1383 68299 33924 117021 1121<br>2 Linked ﬁxed bugs 10017 34914 686 37498 2754 45527 343"<br><br>*p. 6, Table 1, rows 1–2* |
| **1c** | **formal set definitions** | **SILENT** — "the paper defines no such symbols; the only named data sets are A and J" (§7.2) | "We denote the entire set of bugs in the bug database as B. Some of these bugs have been ﬁxed by making changes to the source code, and been marked ﬁxed; we denote these as Bf."<br>"We denote this set of “linked” bug ﬁx commits as Cf l and the set of linked bugs in the bug repository as Bf l."<br><br>*p. 3, §3 "BACKGROUND AND THEORY"* |
| **2** | **is the denominator restricted to bugs?** | Denominator of the headline rate is **commits**: "As shown in Table 2, we have 82 bug ﬁx related com-<br>mits in our evaluation dataset."<br><br>*p. 6, §6.1* | Denominator of the headline rate is **fixed bugs**: "Unfortunately,\|Bf l\| is usually quite a bit smaller than\|Bf\|."<br><br>*p. 3, §3* |
| **2b** | **restricted to *fixed* bugs?** | "4We deﬁne “ﬁxed” bug reports as bug reports that have at least one<br>associated ﬁxing activity (which means a status change to “ﬁxed”)<br>within the considered time period."<br><br>*p. 3, Table 1 footnote 4* | "Some of these bugs have been ﬁxed by making changes to the source code, and been marked ﬁxed; we denote these as Bf."<br><br>*p. 3, §3* |
| **2c** | **are non-bug issue types in or out?** | Commit-side categories are **separate and non-exclusive**: "Note, a single commit can<br>have many annotations, e.g., a commit may be annotated<br>as both a “bug ﬁx” and a “feature request”."<br><br>*p. 5, §6*<br><br>Bug-report side counts non-bugs **inside** the base: "#Duplicate bug reports 364 (15.11%) 8 (7.77%)<br>#Invalid bug reports 766 (31.80%) 38 (36.89%)"<br><br>*p. 3, Table 1* ‡ | **SILENT** on issue types. The extraction searched "enhancement", "improvement", "sub-task", "issue type", "resolution", "WONTFIX", "priority"; the paper never states whether non-bug types are included or excluded. Its denominator is defined only as Bf, bugs "marked ﬁxed". |
| **3** | **unit of analysis, and direction** | **Commits.** "While they studied 10 bugs in detail, we focus on commit history: we employed an expert … to fully annotate a sample of 493 commits."<br>"Thus the linked bug-ﬁx commits are a sample of the entire group of commits."<br><br>*p. 3 §2.2; p. 8 §7* | **Both, but only the bug side is computed.** "We note here that both commit features and bug features can be measured … However, Bf l represents only a portion of the ﬁxed bugs, Bf."<br>"our analysis is conﬁned to bug feature bias."<br><br>*p. 4 §3; p. 5 §5* |
| **3b** | **why the other direction is not computed** | Reports both sides of Table 1 descriptively: "#Linked bug reports 256 (10.63%)" and "#Linked commit messages 472 (5.50%)"<br><br>*p. 3, Table 1* | "Observation 3.3. Given a set of linked commits Cf l, there is no way to know if commit feature bias exists, lacking access to the full set of bug ﬁx commits Cf ."<br><br>*p. 4, §3* |
| **4** | **scope** | "engaging a core developer of the Apache HTTP web server project to exhaustively annotate 493 commits that occurred during a six week period."<br>Original dataset 2004-06-18 – 2008-04-25: "#Bug reports 2,409 (100%) … #Commit messages 8,580 (100%)"<br><br>*p. 1 abstract; p. 3 Table 1* | "Additionally, we gath-<br>ered data for ﬁve projects: Eclipse, Netbeans, the Apache<br>Webserver, OpenOﬃce, and Gnome."<br>Seven columns incl. AspectJ and two Eclipse extractions; 359,744 fixed bugs in total.<br><br>*p. 4 §4; p. 6 Table 1* |
| **5** | **method** | **Manual, one expert.** "We engaged an expert Apache core developer, Dr. Justin Erenkrantz, to use Linkster to manually annotate 6 full weeks (including 493 commit mes-<br>sages) of the Apache history."<br>"All 493 commits in our selected temporal sample were annotated."<br><br>*p. 1 §1; p. 5 §6* | **Automated, with a manual audit of the matcher.** "1. Scan through the commit messages for numbers in a given format … 3. Check if the potential reference number exists in the bug database."<br>"we manually examined 1,500 randomly sampled commit log messages that were marked as unlinked … we looked at 30,000 commit log messages that were marked as linked"<br><br>*p. 5, §4* |
| **6** | **every numeric linkage rate** | 47.6% of 82 bug-fix commits documented; 16% (13/82) mailing-list only; 21% (17/82) neither; "#Linked bug reports 256 (10.63%) 10 (9.71%)"; "#Linked commit messages 472 (5.50%) 29 (5.88%)"; "#Fixed bug reports 4 559 (23.20%) 23 (22.33%)"; 37.1% / 62.9% of all commits functional; per-developer 26 linked / 52 not | Table 1 rows 1–2 per project (7 columns); "In the apache project, 63% of the ﬁxed minor bugs are linked, but only 15% of the ﬁxed blocker bugs are linked."; false-negative CI 0.14%–0.78%; false-positive bound .05%; "We discovered that 81% of the ﬁxed bugs in AspectJ were closed by just three people" ⚠ |
| **7** | **stated purpose** | "Given<br>the wide use of linked defect data, it is vital to gauge the<br>nature and extent of the bias, and try to develop testable<br>theories and models of the bias."<br>"RQ 1: Do the bug reporting and ﬁxing practices of developers correspond to the assumptions commonly made by researchers?"<br><br>*p. 1 abstract; p. 2 §1* | "The question naturally arises, are the bug ﬁxes recorded in these historical datasets a fair representation of the full population of bug ﬁxes?"<br>"We now turn to the critical question, Does bug-feature bias matter?"<br><br>*p. 1 abstract; p. 8 §6* |
| **8** | **across projects, or within one?** | **Within one.** "3. CASE STUDY: APACHE The Apache HTTP web server is an Open Source soft-<br>ware system developed under the auspices of the Apache Software Foundation."<br><br>*p. 3, §3* | **Across.** "Table 1: Data and results for each of the projects."<br>"EclipseZ EclipseB Apache Netbeans OpenOﬃce Gnome AspectJ"<br><br>*p. 6, Table 1* |
| **9** | **linkage rate as a corpus selection / exclusion criterion** | **SILENT** as to linkage rate. The stated reason for choosing the project is popularity: "Apacheis also one of the most popular Open Source projects<br>among researchers. … and<br>thus a good subject for an in-depth examination of data<br>quality." *(p. 3, §3)* Selection language elsewhere concerns the **time window** inside the already-chosen project, not projects. | **SILENT** as to selecting projects on linkage rate — but **not silent on datasets**. See §9 detail: one dataset was dropped for lacking a full record of closed bugs; project choice is stated on governance diversity; and future work names a linkage figure. |

‡ Flagged by the adversarial pass as a correction to an over-broad SILENT.
⚠ Required eliding an interpolated page break; all words verified present in order.

---

## Item detail

### Item 9 — the item the brief calls most important

**Bachmann FSE'10.** The extraction returned **SILENT** for linkage-rate-based
project selection, and the adversarial pass did not overturn it. The passages
that come closest, none of which uses a linkage rate:

> "Apacheis also one of the most popular Open Source projects
> among researchers. It is widely used in current empirical
> software engineering research (e.g., [25, 28, 20, 8, 18]), and
> thus a good subject for an in-depth examination of data
> quality."
> — p. 3, §3, the paper's only statement of why this project was chosen

> "With our own (rather modest) resources, we could only
> completely evaluate and manually verify a subset of the orig-
> inal Apache dataset. Therefore, we had to sample the orig-
> inal dataset. There were two choices: random sampling or
> temporal sampling."
> — p. 3, §3.3 — selection *within* the chosen project

> "To ﬁnd a “typical” period for our evaluation dataset we ana-
> lyzed the whole original Apache dataset based on week-long
> epochs. Then, we chose a period of 6 consecutive weeks
> that was as representative as possible to the overall original
> Apache dataset in terms of its descriptive process statistics"
> — p. 4, §3.3 — the stated criterion is representativeness of process statistics

> "We showed that there are vast diﬀerences between
> the projects, particularly with respect to the quality of the
> link rate between bugs and commits."
> — p. 3, §2.2 — the only use of "link rate" across projects, summarising prior work

> "This variation in
> bug datasets requires a cautious approach to their use in em-
> pirical work."
> — p. 2, §2.2 — attributed to the surveyed prior work

> "It seems prudent to assume that
> the Apache project is not a complete exception and that,
> therefore, the data used in studies of other projects may also
> lack important information."
> — p. 8, §6.7, threats to external validity

**Bird ESEC/FSE'09.** The extraction returned **SILENT**, and **both adversarial
passes overturned it** as over-broad. The relevant passages:

> "We also
> attempted to use other datasets, speciﬁcally the PROMISE
> dataset [42]. However, for our study, we also needed a full
> record of closed bugs, the set Bf. These datasets included
> only ﬁles that were found to include bug ﬁxes, and in many
> cases, do not identify the bugs that were ﬁxed, and thus it is
> impossible to tell if they are a biased sample of the entire set
> of bugs."
> — p. 4, §4 — **a dataset excluded**, for lacking a full record of closed bugs, not for a linkage rate

> "Additionally, we gath-
> ered data for ﬁve projects: Eclipse, Netbeans, the Apache
> Webserver, OpenOﬃce, and Gnome. They are clearly quite
> diﬀerent sorts of systems. In addition, while they are all open-
> source, they are developed under varied regimes."
> — p. 4, §4 — the stated basis for the project set

> "The biases
> we observed may be speciﬁc to the processes adopted in the
> projects we considered; however, we did choose projects with
> varying governance structures, so the results seem robust."
> — p. 9, §7 — the only explicit verb of project choice; criterion is governance variety

> **"Second, we hope to
> use commercial datasets that have nearly 100% linking to
> conduct monte-carlo simulations of statistical models of bi-
> ased non-linking behaviour, and then develop & evaluate,
> also in simulation, robust methods of overcoming them"**
> — p. 9, §7 — **this is the passage both adversarial passes flagged.** A linkage
> figure attached to which datasets will be used, framed as the authors' own
> future work.

> "Interestingly, the trend is prevalent in
> every dataset for which the more accurate method, which we
> believe captures virtually all the intended links, has been used."
> — p. 6, §5 — results discounted by link-capture completeness at dataset level

> "In all the projects where the manually
> veriﬁed data was used (all except AspectJ and Eclipse Z)"
> — p. 6, Figure 2 caption — same qualification

### Item 6 — the full rate inventory

**Bachmann.** Table 1 (p. 3) reports, for the Original Dataset and Evaluation
Sample respectively:

> "#Bug reports 2,409 (100%) 103 (100%)
> #Fixed bug reports 4 559 (23.20%) 23 (22.33%)
> #Linked bug reports 256 (10.63%) 10 (9.71%)
> #Duplicate bug reports 364 (15.11%) 8 (7.77%)
> #Invalid bug reports 766 (31.80%) 38 (36.89%)"

> "#Commit messages 8,580 (100%) 493 (100%)
> (transactions)
> #Empty commit messages 0 (0.00%) 0 (0.00%)
> #Linked commit messages 472 (5.50%) 29 (5.88%)"

Both percentage columns are computed against the row marked (100%) — bug-report
rates against 2,409 bug reports, commit rates against 8,580 commit messages.

**Bird.** Table 1 (p. 6) reports raw counts only, with no derived ratio printed:

> "EclipseZ EclipseB Apache Netbeans OpenOﬃce Gnome AspectJ
> 1 Total ﬁxed bugs 24119 113877 1383 68299 33924 117021 1121
> 2 Linked ﬁxed bugs 10017 34914 686 37498 2754 45527 343"

---

## The 54% figure — traced

**ReLink's claim**, verbatim from the file (p. 2, §1; the letter-spacing is the
PDF text layer's, not ours):

> "Bird and Bachmann et al. confirmed this problem and reported that 54% of fixed
> b u g s i n t h e b u g d a t a b a s e a r e n o t l i n k e d t o change logs [6, 7]."

ReLink's references, verbatim from its bibliography:

> "[6] A. Bachmann, C. Bird, F. Rahman, P. Devanbu, and A. Bernstein, The Missing
> Links: Bugs and Bug-ﬁx Commits. In FSE’10, 97-106, Santa Fe, New Mexico, USA,
> Nov 2010."
> "[7] C. Bird, A. Bachmann, E.Aune, J. Duffy, A. Bernstein, V.Filkov, and P.
> Devanbu, Fair a n d balanced?: bias in bug-fixing datasets. In ESEC/FSE'09, Aug.
> 2009, 121-130."

**The string "54%" appears nowhere in either cited paper.** Nor does "46%". This
was checked mechanically across both full texts.

**It is derivable from Bachmann Table 1, and the derivation is exact:**

| | value | source |
|---|---:|---|
| #Fixed bug reports, Original Dataset | **559** | Bachmann p. 3, Table 1 |
| #Linked bug reports, Original Dataset | **256** | Bachmann p. 3, Table 1 |
| fixed − linked | 303 | |
| **303 / 559** | **54.20%** | |

The Evaluation Sample column gives 23 fixed, 10 linked → 13/23 = **56.52%**.

**Bird's numbers do not produce 54%** under any aggregation tried:

| | not linked |
|---|---:|
| pooled over all seven Table 1 columns (131,739 linked of 359,744 fixed) | **63.38%** |
| mean of the seven per-project rates | 63.67% |
| median of the seven | 61.10% |
| per-project range | 45.10% (Netbeans) – 91.88% (OpenOffice) |
| closest single value to 54% | Apache, **50.40%** |

**Assessment of ReLink's characterisation, as asked:**

* **The number is right and traceable** — to Bachmann's Table 1, Original Dataset
  column, as a two-row subtraction the paper never prints as a percentage.
* **"fixed bugs in the bug database"** matches Bachmann's denominator, which is
  `#Fixed bug reports`, defined by its footnote 4 as bug reports "that have at
  least one associated ﬁxing activity (which means a status change to “ﬁxed”)
  within the considered time period."
* **The joint attribution to "[6, 7]" is loose.** The figure is Bachmann's alone;
  Bird's own equivalent, computed from its Table 1, is 63.38% pooled and never
  54% for any project.
* **It is a single-project figure.** Bachmann's Table 1 covers only the Apache
  HTTP web server, 2004-06-18 – 2008-04-25. ReLink's sentence does not say so.

---

## Points where the papers appear to align

Quoted, **no conclusion drawn**.

**Both state that the linked set is a proper subset and that the full set is not
observable.**

> Bachmann: "Thus the linked bug-ﬁx commits are a sample of the entire group of
> commits." *(p. 8, §7)*
> Bird: "Observation 3.1. Linked bug ﬁxes Cf l can sometimes be found, amongst the
> commits C in a code repository by pattern-matching, but all the bug-ﬁxing
> commits Cf cannot be identiﬁed without extensive, costly, post-hoc eﬀort."
> *(p. 3, §3)*

**Both frame the work as being about bias in data used for defect research.**

> Bachmann: "Given the wide use of linked defect data, it is vital to gauge the
> nature and extent of the bias" *(p. 1, abstract)*
> Bird: "In this paper, we investigate historical data from several software
> projects, and ﬁnd strong evidence of systematic bias." *(p. 1, abstract)*

**Both restrict their denominator with an explicit notion of "fixed".**

> Bachmann: "4We deﬁne “ﬁxed” bug reports as bug reports that have at least one
> associated ﬁxing activity (which means a status change to “ﬁxed”) within the
> considered time period." *(p. 3, footnote 4)*
> Bird: "Some of these bugs have been ﬁxed by making changes to the source code,
> and been marked ﬁxed; we denote these as Bf." *(p. 3, §3)*

**Both report a rate on the bug-report side and a rate on the commit side, in the
same table or section.**

> Bachmann: "#Linked bug reports 256 (10.63%)" and "#Linked commit messages 472
> (5.50%)" *(p. 3, Table 1)*
> Bird: "We denote this set of “linked” bug ﬁx commits as Cf l and the set of
> linked bugs in the bug repository as Bf l." *(p. 3, §3)*

**Neither states a linkage-rate threshold for admitting a project to a study.**
Bachmann is SILENT; Bird is SILENT for project selection but not for dataset
choice (§9 detail).

## Points where they appear to differ

Quoted, **no conclusion drawn**.

**The headline rate is computed in opposite directions.**

> Bachmann: "only 47.6% of bug ﬁx related commits ( 32+7 82 ) are documented in the
> bug tracking database" — denominator **82 commits** *(p. 6, §6.1)*
> Bird: "Figure 2 shows the proportion of ﬁxed bugs that can be linked to speciﬁc
> commits" — denominator **fixed bugs** *(p. 6, §5)*

**One project versus seven columns.**

> Bachmann: "3. CASE STUDY: APACHE" *(p. 3)*
> Bird: "Table 1: Data and results for each of the projects." *(p. 6)*

**Manual ground truth versus automated matching with a manual audit.**

> Bachmann: "All 493 commits in our selected temporal sample were annotated."
> *(p. 5, §6)*
> Bird: "we manually examined 1,500 randomly sampled commit log messages that were
> marked as unlinked … we looked at 30,000 commit log messages that were marked as
> linked" *(p. 5, §4)*

**Formal set notation in one, absent in the other.**

> Bird: "We denote the entire set of bugs in the bug database as B. … we denote
> these as Bf." *(p. 3, §3)*
> Bachmann: **SILENT** — no such symbols; the only named data sets are A and J
> (p. 9, §7.2).

**Bird explains why it does not compute the commit-side rate; Bachmann reports
both descriptively.**

> Bird: "Observation 3.3. Given a set of linked commits Cf l, there is no way to
> know if commit feature bias exists, lacking access to the full set of bug ﬁx
> commits Cf ." *(p. 4, §3)*
> Bachmann: "#Linked bug reports 256 (10.63%)" / "#Linked commit messages 472
> (5.50%)" *(p. 3, Table 1)*

**On non-bug issue types.** Bachmann's commit categories are explicitly
non-exclusive and separate bug fix from feature request — "a commit may be
annotated as both a “bug ﬁx” and a “feature request”" *(p. 5, §6)* — and its
bug-report base counts duplicates and invalids inside the 100% row *(p. 3,
Table 1)*. Bird is **SILENT** on issue types throughout.

---

## What could not be established from the full text

| # | question | why it could not be settled | what would resolve it |
|---:|---|---|---|
| 1 | Whether Bird's Bf includes non-bug issue types (enhancements, tasks) | The paper defines Bf only as bugs "marked ﬁxed" and never discusses issue typing. Its sources are Bugzilla and IssueZilla, whose type semantics the paper does not state. | The replication package, or the Zimmermann Eclipse dataset documentation it builds on |
| 2 | Whether Bachmann's "#Bug reports 2,409" base includes non-bug types | Table 1 counts duplicates and invalids inside the base but never enumerates issue types | The underlying Apache Bugzilla extract |
| 3 | Whether ReLink's authors derived 54% from Bachmann's Table 1 as we did, or from some other route | ReLink states the figure and cites both papers without showing a derivation | Correspondence with ReLink's authors |
| 4 | Whether Bird's 63.38% pooled figure was ever computed by its authors | The paper prints only the raw counts; the pooled percentage is our arithmetic on their Table 1, not their statement | Nothing in the paper resolves this |
| 5 | Whether either paper would regard a linkage rate as a legitimate selection criterion | Neither addresses the question. Bird's "nearly 100% linking" sentence is future work on their own datasets, not guidance | Correspondence with the authors |

**On item 5, a note on how to read the two SILENTs.** Bachmann's is a clean
silence: the search covered "select", "criteri", "exclud", "threshold",
"suitable", "eligib", "candidate", "generaliz" and more, and nothing in the paper
ties a linkage rate to project inclusion. Bird's is not clean, and both
adversarial passes said so: the "nearly 100% linking" sentence is a linkage figure
governing dataset choice, even though it is about the authors' own planned future
work rather than a recommendation to others. **Which of those two readings
matters is a judgment, and it is one of the things the worksheet asks you to
make.**
