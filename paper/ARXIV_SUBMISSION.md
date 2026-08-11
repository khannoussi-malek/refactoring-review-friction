# arXiv submission metadata

Copy-paste into the arXiv submission form. Everything below is taken from the
built `paper/preprint/preprint.pdf`, not from the markdown sources.

Build verified against a stock TeX Live with an empty `TEXMFHOME`, which is the
condition arXiv compiles under: exit 0, no errors, no undefined citations, no
undefined references, 40 pages.

---

## Title

```
Traceability and estimate coverage as corpus-eligibility constraints: a probe of 38 Apache projects
```

## Author

```
Malek Khannoussi
```

Affiliation line for the form: `Independent Researcher, Tunisia`.

## Primary category

```
cs.SE
```

## Secondary category

**None proposed.** The obvious candidate is cs.DL (Digital Libraries), which
covers dataset and repository curation, but the paper's subject is the
eligibility of software projects for a mining study rather than the curation of
a collection, and a cross-list a moderator does not agree with slows the
announcement. cs.SE alone is the honest fit.

## Licence

```
CC BY 4.0
```

One line for the record: the replication package is already deposited under
CC BY 4.0, and matching the paper's licence to the data's avoids a paper that is
more restrictively licensed than the artifacts it points at.

## Comments field

```
40 pages, 3 tables, 1 figure. Replication package: https://doi.org/10.5281/zenodo.21846139
```

---

## Abstract

arXiv's field takes plain text and caps it at 1,920 characters. The abstract in
the paper is **4,378 characters**, so it does not fit. Both versions are below.
Version B is Version A truncated after the third paragraph, with nothing
rewritten and nothing reworded, per the instruction to drop from the end rather
than touch the opening.

Both have had LaTeX artifacts resolved to plain text: `TRR_live` and
`TRR_frozen` for the subscripted forms, `ceiling_live` likewise, `Table 3` and
`Section 3.1.3` for the cross-references, and the en-dash ranges as hyphens.

### Version B, 1,878 characters, fits the form

```
Empirical studies of architectural change read a project's own records and assume the record traces the work. We measure that assumption in three record channels across two ecosystems and find it fails in every one.

We probed 38 Apache projects against a traceability bar of 0.80, pre-registered before any project was cloned and never moved. Twelve passed, and no project outside the Hadoop ecosystem cleared the bar, the best reaching 74.8%, against a median of 63.6% across all 38 and 44.8% across the 26 rejected. The ecosystem label is a hand classification; we tested two measured generational variables in its place and neither separates the corpus as well, so the label is reported as a judgment rather than a finding. The channel the literature publishes is not the channel a ticket-anchored study needs. The commit-side rate, what fraction of commits cite a ticket, runs 82.6-98.3% across the eligible twelve, while the ticket realisation rate, what fraction of tickets ever receive a citing commit, runs 12.0-69.0% under TRR_live. Apache Hive cites a ticket in 97.0% of its 18,213 commits and realises 55.8% of its 29,635 tickets; Table 3 reports the same project at 56.1% under TRR_frozen, which counts a different ticket denominator (Section 3.1.3).

Most of that gap is arithmetic, not discipline. A citing commit adds at most one new distinct ticket, so the ticket-side rate cannot exceed commit-side x commits / tickets. Under the live measurement ceiling_live binds for all twelve eligible projects, ranging 13.7-81.6%, and every project reaches 80-95% of it: the 5.8x spread in the ticket-side rate is a 6.0x spread in the ceiling and only a 1.19x spread in what is left. A tracker accumulates tickets faster than a repository accumulates commits, and below one commit per ticket the two rates are not commensurable.
```

**What Version B loses**, so the choice is informed: the second-ecosystem
result, the 38-project extension and its correlation, the six-mode taxonomy, the
GHS sampling-frame gap, and the explicit no-first-to-measure statement. The
taxonomy is a contribution of the paper, and dropping it from the abstract is
the real cost of fitting the field.

### Version A, 4,378 characters, the paper's own abstract

Over the limit. Kept here so the two can be compared, and because it is what the
PDF says.

