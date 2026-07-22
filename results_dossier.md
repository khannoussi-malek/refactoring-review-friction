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

## 5a. Phase decomposition — the friction is in BUILDING the change, and it is largely intrinsic

§12's caveat says our timing measures may just be measuring volunteers being slow. The status
changelog settles most of it. Apache's workflow (derived from the corpus, not assumed) is
`Open/Reopened → In Progress → Patch Available → Resolved`, where **Patch Available means working code
exists and is waiting on a committer**. That gives two cleanly separable phases:

- **`t_to_patch`** (created → first Patch Available) = time until working code exists → *doing the work*
- **`t_review`** (total time in Patch Available) = time waiting on a reviewer → *getting it accepted*

![friction phases](figures/friction_phases.png)

**Architectural vs ordinary — the friction is in building, not merging:**

| Phase | Architectural | Ordinary | p |
|---|---|---|---|
| Days to first patch | **3.86** | **1.00** | **0.0020** |
| Days in review | 8.52 | 8.37 | 0.52 (n.s.) |
| Days to first comment | 1.21 | 0.44 | 0.0046 |
| **Active coding time** (In Progress) | **4.87** | **1.13** | **0.037** |

Architectural changes are **~4× slower to produce a patch** and take **~4× longer in logged active
coding time**, but once a patch exists they are **merged just as fast as ordinary work**. Reviewers are
not the bottleneck — building the thing is.

**Abstraction pays twice.** Within architectural work (full-workflow sub-corpus, n=251):

| Phase | Abstraction | Relocation | p |
|---|---|---|---|
| Days to first patch | 4.95 | 1.11 | 0.0087 |
| Days in review | **12.15** | **5.46** | **0.0003** |
| Total lifetime | 30.11 | 13.83 | 0.0017 |

Abstraction is the one category that is slower in **both** phases — ~4.5× slower to build *and* ~2×
slower to get merged (OLS on the clean sub-corpus, connector-controlled: `t_to_patch` +0.51 p=0.032,
`t_review` +0.57 p=0.0025, total +0.63 p=0.0032). Creating a shared abstraction is both harder to do
and harder to get others to accept.

**Why this matters more than any other result here:** active coding time and time-to-build-a-patch are
**not volunteer-queueing artifacts**. A ticket in `In Progress` has someone working on it. So the core
finding is substantially **intrinsic difficulty**, not open-source coordination — which is exactly what
§12 said we could not yet claim. The OSS confound is now **bounded, not merely acknowledged**.

**Self-assignment (a strong effect, but read it carefully).** Whether the reporter ends up doing the
work themselves does *not* differ between groups (79.8% architectural vs 78.0% ordinary, p=0.62) — but
it is the largest single predictor of speed we have found: **2.05 days to patch when self-assigned vs
31.66 when not (p < 1e-4)**. This is partly **endogenous** — a ticket that waits for someone else to
take it has, by construction, waited — so it is a description of the mechanism, not a causal estimate.
It says the decisive event in this community is *someone deciding to own the work*.

## 5b. A measurement threat this uncovered — status-derived timings are not comparable across tiers

Decomposing by phase exposed something the aggregate measures hid: **different parts of Hadoop drive
different Jira workflows.**

| Group | Reached `Patch Available` | Used `In Progress` |
|---|---|---|
| Cloud connectors | **28.3%** | 37.0% |
| Everything else | **86.2%** | 27.2% |

A committer who owns a module commits directly and never moves the ticket through `Patch Available`;
the status field simply goes unmaintained while the work happens on a GitHub PR. **This qualifies
§9a:** the connector tier's "43.6-day triage" is closer to a *lifetime* than a measured queue, because
for 72% of those tickets the first status change **is** resolution. Connectors are still genuinely
slower end-to-end (75.2 vs 25.9 days total lifetime, p<1e-4, and 78.9 vs 38.1 days even among tickets
that never reach Patch Available), so the *finding* survives — but the **"waiting for attention"
reading of it does not, and should not be asserted.** Among the 13 connector tickets that do use the
full workflow, review time is 32.2 vs 8.5 days (p=0.19 — directionally 4×, badly underpowered).

