# Audit — Priority 3: the load-bearing numbers

Every figure below was recomputed from primary artifacts with code written for
this audit that imports nothing from `scripts/`. Where possible I re-derived from
the raw sources (`refminer_all.json`, the `hadoop` clone, the 38 upstream bare
clones) rather than from the prior agent's JSON outputs.

**Summary: the arithmetic is sound. Every headline number reproduces. The
problems are not in the computation — they are in what the paper claims the
computation licenses.**

---

## 1. The headline: Spearman rho

### 1.1 Recomputation — CONFIRMED

Own Spearman implementation (average ranks for ties), over
`paper/ticket_side_38.json`:

| quantity | reported | recomputed | verdict |
|---|---|---|---|
| rho, all usable projects | −0.010 | **−0.0097** | CONFIRMED |
| n, usable | 33 | **33** | CONFIRMED |
| rho, truncated-history excluded | −0.062 | **−0.0616** | CONFIRMED |
| n, sensitivity | 30 | **30** | CONFIRMED |
| passing median | 55.5% | **55.53%** | CONFIRMED |
| dropped median | 53.2% | **53.24%** | CONFIRMED |
| passing range | 0.04–68.6% | **0.040–68.63%** | CONFIRMED |
| dropped range | 29.5–84.8% | **29.47–84.79%** | CONFIRMED |
| Syncope | 84.8% ticket-side, 36.0% commit-side | **1,399/1,650 = 84.788%**, **35.980%** | CONFIRMED |

The n=33 set is exactly `{ticket_side_frozen is not None} ∩ {not small_denominator}`
— I enumerated it and it matches the exclusion lists in the artifact
(small denominator: pinot, dubbo, rocketmq; no tracker record: shardingsphere,
skywalking).

### 1.2 The exclusion rule was NOT tuned — CONFIRMED

The brief asked whether the three truncated-history exclusions were chosen after
seeing the result. I swept the threshold across its whole range:

| `share_cited_above_snapshot` ≤ | n | rho | excluded |
|---|---:|---:|---|
| 0.30 | 28 | **−0.120** | calcite, hudi, kylin, ozone, ranger |
| 0.40 | 30 | −0.062 | hudi, kylin, ozone |
| **0.50 (used)** | 30 | **−0.062** | hudi, kylin, ozone |
| 0.60 | 30 | −0.062 | hudi, kylin, ozone |
| 0.65 | 31 | **+0.022** | hudi, kylin |
| 0.70–0.90 | 32 | +0.015 | kylin |
| none | 33 | −0.010 | — |

Every threshold gives a rho between −0.12 and +0.02. **The choice of 0.50 does
not favour the conclusion** — it is a plateau, and the most extreme value
(−0.120) would have made the paper's case *more* strongly. The rule is stated in
the script before the result is read and is insensitive across its plausible
range. **CONFIRMED as principled.**

### 1.3 UNSUPPORTED — the inferential claim is stronger than n=33 allows

No confidence interval or p-value for rho appears in `PAPER.md`,
`paper/table3_ticket_side.md`, or `paper/numbers.md` §10c. I computed them.

```
rho = -0.0097, n = 33   ->  95% CI (Fisher z)  [-0.352, +0.335]
rho = -0.0616, n = 30   ->  95% CI            [-0.413, +0.305]
Mann-Whitney, passing vs dropped ticket-side: U = 124, z = -0.075, p ≈ 0.94
```

The paper says, in three places:

* §4.3 heading: "**the two rates are uncorrelated**"
* §4.3: "**the commit-side rate carries essentially no information about the
  ticket-side one**"
* abstract: "shows the two rates are uncorrelated"

The data are consistent with a true correlation anywhere in **[−0.35, +0.34]**. A
rho of 0.3 is not "essentially no information" — it is a moderate association
that would materially change how a corpus-selection bar behaves. What the data
support is *"we could not detect an association"*, which at n=33 is a weak
statement, not *"there is none"*.

