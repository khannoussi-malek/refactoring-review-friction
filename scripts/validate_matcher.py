#!/usr/bin/env python3
"""
validate_matcher.py -- precision of the Jira key matcher, on a manual sample.

Every headline number in the traceability paper is a citation rate produced by
matching `\\b(?:KEY|KEY2)-\\d+\\b` against commit messages. The first objection a
reviewer raises is that 83.9% is a regex artifact: keys pasted from changelogs,
version strings, cherry-pick trailers, reverts. The SEOSS 33 agreement (4 of 5
projects within 3.3pp) is external validation of the *measure* but establishes
nothing about precision on THIS corpus. This does.

WHY THIS IS NOT THE SAME AS THE CODEBOOK PROBLEM. README.md §8 records that no
measure requiring manual coding is currently defensible, because inter-rater
agreement cannot be computed by one person. That applies to *coded judgments* --
"is this review comment a structural argument?" -- where the construct lives in
the rater's head. This is a mechanical check against a written rule: does the
matched key refer to the work in this commit, or is it one of five enumerated
textual artifacts? The categories are decidable from the message text, so a
second rater would be checking arithmetic rather than calibrating a construct.
The labels are committed alongside the sample so anyone can re-check all 200.

R1 -- THE HELD-OUT CORPUS. Seven of the twelve projects are held out (Ozone, Tez,
ZooKeeper, Ranger, Oozie, Knox, Sqoop). This script reads `%H`, `%s` and `%b`
only. It requests NO commit timestamp, author date, or committer date from git,
stores none, and there is no code path here that can subtract two dates or emit a
duration. Coverage and existence counts are permitted by PROJECT_STATE.md §3;
this is a precision count over commit message text.

PROVING THE MATCHER IS THE PUBLISHED ONE. The scan below does not import
citation_rate.git_log, because git_log always logs from current HEAD and the
clones have advanced past the pinned head_sha in
paper/traceability_probe.json. Instead it logs from the pinned sha with the same
format string, and then ASSERTS that its own commit count and matched count equal
the published `commits_scanned` and `jira_key_refs` for all twelve projects. If
the matcher had drifted, or the clone were wrong, the counts would not reproduce
and the run aborts.

Usage:
    python3 scripts/validate_matcher.py sample --corpora <dir>   # draw the sample
    python3 scripts/validate_matcher.py report                   # labels -> markdown
"""
import argparse
import json
import math
import pathlib
import random
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROBE = ROOT / "paper" / "traceability_probe.json"
SAMPLE = ROOT / "paper" / "matcher_sample.json"
LABELS = ROOT / "paper" / "matcher_labels.json"
OUT = ROOT / "paper" / "matcher_validation.md"

SEED = 20260730
N_SAMPLE = 200

# git format identical to citation_rate.git_log: hash, subject, body. No dates.
FMT = "%H%x1f%s%x1f%b%x1e"

CATEGORIES = {
    "genuine": "the matched key is a genuine reference to work done in this commit",
    "version_string": "a version or release number resembling a key",
    "changelog_paste": "a key pasted from a changelog, release note, or copied file",
    "backport": "a backport or cherry-pick mention referring to other work",
    "revert": "a revert referencing the reverted commit's key",
    "foreign_key": "a key belonging to a different project in the monorepo",
}


def pattern(keys):
    """Byte-for-byte the matcher in citation_rate.py and traceability_probe.py."""
    return re.compile(
        rf"\b(?:{'|'.join(re.escape(k) for k in keys.split(','))})-\d+\b")


def git_log_at(repo, rev):
    """Commits reachable from `rev`. Hash, subject, body. No timestamps."""
    out = subprocess.run(
        ["git", "-C", str(repo), "log", rev, f"--pretty=format:{FMT}"],
        capture_output=True, text=True, check=True).stdout
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) >= 3:
            yield parts[0], parts[1], parts[2]


def eligible():
    probe = json.loads(PROBE.read_text())
    return sorted((r for r in probe["projects"] if r["passes_bar"]),
                  key=lambda r: r["project"])


