# Week-1 feasibility worksheet — trace 5 architectural episodes by hand

This is the real dry-run of the three-filter feasibility count, done manually on
just **5 episodes**. If the filters are survivable on 5, they're worth automating
on thousands. If they're not, you've learned that in a day, not a quarter.

Pick 5 rows from `architectural_episodes.json` (prefer ones with an `issue_key`).
For each, open the commit on GitHub and the ticket on the project's Jira, and fill in:

Traced on **hadoop**, range `rel/release-3.4.0..3.4.1` (2026-07-19). Jira data pulled
live from the public Apache Jira REST API (`issues.apache.org/jira/rest/api/2/issue/<KEY>`).

| # | Commit (sha1) | Arch refactoring type(s) | Cross-module? | Cited issue key | **F1: estimate present?** (value) | **F2: review discussion citing *structure*?** (where) | **F3: commit↔ticket link clean?** | Plausible signal→action story? (notes) |
|---|---------------|--------------------------|---------------|-----------------|-----------------------------------|-------------------------------------------------------|-----------------------------------|----------------------------------------|
| 1 | `91ba4848b36d` | Move Class | N | HADOOP-18830 | **N** — timeoriginalestimate `null` | **Partial** — thin structural rationale in Jira ("confuses everything above it"); real review on **PR #6144** | **Y** — key in subject | "Cut S3 Select": removes a layer that muddied the FS abstraction |
| 2 | `f2ea733732f1` | Extract Subclass ×2 | N | HADOOP-19047 | **N** — `null` | **Partial** — Jira = review coordination + perf rationale; structural review on **PR #6468** | **Y** | in-memory magic-commit tracking; skips a scan phase |
| 3 | `33bbcfa4b042` | Move Class | N | HADOOP-19098 | **N** — `null` | **Weak in Jira** — housekeeping only ("backport to 3.4/3.3"); review on **PR #6604** | **Y** | Vector IO range validation consistency |
| 4 | `2428368a7475` | Extract Interface | N | HADOOP-18679 | **N** — `null` (Loughran: *"no actual time allocated to implement it"*) | **Y** — explicit API/interface design in Jira (`DeleteOperationFactory` interface, builder pattern) | **Y** | new BulkDelete API; interface designed in-ticket |
| 5 | `b7630e2b36b9` | Extract Class ×2 | N | HADOOP-19205 | **N** — `null` | **Y** — profiler-driven analysis of init structure (`FileSystem.createFileSystem`) in Jira | **Y** | slow S3A init; class extracted to cut startup cost |

> **Cross-module?** at the canonical `--module-depth 4`, 0 / 9 episodes cross a top-level
> module boundary (1 / 9 does at depth 5). These strict-definition "architectural" moves
> are almost all *within* a module.

## Tally → go / no-go read

- **Survive all three filters (F1 ∧ F2 ∧ F3): 0 / 5** — F1 removes every one.
- Estimate present (F1): **0 / 5**   ·   Structural review found (F2): **2 / 5** in *native* Jira comments — but **8 / 8** once the PR-relayed review is mined (see below)   ·   Clean link (F3): **5 / 5**

> **F2 pivot, validated.** `scripts/pr_review_signal.py` mines the review discussion
> that `githubbot` mirrors from the GitHub PR into the Jira comments (incl. inline
> "commented on code" review). Run over all 8 traceable episodes: **8 / 8 contain
> structural review discussion** (struct-keyword hits 1–29, review comments 4–141).
> So F2 is a *strong* signal — it was just in the PR thread, not the ticket body.
> Output: `review_signal.json`. (Threshold is keyword>0; a real study needs a codebook —
> the 1-hit episode HADOOP-19098 is borderline. That codebook is the next modelling task.)

