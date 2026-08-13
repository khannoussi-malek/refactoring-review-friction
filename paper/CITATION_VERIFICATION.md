# Citation verification, 2026-08-11

Every citation in the paper, checked before arXiv posting. **Nothing in the
manuscript was changed.** Findings are reported for the author to decide,
because several oddities in this paper are deliberate and load-bearing.

**Why the care.** arXiv CS imposes a one-year submission ban where a preprint
shows incontrovertible evidence that an author did not check LLM-generated
output, with hallucinated or incorrect references the canonical trigger,
followed by a requirement that later submissions first be accepted at a
peer-reviewed venue. Zenodo's Generative AI Policy for Depositors (27 April
2026) applies the same standard to the replication package. §8.3 of this paper
discloses that citations were checked with LLM assistance, which tells a reader
exactly where to look. One error has already been found and corrected here:
Nguyen, Adams and Hassan is WCRE'10, not MSR'10.

**Method.** Registry records and primary texts retrieved in this session, not
recalled: the Crossref REST API for every DOI, the arXiv API and the arXiv
full-text PDF where a figure lives in the body, the Zenodo REST API, the GitHub
REST API, and a live query against the GHS search API. Where a source could not
be reached I say so and characterise nothing.

**Headline.** 16 of 16 bibliographic records PASS. 9 of 11 attributed-claim
groups verified against the source; 2 unreachable behind paywalls and recorded
as unverified rather than assumed. Part C found one internal inconsistency, and
it is cosmetic.

---

## Part A — bibliographic records

| # | reference | source consulted | verdict |
|---:|---|---|---|
| 1 | Rath & Mäder, SEOSS 33, *Data in Brief* 25:104005, 2019 | Crossref `10.1016/j.dib.2019.104005` | **PASS** |
| 2 | Rath, Rendall, Guo, Cleland-Huang, Mäder, ICSE'18, 834–845 | Crossref `10.1145/3180155.3180207`; arXiv `1804.02433` | **PASS** |
| 3 | Vieira, da Silva, Rocha, Gomes, PROMISE'19, 80–89 | Crossref `10.1145/3345629.3345639` | **PASS** on the record; see note B1 |
| 4 | Dabic, Aghajani, Bavota, MSR'21, 560–564 | Crossref `10.1109/MSR52588.2021.00074`; arXiv `2103.04682` | **PASS** |
| 5 | Bachmann, Bird, Rahman, Devanbu, Bernstein, FSE'10, 97–106 | Crossref `10.1145/1882291.1882308` | **PASS** |
| 6 | Bird, Bachmann, Rahman, Bernstein, LINKSTER, FSE'10, 369–370 | Crossref `10.1145/1882291.1882352` | **PASS**; see note A1 |
| 7 | Bird, Bachmann, Aune, Duffy, Bernstein, Filkov, Devanbu, ESEC/FSE'09, 121–130 | Crossref `10.1145/1595696.1595716` | **PASS** |
| 8 | Nguyen, Adams, Hassan, WCRE'10, 259–268 | Crossref `10.1109/WCRE.2010.37` | **PASS**, WCRE confirmed |
| 9 | Herzig, Just, Zeller, ICSE'13, 392–401 | Crossref `10.1109/ICSE.2013.6606585` | **PASS** |
| 10 | Wu, Zhang, Kim, Cheung, ReLink, ESEC/FSE'11, 15–25 | Crossref `10.1145/2025113.2025120` | **PASS** |
| 11 | Iammarino, Zampetti, Aversano, Di Penta, *JSS* 178:110976, 2021 | Crossref `10.1016/j.jss.2021.110976` | **PASS**; see note A2 |
| 12 | Esfandiari & Sami, ICCKE'23 | Crossref `10.1109/ICCKE60553.2023.10326279`; arXiv `2404.01950` | **PASS**; see note A3 |
| 13 | Sutoyo, Avgeriou, Capiluppi, 2026, arXiv:2605.16133 | arXiv API | **PASS** |
| 14 | Sutoyo, Avgeriou, Capiluppi, 2025, arXiv:2501.15387 | arXiv API | **PASS** |
| 15 | Tsantalis et al., RefactoringMiner 3.1.4, 2026 | GitHub releases + issues API | **PASS**; see note A4 |
| 16 | Montgomery, Lüders, Maalej, Public Jira Dataset, Zenodo 15719919 | Zenodo REST API | **PASS**; see note A5 |

### The elevated-risk entries

**[13] arXiv:2605.16133.** Resolves. Title returned by the API is "The Dangers
of Non-Self-Fixed Architecture Technical Debt and Its Impact on Time-to-Fix",
matching the entry word for word. Authors Edi Sutoyo, Paris Avgeriou, Andrea
Capiluppi, in that order. Submitted 2026-05-15, consistent with year 2026.

**[14] arXiv:2501.15387.** Resolves. "Tracing the Lifecycle of Architecture
Technical Debt in Software Systems: A Dependency Approach", exact match, same
three authors in the same order, submitted 2025-01-26.

