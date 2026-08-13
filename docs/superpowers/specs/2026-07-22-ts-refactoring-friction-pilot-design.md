# Design — Architectural refactoring friction in full-stack TypeScript

**Date:** 2026-07-22
**Status:** design, pending approval
**Predecessor:** the Apache Hadoop RQ1 feasibility study in this repo (`README.md`, `results_dossier.md`)

---

## 1. What this is

The Hadoop study established a pipeline and a defended, mechanism-level finding: abstraction is the
locus of refactoring friction, the cost is in *building* it, and it is the one category that did
**not** get cheaper across the decade (difference-in-differences interaction +0.20, p=0.003, on a
workflow-independent git clock). Quality is unchanged even under a stronger rework test — CI
attempts are higher for architectural work (5 vs 3) but the effect dies under a change-size
control. Alongside these: three self-rejected mechanisms, one self-corrected claim, and a systemic
caveat that three independent Apache measurement channels all decay at the 2019–20 GitHub
migration.

Its stated weakness is external validity: one project, one language, one governance model.

This design extends it to **full-stack TypeScript**. It is not a second Hadoop study. It is a
**three-tier programme** whose first tier — the pilot — exists to validate the instrument, not
to produce a finding.

The pilot corpus is `BearStudio/start-ui-web`. It was chosen *because* it is small: at 26.7k LOC
and 1,199 commits, the complete state of the system can be reconstructed at every commit in its
history and its refactorings can be exhaustively hand-labelled. Neither is possible on Hadoop.

**Scope of this document.** It specifies the whole three-tier programme so that tier-1 decisions
are made with tiers 2 and 3 in view. Only **tier 1 is in scope for the first implementation plan**;
tiers 2 and 3 get their own plans once the pilot's validation results are in, since those results
determine which attributes are worth extracting at scale.

**The pilot must never be used to confirm a hypothesis.** It has no friction variance to speak of
(median PR merge 0.80 days, 25% merged under an hour, median review threads 0, and one developer
authored 66% of commits). Any effect measured there would be uninterpretable. Its job is to
validate the detector, fix the operationalisations, and generate candidates.

---

## 2. Corpora

| Tier | Repo | Measurement | Role | Access rule |
|---|---|---|---|---|
| **1 · Pilot** | start-ui-web (16 MB, 1,199 commits) | **dense** — every attribute, every commit | validate detector; fix operationalisations; generate hypotheses | never used for confirmation |
| **2 · Calibration** | Documenso (280 MB) | medium | validate the *outcome* pipeline where friction actually varies | opened before pre-registration |
| **3 · Holdout** | cal.diy (1.1 GB), Twenty (1.4 GB) | **sparse** — only attributes that earned their place in tier 1 | confirmatory tests only | opened **after** pre-registration is committed and hashed |

Tier 2 exists to close a specific gap: the pilot can validate that we *extract* correctly, but
having no friction variance it can never validate that we *measure outcomes* correctly. Documenso
exercises the outcome half while mistakes are still cheap to find.

Dense-then-sparse is what makes the programme affordable. The pilot discovers which of the ~80
candidate attributes carry signal; only those get extracted at scale.

---

## 3. Hypotheses

Committed and hashed before any tier-3 repo is cloned.

### Confirmatory

- **H1 (ported).** Abstraction-creating refactorings carry more friction than relocation.
  *Hadoop: 7.2 vs 2.8 days to first touch, p=0.004.*
- **H2 (ported).** The friction is in **building**, not merging.
  *Hadoop: 4.87 vs 1.13 days active coding, p=0.037; merge time n.s.*
- **H3 (new, TS-specific).** Friction increases monotonically across an ordinal boundary variable:
  `tier-internal < cross-tier < contract-crossing`. Tested as a single ordinal term, not three
  pairwise comparisons.
- **H5 (ported).** Architectural refactoring does not share in the project's speedup over time:
  ordinary refactoring gets faster across the corpus window while architectural work stays flat.
  *Hadoop: rho=−0.21 (p=3e-05) vs rho=+0.04 (p=0.45); DiD interaction +0.20, p=0.003.*

  H5 is unusually well-suited to this corpus. start-ui-web spans 2019–2026 — essentially the same
  window as the Hadoop decade analysis — and cal.diy and Twenty cover comparable spans. It also
  travels better than H1 and H2: a *within-repo trend over time* is far less sensitive to the
  governance confound in §3a than a cross-corpus level comparison, because each repo serves as its
  own control. If governance sinks the cross-language claim, H5 survives it.

