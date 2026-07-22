# Design — Architectural refactoring friction in full-stack TypeScript

**Date:** 2026-07-22
**Status:** design, pending approval
**Predecessor:** the Apache Hadoop RQ1 feasibility study in this repo (`README.md`, `results_dossier.md`)

---

## 1. What this is

The Hadoop study established a pipeline, a defended finding (abstraction is the locus of
refactoring friction, and the cost is in *building*), three self-rejected mechanisms and one
self-corrected claim. Its stated weakness is external validity: one project, one language,
one governance model.

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

### Outcome variables

| DV | Definition | Purpose |
|---|---|---|
| `t_first_touch` | issue/PR created → first commit | triage latency |
| `t_build` | first commit → PR opened | H2 build phase |
| `t_merge` | PR opened → merged | H2 merge phase |
| `survive` | commits until the refactoring is undone | **E2** |
| `reverted` | binary, ever undone | H4 |

`t_build` and `t_merge` are derived from git and GitHub timestamps rather than Jira status
transitions. This **removes** a measurement caveat the Hadoop study had to carry: status-derived
timings were not comparable across module tiers that drive different workflows. Timestamps mean
the same thing in every repository.

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

**Known instrument caveats:**
- Java-shaped vocabulary: a React component is reported as a `method`, a module as a `Class`. The
  write-up needs an explicit mapping table.
- Unchunked runs over long ranges hang; chunking is mandatory.
- 88% coverage; report honestly per range.

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

**Known risks:**
- RM's TS support is new; §7 already found one false-positive class and there may be others.
- The abstraction arm is thin (n=29 in the pilot) and may remain thin in TS generally — if so,
  that is itself a reportable ecosystem difference rather than a failure.
- cal.diy's monorepo structure may break the one-file portability contract.
- Single-vendor governance in TS repos differs from Apache's; the volunteer-queueing dynamics that
  shaped the Hadoop interpretation may not transfer, which is precisely why `survive` was added as
  a queueing-immune outcome.
