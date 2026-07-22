# RQ1 study — full results dossier (for proposal improvement)

*Complete, honest hand-off of everything the preliminary study found. All numbers are exact. This
supersedes earlier partial versions. For an AI agent improving the proposal: the **refined finding
(§5)** is the recommended headline; the **retraction (§10)**, the **refuted blast-radius mechanism
(§9a)** and the **open-source caveat (§12)** are central, not footnotes — do NOT resurrect the
retracted result, do NOT restate §9's original "the foundation stalls" reading (§9a corrects it),
and do not oversell beyond what each number supports.*

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

## 9. Module hotspots — large variation, but NOT where we first thought

Median triage latency by top-level Jira project (architectural tickets):

![module hotspots](figures/module_hotspots.png)

| Jira project | Arch tickets | % abstraction | Median triage |
|---|---|---|---|
| HDFS | 96 | 56% | **1.0 day** |
| HDDS (Ozone) | 72 | 60% | 3.8 days |
| YARN | 75 | 77% | 7.1 days |
| **HADOOP** | 73 | 68% | **39.1 days** |

**~40× variation** — this part stands. Our original interpretation of it (**blast radius**: the more
depended-upon a module, the more hesitation before touching its structure) was **tested in §9a and
does not survive.** Two things were wrong with reading the table above as a blast-radius result:

1. `HADOOP-*` is a **Jira project prefix, not a module.** It bundles `hadoop-common` with every
   cloud-connector ticket (`hadoop-aws`, `hadoop-azure`, …), which live under `hadoop-tools/`.
2. Those connectors, not the foundation, are what makes the row slow.

## 9a. Testing the blast-radius mechanism — it fails, and the effect runs the other way

We measured module centrality **independently of the tickets**, from Hadoop's Maven dependency graph:
117 in-tree modules, 513 internal edges; a module's **blast radius** = how many modules transitively
depend on it (range 0–90; `hadoop-common` = 86, `hadoop-aws`/`hadoop-azure` = 2). Architectural
episodes were mapped to modules via the *file paths of the architectural refactorings themselves*
(from RefactoringMiner, not the whole commit diff). **259/349 episodes → 242 tickets with triage.**

![blast radius](figures/blast_radius.png)

**The mechanism is refuted:**

| Test | Result |
|---|---|
| Blast radius vs triage, ticket level (n=242) | rho = **−0.19**, p = 0.003 — *negative*: more central = picked up **faster** |
| Blast radius vs median triage, module level (n=11) | rho = −0.18, p = 0.59 (n.s.) |
| OLS + connector-tier control | coef **+0.09, p = 0.33 — null** |
| Spearman excluding connectors (n=196) | rho = **−0.03, p = 0.65 — null** |

Once the cloud-connector tier is controlled for, blast radius carries **no signal at all**. The
apparent negative correlation was entirely the connectors (peripheral *and* slow) pulling the line.

**The real hotspot is the peripheral vendor tier:**

| Group | n | Median triage | Median blast radius |
|---|---|---|---|
| Cloud connectors (`hadoop-aws`, `hadoop-azure`, …) | 46 | **43.6 days** | 2 |
| Everything else (incl. `hadoop-common`, HDFS, YARN) | 196 | **3.1 days** | 65 |

**~14× slower, p = 2.7e-07.** It is not an era artifact — connectors are slower in every period
(≤2018: 15.2 vs 2.2 d; 2019–21: 25.7 vs 2.9 d; 2022+: 72.5 vs 20.7 d), and the tier survives a
year control (coef +1.67, p = 0.0001).

**Correcting §9's headline number:** the 39.1-day `HADOOP-*` median reproduces exactly, but **45 of
those 73 tickets (62%) are cloud connectors, not `hadoop-common`.** `hadoop-common` on its own is
**n = 25, median 24.8 days** — still elevated, but the "foundation stalls ~40× longer than HDFS"
claim was inflated by a project-prefix aggregation.

**Why are connectors slow?** Not a thinner volunteer pool — tickets per assignee is the same
(2.56 vs 2.36). It is **concentration**: one maintainer owns **33%** of connector tickets versus 9%
for the top maintainer elsewhere. Work waits on a specific person, not on collective nerve.

**What this means (feeds §12).** Friction does *not* track where technical risk is highest; it tracks
where **community attention is thinnest**. Vendor-specific connectors are structurally safe to change
and still wait ~6 weeks, while the module 86 others depend on is picked up in days. That is attention
rationing, not blast-radius hesitation — direct empirical support for the §12 reframing.

**§5 survives this, strengthened:** with connector tier and era both controlled, abstraction still
predicts triage (coef **+0.67, p = 0.010**), and it holds even with connectors excluded entirely
(coef +0.59, p = 0.041). The headline finding is now robust to a fifth control.