**Consequence for the whole study:** every status-derived timing measure — including the triage
latency used in §4, §5 and §9a — must be reported against the **full-workflow sub-corpus**, where the
headline results hold cleanly (tables in §5a). This is a generalisable methodological caveat for
anyone mining Apache Jira, and worth stating as such.

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

## 9b. Social centrality — corroborates the tier, but fails to explain it

§9a's weakest point was its own admission: the connector tier was **hand-drawn from seven module names
spotted in a table**. §5b then showed its timing numbers are partly a workflow artifact. So we tried to
replace the post-hoc dummy with a continuous, independently measured variable — **maintainer
concentration**, computed from **git** (a different data source from the Jira assignee figures) over
commits **strictly before each ticket was filed**, so the ticket's own work cannot inflate the
predictor.

![social centrality](figures/social_centrality.png)

**What worked — independent corroboration of the tier's character:**

| Measure (median) | Connectors | Rest | p |
|---|---|---|---|
| Top author's share of prior commits | **39%** | 9% | 4e-21 |
| Bus factor (authors covering 50% of commits) | **3** | 10 | 2e-19 |
| Distinct authors | 76 | 124 | 9e-11 |
| Reviewer pool (commenters on the module's other tickets) | 26 | 39 | 1e-04 |

Git independently confirms what Jira assignees suggested: these modules really are owned by very few
people. That is a solid *description*.

**What failed — it does not explain friction.** Concentration is **near-collinear with module size**
(Spearman **−0.86**, p=4e-69): a module maintained by few people is almost tautologically a module with
few commits. Once module size is controlled, the effect collapses on exactly the measures §5b showed
are trustworthy:

| Outcome | Concentration alone | + module-size control |
|---|---|---|
| `t_to_patch` (building) | +3.27, p = 0.024 | +3.51, **p = 0.239** |
| Total lifetime | +2.98, p < 0.001 | +2.38, **p = 0.073** |
| Triage latency | +4.51, p < 0.001 | +7.13, p < 0.001 |

Only **triage** survives — and triage is precisely the measure §5b showed is contaminated for these
tickets (unmaintained status field ⇒ triage ≈ lifetime). Worse, concentration produces **no gradient
at all within the non-connector corpus** (triage rho = −0.05 p=0.50; `t_to_patch` rho = +0.09 p=0.27;
total rho = +0.08 p=0.25).

**Verdict: the replacement attempt fails.** Maintainer concentration does not defensibly substitute for
the post-hoc tier, so **§9a caveat (d) stands** — the connector finding still needs a held-out project.

**What we learned anyway (the useful part).** In this corpus, "peripheral module" is a **single latent
property**: small, few-authored, low-centrality and vendor-specific all travel together and cannot be
separated with 11 modules. That is a concrete design requirement for the next study rather than a
vague call for more data: **breaking this collinearity needs many more modules — i.e. multiple
projects — and is a precondition for any causal claim about attention.**

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

*Substantially revised after §5a: the phase decomposition converts much of this from "unbounded
threat" to "measured and bounded."*

Some of the measured "friction" still reflects **how open-source coordinates work**:
- **Estimates absent** is an Apache-culture artifact (no managerial planning), not a property of
  software.
- **Experience finding** reflects OSS **committer gatekeeping** (trust/permission), not just skill.
- **Self-assignment** (§5a) is the clearest OSS-specific mechanism: the decisive event is someone
  choosing to own the work (2.05 vs 31.66 days to patch). A firm with assigned owners has no
  equivalent.
- **§9a's connector tier** cannot be read as an attention effect, because those tickets do not drive
  the workflow that would make "waiting" measurable (§5b).

**But the core finding is now demonstrably NOT a coordination artifact.** §5a shows architectural work
takes ~4× longer in **logged active coding time** (4.87 vs 1.13 days) and ~4× longer to **produce a
patch**, while being merged just as fast as ordinary work. Time spent `In Progress` is time somebody is
working — it cannot be volunteer queueing. Abstraction additionally costs ~2× in review (12.15 vs 5.46
days, p=0.0003), which *is* a social cost, but it sits on top of a real construction cost rather than
substituting for one.

So the honest split is: **abstraction-as-difficulty is intrinsic and should replicate in industry;
abstraction-as-hard-to-agree-on is social and may be OSS-flavoured; who-picks-it-up is purely OSS.**

**Reframing opportunity:** RQ1 may be less "do individuals hesitate?" and more **"how does a
volunteer community ration attention across high-stakes structural change?"** — a novel, legitimate
framing. To separate intrinsic from OSS-specific effects, the strongest future step is contrasting
with a **commercial/industrial codebase** (all-OSS replication tests OSS-generality only).

## 13. What is / isn't established

**Established:** (a) architectural refactorings are a distinct, higher-friction class (§4); (b) the
friction is specifically in **abstraction-creation, not relocation** (§5), surviving size/volume/
experience/tier/era controls and the full-workflow restriction; (c) **the friction is in building the
change, not in getting it merged** — ~4× longer active coding time — so it is largely **intrinsic
difficulty, not volunteer queueing** (§5a); (d) **abstraction uniquely pays twice**, ~4.5× to build
*and* ~2× in review (§5a); (e) architectural tickets are ~2× more **entangled** (§7); (f) friction is
**time, not quality** (§8); (g) friction varies ~40× across modules (§9), concentrated in the
peripheral vendor tier rather than the foundation (§9a); (h) estimates absent; traceability excellent.

**Refuted by our own tests:** the **blast-radius mechanism** (§9a) — module dependency centrality does
not predict triage latency (p = 0.33 with tier controlled), and the raw association runs *negative*.

**Qualified by our own tests:** §9a's connector tier is slower end-to-end but its "waiting for
attention" interpretation is not supported — those tickets do not drive the Jira workflow that would
make waiting measurable (§5b).

**Tested and failed to establish:** **maintainer concentration** as a measured replacement for the
post-hoc connector tier (§9b) — it corroborates the tier's character from git but is collinear with
module size (rho −0.86) and explains nothing once size is controlled.

**Not established:** whether *structural review discussion as such* adds friction beyond volume (§10 —
untested, not disproven, needs validated signal); whether any attention-based explanation for the
connector tier holds (§9a/§9b — still post-hoc, needs a held-out project); whether the
**self-assignment** effect is causal rather than definitional (§5a — endogenous); whether the
*review-phase* half of the abstraction cost generalizes **beyond open-source** (§12 — the
*build-phase* half now plausibly does); causal direction.

## 14. Threats to validity

Descriptive/associational; single project (Hadoop), single release-line window; groups not fully
matched (module/time); triage-within-sub-tasks borderline (p=0.051); keyword signal 25% precise, no κ;
survivorship bias toward landed changes; the **open-source coordination confound (§12)**, now bounded
by §5a rather than open-ended; **status-derived timings are not comparable across module tiers that
drive different workflows (§5b)** — results should be read on the full-workflow sub-corpus; the
self-assignment effect is **endogenous** (§5a); `In Progress` is logged by only ~25% of tickets, so
active-time results rest on that sub-corpus; and for §9a specifically, **26% episode attrition**
(Ozone/Submarine left the repo), a present-day dependency snapshot applied to a decade of history, and
a **post-hoc** connector tier.

## 15. Open questions / directions

1. ~~**Blast-radius model**~~ (**§9a: no**) → ~~**attention-rationing model** via maintainer
   concentration~~ (**§9b: not separable from module size**). What remains: **break the collinearity.**
   Peripherality, size, author count and centrality are one variable in a single project; only a
   multi-project corpus can tell them apart. This is now the precondition for any attention claim.
2. **Validated structural signal** (dual-rater κ), then re-test §10.
3. **Commercial contrast** to separate intrinsic vs OSS-coordination effects (§12).
4. ~~**Better effort proxies** from the changelog (active vs waiting time)~~ **Done in §5a.** Follow-on:
   rework/reverts, and recovering active time for the ~75% of tickets that never log `In Progress`
   (GitHub PR timestamps via the githubbot relay would give a workflow-independent clock — and would
   also repair the §5b comparability problem).
5. **Replicate** on Kafka/HBase/Camel — now with a **specific pre-registered prediction** from §9a
   (peripheral/vendor-integration modules should show longer triage than core modules) *and* the
   design requirement from §9b (enough modules to separate size from concentration).
6. Human-factors (RQ2): who takes on architectural work, and why *peripheral* work stalls.
7. **Recover the Ozone/Submarine episodes** (§9a caveat a) by resolving their split-out repos.

## 16. Reusable assets

Fault-tolerant parallel refactoring-mining pipeline (`scripts/run_rm_safe.sh`); PR-review recovery
from Jira via bot-relay (no GitHub token); monorepo-aware traceability probe; status-changelog method
separating waiting from active work; **Maven blast-radius graph builder** (`scripts/module_graph.py`)
and **refactoring→module attribution + mechanism test** (`scripts/episode_files.py`,
`scripts/blast_radius_model.py`, which reruns the §5 replication gate before reporting anything);
**status-changelog phase decomposition** (`scripts/friction_decomposition.py`) separating *building*
from *merging* time, with a built-in workflow-comparability check (§5b) that other Apache-Jira studies
would need; **prior-window social-centrality measures** (`scripts/social_centrality.py` — bus factor,
concentration and reviewer pool computed only over history preceding each ticket, with the size-
collinearity check that decides whether they mean anything); committed data artifacts (`*_all.json`, `cox_dataset.json`, `episode_outcomes.json`,
`arch_vs_ordinary.json`, `module_blast_radius.json`, `blast_radius_results.json`,
`friction_decomposition.json`) and the charts.

## 17. Honest abstract

> On 8,919 Apache Hadoop commits (v3.1.0–v3.4.3) we detected 349 architectural refactoring episodes,
> 99% traceable to Jira. Against 400 ordinary refactoring tickets, architectural ones draw more review
> and take ~2× longer to start and resolve. The friction is specifically in **abstraction-creating**
> refactorings (extract interface/superclass/class): ~2.5× longer triage than code relocation
> (p=0.004), surviving controls for change size, discussion volume, and contributor experience; simple
> relocation is no harder than ordinary work. The effect is **time, not quality** (no extra rework).
> Decomposing the status changelog into phases localises it: architectural work takes **~4× longer in
> logged active coding time** (4.87 vs 1.13 days) and ~4× longer to produce a patch, but is **merged as
> fast as ordinary work** — so the friction is largely **intrinsic construction difficulty, not
> volunteer queueing**, bounding the open-source confound rather than merely conceding it. Abstraction
> uniquely pays twice: ~4.5× to build *and* ~2× in review (12.2 vs 5.5 days, p=0.0003).
> Triage latency varies ~40× across modules, and we tested the obvious mechanism — *blast radius*,
> that touching a heavily depended-upon module invites hesitation — against Hadoop's Maven dependency
> graph (117 modules). **It fails:** centrality does not predict triage (p = 0.33) and the raw
> association is *negative*. The friction concentrates instead in the structurally **peripheral**
> vendor cloud-connector tier (43.6 vs 3.1 days, p = 3e-07), where one maintainer owns a third of the
> work — friction tracks where **community attention is thinnest**, not where technical risk is
> highest. Effort estimates are absent in Apache (0%). A within-episode "structural discussion" signal
> was found and **retracted** as a discussion-volume confound. Remaining caveats: the *review* half of
> the abstraction cost and the question of who picks work up are open-source-specific, and
> status-derived timings are not comparable across module tiers that drive different Jira workflows —
> a methodological caveat we surface and correct for. Contribution: a reproducible pipeline, a defended
> mechanism-level finding localised to a specific development phase, two mechanisms killed by our own
> tests, and a well-scoped study design.