These two mattered most. A recent arXiv identifier in a paper that discloses
LLM-assisted citation checking is the first thing a moderator would spot-check,
and a fabricated one would be fatal under the policy quoted above. Both are
real, and both author lists match.

**[3] Vieira et al.** The bibliographic record is confirmed independently of the
paper's own failed fetch: four authors in the stated order, PROMISE'19, pages
80–89. This confirms the record and nothing about the contents. §2.1's statement
that ACM DL, ResearchGate and figshare all returned 403 is unaffected, and its
refusal to characterise the paper remains correct. I did not touch it.

**[15] RefactoringMiner.** Tag `3.1.4` exists and is the latest release, ahead
of 3.1.3, 3.1.2, 3.1.1 and 3.1.0. Issue `tsantalis/RefactoringMiner#1124`
exists, was opened 2026-07-25 by `khannoussi-malek`, and is titled
"TypeScript: interface → type alias reported as *Change Type Declaration Kind
interface to class* (160 false positives in one commit)". That matches the
paper's description exactly, including the count and the mechanism.

**[16] Public Jira Dataset.** Record 15719919 resolves: "The Public Jira
Dataset", creators Montgomery, Lloyd; Lüders, Clara; Maalej, Walid; published
2025-06-23; licence `cc-by-4.0`. All match.

### Part A notes, none of them errors

**A1. Refs 5 and 6 share venue and year with overlapping author sets, and both
are right.** Checked separately rather than assumed. [5] is Bachmann, Bird,
Rahman, Devanbu, Bernstein. [6] is Bird, Bachmann, Rahman, Bernstein: four
authors, different lead, Devanbu absent. Crossref confirms each independently.

**A2. [11] is the co-occurrence paper, not a code-smells paper.** Crossref
returns "An empirical study on the co-occurrence between refactoring actions and
Self-Admitted Technical Debt removal", which is what §2.5 describes.

**A3. [12]'s arXiv ID year and venue year differ, and that is consistent.**
`2404` is April 2024; the arXiv posting is dated 2024-04-02 and the venue is
ICCKE 2023, held that November. A postprint deposited after the conference is
the ordinary case. The entry also omits a page range; Crossref gives 96–101.
Adding it would be an improvement, not a correction.

**A4. RefactoringMiner's `year = 2026` is unconfirmed.** The tag exists; I did
not establish when it shipped. Unconfirmed, not wrong.

**A5. Zenodo 15719919 is the version-specific DOI.** The record gives its
concept DOI as `10.5281/zenodo.5882881`. Citing the version is the defensible
choice for a paper whose §3.1.3 depends on which snapshot was used, so I would
keep it. Noted only because it pulls opposite to the instruction to prefer a
concept DOI for this paper's own package.

---

## Part B — attributed claims

| claim | source consulted | verdict |
|---|---|---|
| Rath 2018: ~48% of commits not linked to any issue | arXiv PDF `1804.02433`, full text | **VERIFIED**, verbatim |
| Rath 2018: ~43.3% of improvements, 42.4% of bugs have no commits | same | **VERIFIED**, verbatim |
| Rath 2018: six Git+Jira projects, "largely followed the practice of tagging commits with issue IDs" | same | **VERIFIED**, verbatim |
| Rath 2018: Derby and Maven among the six | same | **VERIFIED** |
| Rath 2018: per-project spread 15% unlinked in Derby to ~76% in Maven | same | **NOT SEPARATELY CONFIRMED**, see B2 |
| Dabic 2021: 735,669 repositories indexed | arXiv abstract `2103.04682` | **VERIFIED** |
| Dabic 2021: paper describes 25 characteristics | same | **VERIFIED** |
| Dabic 2021: issue-label filtering "still under development" | not reachable in abstract | **UNVERIFIED**, body text |
| GHS today: 35 fields, only `totalIssues` and `openIssues` touch issues | **live GHS API query** | **VERIFIED** |
| Public Jira Dataset: 1,822 projects | Zenodo record description | **VERIFIED** |
| Public Jira Dataset: 16 Jira repositories, ~2.7M issues | same | **VERIFIED** |
| SEOSS 33: per-project "Linked Change Sets [%]", spread, Flink 12,419 change sets | ScienceDirect **403** | **UNVERIFIED**, see B3 |
| Bachmann 2010: 493 commits, six weeks, Linkster, 47.6% | paywalled, no open copy found | **UNVERIFIED** |
| Herzig 2013: >7,000 reports, 33.8% misclassified, 39% of files | paywalled, no open copy found | **UNVERIFIED** |
| ReLink: time proximity, author identity, textual similarity | paywalled, no open copy found | **UNVERIFIED** |

### The one that mattered most

**The Public Jira Dataset reports 1,822 projects. Confirmed.** The Zenodo
record's own description reads: "We collected data from 16 public Jira
repositories containing 1822 projects and 2.7 million issues." §6.8 builds its
reproducibility finding on that number against 1,276 by final-state keys and
2,506 by name-union, and the published figure it argues with is correct as
quoted. The dataset also states 16 repositories and 2.7 million issues, both
consistent with the paper's 2,686,282.

