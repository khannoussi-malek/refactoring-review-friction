# Task 13 — do RefactoringMiner entity identifiers survive the pipeline?

Read-only inspection. Nothing modified.

**Verdict: everything the SATD design needs is present in the raw output and
fully recoverable from committed artifacts. No re-run of RefactoringMiner over
the 8,919 commits is required.**

---

## 1. What the raw output carries

`refminer_all.json` — 8,919 commits, **51,861 refactorings**, 248,336 location
records. Each detection is:

```json
{"type": ..., "description": ..., "markup": ...,
 "leftSideLocations": [...], "rightSideLocations": [...]}
```

and each location record is:

```json
{"filePath": ..., "startLine": ..., "endLine": ...,
 "startColumn": ..., "endColumn": ...,
 "codeElementType": ..., "description": ..., "codeElement": ...}
```

Survival across all 51,861 detections:

| identifier | left side | right side | notes |
|---|---:|---:|---|
| **file path** | **100.0%** | **100.0%** | 112,701 / 135,635 location records |
| **line range** (`startLine`/`endLine`) | **100.0%** | **100.0%** | plus columns |
| **`codeElement`** | 54.9% | 57.1% | present when the location *is* a named entity |
| **fully-qualified class name** | ✅ | ✅ | two routes — see below |
| **method signature** | ✅ | ✅ | for `METHOD_DECLARATION` locations |

**Fully-qualified class names — two independent routes.**
1. `codeElement` on `TYPE_DECLARATION` locations is already the FQN, e.g.
   `org.apache.hadoop.hdds.cli.GenericCli`.
2. The `description` string carries them too, e.g.
   `Extract Interface org.apache.hadoop.hdds.cli.GenericParentCommand from classes [org.apache.hadoop.hdds.cli.GenericCli]`.
   `filter_architectural.py` already parses these with its `FQN` regex.

**Method signatures** are present and typed. The most common
`codeElementType` is `METHOD_DECLARATION` (58,749 of 248,336 locations), and its
`codeElement` is a full signature including parameter types and return type:

```
public getMountPoints(path String) : List<String>
```

`codeElement` is 55–57% rather than 100% because 45% of location records are
statement-level (`EXPRESSION_STATEMENT` 48,306, `VARIABLE_DECLARATION_STATEMENT`
39,772, `IF_STATEMENT` 9,247, …) where no named entity exists. For
`TYPE_DECLARATION` and `METHOD_DECLARATION` — the two the SATD design needs —
it is populated.

---

## 2. Where each field is dropped

Two aggregation steps, and the loss is total at the first one.

### Drop point: `scripts/filter_architectural.py`, lines 100–106

```python
episodes.append({
    "sha1": sha,
    "arch_types": arch,      # list of type STRINGS only
    "n_arch": len(arch),
    "cross_module": cross_module,
    "issue_key": keys.get(sha),
})
```

The loop reads `r["type"]` and `r["description"]`, uses the description only to
compare source/destination *packages*, and **never copies any location record
into the episode**. So at this single step the pipeline loses:

- every `filePath` (left and right)
- every line range
- every `codeElement` — FQNs and method signatures alike
- the `description` string itself, so even the parseable FQNs go

What survives into `architectural_episodes_all.json` (349 episodes) is
`sha1`, `arch_types`, `n_arch`, `cross_module`, `issue_key` — commit-level,
type-level, with no entity anywhere.

### Partial recovery already in the pipeline: `scripts/episode_files.py`

Written later, this re-reads the raw JSON and recovers **file paths only**
(`paths_of()` takes `loc["filePath"]` from both sides), producing
`episode_files.json`: 349 shas → sorted unique file paths. It deliberately
discards line ranges and `codeElement`.

That is why `blast_radius_model.py` can attribute episodes to Maven modules:
module attribution needs paths, and paths are the one identifier that was
recovered. Nothing downstream — `build_frame`, the ticket aggregation, the
joint models — ever sees an entity.

### Second aggregation: commit → ticket

`blast_radius_model.build_frame` groups by `key` with
`n_files=("n_files","sum")`, `abstraction=("abstraction","any")` etc. By this
point only counts remain; this step drops nothing further because nothing
entity-level was left to drop.

---

## 3. Recoverability — the answer that matters

**Yes, fully, with no re-run.**

- All 349 architectural episode SHAs are present in `refminer_all.json`
  (**349/349 verified**).
- `refminer_all.json` is 134.9 MB and committed, and holds every location record
  for all 51,861 detections, not just the architectural ones.
- Re-deriving `(FQN, method signature, file path, line range)` per architectural
  refactoring is a single pass over that file, filtering by the same type sets
  `filter_architectural.py` already defines.

Verified on a sample episode: `a406f6f60e`, 43 refactorings, 1 architectural
(`Extract Interface`), recovering left `GenericCli.java:33–97`
`org.apache.hadoop.hdds.cli.GenericCli` and right `GenericCli.java:32–97`, plus
both FQNs from the description.

The release-range files (`refminer_310_320`, `refminer_320_330`,
`refminer_340_343`, `refminer_wide`) provide redundant coverage.

**Consequence for the SATD design: the 51,861 detections do carry over.** The
entity identifiers were never lost from disk, only from the aggregate the
analysis scripts read. What is needed is a new extraction pass over
`refminer_all.json` — not 8,919 commits of re-mining.

**One caveat to carry forward.** Line ranges are valid *only against the
commit's own parent/child trees*, so any SATD-to-refactoring linkage must anchor
on `(filePath, codeElement)` and treat line numbers as within-commit
coordinates. `codeElement` for a `TYPE_DECLARATION` is stable across moves; the
line range is not.
