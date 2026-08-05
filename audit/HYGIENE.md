# Audit — Priority 5: repository hygiene

---

## 1. Commit authorship — clean

```
git log --format='%h | %an <%ae> | %cn <%ce>' d0bc98e..HEAD
```

| commit | author | committer |
|---|---|---|
| e23b902 | malek khannoussi \<khannoussimalek@gmail.com\> | same |
| 45aebc8 | malek khannoussi \<khannoussimalek@gmail.com\> | same |
| ca3b8cd | malek khannoussi \<khannoussimalek@gmail.com\> | same |
| 152a477 | malek khannoussi \<khannoussimalek@gmail.com\> | same |
| 7cc485b | malek khannoussi \<khannoussimalek@gmail.com\> | same |
| 3c0c24d | malek khannoussi \<khannoussimalek@gmail.com\> | same |

**One identity, the author's personal one, matching `git config user.email`. No
work or organisational account, no bot identity, no co-author trailer.**

Worth noting for the author's awareness rather than as a defect: the `gh` CLI in
this environment is authenticated as a **different** GitHub account,
`malek-ci-hub`. No commit carries it and no GitHub write succeeded (§4), but the
credential is present in the environment and could attribute a future push or API
write to the wrong identity.

**Verdict: CONFIRMED clean.**

---

## 2. `CITATION.cff` — FAILS CFF 1.2.0 validation

I fetched the official schema
(`citation-file-format/citation-file-format@main/schema.json`) and checked the
file against it. `pyyaml` and `jsonschema` are not installed in this environment,
so I validated the structure against the schema's own `required` lists and
`enum`s by hand rather than programmatically — the two defects below are
unambiguous.

Top level is fine: `required: ['authors', 'cff-version', 'message', 'title']` —
all present. `license-url` is a valid top-level key.

**Defect 1 — invalid `type` value.**

```yaml
references:
  - type: dataset          # <- not in the CFF 1.2.0 enum
    title: The Public Jira Dataset
```

The schema's `definitions.reference.properties.type.enum` does **not** contain
`dataset`. The valid values for this case are **`data`** or **`database`**.
Confirmed directly against the schema.

**Defect 2 — missing required `authors` on a reference.**

```
definitions.reference.required = ['authors', 'title', 'type']
```

The Public Jira Dataset reference has `type`, `title`, `doi` and `notes` — and no
`authors`. This is a hard schema violation.

It is also the more serious of the two in substance: the dataset is
**CC-BY-4.0**, which requires attribution of the creators in derivative material,
and this dataset supplies **every denominator in Table 3**. The authors are
**Lloyd Montgomery, Clara Lüders and Walid Maalej**.

**Defect 3 — attribution completeness (not a schema violation).** The
RefactoringMiner reference lists Tsantalis alone. He is the principal author, so
this is legal and conventional, but the project has substantial named
contributors.

**Consequence:** GitHub's "Cite this repository" widget and `cffconvert` will
both reject or degrade on this file. Since the file exists specifically to make
the work citable, that is self-defeating.

**Verdict: DIVERGENT — the file does not validate.**

---

## 3. `LICENSE` — one internal contradiction, one upstream-attribution gap

### 3.1 The archive is placed in two mutually exclusive buckets

`LICENSE` line 10 puts **all of `deposit/`** under CC-BY-4.0:

> TEXT, FIGURES AND DERIVED DATA — … Everything under … `deposit/` …

`LICENSE` line 19, under the heading **"NOT COVERED BY EITHER"**, then says:

> `.jira_*/` and `deposit/jira-caches-v1.tar.gz` are responses from the Apache
> Software Foundation's public Jira …

And `deposit/zenodo.json` says something different again:

> The CC-BY-4.0 licence applies to this compilation and its manifest, **not to the
> underlying Apache issue content**.

Three statements, two of them incompatible, about the licence of the single file
that is about to be deposited under a DOI. A reuser cannot determine what they
may do with `jira-caches-v1.tar.gz`.

The *substance* of the intended position is defensible — the compilation and
manifest are the author's contribution; the underlying Apache issue text is ASF
content redistributed for reproducibility. But `LICENSE` as written does not say
that; `zenodo.json` does. **This must be reconciled before the deposit is
published, because the Zenodo record's licence field is not editable after
minting.**

### 3.2 Upstream licences — no conflict found

