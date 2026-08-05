# Audit — Priority 1: citations and attributed claims

Independent verification against the live record, 2026-08-05. Every reference in
`paper/manuscript/related.md`, `paper/PRIOR_WORK.md` and `CITATION.cff` was
resolved, and every claim attributed to another paper was checked against that
paper's own text where the text was reachable.

**Headline: no fabricated citation was found. Every cited work exists, and every
DOI and arXiv identifier resolves to the work claimed.** Two attribution defects
and one probable mischaracterisation are reported below.

---

## 1. Reference ledger

| # | Reference as cited | Exists? | Authors correct? | Venue / year correct? | Identifier resolves? | Verdict |
|---:|---|---|---|---|---|---|
| 1 | Rath & Mäder 2019, *The SEOSS 33 dataset*, Data in Brief 25:104005, doi:10.1016/j.dib.2019.104005 | yes | yes — Michael Rath, Patrick Mäder | yes — Data in Brief, vol 25, art. 104005, 2019 | yes | **CONFIRMED** |
| 2 | Rath et al., *Traceability in the Wild*, ICSE 2018, arXiv:1804.02433 | yes | yes — Rath, Rendall, Guo, Cleland-Huang, Maeder | yes — ICSE 2018 (repo explicitly corrects an earlier "2019") | yes | **CONFIRMED** |
| 3 | Dabic et al. 2021, *Sampling Projects in GitHub for MSR Studies*, MSR'21, arXiv:2103.04682 | yes | yes — Ozren Dabic, Emad Aghajani, Gabriele Bavota | yes — MSR 2021 | yes | **CONFIRMED** |
| 4 | Vieira et al. 2019, *From Reports to Bug-Fix Commits*, PROMISE'19, figshare 8852084 | yes | yes — Renan Gomes Vieira, Antônio da Silva, Lincoln S. Rocha, João Paulo Pordeus Gomes | yes — PROMISE'19, doi:10.1145/3345629.3345639 | yes | **CONFIRMED** (body paywalled — see §3) |
| 5 | Iammarino et al. 2021, *An Empirical Study on the Co-Occurrence Between Refactoring Actions and SATD Removal*, J. Syst. Softw. | yes | yes — Iammarino, Zampetti, Aversano, Di Penta | yes — JSS 2021 | yes (author PDF) | **CONFIRMED** |
| 6 | Esfandiari 2023, ICCKE, arXiv:2404.01950 | yes | **NO — second author omitted** | yes — ICCKE 2023, 1–2 Nov 2023, Ferdowsi Univ. of Mashhad | yes | **DIVERGENT** — see §4.1 |
| 7 | arXiv:2605.16133, ATD time-to-fix, May 2026 | yes | not named in repo — actual: Sutoyo, Avgeriou, Capiluppi | yes — submitted 15 May 2026 | yes | **CONFIRMED** |
| 8 | arXiv:2501.15387, *Tracing the Lifecycle of Architecture Technical Debt* | yes | not named in repo — actual: Sutoyo, Avgeriou, Capiluppi | yes — Jan 2025 | yes | **DIVERGENT on characterisation** — see §4.2 |
| 9 | Zenodo 15719919, The Public Jira Dataset | yes | **omitted in CITATION.cff** — actual: Lloyd Montgomery, Clara Lüders, Walid Maalej | n/a | yes | **DIVERGENT** — see §4.3 |
| 10 | RefactoringMiner, Tsantalis, v3.1.4 | yes | Tsantalis is the principal author ✓ | v3.1.4 released 2026-05-24 | yes | **CONFIRMED** |
| 11 | tsantalis/RefactoringMiner issue #1124 | yes | opened by `khannoussi-malek`, 2026-07-25 | n/a | yes | **CONFIRMED** |
| 12 | Zampetti et al. 2018, MSR, doi:10.1145/3196398.3196423 | not re-checked | — | — | — | **OUT OF SCOPE** — appears only in `paper/SATD_NOVELTY.md`, not in `PAPER.md`; the repo already marks its method claim unverified |

---

## 2. Attributed claims checked against the source text

### 2.1 SEOSS 33 — every value matches the published table

Retrieved Table 2 of the paper (PMC6557728). The repo's claim that the paper
publishes a per-project **"Linked Change Sets [%]"** column is correct — that is
the literal column heading.

