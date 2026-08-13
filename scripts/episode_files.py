#!/usr/bin/env python3
"""
episode_files.py — for every architectural episode, recover the file paths the
ARCHITECTURAL refactorings actually touched (not the whole commit's diff, which
drags in tests and unrelated edits).

Reuses the exact filter from filter_architectural.py so the episode set here is
by construction the same 349 episodes, just annotated with paths.

Cached step: refminer_all.json is ~135MB, so run once and reuse the output.

Usage:
    python3 scripts/episode_files.py --rm refminer_all.json \
        --episodes architectural_episodes_all.json --out episode_files.json
"""
import argparse, json, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from filter_architectural import PACKAGE_TYPES, CLASS_MOVE_TYPES, FQN, pkg_of


def is_architectural(ref):
    """Same decision rule as filter_architectural.main()."""
    t = ref.get("type", "").strip()
    if t in PACKAGE_TYPES:
        return True
    if t in CLASS_MOVE_TYPES:
        fqns = FQN.findall(ref.get("description", ""))
        return len(fqns) >= 2 and pkg_of(fqns[0]) != pkg_of(fqns[-1])
    return False


def paths_of(ref):
    """Right side = where the code LANDS; left side = where it came from. Both
    are part of the refactoring's footprint."""
    out = set()
    for side in ("leftSideLocations", "rightSideLocations"):
        for loc in ref.get(side, []) or []:
            p = loc.get("filePath")
            if p:
                out.add(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rm", default="refminer_all.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--out", default="episode_files.json")
    args = ap.parse_args()

    wanted = {e["sha1"] for e in json.load(open(args.episodes))}
    data = json.load(open(args.rm))
    commits = data.get("commits", data if isinstance(data, list) else [])

    result, type_counts = {}, Counter()
    for c in commits:
        sha = c.get("sha1") or c.get("sha")
        if sha not in wanted:
            continue
        paths, types = set(), []
        for r in c.get("refactorings", []):
            if is_architectural(r):
                paths |= paths_of(r)
                types.append(r.get("type", "").strip())
        if paths:
            result[sha] = sorted(paths)
            type_counts.update(types)

    json.dump(result, open(args.out, "w"), indent=2)
    missing = len(wanted) - len(result)
    print(f"Episodes requested : {len(wanted)}")
    print(f"Episodes with paths: {len(result)}   (no path recovered: {missing})")
    print(f"Distinct files touched by architectural refactorings: "
          f"{len({p for v in result.values() for p in v})}")
    print(f"\nArchitectural refactoring types matched:")
    for t, n in type_counts.most_common():
        print(f"  {n:5d}  {t}")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
