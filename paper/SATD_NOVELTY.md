# Task 15 — latency vs co-occurrence: is the interval occupied?

Findings only. Verified 2026-07-25.

## The one question

> Has anyone measured the INTERVAL from SATD introduction to a later
> architectural refactoring, or only same-commit co-occurrence?

**Answer: nobody has measured SATD-comment → later architectural-refactoring
latency. The SATD literature is same-commit throughout. But the latency framing
itself is NOT free — an architectural-debt time-to-fix literature exists and is
active as of May 2026. It anchors on Jira issues and files, not on SATD comments
and not on detected refactorings.**

The gap is real but narrower than the design assumed, and one competitor is
three months old.

---

## 1. Iammarino et al. 2021, *J. Syst. Softw.* — strictly same-commit

*An Empirical Study on the Co-Occurrence Between Refactoring Actions and
Self-Admitted Technical Debt Removal.* Iammarino, Zampetti, Aversano, Di Penta.

**Operationalisation — read from the paper text:**

- **Unit: the commit.** RQ1 is "to what extent refactoring actions happen *in the
  same commits* in which SATD is removed, and whether this happens with a greater
  proportion than in other commits."
- **Second, narrower unit: the file.** For the manual analysis (RQ2) they
  "considered instances of all commits where there was at least one refactoring
  action **in the same file** where SATD occurred, therefore considering a total
  of **201 cases**".
- **No entity-level linkage.** Nothing ties a SATD comment to the specific class
  or method that was refactored.
- **No time window of any kind.** All four RQs are proportional/co-occurrence:

  > RQ1 to what extent do refactoring actions co-occur with SATD removals?
  > RQ2 to what extent do refactoring actions actually contribute to SATD removal?
  > RQ3 what types of refactoring actions co-occur more with SATD removals?
  > RQ4 compared to quality metrics, how does SATD removal explain the presence
  > of a refactoring action?

  Keyword scan of the full text: **"survival" 0 hits, "lifetime" 0 hits,
  "months" 0 hits, "days" 1 hit, "how long" 1 hit.** There is no temporal
  analysis.
- **Tool:** RMiner (RefactoringMiner), Tsantalis et al. 2018.
- **Corpus:** four projects — Camel, Gerrit, Log4j, Tomcat. SATD from the
  da S. Maldonado et al. 2017 dataset.

**Verdict: pure co-occurrence. The interval is untouched.**

## 2. Esfandiari 2023 (ICCKE) — the nearest neighbour, also same-commit

*An Exploratory Study of the Relationship between SATD and Other Software
Development Activities.* Shima Esfandiari, ICCKE 2023.

- **Corpus:** SmartSHARK, **77 Java projects**, 35 refactoring type groups.
- **SATD signal:** TODO/FIXME/XXX added or removed in inline comments.
- **Linkage: commit tags only.** "Whenever SATD was present along with another
  tag *on a commit*, it indicated the co-occurrence of the two." The method
  "counts the number of times SATD co-occurs with another category", tested with
  chi-square and odds ratios.
- **No entity linkage, no interval, no survival analysis.**
- **Result:** SATD removal co-occurs with refactoring in 95% of projects,
  addition in 89%; **"move class", "remove method" and "move attribute" occur
  more frequently in the presence of SATD** — but with the important
  qualification that **"their distribution is similar in projects with and
  without SATD."**

**Verdict: co-occurrence at commit granularity, at 77-project scale. This is the
closest published work to the proposed design and it still measures no interval.**

## 3. Zampetti et al. 2018, MSR — the accidental-removal warning

*Was Self-Admitted Technical Debt Removal a Real Removal? An In-Depth
Perspective.* Zampetti, Serebrenik, Di Penta. Five Java projects.

- **The figure: between 20% and 50% of SATD comments are removed accidentally,
  when entire classes or methods are dropped.** Only 8% of removals are
  acknowledged in commit messages.
- **Method: quantitative + qualitative/manual.** Confirmed via abstract and
  secondary sources.
