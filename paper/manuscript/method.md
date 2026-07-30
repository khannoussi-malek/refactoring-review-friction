# 3. Method

**Status: to write** (writing order 2 — immediately after `results.md`).

## What must be here

**Corpus construction.** 38 Apache candidates: Maven-built, Jira-tracked,
multi-module. Cloned `--filter=blob:none --no-checkout`, probed with
`scripts/citation_rate.py` / `scripts/traceability_probe.py`. Key prefixes
detected **empirically from commit messages, not assumed** — the single-key/
multi-key gap is the reason (§ taxonomy mode 5). Per-project HEAD sha pinned in
`paper/traceability_probe.json`, so any re-run is exactly diffable.

**The bar.** ≥0.80 commit-side, **fixed in `predictions/PREDICTIONS.md`
(`ca076a9`) before any project was cloned, and never moved.** State plainly that
lowering it would have widened the corpus and that it was not lowered. The same
discipline held elsewhere: the vendor-share threshold stayed at 0.40 through a
failed replication when lowering it would have rescued two projects.

**Key matching, and its measured precision.** The matcher is
`\b(?:KEY|KEY2)-\d+\b` over subject + body. Precision **195 of 200 = 97.5%**
(Wilson 95% CI 94.3–98.9%), corpus-weighted 97.7%, on a seeded 200-commit manual
sample across the 12 (`paper/matcher_validation.md`). Report the two structural
zeros with the result: `version_string` is near-unreachable given the pattern, and
`foreign_key` is unreachable for 11 of the 12, so **the single-key → multi-key
result on Hadoop is not validated by that sample.**

**Both channels.** GitHub-issue references (`#NNN`, `GH-NNN`) counted alongside
Jira keys, which is what makes each drop reason measured rather than inferred.

**Ticket-side coverage.** `scripts/ticket_coverage.py`, Jira REST, **`key` field
only** — `paper/ticket_coverage.json` records the forbidden fields screened out,
which is how the held-out rule was enforced mechanically rather than by care.

**The detector.** RefactoringMiner 3.1.4. For the TypeScript corpus, note that
support was complete 2026-05-24 and had no independent validation in the
literature, that `Change Type Declaration Kind` was excluded as a false positive
(160 instances, upstream issue #1124), and that coverage was 93% after a repaired
run — see `threats.md`.

**Held-out discipline.** Say it in the method, not only in threats: outcome data
was never observed for seven projects, the rule is written down
(`PROJECT_STATE.md` §3), and the validation script requests `%H`, `%s`, `%b` from
git and nothing else so that it *cannot* produce a timing statistic.
