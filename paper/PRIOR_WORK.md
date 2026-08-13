# Prior work check — does anyone already report per-project traceability rates?

Findings only, no related-work prose. Verified 2026-07-25.

**Short answer: yes, one of the three does, and it is much closer to our
contribution than expected. The novelty claim has to move.**

---

## 1. Rath & Mäder 2019 — SEOSS 33 (the important one)

*The SEOSS 33 dataset — Requirements, bug reports, code history, and trace links
for entire projects*, **Data in Brief** 25:104005, 2019.
doi:[10.1016/j.dib.2019.104005](https://doi.org/10.1016/j.dib.2019.104005)

**Does it report per-project linkage rates? YES — explicitly, as a column.**
Table 2 gives, per project, change-set count and **"Linked Change Sets [%]"**.
That is the same quantity as our commit-side traceability rate.

| project | SEOSS 2019 | our 2026 probe | Δ |
|---|---:|---:|---:|
| Hadoop | 97.13% (27,776 commits) | **97.8%** (7-key, 28,290) | +0.7pp |
| Hive | 96.34% (11,179) | **97.0%** (18,213) | +0.7pp |
| HBase | 90.06% (14,331) | **92.5%** (21,220) | +2.5pp |
| ZooKeeper | 87.12% (1,600) | **90.4%** (2,718) | +3.3pp |
| Flink | 41.98% (12,419) | **66.0%** (38,219) | +24.1pp |
| Maven | 24.10% (10,315) | — | — |
| Errai | 8.11% (7,645) | — | — |
| Cassandra | 37.03% | Groovy 37.91% | Drools 47.24% |

**Independent corroboration of our central result.** Their spread is 8.11% →
97.13% across 33 projects; ours is 0.01% → 98.3% across 38. Four of five
overlapping projects agree within 3.3pp on corpora seven years apart — strong
mutual validation of the method.

The Flink gap (+24pp) is the interesting one and is almost certainly *scope*,
not error: their snapshot ends ~2019 with 12,419 commits, ours has 38,219, so
we cover a decade in which Flink's Jira citation practice could have changed.
Worth a footnote, not a correction.

**Selection criteria (relevant to our corpus-feasibility argument):**
1. project captures requirements, bug reports and source code;
2. **"A project shall continuously capture vertical and horizontal trace links
   among these artifacts"**;
3. ≥3 years active development with stable releases;
4. Jira + git only, primarily Java, from Apache / JBoss / Atlassian.

So a traceability criterion **is** used for selection — but as a qualitative
requirement, **not a numeric threshold**. They do not state a cut-off, do not
report how many candidates were rejected, and having selected on trace links
they still admit Errai at 8.11%. Our pre-registered ≥0.80 bar, the 12-of-38
attrition, and the finding that survivors are one ecosystem are not in this
paper.

**33 projects: Archiva, Axis2, Cassandra, Derby, Drools, Errai, Flink, Groovy,
Hadoop, HBase, Hibernate, Hive, HornetQ, Infinispan, Izpack, JBehave, JBoss-TM,
JBPM, Kafka, Keycloak, Log4j, Lucene, Maven, Pig, Railo, Resteasy, Seam2, Spark,
Switchyard, Teiid, Weld, Wildfly, Zookeeper.**

---

## 2. Rath et al. — "Traceability in the Wild" (ICSE **2018**, not 2019)

*Traceability in the Wild: Automatically Augmenting Incomplete Trace Links*,
ICSE'18. [arXiv:1804.02433](https://arxiv.org/abs/1804.02433)

⚠️ **Year correction:** the brief cites "Rath et al. 2019, selecting OSS projects
for traceability studies". The project-selection-and-link-rate paper is ICSE
**2018**; the 2019 Rath item is the SEOSS 33 dataset above. I found no separate
2019 paper on selecting OSS projects for traceability studies.

**Does it report per-project linkage rates? YES, both directions.**
Six projects, all Git+Jira: Maven, Derby, Infinispan, Groovy, Pig, Drools.

- **Commit side:** "across all of the projects approximately **48% of the
  commits were not linked to any issue**"; headline framing is "on average only
  **60%** of commits were linked". Per-project spread is explicit: **15%
  unlinked in Derby vs ~76% unlinked in Maven**.
- **Ticket side (matters for our Task 9):** "approximately **43.3% of
  improvements and 42.4% of bugs have no commits associated with them**."
  Table 1 gives raw counts — e.g. Derby: 2,638 bug issues, 1,093 linked 1:1,
  273 linked 1:n, **1,272 with no commit** ⇒ ticket-side coverage **51.8%**.

**This is the closest precedent to our Task 9 result**, and it agrees: our 12
passing projects run 12.0%–69.0% ticket-side, straddling their ~57% bug-side
figure. Their sentence — "different practices exist across different projects,
leading to huge disparities in the extent to which issue tags are added to
commit messages" — is our corpus-feasibility finding stated qualitatively in
2018.

Selection was *not* by link rate: the six were chosen because each "largely
followed the practice of tagging commits with issue IDs" — the same informal
criterion as SEOSS, and again with no threshold.

---

## 3. Vieira et al. 2019 — 55 Apache projects bug-fix dataset

*From Reports to Bug-Fix Commits: A 10 Years Dataset of Bug-Fixing Activity from
55 Apache's Open Source Projects*, PROMISE'19, pp. 80–89.
Replication package: figshare 8852084.

**Does it report per-project linkage rates? NOT ESTABLISHED — could not verify.**

Confirmed: >70,000 bug reports, 55 ASF projects in 9 categories, mined from Jira
selecting issues typed *Bug* with status CLOSED/RESOLVED and resolution *Fixed*,
then linked to fixing commits; static and dynamic perspectives; NLTK
preprocessing retaining the 1,000 most frequent words.

**Blocked:** ACM DL, ResearchGate and figshare all returned **403** to
unauthenticated fetches. I could not read the paper body or the package
manifest, so I cannot confirm whether per-project linkage rates appear, how many
of the 70k reports actually have linked commits, or whether any project was
dropped for low linkage. **Flagged as unverified — needs library access.**

Note the selection is already conditioned on *resolution = Fixed*, which
pre-selects tickets that were worked, so any linkage rate it reports would not
be comparable to ours without care.

---

## 4. Dabic et al. 2021 — GHS / seart-ghs.si.usi.ch

*Sampling Projects in GitHub for MSR Studies*, MSR'21 Data Showcase.
[arXiv:2103.04682](https://arxiv.org/abs/2103.04682) · dataset
doi:10.5281/zenodo.4476391

**Does GHS expose any traceability-related selection field? NO.**

Queried the live API directly (`/api/r/search`) rather than trusting the paper's
Table I, which is an image. A record carries **35 fields**:

```
id, name, isFork, commits, branches, releases, forks, mainLanguage,
defaultBranch, license, homepage, watchers, stargazers, contributors, size,
createdAt, pushedAt, updatedAt, totalIssues, openIssues, totalPullRequests,
openPullRequests, blankLines, codeLines, commentLines, metrics, lastCommit,
lastCommitSHA, hasWiki, isArchived, isDisabled, isLocked, languages, labels,
topics
```

Only **`totalIssues`** and **`openIssues`** touch issues at all, and both are
GitHub-issue *counts*. There is **no** field for: issue tracker type, external
tracker (Jira) usage, issue–commit linkage, traceability, or commit-message
convention. The one adjacent feature is filtering by **issue labels**, described
in the paper as "still under development".

**Consequence, and it is the actionable one.** GHS is the standard sampling
frame for MSR studies, indexes 735,669 repositories, and **cannot express the
single criterion that determines whether a project is usable for issue-linked
research.** A researcher sampling with GHS gets stars, commits, contributors and
license, then discovers post hoc that 26 of 38 candidates are unusable. That is
exactly what happened to us, and it is a concrete gap our probe fills.

---

## What this means for the novelty claim

**Weakened:** "nobody reports per-project traceability rates" is false. SEOSS 33
publishes the exact column for 33 projects, and Rath 2018 publishes both
directions for six. Any claim of first-to-measure must go.

**Still standing, and now better positioned:**
1. **A pre-registered numeric bar, applied before outcomes, with reported
   attrition.** Both prior papers select on trace links informally and report the
   rate afterwards; neither states a threshold, an attrition count, or which
   candidates were rejected.
2. **The population finding.** 12 of 38 pass, and *all 12 are one ecosystem*.
   SEOSS's own table contains the ingredients — Apache projects at the top,
   JBoss at the bottom — but the paper does not draw the inference.
3. **Both channels measured together.** No prior work counts GitHub-issue
   references alongside Jira keys, which is what shows the bar selects a
   *tracker* rather than a discipline (7 dropped projects cite GitHub issues in
   >50% of commits).
4. **The commit-side / ticket-side gap as a sampling-frame warning.** Rath 2018
   reports both directions; nobody frames the divergence as a threat to using a
   high commit-side rate to justify a corpus. Kylin at 83.9% commit-side and
   12.0% ticket-side is the sharpest case.
5. **The GHS gap.** The standard sampling tool cannot express the criterion.

**Sources:** [SEOSS 33 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6557728/) ·
[Traceability in the Wild (arXiv)](https://arxiv.org/pdf/1804.02433) ·
[Sampling Projects in GitHub (arXiv)](https://arxiv.org/pdf/2103.04682) ·
[GHS live API](https://seart-ghs.si.usi.ch/) ·
[Vieira et al. PROMISE'19 (ResearchGate, 403)](https://www.researchgate.net/publication/335594592)


---

## 5. The bug-side linkage literature (added 2026-08-05)

Added in response to the MSR review's central finding: the canonical bug-side
work on this exact asymmetry was missing. Every item below was verified against
the source — authors, venue, year, identifier, and the attributed claim. Details
of the verification are in `audit/CITATIONS.md`.

**Bachmann, Bird, Rahman, Devanbu & Bernstein, FSE'10** — *The Missing Links:
Bugs and Bug-fix Commits*, doi:10.1145/1882291.1882308, pp. 97–106. A core Apache
HTTP Server developer annotated **493 commits over six weeks** exhaustively using
their tool Linkster, establishing ground truth rather than inferring it. Against
it, **only 47.6% of bug-fix-related commits are documented in the bug tracking
database**. Verified from the paper's own text.

**Bird, Bachmann, Aune, Duffy, Bernstein, Filkov & Devanbu, ESEC/FSE'09** —
*Fair and Balanced? Bias in Bug-Fix Datasets*, pp. 121–130. Missing links are not
missing at random, so a dataset built from linked records is a biased sample and
models fitted to it inherit the bias.

**Nguyen, Adams & Hassan, WCRE'10** — *A Case Study of Bias in Bug-Fix Datasets*,
pp. 259–268, IEEE. **Venue correction:** the review that prompted this revision
cited this as MSR'10. It is WCRE'10. The review also characterised it as a
replication on a system with near-perfect linkage; that characterisation could
not be verified from an accessible copy and is **not asserted here**.

**Herzig, Just & Zeller, ICSE'13** — *It's not a bug, it's a feature: how
misclassification impacts bug prediction*. **More than 7,000 issue reports across
five open-source projects, 33.8% misclassified**, and **39% of files marked
defective never had a bug**. Bears directly on this study's decision to admit all
issue types: a denominator that admits every type cannot be moved by
misclassification.

**Wu, Zhang, Kim & Cheung, ESEC/FSE'11** — *ReLink: Recovering Links between Bugs
and Changes*, doi:10.1145/2025113.2025120, Szeged. Learns link features — time
proximity, author identity, textual similarity — and recovers missing links well
above regex heuristics. It recovers **links**, not **key sets**, which is why
§5.5's claim survives in qualified form.