This is the classic absence-of-evidence-as-evidence-of-absence overreach, and it
is the paper's headline sentence. **UNSUPPORTED as phrased.** The numbers are
right; the inference is oversold, and the CI that would show this is nowhere in
the manuscript.

The same applies, more mildly, to "the two medians differ by 2.3pp": the
difference is not tested anywhere, and it is not significant (p ≈ 0.94).

---

## 2. The estimator — the most serious finding

### 2.1 The reported validation — CONFIRMED as arithmetic

| quantity | reported | recomputed | verdict |
|---|---|---|---|
| n validated | 12 | **12** | CONFIRMED |
| mean absolute error | 0.45pp | **0.4503pp** | CONFIRMED |
| worst case | 2.14pp (Kylin) | **2.1413pp, Kylin** | CONFIRMED |

Per-project errors run 0.00pp (knox, ranger) to 2.14pp (kylin). The arithmetic is
correct.

### 2.2 DIVERGENT — the reported validation does not cover the estimator that
produced Table 3

There are **two** approximations stacked in Table 3:

1. **number-capping** — using `|{cited keys ≤ N}| / N` instead of intersecting
   with the real key set;
2. **snapshot substitution** — using the frozen public corpus's `N_frozen`
   instead of a live `N`.

The reported 0.45pp validates **only (1)**: it compares `τ̂` computed with
`N_live` against the published exact rate, also at `N_live`. Table 3's numbers
use `N_frozen`. The snapshot substitution is never validated in the manuscript,
yet it is the step that carries the risk.

It **is** measurable from committed artifacts, and I measured it — the end-to-end
error, `|TRR_frozen − TRR_published|` over the same 12 projects:

| project | end-to-end error |
|---|---:|
| kylin | **11.91pp** |
| ranger | 2.93pp |
| ozone | 2.24pp |
| drill | 1.63pp |
| zookeeper | 0.81pp |
| phoenix | 0.61pp |
| knox | 0.37pp |
| hive | 0.29pp |
| sqoop | 0.16pp |
| tez | 0.11pp |
| hbase | 0.04pp |
| oozie | 0.01pp |
| **mean** | **1.76pp** |
| **max** | **11.91pp** |
| mean excluding kylin | 0.84pp |

**The applicable error is 3.9× the reported mean and 5.6× the reported maximum.**
§4.3 introduces the 0.45pp figure with "**The estimator is validated before it is
used**", immediately before applying the *other* estimator. `threats.md` §6.1
lists snapshot truncation as failure mode 2 and flags affected projects in the
table — so the mechanism is disclosed — but the magnitude is never quantified
anywhere, and the number the reader is given is the smaller one.

**Verdict: DIVERGENT.** Not fabricated; the smaller of two available and clearly
distinguishable error figures is presented as validating the larger claim.

### 2.3 UNSUPPORTED — the validation and application ranges do not overlap at all

The brief asked directly: is there evidence the estimator holds on the failing
half? I checked.

```
validation set (12 projects), commit-side range:  82.6% .. 98.3%
applied-only set (21 projects), commit-side range: 10.5% .. 78.1%
projects in the applied set inside the validated range: 0 of 21
```

**Zero overlap.** Every project that carries the headline rho lies outside the
range on which the estimator was checked. All 12 validation projects are also
Hadoop-ecosystem with a shared commit convention; the 21 include Attic projects
and GitHub-migrated ones with quite different tracker dynamics.

A fair counter-argument exists and the author should make it if he keeps the
claim: the estimator's error mechanism is tracker-numbering density, which has no
obvious reason to depend on commit-side hygiene, and within the 12 the error does
not track the commit-side rate (rho = −0.16, n=12). But that is an argument, not
a validation, and **the manuscript makes neither**.

**The headline rho rests on an extrapolation of an unvalidated estimator into a
range where it has never been checked. This is not stated anywhere in the paper.**

