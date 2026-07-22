#!/usr/bin/env python3
"""
selection_bias.py -- does PR-visibility select a biased subset of architectural work?

The surviving finding (architectural PRs draw more review threads) is measured
only on the 31% of architectural commits that reach a PR. If authors route work
to a PR *because* they want it reviewed, the finding is a selection artefact:
we would be measuring "work someone wanted reviewed gets reviewed".

This compares PR-linked against direct-push architectural commits on everything
observable that does NOT depend on the PR: author, size, era, refactoring type.

A clean result (no systematic difference) supports the finding.
A dirty result (PR-linked work is bigger / different / by different people)
means the effect cannot be separated from routing choice.
"""
import collections, datetime as dt, json, re, subprocess
import numpy as np
from scipy import stats

SUI = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/sui"
ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
ARCH = ABSTRACTION | RELOCATION
SUSPECT = {"Change Type Declaration Kind"}


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


def mw(a, b, label, unit=""):
    if len(a) < 3 or len(b) < 3:
        return f"    {label:28} n too small ({len(a)}/{len(b)})"
    _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    s = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return (f"    {label:28} {np.median(a):8.1f} vs {np.median(b):8.1f} {unit:4} "
            f"n={len(a)}/{len(b)} p={p:.4f} {s}")


rmj = json.load(open("refminer_sui_merged.json"))
rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])] for c in rmj["commits"]}

commits = {}
raw = sh("log", "--all", "--numstat", "--format=\x01%H\x02%at\x02%ae\x02%s")
cur = None
for line in raw.split("\n"):
    if line.startswith("\x01"):
        h, t, a, s = line[1:].split("\x02", 3)
        cur = commits[h] = dict(ts=int(t), author=a, subject=s, churn=0, files=0)
    elif line.strip() and cur is not None:
        p = line.split("\t")
        if len(p) == 3:
            cur["files"] += 1
            for v in (p[0], p[1]):
                if v.isdigit():
                    cur["churn"] += int(v)

rows = []
for sha, types in rmap.items():
    t = set(types) - SUSPECT
    if not (t & ARCH) or sha not in commits:
        continue
    c = commits[sha]
    rows.append(dict(
        sha=sha, linked=bool(re.search(r"\(#(\d+)\)", c["subject"])),
        churn=c["churn"], files=c["files"], author=c["author"],
        year=dt.datetime.fromtimestamp(c["ts"]).year,
        abstraction=bool(t & ABSTRACTION), n_ref=len(t),
    ))

L = [r for r in rows if r["linked"]]
D = [r for r in rows if not r["linked"]]
print("=" * 78)
print("SELECTION BIAS: PR-linked vs direct-push architectural commits")
print("=" * 78)
print(f"    architectural commits: {len(rows)}  "
      f"(PR-linked {len(L)}, direct-push {len(D)})")

print("\n  -- size and content (should NOT differ if routing is arbitrary) --")
for k, lab, u in (("churn", "churn (lines)", "loc"), ("files", "files touched", ""),
                  ("n_ref", "refactorings in commit", "")):
    print(mw([r[k] for r in L], [r[k] for r in D], lab, u))
la = 100 * sum(r["abstraction"] for r in L) / max(len(L), 1)
da = 100 * sum(r["abstraction"] for r in D) / max(len(D), 1)
tbl = [[sum(r["abstraction"] for r in L), len(L) - sum(r["abstraction"] for r in L)],
       [sum(r["abstraction"] for r in D), len(D) - sum(r["abstraction"] for r in D)]]
_, pf = stats.fisher_exact(tbl)
print(f"    {'abstraction share':28} {la:8.0f}% vs {da:8.0f}%      Fisher p={pf:.4f}")

print("\n  -- WHO (routing could be a person-level habit) --")
al = collections.Counter(r["author"] for r in L)
ad = collections.Counter(r["author"] for r in D)
auth = sorted(set(al) | set(ad), key=lambda a: -(al[a] + ad[a]))[:6]
print(f"    {'author':34}{'PR':>5}{'direct':>8}{'% via PR':>10}")
for a in auth:
    tot = al[a] + ad[a]
    print(f"    {a[:32]:34}{al[a]:5}{ad[a]:8}{100*al[a]/tot:9.0f}%")

print("\n  -- WHEN (the project may simply have adopted PRs over time) --")
yl = collections.Counter(r["year"] for r in L)
yd = collections.Counter(r["year"] for r in D)
print(f"    {'year':6}{'PR':>5}{'direct':>8}{'% via PR':>10}")
for y in sorted(set(yl) | set(yd)):
    tot = yl[y] + yd[y]
    print(f"    {y:6}{yl[y]:5}{yd[y]:8}{100*yl[y]/tot:9.0f}%")
ys = sorted(set(yl) | set(yd))
frac = [yl[y] / (yl[y] + yd[y]) for y in ys]
rho, p = stats.spearmanr(ys, frac)
print(f"\n    PR-adoption trend over time: rho={rho:+.2f} p={p:.3f}")

print("\n" + "=" * 78)
print("VERDICT")
print("=" * 78)
_, p_churn = stats.mannwhitneyu([r["churn"] for r in L], [r["churn"] for r in D],
                                alternative="two-sided")
issues = []
if p_churn < .05:
    issues.append("PR-linked work differs in SIZE")
if pf < .05:
    issues.append("PR-linked work differs in TYPE (abstraction share)")
if p < .05:
    issues.append("PR adoption is TIME-TRENDED (era confound)")
if issues:
    print("    ROUTING IS NOT ARBITRARY:")
    for i in issues:
        print(f"      - {i}")
    print("    -> the review-thread finding cannot be cleanly separated from")
    print("       the decision to route work through a PR. Report as a threat.")
else:
    print("    No systematic difference detected on size, type or era.")
    print("    -> routing looks arbitrary w.r.t. the measured covariates, which")
    print("       supports (does not prove) the review-thread finding.")
