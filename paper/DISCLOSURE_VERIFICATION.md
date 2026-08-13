# Disclosure verification — §8, line by line

**For the author. Mark each line TRUE, FALSE or INCOMPLETE.**

§8.2 of the manuscript makes factual assertions about how this work was produced.
Some cover the sessions from **3c0c24d onward (2026-08-05)**, which are in the git
history and which I can read. Others cover **19–25 July 2026**, which produced the
original corpus, the pre-registration and every exploratory result — **that period
predates any record available to me, and every claim about it is inferred from
what the repository says about itself.**

Lines marked **INFERRED** are the ones to read closest: I did not observe them.
Lines marked **OBSERVED** are checkable against the git history and the artifacts,
and I did check them.

A disclosure that is wrong in the author's favour is worse than no disclosure. A
disclosure that is wrong against the author is also wrong. Both directions matter.

---

## A. Which tools were used

| # | §8 asserts | basis | ☐ |
|---:|---|---|---|
| A1 | Large language model assistants were used "across parts of this work" | **INFERRED** for 19–25 July; **OBSERVED** for 2026-08-05 | ☐ T ☐ F ☐ I |
| A2 | The assistant was **Anthropic's Claude** | **INFERRED** — I know what produced the August sessions; I do not know what, if anything, was used in July | ☐ T ☐ F ☐ I |
| A3 | No other AI tool is named | **INFERRED** — if a different assistant, a code-completion tool (Copilot or similar), or a translation or grammar tool was used in July, §8 currently omits it | ☐ T ☐ F ☐ I |
| A4 | The disclosure names no specific model versions or dates of use | **OBSERVED** — this is a deliberate omission; add them if you want the record to be precise | ☐ T ☐ F ☐ I |

**A3 is the line most likely to be incomplete.** An omitted tool is the failure
mode reviewers penalise; an over-inclusive list is merely verbose.

## B. What the tools were used for

| # | §8 asserts | basis | ☐ |
|---:|---|---|---|
| B1 | "**Every script in `scripts/` that produced a number in this paper was drafted with assistance**" | **INFERRED for the July scripts** — `citation_rate.py`, `traceability_probe.py`, `ticket_coverage.py`, `filter_architectural.py`, `blast_radius_model.py`, `social_centrality.py`, `temporal_trend.py`, `jira_estimates.py`, `jira_archive.py` and others all predate 3c0c24d. **This is the single strongest claim in §8 and I inferred it.** If any of those were written unassisted, "every" is false. | ☐ T ☐ F ☐ I |
| B2 | The scripts are committed, the artifacts are committed, and each is re-runnable | **OBSERVED** | ☐ T ☐ F ☐ I |
| B3 | "The manuscript sections were **drafted with assistance from the author's outlines, findings and decisions**" | **OBSERVED** for the August drafting. **INFERRED** that the July-era memos (`results_dossier.md`, `SLICE_LOG.md`, `SUI_FINDINGS.md`, `PROJECT_STATE.md`) were produced the same way — §8 does not distinguish them from the manuscript, so a reader will assume it covers both | ☐ T ☐ F ☐ I |
| B4 | Manuscript sections were "**revised by the author**" | **INFERRED** — I cannot see your revision passes. If the August sections went in substantially as drafted, this word is doing work it has not earned | ☐ T ☐ F ☐ I |
| B5 | Citations were checked against source texts — authors, venue, year, identifier, and whether the source says what is attributed | **OBSERVED** — the record is `audit/CITATIONS.md` | ☐ T ☐ F ☐ I |
| B6 | An **adversarial audit** re-derived load-bearing results with separately written code, enumerated the κ bounds, and verified all 2,491 cache files | **OBSERVED** — `audit/`, and the 2,491 check was re-run | ☐ T ☐ F ☐ I |
| B7 | The audit report is in the replication package "**unedited**" | **OBSERVED** — `audit/` has not been modified since it was written | ☐ T ☐ F ☐ I |

## C. What §8 says the tools did **not** do

Each of these is a claim that a decision was **yours**. If any was in fact
tool-suggested and you accepted it, the line needs softening.

