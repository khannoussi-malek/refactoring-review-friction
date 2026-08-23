# Jira cache archive — v2 (corrected)

**Supersedes v1** (`jira-caches-v1.tar.gz` / the `jira-caches.zip` published
on the live Zenodo record 10.5281/zenodo.21846139). v1's record description
claimed developer email addresses were "replaced with salted pseudonyms."
That step was never run before v1 was uploaded. See
`deposit/PSEUDONYMIZATION_VERIFICATION.md` for the discovery and the fix, and
`deposit/V2_CORRECTION.md` for the correction text drafted for the Zenodo
record itself.

- **Archive**: `jira-caches-v2.zip`
- **Built**: 2026-08-23, in `deposit/build/` (gitignored, not committed — see
  below)
- **SHA-256**: `fe67c6607e4ca818c88426a9e23bbdcb4c9c354e4b8da9afca5c9e1da36298f6`
- **MD5**: `7425ea95b02fe11e1e5b1247a1b4c0ec`
- **Size**: 3,817,713 bytes (compressed); 2,491 files, 35,556,731 bytes
  uncompressed
- **Representation**: loose files only — **one** copy of the tree, not two.
  v1 shipped the same 2,491 files both loose and nested inside
  `jira-caches-v1.tar.gz`, which is why the unpseudonymized addresses were
  exposed twice within the same record.

| directory | files | bytes |
|---|---:|---:|
| `.jira_cache` | 323 | 34,185,645 |
| `.jira_changelog` | 323 | 336,124 |
| `.jira_props` | 722 | 75,756 |
| `.jira_assignee` | 723 | 42,215 |
| `.jira_control` | 400 | 916,991 |

Per-file SHA-256 digests (2,491 entries, computed against the pseudonymized
files) are in `MANIFEST-v2.json` alongside this file.

## What changed from v1

Email-shaped values (RFC-5322-ish pattern — this is what actually appeared:
Jira `assignee`/`reporter` fields, and any embedded elsewhere) are replaced
with salted pseudonyms of the form `dev-<12 hex>@example.invalid`, via
`scripts/pseudonymize_caches.py`. The mapping is one-way: the salt was
random per run, printed once, and never retained.

**Unchanged from v1, byte-for-byte:** commit hashes, issue keys (`key`,
`id`), timestamps, and — deliberately, pending a separate decision —
`displayName` (190 distinct real names, 14,272 occurrences) and Jira
usernames (196 distinct handles, 14,292 occurrences). This archive removes
the addresses v1's own description promised would be removed. It does not
remove real names. See `deposit/V2_CORRECTION.md` for that open question.

## Second artifact: `replication-package-v2.zip`

v1's `replication-package.zip` also carried a nested
`deposit/jira-caches-v1.tar.gz` — byte-identical (SHA-256 `fcb705b6...`) to
the unpseudonymized archive, a **third** copy of the same leak inside the
same record. Rebuilt with exactly one substitution: that nested tar.gz is
replaced with the pseudonymized version, at the same path and filename.
Every other one of the package's 222 entries is byte-for-byte identical to
v1 (`diff -rq` against the extracted original confirms this — one file
differs, 221 don't).

- **Archive**: `replication-package-v2.zip`
- **Built**: 2026-08-23, in `deposit/build/` (gitignored, not committed)
- **SHA-256**: `97179a960901f1a6b74f2593506657efabd0e8e3e52bd301e63a126c73d6cf41`
- **MD5**: `a5946e91ba23600b31e65a2687ae6c51`
- **Size**: 10,357,939 bytes; 222 entries

**Pseudonym consistency across both v2 artifacts**: the substituted tar.gz
came from the same pseudonymization run (same salt, same address→pseudonym
cache) as `jira-caches-v2.zip`'s loose files — spot-checked directly:
`stevel@apache.org` maps to `dev-88fa84f2add1@example.invalid` in both.
Anyone cross-referencing the two files in the v2 deposit sees the same
person as the same pseudonym throughout.

**Acceptance scan**: JSON-decode-then-scan across every `.json` file in the
rebuilt package (its own files plus the substituted tar.gz's contents) finds
1,624 email-shaped matches, all ending in either `@example.invalid` (this
correction's pseudonyms) or `@pseudonymized.invalid` (a pre-existing,
unrelated synthetic domain from `scripts/pseudonymize.py`'s own self-check
fixtures, already present and already-synthetic in v1). Zero real addresses
remain.

## Where the built zips actually are

`deposit/build/jira-caches-v2.zip` and `deposit/build/replication-package-v2.zip`
are **not committed** — `deposit/build/` is gitignored. Both contain real
pseudonymized data and are meant to be uploaded to Zenodo by hand as a new
version of the existing record. The checksums above were computed directly
against those files at build time.
