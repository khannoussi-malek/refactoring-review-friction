#!/usr/bin/env python3
"""
replicate.py -- run the start-ui-web analysis against any TypeScript repo.

The finding to replicate (from SUI_FINDINGS.md, n=28, start-ui-web):
    matched on PR size, architectural PRs need MORE commits (rework) and draw
    MORE review threads, while merge latency does NOT differ.

This script reproduces exactly that test on another corpus. Per-repo cost is
the config block below; everything else is derived.

Usage:
    python3 scripts/sui/replicate.py --repo <path> --rm <refminer.json> \
                                     --prs <prs.json> --name <label>

Inputs are produced by:
    bash scripts/run_rm_safe.sh <repo> <start> <end> 32 120 <refminer.json>
    python3 scripts/sui/fetch_prs.py <owner/name> > <prs.json>
"""
import argparse, collections, datetime as dt, json, re, subprocess
import numpy as np
from scipy import stats

ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass", "Extract Subclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
ARCH = ABSTRACTION | RELOCATION
# Systematic false positive in RefactoringMiner's TypeScript mode: 160 instances
# in start-ui-web, all "interface to class", traced to plain type aliases in a
# codebase with no classes. Excluded everywhere. See SUI_FINDINGS.md.
SUSPECT = {"Change Type Declaration Kind"}

# PR references appear differently depending on merge strategy.
PR_PATTERNS = [re.compile(r"\(#(\d+)\)"),                    # squash merge
               re.compile(r"Merge pull request #(\d+)"),      # merge commit
               re.compile(r"#(\d+)$")]                        # trailing ref


def sh(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a),
                          capture_output=True, text=True).stdout


def pr_number(subject):
    for p in PR_PATTERNS:
        m = p.search(subject)
        if m:
            return int(m.group(1))
    return None


def mw(a, b, label, unit=""):
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if len(a) < 3 or len(b) < 3:
        return f"    {label:30} n too small ({len(a)}/{len(b)})", None
    _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    s = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return (f"    {label:30} {np.median(a):8.2f} vs {np.median(b):8.2f} {unit:4} "
            f"n={len(a)}/{len(b)} p={p:.4f} {s}"), p


def match_on_size(A, B, lo=0.5, hi=2.0):
    """Greedy nearest-size matching without replacement."""
    used, pairs = set(), []
    for a in sorted(A, key=lambda x: -x["size"]):
        cand = [b for b in B if b["n"] not in used
                and lo <= b["size"] / max(a["size"], 1) <= hi]
        if cand:
            b = min(cand, key=lambda x: abs(x["size"] - a["size"]))
            used.add(b["n"])
            pairs.append((a, b))
    return pairs


def build(repo, rm_path, prs_path):
    rmj = json.load(open(rm_path))
    rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])]
            for c in rmj["commits"]}
    subj = {}
    for line in sh(repo, "log", "--all", "--format=%H\x02%s").strip().split("\n"):
        if "\x02" in line:
            h, s = line.split("\x02", 1)
            subj[h] = s

    pr_types = collections.defaultdict(set)
    linked = 0
    for sha, types in rmap.items():
        if sha not in subj:
            continue
        n = pr_number(subj[sha])
        if n:
            linked += 1
            pr_types[n] |= (set(types) - SUSPECT)

    prs = json.load(open(prs_path))
    f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    rows = []
    for p in prs:
        n = p["number"]
        t = pr_types.get(n, set())
        rows.append(dict(
            n=n,
            cls="architectural" if t & ARCH else
                "other-refactoring" if t else "none",
            size=p.get("additions", 0) + p.get("deletions", 0),
            files=p.get("changedFiles", 0),
            merge=((f(p["mergedAt"]) - f(p["createdAt"])).total_seconds() / 86400
                   if p.get("mergedAt") else None),
            threads=p.get("reviewThreads", {}).get("totalCount", 0),
            comments=p.get("comments", {}).get("totalCount", 0),
            commits=p.get("commits", {}).get("totalCount", 0),
        ))
    return rmj, rmap, rows, linked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rm", required=True)
    ap.add_argument("--prs", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()

    rmj, rmap, rows, linked = build(a.repo, a.rm, a.prs)
    refs = [r for c in rmj["commits"] for r in c.get("refactorings", [])
            if r["type"] not in SUSPECT]

    print("=" * 78)
    print(f"REPLICATION: {a.name}")
    print("=" * 78)
    print(f"  commits analysed by RM   {len(rmj['commits'])}")
    print(f"  refactorings (ex-suspect) {len(refs)}")
    print(f"  commits linked to a PR    {linked}")
    counts = collections.Counter(r["cls"] for r in rows)
    for k in ("architectural", "other-refactoring", "none"):
        print(f"    PRs {k:20} {counts[k]}")

    A = [r for r in rows if r["cls"] == "architectural" and r["size"]]
    N = [r for r in rows if r["cls"] == "none" and r["size"]]
    if len(A) < 5:
        print("\n  !! too few architectural PRs to test -- widen the commit window")
        return

    print(f"\n  RAW (unmatched) architectural vs non-refactoring")
    for k, lab, u in (("size", "PR size", "loc"), ("merge", "merge latency", "d"),
                      ("commits", "commits per PR", ""), ("threads", "review threads", "")):
        line, _ = mw([r[k] for r in A], [r[k] for r in N], lab, u)
        print(line)

    pairs = match_on_size(A, N)
    print(f"\n  SIZE-MATCHED  ({len(pairs)} pairs)  <-- the actual test")
    results = {}
    for k, lab, u in (("size", "PR size (match check)", "loc"),
                      ("merge", "merge latency", "d"),
                      ("commits", "commits per PR (rework)", ""),
                      ("threads", "review threads", "")):
        line, p = mw([x[k] for x, _ in pairs], [y[k] for _, y in pairs], lab, u)
        print(line)
        results[k] = p

    print(f"\n  VERDICT for {a.name}:")
    for k, lab in (("commits", "rework (commits/PR)"), ("threads", "review threads"),
                   ("merge", "merge latency")):
        p = results.get(k)
        v = ("REPLICATES" if p is not None and p < .05 else
             "no effect" if p is not None else "untestable")
        print(f"    {lab:26} {v}")

    if a.out:
        json.dump(dict(name=a.name, n_pairs=len(pairs), p=results,
                       counts=dict(counts)), open(a.out, "w"), indent=2)


if __name__ == "__main__":
    main()
