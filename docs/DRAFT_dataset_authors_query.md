# DRAFT — query to the Public Jira Dataset authors

**Status: DRAFT. NOT SENT. Do not send without the author's review.**

Written 2026-08-05. Subject matter: `README.md` §9(a) and `paper/numbers.md` §5,
"Validation note — the project count, and why 1,822 is not usable".

The email is deliberately short, states the reproduction precisely, attributes
nothing, and claims no error. The question is answerable in one sentence if a
normalisation step exists, and worth knowing either way.

**Before sending, check:**

* the correct recipient and the current preferred contact route for Zenodo
  15719919 — the deposit page, the dataset's README, or the associated paper's
  corresponding author. **This was not verified;** no address is filled in below
  for that reason.
* whether the version numbers below match the version actually used. This repo
  parsed the deposit at `scripts/jira_archive.py` (`eee902f`); the exact Zenodo
  version string was not recorded and should be quoted in the email.
* whether an issue tracker or discussion thread on the deposit is the better
  channel than email, since the answer is useful to other users.

---

**To:** _(to be filled in — see above)_

**Subject:** Public Jira Dataset — reproducing the 1,822 project count

---

Dear Dr — ,

I have been using the Public Jira Dataset (Zenodo 15719919) as a base-rate source
for a methods paper on corpus eligibility, and I have not been able to reproduce
the published project count. I suspect I am missing a normalisation step rather
than that anything is wrong, and I would rather ask than guess.

What I did. I streamed the mongodump archive directly rather than restoring it,
and parsed 2,686,282 issues against the ~2.7M published, a difference of 0.5%
which I assume is expected. On that pass:

* counting distinct project **keys** in each issue's final state gives **1,276**
  projects;
* implementing the count as your notebook defines it —
  `set.union(unique_projects_final, unique_projects_history)` over project
  **names** — gives **2,506**;
* the README reports **1,822**.

The one measurement I have that bears on the gap: across those 2,686,282 issues,
**326 project ids carry more than one distinct name, and 0 project keys do**. For
example `Jira/12910` appears as *SourceTree*, *SourceTree For Mac* and
*Sourcetree For Mac*, the last differing only in capitalisation; `Mojang/10400`
appears as *Minecraft* and *Minecraft: Java Edition*. Removing the surplus names
brings the name-based union down to roughly 2,180, so renaming explains part of
the overshoot from 2,506 but not the remainder down to 1,822.

My question is simply: **is there a normalisation or deduplication step between
the two figures that I have not reproduced?** If the published 1,822 comes from a
different pass, a different snapshot, or a filter on the project set — archived
projects excluded, or a minimum issue count — that would resolve it, and I would
cite whichever definition you consider canonical.

For what it is worth from a user's side, the key-based count has been the more
useful of the two for my purpose, because keys turned out to be stable
identifiers within a snapshot while names are not.

The dataset has been genuinely useful — it is the only source I found that lets a
single-project observation be checked against a base rate across sixteen
organisations, and streaming the archive rather than restoring it made it usable
on a laptop. Thank you for depositing it.

With best wishes,

Malek Khannoussi
Independent researcher
khannoussimalek@gmail.com
https://github.com/khannoussi-malek/refactoring-review-friction

---

## Notes for the author, not part of the email

* Every number quoted is in `paper/numbers.md` §5 with its provenance:
  2,686,282 parsed and 1,276/2,506 from `scripts/jira_estimates.py` (`eee902f`),
  the 326-ids-multiple-names measurement at `0f116aa`, and the id↔key 1:1 result
  at `5179907`.
* The "roughly 2,180" figure is stated in the repository as *consistent with
  rename inflation, unverified*. It is phrased as an approximation here for that
  reason. Do not tighten it before sending.
* If a reply establishes the canonical definition, the correction is **additive**:
  add a dated note to `paper/numbers.md` §5 rather than editing the existing
  three-figure table, and update `README.md` §9(a) to record that the question
  was answered and by whom.