*Caveats.* (a) **90 episodes (26%) could not be attributed** — 78 are HDDS/Ozone and 2 Submarine,
subprojects since split out of the Hadoop repo, so their poms no longer exist in-tree; this analysis
covers the surviving monorepo only. (b) The dependency graph is a **present-day snapshot** applied to
episodes spanning 2016–2026. (c) Module-level n = 11 is small. (d) The connector tier was **found by
inspecting the module table, not hypothesized in advance** — it needs confirmation on a held-out
project before being treated as a claim rather than a lead.

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
experience/tier/era controls; (c) architectural tickets are ~2× more **entangled** (§7); (d) friction
is **time, not quality** (§8); (e) friction varies ~40× across modules (§9) but is **concentrated in
the peripheral vendor tier, not the foundation** (§9a); (f) estimates absent; traceability excellent.

**Refuted by our own test:** the **blast-radius mechanism** (§9a) — module dependency centrality does
not predict triage latency (p = 0.33 with tier controlled), and the raw association runs *negative*.

**Not established:** whether *structural review discussion as such* adds friction beyond volume (§10 —
untested, not disproven, needs validated signal); whether the **maintainer-concentration** explanation
for the connector tier is causal (§9a — post-hoc, needs a held-out project); whether any of this
generalizes **beyond open-source** (§12); causal direction.

## 14. Threats to validity

Descriptive/associational; single project (Hadoop), single release-line window; groups not fully
matched (module/time); triage-within-sub-tasks borderline (p=0.051); keyword signal 25% precise, no κ;
survivorship bias toward landed changes; the **open-source coordination confound (§12)** pervades
the timing measures; and for §9a specifically, **26% episode attrition** (Ozone/Submarine left the
repo), a present-day dependency snapshot applied to a decade of history, and a **post-hoc** connector
tier.

## 15. Open questions / directions

1. ~~**Blast-radius model:** does a module's dependency centrality predict architectural-change
   triage?~~ **Answered in §9a: no.** Replaced by → **attention-rationing model:** does maintainer
   concentration (or bus factor / review-pool size) predict triage better than any structural
   property? The §9a connector result says test *social* centrality, not *code* centrality.
2. **Validated structural signal** (dual-rater κ), then re-test §10.
3. **Commercial contrast** to separate intrinsic vs OSS-coordination effects (§12).
4. **Better effort proxies** from the changelog (active vs waiting time) and rework/reverts.
5. **Replicate** on Kafka/HBase/Camel — now with a **specific pre-registered prediction** from §9a:
   peripheral/vendor-integration modules should show longer triage than core modules.
6. Human-factors (RQ2): who takes on architectural work, and why *peripheral* work stalls.
7. **Recover the Ozone/Submarine episodes** (§9a caveat a) by resolving their split-out repos.

## 16. Reusable assets

Fault-tolerant parallel refactoring-mining pipeline (`scripts/run_rm_safe.sh`); PR-review recovery
from Jira via bot-relay (no GitHub token); monorepo-aware traceability probe; status-changelog method
separating waiting from active work; **Maven blast-radius graph builder** (`scripts/module_graph.py`)
and **refactoring→module attribution + mechanism test** (`scripts/episode_files.py`,
`scripts/blast_radius_model.py`, which reruns the §5 replication gate before reporting anything);
committed data artifacts (`*_all.json`, `cox_dataset.json`, `episode_outcomes.json`,
`arch_vs_ordinary.json`, `module_blast_radius.json`, `blast_radius_results.json`) and the charts.

## 17. Honest abstract

> On 8,919 Apache Hadoop commits (v3.1.0–v3.4.3) we detected 349 architectural refactoring episodes,
> 99% traceable to Jira. Against 400 ordinary refactoring tickets, architectural ones draw more review
> and take ~2× longer to start and resolve. The friction is specifically in **abstraction-creating**
> refactorings (extract interface/superclass/class): ~2.5× longer triage than code relocation
> (p=0.004), surviving controls for change size, discussion volume, and contributor experience; simple
> relocation is no harder than ordinary work. The effect is **time, not quality** (no extra rework).
> Triage latency varies ~40× across modules, and we tested the obvious mechanism — *blast radius*,
> that touching a heavily depended-upon module invites hesitation — against Hadoop's Maven dependency
> graph (117 modules). **It fails:** centrality does not predict triage (p = 0.33) and the raw
> association is *negative*. The friction concentrates instead in the structurally **peripheral**
> vendor cloud-connector tier (43.6 vs 3.1 days, p = 3e-07), where one maintainer owns a third of the
> work — friction tracks where **community attention is thinnest**, not where technical risk is
> highest. Effort estimates are absent in Apache (0%). A within-episode "structural discussion" signal
> was found and **retracted** as a discussion-volume confound. Major caveat: much of the timing
> friction reflects **open-source volunteer coordination** (triage ≈ time-to-volunteer), so
> generalization beyond OSS is untested. Contribution: a reproducible pipeline, a defended
> mechanism-level finding, two mechanisms killed by our own tests, and a well-scoped study design.
