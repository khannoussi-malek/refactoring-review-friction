# 7. Discussion

## 7.1 For researchers designing an issue-anchored study

**Project eligibility cannot be established from metadata.** Every one of the six
failure modes in §5 was found by reading commit messages from the project itself,
after the project had been selected. Three of them are silent: they yield a
plausible low number rather than an error, and nothing in the result signals that
the key set is wrong. A researcher who samples on stars, contributors and
language, then computes a linkage rate, will get a number for every candidate and
will not be told which of those numbers mean anything.

**Measure the side of the rate your design actually samples on.** A commit-side
rate answers "if I start from a commit, can I find its ticket?". A design that
starts from *tickets* — which is what any study of what precedes a decision must
do — needs the ticket realisation rate, and the first does not imply the second.
Kylin is the demonstration: 83.9% one way, 12.0% the other, in the same project on
the same day. §4.3 shows the gap is not an artefact of the eligible twelve.

**Report the bar, the attrition, and the rejected candidates.** The dropped
projects are the informative part. That 26 of 38 Apache candidates are unusable,
and that the 12 survivors are one ecosystem, is a fact about the population that a
paper reporting only its final corpus cannot convey — and it is a fact each such
paper independently rediscovers and does not write down.

## 7.2 For dataset and sampling-frame builders

The fields that decide usability are absent from the standard frame. GHS indexes
735,669 repositories with 35 fields; only `totalIssues` and `openIssues` touch
issues and both are GitHub-issue counts. There is no tracker type, no external
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

Twelve projects is not enough, and more projects would not fix it. Between-project
correlation caps the effective sample at **P/ICC** whatever the corpus size: at
P = 12 and ICC = 0.02 the ceiling is 600 against the 769 independent tickets the
effect needed at 80% power. **The ICC is unmeasured**, and it was deliberately not
estimated from the four clusters available — between-cluster variance has 3
degrees of freedom at n = 4, and the whole decision turns on the difference
between 0.015 and 0.02, which a four-cluster estimate cannot resolve. It must come
from the pooled study as a first stage.

The direction of the bias is also bad. These twelve share contributors,
committers, review norms, release processes and in several cases build and CI
infrastructure, so this sample's ICC is higher than a random sample's — and higher
ICC is the direction that makes the study impossible.

Three ways out, stated with their costs:

1. **Lower the bar and model the measurement error.** At 60% another nine
   projects qualify and the ecosystem widens. The cost is a biased sample of
   *tickets within* each project, and §7.3 says that bias is real rather than
   hypothetical. **This is the one to avoid drifting into silently**, because it
   looks like a free corpus expansion and is not.
2. **Change the outcome so it needs no tickets.** Anything computed purely from
   git — commit-to-commit intervals, revert rates, recurrence of churn in the same
   files — dissolves both the traceability filter and the ecosystem clustering.
   The cost is losing the creation-to-first-commit clock, and with it the ability
   to measure *waiting* at all.
3. **Accept ecosystem-bounded scope and say so.** Register as a study of one
   ecosystem, twelve projects, and state the boundary as a finding rather than
   discovering it in review.

Option 2 is the strongest study and the largest rebuild. Option 3 is honest and
immediately actionable.

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
