# RQ1 week-1 slice — run log

A step-by-step record of the thin vertical slice, run on **hadoop**.
Everything here is reproducible: each step shows the exact command and the real output.
Follow top to bottom. Author: automated run, 2026-07-19.

---

## TL;DR (read this first)

| Filter | Question | Result | Verdict |
|---|---|---|---|
| **Filter 3** (traceability) | What % of commits cite a Jira key? | **92.3%** (all subproject keys) | ✅ excellent |
| **Definition 1** (architectural episodes) | Do arch refactorings exist & how many? | **9 / 143 commits** (893 refactorings total); 0 cross-module at depth 4 | ✅ present but rare |
| **F1** estimate | Do tickets carry a time estimate? | **0 / 5** — field is `null` in Apache Jira | ❌ absent (data gap) |
| **F2** structural review | Does review discussion cite structure? | **2 / 5** in Jira, **5 / 5** if you count the linked PR | ⚠️ lives on the PR |
| **F3** clean link | Is the commit↔ticket link clean? | **5 / 5** | ✅ clean |

**Verdict: CONDITIONAL GO.** Traceability is excellent and episodes are detectable, but the
**estimate signal is absent** in Apache Hadoop (a *data* problem) and the **review signal lives on
the GitHub PR, not the Jira ticket** (a *modelling* problem). RQ1 is viable on hadoop only if the
signal is re-pointed to review-friction (mined from PRs) or a cycle-time overrun proxy — not explicit
estimates. Full reasoning + the 5-episode table: [worksheet.md](worksheet.md).

---

## Environment

- JDK: `openjdk 17.0.9` ✓
- Python: `3.9.6` ✓
- Repo: `hadoop/` — full clone, 28,290 commits, 942M history
- HEAD: `6f5d1374efb HDFS-11161. Incorporate Baidu BOS file system implementation.`

---

## Step 0-1 · Project choice + clone

hadoop was already cloned (full history — RefactoringMiner needs it).
hadoop is a **monorepo**: HADOOP, HDFS, YARN, MAPREDUCE are *separate* Jira
projects living in one git repo. This matters for the very next step.

## Step 2 · Citation rate (Filter 3) — the decisive probe

The README example uses a single key:

```bash
python3 scripts/citation_rate.py --repo hadoop --key HADOOP
# → Commits citing a key: 7404  (26.2%)
```

**26.2% looks like a warning** — but it's wrong for a monorepo. It only counts
`HADOOP-####` and ignores the HDFS/YARN/MAPREDUCE work that dominates the repo.

### Fix applied: multi-key support

I patched `citation_rate.py` and `filter_architectural.py` so `--key` accepts a
comma-separated list, joined into one regex alternation
(`\b(?:HADOOP|HDFS|YARN|MAPREDUCE)-\d+\b`). Single-key usage is unchanged
(backward compatible).

```bash
python3 scripts/citation_rate.py --repo hadoop --key HADOOP,HDFS,YARN,MAPREDUCE
```
```
Project key prefix : HADOOP, HDFS, YARN, MAPREDUCE
Commits scanned    : 28290
Commits citing a key: 26125  (92.3%)
  ...in the subject : 25889  (91.5%)
Distinct issue keys : 23823
```

**Real Filter-3 ceiling: 92.3%** (≈97.7% if you also count HDDS/YETUS).
hadoop is about as traceable as an OSS project gets — commons-lang's 17% is the
actual bad case. **Filter 3 → strong green.**

## Step 3 · Build RefactoringMiner

```bash
bash scripts/setup.sh
```
Builds a Python venv (pandas + lifelines for later survival modelling) and
compiles RefactoringMiner from source via Gradle. **✅ Done** — exit 0.
Binary verified: `./RefactoringMiner/bin/RefactoringMiner -h` lists `-bt`
(between-tags) mode, which is what the slice uses.

### First-pass range choice

The README example range `rel/release-3.3.0..rel/release-3.4.0` is **3,440
commits** (~hour+ for RM). For a week-1 *slice* that's overkill. I sized the
minor-version ranges:

| Range | Commits |
|---|---|
| 3.3.0 → 3.4.0 (README example) | 3,440 |
| **3.4.0 → 3.4.1 (chosen)** | **143** |
| 3.4.1 → 3.4.2 | 166 |
| 3.4.2 → 3.4.3 | 88 |

Chosen: **`rel/release-3.4.0..rel/release-3.4.1`** — a real result in minutes.
Widen only if the architectural-episode count comes out too thin.

### RM detect command (running)

```bash
./RefactoringMiner/bin/RefactoringMiner -bt hadoop \
    rel/release-3.4.0 rel/release-3.4.1 -json refminer_out.json
```
**✅ Done in 46s** — `[Commits: 143, Errors: 0, Refactorings: 893]`.
59 of the 143 commits carry ≥1 refactoring. Output: `refminer_out.json` (2.4 MB).

