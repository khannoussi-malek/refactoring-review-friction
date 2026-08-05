# 8. Acknowledgements and disclosures

## 8.1 Data and tools

This study is built on artifacts other people made public. The Apache Software
Foundation publishes the issue trackers and repositories the whole corpus is
drawn from. Lloyd Montgomery, Clara Lüders and Walid Maalej deposited the Public
Jira Dataset (Zenodo 15719919, CC BY 4.0), which supplies every estimate-coverage
base rate and every frozen ticket denominator in Table 3. Michael Rath and
Patrick Mäder's SEOSS 33 provides the independent measurement this study's probe
is validated against, and the agreement between them at matched scope
(Section 4.4) is the strongest external check the work has. Nikolaos Tsantalis
and the RefactoringMiner contributors built the detector. None of them is
responsible for what is done with their work here.

## 8.2 Use of AI tools

**Declared in full, because a paper about the trustworthiness of records should
be candid about how its own were produced.**

Large language model assistants (Anthropic's Claude) were used across parts of
this work. Their role was:

* **writing and running analysis code.** Every script in `scripts/` that produced
  a number in this paper was drafted with assistance. The scripts are committed,
  the artifacts they emit are committed, and each is re-runnable — that is what
  makes the assistance auditable rather than something the reader must take on
  trust.
* **drafting prose.** The manuscript sections were drafted with assistance from
  the author's outlines, findings and decisions, and revised by the author.
* **literature verification.** Citations were checked against source texts —
  authors, venue, year, identifier, and whether the source says what is
  attributed to it. The record of those checks is in the replication package.
* **an adversarial audit of this work's own numbers.** An independent
  AI-conducted pass re-derived the load-bearing results from primary artifacts
  with separately written code, exhaustively enumerated the κ bounds, verified
  all 2,491 frozen cache files against their manifest, and reported what it found
  — including several errors that were then corrected. Its report is in the
  replication package under `audit/`, unedited.

**What the tools did not do.** The research questions, the study design, the
pre-registered 0.80 bar and its commitment before any project was cloned, the
decision to hold that bar and the vendor-share threshold when moving them would
have helped, the six retractions, and the judgment of what the results mean are
the author's. **The author takes full responsibility for all content, including
any error a tool introduced and the author did not catch.**

*A line-by-line verification checklist for this section, separating what is
observable in the repository's record from what is inferred about the sessions
that predate it, is at `paper/DISCLOSURE_VERIFICATION.md`.*

**Errors that assistance introduced and review caught** are recorded rather than
quietly fixed, because they bound how much the audit trail is worth: a median
computed as the upper-middle value at even *n*; a validation figure quoted for a
different approximation than the one in use; a provenance checker that could not
fail, and a first rebuild of it that reproduced the same defect by another route.
Each is in `paper/REVISION_LOG.md` with what it changed.

## 8.3 A separate matter: the LLM used as a rater

Section 6.5 reports a pilot in which a language model applied this study's
codebook as a second rater. **That is an object of study here, not a method the
paper's claims rest on**, and it is reported with its contamination disclosed and
its conclusions bounded. No claim in this paper depends on it.

## 8.4 Funding and competing interests

No funding was received. The author declares no competing interests. The work was
carried out independently, alongside full-time employment, which is stated in
Section 6.8 because it explains the shape of the study's limitations.