One thing that *would* have helped and was computed but not used: the frozen
substitution tracks the live measurement within 2.93pp for 11 of the 12 projects
(§2.2 table). That is a real, favourable, reportable validation of exactly the
step in question — and it is absent from the manuscript.

---

## 3. Kylin's two values

| claim | verdict |
|---|---|
| live 12.0% | **CONFIRMED** — `paper/ticket_coverage.json`: 709 / 5,931 = 11.954% |
| frozen 0.04% | **CONFIRMED** — 2 / 4,989 = 0.04009% |
| cause: cited keys numbered above the frozen tracker's count | **CONFIRMED in mechanism** — max cited KYLIN number is 6,090 against a frozen tracker of 4,989 |
| "**100%** of the keys its repository cites are numbered above the snapshot" | **DIVERGENT — it is 709 of 711 = 99.72%** |

The 100% claim appears in `results.md` line 89 and `paper/numbers.md` line 620.
It is **self-contradicting in its own sentence**: if 100% of cited keys were above
the snapshot the numerator would be 0, not 2, and the rate would be 0.00%, not
0.04%. Table 3's cell shows "100%" because the generator formats
`share*100` with `:.0f` — defensible in a table, but the prose repeats it as an
exact statement.

**Disclosure adequacy — my assessment: borderline, and the table is the weak
point.** In `PAPER.md` the caveat travels with the number in both §4.3 and
threats §6.1. But `paper/table3_ticket_side.md` is a standalone generated file
that a reader may well encounter alone, and in it Kylin appears as a **`pass`**
row with ticket realisation "**0.0%**". The note column says "100% of cited keys
postdate the snapshot", which does not tell an uninitiated reader that the same
project measures 12.0% on the live tracker, or that 0.0% is an artefact of a
truncated repository rather than a traceability finding. Three other rows (pinot,
skywalking, shardingsphere) carry the same "100%" note with the same rounding.

---

## 4. Entity tracking — independently re-derived from raw sources

This is the check I ran hardest, because the 26.8% → 89.7% flip decides a GO/NO-GO.

I re-implemented the whole measurement from `refminer_all.json` and the `hadoop`
clone, **using a deliberately different path→FQN rule** (first conventional
package-root segment, rather than the last `java`/`javaNN` source-root segment)
and a different description regex.

| quantity | reported | my independent re-derivation | verdict |
|---|---|---|---|
| git renames of `*.java` at 50% | 1,825 | **1,825** | CONFIRMED |
| FQN-preserving (excluded) | 1,025 | **1,025** | CONFIRMED |
| not a type declaration (excluded) | 255 | **256** | CONFIRMED (±1, rule difference) |
| FQN-changing (denominator) | 545 | **544** | CONFIRMED (±1) |
| explained by an RM identity edge | 489 | **488** | CONFIRMED (±1) |
| **coverage** | **89.7%** | **89.7%** | **CONFIRMED** |
| unfiltered coverage (the NO-GO figure) | 26.8% | **26.7%** | CONFIRMED |
| top-level identity edges | 577 | 578 | CONFIRMED (±1) |

The ±1 differences come from a single path where the two source-root rules
disagree; they do not move any reported figure at one decimal place.

Recomputed from the artifact and internally consistent:

| quantity | reported | recomputed | verdict |
|---|---|---|---|
| sweep 30 / 50 / 70 / 90% | 84.4 / 89.7 / 93.7 / 92.6 | 84.4 / 89.7 / 93.7 / 92.6 | CONFIRMED |
| Move Package coverage | 91.6% (185/202) | 185/202 = 91.58% | CONFIRMED |
| Move Source Folder only | 71.7% (33/46) | 71.74% | CONFIRMED |
| chains 1/2/3 ops | 91.3 / 83.0 / 83.3 | 355/389, 39/47, 10/12 | CONFIRMED |
| terminals at HEAD | 28.8% | 135/468 = 28.85% | CONFIRMED |
| terminals at own commit | 95.1% | 445/468 = 95.09% | CONFIRMED |
| mined window coverage | 83.1% | 8,376/10,083 = 83.07% | CONFIRMED |
| residual split 27/14/9/6 | sums to 56 | 545−489 = 56 ✓ | CONFIRMED |

