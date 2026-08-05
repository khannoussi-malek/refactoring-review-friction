# Task 18 — can an entity be followed across refactorings?

**Verdict: GO, with a stated ceiling.** A class identity survives Move Class and
Move Package in RefactoringMiner's output well enough to anchor an entity-level
design. It does **not** survive at the rate a naive reading of
`paper/ENTITY_IDENTIFIERS.md` would suggest, and the binding constraint turns out
not to be the detector at all — it is the completeness of the commit range the
detector is run over.

Measured 2026-08-05 on the Hadoop corpus, `scripts/entity_tracking.py` (`3c0c24d`),
output `paper/entity_tracking.json`. Every number below comes from that one run.

Regenerate with:

```
python3 scripts/entity_tracking.py --repo hadoop --rm refminer_all.json \
    --out paper/entity_tracking.json
```

---

## 1. The question, and why `ENTITY_IDENTIFIERS.md` did not answer it

`paper/ENTITY_IDENTIFIERS.md` (`2259129`) established that RefactoringMiner's raw
output **carries** fully-qualified class names — 100% of location records have a
file path, `codeElement` is populated on every `TYPE_DECLARATION`, and the FQNs
are recoverable from `refminer_all.json` without re-mining.

Carrying an identifier is not the same as chaining one. The design needs to
observe a symptom against class `A` at time *t₀* and detect an architectural
refactoring of *the same class* at *t₁*, by which time it may be called `B`, sit
in a different package, or both. That requires an unbroken sequence of edges
`A → … → B`. Nothing previously measured whether those edges exist.

## 2. Method — an oracle that is not the detector

Asking RefactoringMiner whether RefactoringMiner found the moves is circular. The
oracle here is **git's own rename detection** over the same 8,919 commits.

A top-level Java class lives in a file whose path is its FQN. So a class that
moves or is renamed produces a *file* rename that git can find independently. For
every such rename the test is: did RefactoringMiner emit a class-level identity
edge in that commit whose two FQNs match the two paths? If yes the identity is
recoverable; if no, the entity silently changes name and any chain anchored on it
breaks there.

**Identity edges** are the three refactoring types that map one existing class
onto one continuing class: `Move Class`, `Rename Class`, `Move And Rename Class`.
`Change Type Declaration Kind` keeps the FQN and is a no-op (22 instances).
`Extract Class / Superclass / Interface / Subclass` create a class — they are
births, not identity edges (361 instances). `Split Class` and `Merge Class` fork
and join identity, so "the same entity" stops being well defined; there are 4 in
the whole corpus and they are excluded from chains.

**Three filters, each of which would otherwise manufacture a failure.**

1. **Top-level classes only.** A nested class (`Outer.Inner`) has no file, so the
   oracle cannot see it. 173 of the 750 parsed identity edges are nested and are
   excluded; 577 are top-level. A further 12 descriptions did not parse, all of
   them non-Java artefacts of the C/native tree (`Rename Class c_api renamed to
   syscall`).
2. **FQN-changing renames only.** Hadoop moves whole source roots —
   `src/main/java` → `src/test/java`, `src/main/java` → `src/main/java8` — and
   git renames every file underneath while the package and class name stay
   exactly as they were. **1,025 of 1,825 java renames (56.2%) are of this kind.**
   They need no edge, because nothing an FQN-anchored chain depends on moved.
   Counting them would have produced a spurious 26.8% and a false NO-GO; that was
   the first result this analysis produced, and it was wrong.
3. **`package-info.java` and `module-info.java` excluded.** They are not type
   declarations, so the detector has no class to emit an edge for. 255 renames
   fall here (including git pairing a real class against a `package-info`).

That leaves **545 FQN-changing renames of real top-level classes** as the
denominator, at git's default 50% similarity threshold.

## 3. Result — 89.7% of identity changes carry an edge

| git similarity threshold | java renames | FQN-preserving | not a type | **FQN-changing** | explained by an RM edge | **coverage** |
|---|---:|---:|---:|---:|---:|---:|
| 30% | 1,893 | 1,026 | 258 | 609 | 514 | **84.4%** |
| **50%** (git default) | 1,825 | 1,025 | 255 | **545** | **489** | **89.7%** |
| 70% | 1,747 | 1,021 | 253 | 473 | 443 | **93.7%** |
| 90% | 1,566 | 981 | 245 | 340 | 315 | **92.6%** |

