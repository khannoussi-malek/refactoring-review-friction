#!/usr/bin/env python3
"""
repair_coverage.py -- find and re-run the commit ranges a chunked RM run lost.

run_rm_safe.sh trades coverage for liveness: a watchdog kills any chunk that
stalls, and the whole chunk's JSON is discarded. Because chunks are contiguous
commit ranges, the loss is CLUSTERED -- on start-ui-web an 88% aggregate figure
concealed a year that was 93% missing, which silently produced "no architectural
work in 2024".

That hole was repaired by hand. This does it systematically:
  1. diff the analysed SHAs against the range RM was asked to cover
  2. group the gaps into contiguous runs
  3. emit (or run) a repair pass over each gap, with a LONGER stall threshold

The longer threshold matters. A chunk dies because ONE commit in it is slow, and
~30 innocent commits die with it, so a repair pass at the same threshold tends to
lose the same ranges again. Default here is 3x the original.

Usage:
    python3 scripts/sui/repair_coverage.py --repo <path> --rm <refminer.json> \
        --out <repair.json> [--stall 400] [--run]

Without --run it prints the commands and changes nothing.
"""
import argparse, json, subprocess, sys


def sh(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a),
                          capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rm", required=True)
    ap.add_argument("--out", default="refminer_repair.json")
    ap.add_argument("--stall", type=int, default=400,
                    help="stall seconds for the repair pass (default 400)")
    ap.add_argument("--min-gap", type=int, default=3,
                    help="ignore gaps shorter than this many commits")
    ap.add_argument("--run", action="store_true", help="execute, not just print")
    a = ap.parse_args()

    have = {c["sha1"] for c in json.load(open(a.rm))["commits"]}
    root = sh(a.repo, "rev-list", "--max-parents=0", "HEAD").split()
    if not root:
        sys.exit("no root commit found")
    # oldest -> newest, the order chunks were cut in
    scope = [s for s in sh(a.repo, "rev-list", "--reverse",
                           f"{root[0]}..HEAD").split() if s]
    print(f"scope {len(scope)} commits, analysed {len(have & set(scope))}, "
          f"missing {len([s for s in scope if s not in have])}")

    gaps, cur = [], []
    for s in scope:
        if s in have:
            if cur:
                gaps.append(cur)
                cur = []
        else:
            cur.append(s)
    if cur:
        gaps.append(cur)
    gaps = [g for g in gaps if len(g) >= a.min_gap]
    if not gaps:
        print("no gaps worth repairing")
        return

    print(f"\n{len(gaps)} gap(s) >= {a.min_gap} commits "
          f"({sum(len(g) for g in gaps)} commits total):")
    cmds = []
    for i, g in enumerate(gaps, 1):
        # run_rm_safe.sh analyses START..END exclusive of START, so anchor one
        # commit BEFORE the gap when there is one.
        idx = scope.index(g[0])
        start = scope[idx - 1] if idx > 0 else g[0]
        end = g[-1]
        out = a.out.replace(".json", f"_{i}.json")
        n = max(2, min(16, len(g) // 20 + 2))
        cmd = (f"bash scripts/run_rm_safe.sh {a.repo} {start} {end} "
               f"{n} {a.stall} {out}")
        d1 = sh(a.repo, "show", "-s", "--format=%ai", g[0]).strip()[:10]
        d2 = sh(a.repo, "show", "-s", "--format=%ai", g[-1]).strip()[:10]
        print(f"  gap {i}: {len(g):4} commits  {d1} .. {d2}")
        cmds.append(cmd)

    print("\nrepair commands:")
    for c in cmds:
        print(f"  {c}")

    if not a.run:
        print("\n(dry run -- pass --run to execute)")
        return

    for i, c in enumerate(cmds, 1):
        print(f"\n=== repair {i}/{len(cmds)} ===")
        subprocess.run(c, shell=True)

    # merge everything that now exists
    merged = json.load(open(a.rm))
    seen = {c["sha1"] for c in merged["commits"]}
    added = 0
    for i in range(1, len(cmds) + 1):
        f = a.out.replace(".json", f"_{i}.json")
        try:
            for c in json.load(open(f))["commits"]:
                if c["sha1"] not in seen:
                    merged["commits"].append(c)
                    seen.add(c["sha1"])
                    added += 1
        except Exception as e:
            print(f"  skipping {f}: {e}")
    json.dump(merged, open(a.out, "w"))
    print(f"\nmerged +{added} commits -> {a.out} "
          f"({len(merged['commits'])}/{len(scope)} = "
          f"{100*len(merged['commits'])/len(scope):.0f}% coverage)")


if __name__ == "__main__":
    main()