## Step 4 · Filter to architectural episodes (Definition 1)

```bash
source .venv/bin/activate
python3 scripts/filter_architectural.py --rm refminer_out.json \
  --repo hadoop --key HADOOP,HDFS,YARN,MAPREDUCE --module-depth 4
```

**9 candidate architectural episodes** out of 893 refactorings. The `--module-depth`
knob barely moves here — count is 9 at depth 3, 4, and 5; only the *cross-module* flag
changes (0 crossers at depth 3–4, 1 at depth 5). Type breakdown:

```
4  Extract Subclass    3  Move Class    3  Extract Class
1  Extract Superclass  1  Extract Interface  1  Move And Rename Class
```

### 🐛 Bug found & fixed: false 0% traceability

First run reported **0 / 9 traceable** — impossible against a 92% repo. Root cause:
`load_commit_keys()` ran `git log` with no ref, walking **only trunk** (28,290 commits).
The 3.4.x episodes live on the **release branch**, which is *not* an ancestor of trunk
(`git log --all` = 77,529 commits), so the sha→key map missed every episode.

**Fix (one flag):** walk `git log --all` when building the sha→key lookup. Re-ran →
**8 / 9 traceable (89%)**. The 1 miss is a lowercase `Hadoop-18759` typo; left as-is
because case-insensitive matching would false-match version strings like `hadoop-3.4.0`.

Also fixed earlier (Step 2): both scripts now accept a comma-separated `--key` for monorepos.

## Step 5 · Trace 5 episodes by hand → worksheet.md

