# Independent verification pass, 2026-08-08

Auditor's note: I did not write the repository under audit, and nothing in it
was taken on trust. Every verdict below comes from re-derivation in this
session against a primary artifact, or it is marked UNVERIFIABLE. No file in
the repository was modified. All building was done in a throwaway clone so the
audited state could not be disturbed by the act of auditing it.

State audited: branch `msr2027` at `de4b14e`, cloned fresh from the local
repository. The working tree carried one uncommitted modification at audit
time, `paper/manuscript/PROVENANCE_CHECK.md`, which is a generated file that
`scripts/check_provenance.py` rewrites whenever it runs.

Sections A, B and C of the brief are complete. Section D onward was truncated
in transmission and is not covered.

## Verdict summary

| check | verdict |
|---|---|
| A1 fresh clone | VERIFIED |
| A2 README followed exactly | **FAILED** |
| A3 both targets build | **FAILED** for ACM, VERIFIED for IEEE |
| A4 machine-bound build | **FAILED**, with one UNVERIFIABLE part |
| A5 no build artifacts committed | **FAILED**, but they carry no usernames |
| B1 PDF text greps | VERIFIED |
| B2 source and .tex greps | VERIFIED |
| B3 metadata and XMP | VERIFIED |
| B4 attachments and annotations | VERIFIED |
| B5 URLs | VERIFIED, and see the note on what is missing |
| B6 AI disclosure survives `anonymous` | VERIFIED |
| B7 named individuals | VERIFIED, one item referred to the author |
| C1 documentclass | VERIFIED |
| C2 `review` active | VERIFIED |
| C3 `anonymous` active | VERIFIED |
| C4 CCS and keywords | VERIFIED |
| C5 page count | **FAILED**, measured below |
| C6 IEEE build unbroken | VERIFIED |

Four findings are severe enough to block submission and are collected at the
end.

---

## A. Reproducibility from clean

### A1 Fresh clone: VERIFIED

`git clone --branch msr2027 file:///Users/malek/phd/walid/rq1-starter` into an
empty scratch directory. Landed at `de4b14e`, working tree clean. No existing
tree reused. The clone contains `paper/msr2027/{README.md, main.tex, main.pdf,
refs.bib}` and no `acmart.cls`, which is correct: the class is gitignored.

Observation, not a defect: `main.tex` and `main.pdf` are both committed even
though `main.tex` is generated. A committed generated file can disagree with
its source, and nothing in the build checks that it does not.

### A2 README followed exactly: FAILED

`paper/msr2027/README.md` gives two build commands. The first succeeded. The
second failed:

```
$ python3 scripts/make_latex.py --out paper/msr2027/main.tex --template acm --selfcheck
Self-check: no leaked markdown, no section-number drift, environments balanced.
exit 0

$ cd paper/msr2027 && pdflatex main
! LaTeX Error: File `acmart.cls' not found.
exit 1
```

The README describes obtaining acmart in prose, under "acmart is not
vendored", but gives no commands for it. A reader following the file as
written cannot build. Steps that had to be guessed, none of which appear as
runnable instructions:

1. Download `acmart.zip` from CTAN. The URL is not given.
2. Run `pdftex acmart.ins` to generate `acmart.cls` from the source. The
   README does not say the class must be generated rather than downloaded.
3. Copy `acmart.cls` and `ACM-Reference-Format.bst` into `paper/msr2027/`.
4. Unpack roughly seventeen dependencies into `~/Library/texmf`. The README
   lists their names but gives no command, no source URL and no ordering.
5. Run `updmap-user --enable Map=zi4.map`. This one is stated, but only after
   the reader has already completed steps 1 to 4.

I completed the build only by copying `acmart.cls` and the `.bst` from the
audited working tree, which a third party would not have.

### A3 Both targets build: FAILED for ACM, VERIFIED for IEEE

IEEE, in the clone: `pdflatex` exits **0**, produces **26 pages**, and the
bibliography resolves to 42 citation markers.

ACM, in the clone: `pdflatex` exits **1** and produces a 17-page PDF. A trivial
control document built in the same sandbox exits 0, so the non-zero status is
real and not an artifact of the environment. The log carries nine errors, all
the same one:

```
! Package longtable Error: longtable not in 1-column mode.   (x9)
```

`table_appendix()` in `scripts/make_latex.py` emits `\onecolumn` only when the
class is `ieee`. `sigconf` is also a two-column class, so the ACM build sends
`longtable` into two-column mode, where it refuses to typeset. The tables in
the ACM PDF are therefore not reliable output.

Note on method: shell `grep` over the terminal transcript reported no errors
here. Parsing `main.log` in Python found all nine. Any check of this build that
greps the console output will report success on a broken document.

### A4 Machine-bound build: FAILED, with an UNVERIFIABLE part

FAILED, by direct test. Building with `TEXMFHOME` pointed at an empty
directory fails immediately:

```
$ TEXMFHOME=<empty> pdflatex main
! LaTeX Error: File `xstring.sty' not found.
```

