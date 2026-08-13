# IEEE build fixes

2026-08-06. Six items from a read of the compiled two-column PDF. Everything went
into `scripts/make_latex.py`; no generated `.tex` was hand-edited, and every fix
was verified in both the `article` and `ieee` builds.

**Both gates remain unsatisfied.** `paper/BACHMANN_DETERMINATION.md` and
`paper/SPLIT_DECISION.md` do not exist. The three markers at `related.md:101`,
`related.md:139` and `CITATION.cff:102` are untouched. Nothing split, nothing
trimmed.

**No numeric value changed.** Checked mechanically across all nine section files
and both hand-written table files: no number present before this pass is absent
after it.

---

## Item 1: the appendix tables are not clipped

**Checked before changing anything, as the brief asked, and nothing needed
changing.** Both landscape appendix pages were rasterised at 130 dpi and read.

**Table III, page 27 of the IEEE build.** The note column is complete on every
row that has one. The wrapped notes read in full:

* row 1, ozone: "60.18% of cited keys postdate the snapshot"
* row 11, kylin: "99.72% of cited keys postdate the snapshot"
* row 19, hudi: "68.28% of cited keys postdate the snapshot"
* row 33, dubbo: "denominator < 500, not usable; 87.79% of cited keys postdate
  the snapshot"
* row 36, pinot: "denominator < 500, not usable; 99.84% of cited keys postdate
  the snapshot"
* rows 37 and 38, skywalking and shardingsphere: "no tracker record for the cited
  key; 100.00% of cited keys postdate the snapshot"

All 38 rows and all 11 columns are present. **Kylin's 99.72% flag is intact**, as
are both 100.00% rows, so no flagged row has become an unflagged one.

**Table I, page 22.** The header reads `tickets cited` in full, not `tickets ci`.
All 13 columns and all 12 rows are present.

**What produced the appearance of clipping.** `pdftotext` on a page rotated by
`pdflscape` emits wrapped cell fragments out of order, which is what turns
"60.18% of cited keys postdate the snapshot" into a stray `60.` and `sna`, and
what runs two rows together as `—3 hive`. The text layer is disordered; the page
is not. The brief was right to require a visual check first, because the
extraction evidence looked convincing and was wrong.

**No change made.** Font size, text block and column widths are as they were.

## Item 2: repository memo pointers no longer Romanized

The cross-reference pass had been converting `§N` after a `.md` filename, so
`paper/numbers.md §5` printed as `§V` and sent a reader looking for a section
that file does not have.

The generator now checks what precedes the `§`. If it is a code span ending in
`.md`, the reference is a pointer into a repository memo and is left as literal
text. This is a guard in the converter, not a set of one-off edits, so a future
pass cannot re-convert them. The generator prints the list it kept literal on
every run, so the decision is visible rather than silent.

All ten instances now print Arabic in both builds, verified by extracting them
from each PDF:

| pointer | prints |
|---|---|
| `paper/numbers.md` | § 2, § 4, § 5 |
| `PROJECT_STATE.md` | § 2, § 3, § 7 |
| `audit/JUDGMENTS.md` | § 3 |
| `README.md` | § 5, § 8 |
| `results_dossier.md` | § 11 (was already correct) |

## Item 3: plural cross-references

The sweep matched `Table N` but not `Tables N and M`. Detection now covers
`Tables N and M`, `Figures N and M` and `Sections N and M`.

Two instances, both in `method.md`, both "Tables 1 and 3". They now print
**Tables 1 and 3** in the article build and **Tables I and III** in the IEEE
build, through `\ref`.

The front-matter reader's map hardcoded "the arithmetic ceiling of Section 3.1.4"
in the generator's own LaTeX rather than in the Markdown, which is why the sweep
never saw it. It is now a `\ref`, printing "Section 3.1.4" and "Section III-A4"
respectively, which agrees with the Table I caption.

The extended sweep caught nothing else. No plural section or figure references
exist in the sources.

## Item 4: the ceiling inequality was never an equation

The brief read this as a float that had drifted. It is worse than that, and it
was wrong in **both** builds, not only in the two-column one.

The line in `method.md` is

```
> |{ k ∈ Tickets(p, T) : k realised }| ≤ CSR(p) · |C_p|
```

