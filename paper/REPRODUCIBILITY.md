# Reproducibility check — fresh clone, clean directory

Performed 2026-07-25 against repo state `d3177c9`. The repository was cloned
into an empty directory and the traceability probe was run end to end on one
project, with no reuse of the working environment.

## Result: the probe reproduces exactly

```
git clone <repo> fresh && cd fresh
git clone --filter=blob:none --no-checkout https://github.com/apache/flume.git flume-probe
python3 scripts/citation_rate.py --repo flume-probe --key FLUME
```

| | recorded | fresh clone | |
|---|---:|---:|---|
| Flume traceability | 73.9% | **73.9%** (1,540 / 2,084) | ✅ exact |

Flume was chosen because it is a **dropped** project — no held-out project was
touched — and because its commits-scanned figure was one of six missing from
`paper/numbers.md` §1. The check filled that gap as a side effect.

Cost: **6 seconds, 4.2 MB.** `--no-checkout` matters — the traceability probe
needs commit messages only, so a working tree is pure waste. The original sweep
cloned working trees for 22 of 38 projects and did not need to.

## What worked with no setup at all

`scripts/citation_rate.py` imports only `argparse, re, subprocess, sys,
collections`. It runs on **system `python3` with no virtualenv and no installed
packages**. For the traceability paper specifically, this is the whole pipeline,
and it is genuinely one command.

No absolute paths are hardcoded anywhere in `scripts/` — a grep for `/Users/`,
`/tmp/` and `/private/tmp` across every script returns nothing. All defaults are
repo-relative (`.jira_changelog`, `architectural_episodes_all.json`, …).

## Undeclared dependencies

**There is no `requirements.txt`, `pyproject.toml`, or `setup.py`.**

`scripts/setup.sh` installs `pandas` and `lifelines` only. The scripts actually
import:

| package | installed by setup.sh? | used by |
|---|---|---|
| `pandas` | ✅ | most analysis scripts |
| `lifelines` | ✅ (but nothing imports it any more) | — dead dependency |
| `numpy` | ❌ transitively via pandas | nearly everything |
| `scipy` | ❌ **missing** | every significance test |
| `statsmodels` | ❌ **missing** | every OLS / VIF |
| `matplotlib` | ❌ **missing** | every figure |
| `pymongo` (for `bson`) | ❌ **missing** | `jira_estimates.py` |

So a fresh clone reproduces the **traceability probe** but not the statistical
analyses. Fix is one file:

```
pandas numpy scipy statsmodels matplotlib pymongo
```

`lifelines` should be dropped — survival analysis was abandoned when the Cox
result was retracted, and nothing imports it.

## Manual steps and missing inputs

A fresh clone does **not** contain, and cannot regenerate without extra work:

| missing | needed by | how to obtain |
|---|---|---|
| `.jira_cache/`, `.jira_changelog/`, `.jira_props/`, `.jira_assignee/`, `.jira_control/` | every Hadoop analysis script | re-fetch from the Apache Jira API; **no script in the repo does this end to end** |
| `hadoop/` clone | `temporal_trend.py`, `blast_radius_model.py`, `ci_rework.py` | `git clone https://github.com/apache/hadoop` |
| `corpora/` | `replication/outcomes.py` | commands are in `replication/REPLICATION.md` |
| `RefactoringMiner/` | refactoring detection | `scripts/setup.sh` builds it (needs JDK 17+, Gradle, several minutes) |
| `ticket_first_commit.json`, `ticket_change_size.json`, `module_commit_log.json` | temporal / size / centrality analyses | derived caches, regenerated on first run **if** `hadoop/` is present |
| Maven | `replication/effective_deps.py` inputs | **not a system install** — local `apache-maven-3.9.9` binary, `MVN_BIN` env var |

The most serious gap is the **Jira caches**. They are gitignored, they are the
input to every statistical result in the dossier, and the repo has no
single script that rebuilds them from the API. Re-running the study from a fresh
clone is therefore not currently possible without reconstructing that fetch step.

## Recommended fixes, in priority order

1. **Add `requirements.txt`** (six packages, one line each). Cheapest fix, unblocks
   every analysis script.
2. **Add a `fetch_jira.py`** that rebuilds `.jira_*` from the API for a given
   project and key list. Without it the repo is not independently runnable.
3. **Add `--out` to `citation_rate.py`** so the traceability sweep writes a JSON
   artifact instead of stdout only (see `paper/numbers.md` §8 — this is why six
   projects' figures are currently unrecoverable).
4. **Drop `lifelines`** from `setup.sh`; add the six real dependencies there too.
5. Document `MVN_BIN` in `README.md`, not only in `replication/REPLICATION.md`.