| upstream | its licence | repo's treatment | conflict? |
|---|---|---|---|
| Apache Jira issue content | ASF / contributor licence agreement | carved out in `LICENSE`, redistribution justified for reproducibility | **no**, subject to §3.1 being fixed |
| The Public Jira Dataset (Zenodo 15719919) | **CC-BY-4.0** — verified on the deposit page | `LICENSE` says "carries its own licence, consult that deposit"; derived file `estimates_by_org.json` is re-licensed CC-BY-4.0 by the repo | **no licence conflict** (CC-BY permits this) but see below |
| RefactoringMiner | MIT | `LICENSE` states the output is data about repositories, not a derivative of the tool | **no** — correct |
| Apache project git histories | Apache-2.0 | not committed; only shas are recorded | **no** |

**Attribution gap.** CC-BY-4.0 requires attribution of the creator in adapted
material. `estimates_by_org.json` — the derived file that supplies every Table 3
denominator — carries **no attribution field of any kind** (I checked: its top-level
keys are `validation`, `catalogues`, `repos`, `projects`; no source, licence, DOI
or author key). Attribution exists in `LICENSE` prose and in `paper/numbers.md`,
which is probably sufficient in practice, but the natural place — inside the
artifact, and in `CITATION.cff` — is where it is missing.

**Verdict: DIVERGENT on §3.1; attribution gap on §3.2.**

---

## 4. Nothing was published externally — CONFIRMED

| check | result |
|---|---|
| `deposit/` change set | only `DEPOSIT_CHECKLIST.md` and `zenodo.json` added; tarball and both manifests untouched since 2026-07-25 |
| Archive integrity | SHA-256 matches `MANIFEST-v1.md` exactly; all 2,491 member files match their per-file digests |
| Minted DOI recorded anywhere | none — the only DOI in `deposit/` is the *cited* Public Jira Dataset DOI |
| Checklist's own statement | "**Nothing has been uploaded, published or submitted.**" — consistent with the artifacts |
| GitHub repository topics (live read) | `empirical-software-engineering`, `mining-software-repositories`, `refactoring`, `traceability` — **`reproducibility` absent**, i.e. the one attempted write did not land, exactly as the prior report disclosed |
| `zenodo.json` placement | deliberately **not** `.zenodo.json` at the repository root, with a comment explaining that a root file would be auto-consumed by Zenodo's GitHub integration — a correct and thoughtful precaution |

**Verdict: CONFIRMED. No external publication occurred.**

---

## 5. Other hygiene observations

* **`paper/numbers.md` §9g still carries the withdrawn "median candidate near
  35%"** with no annotation. §10b withdraws it 400 lines later. Same
  correction-visibility problem as `CORPUS_FEASIBILITY.md`
  (`audit/RULE_COMPLIANCE.md`, rule 7).
* **`scripts/check_provenance.py`'s `NOT_MEASUREMENTS` list is stale**: §5.5 was
  created in `taxonomy.md` during this work and never added, so a section number
  is being counted as a measurement.
* **The 38 probe clones are not retained.** They were recreated in a scratch
  directory outside the repository and are not part of the deliverable, so
  `scripts/ticket_side_38.py` cannot be re-run by a reader without ~38 clones and
  the network patience to survive GitHub throttling. The pinned shas make it
  *possible*; nothing records that it took four attempts and an HTTP/1.1
  downgrade to obtain hbase.
* **No `.gitignore` entry was added for `audit/`** — this audit's own output is
  untracked and the author should decide whether to commit it.

## 6. An uncommitted, already-staged change to `.gitignore` — not mine

At the end of the audit `git status` showed:

```
M  .gitignore        <- staged (in the index), not committed
?? audit/
```

```diff
-
+.claude/
```

**I did not make this change.** I ran no `git add` and edited no file outside
`audit/`. The file's mtime is 05:06, during the audit session. It is almost
certainly a tooling or hook side effect adding `.claude/` to the ignore list.

It matters because it is **staged**: the next `git commit` in this working tree
will sweep it into whatever commit the author is making, with no mention of it in
the commit message. Two things follow for the author:

1. Decide deliberately whether `.claude/` should be ignored, and commit it on its
   own if so.
2. Check `git diff --cached` before the next commit. The prior work's six commits
   were all made with `git add -A`, which would have picked up exactly this kind
   of stray staged change without anyone noticing.

I have left it staged and untouched, per the do-not-fix rule.
