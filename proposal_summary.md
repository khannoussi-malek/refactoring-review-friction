# Preliminary Study Summary — Architectural Refactoring Friction in Apache Hadoop

*Proposal-ready synthesis with figures. Full detail: [results_dossier.md](results_dossier.md);
method + commands: [SLICE_LOG.md](SLICE_LOG.md).*

## 1. Motivation and research question

Large systems accumulate architectural debt, and the refactorings that repay it are believed costlier
and more contentious than routine changes — rarely quantified against real project outcomes. **RQ1:
do architectural refactorings carry measurably more development friction than ordinary changes, and
what is the shape of that friction?** The pilot first rejected the assumption that *effort estimates*
could serve as the signal (absent in Apache), then measured friction from review discussion and
issue-tracker state.

## 2. Method and scale

8,919 Hadoop commits (v3.1.0 → v3.4.3); RefactoringMiner parallelized with a self-healing runner
(90–99% coverage) → 51,861 refactorings → **349 architectural episodes** (323 tickets). Control group:
400 ordinary refactoring tickets. Signals from public Apache Jira: review discussion (githubbot PR
relay), dates, the full status changelog, and ticket properties. Architectural refactoring is rare:

![study funnel](figures/study_funnel.png)

## 3. Feasibility

Traceability **99%** (345/349; needs all monorepo subproject keys — a single-key probe misreads as
26%). Effort estimates **0%** — absent in Apache, ruling out the estimate-based framing.

## 4. Headline finding — the friction is in *abstraction*, not relocation

Architectural refactorings are not uniform. Splitting them by *what they do*:

![abstraction gradient](figures/abstraction_gradient.png)

- **Relocation** (moving/renaming classes and packages) is no harder than ordinary work — triage 2.8
  vs ordinary 2.1 days.
- **Abstraction** (extracting interfaces, superclasses, classes) is **~2.5× slower to be picked up**
  (7.2 vs 2.8 days, p=0.004) and ~2× slower to resolve (34.5 vs 18.0 days, p=0.0001).

The abstraction effect **survives controlling for change size and discussion volume** (p=0.013).
Mechanism: creating a shared abstraction is a larger design commitment → developers hesitate to start.
(Cross-module moves — which are relocations — are actually the *fastest*, confirming that crossing a
boundary is not what makes work hard; the abstraction is.)

**Triage latency is the anchor** because it is measured *before* any discussion, so it cannot be a
discussion-volume artifact.

## 4a. Where the friction lives — and why it is *not* just volunteers being slow

The single strongest objection to §4 is that Apache timing measures capture volunteer queueing rather
than software difficulty. The Jira status changelog answers it. Apache's workflow separates *doing the
work* (`created → Patch Available`, i.e. until working code exists) from *getting it accepted* (time
sitting in `Patch Available`, waiting on a committer).

![friction phases](figures/friction_phases.png)

| Phase | Architectural | Ordinary | p |
|---|---|---|---|
| Days to first patch | **3.86** | **1.00** | **0.002** |
| Days in review | 8.52 | 8.37 | 0.52 (n.s.) |
| **Active coding time** (`In Progress`) | **4.87** | **1.13** | **0.037** |

**Architectural work is ~4× slower to build and ~4× longer in logged active coding — but is merged
just as fast as ordinary work.** Reviewers are not the bottleneck; construction is. Time logged as
`In Progress` is time someone is *working*, which cannot be volunteer queueing — so the core effect is
**intrinsic difficulty** and should be expected to replicate in industry.

**Abstraction is the one category that pays twice** (full-workflow sub-corpus, n=251): 4.95 vs 1.11
days to build (p=0.009) *and* 12.15 vs 5.46 days in review (p=0.0003). Creating a shared abstraction
is both harder to do and harder to get others to agree to.

**A caveat we found and corrected for.** Different parts of Hadoop drive different Jira workflows —
the cloud connectors reach `Patch Available` only 28% of the time vs 86% elsewhere, because a
committer who owns a module commits directly and leaves the status field untouched. Status-derived
timings are therefore **not comparable across tiers**, which qualifies §6a's connector result (it is a
lifetime, not a measured queue) and is a reusable warning for anyone mining Apache Jira. Every number
above is reported on the full-workflow sub-corpus.

## 5. Alternatives ruled out

- **Priority:** similar (82% vs 75% Major) — not the cause.
- **Issue type:** architectural work skews to sub-tasks (63% vs 44%), not bugs — controlled for.
- **Discussion volume + change size:** controlled; abstraction survives.
- **Staffing:** architectural work goes to *more active* contributors (median 9 vs 5 tickets,
  p<0.0001) who normally start *faster* (rho −0.19) — yet it still stalls. Not "waiting for a rare
  expert." Under the strictest control (within sub-tasks) the triage gap is borderline (p=0.051):
  robust in direction and magnitude, modest, and — unlike the retracted signal (§8) — it does not
  collapse.