- ⚠️ **Could NOT verify whether AST-level refactoring detection was used to
  separate class *deletion* from class *extraction/move*.** The MSR'18 PDF is
  behind ACM DL; the author's site 404s on the direct link and the publications
  page did not surface it. Available descriptions say "in-depth quantitative and
  qualitative study" with manual inspection, which suggests comment diffs plus
  human coding rather than a refactoring detector — **but this is not confirmed
  and must not be asserted.** Needs library access.

**Why it matters regardless:** if 20–50% of SATD disappearances are the comment
being deleted along with its class, then any interval measured from "SATD
introduction" to "SATD gone" is contaminated at that rate. Our design measures
to the *refactoring*, not to the comment's disappearance, which side-steps the
problem — that is an argument to make explicitly.

## 4. The real competitor: architectural-debt time-to-fix (May 2026)

*The Dangers of Non–Self-Fixed Architecture Technical Debt and Its Impact on
Time-to-Fix* — [arXiv:2605.16133](https://arxiv.org/html/2605.16133v1), May 2026.

| dimension | that paper | proposed design |
|---|---|---|
| debt identified from | **Jira issues**, manually labelled (3,313 instances; VioMod / ObsTech) | **SATD comments** in source |
| interval measured | **introduction commit → repayment commit** | SATD introduction → architectural refactoring |
| refactoring detection | **none** — SZZ-style tracing via PyDriller + git blame | RefactoringMiner, AST-level |
| granularity | **files and issues** | class/method entities |
| corpus | 10 Apache projects, 896 traceable ATD items | Hadoop (pilot) |
| method | descriptive stats, non-parametric tests, **survival analysis** | — |

**This occupies the latency framing for architectural debt, but not the SATD
route to it.** Their debt comes from a Jira label; ours would come from a comment
in the code. Their repayment is a git-blame-traced commit; ours would be a
detected architectural refactoring. Their finding — repayment time associates
more with dispersed development activity than with the number of affected files
— does not overlap our question.

Also relevant: *Tracing the Lifecycle of Architecture Technical Debt*
([arXiv:2501.15387](https://arxiv.org/html/2501.15387v1)) measures introduction→
payment intervals across 103 Apache projects using FAN-IN/FAN-OUT dependency
metrics — and states ATD items were **"unavailable in source code comments"**,
so again not SATD-anchored, and it uses no refactoring detection.

---

## What is and is not occupied

**Occupied:**
- SATD ↔ refactoring **co-occurrence**, at commit granularity, up to 77 projects
  (Esfandiari 2023; Iammarino 2021).
- Architectural-debt **introduction→repayment latency with survival analysis**,
  from Jira issues, files, no refactoring detection (arXiv 2605.16133, May 2026;
  arXiv 2501.15387).

**Not occupied — the remaining gap:**
1. **Interval from a SATD comment's introduction to a detected architectural
   refactoring of the entity it annotates.** No paper found does this.
2. **Entity-level linkage.** Everything found works at commit or file
   granularity. Iammarino's tightest analysis is same-file, n=201.
3. **Architectural refactoring as the repayment event**, detected at AST level,
   rather than an issue being closed or lines being blamed.

**Risks to state plainly:**
- The distinctness rests on three choices at once — SATD-anchored *and*
  entity-level *and* refactoring-detected. Drop any one and it collapses into an
  existing paper.
- Esfandiari already reports that *move class* is the refactoring most associated
  with SATD, which is the same direction our design would predict. Finding the
  same thing with a latency measure is a refinement, not a discovery.
- A May 2026 paper doing survival analysis on architectural-debt repayment means
  the framing is live and someone may reach the SATD variant first.

**Sources:** [Iammarino 2021 JSS (PDF)](https://mdipenta.github.io/files/jss2021-satd-refactoring.pdf) ·
[Esfandiari 2023 ICCKE (arXiv)](https://arxiv.org/pdf/2404.01950) ·
[Zampetti 2018 MSR (ACM, unverified)](https://dl.acm.org/doi/10.1145/3196398.3196423) ·
[ATD time-to-fix (arXiv 2605.16133)](https://arxiv.org/html/2605.16133v1) ·
[ATD lifecycle (arXiv 2501.15387)](https://arxiv.org/html/2501.15387v1)
