# arXiv preprint — prepared, not submitted

**Nothing has been submitted, uploaded or announced.** This file lists what is
ready and every step that requires the author.

Prepared 2026-08-05.

---

## What is ready

| item | where | state |
|---|---|---|
| LaTeX source | `paper/preprint/preprint.tex` | generated from the Markdown sections by `scripts/make_latex.py` |
| Compiled PDF | `paper/preprint/preprint.pdf` | **35 pages, compiles clean under pdfTeX — 0 errors, 0 undefined references** |
| arXiv abstract | `paper/preprint/arxiv_abstract.txt` | **1,850 characters, plain ASCII**, inside arXiv's ~1,920-character norm |
| Tables 1, 2, 3 | in the .tex | all three, with the front-matter table map |
| Acknowledgements and AI disclosure | `paper/manuscript/acknowledgements.md`, §8 | drafted; **needs the author's verification — see step 3** |

Regenerate the whole thing with:

```
python3 scripts/make_latex.py --out paper/preprint/preprint.tex
cd paper/preprint && pdflatex preprint.tex && pdflatex preprint.tex
```

**The .tex is generated. Do not edit it by hand** — edit the Markdown section and
re-run, or the next regeneration silently discards the edit.

---

## 1. Primary category — recommendation, not a decision

**Recommended primary: `cs.SE` (Software Engineering).** Reasoning:

* Every work the paper argues with — SEOSS 33, GHS, Rath et al., Bachmann et al.,
  Bird et al., ReLink — is in `cs.SE` or in venues whose preprints go there.
* The contribution is a measurement and a taxonomy about *how software
  repositories are mined*, which is the centre of `cs.SE`'s scope and of the MSR
  community the paper is written for.
* Posting elsewhere would put it in front of the wrong readers. The paper's
  actionable content — the four fields a sampling frame should expose — is
  addressed to people who build MSR datasets.

**On cross-listing: my advice is not to.** The candidates and why each is weak:

| candidate | case for | case against |
|---|---|---|
| `cs.DL` (Digital Libraries) | the sampling-frame and metadata argument | `cs.DL` is about document and library systems, not repository mining; the fit is superficial |
| `stat.AP` | the paper now carries CIs, a permutation test and a power statement | the statistics are ordinary and are not the contribution; cross-listing would oversell them |
| `cs.DB` | the frozen tracker corpus | the paper is not about data management |

A cross-list that does not fit annoys moderators and dilutes the listing. **The
author decides**; `cs.SE` alone is my recommendation.

---

## 2. Licence — the choice that cannot be undone, and what it touches

arXiv asks for a licence at first submission. **It can be changed on a later
version but never removed from an already-announced version**, so the first
choice is effectively permanent for that version.

| option | what a reader may do | consequence here |
|---|---|---|
| **arXiv perpetual non-exclusive licence** (the minimal default) | read and redistribute via arXiv; no reuse rights beyond fair dealing | most conservative; keeps every downstream option open, including venues with restrictive policies. **No conflict with anything.** |
| **CC BY 4.0** | reuse, adapt, redistribute commercially, with attribution | **consistent with this repository**, whose `paper/` directory is already CC BY 4.0, and with the Public Jira Dataset it derives from. Maximum reach. Cannot be narrowed later for that version. |
| **CC BY-SA 4.0** | as above, but derivatives must be share-alike | imposes a term the repository does not use; creates a mismatch between the preprint and `LICENSE` |
| **CC BY-NC-SA 4.0** | non-commercial only | **incompatible in spirit with the CC BY 4.0 Public Jira Dataset**, which permits commercial reuse; would make the preprint more restrictive than its inputs |
| **CC0** | public domain dedication | gives up attribution, which is the one thing the repository's own licence asks for |

**My recommendation, for the author to accept or reject:** **CC BY 4.0**, because
the repository already licenses `paper/` that way and a preprint under a *narrower*
licence than the artifacts it describes is an odd signal. The conservative
alternative — the arXiv default licence — is the right choice if there is any
doubt about the target venue's policy.

### 2a. What this interacts with

