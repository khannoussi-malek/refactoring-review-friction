#!/usr/bin/env python3
"""
investigate.py -- deep exploratory pass over start-ui-web for RQ1 signal.

Joins every layer we can reach:
    RefactoringMiner output  ->  commits  ->  PRs/reviews  ->  files  ->  tiers
and then interrogates each angle for anything that bears on RQ1
(architectural refactoring and the friction around it).

Exploratory by design. Every p-value here is uncorrected and hypothesis-
GENERATING, not confirmatory. Nothing in this file may be reported as a result
without a pre-registered re-test on a held-out corpus.
"""
import json, re, subprocess, collections, datetime as dt
import numpy as np
from scipy import stats

SUI = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/sui"
RM = "refminer_sui.json"
PRS = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/prs_all.json"

ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass", "Extract Subclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
ARCH = ABSTRACTION | RELOCATION
# excluded: Change Type Declaration Kind -- suspected systematic false positive
SUSPECT = {"Change Type Declaration Kind"}


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


def load_commits():
    """sha -> {date, author, subject, files, insertions, deletions, paths}"""
    raw = sh("log", "--all", "--numstat", "--format=\x01%H\x02%at\x02%ae\x02%s")
    out, cur = {}, None
    for line in raw.split("\n"):
        if line.startswith("\x01"):
            h, t, a, s = line[1:].split("\x02", 3)
            cur = out[h] = dict(sha=h, ts=int(t), author=a, subject=s,
                                paths=[], ins=0, dele=0)
        elif line.strip() and cur is not None:
            p = line.split("\t")
            if len(p) == 3:
                cur["paths"].append(p[2])
                for k, v in (("ins", p[0]), ("dele", p[1])):
                    if v.isdigit():
                        cur[k] += int(v)
    return out


def classify(types):
    t = set(types) - SUSPECT
    if t & ABSTRACTION:
        return "abstraction"
    if t & RELOCATION:
        return "relocation"
    if t:
        return "other-refactoring"
    return "none"


def mw(a, b, label, unit=""):
    """Mann-Whitney U with medians; returns a printable line."""
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if len(a) < 3 or len(b) < 3:
        return f"    {label:34} n too small ({len(a)} vs {len(b)})"
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    sig = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
    return (f"    {label:34} {np.median(a):8.2f} vs {np.median(b):8.2f} {unit:5} "
            f"n={len(a)}/{len(b)}  p={p:.4f} {sig}")