| # | §8 asserts is the author's | basis | ☐ |
|---:|---|---|---|
| C1 | The research questions | **INFERRED** | ☐ T ☐ F ☐ I |
| C2 | The study design | **INFERRED** | ☐ T ☐ F ☐ I |
| C3 | **The pre-registered 0.80 bar, and its commitment before any project was cloned** | **PARTLY OBSERVED** — `predictions/PREDICTIONS.md` has exactly one commit (`ca076a9`, 2026-07-25) and was never modified, so the *commitment* is verifiable. That the **value 0.80 was your choice** is INFERRED | ☐ T ☐ F ☐ I |
| C4 | The decision to hold the 0.80 bar when lowering it would have helped | **INFERRED** — the fact that it was held is OBSERVED; that the decision was yours is not | ☐ T ☐ F ☐ I |
| C5 | The decision to hold the vendor-share threshold at 0.40 through a failed replication | **INFERRED**, same distinction | ☐ T ☐ F ☐ I |
| C6 | **The six retractions** | **INFERRED** — `PROJECT_STATE.md` records them as your decisions; I did not observe them being taken | ☐ T ☐ F ☐ I |
| C7 | The judgment of what the results mean | **INFERRED** | ☐ T ☐ F ☐ I |
| C8 | "The author takes **full responsibility for all content**, including any error a tool introduced and the author did not catch" | **YOUR STATEMENT TO MAKE** — this is not a fact I can verify. Confirm you intend it as written | ☐ T ☐ F ☐ I |

**C3 through C6 share a structure worth noticing.** In each case the *outcome* is
in the record and the *authorship of the decision* is not. §8 currently asserts
the second. That is very probably right, and it is the class of claim a hostile
reader would ask you to substantiate.

## D. Errors §8 attributes to assistance

§8 lists four errors as "introduced by assistance and caught by review". All four
are **OBSERVED** — I can point to each in the git history. What is **INFERRED** is
the attribution: that assistance introduced them rather than the author.

| # | error | where it is recorded | basis | ☐ |
|---:|---|---|---|---|
| D1 | A median computed as the upper-middle value at even *n* (55.5% where 52.6% is correct) | `REVISION_LOG.md` C4, `scripts/ticket_side_38.py` | OBSERVED; attribution INFERRED | ☐ T ☐ F ☐ I |
| D2 | A validation figure quoted for a different approximation than the one in use (0.45pp where 1.76pp applies) | `REVISION_LOG.md` C5 | OBSERVED; attribution INFERRED | ☐ T ☐ F ☐ I |
| D3 | A provenance checker that could not fail | `REVISION_LOG.md` 0d, `audit/NUMBERS.md` §7 | OBSERVED; attribution INFERRED | ☐ T ☐ F ☐ I |
| D4 | A first rebuild of that checker reproducing the same defect by another route | `REVISION_LOG.md` 0d | OBSERVED; attribution INFERRED | ☐ T ☐ F ☐ I |
| D5 | The list is complete — no other assistance-introduced error is known | **INFERRED, and unprovable.** It is complete as to what review *caught*. Nothing establishes that nothing else was introduced and missed | ☐ T ☐ F ☐ I |

**D5 is the honest weak point of the whole disclosure** and you may want §8 to say
so explicitly rather than leaving the list looking exhaustive.

## E. §8.3 — the LLM used as a rater

| # | §8.3 asserts | basis | ☐ |
|---:|---|---|---|
| E1 | The rater pilot is "an object of study, not a method the paper's claims rest on" | **OBSERVED** — no claim traces to it | ☐ T ☐ F ☐ I |
| E2 | Its contamination is disclosed and its conclusions bounded | **OBSERVED** — `LLM_RATER_PILOT.md` §6 | ☐ T ☐ F ☐ I |
| E3 | It is kept separate from §8.2 because it is a different kind of AI use | **OBSERVED** — a deliberate structural choice; confirm you agree with it | ☐ T ☐ F ☐ I |

## F. §8.4 — funding and interests

| # | §8.4 asserts | basis | ☐ |
|---:|---|---|---|
| F1 | No funding was received | **INFERRED** — nothing in the repository states this either way | ☐ T ☐ F ☐ I |
| F2 | No competing interests | **INFERRED** — same | ☐ T ☐ F ☐ I |
| F3 | The work was carried out independently, alongside full-time employment | **OBSERVED** — `README.md` §1 says so; whether it is still true at submission is yours | ☐ T ☐ F ☐ I |

---

## Summary

30 assertions, counted mechanically from the tables above:

| | count |
|---|---:|
| **OBSERVED** — checkable in the record, and I checked | 9 |
| **INFERRED** — I did not observe it | 12 |
| **Mixed** — the outcome is observed, the attribution is inferred | 7 |
| **Partly observed** (C3) | 1 |
| **Yours to state**, not verifiable by anyone else (C8) | 1 |

The seven **mixed** rows are the interesting class: B3, and D1–D5. In each, the
thing that happened is in the record and *who or what caused it* is not. §8
currently asserts the cause.

**The four lines to read hardest: B1, C3–C6 as a group, D5, and A3.** B1 says
"every script"; C3–C6 assert authorship of decisions whose outcomes but not whose
origins are in the record; D5 implies a complete error list; A3 is silent about
tools I would have no way of knowing were used.

**If any line is FALSE or INCOMPLETE**, the fix belongs in
`paper/manuscript/acknowledgements.md`, and the two assemblers
(`scripts/assemble_manuscript.py`, `scripts/make_latex.py`) regenerate `PAPER.md`
and the preprint from it.
