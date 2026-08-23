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

## Where the built zip actually is

`deposit/build/jira-caches-v2.zip` is **not committed** — `deposit/build/`
is gitignored. It contains the real pseudonymized data and is meant to be
uploaded to Zenodo by hand as a new version of the existing record. The
checksums above were computed directly against that file at build time.