**The `LICENSE` contradiction the brief refers to has been resolved.** The brief
describes it as unresolved; that was true at the time of the audit and was fixed
in the preceding revision (`paper/REVISION_LOG.md`, item 0b). `LICENSE` now has
four headings with each path in exactly one, and heading 3 states the split for
`deposit/jira-caches-v1.tar.gz`: **the compilation, arrangement and manifest are
CC BY 4.0; the underlying ASF issue content is not, and no licence is claimed over
it.** `deposit/zenodo.json` says the same thing. **Verify this yourself before
relying on it** — it is a licence, and it is the one thing in this repository a
mistake in cannot be corrected after the Zenodo deposit is minted.

**The Zenodo interaction is real and one-directional.** A Zenodo record's licence
field **cannot be changed after minting**. So:

1. settle the archive's licence (done, but confirm it);
2. mint the Zenodo DOI;
3. then post to arXiv, citing the DOI.

Doing it in the other order means the preprint cites a DOI that does not exist
yet, or that the DOI's licence is chosen under time pressure.

---

## 3. Steps that require the author

1. **ORCID.** Still commented out in `CITATION.cff` line 24 and absent from the
   preprint. arXiv links submissions to an ORCID and it is the thing that makes a
   preprint findable under a name. Register at https://orcid.org, then fill it in
   `CITATION.cff`, `deposit/zenodo.json` and the arXiv author record.

2. **An arXiv account with endorsement.** A first-time `cs.SE` submitter needs
   endorsement from an existing arXiv author in that category unless the account
   qualifies automatically (typically via an academic email domain). **Check this
   early** — it is the step most likely to delay a submission by days.

3. **Verify the AI-use disclosure against your own record.** §8.2 was drafted
   from `paper/REVISION_LOG.md` and the git history, which cover the assisted
   sessions. **Only you know the full history**, including the earlier sessions of
   19–25 July 2026 that produced the original corpus and results. Check
   specifically:
   * whether the tool list is complete and correctly named;
   * whether "drafted with assistance" accurately describes the earlier work as
     well as the later;
   * that the accountability sentence says what you want it to say.
   The disclosure is deliberately specific rather than boilerplate, and it should
   be right rather than generous in either direction.

4. **Decide the split first (GATE 2).** The preprint is 35 pages and ~14,660
   words. arXiv has no page limit, so it *can* go up as one document — but if the
   work is going to be split into two papers, posting the combined version first
   creates a citation record that the split then has to work around. **This is a
   reason to settle `paper/SPLIT_DECISION.md` before posting, not after.**

5. **Apply the Flink result.** `paper/FLINK_TRUNCATION.md` §7 lists four places
   that still say the truncation check has not been run. It has, and it succeeded
   to 0.004pp. **The preprint currently carries the outdated statement.** Either
   apply those edits before posting or accept that v1 understates a result.

6. **Bibliography.** Citations in the manuscript are prose ("Rath & Mäder 2019,
   SEOSS 33"), not `\cite` commands, and the .tex has no `.bib`. This is fine for
   a preprint and **not** fine for a venue submission. Building the `.bib` is a
   known manual step; every reference is already verified with authors, venue,
   year and identifier in `audit/CITATIONS.md` and `paper/PRIOR_WORK.md` §5.

7. **Figures.** `figures/eligibility_funnel.png` is referenced in the
   front-matter table map but **not embedded** — the preprint points to the
   replication package. Embed it if v1 should be self-contained.

8. **Check the target venue's preprint policy** before choosing a licence, if a
   specific venue is intended. MSR is ACM/IEEE; policies change and this should be
   read at submission time rather than assumed.

---

## 4. Known limits of the generated LaTeX

Stated so nobody discovers them at submission time.

* **Cross-references are literal text.** The sections write "§4.3" as prose and
  that is what appears. There are no `\ref` links between sections. Tables *are*
  properly labelled and referenced.
* **Section numbering is LaTeX's, and the prose numbering is the Markdown's.**
  They agree because the section files are numbered in the same order, but nothing
  enforces it. If a section is reordered, the prose cross-references will drift
  silently. **Check this after any split.**
* **Table 3 is set in landscape** because it is eleven columns. It reads
  correctly on screen and in print; check it looks acceptable to you.
* **No `.bib`, no `\cite`** — see step 6.
* The converter emits `article` class, not `acmart` or `IEEEtran`. That is
  deliberate for a preprint and wrong for a venue submission.
