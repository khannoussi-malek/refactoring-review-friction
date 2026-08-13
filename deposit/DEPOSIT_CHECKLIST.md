# Zenodo deposit — prepared, not published

**Nothing has been uploaded, published or submitted.** This file records what is
ready, what is verified, and the six things that require the author's own
credentials or a decision only the author can make.

Prepared 2026-08-05.

## Ready and verified

| item | state |
|---|---|
| `jira-caches-v1.tar.gz` | 2,833,843 bytes, present |
| archive SHA-256 | `fcb705b664c248d0c4d32f69b854e10fd8b11c907a19c40333322e06d31b9a95` — **re-verified 2026-08-05 against `MANIFEST-v1.md`, matches** |
| per-file digests | `MANIFEST-v1.json`, 2,491 entries |
| deposition metadata | `deposit/zenodo.json` |
| licence | CC-BY-4.0 on the compilation (see `LICENSE` for what that does and does not cover) |
| citation record | `CITATION.cff` at the repository root |

Re-verify the archive at any time with:

```
shasum -a 256 deposit/jira-caches-v1.tar.gz
```

## What remains, and why each needs the author

1. **ORCID.** `CITATION.cff` carries a commented-out `orcid:` line and
   `zenodo.json` has no ORCID in `creators`. An ORCID is what makes the DOI
   resolve to a person rather than a name string, and inventing or guessing one
   is not an option. Register at https://orcid.org if there is none, then fill
   both files.

2. **Affiliation.** `zenodo.json` says "Independent researcher". That matches
   `README.md` §1 ("built by one person … alongside full-time employment"). If a
   host institution should be named instead, change it before minting — it is
   part of the DOI record and awkward to correct afterwards.

3. **Upload and publish.** Zenodo needs an authenticated session; this cannot be
   done from here and should not be. Either:
   * **Web:** https://zenodo.org/uploads/new → upload `jira-caches-v1.tar.gz` →
     paste the fields from `zenodo.json` → **Reserve DOI** before publishing, so
     the DOI can go into the manuscript and `CITATION.cff` first.
   * **API:** `POST https://zenodo.org/api/deposit/depositions` with
     `zenodo.json` as the `metadata` object, then upload the file, then publish.
     Needs a personal access token with `deposit:write` and `deposit:actions`.

4. **Back-fill the DOI in four places once reserved.** The DOI does not exist
   until step 3, so these cannot be done now:
   * `CITATION.cff` — add an `identifiers:` block with the DOI.
   * `deposit/MANIFEST-v1.md` — add the DOI line.
   * `README.md` §10 — the reproducibility section names the archive but not a
     DOI.
   * the manuscript's data-availability statement.

5. **Decide on pseudonymisation before publishing, not after.** The archive
   carries Jira author and assignee display names. They are already public on
   issues.apache.org, so republishing them is defensible, and
   `scripts/pseudonymize.py` exists if the pseudonymised variant is preferred.
   **This is a decision, not an oversight** — but it must be taken before the DOI
   is minted, because a Zenodo record's files cannot be changed after
   publication, only superseded by a new version. If in doubt, deposit the
   pseudonymised archive as v1 and keep the identified one local.

6. **Repository topic.** The GitHub repository already carries a description and
   the topics `empirical-software-engineering`, `mining-software-repositories`,
   `refactoring` and `traceability`. Only `reproducibility` is missing. It could
   not be added from here — the available `gh` credential is a different account
   (`malek-ci-hub`) and the topics endpoint returns HTTP 404 for it. One command,
   from an account with write access:

   ```
   gh repo edit khannoussi-malek/refactoring-review-friction --add-topic reproducibility
   ```

## What is deliberately not deposited

* **`refminer_all.json` and the other detector outputs** (134.9 MB and up). They
  are regenerable from public repositories with `scripts/run_rm_safe.sh` at a
  pinned RefactoringMiner version, so they are a build artifact rather than a
  frozen observation. The Jira caches are the opposite: not regenerable at all,
  which is the whole reason for the deposit.
* **The 38 probe clones.** Public Apache repositories; `paper/traceability_probe.json`
  pins a `head_sha` per project, so any re-clone is exactly diffable.
* **The Public Jira Dataset itself.** It has its own DOI (10.5281/zenodo.15719919)
  and is referenced, not redistributed.
