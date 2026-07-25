# Era audit — which results depend on instruments that decay at the 2019–20 migration

Read-only. No analysis was re-run; every span below comes from the committed
Jira caches and result JSONs.

## The two decaying instruments

| instrument | ≤2018 | 2019–21 | ≥2022 |
|---|---:|---:|---:|
| **Jira status transitions** — architectural tickets reaching `Patch Available` | 147 of 150 | 98 of 130 | **6 of 43** |
| **CI verdicts** — architectural tickets carrying ≥1 Hadoop-QA comment | 145 of 150 (**96.7%**) | 66 of 130 (**50.8%**) | **0 of 43 (0.0%)** |

Corpus creation-year span: architectural **2013–2026** (n=323), ordinary control
**2013–2024** (n=400). Era composition: ≤2018 46.4% / 36.8%; 2019–21 40.2% /
47.8%; ≥2022 13.3% / 15.5%.

Sub-corpus spans actually available to status-based analyses:

| sub-corpus | architectural | ordinary |
|---|---|---|
| reached `Patch Available` | n=251, **2013–2024** (77.7%) | n=294, 2013–2023 (73.5%) |
| used `In Progress` | n=92, **2016–2024** (28.5%) | n=91, 2015–2023 (22.8%) |
| carries a CI verdict | n=211, **2013–2021** (65.3%) | not measured |

**The CI channel terminates in 2021.** Not "decays" — there is no architectural
ticket after 2021 with a CI verdict in Jira.

---

## Results that depend on Jira status transitions

Triage latency is *created → first status transition out of Open*, so every
result below inherits the status instrument.

| § | result | data actually used | spans 2019–20? |
|---|---|---|---|
| §4 | Primary finding: triage 4.6 vs 2.1 d, resolution 30.2 vs 15.5 d | all 323 / 400 tickets, **2013–2026** | ⚠️ **YES** |
| §5 | Abstraction vs relocation, triage 7.2 vs 2.8 d | 323 arch, **2013–2026** | ⚠️ **YES** |
| §5 (corrected) | Joint model, ×1.54 [0.97, 2.43] p=0.068 | n=319, **2013–2026** | ⚠️ **YES** |
| §5a | Phase decomposition: t_to_patch, t_review | reached-patch subset, **2013–2024**; only **6 arch tickets after 2021** | ⚠️ **YES** |
| §5a | Active coding time (In Progress) | n=92 arch / 91 ord, **2016–2024** | ⚠️ **YES** |
| §5a | Self-assignment 2.05 vs 31.66 d to patch | reached-patch subset, 2013–2024 | ⚠️ **YES** |
| §5b | Workflow comparability, 28.3% vs 86.2% | all tickets, 2013–2026 — **this result IS the instrument failure** | n/a (it measures it) |
| §5c | Secondary status-based DiD (+0.308, p=0.011) | status subset; dossier already flags 2.8% post-2022 | ⚠️ **YES**, already disclosed |
| §6 | Triage within sub-tasks (6.0 vs 2.1, p=0.051) | sub-task subset of 2013–2026 | ⚠️ **YES** |
| §6 | Experience vs triage (rho −0.19) | 2013–2026 | ⚠️ **YES** |
| §8 | Reopen rate ~7% | status history, 2013–2026 | ⚠️ **YES** |
| §9 | Module hotspots, ~40× triage variation | 2013–2026 | ⚠️ **YES** |
| §9a | Blast radius vs triage (rho −0.19); connector tier 43.6 vs 3.1 d | n=242 attributed, 2013–2026 | ⚠️ **YES** |
| §9b | Social centrality vs triage / t_to_patch / total | 2013–2026 | ⚠️ **YES** |
| §9c | Wrapper rule, 42.0 vs 3.1 d triage split | n=242, 2013–2026 | ⚠️ **YES** |
| §10 | Retracted Cox on resolution time | 2013–2026 | ⚠️ **YES** (already retracted) |

## Results that depend on CI verdicts

| § | result | data actually used | spans 2019–20? |
|---|---|---|---|
| §8a | CI rework: median 5 vs 3 runs, p<1e-4 | tickets with CI verdicts, **2013–2021 only** | ⚠️ **YES**, and **terminates at 2021** |
| §8a | Nested models to +0.092 (p=0.072) with change size | same | ⚠️ **YES** |
| §8a | Failure-rate instrument (86.7% of runs "fail") | same | ⚠️ **YES** |

The dossier already states §8a "is about the pre-2022 era only". This audit
sharpens that: the last architectural ticket with a CI verdict is **2021**, and
coverage was already down to **50.8%** across 2019–21, so the mid-window is
half-blind rather than merely thinner.

## Results that do NOT depend on either instrument

| § | result | instrument |
|---|---|---|
| §5c | **Primary** decade divergence, DiD +0.202 | git clock: ticket → first citing commit |
| §7 | Entanglement, issue-links 1.53 vs 0.76 | ticket property, no status |
| §8a | Change size, 1,178 vs 213 java lines | git |
| §3 | Traceability 99%; estimates 0/323 against a 1.449% Hadoop-corpus base rate | ticket fields, no status |
| §11 | Codebook keyword precision 25% | comment text |
| §9a | Blast radius itself (Maven graph) | poms |

## What this means

**Every timing result in the dossier except the §5c primary depends on the Jira
status field, and all of them span the migration.** The corpus is 46% pre-2018
and only 13% post-2022, so the pooled estimates are dominated by the era where
the instrument works — which is fortunate for validity and fatal for
generalisation to current practice.

Two specific exposures worth stating in the paper:

1. **§5a's phase decomposition rests on 6 architectural tickets after 2021.**
   The reached-patch sub-corpus nominally spans 2013–2024, but the post-2021
   tail is 6 tickets. Any claim that build-vs-merge behaviour *persists* is
   unsupported; the result is a statement about 2013–2021.
2. **§8a cannot be extended past 2021 by any amount of additional mining.** The
   verdicts are not sparse after 2021, they are absent. The dossier's follow-on
   suggestion — reverts and follow-up-fix commits from git — is the only route.

Neither is a new threat: §5b, §5c and §8a each disclose their own instrument
failure. What is new is that the exposure is **uniform across the dossier**
rather than confined to the three sections that discuss it.