### Exploratory (no direction committed)

- **H4.** Contract-crossing refactorings are reverted or re-refactored at a different rate than
  tier-internal ones. Direction is genuinely uncertain — contract changes attract more scrutiny,
  which could make them either more durable or more fragile. Recorded as exploration, not a bet.
- **E4.** Fork divergence: of 165 forks, 68 are active and 14 have diverged substantially. What do
  downstream adopters keep versus rip out? At n=14 this is a qualitative case study that generates
  hypotheses. It will be written up as such and never as a statistical result.

### H1's operationalisation is TypeScript-native, and this is not optional

Java's abstraction categories barely fire in a React codebase: Extract Interface, Extract
Superclass and Extract Class total **8 instances** across the entire history. Transliterating the
Hadoop category would have made H1 untestable.

The empirical probe (§7) shows why: **in React the abstraction mechanism is the custom hook**, not
the class hierarchy. 14 of 21 detected extractions are hooks, and several are *context* hooks —
`useLayoutContext`, `useNavContext`, `usePageContext`, `useDataListContext`. Extracting a context
hook is structurally the same act as Extract Interface: consumers stop depending on a concrete
parent and begin depending on an abstract contract.

| Hadoop (Java) | TypeScript/React equivalent | RefactoringMiner type | n (pilot) |
|---|---|---|---|
| Extract Interface / Superclass | custom hook, especially context hooks | `Extract Method` | 9 |
| Extract Class | extract module | `Extract Class` | 8 |
| Extract + relocate | hook extracted and relocated | `Extract And Move Method` | 12 |
| | | **abstraction** | **29** |

The hook signal cuts across the first and third rows rather than mapping to one type: of the 21
extractions whose extracted symbol name could be parsed, **14 match `use[A-Z]`** and are therefore
hooks. Whether an extraction counts as abstraction is decided by the refactoring type; the
`use[A-Z]` name test is a secondary attribute recorded per event, used to identify the
context-hook subclass that is the closest analogue to Extract Interface.
| Move Class | move module | `Move Class`, `Move And Rename Class` | 155 |
| Move Package | **move source folder** | `Move Source Folder` | 64 |
| | | **relocation** | **219** |

`Move Source Folder` has no Hadoop counterpart — Maven modules do not move that way — and it is
the single most architectural signal in the corpus (`packages/lib-ui/src → src/theme`,
`src/app → src/spa`). It must be in the filter.

---

## 3a. Corpus provenance — governance, motivation, and what they threaten

The pilot corpus is not a community project. **BearStudio is a company**, `start-ui-web` is a
product they publish for public use *and* consume internally on client work. Every tier-2 and
tier-3 candidate is the same shape: cal.diy, Twenty and Documenso are all company-owned,
VC-backed open source. Apache Hadoop is foundation-governed, multi-vendor and volunteer-staffed.
This difference is structural, not incidental, and it has three consequences.

### Threat 1 — governance confounds the cross-language comparison

If every TypeScript repo in the corpus is company-owned and the Java comparator is
foundation-governed, then **any Hadoop-versus-TypeScript difference is equally explainable by
governance as by language.** The design cannot currently separate them. This is the same class of
error as the connector-tier result in the Hadoop study: a variable that looks like the thing of
interest but is collinear with something else.

Two honest responses, and the design takes both:

1. **State it as a bound.** The comparison is "Apache-governed Java" versus "company-governed
   TypeScript", and no claim may attribute a difference to language alone.
2. **Add a governance-matched repo.** At least one foundation-governed JS/TypeScript project
   (OpenJS Foundation: Node.js, Electron, webpack, ESLint) enters tier 3 so that governance varies
   *within* the TypeScript arm. Without it, language and governance are perfectly confounded and
   the cross-language claim is not recoverable.

### Threat 2 — the decisions happen off-repo

In a company-owned project, architectural decisions are made in meetings, Slack and internal
planning. The repository records the *outcome*, not the deliberation. Apache's norm of
"if it didn't happen on the mailing list, it didn't happen" is precisely what made the Hadoop
mining viable.

