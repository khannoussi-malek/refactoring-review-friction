# RQ1 feasibility study — architectural refactoring & review friction in Apache Hadoop

This started as a week-1 "thin slice" starter kit. It grew into a feasibility study that established
a reproducible pipeline, ruled out the original signal, and **stress-tested a candidate result to the
point of retracting it.** This README explains what was done and what was (and wasn't) found; full
commands are in [SLICE_LOG.md](SLICE_LOG.md), the write-up in [research_prospectus.md](research_prospectus.md).

> **Headline finding:** Architectural refactorings are a distinct, higher-friction class of change.
> Vs. ordinary refactorings (323 vs 400 tickets), they draw more review discussion (14 vs 11 comments,
> p=0.0004), wait ~2× longer to be picked up (4.6 vs 2.1 days in triage, p=0.002), and take ~2× longer
> to resolve (30 vs 15 days, p=0.0003) — while engaging the same small core of maintainers. **Triage
> latency is the clean, volume-independent evidence** (it happens before any discussion). Chart:
> `figures/arch_vs_ordinary.png`.
>
> *(A separate within-episode signal — structural review discussion → slower resolution — was found,
> stress-tested, and **retracted** as a discussion-volume confound. See below; the rigor is part of the
> story.)*

---

## What we found

Measured on **8,919 Hadoop commits** (4 release ranges, 3.1.0 → 3.4.3), **349 architectural episodes**:

| Filter (RQ1's chain) | Question | Result | Verdict |
|---|---|---|---|
| **F3** traceability | commit → Jira ticket? | **345/349 = 99%** | ✅ excellent |
| **F1** effort estimate | ticket carries an estimate? | **0/345 = 0%** | ❌ absent in Apache |
| **F2** structural review | review argues about structure? | **31%** (operational) | ⚠️ present, selective |

Three things this study established:

1. **The original framing was wrong.** RQ1 assumed *effort estimates* as the signal. Apache records
   **none** — the field is empty on all 345 tickets ("*no actual time allocated to implement it*").
   No amount of data fixes this; it's a property of the process.
2. **A better signal exists and is minable.** *Structural review discussion* lives on the GitHub PR,
   which Apache's `githubbot` mirrors into the Jira ticket — so it's reachable from the public Jira
   API, no GitHub token. Present in ~31% of episodes (the naive keyword rule says 62%, but a codebook
   check found it only 25% precise — see [codebook_results.md](codebook_results.md)).
3. **Architectural refactorings are measurably higher-friction than ordinary ones** (the positive
   result). Vs. a 400-ticket ordinary-refactoring control: more review discussion (14 vs 11, p=0.0004),
   ~2× longer triage before pickup (4.6 vs 2.1 days, p=0.002), ~2× longer resolution (30 vs 15 days,
   p=0.0003), same small core of reviewers. **Triage latency is volume-independent** (it precedes the
   discussion), so it isn't the confound below.
4. **A within-episode signal was tested and retracted.** "Structural review discussion → slower
   resolution" held under a change-size control (Cox HR 0.69, p=0.003) but **collapsed under a
   discussion-volume control** (HR 1.10, p=0.51). The keyword signal is entangled with sheer discussion
   volume, which is the real predictor. Reported honestly — catching this is part of the contribution.

**Net:** a positive between-group finding (architectural refactoring is a distinct, costlier class),
two supporting results (estimates absent; friction ≈ discussion volume), and a reproducible pipeline.
Full detail: [results_dossier.md](results_dossier.md); threats to validity there and in the prospectus.

## What we did (the pipeline)

```
citation probe ─▶ detect refactorings ─▶ filter to architectural episodes ─▶ mine review signal ─▶ survival analysis
   (Filter 3)        (RefactoringMiner)         (Definition 1)                  (F1/F2 per episode)     (Cox / KM)
```

1. **Picked the project by traceability.** `citation_rate.py` — Hadoop cites a Jira key in **92.3%**
   of commits (multi-key: the repo is a monorepo, so a single `HADOOP` key misleadingly reads 26%).
2. **Detected refactorings at scale.** RefactoringMiner is single-threaded, so
   `run_rm_parallel.sh` / `run_rm_safe.sh` split each release range into chunks across 8–16 cores.
   RM hangs on minified-JS dependency bumps; the self-healing runner's watchdog auto-kills and skips
   those (they hold no architectural refactorings). 90–99% coverage per range → **51,861 refactorings**.
3. **Filtered to architectural episodes.** `filter_architectural.py` keeps package-level and
   cross-package refactorings → **349 episodes** (incl. 40 cross-module + Move/Rename/Split Package).
4. **Mined the signals.** `pr_review_signal.py` reads each ticket's review discussion from Jira
   (githubbot PR relay), scoring structural content; a codebook (`codebook.md`) calibrates it.
5. **Ran the analysis.** Cycle-time by F2, Kaplan–Meier + log-rank, then a Cox model controlling for
   change size.

## Reproduce

The `hadoop/` clone and all large outputs are **not** in this repo (see `.gitignore`) — they're
external or regenerable. The committed `*.json` results are the findings; regenerate the rest with:

```bash
# 0    get the corpus (not committed — it's a 1.2 GB upstream clone)
git clone https://github.com/apache/hadoop.git

# 1-2  environment + the decisive traceability probe
bash scripts/setup.sh                      # builds RefactoringMiner + Python venv (JDK 17, Python 3.9)
python3 scripts/citation_rate.py --repo hadoop --key HADOOP,HDFS,YARN,MAPREDUCE

# 3    detect refactorings over a release range (self-healing, uses all cores)
bash scripts/run_rm_safe.sh hadoop rel/release-3.3.0 rel/release-3.4.0 16 150 refminer_wide.json

# 4    filter to architectural episodes (multi-key for the monorepo + Ozone/HDDS)
source .venv/bin/activate
python3 scripts/filter_architectural.py --rm refminer_wide.json --repo hadoop \
  --key HADOOP,HDFS,YARN,MAPREDUCE,HDDS,OZONE,SUBMARINE,YETUS --module-depth 4

# 5    mine the F2 review signal per episode (public Apache Jira, cached)
python3 scripts/pr_review_signal.py --episodes architectural_episodes.json --out review_signal.json
```

## Key documents

| File | What it is |
|---|---|
| [research_prospectus.md](research_prospectus.md) | **The 2-page write-up** — finding, method, threats, plan |
| [SLICE_LOG.md](SLICE_LOG.md) | Full reproducible run log, every command + the RM-hang saga |
| [worksheet.md](worksheet.md) | The manual 5-episode trace + go/no-go, then the scaled n=345 check |
| [codebook.md](codebook.md) · [codebook_results.md](codebook_results.md) | F2 definition + first-pass labeling (keyword is 25% precise) |
| [codebook_labeling.md](codebook_labeling.md) | 40 real comments to dual-rate (κ) — the open next step |

## Files

```
scripts/
  citation_rate.py          Filter-3 probe: % commits citing an issue key (multi-key)
  setup.sh                  build RefactoringMiner + Python env
  run_refactoringminer.sh   single-threaded RM (original starter)
  run_rm_parallel.sh        N-way parallel RM (tag range → chunks)
  run_rm_safe.sh            self-healing parallel RM (watchdog skips hang-inducing commits)
  rm_skip_range.sh          RM over a range excluding specific commits
  filter_architectural.py   RM output → candidate architectural episodes (multi-key, --all branches)
  pr_review_signal.py       episode → F2 review signal, mined from githubbot's PR relay in Jira

data (generated)
  refminer_all.json               51,861 refactorings, 8,919 commits (4 ranges merged)
  architectural_episodes_all.json 349 episodes, 345 traceable
  review_signal_all.json          F2 signal per ticket
  episode_outcomes.json           per-episode cycle-time + F2 + resolved flag
  cox_dataset.json                the survival-model table
  .jira_cache/ .jira_meta/        cached Jira responses (comments; dates/status)
```

## What a full study adds (RQ1 proper)

Validate the codebook with a second rater (Cohen's κ — set is ready in `codebook_labeling.md`),
replace cycle-time with better changelog-derived effort proxies, add covariates + clustering to the
survival model, and replicate on Kafka/HBase/Camel for generality. The public Jira dump (Zenodo
record 15719919) supplies the full changelog history when you scale beyond the live API.
# refactoring-review-friction
