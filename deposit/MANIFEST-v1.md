# Jira cache archive — v1

**SUPERSEDED.** This archive's data was published live on Zenodo
(10.5281/zenodo.21846139) with 1,525 occurrences of 18 real developer email
addresses, unpseudonymized, despite the record description claiming
otherwise. See `deposit/PSEUDONYMIZATION_VERIFICATION.md` for the finding and
`deposit/MANIFEST-v2.md` for the corrected archive. The digests below still
describe this exact (unpseudonymized) file correctly — nothing here was
altered — they are kept as the historical record of what v1 actually was,
not as a recommendation to use it.

- **Archive**: `jira-caches-v1.tar.gz` (2.83 MB)
- **SHA-256**: `fcb705b664c248d0c4d32f69b854e10fd8b11c907a19c40333322e06d31b9a95`
- **Files**: 2,491 (32.11 MB uncompressed)
- **Source**: https://issues.apache.org/jira (Jira REST API v2)
- **API pulls**: 2026-07-19T00:27:37Z → 2026-07-19T20:04:44Z
- **Created**: 2026-07-25T04:49:20Z

| directory | files | MB | first pull | last pull |
|---|---:|---:|---|---|
| `.jira_cache` | 323 | 31.12 | 2026-07-19T00:27:37Z | 2026-07-19T02:06:49Z |
| `.jira_changelog` | 323 | 0.22 | 2026-07-19T04:07:11Z | 2026-07-19T04:10:46Z |
| `.jira_props` | 722 | 0.06 | 2026-07-19T19:30:13Z | 2026-07-19T19:38:48Z |
| `.jira_assignee` | 723 | 0.04 | 2026-07-19T19:57:11Z | 2026-07-19T20:04:44Z |
| `.jira_control` | 400 | 0.67 | 2026-07-19T04:17:08Z | 2026-07-19T04:21:49Z |

Per-file SHA-256 digests are in the JSON manifest alongside this file.

**These caches are not regenerable.** Jira is live: issues are edited, reopened and occasionally deleted, so a re-fetch returns a different state. Every statistical result in `results_dossier.md` is computed from this snapshot, which is why it is deposited rather than scripted.
