# Project state — decision log

Internal record. `README.md` is the outward-facing account. This exists so a
future session can reconstruct *why* without re-reading chat. Every row carries a
commit hash or is marked `[undocumented]`.

## 1. Current state

RQ1's first operationalisation (effort estimates) is tested and closed; the
second (review discussion) was retracted as a volume confound. The methods paper
— traceability and estimate coverage as corpus-eligibility constraints — is near
complete and is the only shippable output. The RQ1 successor design (SATD
comment → architectural refactoring interval) is unstarted and gated on Task 18,
which decides whether entity tracking across Move Class / Move Package is
achievable at all. Blocking: external judgement on whether the SATD novelty
margin justifies a registered report, and a branch layout decision.

## 2. Decision log

| Date | Decision | Evidence | Commit | Reversed? |
|---|---|---|---|---|
| 07-19 | Corpus = Apache Hadoop, 8,919 commits, RefactoringMiner | `results_dossier.md` §2 | `de657c3` | no |
| 07-19 | **Retract structural-review finding** — Cox HR 0.69 (p=0.003) → HR 1.10 (p=0.51); discussion volume is the real predictor | `results_dossier.md` §10 | `b8d1476` | **yes — reversal of `4e84bcf`** |
| 07-19 | Adopt arch-vs-ordinary as primary finding | `results_dossier.md` §4 | `475fb5b` | superseded by `4b8c3af` |
| 07-22 | Split architectural work into abstraction vs relocation — defined *after* seeing §4 triage numbers, so post-hoc | `results_dossier.md` §5 | `22ec902` | qualified by `4b8c3af` |
| 07-22 | **Kill blast radius** — centrality does not predict triage, p=0.33 with tier controlled, raw association negative | `results_dossier.md` §9a | `6d1ed8d` | no |
| 07-22 | **Kill maintainer concentration** — collinear with module size, rho = −0.86 | `results_dossier.md` §9b | `93056ae` | no |
| 07-22 | Phase decomposition: friction is in building, not merging | `results_dossier.md` §5a | `986a3ae` | qualified by `4b8c3af` |
| 07-22 | Decade divergence via workflow-independent git clock | `results_dossier.md` §5c | `a6accaf` | qualified by `4b8c3af` |
| 07-22 | **Retract start-ui-web rework finding** — "commits per PR" is a duration proxy, not rework | `SUI_FINDINGS.md` | `1b51128` | **yes — reversal of `1ecbbee`** |
| 07-22 | Chunk-loss bias hypothesis rejected; lost commits are *smaller* | `SUI_FINDINGS.md` | `4839cd4` | no |
| 07-25 | **Full-adjustment pass**: abstraction ×1.54 [0.97, 2.43] p=0.068 — five nested models were never one equation | `full_adjustment.json` | `4b8c3af` | **yes — weakens `22ec902`** |
| 07-25 | **Withdraw "abstraction pays twice"** — review-phase half p=0.61 adjusted | `results_dossier.md` §5a | `4b8c3af` | **yes — reversal of `986a3ae`** |
| 07-25 | **Decade trend bounded** — post-2020 p=0.44, control arm 394 → 145 → 101 | `full_adjustment.json` | `4b8c3af` | **yes — bounds `a6accaf`** |
| 07-25 | Freeze tier rule at vendor share ≥0.40 + 90th-pct dependents guard | `scripts/external_wrapper_tier.py` | `314845c` | no — frozen by design |
| 07-25 | Pre-register held-out predictions before any outcome data | `predictions/PREDICTIONS.md` | `ca076a9` | no |
| 07-25 | **Hold the 0.40 threshold during the failed replication.** Lowering it would have rescued HBase (max 0.33) and Phoenix; not lowered | `replication/REPLICATION.md` | `48caf14` | no — deliberate |
| 07-25 | **Kill the tier rule** — 0 of 3 replicate (Hive p=0.210, Drill p=1.000 wrong direction, Kylin p=0.310) | `replication/*.test.json` | `48caf14` | no |
| 07-25 | **Abandon dependency-based tier rules entirely** — v2 scored 0.608 pooled vs v1's 0.617 on its own development data | `wrapper_rule_v2_dev.json` | `0216b64` | no |
| 07-25 | **Decline to run ICC on four clusters** — between-cluster variance not estimable at n=4; must come from the pooled study as a first stage | `[undocumented]` — reasoning is in chat only; `replication/CORPUS_FEASIBILITY.md` states the ICC *requirement* but not the refusal | `0a81339` | no |
| 07-25 | Corpus eligibility: 12 of 38, all Hadoop-ecosystem | `paper/traceability_probe.json` | `0a81339`, `b878131` | no |
| 07-25 | **Freeze Jira caches rather than write a rebuild script** — Jira is live, a re-fetch returns different state, so a rebuild script would imply reproducibility that does not exist | `deposit/MANIFEST-v1.md` | `ce4bf7d` | no |
| 07-25 | **Do not rewrite dated working logs** (`SLICE_LOG.md`, `worksheet.md`, `advisor_brief.md`) — they record what was believed when; rewriting would falsify the record | `README.md` §10 | `eee902f` | no |
| 07-25 | Drop `lifelines`; pin requirements from actual imports | `requirements.txt` | `dd27103` | no |
| 07-25 | **Estimate conclusion was drawn at the wrong aggregation level** — "absent in Apache" replaced by 2.557% Apache-wide / 1.449% Hadoop corpus / 0 of 323 architectural (expected 4.7, P≈0.009) | `estimates_by_org.json` | `eee902f` | **yes — reversal of `de657c3` §3** |
| 07-25 | Read the mongodump archive as a stream rather than restoring it (~60 GB expanded vs 10.5 GB free) | `scripts/jira_archive.py` | `eee902f` | no |
| 07-25 | **Switch RQ1 from tier rule to SATD-interval design** — dependency channel closed, tier rule dead, estimate signal too thin | `paper/SATD_NOVELTY.md` | `5b50ef1` | no |
| 07-25 | Record the SATD novelty risk as three simultaneous legs, any one of which collapses it | `paper/SATD_NOVELTY.md` | `5b50ef1` | no |
| 07-25 | Entity identifiers recoverable from `refminer_all.json` without re-mining 8,919 commits | `paper/ENTITY_IDENTIFIERS.md` | `2259129` | no |
| 07-25 | Project count: report 1,276 (key-based) / 2,506 (name-union) / 1,822 (published, not reproducible); never quote 1,822 beside a per-project number | `paper/numbers.md` | `0f116aa` | no |
| 07-25 | **id→key measured: 0 ids carry >1 key, 0 keys map to >1 id, against 326 ids with >1 name.** Supersedes the earlier key-vs-name framing: keys are 1:1 with ids *within a snapshot*, and the multi-key requirement is caused by concurrent siblings or superseded records, not key instability | `paper/eligibility_failure_modes.md` mode 6 | `5179907` | **yes — supersedes the `0f116aa` framing** |
| 07-25 | Attic skew is on the estimate dimension, not traceability: 9/23 estimate-ranked Apache in Attic, 5/8 among ≥10%; traceability skew n.s. (Fisher p=0.229) | `paper/intersection.json` | `5179907` | no |
| 07-25 | Estimate × traceability intersection: 3 of 27 clear both; 4 of 27 clear traceability at all | `paper/intersection.json` | `63f4231` | no |

