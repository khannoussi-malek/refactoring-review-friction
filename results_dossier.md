# RQ1 study — full results dossier (for proposal improvement)

*Complete, honest hand-off of everything the preliminary study found. All numbers are exact. This
supersedes earlier partial versions. For an AI agent improving the proposal: the **refined finding
(§5)** is the recommended headline; the **retraction (§10)** and **open-source caveat (§12)** are
central, not footnotes — do NOT resurrect the retracted result or oversell beyond what each number
supports.*

Repo: `khannoussi-malek/refactoring-review-friction` (private). Corpus: Apache Hadoop. Independent
pre-PhD pilot to establish feasibility and demonstrate method.

---

## 1. Research question

**RQ1:** Do architectural refactorings carry measurably more development friction than ordinary
changes, and what is the shape of that friction? (Reframed after the original *effort-estimate* signal
proved unusable — see §3.)

## 2. Method

- **Corpus:** 8,919 commits, Hadoop v3.1.0 → v3.4.3 (four release ranges), spanning Mar 2018 – Feb 2026.
- **Detection:** RefactoringMiner, parallelized 8–16× with a self-healing runner that auto-skips
  commits it hangs on (minified-JS bumps); 90–99% coverage. Output: **51,861 refactorings**.
- **Architectural episodes:** package-level + cross-package structural refactorings → **349 episodes**
  (323 unique tickets; some tickets carry >1 architectural commit).
- **Control group:** 400 *ordinary* refactoring tickets for the primary comparison.
- **Signals from public Apache Jira:** review discussion (githubbot PR relay), ticket dates, the full
  **status changelog** (Open→In Progress→Patch Available→Resolved), and ticket properties
  (priority, issue type, components, issue-links, assignee).

**Scale of the pipeline** (architectural refactoring is rare — 349 of 51,861 refactorings):

![study funnel](figures/study_funnel.png)

## 3. Feasibility

- **Traceability 99%** (345/349 episodes cite a Jira key) — but only when every monorepo subproject key
  is matched (HADOOP/HDFS/YARN/MAPREDUCE/HDDS/Ozone/Submarine); a single-key probe misreads it as 26%.
- **Effort estimates 0%** (0/345) — absent in Apache, which killed the original framing.

## 4. Primary finding — architectural refactorings are a distinct, higher-friction class

**323 architectural** vs **400 ordinary** refactoring tickets (medians; Mann–Whitney).

| Measure | Architectural | Ordinary | p |
|---|---|---|---|
| Review comments | 14 | 11 | 0.0004 |
| **Triage latency** (days in Open before pickup) | **4.6** | **2.1** | 0.0016 |
| Resolution time (days) | 30.2 | 15.5 | 0.00028 |
| Distinct participants | 3 | 3 | 0.18 (n.s.) |

More discussion, ~2× longer to start, ~2× longer to resolve — same small core of maintainers.
**Triage latency is the anchor** (measured before discussion → not a discussion-volume artifact).

![architectural vs ordinary](figures/arch_vs_ordinary.png)

## 5. Refined finding (RECOMMENDED HEADLINE) — the friction is in *abstraction*, not relocation

Splitting architectural episodes by *what they do*:

![abstraction gradient](figures/abstraction_gradient.png)

| Measure | Relocation-only (move/rename) | **Abstraction (extract interface/superclass/class)** | p |
|---|---|---|---|
| Triage latency (days) | 2.8 | **7.2** | 0.0036 |
| Resolution time (days) | 18.0 | **34.5** | 0.0001 |

**Relocating code is no harder than ordinary work (2.8 vs ordinary 2.1 days); introducing new
abstractions is ~2.5× slower to start and ~2× slower to resolve.** The abstraction effect **survives
controlling for change size and discussion volume** (OLS on log-triage: coef +0.55, **p = 0.013**).
Mechanism: creating a shared abstraction is a larger design commitment → developers hesitate to start.

