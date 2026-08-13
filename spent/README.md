# Quarantine — HBase and Phoenix

**These four files are not held-out data and they are not results. They are
quarantined, and the distinction matters.**

`PROJECT_STATE.md` §3 held HBase and Phoenix in the held-out corpus and flagged
them "at risk". On 2026-07-30 the flag was resolved by dropping the held-out
corpus from nine projects to **seven** and moving their artifacts here.

## What was and was not observed

**No outcome was ever observed.** The frozen tier rule (vendor share ≥0.40 plus
the 90th-percentile dependents guard, `314845c`) flagged **zero modules** in
either project, so no prediction was possible and the test stage never ran. No
`.test.json` exists for either, and no timing statistic was computed or printed
for either, at any point (`replication/REPLICATION.md`, "HBase and Phoenix flag
nothing — no prediction possible").

**But the files are one operation from an outcome.** They are keyed on the same
ticket identifiers and align exactly:

| file | records | content |
|---|---:|---|
| `hbase.git.json` | 11,415 | ticket key → first citing commit: `sha`, `ts`, `module`, file counts |
| `hbase.jira.json` | 11,415 | ticket key → creation date |
| `phoenix.git.json` | 2,899 | as above |
| `phoenix.jira.json` | 2,899 | as above |

A single subtraction over the shared keys yields per-ticket days-to-first-commit
— the exact outcome measure the held-out corpus exists to protect. Nothing marks
the files as dangerous when read casually, and a future session could spend both
projects by accident in one line of pandas.

## The rule applied

Held-out status is a claim about what a future analyst *can still learn* from a
project, not about what was in fact learned. Two projects whose outcome data sits
committed in the repository cannot support that claim, however scrupulous the
history. Quarantining them costs two projects out of nine; leaving them in the
held-out corpus would have made the remaining seven unfalsifiable as a claim.

**They are quarantined rather than deleted** because deleting them would falsify
the record in the other direction — the files were produced, the pipeline that
produced them is part of the replication attempt, and `REPLICATION.md` §"Coverage
failure" depends on the fact that the rule fired on nothing here. The record of
what was collected stays intact; what changes is that neither project may be used
as held-out data again.

## Consequences

* The held-out corpus is **seven** projects: Ozone, Tez, ZooKeeper, Ranger,
  Oozie, Knox, Sqoop (`PROJECT_STATE.md` §3).
* HBase and Phoenix keep their **coverage** results — commit-side 92.5% and
  92.0%, ticket-side 55.6% and 41.3% — which are existence counts, permitted
  under the §3 rule and reported in `paper/table1_eligibility.md`.
* Neither project may carry a timing, latency, resolution-time or status-duration
  statistic in any future analysis without being declared spent first.