## 3. What is held out and why

**Rule: outcome data unobserved. Coverage and existence counts permitted.**
A citation rate, a ticket count or an estimate-field count says nothing about how
long anything took; a triage latency, resolution time or status duration does.
Observing an outcome spends the project.

| project | observed | NOT observed |
|---|---|---|
| Ozone, Tez, ZooKeeper, Ranger, Oozie, Knox, Sqoop | commit-side traceability; ticket-side coverage; GitHub-ref counts | any timing, latency or status duration |
| **HBase, Phoenix** | as above, **plus `replication/{hbase,phoenix}.{git,jira}.json` are committed** — first-citing-commit timestamps and ticket creation dates | no timing statistic was ever computed or printed; no `.test.json` exists for either |

**HBase and Phoenix are at risk.** Their committed `git.json` + `jira.json` are
one subtraction apart from per-ticket latencies. No outcome was observed — the
frozen rule flagged zero modules, so the test stage never ran — but a future
session could spend them by accident. Decision pending on whether to drop them to
a seven-project held-out corpus (`5179907` records the flag, not a resolution).

## 4. What was spent

| project | what was observed | artifact |
|---|---|---|
| **Hadoop** | everything — triage, resolution, phase durations, CI verdicts, module medians | `results_dossier.md` |
| **Hive, Drill, Kylin** | per-module median days-to-first-commit; full replication test | `replication/{hive,drill,kylin}.test.json` |
| **27 estimate-ranked projects** | commit-side traceability, both reference channels, HEAD sha. **No timing.** | `paper/intersection.json` |