Stripped of its blockquote marker it begins and ends with `|`, which is exactly
the shape of a Markdown pipe-table row. The parser claimed it as a table and cut
the bound into three cells: `{ k ∈ Tickets(p, T) : k realised }`, `≤ CSR(p) ·`,
and `C_p`. In the article build that came out as a one-row longtable. In the IEEE
build the same table became a `table*`, which floats, which is how it ended up
displaced from its own derivation and got noticed.

**The display equation was not floating. It did not exist.**

The parser now tests a quoted single line for formula shape before the pipe-table
rule can see it. The test is the one already used to decide display equations, so
there is one definition of what a formula is rather than two. It is scoped to
blockquotes, so a genuine data row containing `≤` (Table III's `cited ≤ N` header,
for instance) is unaffected.

The derivation now reads, in one column and on one page in both builds:

> So the number of distinct realised tickets is bounded by the number of citing
> commits:

$$\bigl|\{k \in \mathrm{Tickets}(p,T) : k\;\mathrm{realised}\}\bigr| \leq \mathrm{CSR}(p)\cdot|C_p|$$

> and dividing by |Tickets(p, T)|:

$$\mathrm{TRR}(p) \leq \frac{\mathrm{CSR}(p)\cdot|C_p|}{|\mathrm{Tickets}(p,T)|} \equiv \mathrm{ceiling}(p)$$

Set with `\[...\]`, which does not float and which the class cannot move. There
are now five display equations where there were four.

One thing this exposed: math mode eats the source space, so `k realised` was
setting as `krealised`. A bare predicate now gets an explicit thin space while a
name applied to an argument, `Tickets(p, T)`, does not. Subscripts such as
`TRR_live` are unaffected.

## Item 5: structural markers no longer leak

`## Caption` and `## Sources` are markers in the table source files, not headings
of the paper, and they were printing as body text above each caption block. They
are now suppressed in the table appendix. Zero occurrences of either as body text
in either build.

The other headings in those files are real prose headings and were kept: "Eligible
(12)", "Dropped (26)", "Two cells that are absences, and what kind of absence each
is", and "Note — where the 25% codebook figure actually belongs". Suppressing
those would have removed content rather than scaffolding.

## Item 6: the Esfandiari identifier is confirmed and kept

The arXiv record at 2404.01950 gives the same title and the same two authors as
the bibliography entry, and its Comments field reads "6 pages, DOI:
https://doi.org/10.1109/ICCKE60553.2023.10326279" — the ICCKE 2023 conference
DOI, and the same DOI the entry already carries.

**The venue is established by that DOI and by nothing else**: the record has no
`Journal reference` field. That is stated plainly rather than glossed, because the
strength of the check is the strength of the DOI.

The April 2024 posting of a December 2023 paper resolves as a postprint uploaded
after publication. **The identifier is kept.** The outcome is recorded as a dated
addendum in `paper/CITATION_VERIFICATION.md`. The page range remains unconfirmed
for the reason already recorded there: the ICCKE proceedings record is closed and
DBLP has no entry.

---

## Build

Both classes, each with a full bibtex pass.

| | `--class article` | `--class ieee` |
|---|---:|---:|
| pages | **41** | **28** |
| LaTeX errors | **0** | **0** |
| undefined references | **0** | **0** |
| overfull boxes | **0** | **1**, at 1.5pt |
| leaked markdown markers | **0** | **0** |
| section-number drift | none | none |
| display equations | 5 | 5 |
| cited works / `\cite` | 16 / 25 | 16 / 25 |

The IEEE build lost a page, 29 to 28, because the misparsed table became a two-line
equation.

## Files touched

| file | items |
|---|---|
| `scripts/make_latex.py` | 2, 3, 4, 5 |
| `paper/CITATION_VERIFICATION.md` | 6 (dated addendum) |
| `paper/IEEE_FIXES.md` | this file (new) |
| `paper/preprint/preprint.{tex,pdf,aux,bbl,out}` | regenerated |
| `paper/preprint/preprint-ieee.{tex,pdf,aux,bbl,out}` | regenerated |

No Markdown source needed editing. Every fix was a converter fault, which is the
outcome to want: the sources were already right.

Not touched: `predictions/PREDICTIONS.md`, every dated log, `requirements.txt`,
`refs.bib`, and every `[DETERMINATION PENDING]` marker.
