# MSR 2027 submission

Ten pages of main text plus two of references, ACM `sigconf`, double-anonymous.
The call is https://2027.msrconf.org/track/msr-2027-technical-papers and it is
the source of truth; re-read it before relying on any date below.

    Abstract        Mon 20 Oct 2026 AoE
    Paper           Thu 23 Oct 2026 AoE
    Early reject    Thu  3 Dec 2026
    Author response Fri  4 - Tue 8 Dec 2026
    Notification    Fri  8 Jan 2027
    Camera ready    Tue 26 Jan 2027

## Build

    python3 scripts/make_latex.py --out paper/msr2027/main.tex --template acm --selfcheck
    cd paper/msr2027 && pdflatex main && bibtex main && pdflatex main && pdflatex main

`main.tex` is generated. Editing it by hand is pointless: the next build
overwrites it. Edit `paper/manuscript/*.md` and rebuild.

## What is in this version, and what is not

`paper/manuscript/targets.json` decides. Both the preprint and this submission
read the same section files, and the manifest lists only what this target leaves
out, so no prose exists twice and no number can drift between the two. That
property is checked: `scripts/check_provenance.py` reports `TARGET_DRIFT` and
fails on any number the short paper carries and the preprint does not.

## acmart is not vendored

The class and its dependencies are fetched at build time and are gitignored. On
a machine with a full TeX Live, `tlmgr install acmart` is enough. This one runs
BasicTeX without write access to the system tree, so the class was generated
from the CTAN source into `paper/msr2027/` and its dependencies were unpacked
into `~/Library/texmf`: xstring, totpages, environ, hyperxmp, ncctools,
comment, libertine, newtx, fontaxes, mweights, txfonts, inconsolata, xkeyval,
etoolbox, kastrup (for `binhex.tex`, which newtxmath loads). The Type1 maps
need `updmap-user --enable Map=zi4.map` or pdflatex aborts with a font-expansion
error.

## Before submitting

Everything in the spec's §9. The two that are not yet satisfiable here are the
Zenodo DOI for the data availability statement and the ORCID.