The 27: Apache STDCXX, USERGRID, MESOS, IOTDB, MXNET, SLIDER, LIBCLOUD, SHINDIG,
AURORA, MATH, TRINIDAD, REEF, MAHOUT, OPENNLP, OWB, CONNECTORS, AXIS2, CMIS,
OPENJPA, LANG, HAMA, THRIFT, DATALAB; RedHat PLANNER; IntelDAOS DAOS; MongoDB
EVG; Spring BATCH. These are spent for *traceability* purposes only — their
outcomes remain unobserved, so they are still usable as held-out data for a
timing study.

## 5. Open decisions

| decision | state |
|---|---|
| Branch layout — four branches separating methods paper / SATD design / exploratory Hadoop | proposed, awaiting decision; nothing created. Constraint: `ca076a9` must remain an ancestor of `48caf14` or the pre-registration evidence is destroyed |
| Whether the three-legged SATD novelty margin justifies a registered report | awaiting external judgement; literature search cannot settle it (`5b50ef1`) |
| Which RQ1 design proceeds | gated on Task 18 |
| HBase/Phoenix held-out status | flagged, unresolved |

## 6. Outstanding tasks

| task | gating |
|---|---|
| **16** — Flink truncation test (first 12,419 commits, matching SEOSS 33) | none. `paper/numbers.md` §1b currently asserts the 24.1pp gap is "scope, not error" and flags it untested. Clone on disk, ~10 min |
| **18** — entity-tracking prototype, 10 cases | none. Decides whether the entity-level leg of the SATD design is achievable |
| **14** — SATD feasibility count | gated on 18 passing |

## 7. Corrections made to own work

| what was reported | what was true | commit |
|---|---|---|
| "Survives size, volume, experience, tier and era controls" | Five nested models in three scripts, never one equation, no CI ever reported. Joint model ×1.54 [0.97, 2.43], p=0.068 | `4b8c3af` |
| "Abstraction pays twice" — ~2× review cost, p=0.0003 | Connector-controlled only; fully adjusted p=0.61 | `4b8c3af` |
| Decade divergence as a decade-long trend | Holds to 2019; post-2020 p=0.44 | `4b8c3af` |
| "12 of 34 projects pass"; TomEE listed twice (23.8% and 32.2%) | 38 probed; 23.8% was single-key, 32.2% multi-key | `abdfb40` |
| Probe discrepancies at knox (84.3→84.4) and helix (10.5→10.4) attributed to HEAD advancing | My own double-rounding: `round(rate,4)` then `.1f`. Identical HEAD, identical counts | `da74465` |
| ShardingSphere "not one Jira citation" in 49,109 commits | 5 citations in 49,111 (0.01%) | `6e6586e` |
| "Effort estimates absent in Apache (0%)" | 2.557% Apache-wide, 1.449% Hadoop corpus, 0/323 architectural — a deficit, not an absence | `eee902f` |
| "observing 0 is unsurprising (P≈0.009)" | Self-contradictory: P=0.009 *is* the deficit | `eee902f` |
| 0/345 as the estimate denominator | 345 is episodes; 323 is tickets, and an estimate is a ticket property | `9b4e384` |
| "394 → 101 control-arm collapse" paired with post-2020 p=0.44 | Two different windows: 394 (2016+), 145 (2020+), 101 (2021+) | `53826c8` |
| Step 2: `kiegroup/optaplanner` "misresolved, build-config repo" | HTTP-redirects to `apache/incubator-kie-optaplanner`; identical history, PLANNER 1,629 both. Verdict came from reading 20 post-archive CI commits | `63f4231` |
| **`paper/estimate_field_schema.md` reported as written** | Did not exist. Created later | `eee902f` |
| **`estimates_by_org.json` reported as committed with per-project data** | Committed copy had an empty `projects` map; the 1,276 entries were uncommitted | `dcea7c0` |
