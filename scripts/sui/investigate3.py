#!/usr/bin/env python3
"""
investigate3.py -- round 3, on the REPAIRED corpus (93% coverage).

Round 2 found the 2024 hole (93% of that year missing) which invalidated every
temporal result. This re-runs the time analysis on the merged dataset and adds
the review-participation mechanism: who actually reviews architectural work,
and is it independently reviewed at all.
"""
import json, re, subprocess, collections, datetime as dt
import numpy as np
from scipy import stats

SUI = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/sui"
SCR = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad"

ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
SUSPECT = {"Change Type Declaration Kind"}
ARCH = ABSTRACTION | RELOCATION


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


def mw(a, b, label, unit=""):
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if len(a) < 3 or len(b) < 3:
        return f"    {label:30} n too small ({len(a)}/{len(b)})"
    _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    s = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return (f"    {label:30} {np.median(a):7.2f} vs {np.median(b):7.2f} {unit:4} "
            f"n={len(a)}/{len(b)} p={p:.4f} {s}")


rmj = json.load(open("refminer_sui_merged.json"))
rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])] for c in rmj["commits"]}
meta = {}
for line in sh("log", "--format=%H\x02%at\x02%s\x02%ae").strip().split("\n"):
    h, t, s, a = line.split("\x02")
    meta[h] = (int(t), s, a)

print("=" * 78)
print("1. TEMPORAL -- architectural rate per year (REPAIRED corpus, 93%)")
print("=" * 78)
yr_all, yr_arch, yr_abs = collections.Counter(), collections.Counter(), collections.Counter()
for sha, types in rmap.items():
    if sha not in meta:
        continue
    y = dt.datetime.fromtimestamp(meta[sha][0]).year
    t = set(types) - SUSPECT
    if not t:
        continue
    yr_all[y] += 1
    if t & ARCH:
        yr_arch[y] += 1
    if t & ABSTRACTION:
        yr_abs[y] += 1
print(f"    {'year':6}{'refac':>7}{'arch':>7}{'rate':>7}{'abstr':>7}")
for y in sorted(yr_all):
    print(f"    {y:6}{yr_all[y]:7}{yr_arch[y]:7}{100*yr_arch[y]/yr_all[y]:6.0f}%{yr_abs[y]:7}")
ys = sorted(yr_all)
rate = [yr_arch[y] / yr_all[y] for y in ys]
rho, p = stats.spearmanr(ys, rate)
print(f"\n    trend in architectural share over time: rho={rho:+.2f} p={p:.3f}"
      f"  {'(no trend)' if p > .05 else '(TREND)'}")

print("\n" + "=" * 78)
print("2. REVIEW PARTICIPATION -- is architectural work independently reviewed?")
print("=" * 78)
det = {p["number"]: p for p in json.load(open(f"{SCR}/pr_review_detail.json"))}
base = {p["number"]: p for p in json.load(open(f"{SCR}/prs_all.json"))}

pr_types = collections.defaultdict(set)
for sha, types in rmap.items():
    if sha not in meta:
        continue
    m = re.search(r"\(#(\d+)\)", meta[sha][1])
    if m:
        pr_types[int(m.group(1))] |= (set(types) - SUSPECT)

rows = []
for n, d in det.items():
    t = pr_types.get(n, set())
    cls = ("architectural" if t & ARCH else
           "other-refactoring" if t else "none")
    author = (d["author"] or {}).get("login")
    merger = (d["mergedBy"] or {}).get("login")
    revs = [r["author"]["login"] for r in d["reviews"]["nodes"] if r["author"]]
    indep = {r for r in revs if r != author}
    rows.append(dict(n=n, cls=cls, author=author,
                     self_merged=(merger is not None and merger == author),
                     n_indep=len(indep), any_indep=len(indep) > 0,
                     commits=d["commits"]["totalCount"],
                     issue=d["closingIssuesReferences"]["totalCount"] > 0
                     if isinstance(d["closingIssuesReferences"], dict)
                     and "totalCount" in d["closingIssuesReferences"]
                     else bool(d["closingIssuesReferences"]["nodes"]),
                     labels=[l["name"] for l in d["labels"]["nodes"]]))
A = [r for r in rows if r["cls"] == "architectural"]
O = [r for r in rows if r["cls"] == "other-refactoring"]
N = [r for r in rows if r["cls"] == "none"]
print(f"    PRs: architectural {len(A)}, other-refac {len(O)}, none {len(N)}")
print(f"\n    {'group':20}{'self-merged':>13}{'indep reviewed':>16}{'med reviewers':>15}")
for lab, g in (("architectural", A), ("other-refactoring", O), ("none", N)):
    if not g:
        continue
    print(f"    {lab:20}{100*sum(r['self_merged'] for r in g)/len(g):12.0f}%"
          f"{100*sum(r['any_indep'] for r in g)/len(g):15.0f}%"
          f"{np.median([r['n_indep'] for r in g]):15.1f}")
print()
print(mw([r["n_indep"] for r in A], [r["n_indep"] for r in N],
         "independent reviewers", ""))
print(mw([r["commits"] for r in A], [r["commits"] for r in N],
         "commits per PR (rework)", ""))

print("\n" + "=" * 78)
print("3. IS ARCHITECTURAL WORK PLANNED?  (linked issue / labels)")
print("=" * 78)
for lab, g in (("architectural", A), ("other-refactoring", O), ("none", N)):
    if not g:
        continue
    print(f"    {lab:20} links an issue: {100*sum(r['issue'] for r in g)/len(g):4.0f}%"
          f"   labelled: {100*sum(1 for r in g if r['labels'])/len(g):4.0f}%")

print("\n" + "=" * 78)
print("4. DOES THE AUTHOR SAY IT IS A REFACTORING?")
print("=" * 78)
says, is_arch = 0, 0
tp, fp, fn = 0, 0, 0
for sha, types in rmap.items():
    if sha not in meta:
        continue
    s = meta[sha][1].lower()
    said = s.startswith("refactor") or "refactor" in s[:40]
    real = bool((set(types) - SUSPECT) & ARCH)
    tp += said and real
    fp += said and not real
    fn += (not said) and real
print(f"    commits whose message claims refactoring AND are architectural: {tp}")
print(f"    claims refactoring but is not architectural (false claim):      {fp}")
print(f"    IS architectural but message never says so (silent):            {fn}")
if tp + fp:
    print(f"\n    -> message-based precision {100*tp/(tp+fp):.0f}%, "
          f"recall {100*tp/(tp+fn):.0f}%")
    print("    -> mining commit MESSAGES for refactoring would miss most of it")
