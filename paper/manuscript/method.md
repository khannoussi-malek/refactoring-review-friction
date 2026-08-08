# 3. Method

## 3.1 Two traceability rates, and only one of them is published

The literature reports one number and issue-anchored studies depend on another.
Both are stated here as definitions so that the divergence in §4 is a comparison
between named quantities rather than between two informal readings of the word
"traceability".

Let *p* be a project with a set of Jira project keys **K_p**, a git repository
observed at a pinned commit **H_p**, and a tracker read at a snapshot time **T**.
Write `cites(c)` for the set of issue keys appearing in commit *c*'s message.

**Definition 1 — commit-side rate.** The fraction of commits reachable from H_p
whose message cites at least one key with a prefix in K_p:

> **CSR(p) = |{ c : c ⟶ H_p, cites(c) ∩ K_p ≠ ∅ }| / |{ c : c ⟶ H_p }|**

This is the quantity Rath & Mäder publish per project as *"Linked Change Sets
[%]"* (SEOSS 33 [@rath2019seoss]) and the quantity Rath et al. (ICSE'18)
[@rath2018traceability] report as "approximately
48% of the commits were not linked to any issue". It is what the corpus-selection
bar in this study is defined on, and it is not novel here.

**Definition 2 — ticket realisation rate (TRR).** The fraction of the project's
tracked issues that are ever cited by at least one commit:

> **TRR(p) = |{ k ∈ Tickets(p, T) : ∃ c ⟶ H_p, k ∈ cites(c) }| / |Tickets(p, T)|**