This systematically **suppresses observable friction** and can manufacture a false null: a
change that took three weeks of internal argument appears in git as one clean PR merged in an
hour. Twenty-five percent of pilot PRs merge within the hour and the dominant author frequently
merges his own work — consistent with deliberation that happened elsewhere.

Consequence: `t_merge` and review-based measures are weak instruments in company-owned repos.
This is an additional reason the design leans on `t_build`, `survive` and `reverted`, which record
work actually done rather than discussion actually logged.

### Threat 3 — migration-driven change is a different phenomenon

A starter template's product *is* tracking the current frontend stack. The pilot history shows
continuous re-platforming: a V3 rewrite, Next.js app-directory migration, TanStack Start adoption,
Chakra → shadcn → base-ui, radix repackaging, ESLint → oxlint, prettier → oxfmt, MirageJS removal.

Moving a component because `base-ui` replaced `radix-ui` is **not** the phenomenon this study is
about. Hadoop has no analogue — Hadoop *is* the platform; it does not chase one.

**Operationalisation.** A refactoring co-occurring with a change to `package.json`,
`pnpm-lock.yaml` or `pnpm-workspace.yaml` is coded `migration_driven`. Measured on the pilot:

| | n | share |
|---|---|---|
| architectural-refactoring commits | 81 | |
| ...co-occurring with a dependency change | 19 | **23%** |
| ...internally motivated | 62 | 77% |

This is a **lower bound**: a migration spanning several commits trips the test only on the one
touching the manifest. `migration_driven` becomes a covariate in every model and a reported
stratum, not a filter — migration-driven refactoring is interesting, it is simply a different
question.

This threat generalises beyond the pilot. Fast-moving-ecosystem repos in general mix
externally-forced churn with internally-motivated design work; any TypeScript refactoring study
that ignores the distinction is measuring npm's release cadence.

---

## 4. Architecture

```
COLLECT      raw, immutable, cached — the only layer that touches the network
  ↓
DETECT       RefactoringMiner 3.1.4 — the only layer that decides "a refactoring happened"
  ↓
RECONSTRUCT  repo state at every commit — blob-cached; the only layer that touches git internals
  ↓
CLASSIFY     tier assignment + architectural filter — our contribution
  ↓
DERIVE       episodes · controls · covariates · outcomes → one fact table
  ↓
ANALYSE      survival models — ports of the existing Hadoop scripts

VALIDATE     κ labelling + mutation injection — hangs off DETECT, gates ANALYSE
```

### Detection is delegated

RefactoringMiner 3.1.4 is the detector. It is already vendored in this repo
(`RefactoringMiner/lib/RefactoringMiner-3.1.4.jar`). TypeScript support landed in 3.1.3
(2026-03-29, beta) and was completed in 3.1.4 (2026-05-24).

This is a significant improvement over hand-rolling a detector:

1. **Cross-language comparability.** Same tool, same taxonomy, same JSON schema on Hadoop and on
   TypeScript. The comparison holds the instrument constant, which is a far stronger external
   validity claim than "we replicated it with a different tool."
2. **`scripts/filter_architectural.py` ports nearly unchanged** — it keys on type names.
3. **`scripts/run_rm_safe.sh` transfers as-is.** Required, not optional: a single unchunked run
   over the full history timed out at 10 minutes, exactly the pathology that script was written for.
4. It removes the "why should we trust your detector" objection entirely.

### Classification is ours, and it is the contribution

RefactoringMiner does not know about client/server tiers. It reports *"a Move Class happened"*; it
cannot report *"and it crossed the contract boundary that breaks frontend and backend
simultaneously."*

Tier membership is computed by **reachability over the import graph**, never from paths. Seeds are
declared per repo; membership is derived. On the pilot: 304 files, 41 server-reachable, 283
client-reachable, **32 in both** — the shared contract. Only 4 of those 32 live in a path that
looks shared (`src/lib/`, `src/types/`); the rest sit in feature folders such as
`src/features/book/schema.ts`, imported by both `form-book.tsx` and `src/server/routers/book.ts`.
**A path-based rule would misclassify 88% of the contract surface.**

The three-level ordinal variable for H3 follows directly:

1. `tier-internal` — client-only or server-only
2. `cross-tier` — moves code between tiers
3. `contract-crossing` — touches a file in the shared set; the type-checker breaks on both sides