```
Empirical studies of architectural change read a project's own records and assume the record traces the work. We measure that assumption in three record channels across two ecosystems and find it fails in every one.

We probed 38 Apache projects against a traceability bar of 0.80, pre-registered before any project was cloned and never moved. Twelve passed, and no project outside the Hadoop ecosystem cleared the bar, the best reaching 74.8%, against a median of 63.6% across all 38 and 44.8% across the 26 rejected. The ecosystem label is a hand classification; we tested two measured generational variables in its place and neither separates the corpus as well, so the label is reported as a judgment rather than a finding. The channel the literature publishes is not the channel a ticket-anchored study needs. The commit-side rate, what fraction of commits cite a ticket, runs 82.6-98.3% across the eligible twelve, while the ticket realisation rate, what fraction of tickets ever receive a citing commit, runs 12.0-69.0% under TRR_live. Apache Hive cites a ticket in 97.0% of its 18,213 commits and realises 55.8% of its 29,635 tickets; Table 3 reports the same project at 56.1% under TRR_frozen, which counts a different ticket denominator (Section 3.1.3).

Most of that gap is arithmetic, not discipline. A citing commit adds at most one new distinct ticket, so the ticket-side rate cannot exceed commit-side x commits / tickets. Under the live measurement ceiling_live binds for all twelve eligible projects, ranging 13.7-81.6%, and every project reaches 80-95% of it: the 5.8x spread in the ticket-side rate is a 6.0x spread in the ceiling and only a 1.19x spread in what is left. A tracker accumulates tickets faster than a repository accumulates commits, and below one commit per ticket the two rates are not commensurable.

Extending the computation to all 38 projects, including the 26 the bar rejected, we find no detectable association between the two rates: rho = -0.010, n = 33, 95% CI [-0.35, +0.34], permutation p = 0.958. That rules out the strong positive relationship a selection bar implicitly assumes, but at 80% power this study detects only |rho| >= 0.47, so a null is not established. On the twelve measured exactly and live the same correlation is +0.518, and we report the disagreement rather than resolving it.

The same invisibility appears in a second ecosystem and two further channels: in a TypeScript corpus, 3 of 96 architectural commits mention refactoring, 7% link an issue, and 69% never pass through code review, and the 31% that do are five times larger and four times more abstraction-heavy than those that do not, so the visible minority is not a random sample of the whole.

We give a taxonomy of six mechanisms by which a project silently fails to support an issue-linked study. Three are disqualifying: the tracker is displaced by GitHub Issues, no source repository exists, the tracker is downstream of the repository. Three are silent: a convention that changed mid-history, a monorepo needing multi-key matching, and a cited key with no project record in the tracker.

None of the six is expressible in any published sampling frame. GHS indexes 735,669 repositories and exposes 35 fields per record, of which only two touch issues, and both are GitHub-issue counts. Four cheap fields would close most of the gap, all computable from a shallow clone and one tracker listing.

We make no first-to-measure claim: per-project linkage rates are published by SEOSS 33 and by Rath et al. An earlier version of this work claimed novelty on that ground; the claim was checked, found false, and withdrawn.
```

---

## Submission tarball

Exactly three files. Everything else is build output and must not be uploaded.

```
preprint.tex
preprint.bbl
figures/eligibility_funnel.png
```

Notes on each:

* `preprint.bbl` is required. arXiv does not run BibTeX, so the compiled
  bibliography has to travel with the source. It carries 16 entries.
* The figure is PNG, which arXiv accepts, and it has no external dependencies.
  `\graphicspath{{../../}{./}}` resolves it from `figures/` inside the
  submission directory.
* Do **not** upload `preprint.aux`, `preprint.log`, `preprint.out`,
  `preprint.pdf`, or any `.synctex.gz`. The log in particular contains absolute
  paths that include the local username.

Verified: no `\write18`, no shell-escape, no `\input` or `\include` reaching
outside the submission directory. Packages used are all stock TeX Live:
amsmath, amssymb, array, babel, booktabs, caption, fontenc, geometry, graphicx,
hyperref, inputenc, lmodern, longtable, microtype, parskip, pdflscape.