This also explains an **inverted cross-module result**: cross-module moves (which are *relocations*)
are actually the *fastest* (triage 1.0 day) — so crossing a module boundary is not what makes work
hard; the abstraction is.

## 6. Alternative explanations ruled out

- **Priority:** similar in both groups (Major 82% arch vs 75% ordinary) — not the cause.
- **Issue type:** architectural work is 63% sub-tasks / 11% bugs vs ordinary 44% / 31% — a real
  difference (planned structural work, not bug-driven), *controlled for* in §5.
- **Discussion volume:** controlled (§5); abstraction survives.
- **Contributor experience / staffing:** architectural work goes to *more active* contributors
  (assignee handled median 9 vs 5 of our tickets, p<0.0001), and more-active contributors have
  *shorter* triage (rho −0.19, p=0.001). So the delay is **not** "waiting for a rare expert" — capable
  people own this work and it *still* stalls. Rules out the staffing objection.
- **Strictest control** (triage within sub-tasks only): borderline, 6.0 vs 2.1 days, p=0.051 — the
  effect is robust in direction/magnitude but modest under the tightest control. Honest verdict: real,
  consistent, not a slam dunk; does NOT collapse the way the retracted signal did.

## 7. Second, volume-independent finding — entanglement

Architectural tickets link to ~2× more other issues (issue-links mean **1.53 vs 0.76, p = 0.001**),
and this **holds within sub-tasks** (1.55 vs 0.73, p=0.003). Issue-links are a structural ticket
property, not built from discussion → immune to the volume confound. Architectural changes are more
tangled into the surrounding web of work.

## 8. Outcome quality — a clean NULL (informative)

Rework does **not** differ: reopen rate ~7% across ordinary / relocation / abstraction (p=0.97);
review rounds 0.97 / 1.04 / 1.39 (p=0.79). **Abstraction work is slower but not buggier** — the
friction is time/effort, not error-proneness. (Note: our sample is survivorship-biased toward changes
that landed, so *abandonment* is not measurable here.)

## 9. Module hotspots — friction concentrates in the foundation

Median triage latency by top-level project (architectural tickets):

![module hotspots](figures/module_hotspots.png)

| Module | Arch tickets | % abstraction | Median triage |
|---|---|---|---|
| HDFS | 96 | 56% | **1.0 day** |
| HDDS (Ozone) | 72 | 60% | 3.8 days |
| YARN | 75 | 77% | 7.1 days |
| **HADOOP (common)** | 73 | 68% | **39.1 days** |

**~40× variation.** Architectural work in `hadoop-common` — the shared foundation everything depends
on — stalls ~39 days vs ~1 day in HDFS. Interpretation: **blast radius** — the more depended-upon the
module, the more hesitation before touching its structure. (Small modules MAPREDUCE/SUBMARINE omitted
as noisy.)

## 10. Retracted result — a within-episode signal that was a volume confound

We tested whether, *among* architectural episodes, more *structural review discussion* predicts slower
resolution.

![retraction](figures/retraction.png)

Apparent effect (Cox HR 0.69, p=0.003, robust to change size) **collapsed** when
discussion volume was added (HR **1.10, p=0.51**). Discussion volume is the real predictor (HR 0.70
per log-comment, p≈1e-9); structural *density* is null (p=0.26). Reported deliberately — catching this
before it became a claim is part of the contribution.

## 11. Measurement validity — the keyword signal is weak

First-pass codebook labeling (single rater) of 40 comments: keyword **precision ≈ 25%** for
"structural" (5/20 flagged comments genuinely structural), miss ≈ 5%. The naive 62% "structural
review" rate is inflated; a validated, dual-rated (κ) classifier is needed to use this signal.

## 12. Open-source context — threat to validity AND a reframing (IMPORTANT)

