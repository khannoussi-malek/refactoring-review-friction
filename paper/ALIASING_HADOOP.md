# Does the Hadoop social measure share the start-ui-web aliasing defect?

**Answer: no, and this was already measured. The Hadoop measure keys on the git
author *name*, its raw aliasing is worse than start-ui-web's, and the effect on
every derived measure is null.**

Read-only determination, 2026-07-30. No analysis was re-run.

## What the Hadoop measure keys on

`scripts/social_centrality.py` builds its per-module author history with

```
git -C <repo> log --all --format=%at|%an -- <module dir>
```

— `%an`, the git **author name**. Not email, and not GitHub login. So the
start-ui-web defect cannot occur in the same form: that bug was one person
appearing as two *emails* (`ivan@dalmet.fr` and
`ivan-dalmet@users.noreply.github.com`), and grouping by name merges exactly that
pair. The Hadoop measure has the mirror-image exposure instead — one person
appearing under several *name spellings* behind one email.

## That mirror-image exposure is real, and larger

`scripts/sui/ALIASING_NOTE.md` (2026-07-22, `scripts/sui/identity.py`) measured
it. Hadoop is worse than start-ui-web on raw aliasing:

* 1,035 emails resolve to 797 identities — **238 merged**
* **96 emails span multiple author names, covering 27,307 commits = 35.2% of the
  corpus** — e.g. `stack@apache.org` as both "Michael Stack" and "stack" (2,766
  commits); `szetszwo@apache.org` under three spellings of Tsz-Wo Nicholas Sze
  (1,971).

## But the impact on the derived measures is null

Concentration recomputed for all **112 modules with ≥20 commits**, by author name
(what the script uses) against by email (which collapses name variants):

| | by NAME | by EMAIL | |
|---|---|---|---|
| mean `top1_share` | 0.1545 | 0.1495 | −3.2% |
| mean `bus_factor` | 8.46 | 8.56 | |
| mean `n_authors` | 87.2 | 91.0 | |

**Paired Wilcoxon on `top1_share`: p=0.3651.** 67 of 112 modules differ, with no
systematic direction and a maximum absolute delta of 0.19.

The mechanism is stated in the note and is the generalisable point: **aliasing
severity scales inversely with contributor count.** Splitting one person in two
moves `top1_share` a great deal in a 53-author repository dominated by one
developer, and negligibly in an ~800-author repository whose top contributor
holds 3.6% of commits. The same data defect is critical in one corpus and
irrelevant in the other, so aliasing must be measured per corpus rather than
assumed present or absent.

## Nothing depends on it in either direction

The maintainer-concentration hypothesis is already dead on other grounds —
collinear with module size, rho = −0.86 (`README.md` §4, `93056ae`). So even a
material aliasing effect would have changed no surviving claim. This note exists
so the threats section can say that from evidence instead of leaving a reader to
wonder whether the same bug ran twice.

## One exposure the earlier note does not cover

`social_centrality.py` uses a **third** identity namespace for its
`reviewer_pool` variable — the Jira comment author, not git at all — and the two
arms read it by different paths:

* architectural tickets: `c["author"].get("name")` from
  `.jira_cache/<KEY>.json`
* ordinary controls: `c.get("author")` from `.jira_control/<KEY>.json`

Jira usernames are a separate namespace from both git names and git emails, and
these two extractions are not verified to yield the same kind of token. **This
was never checked.** It matters little in practice: `reviewer_pool` is the one
social variable that is null everywhere — `triage~reviewer_pool` rho = 0.0010,
p = 0.988 (`social_centrality.json`) — so no claim rests on it. Recorded as an
unverified difference between the two arms rather than a measured threat.

## Correction preserved from the earlier note

An earlier claim in the 07-22 working session — that Hadoop "has the same bug"
and that `social_centrality.py` therefore understated concentration — **was
wrong**, and `scripts/sui/ALIASING_NOTE.md` says so. The raw aliasing is present
and larger than in start-ui-web; its effect on the derived measures is null. The
claim had been made from the alias counts before the impact was measured.

## Sources

| claim | source |
|---|---|
| keys on `%an` | `scripts/social_centrality.py`, `module_commit_log()` |
| 238 merged identities; 96 emails, 27,307 commits, 35.2% | `scripts/sui/ALIASING_NOTE.md`, `scripts/sui/identity.py` |
| name-vs-email null, Wilcoxon p=0.3651, 112 modules | `scripts/sui/ALIASING_NOTE.md` |
| start-ui-web 58.1% → 67.2% top-author share | `scripts/sui/ALIASING_NOTE.md`; `SUI_FINDINGS.md` |
| maintainer concentration dead, rho = −0.86 | `README.md` §4; `93056ae` |
| `reviewer_pool` null, rho = 0.0010, p = 0.988 | `social_centrality.json` |