Picked 5 traceable episodes spanning distinct arch types. Jira data pulled **live from the
public Apache Jira REST API** (the local Mongo dump isn't restored yet — not needed for 5):

```bash
curl -s "https://issues.apache.org/jira/rest/api/2/issue/HADOOP-18830?fields=summary,status,timeoriginalestimate,comment,..."
```

Per-episode F1/F2/F3 findings are in the filled-in [worksheet.md](worksheet.md). Headlines:
- **F1 estimate — 0/5.** Every ticket's `timeoriginalestimate` is `null`. HADOOP-18679 even
  says it out loud: *"no actual time allocated to implement it."* Apache doesn't estimate.
- **F2 review — structural discussion exists, but on the PR.** Human Jira comments cite
  structure clearly on only 2/5 (18679's interface design, 19205's init profiling). The
  substantive code review is relayed from GitHub PRs by `githubbot`. F2 requires PR mining.
- **F3 link — 5/5 clean.** Every commit subject cites its key (`HADOOP-####. …`).

## Step 6 · Decide → go/no-go

Written into [worksheet.md](worksheet.md): **CONDITIONAL GO.** Estimates are the killer
(data gap), not traceability. Re-point RQ1's signal to review-friction (PR-mined) or a
changelog cycle-time overrun proxy, or move to a corpus that mandates estimation.

---

## Reproduce the whole slice

```bash
# 0-2  pick + probe (decisive number)
python3 scripts/citation_rate.py --repo hadoop --key HADOOP,HDFS,YARN,MAPREDUCE
# 3    build RM (once) + detect on a small range
bash scripts/setup.sh
./RefactoringMiner/bin/RefactoringMiner -bt hadoop rel/release-3.4.0 rel/release-3.4.1 -json refminer_out.json
# 4    filter to architectural episodes
source .venv/bin/activate
python3 scripts/filter_architectural.py --rm refminer_out.json --repo hadoop \
  --key HADOOP,HDFS,YARN,MAPREDUCE --module-depth 4
# 5    trace: open each episode's HADOOP-#### on issues.apache.org, fill worksheet.md
```

## Step 7 · Pivot — mine the review signal (decision: F2 as primary)

The estimate signal (F1) is a dead end here, so RQ1 pivots to the review-discussion
signal (F2). Key enabler: **Apache's `githubbot` mirrors the whole GitHub PR review —
including inline "commented on code" comments — into the Jira ticket**, so F2 needs no
GitHub token, just the same Jira REST call. New script:

```bash
python3 scripts/pr_review_signal.py --selftest                 # classifier self-check
python3 scripts/pr_review_signal.py --episodes architectural_episodes.json --out review_signal.json
```

Result over all 8 traceable episodes:

```
KEY            review human  ci struct   F2
HADOOP-18830       16     2  14      3   YES
HADOOP-19047       37     3   7      6   YES
HADOOP-19098       18     2  19      1   YES   <- borderline (1 hit)
HADOOP-19102       40     2  18     18   YES
HADOOP-18679       48     5  21     19   YES
HADOOP-19205        4     1   2      3   YES
HADOOP-19120      141     2  45     29   YES
HADOOP-19221       28     5  19      7   YES
F2 structural-review present: 8/8
```

**F2 jumps from 2/5 (native Jira only) to 8/8 (PR-relay mined).** The review signal is
strong and fully minable from the public Jira API. Caveat: threshold is keyword-hit>0;
a proper codebook (structural-review vs. style/correctness) is the next modelling task,
and HADOOP-19098 (1 hit) shows why. Output: `review_signal.json`.

## Artifacts produced
```
refminer_out.json                 893 refactorings over 143 commits
architectural_episodes.json       9 candidate episodes (depth 4, key-annotated)
architectural_episodes_d{3,5}.json depth-sweep variants
review_signal.json                F2 review-discussion signal per episode (8/8 positive)
worksheet.md                      filled 5-episode trace + go/no-go
SLICE_LOG.md                      this log
.jira_cache/                      cached Jira REST responses (re-run without re-fetching)
```

## New script added in the pivot
- `scripts/pr_review_signal.py` — turns each episode's issue key into the F2 review
  signal by mining githubbot's PR-relay in the Jira comments (stdlib only, `--selftest`).

---

## Step 8 · Scale it — the real feasibility number (n=86, not n=8)

Widened from the 143-commit slice to the full **3.3.0 → 3.4.0** range (3,440 commits).

### Parallelising RefactoringMiner (M4 Pro, 12 cores)
RM is single-threaded — one `-bt` run pins 1 core (~8% of the machine). `scripts/run_rm_parallel.sh`
splits the range's first-parent mainline into N chunks and runs one `RM -bc` per chunk.
8 chunks → **784% CPU**, ~20 min → a few min. Two gotchas hit and fixed:
- **Annotated tags**: `git rev-parse rel/release-X` returns the *tag object*, which JGit rejects
  (`is not a commit`). Fix: `^{commit}`. (Only the tag-anchored end chunks failed; middle chunks
  used rev-list commit shas and were fine.)
- **RefactoringMiner hangs on jQuery/*.min.js dependency-bump commits** — it spins at 100% CPU
  forever. This is what silently froze the original single-threaded run at 547 commits.
  `RM -bc A B` is *inclusive of A*, so you can't route around a bad commit by using it as a
  boundary — RM still parses it. Pragmatic resolution: skip those regions and accept partial
  coverage (jQuery bumps have zero architectural refactorings, so nothing of interest is lost).

### Coverage
Merged 5 clean chunks + the completed skip-segments, deduped by sha, verified against
`git rev-list`: **3,175 / 3,440 commits = 92.3%** (the 265 uncovered are jQuery bumps and
their immediate neighbours). **17,817 refactorings.**

### Results at scale

| Metric | Slice (143 commits) | **Scaled (3,175 commits)** |
|---|---|---|
| Architectural episodes | 9 | **87** |
| Traceable to a ticket (F3) | 8/9 | **86/87 (99%)** |
| Cross-module moves | 0 | **8** |
| Package-level refactorings | 0 | Move/Rename/Split Package present |
| F1 estimate present | 0/5 | **0/86 (0%)** |
| F2 review cites structure (keyword>0) | — | **42/86 (49%)** |
| F2 strong (≥3 structural hits) | — | **17/86 (20%)** |

**The headline feasibility number:** of 87 detected architectural episodes, **99% are traceable**,
**0% carry an effort estimate**, and **~49% have some structural review discussion** (49% by a loose
keyword rule; **20%** show a strong signal). The 8/8 from the hand-picked slice was optimistic — it
sampled Steve Loughran's heavily-reviewed S3A work. At scale, many YARN/HDFS episodes have thin or
no review, so the real F2 rate is **half, not all** — and the true rate sits between 20% and 49%
depending on where the codebook draws the "structural argument vs. incidental mention" line.

### Artifacts added
```
refminer_wide.json                 17,817 refactorings, 3,175 commits (92.3% of range)
architectural_episodes_wide.json   87 episodes, 86 traceable
review_signal_wide.json            F2 signal per ticket, 86 episodes
scripts/run_rm_parallel.sh         N-way parallel RM (tag-range → chunks)
scripts/rm_skip_range.sh           RM over a range skipping hang-inducing commits
rm_chunks/                         per-chunk RM output + logs + exclude list
```

## Step 9 · Scale wider — self-healing runner, 4 ranges, the tightened number

To get n in the hundreds without babysitting RM's hangs, added a **self-healing runner**:

```bash
bash scripts/run_rm_safe.sh <repo> <start> <end> <N=16> <stall=150> out.json
```

Splits the range into many small chunks; a **watchdog kills any chunk whose log stalls for
`stall` seconds** (a pathological commit wedges only its small chunk, not the run). Merges the
survivors and reports coverage. Proven: on 3.1.0→3.2.0 it auto-killed one hung chunk (a jQuery
bump) and still delivered 83% coverage, unattended.

Ran 3 more ranges and merged with the 3.3.0→3.4.0 set:

| Range | Commits | Coverage | Refactorings |
|---|---|---|---|
| 3.1.0 → 3.2.0 | 2,229 | 83% (1 hang auto-killed) | 13,556 |
| 3.2.0 → 3.3.0 | 3,578 | 99% | 18,293 |
| 3.3.0 → 3.4.0 | 3,440 | 92% | 17,817 |
| 3.4.0 → 3.4.3 | 347 | 100% | 2,195 |
| **combined (dedup)** | **8,919** | — | **51,861** |

### Final feasibility number (n = 345 traceable episodes)

```
architectural episodes : 349
traceable (F3)         : 345/349 (99%)   [keys: HADOOP,HDFS,YARN,MAPREDUCE,HDDS,OZONE,SUBMARINE,YETUS]
cross-module moves     : 40
F1 estimate present    : 0/345  (0%)
F2 any (keyword>0)     : 215/345 (62%)
F2 strong (>=3 hits)   : 106/345 (31%)
```

**Bottom line unchanged, now firm:** traceability excellent (99%), estimates absent (0%), review
signal present in **31–62%** of episodes (true rate pending the codebook). Adding key prefixes was
essential — older episodes cite HDDS/Ozone/Submarine tickets that split out of Hadoop later; without
them F3 read a misleading 76%.

## Step 10 · From feasibility to a preliminary finding

With the signal decided (review discussion) and F2 calibrated to 31% (codebook labeling found the
keyword rule only 25% precise — `codebook_results.md`), tested whether the signal predicts an outcome.

**Outcome = ticket cycle-time (created→resolutiondate), unresolved right-censored.** Split episodes
by F2 (strong ≥3 structural mentions):

```
                       n     median resolve    median review size
structural review     106       67 days            30 comments
other                 239       23 days            10 comments
Kaplan-Meier log-rank test:  p = 0.0001
```

**Cox regression controlling for change size** (log refactorings, files, churn):
`F2 hazard ratio 0.66 (alone) → 0.69 (adjusted), p=0.003` — appeared to survive size.

### Step 10b · The result does NOT survive discussion-volume control (retracted)

Ran the obvious next robustness check — add discussion volume (log comment-count) as a covariate,
since structural episodes also have far more comments (median 30 vs 10; corr(F2, log-comments)=0.52):

```
Model                          F2 HR    95% CI          p
A. F2 alone                    0.66     [0.52, 0.84]    0.0006
B. + change size               0.69     [0.55, 0.88]    0.0029
C. + DISCUSSION VOLUME         1.10     [0.83, 1.46]    0.51    <- collapses
   discussion volume (in C):   0.70 per log-comment,    p≈1e-9  <- the real predictor
   structural DENSITY test:    struct_ratio HR 1.50,    p=0.26  <- also null
```

**The structural-review effect is confounded by discussion volume and does not stand.** The keyword
signal (≥3 structural mentions) is entangled with "this ticket had a lot of discussion"; once volume
is controlled, no structural-specific effect remains, and structural *density* is null too. What is
robust is that discussion volume predicts resolution time (partly mechanical). The hypothesis is
**untested, not disproven** — the 25%-precise keyword measure can't separate structural *content*
from discussion *quantity*; a validated, volume-independent codebook signal is required. Reported
deliberately: catching this before pitching is the point of the check.

### Artifacts added (Step 10)
```
.jira_meta/                 ticket dates/status/priority (created, resolutiondate)
episode_outcomes.json       per-episode cycle-time + F2 + resolved flag
cox_dataset.json            the modelling table (duration, event, f2, size covariates)
codebook_results.md         first-pass labeling + 25%-precision finding + F2 decision
research_prospectus.md      the 2-page proof-of-worth write-up (finding + method + plan)
```

### Artifacts added (Step 9)
```
refminer_{310_320,320_330,340_343}.json   per-range RM output
refminer_all.json                          8,919 commits, 51,861 refactorings (4 ranges merged)
architectural_episodes_all.json            349 episodes, 345 traceable
review_signal_all.json                     F2 signal, 345 episodes
scripts/run_rm_safe.sh                     self-healing parallel RM (watchdog-killed chunks)
codebook_labeling.md                       40 real comments to hand-label (2 raters → κ)
advisor_brief.md                           1-page decision memo for the group meeting
```

## What changed in the starter scripts
- `scripts/citation_rate.py` — `--key` now accepts comma-separated prefixes (monorepo support).
- `scripts/filter_architectural.py` — same multi-key support **+** `git log --all` fix for
  release-branch episodes (the 0%-traceable bug).
