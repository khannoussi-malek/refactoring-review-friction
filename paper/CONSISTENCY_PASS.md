# Internal consistency pass

2026-08-05. Six items, all of them the paper disagreeing with itself rather than
a new measurement. No analysis was re-run and no script that touches Jira or a
clone was executed. Both gates were unsatisfied when this started and are
unsatisfied now.

**Gate status.** `paper/BACHMANN_DETERMINATION.md` does not exist.
`paper/SPLIT_DECISION.md` does not exist. Every `[DETERMINATION PENDING]` marker
is where it was: `related.md` §2.4, `related.md` §2.2 item 5, and the
`UNDETERMINED` note in `CITATION.cff`. Nothing was split and nothing was trimmed.

---

## Item 1. Table 1's caption led with the withdrawn example

The caption still built its worked example on Kylin, the same example §4.2.1
withdraws and §6.1 explains. It has been re-cut around Hive, which §4.2 already
uses.

The caption text lives in `scripts/make_table1.py`, not in the artifact, so it was
changed there and the table regenerated from the committed
`paper/traceability_probe.json` and `paper/ticket_coverage.json`. No fetch, no
re-probe. Hive's figures are read out of the same data that fills the row: 97.0%
of 18,213 commits, 55.8% of 29,635 tickets.

Kylin keeps its row and gains a paragraph that flags it. The row is correct for
the branch that was pinned, and saying so is not the same as featuring it.

**The sweep.** Every occurrence of "kylin" across the nine section files and the
three table files, 29 in all. One was still an unflagged exemplar.

| where | role | disposition |
|---|---|---|
| `table2_visibility.md` L11 | **exemplar, unflagged** | **fixed.** Replaced with Hive as the worked example; Kylin kept as a parenthetical carrying the §4.2.1 pointer |
| `table1_eligibility.md` L23 | data row | left. It is a measurement |
| `table1_eligibility.md` caption | was exemplar | **fixed** as above, and a flagging paragraph added |
| `table3_ticket_side.md` L7, L25 | data row and worst-case flag | left. Both already read as caveats |
| `results.md` L41 | ecosystem sensitivity | left. Names Kylin as an exposure, not an exemplar |
| `results.md` L76 | endpoint of the ceiling_live range | left. A range endpoint, not an illustration |
| `results.md` §4.2.1, 12 hits | the withdrawal itself | left. This is the passage that performs it |
| `results.md` L162, L176, L177, L181 | validation worst case | left. Every one is a flag |
| `threats.md` L45, L74, L76, L79, L87 | §6.1 and §6.2 | left. This is where the explanation lives |

The abstract, §1, §7.1 and the acknowledgements contain no mention of Kylin at
all, so nothing there needed changing.

## Item 2. Four floats carried three numbers

The continuation half of Table 1 printed as "Table 2" and Table 2's sources list
printed as "Table 3".

Two separate causes. A continuation was emitted with a numbered `\caption`, which
consumed the next number, and only afterwards was the counter wound back, so the
printed label was always one too high. And the sources list was being treated as a
continuation when it is provenance rather than data.

`scripts/make_latex.py` now records, per table file, how many data tables belong
to the caption. The first takes the number and the label. A second data table
takes `\caption*`, which prints "Table 1, continued" without consuming a number.
Anything past that count is set with no caption and no number.

After the fix: Figure 1, Table 1, Table 2, Table 3. Four floats, four numbers,
zero undefined references, and the front-matter map resolves through `\ref` so it
cannot drift from the floats again.

Figure 1's caption is no longer truncated. It reads "with the six
operationalisations that were tested and closed" in full. The truncation was the
caption overrunning the measure of a text-width figure; the figure now sets on a
landscape page. Every other float caption was checked against its source string
and none is cut.

## Item 3. The ceiling sentence contradicted Table 3

§4.2 said the ceiling binds for all twelve. Table 3 has Ozone at 176.0%, Ranger
at 130.4% and Knox at 100.0%, and its own note says a ceiling above 100% does not
bind.

Both were right and neither said which estimator it meant. §4.2's sentence is now
explicitly `ceiling_live`, and a paragraph after it points forward to Table 3,
names the three projects, and gives the reason: a 2026 commit window measured
against an older tracker leaves the repository holding more citing commits than
the snapshot holds tickets, so the bound exceeds one and stops bounding anything.

**No numeric value was altered.** Verified mechanically: the set of numbers in
`results.md` after the edit is a superset of the set before it, so nothing was
removed or changed. The values added are 176.0, 130.4, 100.0, 16.3, 0.04, 99.72,
4,989 and 0.00, and every one is quoted from `paper/table3_ticket_side.md`.

## Item 4. §6.5 contradicted itself

The paragraph said re-labelling six comments moves the kappa ceiling to 0.840,
then gave a table in which six gives 0.837 and five gives 0.840.

`paper/LLM_RATER_PILOT.md` and `audit/JUDGMENTS.md` §3 agree with each other, so
there was nothing to report as a conflict between artifacts. The pilot's §4 table
lists six comments that change label. Its §4 bucket table shows the flagged margin
moving from 3/12/5 to 3/7/10, a swing of exactly five, because **five of the six
sit in the flagged bucket and the sixth does not**. The ceiling is computed on the
flagged bucket, so the count that drives it is five.

