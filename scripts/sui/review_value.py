#!/usr/bin/env python3
"""
review_value.py -- does code review actually prevent anything?

69% of architectural work in start-ui-web never passes through a PR. That is a
natural experiment: if reviewed architectural change survives better than
unreviewed architectural change, review has measurable value. If not, the
review attention we measured is ceremonial.

Outcome: for each architectural commit, do the .ts/.tsx files it touched get
DELETED, or architecturally re-refactored, within a horizon?

Confound to respect: PR-routed architectural work is 5x larger and 4x more
abstraction-heavy (selection_bias.py). Size is therefore matched before testing,
and the raw comparison is reported alongside so the difference is visible.

Right-censoring: commits near the end of history have not had a full horizon to
be undone in. Those are excluded rather than counted as survivors.
"""
import argparse, collections, datetime as dt, json, re, subprocess
import numpy as np
from scipy import stats

SUI = "/private/tmp/claude-502/-Users-malek-phd-walid-rq1-starter/f0f36bda-082a-433c-aeb1-42b6cb6f4578/scratchpad/sui"
ABSTRACTION = {"Extract Class", "Extract Method", "Extract And Move Method",
               "Extract Interface", "Extract Superclass"}
RELOCATION = {"Move Class", "Move And Rename Class", "Move Source Folder",
              "Move Method", "Move Attribute"}
ARCH = ABSTRACTION | RELOCATION
SUSPECT = {"Change Type Declaration Kind"}
HORIZON_DAYS = 180


def sh(*a):
    return subprocess.run(["git", "-C", SUI] + list(a), capture_output=True, text=True).stdout


def main():
    rmj = json.load(open("refminer_sui_merged.json"))
    rmap = {c["sha1"]: [r["type"] for r in c.get("refactorings", [])]
            for c in rmj["commits"]}

    # commit metadata + touched files
    meta, files = {}, {}
    cur = None
    for line in sh("log", "--all", "--name-only",
                   "--format=\x01%H\x02%at\x02%s").split("\n"):
        if line.startswith("\x01"):
            h, t, s = line[1:].split("\x02", 2)
            meta[h] = (int(t), s)
            cur = files[h] = []
        elif line.strip() and cur is not None and line.endswith((".ts", ".tsx")):
            cur.append(line.strip())

    # file deletion times
    died = {}
    t = None
    for line in sh("log", "--all", "--format=@%at", "--name-status",
                   "--diff-filter=D").split("\n"):
        if line.startswith("@"):
            t = int(line[1:])
        elif "\t" in line and t is not None:
            p = line.split("\t")[-1]
            if p.endswith((".ts", ".tsx")):
                died[p] = max(died.get(p, 0), t)

    # later architectural touches per file
    arch_touch = collections.defaultdict(list)
    for sha, types in rmap.items():
        if (set(types) - SUSPECT) & ARCH and sha in meta:
            for f in files.get(sha, []):
                arch_touch[f].append(meta[sha][0])
    for f in arch_touch:
        arch_touch[f].sort()

    now = max(t for t, _ in meta.values())
    horizon = HORIZON_DAYS * 86400

    rows = []
    for sha, types in rmap.items():
        if not ((set(types) - SUSPECT) & ARCH) or sha not in meta:
            continue
        ts, subj = meta[sha]
        if now - ts < horizon:          # right-censored: exclude
            continue
        fs = [f for f in files.get(sha, []) if f]
        if not fs:
            continue
        deleted = sum(1 for f in fs if died.get(f, 1 << 62) - ts <= horizon)
        redone = sum(1 for f in fs
                     if any(ts < x <= ts + horizon for x in arch_touch.get(f, [])))
        rows.append(dict(
            sha=sha, reviewed=bool(re.search(r"\(#(\d+)\)", subj)),
            n=len(fs), frac_deleted=deleted / len(fs), frac_redone=redone / len(fs),
            any_deleted=deleted > 0, any_redone=redone > 0,
            size=len(fs),
        ))

    R = [r for r in rows if r["reviewed"]]
    U = [r for r in rows if not r["reviewed"]]
    print("=" * 78)
    print(f"DOES REVIEW PREVENT ANYTHING?  horizon={HORIZON_DAYS}d, "
          f"right-censored commits excluded")
    print("=" * 78)
    print(f"    architectural commits with a full horizon: {len(rows)}"
          f"   (reviewed {len(R)}, unreviewed {len(U)})")
    if len(R) < 5 or len(U) < 5:
        print("    too few in one arm to test")
        return

    def show(label, A, B):
        print(f"\n  {label}")
        for k, lab in (("frac_deleted", "fraction of files deleted"),
                       ("frac_redone", "fraction re-refactored")):
            x = [a[k] for a in A]
            y = [b[k] for b in B]
            _, p = stats.mannwhitneyu(x, y, alternative="two-sided")
            s = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
            print(f"    {lab:32} {np.median(x):6.3f} vs {np.median(y):6.3f} "
                  f"n={len(x)}/{len(y)} p={p:.4f} {s}")
        for k, lab in (("any_deleted", "any file deleted"),
                       ("any_redone", "any file re-refactored")):
            a1 = sum(a[k] for a in A)
            b1 = sum(b[k] for b in B)
            tbl = [[a1, len(A) - a1], [b1, len(B) - b1]]
            _, p = stats.fisher_exact(tbl)
            print(f"    {lab:32} {100*a1/len(A):5.0f}% vs {100*b1/len(B):5.0f}% "
                  f"                   p={p:.4f}")

    show("RAW (reviewed vs unreviewed) -- confounded by size", R, U)

    # size-matched on number of .ts files touched
    used, pairs = set(), []
    for a in sorted(R, key=lambda x: -x["size"]):
        cand = [b for b in U if b["sha"] not in used
                and .5 <= b["size"] / max(a["size"], 1) <= 2.]
        if cand:
            b = min(cand, key=lambda x: abs(x["size"] - a["size"]))
            used.add(b["sha"])
            pairs.append((a, b))
    print(f"\n  SIZE-MATCHED ({len(pairs)} pairs)")
    if len(pairs) >= 5:
        A2 = [a for a, _ in pairs]
        B2 = [b for _, b in pairs]
        _, pc = stats.mannwhitneyu([a["size"] for a in A2], [b["size"] for b in B2],
                                   alternative="two-sided")
        print(f"    size check: {np.median([a['size'] for a in A2]):.1f} vs "
              f"{np.median([b['size'] for b in B2]):.1f} files  p={pc:.3f}")
        show("matched", A2, B2)
    else:
        print("    too few matched pairs to test")


if __name__ == "__main__":
    main()