def main():
    commits = load_commits()
    rmj = json.load(open(RM))
    rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])]
            for c in rmj["commits"]}
    prs = {p["number"]: p for p in json.load(open(PRS))}

    # ---- join -------------------------------------------------------------
    rows = []
    for sha, types in rmap.items():
        c = commits.get(sha)
        if not c:
            continue
        m = re.search(r"\(#(\d+)\)", c["subject"])
        pr = prs.get(int(m.group(1))) if m else None
        ts_files = [p for p in c["paths"] if p.endswith((".ts", ".tsx"))]
        rows.append(dict(
            sha=sha, ts=c["ts"], author=c["author"], subject=c["subject"],
            cls=classify(types), n_ref=len(types),
            churn=c["ins"] + c["dele"], nfiles=len(c["paths"]),
            migration=any(x in p for p in c["paths"]
                          for x in ("package.json", "pnpm-lock.yaml")),
            touches_server=any(p.startswith("src/server/") for p in ts_files),
            touches_client=any(p.startswith(("src/routes/", "src/components/",
                                             "src/layout/", "src/features/"))
                               for p in ts_files),
            has_test=any(".spec." in p or ".test." in p for p in c["paths"]),
            has_story=any("stories" in p for p in c["paths"]),
            pr=pr,
        ))

    def dt_days(p):
        if not p or not p.get("mergedAt"):
            return None
        f = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return (f(p["mergedAt"]) - f(p["createdAt"])).total_seconds() / 86400

    for r in rows:
        p = r["pr"]
        r["merge_days"] = dt_days(p)
        r["comments"] = p["comments"]["totalCount"] if p else None
        r["reviews"] = p["reviews"]["totalCount"] if p else None
        r["threads"] = p["reviewThreads"]["totalCount"] if p else None

    arch = [r for r in rows if r["cls"] in ("abstraction", "relocation")]
    absr = [r for r in rows if r["cls"] == "abstraction"]
    relo = [r for r in rows if r["cls"] == "relocation"]
    other = [r for r in rows if r["cls"] == "other-refactoring"]

    print("=" * 78)
    print("1. CORPUS")
    print("=" * 78)
    print(f"  commits with RM output      {len(rows)}")
    for k, v in collections.Counter(r["cls"] for r in rows).most_common():
        print(f"    {k:20} {v}")
    print(f"  architectural total         {len(arch)}  "
          f"(abstraction {len(absr)}, relocation {len(relo)})")
    print(f"  with a linked PR            {sum(1 for r in rows if r['pr'])}"
          f" / {len(rows)}  ({100*sum(1 for r in rows if r['pr'])/len(rows):.0f}%)")

    print("\n" + "=" * 78)
    print("2. IS ARCHITECTURAL WORK DIFFERENT?  (architectural vs other-refactoring)")
    print("=" * 78)
    for f, lab, u in (("churn", "churn (lines)", "loc"),
                      ("nfiles", "files touched", ""),
                      ("merge_days", "PR merge latency", "d"),
                      ("comments", "PR comments", ""),
                      ("reviews", "PR reviews", ""),
                      ("threads", "review threads", "")):
        print(mw([r[f] for r in arch], [r[f] for r in other], lab, u))

    print("\n" + "=" * 78)
    print("3. ABSTRACTION vs RELOCATION  (the Hadoop headline, re-asked here)")
    print("=" * 78)
    for f, lab, u in (("churn", "churn (lines)", "loc"),
                      ("nfiles", "files touched", ""),
                      ("merge_days", "PR merge latency", "d"),
                      ("comments", "PR comments", ""),
                      ("threads", "review threads", "")):
        print(mw([r[f] for r in absr], [r[f] for r in relo], lab, u))

    print("\n" + "=" * 78)
    print("4. MIGRATION-DRIVEN vs INTERNALLY MOTIVATED (architectural only)")
    print("=" * 78)
    mig = [r for r in arch if r["migration"]]
    own = [r for r in arch if not r["migration"]]
    print(f"    migration-driven {len(mig)} / internally motivated {len(own)}")
    for f, lab, u in (("churn", "churn (lines)", "loc"),
                      ("merge_days", "PR merge latency", "d"),
                      ("comments", "PR comments", "")):
        print(mw([r[f] for r in mig], [r[f] for r in own], lab, u))

    print("\n" + "=" * 78)
    print("5. WHO DOES ARCHITECTURAL WORK?")
    print("=" * 78)
    tot = collections.Counter(r["author"] for r in rows)
    ac = collections.Counter(r["author"] for r in arch)
    print(f"    {'author':34} {'arch':>5} {'all':>5} {'share':>6}")
    for a, n in ac.most_common(6):
        print(f"    {a[:32]:34} {n:5} {tot[a]:5} {100*n/tot[a]:5.0f}%")
    print(f"    Gini-ish: top author does {100*ac.most_common(1)[0][1]/len(arch):.0f}%"
          f" of architectural commits")

    print("\n" + "=" * 78)
    print("6. TESTS AND STORIES ACCOMPANYING ARCHITECTURAL CHANGE")
    print("=" * 78)
    for lab, grp in (("architectural", arch), ("other-refactoring", other)):
        t = 100 * sum(r["has_test"] for r in grp) / max(len(grp), 1)
        s = 100 * sum(r["has_story"] for r in grp) / max(len(grp), 1)
        print(f"    {lab:22} test touched {t:5.0f}%   story touched {s:5.0f}%")

    print("\n" + "=" * 78)
    print("7. TIER REACH  (does it cross the client/server line?)")
    print("=" * 78)
    for lab, grp in (("architectural", arch), ("other-refactoring", other)):
        both = sum(1 for r in grp if r["touches_server"] and r["touches_client"])
        srv = sum(1 for r in grp if r["touches_server"] and not r["touches_client"])
        cli = sum(1 for r in grp if r["touches_client"] and not r["touches_server"])
        n = max(len(grp), 1)
        print(f"    {lab:22} client-only {100*cli/n:4.0f}%  "
              f"server-only {100*srv/n:4.0f}%  BOTH {100*both/n:4.0f}%")

    print("\n" + "=" * 78)
    print("8. TIME  (architectural rate per year)")
    print("=" * 78)
    yr_all = collections.Counter(dt.datetime.fromtimestamp(r["ts"]).year for r in rows)
    yr_ar = collections.Counter(dt.datetime.fromtimestamp(r["ts"]).year for r in arch)
    print(f"    {'year':6} {'arch':>5} {'refac commits':>14} {'rate':>7}")
    for y in sorted(yr_all):
        print(f"    {y:6} {yr_ar[y]:5} {yr_all[y]:14} "
              f"{100*yr_ar[y]/yr_all[y]:6.0f}%")

    return rows, arch, absr, relo, other


if __name__ == "__main__":
    main()