The sweep is the point: coverage rises as the oracle gets stricter, which is what
it must do if the misses at a loose threshold are git's false pairings rather than
the detector's omissions. At 30% git accepts pairs sharing barely a third of
their content; at 90% it accepts near-identical files. The 84.4 → 93.7 climb says
the residual is shared between the two error sources, not concentrated in one.

**The reverse direction.** 88 of the 577 top-level identity edges (15.3%) have no
matching git rename. These are the opposite error: RefactoringMiner tracked a
class through a change large enough that git gave up on the rename. They are not
failures of the design — they are cases where the detector is *better* than the
oracle, and they are the reason the coverage figure above is a lower bound.

## 4. Move Package specifically — the case the brief asked about

The fear was that a package-level move would be reported *instead of* the
per-class moves, so a chain would hit a `Move Package` record and lose every
entity inside it. **That is not what happens.**

| commits carrying | commits | FQN-changing renames | with a per-class edge | coverage |
|---|---:|---:|---:|---:|
| a package-level op (`Move`/`Rename`/`Merge`/`Split Package`) | 19 | 202 | 185 | **91.6%** |
| `Move Source Folder` only | 42 | 46 | 33 | **71.7%** |
| all bulk-move commits | 61 | 248 | 218 | 87.9% |

Package-level moves are **accompanied** by per-class edges at 91.6%, slightly
*above* the corpus-wide rate. The worked example is `9cbd76cc7`: alongside
`Move Package org.apache.hadoop.hdfs.procedure to org.apache.hadoop.tools.fedbalance`
the detector emits 12 individual class edges, including
`Move And Rename Class org.apache.hadoop.hdfs.procedure.BalanceProcedureConfigKeys
moved and renamed to org.apache.hadoop.tools.fedbalance.FedBalanceConfigs`. The
only unexplained rename in that commit is the package's `package-info.java`,
which is not a class.

`Move Source Folder` is weaker at 71.7%, but on **n = 46** renames, and it is a
build-layout event rather than a design one — most of what it moves keeps its
FQN and never enters the denominator at all.

## 5. Chains — 91% survive one operation, 83% survive two or three

Following each entity's FQN through successive changes:

| operations survived | chains | fully tracked by RM | share |
|---:|---:|---:|---:|
| 1 | 389 | 355 | **91.3%** |
| 2 | 47 | 39 | **83.0%** |
| 3 | 12 | 10 | **83.3%** |
| 4 | 1 | 1 | 100.0% |

Chains are short: of the 449 entities that move at all, 389 (86.6%) move exactly
once and 13 move three or more times. Per-link coverage is 89.7%, so independent links would
give 0.897² = 80.5% at two operations; the observed 83.0% is slightly better,
which says the links are not independent — an entity the detector tracks cleanly
once tends to be tracked cleanly again. That is the favourable direction and it
is what makes long chains survivable in principle. **It is also thin evidence: 47
chains at length 2, 12 at length 3.**

RefactoringMiner's own identity graph, read without the oracle, gives the same
shape: 567 edges, 10 FQNs reused as a source (a name recreated after its bearer
moved away), and a length distribution of 403 / 51 / 12 / 2 across 1–4
operations.

**Chains land on real files.** 445 of the 468 chain terminals (95.1%) resolve to
a file that exists in the tree of the commit that produced them. The chain
arithmetic is not producing names that never existed.

## 6. The constraint that actually binds — and it is not the detector

Only **135 of 468 terminals (28.8%)** correspond to a file present at HEAD,
against 12,579 Java files in the tree. That gap is not a chaining failure. It has
two causes, and the second is the one that matters for the design:

* classes are deleted, and a class that moved in 2019 and was removed in 2023
  correctly has no file at HEAD;
* **the mined corpus is not the full history.** The 8,919 mined commits cover
  **8,376 of the 10,083 HEAD-reachable commits (83.1%)** whose committer date
  falls inside the mined window, and 543 mined commits are not on HEAD at all.
  A move that happened in one of the ~1,700 unmined commits is invisible, and the
  chain breaks there with no signal.