### 4.1 Is the filter principled? — YES

The exclusion of FQN-preserving renames is **definitional, not a tuning knob**: if
a class's fully-qualified name is unchanged, there is no identity change for an
FQN-anchored chain to survive, so no edge is expected. I verified independently
that the 1,025 excluded renames really do have identical package + class name —
two different implementations agree exactly on the count.

The `package-info.java` / `module-info.java` exclusion is likewise definitional:
those files declare no type, so RefactoringMiner has no class to emit an edge for.

**The rule is stated in the script's docstring and in the memo, and the memo
volunteers that the first run produced 26.8% and was wrong.** That disclosure is
to the author's credit.

**Caveat the memo does not draw.** The flip depends entirely on measuring identity
in **FQN space**. A design anchored on **file paths** — which is what this
repository's own `episode_files.py` and `blast_radius_model.py` actually use —
faces the 26.8% figure, because a source-root move does break a path-anchored
chain. The memo says the excluded renames need no edge "because nothing an
FQN-anchored chain depends on moved", which is correct but does not tell the
reader that the successor design must therefore be FQN-anchored, not path-anchored.

### 4.2 Tuning history is not in the repository

`scripts/entity_tracking.py` was introduced in a single commit (`3c0c24d`) already
containing the filter. The sequence — 26.8% first, filter added, 89.7% after —
exists only in the memo's prose. Nothing in git corroborates the order of events.
Not a defect (the memo discloses it), but it cannot be independently verified.

---

## 5. The κ bounds — exhaustively verified

I did not use the closed-form bound. I **enumerated every integer 3×3
contingency table** consistent with each pair of margins and computed κ for all
of them.

| bucket | feasible tables | reported | brute-forced | verdict |
|---|---:|---|---|---|
| flagged (5,5,10) × (3,12,5) | 180 | [−0.455, +0.491] | **[−0.4545, +0.4909]** | CONFIRMED |
| unflagged (1,1,18) × (2,1,17) | 8 | [−0.099, +0.780] | **[−0.0989, +0.7802]** | CONFIRMED |
| pooled (6,6,28) × (5,13,22) | 574 | [−0.370, +0.680] | **[−0.3699, +0.6804]** | CONFIRMED |
| flagged, rule-4-first (5,5,10) × (3,7,10) | 230 | [−0.600, +0.840] | **[−0.6000, +0.8400]** | CONFIRMED |
| pooled, rule-4-first (6,6,28) × (5,7,28) | 504 | [−0.290, +0.946] | **[−0.2903, +0.9462]** | CONFIRMED |

**The load-bearing claim — that no pairing on the flagged bucket reaches
κ = 0.491 — is confirmed exhaustively over all 180 feasible tables.** The maximum
is exactly 0.4909.

The premise is also confirmed: I checked **every historical version** of
`codebook_labeling.md` (there is one, `de657c3`) and columns A and B are empty for
all 40 rows. `codebook_results.md` records exactly (5,5,10) and (1,1,18).
**κ genuinely is not computable from what exists.**

---

## 6. Keyword-rule precision and recall — CONFIRMED

Recomputed from `paper/llm_rater_labels.json` (40 labels, numbers 1–40 complete):

