# A within-project temporal observation, carried forward and not built on

**Status: an observation, not a finding.** It is recorded here so the split does
not lose it. It is **not** in the abstract, not in the contributions list, and no
claim in the paper rests on it. Nothing should be built on it without a study
designed for it.

Recorded 2026-08-05. Numbers from `scripts/flink_truncation.py` →
`paper/flink_truncation.json` and `scripts/springbatch_recency.py` →
`paper/springbatch_recency.json`. Graduation dates from
`scripts/era_separation.py`.

---

## 1. What was observed

Flink's Jira-citation rate, by year, over the 38,219 commits reachable from its
pinned sha:

| year | commits | citing | rate |
|---|---:|---:|---:|
| 2010 | 37 | 0 | **0.0%** |
| 2011 | 1,880 | 0 | **0.0%** |
| 2012 | 1,518 | 0 | **0.0%** |
| 2013 | 509 | 0 | **0.0%** |
| **2014** | 2,084 | 404 | **19.4%** |
| **2015** | 2,146 | 1,416 | **66.0%** |
| 2016–2026 | 27,845 | 21,420 | **70–88%** every year |

Flink **graduated from the Apache Incubator in December 2014**
(https://incubator.apache.org/projects/, read 2026-08-05).

The convention appears in the same year as graduation, from a standing start of
four years at exactly zero, and reaches its steady state within two.

## 2. Why this is not contradicted by the failed corpus-level test

§4.1 reports that project generation **fails** to separate the eligible twelve
from the twenty-six: repository start year gives AUC 0.611 (p = 0.279) and
Incubator graduation date AUC 0.289 (p = 0.098), both worse than the hand-drawn
ecosystem label's 0.868 accuracy. On that basis the paper declines to replace the
judgment with a measurement.

**That test and this observation are different units of analysis, and the first
does not rule out the second.**

* The corpus-level test asks: *across projects*, does the year a project
  graduated predict whether its lifetime citation rate clears 0.80? It compares
  38 projects at one point each.
* This observation is about *one project across time*: does a single project's
  rate change at its own graduation? It compares one project against itself.

A between-project null is compatible with a within-project effect, and vice
versa. Projects differ in a great many ways that swamp a common temporal shift
when compared cross-sectionally; the same shift can be sharp inside a project
where those differences are held constant. Ecological inference runs in neither
direction without assumptions this study has not made.

**Neither result licenses the other.** The corpus-level null stands as reported.
This observation stands as an observation.

## 3. What it is not

**n = 1.** One project, one graduation, one coincidence of dates. There is no
control, no comparison against projects that did not graduate, no test, and no
p-value — because computing one on a single series chosen *after* seeing that it
looked interesting would be a post-hoc test presented as a prospective one.

**Consistent with, not evidence for.** The pattern is what a graduation effect
would look like if there were one. It is also what would be produced by: a
release cycle that happened to coincide; a single committer changing the project's
commit-message template; a CI or hook change enforcing keys; the project's
migration to a new repository host; or the arrival of contributors who brought
the convention from another ASF project. **None of these was checked**, and at
n = 1 none can be excluded.

**Not a claim about causation, and not a claim about generality.**

## 4. The second instance, which points the other way

`scripts/springbatch_recency.py` records the mirror image in spring-batch:
`BATCH-` in **45.6%** of 7,035 commits overall, **0 of the most recent 1,000**,
and **0.0% in every year from 2020**, the last year of use being **2019**.

So within-project change is not one-directional: one project adopts the
convention and one abandons it. **The pair supports the taxonomy's mode 4 — "a
single lifetime rate averages two regimes" — which the paper does claim** (§5,
and it is the sole basis on which either series appears in the manuscript). It
does **not** support a graduation story, since spring-batch is not an ASF project
and never graduated anything.

## 5. What would be needed to make this a finding

Stated so the gap is explicit rather than implied:

1. **Every ASF project with a known graduation date**, not one. The Incubator
   publishes them; §4.1 already collected 24 of the 38.
2. **A per-project change-point estimate** on the citation series, computed
   without reference to the graduation date, and then compared against it.
3. **A control group** — ASF projects that entered as subprojects and never
   graduated (Hive, HBase, ZooKeeper, Ozone here), plus non-ASF projects.
4. **Pre-registration**, because the hypothesis is now known to the person who
   would test it. This observation is exactly the kind that generates a
   post-hoc-looking result if tested on the data that produced it.

Points 1 and 2 are a day's work on data already on disk. Point 4 is the reason
this file says "carried forward" rather than "next".

## 6. Where it appears

* `paper/numbers.md` §10i — the provenance rows.
* `paper/FLINK_TRUNCATION.md` §4 — the by-year table, in its original context.
* **Not** in the abstract, §1's contributions, or any claim.

If the paper is split, this file travels with whichever part carries the
taxonomy, because mode 4 is the only claim either series supports.