**This is the finding to carry into the design.** Per-link detector coverage is
89.7%; per-link *corpus* coverage is 83.1%. The corpus is the weaker link, and
unlike the detector it is under the researcher's control. A study that mines only
the commits it thinks are interesting — architectural episodes, or commits
touching a flagged entity — will lose identity at a far higher rate than 10% per
operation, and will lose it silently.

**Design consequence, stated as a requirement:** the refactoring detector must be
run over *every* commit in the observation window, not over a sampled subset, and
the coverage of that run must be reported per year, because
`SUI_FINDINGS.md` already established that chunked detector loss clusters (75 of
81 commits in one year absent, against 2–8% elsewhere).

## 7. What the residual is

The 56 unexplained FQN-changing renames at the 50% threshold, split **mechanically**
on the two FQNs — no rater adjudicates this:

| split | n | reading |
|---|---:|---|
| same class name, different package | 27 | a `Move Class` the detector did not emit — the genuine misses |
| unrelated names (name similarity < 0.6) | 14 | git pairing an added file with a deleted one; no move occurred |
| same package, similar name | 9 | a `Rename Class` not emitted, e.g. `ScmBlockLocationTestIngClient` → `ScmBlockLocationTestingClient` |
| different package, similar name | 6 | a `Move And Rename Class` not emitted |

Splitting the 14 "unrelated names" cases into git false pairings and real
detector misses would require reading the diffs and coding a judgment. **That is
manual coding by a single rater with no κ available, so it is not done**
(`README.md` §8). The mechanical split is reported instead, and the reader can
see that the worst case — treating all 56 as detector misses — is the 89.7%
already quoted.

Two of the 27 "package-only" cases are a path artefact rather than a move:
`org.apache.hadoop.security.token.org.apache.hadoop.security.token.DelegationTokenIssuer`
is a file committed at a duplicated directory path and later corrected.

## 8. Threats

**The oracle is not ground truth.** git rename detection misses moves whose
content changed by more than the threshold (which is why 88 RM edges have no git
rename) and invents moves between similar unrelated files (which is why 14
residuals pair unrelated names). Both directions are reported rather than assumed
away, and the threshold sweep is the sensitivity analysis. There is no
independent gold set of "true" class moves for Hadoop, and constructing one would
need manual coding this study cannot validate.

**Top-level only.** 173 of 750 identity edges (23.1%) involve a nested class and
are outside the measurement entirely. If a design anchors on nested classes, none
of the above applies to it, and the same test would have to be redone with a
different oracle — nested classes have no file, so git cannot see them at all.

**One project, one language, one detector version.** Hadoop, Java,
RefactoringMiner 3.1.4. The TypeScript pilot found a detector defect at
`Change Type Declaration Kind` (`paper/RM_TYPESCRIPT.md`, upstream issue #1124),
and TypeScript support was two months old at measurement. **Nothing here
transfers to the TypeScript corpus** and the same test would have to be re-run
there.

**The mined window is 2018-03-18 to 2026-02-12**, so this measures the detector's
behaviour on eight years of one project's recent history, not on its whole
history.

## 9. Verdict

**GO for the entity-level leg**, on these terms:

1. Class identity is recoverable across Move Class, Rename Class and Move And
   Rename Class at **89.7%** per operation, and across **Move Package at 91.6%** —
   the package case, which was the specific worry, is the stronger one.
2. Chains are short (86.6% of moving entities move exactly once) and survive at
   **83%** through two and three operations.
3. The design must **mine every commit in the window**. At 83.1% corpus coverage
   the mined range, not the detector, is the weaker link, and its losses are
   silent and clustered.
4. Any per-entity result must carry the ~10% per-operation identity loss as a
   measurement-error term, in the direction that **attenuates** an interval
   measure: a broken chain drops the pair, it does not fabricate one. Losses are
   therefore conservative for a positive finding and fatal for a null one, and a
   null result from an entity-anchored interval cannot be reported without a
   power calculation that carries this term.

**What this verdict does not license.** It says the entity leg is *achievable*.
It says nothing about whether the violation-symptom anchor is detectable
(`prereg/RESOLUTION_GATE.md`), nor about the novelty margin, which
`PROJECT_STATE.md` §5 records as **not assessed** for the current anchor.
