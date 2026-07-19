# F2 codebook — first-pass labeling & the operational decision

**Rater A: automated (Claude), applying `codebook.md`.** These are a *bootstrap* set of labels — a
real study wants a second independent human rater and Cohen's κ. But even one careful pass answers
the question that was blocking a single F2 number: *how good is the keyword heuristic?*

## Labels on the 40-comment sample (S = structural / I = incidental / C = style-correctness)

| Bucket | S | I | C |
|---|---|---|---|
| Comments the keyword filter **flagged** (n=20) | **5** | 5 | 10 |
| Comments the keyword filter **missed** (n=20) | **1** | 1 | 18 |

## What it reveals

- **Keyword precision for "structural" ≈ 25%** (5 of 20 flagged comments are real structural
  arguments). The rest are approvals that happen to say *"nice refactor"*, or *"split into subtasks"*
  (work-planning, not code shape), or *"12 too big"* (thread count). **The naive keyword rule
  over-counts structural review ~4×.**
- **Miss rate ≈ 5%** (1 of 20 unflagged comments was actually structural — HADOOP-18830's
  *"it just confuses everything above it"*, an architectural rationale with no keyword). Noisy at
  n=20, but small.

## Decision: operational F2

Because the "any keyword ≥1" rule is only 25% precise, **F2 = the strong signal (≥3 structural
keyword mentions in an episode's review discussion)** is the working operational definition:

> **F2 (operational) = 106 / 345 episodes = 31%.**

Rationale: an episode with ≥3 keyword hits has ~1−0.75³ ≈ 58% chance of containing a genuinely
structural comment, versus ~25% for a single hit — so the strong threshold is the defensible proxy
until full episode-level labeling is done. The honest bound on the true structural-review rate is
**~25–35%**, not the naive 62%.

## What would finish this properly
Label all ~1,810 substantive comments (or the ~323 episode tickets) with two raters, compute κ, and
replace the heuristic in `pr_review_signal.py` with the labeled classifier. Until then, **31% is the
number to quote**, with 62% flagged as the keyword-inflated upper bound.