## 6. Supporting findings

- **Entanglement:** architectural tickets link to ~2× more other issues (1.53 vs 0.76, p=0.001, holds
  within sub-tasks). Volume-independent — a second friction dimension.
- **Quality is a null:** reopen rate ~7% across all groups (p=0.97). Abstraction is slower but *not
  buggier* — the friction is time, not error-proneness.
- **Module hotspots:** triage latency varies ~40× across modules.

![module hotspots](figures/module_hotspots.png)

## 6a. A mechanism we proposed, tested, and killed

The obvious reading of that ~40× spread is **blast radius**: touching a module that many others depend
on invites hesitation. We tested it properly — building Hadoop's Maven dependency graph (117 modules,
513 internal edges) so that centrality is measured *independently of the tickets*, then mapping each
architectural refactoring to a module by its file paths (259 episodes → 242 tickets).

![blast radius](figures/blast_radius.png)

**It fails.** Centrality does not predict time-to-pickup (OLS coef +0.09, **p = 0.33**; Spearman
excluding connectors rho = −0.03, p = 0.65), and the raw association even runs *negative* — the most
depended-upon modules are picked up **fastest**. The ~40× spread is real but had two flaws as
evidence: `HADOOP-*` is a Jira prefix, not a module, and **62% of those "hadoop-common" tickets are
actually cloud connectors**. `hadoop-common` alone is 24.8 days, not 39.

**What is actually there** is the opposite finding: the structurally **peripheral** vendor
cloud-connector tier (`hadoop-aws`, `hadoop-azure`; blast radius ~2) waits **43.6 days vs 3.1**
elsewhere — **~14×, p = 3e-07**, stable across eras. Nothing depends on these modules, so hesitation
cannot be the story; **one maintainer owns 33%** of their tickets (vs 9% elsewhere).

**Friction tracks where community attention is thinnest, not where technical risk is highest.** That
is hard evidence for the reframing in §9 below. And §4 survives it: abstraction still predicts triage
with tier and era controlled (coef +0.67, **p = 0.010**) — a fifth control passed.

## 7. Between-group primary comparison (context for §4)

Architectural vs. ordinary refactorings overall — more review, ~2× longer triage and resolution, same
core of maintainers:

![architectural vs ordinary](figures/arch_vs_ordinary.png)

## 8. A finding we retracted (methodological rigor)

A within-episode signal — structural review discussion → slower resolution — looked robust (Cox HR
0.69, p=0.003, survived change-size control) but **collapsed once discussion volume was controlled**
(HR 1.10, p=0.51). Discussion volume is the real predictor; the keyword signal (25% precise) is
entangled with sheer discussion quantity. Reported deliberately.

![retraction](figures/retraction.png)

## 9. Open-source caveat (important)

*Substantially narrowed by §4a — this is now a bounded caveat rather than an open-ended one.*

**No longer a threat:** the central effect survives the strongest available test. Architectural work
takes ~4× longer in *logged active coding time*, which is time someone is demonstrably working, not
time in a queue. That half of the finding should generalize beyond open source.

**Still open-source-specific:** (i) *who picks the work up* — self-assignment predicts speed
enormously (2.05 vs 31.66 days to patch), and a firm with assigned owners has no equivalent;
(ii) the *review* half of the abstraction cost (12.15 vs 5.46 days), which is a social cost of getting
agreement; (iii) absent estimates (Apache culture) and committer gatekeeping.

So the honest split is: **abstraction-as-difficulty is intrinsic; abstraction-as-hard-to-agree-on is
social; who-volunteers is purely OSS.** A commercial contrast is still the strongest next step, but it
now tests a *specific, pre-stated* prediction rather than the whole result. The reframing stands as a
complement, not a retreat: *"how does a volunteer community ration attention across high-stakes
structural change?"*

## 10. Contribution and full-study plan

**Contribution:** a reproducible fault-tolerant pipeline; a defended, mechanism-level preliminary
finding, now **localised to a specific development phase** (abstraction-creation is the locus of
refactoring friction, and the cost is in *building* — robust to five controls, time-not-quality, and
demonstrably not a volunteer-queueing artifact); **two mechanisms tested and killed by our own
analysis** (the structural-discussion signal, §8; the blast-radius model, §6a); a **measurement caveat
for Apache-Jira mining generally** (status-derived timings are not comparable across module tiers that
drive different workflows, §4a); and a well-scoped design. **Full study:** an **attention-rationing model** (maintainer concentration / review
pool, not code centrality — the §6a lead); a validated, dual-rated (κ) structural signal; better
changelog effort proxies; a commercial contrast to separate intrinsic from OSS effects; and
replication on Kafka/HBase/Camel, now carrying a **pre-registered prediction** from §6a — peripheral
vendor-integration modules should stall more than core ones.