So the build depends on the contents of `~/Library/texmf` and not on the
system TeX installation. Directory timestamps separate what this project
added from what was already there:

* Added 2026-08-08, seventeen packages: binhex, comment, environ, etoolbox,
  fontaxes, hyperxmp, inconsolata, kastrup, metalogo, mweights, ncctools,
  newtx, totpages, txfonts, xkeyval, xstring, plus the generic xkeyval tree.
* Predating this work: libertine (2024-12-01), and enumitem, marvosym,
  preprint, titlesec (2026-07-24).

`libertine` is required by acmart and was already present on this machine. A
clean machine would need it supplied.

UNVERIFIABLE: whether `tlmgr install acmart` obtains this set. I could not test
it. `tlmgr` refuses to operate here for two independent reasons:

```
$ tlmgr install acmart
You don't have permission to change the installation in any way,
specifically, the directory /usr/local/texlive/2025basic/tlpkg/ is not writable.

$ tlmgr info acmart
tlmgr: Local TeX Live (2025) is older than remote repository (2026).
Cross release updates are only supported with update-tlmgr-latest
```

I also could not obtain acmart's declared dependency list offline: the runtime
package archive carries a `tlpobj` with `name` and `category` only, and no
`depend` lines, which live in the full `texlive.tlpdb`. The README's claim that
"on a machine with a full TeX Live, `tlmgr install acmart` is enough" is
therefore untested. It is plausible, and plausible is not verified. One
concrete reason for doubt: `binhex.tex` is required by `newtxmath` and ships in
the `kastrup` package, which is a transitive dependency two levels below
acmart.

### A5 No build artifacts committed: FAILED, with a mitigating measurement

Six are committed, all for the preprint target:

```
paper/preprint/preprint-ieee.aux    paper/preprint/preprint.aux
paper/preprint/preprint-ieee.bbl    paper/preprint/preprint.bbl
paper/preprint/preprint-ieee.out    paper/preprint/preprint.out
```

The stated risk is username disclosure through absolute paths. I searched all
six for `/Users/`, `malek` and `khannoussi` and found **zero** occurrences.
`.aux`, `.bbl` and `.out` record labels, citations and bookmarks rather than
input paths. `.log` files do carry absolute paths, and no `.log`, `.synctex` or
`.fdb_latexmk` is committed anywhere in the repository.

`paper/msr2027/.gitignore` covers the msr2027 artifacts. The preprint directory
has no equivalent, which is why the six exist.

---

## B. Anonymity

All checks below were run against the PDF built in the clone during this
session, not against the committed PDF and not against the source.

### B1 and B2 Text greps: VERIFIED

Counts are occurrences, case-insensitive, over `pdftotext -layout` output and
over the generated `main.tex`.