This is the claim you flagged as the basis of a message to one of the dataset's
authors. It is right.

**GHS verified live, and the paper's two-era distinction holds.** A query
against the GHS search API returned a record with exactly **35 fields**, of
which the only issue-related ones are `openIssues` and `totalIssues`, both
GitHub-issue counts. The paper keeps the 2021 published figure (735,669
repositories, 25 characteristics) apart from the 2026 measured one (35 fields),
and it does so consistently: §2.3 and §5 both say "indexed 735,669 repositories
as published in 2021 and exposes 35 fields per record today".

### Part B notes

**B1. Vieira is a record check only**, as above.

**B2. The Derby 15% / Maven ~76% spread was not separately confirmed.** The
paper's sentence attributes a per-project range to Rath 2018, and the source
does state significant variance across projects and does carry a per-project
table. I found the table but did not extract those two cells cleanly from the
PDF text layer, so I am recording the specific pair as unconfirmed rather than
claiming verification I did not do. The two headline percentages either side of
it are verbatim.

**B3. SEOSS 33 could not be fetched.** ScienceDirect returned 403 to an
unauthenticated request. The five overlapping project figures, the 8.11–97.13%
spread, Errai at 8.11%, and the load-bearing Flink change-set count of 12,419
are therefore **unverified against the publisher**. This is the most valuable
remaining check, because §4.4's reproduction to +0.0041pp is built on that
12,419, and it is also the figure quoted in the endorsement email to Rath. You
have institutional or personal access routes I do not.

---

## Part C — internal consistency

**C1. Bibliography and citations close exactly.** 16 entries, 16 cited. Nothing
cited that is absent from the bibliography, nothing in the bibliography left
uncited.

**C2. Repeated numbers agree.** Counted in the built PDF: Hive 97.0% (12
occurrences), 18,213 commits (6), 55.8% (7), 29,635 tickets (5); the 12-of-38
result (5); ceiling range 13.7% (3) and 81.6% (5); fill median 0.89 (2), range
0.80 (12) and 0.95 (5); rho −0.010 (4) with n = 33 (3); rho +0.518 (3); the
estimator error 1.76pp (4) and 11.91pp (8). No contradictory value found for any
of them.

**C3. The subscript rule holds.** §3.1.4 states that an unsubscripted `TRR`,
`ceiling` or `fill` means the quantity in general, and that every measured value
carries its subscript, in prose, abstract and table captions. Scanning the built
PDF for a bare token adjacent to a measured value, after excluding section
cross-references and table column headers, returns **zero** violations. Table
headers use the bare word and their captions carry the subscripts, which is what
the rule permits.

**C4. Kylin's 99.72% is consistent everywhere.** Three occurrences, and the
paper states the correction explicitly: "99.72% for Kylin (709 of 711), not
100%; an earlier draft printed 100%". No surviving claim of 100% for Kylin. The
two `100.00%` figures elsewhere belong to shardingsphere and skywalking, which
genuinely have no tracker record, and are correct.

### The one inconsistency found

**The confidence interval appears at two precisions.** §4.3's prose and §7.1
give `95% CI [−0.35, +0.34]`; Table 3's association note gives
`95% CI [−0.352, +0.335]`. Same interval, different rounding. Nothing is wrong
and no claim changes, but a reader comparing the two will pause, and the
two-decimal form appears twice against the three-decimal form once. Left alone,
as instructed. If you want them uniform, the table's three-decimal form is the
one with the digits.

---

## Summary: unverifiable, separated from wrong

**Verified as wrong: nothing.** No hallucinated reference, no wrong venue, year,
author list, page range or identifier. No attributed figure contradicted by a
source I could reach.

**Could not verify, and why:**

1. **SEOSS 33's contents** (five project figures, the 8.11–97.13% spread, Errai,
   and the Flink 12,419 change-set count). ScienceDirect 403. Highest value of
   the remaining checks.
2. **Bachmann 2010, Herzig 2013 and ReLink** attributed figures. Paywalled, no
   open copy located. The bibliographic records for all three are confirmed.
3. **Dabic's "still under development"** wording about issue-label filtering.
   Body text, not in the abstract.
4. **Rath 2018's Derby 15% / Maven ~76% pair.** Present in the source's tables;
   not cleanly extracted, so recorded as unconfirmed.
5. **RefactoringMiner's 2026 release year.** Tag confirmed, date not.
6. **This paper's own replication DOI, `10.5281/zenodo.21846139`.** 404 from
   `doi.org`, from the Zenodo record page and from the Zenodo REST API. A
   restricted deposit behaves exactly this way for an anonymous request, so this
   is equally consistent with a correctly restricted deposit and with a wrong
   number, and I have not assumed either. Note the contrast: record 15719919
   returned full metadata through the same API in the same session, so the check
   works the moment the deposit is readable. Until then §8.1's claim that
   nothing needed to reproduce a figure lives only in a version-control host
   remains unconfirmed, though all 31 artifact paths the paper cites do exist in
   this repository.

The distinction between these two lists is the one §2.1 of the paper models:
an unverifiable source is recorded as unverified, not characterised.
