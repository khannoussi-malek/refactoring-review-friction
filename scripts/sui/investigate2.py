#!/usr/bin/env python3
"""
investigate2.py -- round 2. Fixes round 1's errors and pushes the live threads.

Round 1 problems this addresses:
  * commit-level unit wasted 74% of the data (only 26% of commits link a PR).
    Friction lives on the PR, so aggregate refactorings TO the PR.
  * section 7 used PATH-based tier assignment, which the earlier probe showed
    misclassifies 88% of the contract surface. Uses the import graph instead.
  * no check on whether the 3 lost RM chunks bias the corpus.

New angles: file survival x refactoring history; what the V3 reset did.
"""
import json, re, subprocess, collections, datetime as dt
import numpy as np
from scipy import stats

SUI = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/sui"
PRS = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/prs_all.json"

ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
SUSPECT = {"Change Type Declaration Kind"}


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


def mw(a, b, label, unit=""):
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if len(a) < 3 or len(b) < 3:
        return f"    {label:32} n too small ({len(a)}/{len(b)})"
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    sig = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return (f"    {label:32} {np.median(a):8.2f} vs {np.median(b):8.2f} {unit:4} "
            f"n={len(a)}/{len(b)} p={p:.4f} {sig}")


# ---------------------------------------------------------------- coverage
print("=" * 78)
print("0. COVERAGE CHECK -- do the 3 lost RM chunks bias the corpus?")
print("=" * 78)
rmj = json.load(open("refminer_sui.json"))
seen = {c["sha1"] for c in rmj["commits"]}
allc = [l.split() for l in sh("log", "--format=%H %at").strip().split("\n")]
missing = [(h, int(t)) for h, t in allc if h not in seen]
print(f"    commits in history {len(allc)}, analysed {len(seen)}, missing {len(missing)}")
if missing:
    yrs = collections.Counter(dt.datetime.fromtimestamp(t).year for _, t in missing)
    print(f"    missing by year: {dict(sorted(yrs.items()))}")
    tot = collections.Counter(dt.datetime.fromtimestamp(int(t)).year for _, t in allc)
    print("    -> loss is CLUSTERED, not random:" if max(
        yrs[y] / tot[y] for y in yrs) > .5 else "    -> loss looks diffuse")
    for y in sorted(yrs):
        print(f"       {y}: {yrs[y]:4}/{tot[y]:4} missing ({100*yrs[y]/tot[y]:3.0f}%)")

# ---------------------------------------------------------------- PR level
print("\n" + "=" * 78)
print("1. PR-LEVEL ANALYSIS  (the unit that actually carries review data)")
print("=" * 78)
rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])] for c in rmj["commits"]}
subj = {}
for line in sh("log", "--format=%H\x02%s\x02%at\x02%ae").strip().split("\n"):
    h, s, t, a = line.split("\x02")
    subj[h] = (s, int(t), a)

pr_ref = collections.defaultdict(list)
for sha, types in rmap.items():
    if sha not in subj:
        continue
    m = re.search(r"\(#(\d+)\)", subj[sha][0])
    if m:
        pr_ref[int(m.group(1))].extend(t for t in types if t not in SUSPECT)

prs = {p["number"]: p for p in json.load(open(PRS))}
f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
rows = []
for n, p in prs.items():
    types = set(pr_ref.get(n, []))
    cls = ("abstraction" if types & ABSTRACTION else
           "relocation" if types & RELOCATION else
           "other-refactoring" if types else "none")
    rows.append(dict(
        n=n, cls=cls,
        merge=(f(p["mergedAt"]) - f(p["createdAt"])).total_seconds() / 86400
        if p.get("mergedAt") else None,
        comments=p["comments"]["totalCount"], reviews=p["reviews"]["totalCount"],
        threads=p["reviewThreads"]["totalCount"],
        size=p["additions"] + p["deletions"], files=p["changedFiles"],
        author=(p["author"] or {}).get("login", "?"),
    ))
arch = [r for r in rows if r["cls"] in ("abstraction", "relocation")]
oth = [r for r in rows if r["cls"] == "other-refactoring"]
non = [r for r in rows if r["cls"] == "none"]
print(f"    PRs {len(rows)}: architectural {len(arch)}, other-refac {len(oth)}, none {len(non)}")
print("\n  -- architectural vs other-refactoring PRs --")
for k, lab, u in (("size", "PR size (lines)", "loc"), ("files", "files changed", ""),
                  ("merge", "merge latency", "d"), ("comments", "comments", ""),
                  ("reviews", "reviews", ""), ("threads", "review threads", "")):
    print(mw([r[k] for r in arch], [r[k] for r in oth], lab, u))
print("\n  -- architectural vs NON-refactoring PRs --")
for k, lab, u in (("size", "PR size (lines)", "loc"), ("merge", "merge latency", "d"),
                  ("comments", "comments", ""), ("threads", "review threads", "")):
    print(mw([r[k] for r in arch], [r[k] for r in non], lab, u))

