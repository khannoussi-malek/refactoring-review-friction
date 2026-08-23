# V2 correction — drafts for review, not published

Nothing here has been posted to Zenodo or the manuscript. Three drafts,
as asked, for you to accept, edit, or reject before anything goes live.

---

## (a) Zenodo v2 version note

For the "Version notes" field when uploading the new version.

> **v2 corrects a privacy defect in v1.** v1's `jira-caches.zip` was
> published with a record description claiming developer email addresses
> had been replaced with salted pseudonyms; that step was never run, and the
> archive shipped 1,525 occurrences of 18 real addresses. This was found by
> the author, who pseudonymized the archive (`scripts/pseudonymize_caches.py`,
> verified zero real addresses remain) and rebuilt it as v2, replacing v1's
> two redundant copies of the data with one.

---

## (b) Corrected record description

The existing description (fetched verbatim from the live record via the
Zenodo API), with only the "Personal data" paragraph changed to make it
true, and nothing else touched. Diff-style below; the rest of the
description is unchanged and omitted for brevity — see the live record for
the full text.

**Before (false as published):**

> **Personal data.** Developer email addresses appearing in Apache commit
> metadata have been replaced with salted pseudonyms, following the practice
> of SEOSS 33. Commit hashes are unmodified, so every determination remains
> checkable against the public repositories.

**After (proposed):**

> **Personal data.** Developer email addresses appearing in the frozen Jira
> caches have been replaced with salted pseudonyms (`dev-<hash>@example.invalid`),
> following the practice of SEOSS 33. **v1 of this record shipped this step
> undone — 1,525 occurrences of 18 real addresses were published in error —
> and has been superseded by this version.** Commit hashes are unmodified,
> so every determination remains checkable against the public repositories.
> Jira display names and usernames (e.g. "Steve Loughran", `stevel`) are
> unchanged from v1 and are not pseudonymized; these are already public
> under the same accounts on issues.apache.org.

The last sentence is added, not implied by the original — it states plainly
that names are still real, since (b) only fixes the sentence that was false
and does not silently expand it to claim more privacy protection than v2
actually provides.

**Also correct the creator affiliation** (currently `null` on the live
record): set to `"Independent Researcher, Tunisia"`.

---

## (c) Manuscript correction-record entry

Matching the format of `README.md` §4 ("What did not hold" — Hypothesis /
Result / Named cause), extended with the "how it was found" the brief asked
for, since this entry isn't a hypothesis test and doesn't fit that table's
three columns cleanly on its own.

| What was claimed | What was actually true | Named cause |
|---|---|---|
| Zenodo record description: developer email addresses in the frozen Jira caches "have been replaced with salted pseudonyms" | v1's `jira-caches.zip` contained 1,525 occurrences of 18 real addresses, unpseudonymized | A pseudonymization step was documented as required in `deposit/DEPOSIT_CHECKLIST.md` before the archive was assembled and uploaded, and was never executed |

**How it was found.** Not by a reader or a reviewer — by a verification
pass the author ran against the record after publication, downloading the
live `jira-caches.zip` and scanning its extracted contents directly against
the pseudonymization claim, rather than assuming the claim held because it
was written down.

**What changed.** `scripts/pseudonymize_caches.py` was written and run
against a copy of the raw data; the corrected archive was rebuilt as
`jira-caches-v2.zip` (one representation, not v1's two); per-file digests
were regenerated into `deposit/MANIFEST-v2.json`/`.md`; v1's manifest was
marked superseded, not deleted. Zero real addresses remain, verified in
`deposit/PSEUDONYMIZATION_VERIFICATION.md`. Display names and Jira usernames
are unchanged from v1 in v2 — that is a separate, still-open scope question,
not folded into this correction.
