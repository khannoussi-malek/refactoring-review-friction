# Preliminary Study Summary — Architectural Refactoring Friction in Apache Hadoop

> **Superseded 2026-08-08.** This document records the state of the work as of
> its date. Several of its conclusions were later retracted or corrected. The
> current account is `README.md` §3 and §4; the retraction record is
> `PROJECT_STATE.md` §2.
>
> It is the same vintage as `research_prospectus.md` and `advisor_brief.md` and
> carries the same withdrawn headline — *harder to build, not harder to merge*
> (withdrawn 2026-07-25, `4b8c3af`) — and the same superseded estimate claim
> (corrected to 2.557% / 1.449% / 0 of 323, `eee902f`).

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

**Triage latency anchors this against the volume confound** — it is measured *before* any discussion
exists, so it cannot be a discussion-volume artifact (the failure mode that killed §8). It is *not*
comparable across module tiers or across eras, though: see §4a and §4b, where the Jira status field it
derives from turns out to be unmaintained for one tier and to collapse project-wide in 2019–20.

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

## 4b. The trajectory — the one kind of work that a decade of tooling did not make cheaper

Everything above is a snapshot. Tracked year by year, it becomes a trajectory, and the trajectory is
the strongest thesis statement in the study.

This required fixing the instrument first: Hadoop moved to GitHub PRs around 2019–20 and Jira status
hygiene collapsed with it (**93.5% → 15.5%** of tickets reaching `Patch Available`), so status-derived
durations change meaning mid-corpus. The raw signal is therefore mostly measurement drift and is *not*
reported. Instead we use a workflow-independent clock — ticket creation → **the first commit citing
it**, from git — which means the same thing in 2016 and 2025 and covers **714/714 tickets**.

![temporal trend](figures/temporal_trend.png)

| | Architectural | Ordinary (control) |
|---|---|---|
| Year vs days-to-first-commit | rho = +0.04, p = 0.45 (**flat**) | rho = **−0.21**, p = 3e-05 (**improving**) |

**Ordinary refactoring got faster across the decade. Architectural refactoring did not.** The
difference-in-differences interaction is **+0.20, p = 0.003** with abstraction and connector-tier
composition controlled, and stable at +0.19 under every truncation window. The gap widens from ~1.6×
to ~10×.

The ordinary-refactoring control is what makes this interpretable: a shrinking or ageing community
would slow *both* groups. Only structural work is left behind.

**Why it matters.** A decade of process investment — CI, PR review, Yetus automation — made routine
change substantially cheaper and left structural change untouched. That is architectural debt
behaving exactly as theory predicts: its cost does not fall with ordinary productivity, so it
**compounds relative to everything else**. It reframes RQ1's stakes — the problem is not that
architectural work is slow, but that it is **the one category not getting better**.

*Honest limits:* right-censoring biases recent years toward fast, making the divergence conservative;
the ordinary control thins to <5 tickets after 2023; and "days to first commit" is a total, mixing
queueing with building.

**A systemic caveat worth stating once.** Three independent measurement channels — Jira status
comparability, status hygiene over time, and CI verdict visibility — all decay at the same 2019–20
GitHub migration. That is not three coincidences; it is one structural fact about mining Apache Jira,
and it is why this study builds git-derived instruments (commit clock, change size, authorship)
wherever a claim has to span the decade.

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
- **Quality is a null, and it holds under a much stronger test.** The reopen rate is equal (~7%,
  p=0.97), but that is a blunt instrument. Hadoop's pre-commit CI gives a real rework measure —
  **CI runs ≈ patch revisions**. Architectural tickets do need more (median 5 vs 3, p<1e-4), and that
  survives a discussion-volume control (the §8 trap). It does **not** survive a *change-size* control
  (p → 0.07): architectural patches are simply far bigger (**1,178 vs 213 java lines churned**).
  So the refined claim is: architectural work is **not more error-prone per unit of code changed** —
  it just involves more code. `-1`-rate was tested as a volume-free alternative and discarded: it
  fires on any warning, so 87% of all runs "fail" and the measure is pinned at its ceiling.
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

And §4 survives it: abstraction still predicts triage with tier and era controlled (coef +0.67,
**p = 0.010**) — so the finding now holds under all five controls: change size, discussion
volume, contributor experience, module tier, and era.

**We then tried to promote this from observation to mechanism, and could not.** The connector tier was
hand-drawn from module names in a table, so we tried replacing it with a measured variable —
maintainer concentration from git, computed only over commits *preceding* each ticket. It corroborates
the tier's character independently (top author owns 39% of connector commits vs 9% elsewhere,
p=4e-21; bus factor 3 vs 10) but **explains nothing**: concentration is collinear with module size
(rho = −0.86), and once size is controlled the effect vanishes on every trustworthy measure
(building-time p = 0.24, lifetime p = 0.07), with no gradient at all inside the rest of the corpus.

The useful residue is a **design requirement, not a result**: in one project, "peripheral" — small,
few-authored, low-centrality, vendor-specific — is a *single* variable. Separating those requires a
multi-project corpus, which is now a precondition for any attention-based claim rather than a
nice-to-have.

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
refactoring friction, and the cost is in *building* — robust to five controls plus the
full-workflow restriction, time-not-quality, and
demonstrably not a volunteer-queueing artifact); **three mechanisms tested and rejected by our own
analysis** (the structural-discussion signal §8; the blast-radius model §6a; maintainer concentration
§6a) — each reported rather than buried; a **measurement caveat for Apache-Jira mining generally**
(status-derived timings are not comparable across module tiers that drive different workflows, §4a);
and a well-scoped design in which the surviving claim is small, specific and defended. **Full study:** an **attention-rationing model** (maintainer concentration / review
pool, not code centrality — the §6a lead); a validated, dual-rated (κ) structural signal; better
changelog effort proxies; a commercial contrast to separate intrinsic from OSS effects; and
replication on Kafka/HBase/Camel, now carrying a **pre-registered prediction** from §6a — peripheral
vendor-integration modules should stall more than core ones.