### State reconstruction is blob-cached

The naive approach parses 224,000 file-states across history. Git already content-addresses
everything, so identical files across commits share a SHA: the history contains only **5,180
unique `.ts`/`.tsx` blobs**, a **43× reduction**. Parse once per blob. The "expensive" time machine
costs minutes.

This is what makes the E2 outcomes (`survive`, `reverted`) computable at all.

### One language boundary

`symbols.ts` (ts-morph) is the only TypeScript component; it reads blob SHAs on stdin and writes
symbol tables as JSON on stdout, knowing nothing about the study. Everything else is Python,
because the entire existing analysis pipeline already is. Rewriting nine working scripts to
achieve language purity would buy nothing.

### Component layout

```
scripts/
  collect/     git_log.py       commits · authors · renames · co-authors · merges
               github_api.py    PRs · reviews · threads · timeline · checks · forks
  detect/      run_rm.sh        wraps run_rm_safe.sh, per-repo config
  reconstruct/ blob_cache.py    content-addressed parse cache
               import_graph.py  module graph at commit N
               tier_map.py      client / server / shared reachability
               symbols.ts       ts-morph symbol table  (only Node component)
  classify/    architectural.py TS-native filter (extends filter_architectural.py)
               boundary.py      the H3 ordinal variable
  derive/      episodes.py      grouping
               controls.py      matched ordinary changes            [G1]
               covariates.py    self-merge · discussion volume · tenure [G2]
               outcomes.py      t_build · t_merge · survive · reverted [E2]
  validate/    sample_frame.py  stratified labelling frame
               mutate.py        synthetic refactoring injection      [E1]
               kappa.py         agreement statistics
  analyse/     ports of blast_radius_model.py, friction_decomposition.py, …
```

Files stay in the 200–400 line band. Every stage reads and writes JSON, so any stage is
independently re-runnable and testable.

### Portability contract

Per-repo cost is one config file:

```yaml
# corpus/start-ui-web.yml
repo: BearStudio/start-ui-web
tiers:
  server: ["src/server/**"]
  client: ["src/routes/**", "src/layout/**", "src/components/**"]
alias:   { "@/": "src/" }
```

If onboarding a repo ever needs more than this, the harness has a leak and that is a bug. The case
most likely to break it is cal.diy's monorepo, which has many packages; that is a known risk to
test early.

### Failure handling

Per-commit failures are recorded as `failed` rows with a reason, never aborting a batch. Every
stage is resumable. Coverage is reported explicitly per range, as it was for Hadoop.

---

## 5. Controls, covariates, outcomes

### Matched control group [G1]

For every architectural episode, a matched ordinary change on change size (files + churn), era,
author tenure, and self-merge status. Mirrors the 400-ticket `control_tickets.json` from the
Hadoop study. Without a control there is no referent for "more friction" and the claim is not
measurable.

### Covariates present in every model from the first run

Non-negotiable, because this is exactly what retracted the Hadoop result:

- `log(discussion_volume)` — the variable that collapsed the structural-review effect from
  HR 0.69 (p=0.003) to HR 1.10 (p=0.51). It enters from the first model fit, never as a
  post-hoc robustness check.
- `self_merged`, `review_present`, `reviewer_count` [G2] — 25% of pilot PRs merge within an hour
  and the dominant author frequently merges his own work. A PR that was never independently
  reviewed and one that survived three rounds are not the same observation.
- `author_tenure`, `is_bot` (12% of PRs), `is_pair` (156 co-authored-by commits)
- `migration_driven` (§3a) — refactoring co-occurring with a dependency-manifest change. 23% of
  architectural commits in the pilot, and that is a lower bound.
- `governance` — foundation vs company, recorded per repo, constant within a repo and therefore
  usable only in cross-repo models.

### Outcome variables

| DV | Definition | Purpose |
|---|---|---|
| `t_first_touch` | issue/PR created → first commit | triage latency |
| `t_build` | first commit → PR opened | H2 build phase |
| `t_merge` | PR opened → merged | H2 merge phase |
| `survive` | commits until the refactoring is undone | **E2** |
| `reverted` | binary, ever undone | H4 |
| `rework` | CI check-run attempts on the PR | ports `ci_rework.py`; quality-vs-time |