| term | PDF | .tex |
|---|---:|---:|
| khannoussi | 0 | 0 |
| malek | 0 | 0 |
| tunisia | 0 | 0 |
| gmail | 0 | 0 |
| independent researcher | 0 | 0 |
| orcid | 0 | 0 |
| refactoring-review-friction | 0 | 0 |
| version2 | 0 | 0 |
| khannoussi-malek | 0 | 0 |
| the old paper title | 0 | 0 |

### B3 Metadata and XMP: VERIFIED

`pdfinfo` reports no Author field at all. Title is the submission title, not
the preprint's. Creator and Producer name acmart, hyperref and pdfTeX, which
are tool identifiers and carry no personal information.

`pdfinfo` does not show XMP, so the packet was read separately. It contains:

```
<dc:creator><rdf:li>Anonymous Author(s)</rdf:li></dc:creator>
```

That is the placeholder from the generator's ACM preamble, and it is the
correct value to find.

### B4 Attachments and annotations: VERIFIED

`pypdf` reports no embedded files. Sixty-two annotations are present; every one
is a `/GoTo` internal link, and none carries a `/URI`.

### B5 URLs: VERIFIED, with a compliance gap that is not an anonymity gap

Zero URLs in the extracted text and zero URI actions in the annotations. There
is nothing to deanonymise.

The same measurement shows the paper carries **no anonymous.4open.science link
and no Zenodo DOI**. There is no data availability statement to check, because
there is no data availability statement. That is an open-science compliance
failure rather than an anonymity failure, and it is listed among the blocking
findings.

### B6 The `anonymous` trap: VERIFIED, the trap does not fire

The concern is that acmart's `anonymous` option suppresses `\begin{acks}`, and
that the AI disclosure lives there. It does not apply here: the generator emits
the acknowledgements as an ordinary `\section*{Acknowledgements and
disclosures}` produced from a markdown heading, and never uses the `acks`
environment. `\begin{acks}` does not appear in `main.tex`.

Confirmed by reading the built PDF rather than by inspecting the source. The
section is present and its §8.3 discusses the language model used as a rater.
"claude" and "large language model" each occur once in the PDF text, and
"disclosure" twice.

One caveat the brief did not ask for but which follows from the same reading:
the disclosure that survives is §8.3, which is specifically about an LLM used
as an object of study. Whether the section as printed also carries the broader
statement of generative-AI use in producing the manuscript, which is what ACM
policy requires, is a question about the wording, and I do not consider it
settled by the presence of §8.3 alone. Recorded as an observation, not a
verdict.

### B7 Named individuals: VERIFIED, one item referred to the author

Names appearing in the PDF: Rath (10), Mäder (4), Montgomery (1), Lüders (1),
Maalej (1), Tsantalis (1), ASF (2).

Every one appears as attribution rather than personal thanks. Montgomery,
Lüders and Maalej are named as the depositors of the Public Jira Dataset;
Rath and Mäder as the authors of SEOSS 33. By the brief's own criterion, data
provider acknowledgement is not identifying, so this passes.

Referred to the author rather than decided here: this repository elsewhere
records an advisor relationship with one of the named dataset depositors
(`advisor_brief.md` is addressed to a "Maalej group meeting"). The
acknowledgement itself is ordinary data attribution that many papers using
that dataset would carry, so it is weak evidence at most. It is the author's
call whether it is weak enough.

---

## C. Format compliance

### C1 Documentclass: VERIFIED

```
\documentclass[sigconf,review,anonymous]{acmart}
```

Exactly as required, all three options present.

### C2 `review` active: VERIFIED

Line numbers are present in the rendered output. Detected on 6 of 17 pages by
looking for a column of standalone integers in the extracted text; the pages
where detection fails are the ones dominated by tables and the figure, where
extraction interleaves the number column with body text. The option is
confirmed active both from the class line and from the numbering that appears
in the text.

### C3 `anonymous` active: VERIFIED

No author name appears in the PDF (see B1), and the XMP creator is the
anonymous placeholder (see B3).

### C4 CCS and keywords: VERIFIED