def scan(repo, rec):
    """-> (n_commits, [(sha, subject, body, [keys])]) for matching commits only."""
    pat = pattern(rec["keys_multi"])
    total, matched = 0, []
    for sha, subj, body in git_log_at(repo, rec["head_sha"]):
        total += 1
        msg = f"{subj}\n{body}"
        found = pat.findall(msg)
        if found:
            matched.append((sha, subj, body, found))
    return total, matched


def allocate(records, n_total):
    """Equal allocation, remainder to the largest strata. Deterministic."""
    k = len(records)
    base, extra = divmod(n_total, k)
    # largest-remainder by citing-commit count, name as tie-break
    order = sorted(records, key=lambda r: (-r["jira_key_refs"], r["project"]))
    quota = {r["project"]: base for r in records}
    for r in order[:extra]:
        quota[r["project"]] += 1
    assert sum(quota.values()) == n_total
    return quota


def do_sample(corpora):
    records = eligible()
    quota = allocate(records, N_SAMPLE)
    rng = random.Random(SEED)
    rows, verified = [], []

    for rec in records:
        name = rec["project"]
        repo = corpora / name
        if not (repo / ".git").is_dir():
            sys.exit(f"missing clone: {repo}")
        total, matched = scan(repo, rec)

        # Precondition: the published counts must reproduce exactly.
        if total != rec["commits_scanned"] or len(matched) != rec["jira_key_refs"]:
            sys.exit(
                f"{name}: scan does not reproduce the published probe.\n"
                f"  commits  got {total:,} want {rec['commits_scanned']:,}\n"
                f"  matching got {len(matched):,} want {rec['jira_key_refs']:,}\n"
                f"  head_sha {rec['head_sha']}")
        verified.append({"project": name, "commits_scanned": total,
                         "jira_key_refs": len(matched),
                         "head_sha": rec["head_sha"]})

        matched.sort(key=lambda t: t[0])          # stable order before sampling
        picked = rng.sample(matched, quota[name])
        for sha, subj, body, keys in sorted(picked, key=lambda t: t[0]):
            rows.append({
                "project": name,
                "sha": sha,
                "keys_matched": sorted(set(keys)),
                "subject": subj,
                "body": body,
            })
        print(f"{name:12s} verified {total:6,d} commits, "
              f"{len(matched):6,d} matching -> sampled {quota[name]}")

    payload = {
        "seed": SEED,
        "n_sample": N_SAMPLE,
        "allocation": "equal per project, remainder to the largest strata",
        "matcher": r"\b(?:KEY[,KEY2...])-\d+\b over subject + body",
        "fields_read_from_git": ["%H", "%s", "%b"],
        "timestamps_read": "none -- see R1 note in the script docstring",
        "quota": quota,
        "verified_against_probe": verified,
        "categories": CATEGORIES,
        "commits": rows,
    }
    SAMPLE.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"\nwrote {SAMPLE.relative_to(ROOT)}  ({len(rows)} commits)")