# ------------------------------------------------- size-controlled friction
print("\n" + "=" * 78)
print("2. IS THE FRICTION JUST SIZE?  (matched on PR size)")
print("=" * 78)
pool = [r for r in rows if r["merge"] is not None and r["size"]]
A = [r for r in pool if r["cls"] in ("abstraction", "relocation")]
B = [r for r in pool if r["cls"] == "none"]
matched = []
used = set()
for a in A:
    cand = [b for b in B if b["n"] not in used and 0.5 <= b["size"] / max(a["size"], 1) <= 2.0]
    if cand:
        b = min(cand, key=lambda x: abs(x["size"] - a["size"]))
        used.add(b["n"])
        matched.append((a, b))
print(f"    matched pairs: {len(matched)}")
if len(matched) >= 5:
    for k, lab, u in (("size", "PR size (check)", "loc"), ("merge", "merge latency", "d"),
                      ("comments", "comments", ""), ("threads", "review threads", "")):
        print(mw([a[k] for a, _ in matched], [b[k] for _, b in matched], lab, u))

# ------------------------------------------------- survival x refactoring
print("\n" + "=" * 78)
print("3. DO REFACTORED FILES SURVIVE LONGER?")
print("=" * 78)
log = sh("log", "--all", "--format=@%at", "--name-status", "--diff-filter=AD")
born, died, t = {}, {}, None
for line in log.split("\n"):
    if line.startswith("@"):
        t = int(line[1:])
        continue
    p = line.split("\t")
    if len(p) < 2 or t is None or not p[-1].endswith((".ts", ".tsx")):
        continue
    if p[0] == "A":
        born[p[-1]] = min(born.get(p[-1], t), t)
    elif p[0] == "D":
        died[p[-1]] = max(died.get(p[-1], 0), t)
# which files were ever touched by an architectural refactoring commit?
arch_shas = {s for s, ts in rmap.items()
             if (set(ts) - SUSPECT) & (ABSTRACTION | RELOCATION)}
touched = set()
for s in arch_shas:
    for line in sh("show", "--name-only", "--format=", "-1", s).strip().split("\n"):
        if line.endswith((".ts", ".tsx")):
            touched.add(line)
now = max(born.values())
lives_t = [((died.get(fn, now) - b) / 86400, fn in died) for fn, b in born.items() if fn in touched]
lives_u = [((died.get(fn, now) - b) / 86400, fn in died) for fn, b in born.items() if fn not in touched]
print(f"    files ever architecturally refactored: {len(lives_t)}")
print(f"    files never:                           {len(lives_u)}")
print(mw([d for d, _ in lives_t], [d for d, _ in lives_u], "lifespan", "d"))
print(f"    death rate: refactored {100*sum(x for _,x in lives_t)/max(len(lives_t),1):.0f}%"
      f"  vs untouched {100*sum(x for _,x in lives_u)/max(len(lives_u),1):.0f}%")

# ------------------------------------------------- import-graph tiers
print("\n" + "=" * 78)
print("4. TIER REACH -- import-graph derived (NOT path-based)")
print("=" * 78)
head = sh("rev-parse", "HEAD").strip()
tree = [f for f in sh("ls-tree", "-r", "--name-only", head).split("\n")
        if f.endswith((".ts", ".tsx")) and ".spec." not in f]
src = {f: sh("show", f"{head}:{f}") for f in tree}
def resolve(imp):
    if not imp.startswith("@/"):
        return None
    b = "src/" + imp[2:]
    for c in (b + ".ts", b + ".tsx", b + "/index.ts", b + "/index.tsx"):
        if c in src:
            return c
edges = collections.defaultdict(set)
for f, s in src.items():
    for imp in re.findall(r"from\s+['\"]([^'\"]+)['\"]", s):
        r = resolve(imp)
        if r:
            edges[f].add(r)
def closure(seeds):
    seen_, st = set(seeds), list(seeds)
    while st:
        for m in edges[st.pop()]:
            if m not in seen_:
                seen_.add(m); st.append(m)
    return seen_
S = closure([f for f in src if f.startswith("src/server/")])
C = closure([f for f in src if f.startswith(("src/routes/", "src/layout/", "src/components/"))])
shared = S & C
print(f"    server-reachable {len(S)}, client-reachable {len(C)}, SHARED {len(shared)}")
arch_files = touched & set(src)
oth_shas = {s for s, ts in rmap.items() if (set(ts) - SUSPECT) and s not in arch_shas}
oth_files = set()
for s in oth_shas:
    for line in sh("show", "--name-only", "--format=", "-1", s).strip().split("\n"):
        if line in src:
            oth_files.add(line)
for lab, fs in (("architectural", arch_files), ("other-refactoring", oth_files - arch_files)):
    if not fs:
        continue
    print(f"    {lab:20} touches shared-contract files: "
          f"{len(fs & shared)}/{len(fs)} ({100*len(fs & shared)/len(fs):.0f}%)")
print(f"    baseline: shared files are {100*len(shared)/len(src):.0f}% of the codebase")