Six is the total across both buckets. Five is the flagged count. The paragraph had
attached the ceiling to the wrong one of the two.

Corrected additively and dated in place. The disclosure is untouched: five is
still stated to be the global maximum, the neighbouring values are still given,
and the sentence saying the criterion was applied by the party that reported the
result still stands. Nothing was deleted.

## Item 5. The Bachmann figure

Report only, in `paper/BACHMANN_FIGURE_CHECK.md`. The distinctness argument was
not rewritten and no marker was resolved.

Both figures verified against the full text. §2.4 quotes the commit-side one,
47.6% of 82 bug-fix commits, and quotes it accurately. The ticket-side one,
303 of 559 fixed bug reports, is 54.20% and appears nowhere in §2.4; it is a
subtraction Bachmann never prints as a percentage, and the string "54%" is absent
from the paper.

Reasoning from denominators alone, the ticket-side figure is the one that shares
TRR's direction. What §2.4 would need in order to compare like with like is
described in that file as four steps, three of which are reporting and hold under
either branch of the worksheet. The fourth is the gate and was not taken.

## Item 6. Live and frozen were not distinguished

Four headline quantities appeared with two values each and the paper alternated
without marking which estimator produced which.

§3.1.3 already defined TRR_live and TRR_frozen. What was missing is that
`ceiling` and `fill` never inherited the subscript, and that the convention was
never stated. A paragraph at the end of §3.1.4 now propagates it: an unsubscripted
name means the quantity in general, every measured value carries its subscript,
and where a project shows two numbers for what looks like one quantity the
subscript is the difference.

Applied at each site the brief names:

| quantity | now reads |
|---|---|
| Hive ticket realisation | 55.8% marked TRR_live in the abstract, §1, §4.2 and §7.1, with Table 3's 56.1% named as TRR_frozen and the reason given |
| fill | `fill_live` in §4.2, `fill_frozen` where Table 3 is meant |
| TRR range | 12.0–69.0% marked TRR_live; the 0.04–68.6% row in §4.3 marked TRR_frozen |
| Kylin fill | `fill_live` 0.87 in §4.2.1, with `fill_frozen` 0.00 explained rather than left to collide |

Table 1's caption now states that everything in it is the live measurement and
Table 3's that everything in it is frozen.

**No numeric value was altered.** Same mechanical check as item 3, run across
`abstract.md`, `intro.md`, `method.md`, `results.md`, `threats.md`,
`discussion.md`, `table1_eligibility.md` and `table2_visibility.md`. No value was
removed from any of them.

One correction worth recording, because I made it and caught it. My first draft of
the Kylin paragraph said `fill_frozen` is 0.00 because the frozen ceiling exceeds
100%. That is false. Kylin's `ceiling_frozen` is 16.3%, well under the bound; its
`fill_frozen` is 0.00 because `TRR_frozen` is 0.04%, and that is because 99.72% of
its cited keys postdate the snapshot. The paragraph now says so.

---

## Files touched

| file | item |
|---|---|
| `scripts/make_table1.py` | 1, 6 |
| `paper/table1_eligibility.md` | 1, 6 (regenerated, not hand-edited) |
| `paper/table2_visibility.md` | 1, 6 |
| `scripts/make_latex.py` | 2, 6 |
| `paper/manuscript/results.md` | 3, 6 |
| `paper/manuscript/threats.md` | 4 |
| `paper/manuscript/method.md` | 6 |
| `paper/manuscript/abstract.md` | 6 |
| `paper/manuscript/intro.md` | 6 |
| `paper/manuscript/discussion.md` | 6 |
| `paper/numbers.md` | provenance rows for the values items 3 and 6 now cite (appended) |
| `paper/BACHMANN_FIGURE_CHECK.md` | 5 (new) |
| `paper/CONSISTENCY_PASS.md` | this file (new) |
| `paper/manuscript/PAPER.md`, `PROVENANCE_CHECK.md`, `paper/preprint/*` | regenerated |

Not touched: `predictions/PREDICTIONS.md`, every dated log, `requirements.txt`,
`paper/table3_ticket_side.md`, and every `[DETERMINATION PENDING]` marker.

## Build

Rebuilt from the sources after every edit.

| check | result |
|---|---|
| pages | **40** |
| LaTeX errors | **0** |
| undefined or multiply-defined references | **0** |
| overfull boxes | **0** |
| leaked markdown markers | **0** |
| section-number drift against the authored numbers | **none** |
| float numbers | Figure 1, Table 1, Table 2, Table 3 |
| prose paragraphs present in the PDF text layer | **185 of 185** |
| headings present | **51 of 51** |
| provenance checker | 207 ARTIFACT, 45 DOCUMENTED, **0 unsourced**, 0 without a registry row |

The four paragraphs that a naive text match reports as missing all contain a
subscripted symbol, which extracts as "ceilinglive" rather than "ceiling_live".
Each was checked by hand and is present.