| quantity | reported | recomputed |
|---|---|---|
| LLM flagged margins | 3 / 12 / 5 | **S=3, I=12, C=5** |
| LLM unflagged margins | 2 / 1 / 17 | **S=2, I=1, C=17** |
| LLM precision | 15% | **3/20 = 15%** |
| LLM recall | 60% | **3/5 = 60%** |
| human precision | 25% | 5/20 = 25% (from `codebook_results.md`) |
| human recall | 83% | 5/6 = 83.3% |
| "over-counts roughly fourfold" | — | human **4.0×** (20/5); LLM **6.7×** (20/3) |

The "roughly fourfold" phrasing uses the human figure; `LLM_RATER_PILOT.md` §5
correctly widens it to "four to six times". Consistent. **CONFIRMED.**

Separately, I recomputed the matcher precision from `paper/matcher_labels.json`:
**195 genuine / 200 = 97.5%**, with the residual being 4 reverts + 1 backport —
exactly as published. **CONFIRMED from a committed artifact.**

---

## 7. Provenance — the check is weaker than its verdict suggests

### 7.1 What `scripts/check_provenance.py` actually does

I read it. For each "distinctive" numeric token in the manuscript it tests
**`if tok in body`** — a raw substring search against the text of
`paper/numbers.md`.

It does **not**:

* open, run, or even look at any script;
* verify that the number in `numbers.md` denotes the same quantity;
* verify that a cited commit hash exists;
* verify that a cited artifact contains the value.

`paper/numbers.md` is a hand-written prose file by the same author. **The gate is
satisfied by typing the number into `numbers.md`.** "175 sourced, 0 unsourced" is
therefore a statement about textual self-consistency, not about provenance.

### 7.2 Three tokens pass by coincidence — measured

I re-implemented the tokeniser and tested which "sourced" tokens match
`numbers.md` **only as a substring of a longer, unrelated number**:

| token | manuscript claim | what it actually matched in `numbers.md` | real provenance? |
|---|---|---|---|
| `0.86` | `intro.md`: "collinear with module size, **rho = −0.86**" | `rest_reached_patch = 0.86232` — an unrelated proportion | **NONE. UNSUPPORTED** |
| `930` | `threats.md`: "contaminated with **930** commits on other branches" | commit hash `93056ae` | **NONE. UNSUPPORTED** |
| `5.5` | `taxonomy.md`: section heading `## 5.5` | `15.5%` / `55.5%` | not a measurement — tokeniser defect |

The `5.5` case also shows the exclusion list is stale: `NOT_MEASUREMENTS` was
updated with §3.2–3.4, §4.6 and §7.1–7.5 when new sections were added, but the
renumbered `## 5.5` was missed.

So the true count is at best **172 sourced, 2 unsourced, 1 miscounted** — and the
2 unsourced are real claims in the paper with no provenance row.

### 7.3 Twenty numbers traced by hand

Sampled 20 numeric tokens from `PAPER.md` (seeded) and traced each myself. Six of
the draws were section numbers or years and are reported as such.