def wilson(k, n, z=1.96):
    """Wilson score interval -- behaves at proportions near 1, unlike Wald."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def do_report():
    sample = json.loads(SAMPLE.read_text())
    labelfile = json.loads(LABELS.read_text())
    labels = labelfile["labels"]
    rules = labelfile["rules"]
    rows = sample["commits"]

    missing = [r["sha"] for r in rows if r["sha"] not in labels]
    if missing:
        sys.exit(f"{len(missing)} commits unlabelled, first: {missing[0]}")
    bad = sorted({v for v in labels.values()} - set(CATEGORIES))
    if bad:
        sys.exit(f"unknown label(s): {bad}")

    by_project, cats = {}, {c: 0 for c in CATEGORIES}
    for r in rows:
        lab = labels[r["sha"]]
        cats[lab] += 1
        d = by_project.setdefault(r["project"], {"n": 0, "genuine": 0})
        d["n"] += 1
        d["genuine"] += (lab == "genuine")

    n = len(rows)
    k = cats["genuine"]
    lo, hi = wilson(k, n)

    # Stratified estimator: strata are projects, weights are each project's share
    # of matching commits in the corpus. This is the estimate that answers "what
    # fraction of the corpus's matched commits are genuine", because the sample
    # is equal-allocation and therefore NOT self-weighting.
    weights = {v["project"]: v["jira_key_refs"]
               for v in sample["verified_against_probe"]}
    total_w = sum(weights.values())
    strat = sum(weights[p] * by_project[p]["genuine"] / by_project[p]["n"]
                for p in by_project) / total_w
    var = sum((weights[p] / total_w) ** 2
              * (by_project[p]["genuine"] / by_project[p]["n"])
              * (1 - by_project[p]["genuine"] / by_project[p]["n"])
              / by_project[p]["n"]
              for p in by_project)
    se = math.sqrt(var)

    L = []
    a = L.append
    a("# Key-matcher precision on a 200-commit manual sample")
    a("")
    a("<!-- GENERATED by `scripts/validate_matcher.py report` from")
    a("     paper/matcher_sample.json and paper/matcher_labels.json.")
    a("     Do not edit by hand. -->")
    a("")
    a(f"**Precision {k} of {n} = {100.0*k/n:.1f}%** "
      f"(Wilson 95% CI **{100.0*lo:.1f}–{100.0*hi:.1f}%**) on an equal-allocation "
      f"sample of {n} matching commits drawn across the "
      f"{len(by_project)} eligible projects.")
    a("")
    a(f"**Corpus-weighted precision {100.0*strat:.1f}%** "
      f"(±{100.0*1.96*se:.1f}pp, stratified normal approximation). This is the "
      "estimate that applies to the published rates: the sample allocates equally "
      "across projects, so it is not self-weighting, and re-weighting each project "
      "by its share of the corpus's matching commits is what makes the figure "
      "comparable to a corpus-wide citation rate.")
    a("")

    a("## What was checked")
    a("")
    a("The matcher is `\\b(?:KEY|KEY2)-\\d+\\b` over subject + body — identical in "
      "`scripts/citation_rate.py` and `scripts/traceability_probe.py`. For each "
      "sampled commit, one question: **does the matched key refer to the work done "
      "in this commit?** If not, it falls into one of five enumerated textual "
      "artifacts, fixed before labelling began:")
    a("")
    a("| label | meaning | n |")
    a("|---|---|---:|")
    for c, desc in CATEGORIES.items():
        a(f"| `{c}` | {desc} | {cats[c]} |")
    a(f"| | **total** | **{n}** |")
    a("")
    a("### Adjudication rules, fixed before labelling")
    a("")
    for r in rules:
        a(f"* {r}")
    a("")
    a("### Which categories were structurally reachable")
    a("")
    a("Three categories returned zero, and two of those three could **not** have "
      "returned anything else on this corpus. Reporting the zero without saying so "
      "would overstate what the sample tested:")
    a("")
    a("* **`version_string` is near-unreachable.** The pattern requires the "
      "upper-case project key immediately followed by `-` and digits. Release "
      "identifiers in these projects are lower-case or dotted "
      "(`1.116.0-kylin-4.x-r028`, `4.1.89.Final`, `phoenix-<version>.tar.gz`) and "
      "cannot match. The sample confirms the category is empty; it does not "
      "confirm the matcher would survive a corpus that tags releases `PROJ-123`.")
    a("* **`foreign_key` is unreachable for eleven of the twelve.** The matcher is "
      "given each project's own key set, so a key from another project cannot "
      "match. Only Ozone is multi-key (`HDDS,OZONE`) and both keys are its own. "
      "This category is only testable on a true monorepo — Hadoop's "
      "`HADOOP,HDFS,YARN,MAPREDUCE`, which is not among the twelve. **The 26.2% → "
      "92.3% → 97.8% single/four/seven-key result is therefore not validated "
      "here.**")
    a("* **`changelog_paste` was reachable and did not fire**, though one revert "
      "(`Revert \"Amending release-log for OOZIE-1549\"`) is the adjacent case: the "
      "key entered the history through a release-log edit.")
    a("")

    a("## By project")
    a("")
    a("| project | sampled | genuine | precision | 95% CI (Wilson) |")
    a("|---|---:|---:|---:|---|")
    for p in sorted(by_project):
        d = by_project[p]
        plo, phi = wilson(d["genuine"], d["n"])
        a(f"| {p} | {d['n']} | {d['genuine']} | {100.0*d['genuine']/d['n']:.1f}% "
          f"| {100.0*plo:.1f}–{100.0*phi:.1f}% |")
    a("")
    a(f"At n≈{n // len(by_project)} per project the per-project intervals are wide "
      "and are reported for completeness, not for comparison between projects. "
      "The pooled and corpus-weighted figures above are the usable ones.")
    a("")

    a("## Why a single rater is sufficient here, and is not elsewhere")
    a("")
    a("`README.md` §8 records that no measure requiring manual coding is currently "
      "defensible in this repository, because inter-rater agreement cannot be "
      "computed by one person. That constraint binds **coded judgments** — the "
      "architectural-episode gold set, and the codebook whose keyword rule is 25% "
      "precise on a single-rater pass — where the construct being labelled lives "
      "in the rater's head and κ is the only evidence that two people would agree.")
    a("")
    a("This measure is different in kind. It is a **mechanical check against a "
      "written rule**: the five failure categories are properties of the commit "
      "message text, enumerated before labelling, and decidable by reading it. A "
      "second rater would be verifying a determination, not calibrating a "
      "construct. The check is made auditable rather than agreed: "
      "`paper/matcher_sample.json` carries all 200 messages and "
      "`paper/matcher_labels.json` carries every label, so any reader can re-check "
      "the whole sample against the rule without re-drawing it.")
    a("")
    a("This is the reason this validation is reported as a result while the "
      "architectural gold set is not.")
    a("")

    a("## Reproducibility")
    a("")
    a(f"* Seed **{sample['seed']}**, `random.Random(seed)`, strata sampled in "
      "sorted-sha order, so the draw is deterministic.")
    a("* Drawn from commits reachable from each project's **pinned `head_sha`** in "
      "`paper/traceability_probe.json`, not from current HEAD, so the sample is "
      "taken from exactly the history the published rates were measured on.")
    a("* Before sampling, the scan **reproduces each project's published "
      "`commits_scanned` and `jira_key_refs` exactly** and aborts otherwise. That "
      "is what establishes the matcher validated here is the matcher that produced "
      "Table 1, without modifying `citation_rate.py`.")
    a("")
    a("| project | commits scanned | matching | HEAD |")
    a("|---|---:|---:|---|")
    for v in sorted(sample["verified_against_probe"], key=lambda v: v["project"]):
        a(f"| {v['project']} | {v['commits_scanned']:,} | {v['jira_key_refs']:,} "
          f"| `{v['head_sha'][:10]}` |")
    a("")
    a("**R1 compliance.** Seven of the twelve projects are held out. This script "
      "requests `%H`, `%s` and `%b` from git and nothing else: no author date, no "
      "committer date, no `%at`. No duration is computed, printed or computable "
      "from the artifacts it writes. Precision over message text is a coverage "
      "measure, permitted by `PROJECT_STATE.md` §3.")
    a("")
    a("Regenerate:")
    a("")
    a("```")
    a("python3 scripts/validate_matcher.py sample --corpora <dir>   # 12 log-only clones")
    a("python3 scripts/validate_matcher.py report")
    a("```")

    OUT.write_text("\n".join(L) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  precision {k}/{n} = {100.0*k/n:.1f}% "
          f"[{100.0*lo:.1f}, {100.0*hi:.1f}]  weighted {100.0*strat:.1f}%")
    for c in CATEGORIES:
        if cats[c]:
            print(f"  {c:16s} {cats[c]}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--corpora", required=True, type=pathlib.Path,
                   help="dir holding the 12 log-only clones")
    sub.add_parser("report")
    a = ap.parse_args()

    if a.cmd == "sample":
        do_sample(a.corpora)
    else:
        do_report()


if __name__ == "__main__":
    main()
