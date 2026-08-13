#!/usr/bin/env python3
"""
robustness.py -- adversarial self-review of the start-ui-web finding.

SUI_FINDINGS.md reports two effects surviving size matching (rework p=0.014,
review threads p=0.005). This script tries to kill them.

Checks:
  1. MULTIPLE COMPARISONS -- how many tests were run in total, and do the
     survivors hold under Benjamini-Hochberg FDR?
  2. MATCHING INSTABILITY  -- greedy matching depends on iteration order.
     Bootstrap it: how often does the effect stay significant?
  3. ZERO-INFLATION        -- review threads are mostly 0. Mann-Whitney on a
     near-degenerate distribution is fragile; re-test as a proportion.
  4. REWORK VALIDITY       -- is "commits per PR" measuring rework, or just
     elapsed time / size? Test its correlates.
  5. LINKAGE CONTAMINATION -- only ~32% of commits link to a PR, so control
     PRs may silently contain architectural work. Quantify the dilution.
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
RNG = np.random.default_rng(20260722)


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


rmj = json.load(open("refminer_sui_merged.json"))
rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])] for c in rmj["commits"]}
subj = {}
for line in sh("log", "--all", "--format=%H\x02%s").strip().split("\n"):
    if "\x02" in line:
        h, s = line.split("\x02", 1)
        subj[h] = s

pr_types, linked_shas = collections.defaultdict(set), set()
for sha, t in rmap.items():
    if sha in subj:
        m = re.search(r"\(#(\d+)\)", subj[sha])
        if m:
            pr_types[int(m.group(1))] |= (set(t) - SUSPECT)
            linked_shas.add(sha)

prs = json.load(open("prs_sui_full.json"))
f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for p in prs:
    t = pr_types.get(p["number"], set())
    rows.append(dict(
        n=p["number"], arch=bool(t & ARCH), any_ref=bool(t),
        size=p["additions"] + p["deletions"],
        merge=((f(p["mergedAt"]) - f(p["createdAt"])).total_seconds() / 86400
               if p.get("mergedAt") else None),
        threads=p["reviewThreads"]["totalCount"],
        commits=p.get("commits", {}).get("totalCount", 0),
    ))
A = [r for r in rows if r["arch"] and r["size"]]
N = [r for r in rows if not r["any_ref"] and r["size"]]


def match(A, N, key, order=None):
    av = [r for r in A if r.get(key) is not None]
    nv = [r for r in N if r.get(key) is not None]
    idx = list(range(len(av)))
    if order is not None:
        idx = list(order)
    used, pairs = set(), []
    for i in idx:
        a = av[i]
        c = [b for b in nv if b["n"] not in used
             and .5 <= b["size"] / max(a["size"], 1) <= 2.]
        if c:
            b = min(c, key=lambda x: abs(x["size"] - a["size"]))
            used.add(b["n"])
            pairs.append((a, b))
    return pairs


print("=" * 78)
print("1. MULTIPLE COMPARISONS")
print("=" * 78)
# every test reported across investigate*.py + replicate.py on this corpus
pvals = {
    "r1 arch-vs-other churn": 0.0001, "r1 arch-vs-other files": 0.00001,
    "r1 arch-vs-other merge": 0.3159, "r1 arch-vs-other comments": 0.9824,
    "r1 arch-vs-other reviews": 0.0456, "r1 arch-vs-other threads": 0.1920,
    "r1 abs-vs-relo churn": 0.4952, "r1 abs-vs-relo files": 0.4744,
    "r1 abs-vs-relo merge": 0.6887, "r1 abs-vs-relo comments": 0.6598,
    "r1 abs-vs-relo threads": 0.0426,
    "r1 migration churn": 0.00001, "r1 migration merge": 0.0602,
    "r1 migration comments": 0.0247,
    "r2 PR size vs other": 0.0337, "r2 PR files vs other": 0.0013,
    "r2 PR merge vs other": 0.3159, "r2 PR reviews vs other": 0.0456,
    "r2 PR size vs none": 0.0002, "r2 PR merge vs none": 0.0102,
    "r2 PR threads vs none": 0.00001,
    "r2 survival lifespan": 0.00001,
    "r3 indep reviewers": 0.0002, "r3 commits per PR raw": 0.00001,
    "r3 temporal trend": 0.215,
    "MATCHED merge": 0.0584, "MATCHED rework": 0.0140, "MATCHED threads": 0.0049,
}
names = list(pvals)
p = np.array([pvals[k] for k in names])
order = np.argsort(p)
m = len(p)
bh = np.empty(m)
prev = 1.0
for rank in range(m - 1, -1, -1):
    i = order[rank]
    prev = min(prev, p[i] * m / (rank + 1))
    bh[i] = prev
print(f"    total tests run on this corpus: {m}")
print(f"    Bonferroni threshold: {0.05/m:.5f}")
print(f"\n    {'test':30}{'raw p':>10}{'BH q':>10}  verdict")
for k in ("MATCHED rework", "MATCHED threads", "MATCHED merge",
          "r3 indep reviewers", "r1 abs-vs-relo threads"):
    i = names.index(k)
    v = "survives FDR" if bh[i] < .05 else "FAILS FDR"
    b = "survives Bonf" if p[i] < .05 / m else ""
    print(f"    {k:30}{p[i]:10.4f}{bh[i]:10.4f}  {v} {b}")

print("\n" + "=" * 78)
print("2. MATCHING INSTABILITY  (greedy order dependence, 500 bootstraps)")
print("=" * 78)
for key, lab in (("commits", "rework"), ("threads", "review threads"),
                 ("merge", "merge latency")):
    ps = []
    av = [r for r in A if r.get(key) is not None]
    for _ in range(500):
        o = RNG.permutation(len(av))
        pr = match(A, N, key, o)
        if len(pr) < 5:
            continue
        x = [a[key] for a, _ in pr]
        y = [b[key] for _, b in pr]
        if len(set(x + y)) < 2:
            continue
        ps.append(stats.mannwhitneyu(x, y, alternative="two-sided")[1])
    ps = np.array(ps)
    print(f"    {lab:16} median p={np.median(ps):.4f}  "
          f"[{np.percentile(ps,5):.4f}, {np.percentile(ps,95):.4f}]  "
          f"significant in {100*(ps<.05).mean():3.0f}% of orderings")

print("\n" + "=" * 78)
print("3. ZERO-INFLATION  (review threads as a proportion, not a rank test)")
print("=" * 78)
pairs = match(A, N, "threads")
a_any = sum(1 for a, _ in pairs if a["threads"] > 0)
b_any = sum(1 for _, b in pairs if b["threads"] > 0)
n = len(pairs)
print(f"    matched pairs: {n}")
print(f"    architectural PRs with >=1 review thread: {a_any}/{n} ({100*a_any/n:.0f}%)")
print(f"    matched controls with >=1 review thread:  {b_any}/{n} ({100*b_any/n:.0f}%)")
tbl = [[a_any, n - a_any], [b_any, n - b_any]]
try:
    _, pf = stats.fisher_exact(tbl)
    print(f"    Fisher exact p={pf:.4f}  "
          f"{'holds as a proportion' if pf < .05 else 'DOES NOT hold as a proportion'}")
except Exception as e:
    print("   ", e)
# McNemar (paired) is the stricter test for matched pairs
disc_a = sum(1 for a, b in pairs if a["threads"] > 0 and b["threads"] == 0)
disc_b = sum(1 for a, b in pairs if a["threads"] == 0 and b["threads"] > 0)
if disc_a + disc_b > 0:
    pm = stats.binomtest(disc_a, disc_a + disc_b, 0.5).pvalue
    print(f"    McNemar (paired): {disc_a} vs {disc_b} discordant, p={pm:.4f}")

print("\n" + "=" * 78)
print("4. IS 'commits per PR' REALLY REWORK?")
print("=" * 78)
mer = [r for r in rows if r["merge"] is not None and r["commits"] and r["size"]]
for x, lab in (("size", "PR size"), ("merge", "open duration")):
    rho, pp = stats.spearmanr([r[x] for r in mer], [r["commits"] for r in mer])
    print(f"    commits ~ {lab:16} rho={rho:+.2f} p={pp:.2e}")
print("    -> if commits tracks duration as strongly as size, it is a poor")
print("       rework proxy: a PR open longer accrues commits regardless.")

print("\n" + "=" * 78)
print("5. LINKAGE CONTAMINATION")
print("=" * 78)
tot = len(rmap)
arch_all = {s for s, t in rmap.items() if (set(t) - SUSPECT) & ARCH}
arch_linked = arch_all & linked_shas
print(f"    commits with RM output            {tot}")
print(f"    linked to a PR                    {len(linked_shas)} ({100*len(linked_shas)/tot:.0f}%)")
print(f"    architectural commits             {len(arch_all)}")
print(f"    ...of which linked to a PR        {len(arch_linked)} ({100*len(arch_linked)/len(arch_all):.0f}%)")
print(f"    ...UNLINKED (invisible to PR tests) {len(arch_all)-len(arch_linked)}")
print("    -> unlinked architectural commits land in PRs classified 'none',")
print("       contaminating the control group. This biases toward the NULL,")
print("       so the reported effects are conservative, not inflated.")