**Reading it:**
- **≥ 2–3 of 5 survive all three** → the study is viable on this project; scale the pipeline and start the real feasibility count.
- **Traceability (F3) is the killer** → switch to a project with an enforced commit-key convention (see `config.example.env`).
- **Estimates (F1) are the killer** → lean on review friction as the primary signal, or derive overruns from changelog cycle-time instead of explicit estimates.
- **Structural review (F2) can't be told apart from style/correctness** → that's a finding too: invest in the codebook, and if it stays fuzzy, the signal is pointing you toward human factors (→ RQ2).

### Scaled check — the real feasibility count (n=345, 4 release ranges)

The 5-episode trace above was hand-picked (heavily-reviewed S3A work) and read 8/8 on F2.
Scaling to **all 349 architectural episodes** across 4 release ranges (3.1.0 → 3.4.3, 8,919 commits;
see [SLICE_LOG.md](SLICE_LOG.md) Steps 8–9) gives the honest, unbiased number:

| Filter | Slice (n=5) | 1 release (n=86) | **4 ranges (n=345)** |
|---|---|---|---|
| F3 clean link | 5/5 | 86/87 (99%) | **345/349 (99%)** |
| F1 estimate | 0/5 | 0/86 (0%) | **0/345 (0%)** |
| F2 structural review (keyword>0) | 8/8 (cherry-picked) | 42/86 (49%) | **215/345 (62%)** |
| F2 strong (≥3 structural hits) | — | 17/86 (20%) | **106/345 (31%)** |

**Reading it:** F3 is a non-issue (99%). F1 stays dead (0%). F2 is present in **31% (strong) to 62%
(any mention)** of episodes — the true rate awaits the codebook (`codebook.md` + `codebook_labeling.md`).
RQ1's effective sample = (episodes) × (~0.3–0.6 with signal) × (0.99 traceable). Across these 4 ranges
that is **~100–215 usable episodes**; across full history (~28k commits) it scales to **many hundreds** —
ample for the survival models. The decision memo is `advisor_brief.md`.

### Verdict (this trace): **CONDITIONAL GO — the estimate signal is the killer, not traceability.**

Mapping onto the reading guide above:
- **F3 traceability is a non-issue.** 5 / 5 clean links; 92 % repo-wide. hadoop is excellent to mine.
- **Architectural episodes are detectable** but *rare and mostly within-module*: 9 in 143 commits (~6 %),
  0 cross-module at depth 4. Fine for a full-history mine (~1–2k episodes across 28k commits), thin per release.
- **F1 estimates are the killer (0 / 5).** Apache Hadoop does not record time estimates in Jira — the field is
  simply empty. This is a **data** problem for the estimate framing, and it will not improve by scaling.
- **F2 review-structure signal exists but lives on the GitHub PR, not the Jira ticket.** Human Jira comments
  are strong on structure for only 2 / 5; the substantive code review is relayed from the PR by `githubbot`.
  So F2 is a **modelling** problem: to use it you must ingest PR review comments, not just the Jira changelog.

**So RQ1 on hadoop is viable only if you re-point the signal** (per the guide's "estimates are the killer" branch):
1. **Primary signal = review friction / discussion structure**, mined from **PR review threads** (githubbot relay), or
2. **Overrun proxy = changelog cycle-time** (created→resolutiondate; e.g. these 5 ran 3 wk – 14 mo) instead of explicit estimates.

If RQ1 *fundamentally requires explicit effort estimates*, hadoop (and ASF projects generally) is the wrong corpus —
you'd need a commercial Jira that mandates estimation. That's the decision to take to the group.

## What to bring to Maalej from this
1. The citation-rate table: hadoop **92.3%** (multi-key) vs commons-lang 17% → mine hadoop. (Single-key HADOOP alone reads 26% — a monorepo trap; fixed in the scripts.)
2. This 5-episode worksheet — concrete evidence: **F3 ✅, episodes ✅ (rare), F1 ❌ absent, F2 ✅ but on the PR.**
3. Two decisions to settle together: the **module-boundary depth** (3/4/5 all give 9 here; depth only flips the cross-module flag) and the **estimate fallback** (cycle-time proxy vs. PR-review signal vs. different corpus).
