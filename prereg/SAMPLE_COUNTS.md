# Gate candidate frame — counts, and one defect in the frame

Produced by `scripts/gate_sample.py` from `.jira_cache/` under the filter and seed
fixed in `prereg/RESOLUTION_GATE.md` (`74424dc`), committed before this script
existed. Offline; no comment was labelled, classified or judged.

## The funnel

| stage | n |
|---|---:|
| **comments scanned** (323 tickets) | **7,136** |
| · human-authored | 5,185 |
| · `githubbot`-relayed PR review | 1,230 |
| · bot CI/Yetus — *excluded per prereg* | 551 |
| · bot "opened a new pull request" — *excluded per prereg* | 76 |
| · bot other notices (merge/close/edit) | 94 |
| **eligible after bot exclusion** | **6,509** |
| **keyword-flagged** (`codebook.md` net, `pr_review_signal.py:32-35`) | **848** |
| · **AND names a code entity → the candidate frame** | **723** |
| · names **no** traceable entity | **125** |
| **drawn** (seed 20260801) | **20** |

`P = 723`. Under the pre-registered arithmetic `r × P ≥ 50`, this gate clears at
a bucket-(b) rate of **≥ 6.92%** and fails below it. At n=20 the finest
resolution available is 5 percentage points, so 1 of 20 in bucket (b) (5.0%,
36 expected events) fails and 2 of 20 (10.0%, 72 expected) clears — which is why
the pre-registered extension rule sends 2–14 to a 40-case redraw.

## The finding: 14.7% of flagged comments name no entity at all

**125 of 848 keyword-flagged comments (14.7%) name no `.java` path, no
`ClassName` and no `Class#method` form.** A structural comment with no named
entity cannot enter this design at all: the interval is measured *to a
refactoring of the flagged entity*, so with no entity there is nothing to follow
forward. Those 125 are not a coding problem to be resolved by a careful rater;
they are outside the design's reach by construction.

Read the number with its instrument in view. The entity regexes are recall-first,
deliberately matching the keyword net beside them:

```
java_path     \b[A-Za-z0-9_./-]+\.java\b
class_method  \b([A-Z][A-Za-z0-9_]*)#([A-Za-z_][A-Za-z0-9_]*)
camel_case    \b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b
```

`camel_case` accepts any two-hump token, so `IntelliJ`, `LiJinglun` (a Jira
username) and `InterruptedException` all count as "an entity named". **14.7% is
therefore a floor on the no-entity rate, not an estimate of it.** The true rate at
which a structural comment names a *resolvable, first-party* Hadoop entity is
lower, and is NOT COMPUTABLE here — it needs the same manual pass the buckets do,
which R6 forbids resting a claim on with one rater.

## Defect in the frame, reported not fixed

**The pre-registered bot exclusion misses Apache's non-GitHub-Bot automation.**
`pr_review_signal.py` reaches its CI test only after `displayName == "asf github
bot"` (`:56-62`), so an automated comment posted under any other account bypasses
it. In the candidate frame:

* **90 of 723 (12.4%) are authored by `Hudson`** — post-commit *"SUCCESS:
  Integrated in Jenkins build …"* notices, which list every changed file and so
  reliably match both the keyword net and the entity regexes. Their bodies do
  **not** match the CI pattern; it targets Yetus/precommit boilerplate
  (`green_heart`, `spotbugs`, `mvninstall`, `Apache Yetus`, `precommit`), a
  different template.
* **96 of 723 (13.3%)** are `Hudson`, `Hadoop QA` or `genericqa` combined.
* **8 of 723** match the CI pattern in the body yet passed the filter, because
  their author is not the GitHub bot (`Hadoop QA` ×4, `genericqa` ×2, and 2
  human comments containing a matching word).
* **4 of the 20 drawn are `Hudson` notices** — rows 3, 11, 19, 20
  (HADOOP-16916, HDDS-749, YARN-9923, YARN-9970).

`codebook.md:54` decision rule 1 already says *"Is it a bot CI/Yetus report? →
drop (not coded)"*, so the intent was always to exclude these; the implementation
imported from `pr_review_signal.py` does not reach them.

**Not fixed, deliberately.** Anti-hindsight commitment 4 forbids changing the
candidate filter, and the filter is being changed *after seeing the draw* either
way — loosening or tightening. Per the plan's §9 (*"If you find something that
looks like an error, report it rather than fixing it"*), it is recorded here and
carried into coding: **the four `Hudson` rows are expected to go to bucket (e)**,
and (e) leaves the denominator by pre-registered rule, so the arithmetic absorbs
them without the frame being edited.

The consequence for `P` is stated now rather than after the count: if all 96
automated comments were removed, `P` would fall from 723 to **627**, and the
clearing rate would rise from 6.92% to **7.97%**. Both figures are reported when
the gate reports, and neither is chosen after seeing `r`.

## What the draw looks like

20 comments across **18 distinct tickets** (HADOOP-19232 and YARN-8732 each
contribute two), 2017-12 to 2026-01, 11 human-authored and 9 `githubbot`-relayed.
Full untruncated bodies are in `prereg/gate_sample.json` (150 KB); the sheet to
fill in is `prereg/gate_labelling.md`.

## Reproducibility

`python3 scripts/gate_sample.py` regenerates both artifacts byte-identically:
`random.Random(20260801)` over candidates pre-sorted by `(ticket, comment_id)`,
no clock, no filesystem-order dependence. `python3 scripts/gate_sample.py
--selftest` checks the channel classifier, the entity regexes, the
double-counting guard and draw determinism.
