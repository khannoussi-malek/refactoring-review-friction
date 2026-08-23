# Pseudonymization verification — v2 correction

Run 2026-08-23. Verifies `scripts/pseudonymize_caches.py` against a copy of
the raw Jira cache data extracted from the published v1 Zenodo record
(10.5281/zenodo.21846139), outside this repository's tree. No raw data and
no pseudonymized output is committed anywhere in this repo — this file
records the process and the result, not the data.

## What was found in v1 (corrected count)

The session that discovered the gap reported 1,530 occurrences of 22
distinct addresses. That count is revised here after finding two more
false-positive shapes that a naive scan catches:

- Hadoop KMS provider URIs, `https@kms0{1,2}.example.com` (2 occurrences) —
  this is Hadoop's KMS client URI syntax (`kms://<scheme>@<host>:<port>/kms`),
  not an email.
- Azure ADLS Gen2 container URIs, `testcontainer@<account>.dfs.core.windows.net`
  (2 occurrences) — ABFS container@account addressing, not an email.

Corrected: **1,525 occurrences of 18 distinct real addresses** — the single
most frequent one accounts for 1,396 of those occurrences by itself; the
rest are personal Gmail/Yahoo/corporate addresses appearing far less often.
The previously-excluded categories (Java
`@InterfaceAudience`/`@InterfaceStability` annotation text, GitHub
`users.noreply.github.com` addresses) still stand as false positives, now
joined by the two above.

## Command

```
python3 scripts/pseudonymize_caches.py <raw_copy_dir> <pseudonymized_dir>
```

Run against a copy of the five `.jira_*` directories plus the nested
`jira-caches-v1.tar.gz`, extracted from the live `jira-caches.zip` on the
Zenodo record, in a scratch directory outside this repo. `raw_copy_dir` was
never written back to and no output was copied into the repo tree.

## Acceptance scan

Re-scanning by raw-text `grep` with the same RFC-5322-ish pattern used to
find the original leak returns 2 apparent hits post-pseudonymization:
`n@InterfaceAudience.Private` and `n@InterfaceStability.Evolving` in
`.jira_cache/HDDS-1333.json`. Traced to source: both are preceded by the
literal JSON escape sequence `\r\n` in the file's raw bytes — the "n" a
byte-level grep sees is the `n` inside `\n`, not a character adjacent to `@`
in the actual string. A proper JSON-parse-then-scan (decoding the escape
first, so `\r\n` becomes a real control character, not the letter `n`)
confirms these were never email-shaped content:

```
total email-shaped matches in decoded strings: 1580
matches NOT ending in @example.invalid:        0
```

Run identically against both representations present in v1 (the loose
`.jira_*` files and the nested `jira-caches-v1.tar.gz`) — same result, zero,
for each.

**Verdict: PASS.** Zero real addresses remain in the pseudonymized output.

## What was and was not touched (spot-checked)

- The single most-frequent real address maps to the same pseudonym
  consistently everywhere it appears — as `assignee`, `reporter`, and a
  comment author's `name` field (that developer's Jira username happens to
  equal their email address).
- `displayName` ("Steve Loughran") — **untouched**, confirmed identical
  before/after. Pseudonymizing display names was explicitly out of scope for
  this pass — see the scope note below and `deposit/V2_CORRECTION.md`.
- Issue `key`, `id`, and `created` timestamp — confirmed byte-identical
  before/after on a spot-checked file.

## Scope note: names are not addressed here

The same archive carries 14,272 `displayName` occurrences (190 distinct real
people, e.g. "Steve Loughran", "Anu Engineer") and 14,292 Jira-username
occurrences (196 distinct handles, e.g. `snemeth`) that this pass does not
touch. Whether those need pseudonymizing too, given they are also public on
`issues.apache.org` under the same accounts, is a separate decision — not
made here. See `deposit/V2_CORRECTION.md`.
