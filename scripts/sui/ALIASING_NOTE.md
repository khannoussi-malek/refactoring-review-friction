# Author identity aliasing — measured impact on both corpora

**Date:** 2026-07-22 · **Tool:** `scripts/sui/identity.py`

## What prompted this

In start-ui-web the same developer appeared twice with opposite workflow habits —
`ivan@dalmet.fr` (0% via PR) and `ivan-dalmet@users.noreply.github.com` (100% via PR) — because
local CLI commits and GitHub-web commits carry different addresses. That corrupted every
author-level statistic in the exploratory pass.

The obvious next question was whether the Hadoop analysis has the same problem, since
`social_centrality.py` computes `top1_share`, `bus_factor` and `n_authors` per module.

## Result: material in start-ui-web, immaterial in Hadoop

### start-ui-web — the bug is real and large

| | raw | resolved |
|---|---|---|
| distinct author identities | 59 | 50 (9 merged) |
| **top-author share** | **58.1%** | **67.2%** |

A 9-point understatement of concentration. `ivan dalmet` is 1,335 commits, not 1,154.

### Hadoop — the aliasing exists but does not move the measures

Hadoop is worse on raw aliasing: 1,035 emails → 797 identities (238 merged), and **96 emails span
multiple author names, covering 27,307 commits = 35.2% of the corpus**:

```
stack@apache.org     -> "Michael Stack", "stack"                          2,766 commits
szetszwo@apache.org  -> "Tsz Wo Nicholas Sze", "Tsz-Wo Nicholas Sze",
                        "Tsz-wo Sze"                                      1,971 commits
jlowe@apache.org     -> "Jason Darrell Lowe", "Jason Lowe"                1,890 commits
cnauroth@apache.org  -> "Chris Nauroth", "cnauroth"                       1,671 commits
```

**But it does not matter.** Recomputing concentration for all 112 modules with ≥20 commits, by
author *name* (what `social_centrality.py` uses) versus by *email* (which collapses name variants):

| | by NAME | by EMAIL | |
|---|---|---|---|
| mean `top1_share` | 0.1545 | 0.1495 | −3.2% |
| mean `bus_factor` | 8.46 | 8.56 | |
| mean `n_authors` | 87.2 | 91.0 | |

**Paired Wilcoxon on `top1_share`: p=0.3651 — not significant.** 67 of 112 modules differ, but with
no systematic direction and a maximum absolute delta of 0.19.

**Conclusion: `social_centrality.py` does not need to be corrected.** Its concentration measures
are statistically indistinguishable under either grouping.

## The generalisable point

**Aliasing severity scales inversely with contributor count.**

Splitting one person into two identities moves `top1_share` enormously in a 53-author repository
dominated by a single developer, and negligibly in an 800-author repository where the top
contributor holds 3.6% of commits. The same underlying data defect is critical in one corpus and
irrelevant in the other.

So aliasing is not a threat to be assumed present or absent — it must be **measured per corpus**.
`identity.py` reports the before/after concentration shift so that decision is empirical.

## Correction

An earlier claim in the working session — that Hadoop "has the same bug" and that
`social_centrality.py` produced understated concentration — was **wrong**. The raw aliasing is
present and larger than in start-ui-web, but its effect on the derived measures is null. The claim
was made from the alias counts before the impact was measured.

## Usage

```
python3 scripts/sui/identity.py --repo <path> [--out mapping.json]
```

Reports: raw vs resolved identity counts, every merge grouped by rule (GitHub-login merges are
authoritative; name and local-part merges are heuristics, listed separately for inspection), and
the before/after top-author concentration shift.