| # | number | claim | how far I could follow it |
|---:|---|---|---|
| 1 | 195/200 = 97.5% | matcher precision | **to a committed artifact — recomputed from `paper/matcher_labels.json`** |
| 2 | ×1.54 [0.97, 2.43] p=0.068 | abstraction, fully adjusted | **to a committed artifact — `full_adjustment.json` gives 1.5355 [0.969, 2.4333] p=0.0679** |
| 3 | 97.0% | Hive commit-side | **to a committed artifact — 17,670/18,213 from `traceability_probe.json`** |
| 4 | 83.9% / 12.0% | Kylin both channels | **to committed artifacts — 812/968 and 709/5,931** |
| 5 | 74.8% | James commit-side | **to a committed artifact** |
| 6 | 69.0% | Knox ticket-side | **to a committed artifact** |
| 7 | 63.6% / 44.8% | probe medians | **to a committed artifact — `probe_summary.json`** |
| 8 | 2.14pp | estimator worst case | **to a committed artifact — `ticket_side_38.json`** |
| 9 | 55.5% / 84.8% | passing median, Syncope | **to a committed artifact** |
| 10 | 89.7% | entity coverage | **to raw sources — re-derived from `refminer_all.json` + clone** |
| 11 | 0.491 | κ ceiling | **re-derived by brute force** |
| 12 | 735,669 | GHS repositories | **to the cited paper** |
| 13 | 97.13 / 96.34 / 90.06 / 87.12 / 41.98 | SEOSS rates | **to the cited paper's Table 2** |
| 14 | 26.2% | Hadoop single-key | **prose only** — `numbers.md` §2 gives 7,404/28,290, which I verified arithmetically (26.17%), but `citation_rate.py` prints to stdout and emits no artifact, so no committed file records the 7,404 as a result |
| 15 | 0.33 | HBase max vendor share | **prose only** — appears in `replication/REPLICATION.md`; **not present in `external_wrapper_tier.json`**, the artifact `numbers.md` cites |
| 16 | 1,035 → 797 identities | Hadoop aliasing | **prose only** — in `paper/ALIASING_HADOOP.md`; no machine-readable artifact on disk carries it |
| 17 | p = 0.3651 | paired Wilcoxon on aliasing | **prose only** — same |
| 18 | −0.86 | maintainer-concentration collinearity | **NO provenance row at all** (§7.2) |
| 19–20 | `4.1`, `6.2` etc. | section numbers | not measurements |

**Result: 13 of the 15 genuine measurements I drew are traceable to a committed
artifact or a cited source and were recomputed. Four (26.2%, 0.33, 1,035/797,
p=0.3651) are traceable only to hand-written prose in another repository file.
One (−0.86) has no provenance anywhere.**

Supporting checks that came out clean:

* All 32 commit hashes in `numbers.md` that refer to **this** repository resolve
  to real commits. (The 39 that do not resolve locally are upstream Apache HEAD
  shas and one sampling seed — expected.)
* All 21 script paths and all 23 artifact paths cited in `numbers.md` exist.
* **All 38 pinned upstream `head_sha` values resolve to real commits in the
  Apache repositories, and `git rev-list --count` reproduces the published
  `commits_scanned` exactly for all 38.** This validates the entire §1 corpus
  table against primary source and is the strongest provenance result in the
  repository.

---

## 8. Verdict table

| claim | verdict |
|---|---|
| rho = −0.010, n=33 | CONFIRMED |
| rho = −0.062, n=30 | CONFIRMED |
| exclusion threshold not tuned | CONFIRMED |
| "the two rates are uncorrelated" / "essentially no information" | **UNSUPPORTED** (CI [−0.35, +0.34], never reported) |
| median difference 2.3pp presented without a test | **UNSUPPORTED** (p ≈ 0.94) |
| Syncope 84.8% / 36.0% | CONFIRMED |
| estimator mean 0.45pp, worst 2.14pp | CONFIRMED as arithmetic |
| that validation covers the estimator used in Table 3 | **DIVERGENT** — true end-to-end error 1.76pp mean / 11.91pp max |
| estimator validated where it is applied | **UNSUPPORTED** — zero range overlap |
| Kylin 12.0% live / 0.04% frozen, and the mechanism | CONFIRMED |
| "100% of cited keys postdate the snapshot" | **DIVERGENT** — 99.72% (709/711) |
| entity tracking 89.7%, sweep, Move Package 91.6%, chains, 83.1% window | CONFIRMED by independent re-derivation |
| the FQN filter is principled, not tuned | CONFIRMED |
| κ bounds, all five | CONFIRMED by exhaustive enumeration |
| κ not computable from the recorded evidence | CONFIRMED |
| keyword precision/recall, over-counting factor | CONFIRMED |
| "175 sourced, 0 unsourced" | **DIVERGENT** — 2 genuinely unsourced, 1 miscounted |
| −0.86 collinearity figure | **UNSUPPORTED** |
| 930 lost-commit figure | **UNSUPPORTED** |
