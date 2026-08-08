# 7. Discussion

## 7.1 For researchers designing an issue-anchored study

**Project eligibility cannot be established from metadata.** Every one of the six
failure modes in §5 was found by reading commit messages from the project itself,
after the project had been selected. Three of them are silent: they yield a
plausible low number rather than an error, and nothing in the result signals that
the key set is wrong. A researcher who samples on stars, contributors and
language, then computes a linkage rate, will get a number for every candidate and
will not be told which of those numbers mean anything.

**Measure the side of the rate your design actually samples on, and report
commits per ticket beside it.** A commit-side rate answers "if I start from a
commit, can I find its ticket?". A design that starts from *tickets* needs the
ticket realisation rate, and the first does not imply the second — Hive is 97.0%
one way and 55.8% the other (TRR_live). But the more useful advice is the
ceiling (§3.1.4):
**below one commit per ticket the two rates are not commensurable at all**, and
every project in our eligible corpus is below it. Report
`commits / tickets`; it costs nothing, it bounds the ticket-side rate before any
measurement, and no published linkage rate carries it.

**What our own extension does and does not license.** Across the whole probe we
find no detectable association between the two rates (rho = −0.010, n = 33, 95%
CI [−0.35, +0.34]). That rules out a strong positive relationship — the
assumption a selection bar encodes — but at 80% power this study detects only
|rho| ≥ 0.47, so it does not establish a null. On the twelve projects measured
exactly the same correlation is +0.518, and we report the disagreement rather
than resolving it (`paper/DIRECTION_TENSION.md`).

**Report the bar, the attrition, and the rejected candidates.** The dropped
projects are the informative part. That 26 of 38 Apache candidates are unusable,
and that the 12 survivors are one ecosystem, is a fact about the population that a
paper reporting only its final corpus cannot convey — and it is a fact each such
paper independently rediscovers and does not write down.

## 7.2 For dataset and sampling-frame builders

The fields that decide usability are absent from the standard frame. GHS indexed
735,669 repositories as published in 2021 and exposes 35 fields per record
today; only `totalIssues` and `openIssues` touch issues and both are
GitHub-issue counts. There is no tracker type, no external
tracker, no issue–commit linkage, no commit-message convention.

Four fields would close most of the gap, and all four are cheap to compute from a
shallow clone and a tracker listing:

1. **the dominant reference channel** — Jira-key citations against GitHub-issue
   references, *counted*, not assumed;
2. **the tracker's project-key set**, which catches concurrent siblings (mode 5);
3. **the key set actually appearing in commit messages**, which is the only thing
   that catches superseded records (mode 6) — those keys exist in git and nowhere
   else;
4. **the rate recomputed over recent history**, which exposes a convention that
   changed mid-history (mode 4).

**What the four fields would cost.** All four come from a `--filter=tree:0`
bare clone plus one tracker listing. On this corpus those 38 clones came to
**228 MB, a mean of 6.0 MB per project**, against the 4.3 GB the original
working-tree sweep took — a 19x reduction. Fields 1, 3 and 4 need only `git log` over commit
messages — no trees, no blobs, no working tree. Field 2 is one paginated tracker
call for issue keys. For a frame that already crawls repository metadata at the
scale of 735,669 repositories, the marginal cost is the clone, and the clone is
the cheapest kind there is. We are not claiming it is free at that scale; we are
claiming it is the same order as what GHS already does per repository, and that
nobody has to guess.

This study spent 38 clones and 4.3 GB to keep 12. That cost is paid again by every
group that attempts the same kind of corpus, and none of it is recoverable from
published metadata.

## 7.3 For the field

If architectural change is invisible in three record channels across two
ecosystems, then a literature built on those records is measuring the minority of
architectural work that someone chose to expose. The obvious hope is that the
visible minority is a random sample of the whole. **In the one corpus where we
could test that, it is not.** In the TypeScript corpus, architectural commits
routed through a pull request are five times larger by churn and four times more
abstraction-heavy than those pushed directly to main. The 31% that are visible are
systematically the big, abstraction-heavy ones, and the 69% that are not are
systematically the small, relocation-shaped ones.

That is a selection effect on the dependent variable, and it points the same way
in every study that mines only what was recorded: architectural work will look
larger, more deliberate and more discussed than it is.

## 7.4 What follows from the corpus limit, without softening it

Twelve projects is not enough, and more projects would not fix it.
Between-project correlation caps the effective sample at **P/ICC** whatever the
corpus size: at P = 12 and ICC = 0.02 the ceiling is 600 against the 769
independent tickets the effect needed at 80% power. **The ICC is unmeasured**, and
was deliberately not estimated from the four clusters available — between-cluster
variance has 3 degrees of freedom at n = 4, and the decision turns on the
difference between 0.015 and 0.02, which four clusters cannot resolve. It must
come from the pooled study as a first stage. The direction of the bias is also
bad: these twelve share contributors, committers, review norms and in several
cases build and CI infrastructure, so this sample's ICC exceeds a random
sample's, and higher ICC is what makes the study impossible.

Three ways out, with their costs. **Lower the bar and model the measurement
error** — at 60% another nine projects qualify, at the cost of a biased sample of
tickets *within* each project, which §7.3 shows is real rather than hypothetical.
**This is the one to avoid drifting into silently.** **Change the outcome so it
needs no tickets** — anything computed purely from git dissolves both the
traceability filter and the ecosystem clustering, at the cost of the
creation-to-first-commit clock and with it the ability to measure waiting at all.
**Accept ecosystem-bounded scope and say so** — register as a study of one
ecosystem, twelve projects, and state the boundary as a finding rather than
discovering it in review. The second is the strongest study and the largest
rebuild; the third is honest and immediately actionable.

## 7.5 What this paper does not claim

It does not claim that Jira-citing projects are better engineered, or that the
projects on GitHub Issues are less traceable in any sense that matters to their
own maintainers. The convention this research needs is not a quality signal; it is
a research affordance, and its decline is a cost to researchers rather than to the
projects.

It does not propose the successor design that the corpus limits point towards.
That is a separate registered report with its own feasibility gates, and its
novelty margin against an active architectural-debt time-to-fix literature is
recorded in the replication package as **not assessed**.

And it does not offer a fix. The six modes are diagnosable, not repairable: a
project whose tracker is downstream of its repository will not start citing keys
because a researcher would like it to.