TRR is a label of convenience for this paper. It is not a claim to have named the
quantity first, and nothing here depends on the name being new. The quantity has
been measured before: Rath et al. (ICSE'18) [@rath2018traceability] report that
"approximately 43.3% of improvements and 42.4% of bugs have no commits associated
with them", as a property of an issue type rather than as a project-level rate,
and Bachmann et al. (FSE'10) [@bachmann2010missing] measure the completeness of
the bug-side link against expert ground truth. What is new here is the use made
of the quantity rather than the quantity itself: the divergence between TRR and
CSR is not framed anywhere as a constraint on corpus selection.

**"Realisation" is a claim about the record, not about the work.** TRR counts a
ticket as realised when the repository's own record points back to it. A ticket
can be resolved, implemented and shipped without any commit naming it, and such a
ticket is counted as unrealised. That is the intended reading: the measure is of
what a researcher can *recover*, not of what a project *did*.

### 3.1.1 What counts as a ticket

Denominator membership is deliberately permissive, because a ticket-anchored
study samples from the whole tracker before it knows which tickets are useful:

* **All issue types.** Bug, Improvement, New Feature, Task, Test, Wish and
  Sub-task alike. **Sub-tasks are included**, because they carry their own key
  and are cited in commit messages in their own right; excluding them would drop
  the keys most likely to be cited and inflate the rate.
* **All statuses and resolutions.** Nothing is conditioned on `resolution =
  Fixed`. This matters for comparability: Vieira et al. (PROMISE'19)
  [@vieira2019reports] select on
  resolution before measuring, which pre-selects tickets that were worked, so any
  rate computed that way is not comparable to TRR without adjustment.
* **Keys, not names.** Membership is by the issue's key prefix. Measured across
  the 2,686,282-issue public Jira corpus, 326 project ids carry more than one
  distinct name while 0 carry more than one key, so a name-based denominator is
  not stable and a key-based one is (`paper/numbers.md` §5).
* **Issues that left the project are not in it.** An issue moved out of *p*
  before T no longer has a *p*-key in the tracker and is not counted; one moved in
  is counted under its current key. This is a property of the snapshot, not a
  choice.

### 3.1.2 What counts as "ever received a commit"

A ticket is realised if **at least one** commit reachable from H_p carries a
token matching `\b(?:K1|K2|…)-\d+\b` equal to its key, in the commit **subject or
body**. Nothing else is read: not the diff, not the branch name, not a pull
request body, not the tracker's own link fields.

The matcher's precision was measured rather than assumed: **195 of 200 = 97.5%**
(Wilson 95% CI 94.3–98.9%) on a seeded 200-commit manual sample across the 12
eligible projects, corpus-weighted 97.7% (`paper/matcher_validation.md`). Two of
the five enumerated failure categories could not have fired — `version_string` is
near-unreachable given a pattern demanding the upper-case key followed by `-` and
digits, and `foreign_key` is unreachable for 11 of the 12, because each project is
probed with its own key set and only Ozone is multi-key with both keys its own.
**The single-key → multi-key result on Hadoop is therefore not validated by that
sample**, Hadoop being the only true monorepo in the study and not among the 12.

One construct limit is recorded rather than corrected: **a key matched from a
branch name counts as a citation.** Merge subjects
(`Merge branch 'master' into KNOX-998-Package_Restructuring`) and svn trailers
(`.../branches/TEZ-1@1471779`) both occur in the sample. The ticket association is
correct; the commit need not implement the ticket. The five failure categories
were fixed before labelling and do not cover this case, so it was counted genuine
and is disclosed here instead of being assigned an invented category.

### 3.1.3 How the denominator is bounded in time

This is the definitional detail that decides whether TRR is interpretable, and it
is the one most easily got wrong.

TRR compares a tracker read at T against a repository read at H_p. **The measure
requires T ≤ date(H_p)**, so that every ticket in the denominator has had the
whole interval from its creation to date(H_p) in which to receive a commit. If T
runs ahead of the repository, the last tickets filed are structurally incapable
of being realised and TRR is biased downward by an amount that depends on the
project's filing rate — an artefact that looks exactly like poor traceability.

Two instantiations are used, and both satisfy the constraint:

| | tracker snapshot T | repository H_p | coverage |
|---|---|---|---|
| **TRR_live** | Apache Jira read 2026-07-25, issue **keys only** | pinned shas of 2026-07-25 | the 12 eligible projects |
| **TRR_frozen** | the Public Jira Dataset [@montgomery2025jira] (Zenodo 15719919), a snapshot predating every pinned sha | the same pinned shas | all 38 probed projects |

For **TRR_live**, T ≈ date(H_p): the two were read the same day, so the newest
tickets are the censored ones and TRR_live is a slight underestimate. The
restriction to issue keys is enforced mechanically, not by care — the field list
sent to the API is asserted to be `["key"]`, every returned issue is screened
against a forbidden-field set and a hit aborts the run rather than being filtered
out, and only the key string survives the parse loop. That is what makes the
measurement admissible over a held-out corpus: key existence is not an outcome
and nothing in it can be turned into a duration.

For **TRR_frozen**, T is years behind H_p, which is the safe direction but
introduces a different problem: the snapshot's date is not recoverable per
project from the parsed artifact. Membership is therefore defined in **issue-number
space** rather than in date space. Jira numbers issues sequentially from 1 within
a project, so a tracker holding N_p issues at T holds approximately the first N_p
numbers, and the denominator is N_p while the numerator counts only cited keys
numbered ≤ N_p. The two definitions coincide except for issues moved between
projects, which perturb the correspondence between count and highest number.
§4.3 measures the size of that perturbation rather than assuming it away.

### 3.1.4 The arithmetic ceiling, and what is left once it is removed

CSR and TRR are not independent quantities, and the constraint between them is
exact rather than statistical. It is stated here because §4.2 and §4.3 are
organised around it.

A commit either cites no key of *p*, in which case it contributes nothing to the
numerator of TRR, or cites at least one — and however many it cites, it can add
**at most one ticket that no earlier commit had already cited**, in the limiting
case where every citing commit introduces a fresh key. So the number of distinct
realised tickets is bounded by the number of citing commits:

> |{ k ∈ Tickets(p, T) : k realised }| ≤ CSR(p) · |C_p|

and dividing by |Tickets(p, T)|:

> **TRR(p) ≤ CSR(p) · |C_p| / |Tickets(p, T)| ≡ ceiling(p)**

The bound is tight — equality holds when citing commits map one-to-one onto
distinct previously-uncited tickets — and it is reached in practice only if no
ticket ever receives two commits.

**Two consequences, and the second is why this matters.**

First, **`commits / tickets` is a scale factor the two rates do not share.** A
project with 0.16 commits per ticket cannot exceed a 16% ticket-side rate at
*any* commit-side rate, including 100%. Comparing CSR and TRR without it
compares a ratio to a ratio with a different denominator.

Second, it decomposes TRR into a part that is arithmetic and a part that is
behaviour:

> **fill(p) = TRR(p) / ceiling(p) ∈ [0, 1]**

`fill` is the share of the attainable maximum actually reached — how efficiently
a project's citing commits spread across distinct tickets rather than piling onto
a few. **`fill` is the quantity a claim about citation discipline needs**;
`ceiling` is a property of how much code the project writes per ticket it files.
Both are reported for every eligible project (Table 1). §4.2 shows that in this corpus almost all of the
ticket-side variation is ceiling and almost none of it is fill.

**The subscript propagates, and it matters.** `ceiling` and `fill` are both
functions of TRR and of the ticket denominator, so each inherits whichever
instantiation of §3.1.3 produced it: ceiling_live and fill_live are computed
against the live Jira read of 2026-07-25, ceiling_frozen and fill_frozen
against the frozen snapshot. The two are not interchangeable and they do not
always agree about whether the bound binds at all — three projects have
ceiling_frozen at or above 100% while every ceiling_live is below it (§4.2,
Table 3). **Throughout this paper an unsubscripted `TRR`, `ceiling` or `fill`
means the quantity in general rather than a measured value; every measured value
carries its subscript**, in the prose, in the abstract and in the table captions.
Where a project appears with two numbers for what looks like one quantity, the
subscripts are the difference.

## 3.2 Corpus construction

**38 Apache candidates**, each Maven-built, Jira-tracked and multi-module. Each
was cloned `--filter=blob:none --no-checkout` — the probe needs `git log` and
nothing else, so a working tree is pure cost — and probed with
`scripts/traceability_probe.py`. Per-project HEAD shas are pinned in
`paper/traceability_probe.json`, so any re-run is exactly diffable against this
one.

**Hadoop itself is not one of the 38.** It is the corpus the exploratory work was
done on, and it is used here only as the worked example for multi-key matching.
Every rate reported for the eligible corpus is from a project Hadoop is not.

**Key prefixes were detected empirically from commit messages, not assumed.**
This is not a refinement; it decides the answer. A single-key probe reads Hadoop
at **26.2%**, against **92.3%** on a four-key probe and **97.8%** on a seven-key
probe of the same 28,290 commits (§5, modes 5 and 6). The three figures are the
same measurement under three key sets, not a rate and a correction to it; 97.8%
is the most complete of them, and the paper quotes whichever key set it names.
Evergreen reads 71.7% under a single-key probe for the same reason. Seven of the
38 needed a second key (`CALCITE,OPTIQ`, `HDDS,OZONE`, `KARAF,FELIX`,
`PINOT,THIRDEYE`, `ROCKETMQ,RIP`, `TOMEE,OPENEJB`, `JAMES,MAILBOX`).

**One of those second keys was never used.** `OZONE` appears in Ozone's probed
key set and is cited by **zero** commits; every Jira reference in that repository
is an `HDDS` key. It is retained in the probe because the key set was fixed from
a prefix scan before the counts were read, and removing it afterwards would be
selection on the outcome. §5.3 counts it among the six probed keys with no
project record in the frozen tracker corpus, which is a different fact about the
same key: it is neither cited in git nor present in the tracker.

**Both reference channels are counted.** GitHub-issue references (`#NNN`,
`GH-NNN`) are counted per repository alongside Jira keys. This is what turns each
drop reason from an inference into a measurement: `github_issue_references_dominate`
means the GitHub count exceeds the Jira count in that repository, and nine
projects qualify.

## 3.3 The bar, and the discipline around it

**CSR ≥ 0.80**, fixed in `predictions/PREDICTIONS.md` (`ca076a9`) **before any
project was cloned, and never moved.** Lowering it to 60% would have admitted
nine more projects and widened the corpus beyond a single ecosystem. It was not
lowered.

The same discipline was applied where it hurt more. A separate frozen threshold —
vendor share ≥ 0.40 for the module-tier rule — was held through a held-out
replication in which lowering it would have rescued two of five projects (HBase,
maximum share 0.33; Phoenix, which flagged nothing). It was not lowered, and the
rule then failed 0 of 3 where it could be tested (`replication/REPLICATION.md`).
Both facts are stated because a pre-registered threshold that is never tested
against temptation is not evidence of anything.

**Held-out discipline is mechanical.** Outcome data was never observed for seven
projects — Ozone, Tez, ZooKeeper, Ranger, Oozie, Knox, Sqoop. The rule is written
down (`PROJECT_STATE.md` §3); the ticket-side script requests one Jira field and
aborts if it receives another; the matcher-validation script asks git for `%H`,
`%s` and `%b` and nothing else, so it *cannot* compute a duration. HBase and
Phoenix were dropped from the held-out corpus on 2026-07-30 and quarantined,
because their committed artifacts are one subtraction away from per-ticket
latency even though no outcome was ever observed for either; their coverage
numbers remain usable and are reported.

## 3.4 The detector, and the second ecosystem

Architectural episodes in the Apache corpus were detected with **RefactoringMiner
3.1.4** over 8,919 Hadoop commits, at AST level, never from message text. The
second ecosystem — `BearStudio/start-ui-web`, TypeScript, 1,199 commits — is
**exploratory throughout**, and only counts and proportions from it enter this
paper, never a test. Its detector caveats are load-bearing and are given in full
in §6.7: TypeScript support was two months old at measurement, has no independent
validation in the literature, and `Change Type Declaration Kind` was excluded as
a false positive (160 instances in one commit, upstream issue #1124).