`rework` ports the Hadoop CI-rework test directly. Hadoop used pre-commit CI runs as a proxy for
patch revisions; GitHub Actions check runs are the same instrument, and the pilot has two workflows
(`code-quality`, `e2e-tests`) exposing them through the checks API. The Hadoop result is that
architectural work needs more attempts but **not per unit of code** — the effect dies under a
change-size control. That control is therefore mandatory here too, not optional.

`t_build` and `t_merge` are derived from git and GitHub timestamps rather than Jira status
transitions. This **removes** a measurement caveat the Hadoop study had to carry: status-derived
timings were not comparable across module tiers that drive different workflows. Timestamps mean
the same thing in every repository.

The Hadoop decade analysis reached the same instrument choice independently and for a different
reason — Jira status hygiene collapsed from 93% to 16% at the 2019–20 GitHub migration, forcing a
workflow-independent git clock. Two independent routes to the same decision.

The corresponding TypeScript risk is **not** absent, merely different: CI providers, workflow files
and review tooling change over a repo's life, so any check-run-derived measure (`rework`) must be
tested for coverage decay across the window before it is trusted, exactly as the Hadoop study
tested its three decaying channels.

`survive` and `reverted` exist only because of state reconstruction. They are durability measures,
immune to the volunteer-queueing critique that dogged the cycle-time results — idle waiting cannot
inflate them.

### Inference

Cox proportional hazards, clustered by author, which addresses the non-independence threat in
`research_prospectus.md` §5. H3 enters as a single ordinal term. A **power analysis runs as a gate**
before tier 3 is touched: if the corpus cannot detect the effect size Hadoop found, that costs an
afternoon to learn rather than a month of compute.

---

## 6. Validation

Precision and recall come from two independent sources. Neither alone is sufficient.

### Precision — dual-rated κ

Stratified frame of ~180 items: all `Move Source Folder` events, all abstraction-category events,
all 10 `refactor:`-prefixed commits, plus a random sample of others.

Cohen's κ measures agreement between two raters corrected for chance agreement, and is the
standard the Hadoop study already promised itself — `research_prospectus.md` §5 lists
*"the codebook is drafted but not yet dual-rated to κ"* as an open threat. Publication bar is
κ ≥ 0.61 (substantial).

Protocol: a human collaborator dual-rates a ~60-item subset to establish human–human κ; an LLM
rates all ~180 and is calibrated against that subset; disagreements are adjudicated. The human
half gives the κ reviewers expect; the LLM half is what makes tiers 2 and 3 affordable.

### Recall — mutation injection [E1]

κ cannot tell you what the detector *missed*. So inject known refactorings: programmatically apply
an extract-hook, a cross-tier move, a source-folder move to real commits and check whether
RefactoringMiner recovers them. This yields a recall figure at **zero human labelling cost**, and
is an established technique in the refactoring-tool literature.

Together: precision from κ, recall from mutation, full confusion matrix.

### This validation is itself a contribution

RefactoringMiner's TypeScript support is two months old and has no independent validation in the
literature. This protocol produces the first, and §7 shows it has already found something.

---

## 7. Empirical findings from the pilot probe (2026-07-22)

Run: `run_rm_safe.sh` over the full history, 32 chunks, 120s stall watchdog.

| | |
|---|---|
| Commits analysed | 1,057 / 1,198 (**88%**, 3 chunks lost to hangs) |
| Refactorings detected | **2,214** |
| Commits with ≥1 refactoring | 302 |
| Architectural candidates | **198** across **65 commits** |

**Finding 1 — `Move Source Folder` is architectural gold.** 64 instances, real monorepo
restructures, no Hadoop counterpart. Added to the filter.

**Finding 2 — `Change Type Declaration Kind` is a suspected systematic false positive.** 160
instances, *all* reporting "interface to class". A traced instance
(`src/features/account/types.ts`) is `export type Account = User` — a plain type alias, neither
interface nor class. This appears to be an artefact of RefactoringMiner mapping TypeScript
declarations onto its Java-shaped model. **Excluded from the architectural filter pending
mutation-based confirmation**, and reported as a finding about RM's TS mode.

This is the same class of error as the 62%→25% precision collapse the Hadoop codebook caught, and
it surfaced in the first hour of looking at data. It is the argument for §6 in miniature.

**Finding 3 — abstraction is present but scarce.** 29 abstraction events vs 219 relocation. Small
on the abstraction arm; sufficient to validate the operationalisation, which is the pilot's job.

