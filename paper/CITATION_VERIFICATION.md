# Citation verification

Every entry in `paper/preprint/refs.bib`, how it was checked, and what could not
be confirmed. Written 2026-08-06 while building the bibliography from scratch.

Rule 8 governs this file. Creating a reference list from nothing is the single
highest-risk operation for fabrication, so the standard applied was: a field goes
in only if a primary or canonical record was read for it. Where a field could not
be confirmed it is absent from the entry and named here. Nothing was filled in by
inference.

Three routes were used, in this order of preference.

**Full text in hand.** Bachmann, Bird and ReLink were worked from complete PDFs
already in the repository's scratch area from the prior-art brief. For these the
bibliography was checked against the paper itself, and in the case of the page
ranges also against ReLink's own bibliography, which cites all three.

**DBLP.** The canonical bibliographic index for computer science. Used for
authors, venue, year, pages and DOI.

**Publisher or preprint record.** arXiv abstract pages, PubMed Central, and the
Zenodo deposit page, where DBLP had no entry or where the deposit is the primary
object.

---

## Entries

| key | verified how | result |
|---|---|---|
| `rath2019seoss` | PubMed Central PMC6557728 for the full title and article number; DOI from `audit/CITATIONS.md`, which had already resolved it | **complete** |
| `rath2018traceability` | DBLP: authors, venue, year, pages 834-845, doi 10.1145/3180155.3180207 | **complete** |
| `dabic2021sampling` | DBLP: pages 560-564, doi 10.1109/MSR52588.2021.00074 | **complete** |
| `bachmann2010missing` | Full text held; DBLP for doi 10.1145/1882291.1882308; page range 97-106 cross-checked against ReLink reference [6] | **complete** |
| `bird2009fair` | Full text held; DBLP for doi 10.1145/1595696.1595716; pages 121-130 cross-checked against ReLink reference [7] | **complete** |
| `bird2010linkster` | DBLP for doi 10.1145/1882291.1882352; pages 369-370 cross-checked against ReLink reference [8], quoted verbatim below | **complete** |
| `nguyen2010case` | DBLP: Nguyen, Adams, Hassan, WCRE 2010, pages 259-268, doi 10.1109/WCRE.2010.37 | **complete** |
| `herzig2013not` | DBLP: ICSE 2013, pages 392-401, doi 10.1109/ICSE.2013.6606585 | **complete** |
| `wu2011relink` | Full text held for the title block and authors; ACM record for pages 15-25 and doi 10.1145/2025113.2025120 | **complete** |
| `iammarino2021empirical` | DBLP: JSS volume 178, article 110976, doi 10.1016/j.jss.2021.110976 | **complete** |
| `esfandiari2023exploratory` | arXiv 2404.01950, which carries the publisher DOI 10.1109/ICCKE60553.2023.10326279 | **pages missing**, see below |
| `vieira2019reports` | DBLP for the full title, four authors, PROMISE 2019, pages 80-89, doi 10.1145/3345629.3345639 | **metadata complete, body unread**, see below |
| `montgomery2025jira` | Zenodo record 15719919 read directly: three creators, v7, 23 June 2025, CC BY 4.0 | **complete** |
| `tsantalis2026refactoringminer` | Version and release date from `audit/CITATIONS.md`, which checked the release directly | **author list abbreviated**, see below |
| `sutoyo2025tracing` | arXiv 2501.15387 abstract page: exact title, three authors, 26 January 2025 | **complete** |
| `sutoyo2026dangers` | arXiv 2605.16133 abstract page: exact title, three authors, 15 May 2026 | **complete** |

The LINKSTER page range, quoted verbatim from ReLink's bibliography, because it
is the one entry whose range came from a third paper rather than from DBLP alone:

> "[8] C. Bird, A. Bachmann, F. Rahman, and A. Bernstein, LINKSTER: enabling
> efficient manual inspection and annotation of mined data. In FSE'10, 369-370,
> Santa Fe, New Mexico, USA, Nov 2010."

DBLP independently gives the same authors, venue, year and pages.

---

## What could not be confirmed

**`esfandiari2023exploratory`, page range.** The ICCKE 2023 proceedings record is
not open and DBLP returns zero hits for the paper. Authors, title, venue, year and
the publisher DOI are all confirmed from the arXiv record, which carries the DOI
in its journal reference field. The entry therefore has no `pages` field rather
than a guessed one. A reader following the DOI reaches the paper.

**`vieira2019reports`, the body.** Every bibliographic field is confirmed. The
paper itself is not readable: ACM Digital Library returns 403 to an
unauthenticated fetch, and `audit/CITATIONS.md` records the same for ResearchGate
and figshare. This was re-tested during this pass and the 403 stands. Section 2.1
records the work as unverified rather than characterised, and **that status is
unchanged**. The citation gives the reader the record; the prose still declines to
say what the paper found.

**`tsantalis2026refactoringminer`, the author list.** Cited as "Tsantalis and
others". Nikolaos Tsantalis is confirmed as the principal author and v3.1.4 is
confirmed as released 2026-05-24, both from `audit/CITATIONS.md`. The full
contributor list of the tool was not enumerated, so `others` is used rather than a
partial list presented as complete.

**One characterisation the bibliography does not repair.** `audit/CITATIONS.md`
section 4.2 records that section 2.4 describes arXiv:2501.15387 as using Jira
issues at file granularity, while that paper's own abstract describes a dataset of
self-admitted technical debt. The citation is now correct and the work is now in
the reference list, but **the disputed characterisation in the prose is untouched**
because changing it would alter a claim about what territory is unoccupied, and
that is not what this brief authorises. It remains an open finding in the audit.

---

## Addendum, 2026-08-06: the Esfandiari arXiv identifier

`refs.bib` pairs an ICCKE 2023 conference entry with `arXiv:2404.01950`, an April
2024 identifier. A 2024 identifier on a 2023 paper is unusual enough to be worth
checking, so the arXiv record was re-read to confirm it is the same work rather
than a different paper by the same authors.

It is the same work. From the abstract page, verbatim:

| field | value |
|---|---|
| title | "An Exploratory Study of the Relationship between SATD and Other Software Development Activities" |
| authors | Shima Esfandiari, Ashkan Sami |
| Comments | "6 pages, DOI: https://doi.org/10.1109/ICCKE60553.2023.10326279" |
| submitted | 2 Apr 2024 |

Title and both authors match the bibliography entry exactly. **The venue is
established by the DOI in the Comments field**, not by a prose journal reference:
`ICCKE60553.2023` is the ICCKE 2023 conference identifier, and it is the same DOI
the bibliography entry already carries. There is no `Journal reference` field on
the record, so the DOI is the whole of the evidence, and that is stated here
rather than implied.

The ordering resolves as an author posting a preprint after publication, which is
ordinary. **The identifier is kept.** The page range remains unconfirmed for the
reason given above.

## What was checked and found sound

* No entry was written from memory. Every one has a route in the table above.
* The two corrections the brief carried are both confirmed against primary
  records rather than accepted on the brief's word: Nguyen, Adams and Hassan is
  **WCRE 2010**, not MSR, per DBLP; and Esfandiari's paper has **two** authors,
  Shima Esfandiari and Ashkan Sami, per the arXiv record.
* Mäder and Lüders keep their umlauts, and the names carrying diacritics are
  written with LaTeX escapes so the file builds under either inputenc setting.
* The generator fails the build on a `\cite` whose key is absent from the `.bib`,
  so a citation cannot silently degrade to a question mark.
