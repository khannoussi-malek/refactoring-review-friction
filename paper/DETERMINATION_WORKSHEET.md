# Determination worksheet — the Bachmann/Bird question

**This sheet is blank on purpose. Every answer is yours.**

The question it serves is the one held open at `related.md` §2.4 and §2.2 item 5:
whether the quantity defined in `method.md` §3.1 is the same quantity Bachmann et
al. (FSE'10) and Bird et al. (ESEC/FSE'09) measured, or a distinct one. Nothing in
this repository has answered it, and nothing here should be read as leaning either
way.

**How to use it.** Read the two papers. `paper/PRIOR_ART_EVIDENCE.md` has the
verbatim passages laid out side by side with page locations, so you can go
straight to the relevant sections rather than reading cover to cover. Mark each
line **Y / N / ?** as you go. Note the page you settled it from — the notes column
is what makes the determination defensible later.

A **?** is a real answer. A question you cannot settle from the text is worth
more than a guess, and §2.4 can say so.

---

## A. Bachmann et al., FSE'10 — *The Missing Links: Bugs and Bug-fix Commits*

| # | question | Y / N / ? | settled from (page / §) | note |
|---:|---|:---:|---|---|
| A1 | Is the denominator restricted to **bugs** (as opposed to all issue types)? | | | |
| A2 | Is the denominator restricted to **fixed** bugs specifically? | | | |
| A3 | Is the denominator restricted by **resolution status** in any other way? | | | |
| A4 | Are non-bug issue types (improvements, features, tasks, sub-tasks) explicitly **excluded**? | | | |
| A5 | Are non-bug issue types explicitly **included**? | | | |
| A6 | Is the rate computed **per commit** (what fraction of commits link)? | | | |
| A7 | Is the rate computed **per bug** (what fraction of bugs are linked)? | | | |
| A8 | Are **both directions** computed? | | | |
| A9 | Is the rate computed **across multiple projects for comparison**? | | | |
| A10 | Is the rate computed **within one project to characterise it**? | | | |
| A11 | Does the paper use linkage rate as a **corpus selection criterion**? | | | |
| A12 | Does the paper **recommend** that others select or exclude projects on linkage rate? | | | |
| A13 | Does the paper **name** the quantity as a defined metric (a term of art, not a description)? | | | |
| A14 | Does the paper **define** the quantity symbolically or formally? | | | |
| A15 | Does the paper distinguish a **commit-side** rate from a **ticket-side** rate as two quantities? | | | |
| A16 | Does the paper have any counterpart to a **taxonomy of failure modes** by which a project cannot support linkage-based study? | | | |
| A17 | Is the measurement **manual**, automated, or both? | | | |
| A18 | Is the stated purpose **bias in defect prediction / data quality**, rather than corpus eligibility? | | | |

## B. Bird et al., ESEC/FSE'09 — *Fair and Balanced? Bias in Bug-Fix Datasets*

| # | question | Y / N / ? | settled from (page / §) | note |
|---:|---|:---:|---|---|
| B1 | Is the denominator restricted to **bugs**? | | | |
| B2 | Is the denominator restricted to **fixed** bugs specifically? | | | |
| B3 | Is the denominator restricted by **resolution status** in any other way? | | | |
| B4 | Are non-bug issue types explicitly **excluded**? | | | |
| B5 | Are non-bug issue types explicitly **included**? | | | |
| B6 | Is the rate computed **per commit**? | | | |
| B7 | Is the rate computed **per bug**? | | | |
| B8 | Are **both directions** computed? | | | |
| B9 | Is the rate computed **across multiple projects for comparison**? | | | |
| B10 | Is the rate computed **within one project to characterise it**? | | | |
| B11 | Does the paper use linkage rate as a **corpus selection criterion**? | | | |
| B12 | Does the paper **recommend** that others select or exclude projects on linkage rate? | | | |
| B13 | Does the paper **name** the quantity as a defined metric? | | | |
| B14 | Does the paper **define** the quantity symbolically or formally? | | | |
| B15 | Does the paper distinguish a **commit-side** rate from a **ticket-side** rate as two quantities? | | | |
| B16 | Does the paper have any counterpart to a **taxonomy of failure modes**? | | | |
| B17 | Is the measurement **manual**, automated, or both? | | | |
| B18 | Is the stated purpose **bias in defect prediction / data quality**, rather than corpus eligibility? | | | |

## C. This study's quantity — `method.md` §3.1, Definition 2

Answer these from your own definition, not from the papers.

| # | question | Y / N / ? | note |
|---:|---|:---:|---|
| C1 | Is its denominator restricted to **bugs**? | | |
| C2 | Is its denominator restricted to **fixed** bugs? | | |
| C3 | Is it conditioned on any **resolution status**? | | |
| C4 | Does it admit **all issue types**, including sub-tasks? | | |
| C5 | Is it computed **per bug / per ticket** rather than per commit? | | |
| C6 | Is a **commit-side** rate defined separately as a distinct quantity? | | |
| C7 | Is it computed **across projects for comparison**? | | |
| C8 | Is it used as a **corpus selection criterion**? | | |
| C9 | Is it given a **name** and a formal definition? | | |
| C10 | Is the **time-bounding of the denominator** specified? | | |

## D. The comparison — answer only after A, B and C

| # | question | Y / N / ? | note |
|---:|---|:---:|---|
| D1 | Do the denominators differ in a way that changes what the number means? | | |
| D2 | Does either paper compute the same directional rate over the same population? | | |
| D3 | Does the ReLink attribution (§ "the 54% figure" in `PRIOR_ART_EVIDENCE.md`) change your reading of what the prior work reported? | | |
| D4 | Is the **naming** claim in §3.1 defensible — that the quantity had been reported without a name? | | |
| D5 | Is the **corpus-eligibility framing** distinct from what either paper does? | | |
| D6 | Should §2.4 cite Bachmann as a **direct ancestor**, a **prior measurement of the same quantity**, or something else? | | |

---

## The decision

Circle one, or write your own:

* **Branch A — TRR is distinct.** Keep the definition, cite Bachmann as the direct
  ancestor, state the distinction in one sentence in §2 and one in §3.1. Do not
  oversell the gap.
* **Branch B — TRR is not distinct.** Withdraw the naming claim the way §2.1's
  first-to-measure claim was withdrawn: dated correction, original sentence left
  standing. Reframe the contribution around eligibility and the taxonomy.
* **Branch C — something else**, written out below.

```
Determination:



Reasoning (two or three sentences is enough; it goes into the paper):



Date:                        Settled from:
```

**When you have filled this in**, the next steps are mechanical and are listed in
`paper/REVISION_LOG.md` under GATE: write `paper/BACHMANN_DETERMINATION.md`, then
the `[DETERMINATION PENDING]` markers in `related.md` §2.4, `related.md` §2.2
item 5 and the `UNDETERMINED` note in `CITATION.cff` can all be resolved in one
pass.