**Finding 4 — the RM→React decoding is deterministic, because the codebase is 100% function
components.** With no class components anywhere, RefactoringMiner synthesises a pseudo-class per
module and marks it explicitly: every class-level identifier carries a `__module__` suffix
(`addons.__module__`, `FieldInput.__module__`). Method-level entities then decode by React's own
naming rules, which are enforced by the framework and its linter rather than being convention:
hooks must begin with `use`, components must be capitalized to be treated as components in JSX.

| RM reports | Actually is | n | Share |
|---|---|---|---|
| `Class` | ES module / file | — | `__module__` suffix on all |
| `Method`, capitalized | React function component | 82 | 50% |
| `Method`, lowercase | plain function | 62 | 38% |
| `Method`, `use[A-Z]` | custom hook | 19 | 12% |

163 of 166 method-level refactorings decode unambiguously (**98%**). Three consequences:

- The mapping table is evidence-backed rather than asserted, which turns a write-up caveat into a
  defended methodological contribution.
- `Move Method` (32) splits into acts that are not equivalent: relocating a shared hook is
  architectural, relocating a private lowercase helper generally is not. The filter must
  distinguish them.
- It **independently corroborates Finding 2**. A codebase with no classes cannot contain 160 real
  "interface to class" conversions. Finding 2 was reached by tracing a single file; this reaches it
  from the language model of the codebase. Two independent routes to the same conclusion.

**Free consistency check.** Server-side code contains no React components. Any entity the tier
classifier assigns to the server tier while the name test identifies it as a component indicates a
bug in the classifier or the parse. This invariant costs nothing and runs on every commit.

**Known instrument caveats:**
- Unchunked runs over long ranges hang; chunking is mandatory.
- 88% coverage; report honestly per range.
- The `__module__` decoding is verified on a function-component codebase. Repos mixing in legacy
  class components need the check re-run, since `Class` would then be ambiguous between a real
  class and a module pseudo-class.

---

## 8. Research hygiene

- **Pre-registration** [E5] — hypotheses, operationalisations and model specifications committed
  and hashed before tier 3 is cloned. The commit hash is the timestamp.
- **Pseudonymisation** [E6] — wired in from day one, not retrofitted. 53 named contributors in the
  pilot alone; `scripts/pseudonymize.py` already exists and must be part of the pipeline before any
  data is published.
- **Data availability** — large intermediate JSON stays gitignored (`refminer*.json`, `rm_chunks/`
  already are); a manifest of checksums plus the scripts to regenerate is what gets committed.
- **Exploratory results are labelled as exploratory** in every artefact that reports them, not only
  in the paper.

---

## 9. What this study can and cannot claim

**Can:** that the Hadoop pipeline transfers to TypeScript with the instrument held constant; that
architectural refactoring is measurable in a full-stack TS codebase; that the client/server
contract boundary is machine-derivable and behaves as an ordinal friction variable; a validated
precision/recall characterisation of RefactoringMiner's TypeScript mode.

**Cannot:** anything about friction from the pilot corpus alone. start-ui-web has no meaningful
outcome variance. Every friction claim rests on tiers 2 and 3.

**Cannot, specifically because of corpus provenance (§3a):** attribute any Hadoop-versus-TypeScript
difference to *language* unless a governance-matched TypeScript repo is in the corpus. Without one,
language and governance are perfectly confounded.

**Known risks:**
- RM's TS support is new; §7 already found one false-positive class and there may be others.
- The abstraction arm is thin (n=29 in the pilot) and may remain thin in TS generally — if so,
  that is itself a reportable ecosystem difference rather than a failure.
- cal.diy's monorepo structure may break the one-file portability contract. It is also old enough
  to contain legacy class components, which would make the `__module__` decoding (§7, Finding 4)
  ambiguous; re-verify there before use.
- **Off-repo deliberation** (§3a) suppresses observable friction in company-owned repos and can
  manufacture a false null. `t_merge` and review-volume measures are weak instruments there; the
  design leans on `t_build`, `survive` and `reverted` in response.
- **Migration-driven churn** (§3a) mixes externally-forced re-platforming with internally-motivated
  design work. Measured at ≥23% of architectural commits in the pilot, controlled as a covariate,
  never silently filtered.