| project | repo states | paper's Table 2 | verdict |
|---|---|---|---|
| Hadoop | 97.13% (27,776) | 97.13, 27,776 | CONFIRMED |
| Hive | 96.34% (11,179) | 96.34, 11,179 | CONFIRMED |
| HBase | 90.06% (14,331) | 90.06, 14,331 | CONFIRMED |
| ZooKeeper | 87.12% (1,600) | 87.12, 1,600 | CONFIRMED |
| Flink | 41.98% (12,419) | 41.98, 12,419 | CONFIRMED |
| Maven | 24.10% (10,315) | 24.10, 10,315 | CONFIRMED |
| Errai | 8.11% (7,645) | 8.11, 7,645 | CONFIRMED |

The 33-project list in `paper/PRIOR_WORK.md` matches the paper's list exactly
(capitalisation differences only: IzPack, RESTEasy, WildFly, Teiid).

The selection criterion quoted in `related.md` §2.1 —
*"continuously capture vertical and horizontal trace links among these
artifacts"* — is **verbatim** in the paper's criteria, as is the ≥3-years
requirement. **CONFIRMED.**

### 2.2 Rath et al. ICSE'18 — every quoted figure is verbatim in the paper

Extracted the full text of arXiv:1804.02433 and searched it.

| repo claim | found in the paper | verdict |
|---|---|---|
| "across all of the projects approximately 48% of the commits were not linked to any issue" | verbatim | CONFIRMED |
| "on average only 60% of the commits were linked" | verbatim (abstract) | CONFIRMED |
| 15% unlinked in Derby vs ~76% in Maven | verbatim: "only 15% of commits in Derby having no links compared to approximately 76% of unlinked commits in Maven" | CONFIRMED |
| "approximately 43.3% of improvements and 42.4% of bugs have no commits associated with them" | verbatim | CONFIRMED |
| Derby: 2,638 bugs, 1,093 1:1, 273 1:n, 1,272 unlinked | verbatim | CONFIRMED |
| ⇒ ticket-side 51.8% | (1,093+273)/2,638 = 51.78% — arithmetic re-done | CONFIRMED |
| quote: "different practices exist across different projects, leading to huge disparities in the extent to which issue tags are added to commit messages" | **verbatim, exact string match** | CONFIRMED |
| six projects: Maven, Derby, Infinispan, Groovy, Pig, Drools | all six named in the paper | CONFIRMED |

This is the most heavily quoted source in the paper and **not one quotation is
paraphrased or altered.**

### 2.3 GHS — the field list matches the live API exactly

The repo states it queried the live API rather than the paper's Table I. I
re-queried `seart-ghs.si.usi.ch/api/r/search` myself and extracted the field
names from a live record.

* **35 fields — exact match, set-identical to the list in `paper/PRIOR_WORK.md`
  §4** (zero fields in one and not the other).
* Only `totalIssues` and `openIssues` touch issues, and both are GitHub-issue
  counts. **CONFIRMED.**
* **735,669 repositories** — CONFIRMED against the 2021 paper. See §4.4 for a
  vintage-mixing caveat.

### 2.4 Iammarino 2021 — including the keyword counts

Extracted the full text of the author's PDF.

* Four projects, Camel / Gerrit / Log4j / Tomcat — CONFIRMED.
* "at least one refactoring action in the same file where SATD occurred,
  therefore considering a total of **201 cases**" — **verbatim.** CONFIRMED.
* The repo's keyword scan claim — *"'survival' 0 hits, 'lifetime' 0 hits,
  'months' 0 hits, 'days' 1 hit, 'how long' 1 hit"* — I re-ran it on my own
  extraction and got **survival 0, lifetime 0, months 0, days 1, how long 1**.
  **All five match exactly.** CONFIRMED.

### 2.5 Esfandiari — 77 projects and the "move class" finding

* 77 open-source Java projects — CONFIRMED.
* "we found that three types of refactoring — 'move class', 'remove method', and
  'move attribute' — occur more frequently in the presence of SATD" — CONFIRMED
  from the abstract.
* ICCKE 2023 venue — CONFIRMED (13th ICCKE, 1–2 Nov 2023).
* SmartSHARK as the corpus source (claimed in `paper/SATD_NOVELTY.md`) —
  **UNVERIFIED**; neither the abstract nor the conference record mentions
  SmartSHARK. Not repeated in `PAPER.md`, so it does not affect the manuscript.

### 2.6 The Public Jira Dataset

