# Audit — Priority 2: hard-rule compliance

Verified from git and from the artifacts, not from the prior agent's report.
Pre-work state is `d0bc98e`; the work is `3c0c24d..e23b902`, six commits.

**Result: all eight hard rules were kept. One placement deviation and one
scope-of-negative-result question are reported as sub-findings, neither of them a
violation.**

---

## Rule 1 — never state a number you did not compute

Assessed in `audit/NUMBERS.md`. Summary: no fabricated number found; three
numbers pass the repository's own provenance gate spuriously; one manuscript
sentence states 100% where the artifact says 99.7%.

**Verdict: SUBSTANTIALLY KEPT, with the exceptions in `audit/NUMBERS.md` §5.**

---

## Rule 2 — never soften, remove or bury a negative result

I diffed `README.md` against its pre-work state in full.

```
git diff d0bc98e..HEAD -- README.md
```

The diff is **purely additive**: three hunks, all insertions, no deletions of
substantive text except the replacement of four bullet lines in §7 by an expanded
version of the same four bullets.

| element the brief named | still present? | still prominent? |
|---|---|---|
| §4 "What did not hold" table (six failed hypotheses, named causes) | yes — **untouched** | yes, §4, unchanged position |
| Retracted Cox result (HR 0.69 p=0.003 → HR 1.10 p=0.51) | yes — **untouched** | yes, first row of §4 |
| The tier rule failing 0 of 3, and the note that lowering 0.40 would have rescued HBase and Phoenix | yes — **untouched** | yes |
| §8 "What this needs that one person cannot supply" | yes | yes — and **strengthened**, not softened |
| §2 headline (12.0%–69.0%, none above 69%) | yes — untouched | yes |
| §5 six failure modes | yes — untouched | yes |
| Self-corrected estimate aggregation error | yes — untouched | yes |

The §8 change is the only edit to a negative-result section, and it makes the
limitation **worse**, not better: it adds that κ is not computable *even if a
second rater appears now*, and that no pairing on the flagged bucket reaches
κ = 0.491. That is the correct direction.

**Verdict: KEPT.**

**Sub-finding (not a violation), worth the author's judgment.** §7 formerly
listed "Registered report proposing the SATD-interval design" as a forthcoming
deliverable; it now reads "**Superseded 2026-07-26** before it was started". That
is factually supported by `PROJECT_STATE.md`'s 07-26 row, which predates this
work — so it is a status update, not a retirement of a negative result. But a
reader diffing the README will see a promised deliverable disappear, and the
justification lives in another file.

---

## Rule 3 — never edit `predictions/PREDICTIONS.md`

```
git log --follow --format='%h %ad %s' --date=short -- predictions/PREDICTIONS.md
ca076a9 2026-07-25 feat: pre-register the held-out predictions -- before any outcome data
```

**Exactly one commit in the file's entire history.** It has never been modified,
by this work or any other. The pre-registration evidence is intact.

**Verdict: KEPT — CONFIRMED.**

---

## Rule 4 — never rewrite the dated working logs

| file | last modified | in scope of this work? |
|---|---|---|
| `SLICE_LOG.md` | `b8d1476`, 2026-07-19 | no |
| `worksheet.md` | `de657c3`, 2026-07-19 | no |
| `advisor_brief.md` | `cc5dadb`, 2026-07-22 | no |

None appears in `git diff --name-status d0bc98e..HEAD`. Not appended to, not
rewritten, not touched.

**Verdict: KEPT — CONFIRMED.**

---

## Rule 5 — never re-fetch Jira

Two independent checks.

**(a) Nothing in git.** No `.jira_*` path is tracked (`git ls-files | grep
'^\.jira'` → 0), and no cache file appears in the change set.

**(b) The frozen archive is byte-identical to its manifest.** I re-verified
**every one of the 2,491 files** in `deposit/MANIFEST-v1.json` against its
recorded SHA-256, on disk:

```
manifest files: 2491   verified-identical: 2491   missing: 0   MISMATCH: 0
```

and the archive itself:

```
shasum -a 256 deposit/jira-caches-v1.tar.gz
fcb705b664c248d0c4d32f69b854e10fd8b11c907a19c40333322e06d31b9a95   <- matches MANIFEST-v1.md
```

The extension work took its denominators from `estimates_by_org.json` (the
already-parsed frozen public corpus) instead of the Jira API. `scripts/ticket_side_38.py`
sets `GIT_NO_LAZY_FETCH=1` and `GIT_TERMINAL_PROMPT=0` and makes no HTTP call.

**Verdict: KEPT — CONFIRMED, at file-level granularity.**

---

## Rule 6 — never change pinned versions in `requirements.txt`

```
git diff d0bc98e..HEAD -- requirements.txt
(empty)
```

**Verdict: KEPT — CONFIRMED.**

---

## Rule 7 — corrections are additive

The named test case is the withdrawal of "the median sits near 35%".

* The original sentence **still stands verbatim** at
  `replication/CORPUS_FEASIBILITY.md` lines 54–56:
  *"No general-purpose Java project clears the bar — the best, James, reaches
  74.8%, and the median sits near 35%."*
* The correction is **appended at the end of the file**, dated
  `## Correction (2026-08-05)`, with the recomputed medians and an explicit
  "unsourced and withdrawn".
* The git diff for that file is **insert-only** — zero deletions.

**Verdict: KEPT — CONFIRMED.**

**Sub-finding — placement deviates from the file's own convention.** The
correction sits ~110 lines below the sentence it corrects, with no inline marker
at the point of the error. The same file's earlier corrections (2026-07-25, on
the 12-of-34 denominator and on ShardingSphere) are placed *immediately beneath
the affected paragraph* in italics. A reader of the "Result — 12 of 38 projects
pass" section will read the withdrawn 35% and have no signal that it is
withdrawn. This is a real exposure — the figure is now known-false and is the
first thing a reader of that section encounters — but it is a placement problem,
not a rule violation.

Note also: `paper/numbers.md` §9g still carries "median candidate near **35%**"
in its own table row. §10b withdraws it, but §9g is not annotated. Same class of
exposure.

---

## Rule 8 — report uncertainty as uncertainty

The prior agent's report opened five uncertainties unprompted, including the
Jira-rule tension, the Kylin double value, the family classification, the
unadjudicated entity-tracking residual and the rater contamination. Four of the
five I independently confirm as real (see `audit/JUDGMENTS.md`); the family one
was raised but **analysed on the wrong project** (`audit/JUDGMENTS.md` §1).

Two material uncertainties were **not** disclosed and I found them independently:
the validation/application range disjunction and the understated end-to-end
estimator error (`audit/NUMBERS.md` §2).

**Verdict: SUBSTANTIALLY KEPT; two undisclosed uncertainties reported.**

---

## Rule additional — no external publication

* `deposit/` gained only `DEPOSIT_CHECKLIST.md` and `zenodo.json`. The tarball and
  both manifests are unchanged since 2026-07-25.
* No Zenodo DOI appears anywhere as minted; the only DOI in `deposit/` is the
  *cited* Public Jira Dataset DOI.
* The one attempted external write — adding a GitHub repository topic — did not
  land. I confirmed by reading the live repository: topics are still
  `empirical-software-engineering`, `mining-software-repositories`, `refactoring`,
  `traceability`. `reproducibility` is absent, exactly as the prior report stated.

**Verdict: KEPT — CONFIRMED.**