One `CCSXML` block, two `\ccsdesc` entries and one `\keywords` block in
`main.tex`, and the concepts render in the built PDF.

### C5 Page count: FAILED

Measured from the PDF, not estimated.

```
total pages                      17
references heading                NONE FOUND
main text pages                  17     (limit 10)
reference pages                   0     (limit 2)
```

The main text is **seven pages over** a limit the call states as a desk-reject
criterion.

The reference count is 0 because the bibliography is absent from the document
entirely, not because it is short. That is a separate failure, below.

### C6 IEEE build unbroken: VERIFIED

Rebuilt from the clone: exit **0**, **26 pages**, identical to the committed
`preprint-ieee.pdf` page count. The author name is present, which is correct
for the preprint. Forty-two citation markers, so its bibliography resolves.
The short version has not broken the long one.

---

## Blocking findings

**1. The ACM submission has no bibliography at all.** `bibliography()` in
`scripts/make_latex.py` returns `\bibliographystyle{IEEEtran}` for every
target. The ACM build directory contains `ACM-Reference-Format.bst` and not
`IEEEtran.bst`, so bibtex fails:

```
$ bibtex main
I couldn't open style file IEEEtran.bst
I found no style file---while reading file main.aux
```

`main.bbl` is **0 bytes**. The built PDF contains no References heading, and
zero `[n]` citation markers, against 42 in the IEEE build. Sixteen keys are
present and correct in `refs.bib`; nothing is wrong with the bibliography data.
A submission with no reference list is not reviewable.

**2. Eighteen broken cross-references print as `??` in the PDF.** All of them
point at `tab:ticketside`, which is Table 3. `targets.json` excludes Table 3
from the ACM target, and the prose that cites it was not adjusted, so the label
is never defined. Examples from the rendered text:

```
Tables 1 and ?? report ...
every ceilinglive is below it (§ 4.2, Table ??)
Every rate in Tables 1 and ?? is ...
Table ?? actually uses is 1.76pp mean / 11.91pp ...
```

The dangling-reference check added on this branch guards `\ref{sec:...}` only.
It does not guard `\ref{tab:...}`, which is why a build that reports
"Self-check: no leaked markdown, no section-number drift, environments
balanced" still produced eighteen of them. One of the eighteen falls inside the
acknowledgements.

**3. `longtable` is emitted into a two-column class.** Nine errors per run, the
cause of the non-zero exit status in A3. `\onecolumn` is applied for `ieee`
only, and `sigconf` is equally two-column.

**4. No data availability statement and no archived artifact.** Required by the
open-science policy, which names Zenodo and figshare and explicitly rejects
GitHub. Neither a DOI nor an anonymised repository link appears anywhere in the
PDF.

## What was checked and found sound

Worth stating, because a report that lists only failures misrepresents the
state. The anonymisation is genuinely clean: eleven distinct greps across the
PDF text, the generated LaTeX, the document metadata, the XMP packet, the
embedded-file table and all sixty-two link annotations returned nothing
identifying. The AI disclosure survives the `anonymous` option, which is a real
trap that this build avoids by construction rather than by luck. The template
options are exactly right. The IEEE preprint is unaffected by the branch. And
the section-renumbering machinery works: a reference written as "Section 6.5"
in the source correctly prints as "6.2" in a build where three earlier
subsections were cut, which I verified by tracing the source string, the
emitted `\ref{sec:6.5}`, and the rendered output.

## Method notes and limits of this audit

* Everything was built in a scratch clone. The audited tree was not modified.
  The single exception is this file.
* Shell `grep` over LaTeX console output missed all nine `longtable` errors
  that Python found in `main.log`. Anyone verifying this build should parse the
  log, not the terminal.
* The ACM PDF I measured was built by me in the clone. It has the same page
  count, 17, as the committed `paper/msr2027/main.pdf`.
* I did not verify any numeric claim in the manuscript body. That is section D
  of the brief, which was truncated in transmission.