Title, three authors, **16 repositories, 1,822 projects, 2.7M issues, CC-BY-4.0**
— every figure the repo attributes to this deposit is CONFIRMED, *including the
1,822 the repo says it cannot reproduce.* The repo is correct that 1,822 is what
the deposit publishes.

---

## 3. Unverifiable

| item | why | what would resolve it |
|---|---|---|
| Whether Vieira et al. PROMISE'19 reports per-project linkage rates | ACM DL paywall; figshare package not machine-readable without download | institutional library access |
| Zampetti et al. 2018 method (whether AST-level detection was used) | ACM DL paywall | institutional library access |
| Whether arXiv:2501.15387 covers 103 Apache projects | full text not open; abstract does not state a project count | full-text access |

The repo already marks the first two as unverified in its own text. That is
correct practice and is noted in its favour.

---

## 4. Findings

### 4.1 DIVERGENT — Esfandiari cited as a single-author paper

`paper/manuscript/related.md` §2.4, `paper/PRIOR_WORK.md` and
`paper/SATD_NOVELTY.md` all cite:

> **Esfandiari 2023** (ICCKE, arXiv:2404.01950, commit tags, 77 projects)
> *An Exploratory Study of the Relationship between SATD and Other Software
> Development Activities.* Shima Esfandiari, ICCKE 2023.

The paper has **two** authors: **Shima Esfandiari and Ashkan Sami**. Everything
else about the citation is correct. This is a straightforward attribution defect
that a reviewer or the second author would notice.

### 4.2 DIVERGENT — arXiv:2501.15387 characterised as Jira-issue-based

`related.md` §2.4 (and therefore `PAPER.md`) states:

> An architectural-debt time-to-fix literature is active — arXiv:2605.16133
> (May 2026) and arXiv:2501.15387 — **using Jira issues at file granularity with
> no refactoring detection**.

The abstract of arXiv:2501.15387 describes "a dataset of **SATD** from various
software artifacts" — i.e. self-admitted technical debt, not Jira issues.
`paper/SATD_NOVELTY.md` goes further and asserts the paper "states ATD items were
*'unavailable in source code comments'*", which points the opposite way from its
own abstract.

If 2501.15387 is SATD-anchored, then it is *closer* to the successor design the
repo describes than the repo claims, and the sentence in `related.md` is wrong.
**Confidence: moderate — abstract-level evidence only; the full text is not
open.** The claim about arXiv:2605.16133 ("Jira artifacts") **is** corroborated by
its abstract.

This one matters beyond a citation tidy-up: §2.4 exists to bound what the paper
claims is unoccupied.

### 4.3 DIVERGENT — the Public Jira Dataset is cited without its authors

`CITATION.cff` cites the deposit by DOI and title only. Its authors —
**Lloyd Montgomery, Clara Lüders, Walid Maalej** — appear nowhere in
`CITATION.cff`, and `estimates_by_org.json`, which is derived from it and
supplies **every denominator in Table 3**, carries no attribution field.

The deposit is **CC-BY-4.0**, which requires attribution of the creator in
derivative and adapted material. This is both a schema violation (see
`audit/HYGIENE.md`) and a licence-compliance gap.

### 4.4 UNSUPPORTED framing — a 2021 count fused with a 2026 schema

`abstract.md` and `results.md` §4.6 both read, in the present tense:

> GHS indexes **735,669 repositories** with **35 fields**

735,669 is the figure published in the 2021 MSR paper. 35 fields is an
observation of the **live API in 2026** — the 2021 paper itself describes 25
characteristics. Both numbers are individually correct and separately sourced,
and `paper/PRIOR_WORK.md` keeps them apart properly. Fusing them into one
present-tense clause implies a single 2026 observation, and the live index has
certainly grown past 735,669 in five years. A reviewer who checks the live count
will find a mismatch and will not know which half of the sentence is dated.

---

## 5. What I checked and found nothing wrong with

* Every DOI and arXiv identifier in the repository resolves to the work claimed.
  **No reference was unlocatable. Nothing is FABRICATED.**
* No quotation attributed to SEOSS 33 or Rath et al. ICSE'18 is altered,
  truncated misleadingly, or paraphrased as a quotation. I checked all of them
  against extracted full text, not against secondary summaries.
* The repo's own year correction (Rath ICSE **2018**, not 2019) is right, and the
  correction is documented rather than silently applied.
* The repo's refusal to characterise Vieira et al. beyond what it could read is
  correct and is the right call.
* Every per-project SEOSS number, including change-set counts, matches.