Much of the measured "friction" reflects **how open-source coordinates work**, not universal software
behavior:
- **Triage latency** in OSS is largely *"how long until a volunteer opts in,"* not individual
  hesitation. The 39-day `hadoop-common` wait may be "no volunteer would risk the core."
- **Estimates absent** is an Apache-culture artifact (no managerial planning), not a property of
  software.
- **Experience finding** reflects OSS **committer gatekeeping** (trust/permission), not just skill.
- **More likely intrinsic:** abstraction being a larger design commitment; high-dependency modules
  being riskier everywhere. "Slow to finish" is more intrinsic than "slow to start."

**Reframing opportunity:** RQ1 may be less "do individuals hesitate?" and more **"how does a
volunteer community ration attention across high-stakes structural change?"** — a novel, legitimate
framing. To separate intrinsic from OSS-specific effects, the strongest future step is contrasting
with a **commercial/industrial codebase** (all-OSS replication tests OSS-generality only).

## 13. What is / isn't established

**Established:** (a) architectural refactorings are a distinct, higher-friction class (§4); (b) the
friction is specifically in **abstraction-creation, not relocation** (§5), surviving size/volume/
experience controls; (c) architectural tickets are ~2× more **entangled** (§7); (d) friction is
**time, not quality** (§8); (e) it concentrates in **foundational modules** (§9); (f) estimates absent;
traceability excellent.

**Not established:** whether *structural review discussion as such* adds friction beyond volume (§10 —
untested, not disproven, needs validated signal); whether any of this generalizes **beyond
open-source** (§12); causal direction.

## 14. Threats to validity

Descriptive/associational; single project (Hadoop), single release-line window; groups not fully
matched (module/time); triage-within-sub-tasks borderline (p=0.051); keyword signal 25% precise, no κ;
survivorship bias toward landed changes; and the **open-source coordination confound (§12)** pervades
the timing measures.

## 15. Open questions / directions

1. **Blast-radius model:** does a module's dependency centrality predict architectural-change triage?
2. **Validated structural signal** (dual-rater κ), then re-test §10.
3. **Commercial contrast** to separate intrinsic vs OSS-coordination effects (§12).
4. **Better effort proxies** from the changelog (active vs waiting time) and rework/reverts.
5. **Replicate** on Kafka/HBase/Camel (tests OSS-generality).
6. Human-factors (RQ2): who takes on architectural work and why the core stalls.

## 16. Reusable assets

Fault-tolerant parallel refactoring-mining pipeline (`scripts/run_rm_safe.sh`); PR-review recovery
from Jira via bot-relay (no GitHub token); monorepo-aware traceability probe; status-changelog method
separating waiting from active work; committed data artifacts (`*_all.json`, `cox_dataset.json`,
`episode_outcomes.json`, `arch_vs_ordinary.json`) and the comparison chart.

## 17. Honest abstract

> On 8,919 Apache Hadoop commits (v3.1.0–v3.4.3) we detected 349 architectural refactoring episodes,
> 99% traceable to Jira. Against 400 ordinary refactoring tickets, architectural ones draw more review
> and take ~2× longer to start and resolve. The friction is specifically in **abstraction-creating**
> refactorings (extract interface/superclass/class): ~2.5× longer triage than code relocation
> (p=0.004), surviving controls for change size, discussion volume, and contributor experience; simple
> relocation is no harder than ordinary work. The effect is **time, not quality** (no extra rework) and
> **concentrates in the foundational `hadoop-common` module** (~40× the triage latency of HDFS),
> consistent with a *blast-radius/hesitation* mechanism. Effort estimates are absent in Apache (0%). A
> within-episode "structural discussion" signal was found and **retracted** as a discussion-volume
> confound. Major caveat: much of the timing friction reflects **open-source volunteer coordination**
> (triage ≈ time-to-volunteer), so generalization beyond OSS is untested. Contribution: a reproducible
> pipeline, a defended and mechanism-level preliminary finding, and a well-scoped study design.
