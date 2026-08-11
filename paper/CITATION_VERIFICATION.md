# Citation verification, 2026-08-11

All 16 bibliography entries checked against a primary source. Nothing was
corrected: discrepancies are reported for the author to decide, per instruction.

**Why this file exists.** §8.3 discloses that citations were verified with LLM
assistance, which tells an arXiv moderator exactly where to look, and arXiv CS
imposes a one-year submission ban where there is incontrovertible evidence that
an author did not check LLM-generated output. Hallucinated or wrong references
are the canonical trigger. One venue error has already been found and corrected
in this paper (Nguyen et al. is WCRE'10, not MSR'10), which is evidence the
checking happens but also evidence that it was needed.

**Method.** Publisher-deposited metadata via the Crossref REST API for every
DOI, the arXiv API for every arXiv identifier, the Zenodo REST API for the
dataset, and the GitHub releases API for the software version. These are
registry records rather than my recollection, and every field below was read
from a response received in this session. Where a source could not be reached I
say so rather than inferring.

## Result

**16 of 16 PASS.** No hallucinated reference, no wrong venue, no wrong year, no
wrong author list, no wrong page range. Three observations that are not errors
are recorded at the end.

| # | key | source checked | authors | title | venue | year | pages | id | verdict |
|---:|---|---|:-:|:-:|:-:|:-:|:-:|:-:|---|
| 1 | `rath2019seoss` | Crossref `10.1016/j.dib.2019.104005` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 2 | `rath2018traceability` | Crossref `10.1145/3180155.3180207` + arXiv `1804.02433` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 3 | `dabic2021sampling` | Crossref `10.1109/MSR52588.2021.00074` + arXiv `2103.04682` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 4 | `bachmann2010missing` | Crossref `10.1145/1882291.1882308` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 5 | `bird2009fair` | Crossref `10.1145/1595696.1595716` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 6 | `bird2010linkster` | Crossref `10.1145/1882291.1882352` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 7 | `nguyen2010case` | Crossref `10.1109/WCRE.2010.37` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 8 | `herzig2013not` | Crossref `10.1109/ICSE.2013.6606585` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 9 | `wu2011relink` | Crossref `10.1145/2025113.2025120` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 10 | `iammarino2021empirical` | Crossref `10.1016/j.jss.2021.110976` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS** |
| 11 | `esfandiari2023exploratory` | Crossref `10.1109/ICCKE60553.2023.10326279` + arXiv `2404.01950` | ✓ | ✓ | ✓ | ✓ | n/a | ✓ | **PASS**, see note A |
| 12 | `vieira2019reports` | Crossref `10.1145/3345629.3345639` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS**, see note B |
| 13 | `sutoyo2026dangers` | arXiv API `2605.16133` | ✓ | ✓ | n/a | ✓ | n/a | ✓ | **PASS** |
| 14 | `sutoyo2025tracing` | arXiv API `2501.15387` | ✓ | ✓ | n/a | ✓ | n/a | ✓ | **PASS** |
| 15 | `tsantalis2026refactoringminer` | GitHub releases API | ✓ | ✓ | n/a | — | n/a | ✓ | **PASS**, see note C |
| 16 | `montgomery2025jira` | Zenodo API record `15719919` | ✓ | ✓ | n/a | ✓ | n/a | ✓ | **PASS**, see note D |

## The five you asked me to look at hardest

**[13] Sutoyo, Avgeriou, Capiluppi, arXiv:2605.16133.** Resolves. Title returned
by the arXiv API is "The Dangers of Non-Self-Fixed Architecture Technical Debt
and Its Impact on Time-to-Fix", which matches the entry exactly. Authors "Edi
Sutoyo, Paris Avgeriou, Andrea Capiluppi", matching order. Submitted
2026-05-15, consistent with the 2026 year in the entry.

**[14] Same authors, arXiv:2501.15387.** Resolves. "Tracing the Lifecycle of
Architecture Technical Debt in Software Systems: A Dependency Approach", exact
match. Same three authors, same order. Submitted 2025-01-26, consistent with
the 2025 year.

Both of these were worth checking. A recent arXiv ID in a paper that discloses
LLM-assisted citation verification is the single most likely thing a moderator
would spot-check, and a fabricated one would be fatal. They are real.

**[3] Vieira et al., PROMISE'19.** The bibliographic record is confirmed
independently through Crossref: "From Reports to Bug-Fix Commits", Proceedings
of the Fifteenth International Conference on Predictive Models and Data
Analytics in Software Engineering, 2019, pages 80–89, four authors in the order
the entry gives. This confirms the *record* only. §2.1 states the paper's
contents could not be read because ACM DL, ResearchGate and figshare all
returned 403, and that limitation is unaffected by this check. The paper's
refusal to characterise what it could not read remains correct and I did not
touch it.

**[16] Montgomery, Lüders, Maalej, Zenodo 15719919.** Record resolves. Title
"The Public Jira Dataset", creators "Montgomery, Lloyd", "Lüders, Clara",
"Maalej, Walid", published 2025-06-23, licence `cc-by-4.0`, DOI
`10.5281/zenodo.15719919`. All match the entry, including the CC BY 4.0 note.

**[15] RefactoringMiner 3.1.4.** Tag `3.1.4` exists in
`tsantalis/RefactoringMiner` and is the most recent release, ahead of 3.1.3,
3.1.2, 3.1.1 and 3.1.0.

## Notes, none of which is an error

**A. `esfandiari2023exploratory` has no page range in the entry.** Crossref
gives `096-101`. Nothing in the entry contradicts the registry; the field is
simply absent. Adding it would be an improvement, not a correction, and I left
it alone because the instruction was not to change anything silently.

**B. `vieira2019reports` is verified as a record, not as content.** See above.

**C. `tsantalis2026refactoringminer` carries `year = 2026` and author
"Tsantalis, Nikolaos and others".** Software citations have no fixed
convention, the tag exists, and the repository URL is correct. I did not verify
that tag 3.1.4 was *released* in 2026, only that it exists, so the year is
unconfirmed rather than wrong.

**D. Zenodo 15719919 is the version-specific DOI, not the concept DOI.** The
record lists its concept DOI as `10.5281/zenodo.5882881`, which addresses all
versions. Citing the version-specific DOI is the defensible choice for a paper
that froze a particular snapshot, and §3.1.3 depends on exactly which snapshot
was used, so I would keep it. Flagged only because your own instruction for
this repository's replication package was to prefer a concept DOI, and the two
cases pull in opposite directions for good reasons.

## Unverifiable

**The paper's own replication-package DOI, `10.5281/zenodo.21846139`.** It does
not resolve for me: 404 from `doi.org`, from the Zenodo record page, and from
the Zenodo REST API. A deposit with restricted access behaves exactly this way
for an anonymous request, so this is consistent with a correctly restricted
deposit and equally consistent with a wrong number. I cannot separate the two
without credentials, and I have not assumed either.

Because I could not read the deposit, I also could not confirm the §8.1 claim
that "nothing needed to reproduce a figure in this paper lives only in a
version-control host". What I can report: the preprint cites **31 distinct
artifact paths**, and all 31 exist in this repository. Whether they are inside
the deposit is the part that stayed unchecked.

Note the contrast with note D, which shows what a resolvable record looks like
through the same API. The check is available the moment the deposit is public.
