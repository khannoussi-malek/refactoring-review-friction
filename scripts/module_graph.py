#!/usr/bin/env python3
"""
module_graph.py — build the Maven module dependency graph of a monorepo and
compute each module's BLAST RADIUS: how many other modules (transitively)
depend on it.

This operationalises the mechanism proposed in the results dossier (§9): the
more depended-upon a module is, the more hesitation before touching its
structure. §9 only observed ~40x triage variation across four top-level
projects; blast radius turns that observation into a continuous predictor.

Usage:
    python3 scripts/module_graph.py --repo hadoop --out module_blast_radius.json
"""
import argparse, json, os
import xml.etree.ElementTree as ET
from collections import deque

NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _text(node, path):
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else None


def parse_poms(repo):
    """dir -> (artifactId, {dependency artifactIds}). Only internal deps matter,
    so groupId filtering happens later once we know every artifactId in-tree."""
    poms = {}
    for root, dirs, files in os.walk(repo):
        if ".git" in dirs:
            dirs.remove(".git")
        if "pom.xml" not in files:
            continue
        try:
            tree = ET.parse(os.path.join(root, "pom.xml"))
        except ET.ParseError:
            continue
        proj = tree.getroot()
        art = _text(proj, "m:artifactId")
        if not art:
            continue
        # ponytail: only project/dependencies. <dependencyManagement> declares
        # versions without depending, and <parent> is config inheritance, not a
        # code dependency -- neither belongs in a blast-radius graph.
        deps = {
            _text(d, "m:artifactId")
            for d in proj.findall("m:dependencies/m:dependency", NS)
        }
        poms[os.path.relpath(root, repo)] = (art, {d for d in deps if d})
    return poms


def blast_radius(edges):
    """edges: artifact -> {artifacts it depends on}.
    Returns artifact -> number of DISTINCT modules that transitively depend on it."""
    dependents = {a: set() for a in edges}
    for a, deps in edges.items():
        for d in deps:
            if d in dependents:
                dependents[d].add(a)

    radius = {}
    for target in edges:
        seen, q = set(), deque([target])
        while q:
            cur = q.popleft()
            for up in dependents.get(cur, ()):
                if up not in seen:
                    seen.add(up)
                    q.append(up)
        seen.discard(target)  # a module is not its own blast radius
        radius[target] = len(seen)
    return radius, {a: len(v) for a, v in dependents.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--out", default="module_blast_radius.json")
    args = ap.parse_args()

    poms = parse_poms(args.repo)
    if not poms:
        raise SystemExit(f"no pom.xml found under {args.repo}")

    internal = {art for art, _ in poms.values()}
    edges = {art: (deps & internal) for art, deps in poms.values()}
    radius, direct = blast_radius(edges)

    # dir -> artifact, so file paths can be attributed to a module later.
    dir_to_artifact = {d: art for d, (art, _) in poms.items()}

    out = {
        "modules": {
            art: {
                "blast_radius": radius[art],
                "direct_dependents": direct.get(art, 0),
                "depends_on": sorted(edges[art]),
            }
            for art in sorted(edges)
        },
        "dir_to_artifact": dir_to_artifact,
    }
    json.dump(out, open(args.out, "w"), indent=2)

    ranked = sorted(radius.items(), key=lambda kv: -kv[1])
    print(f"Modules: {len(edges)}   internal edges: {sum(len(v) for v in edges.values())}")
    print(f"\nTop 12 by blast radius (modules transitively depending on it):")
    for art, n in ranked[:12]:
        print(f"  {n:4d}  {art}")
    print(f"\nLeaves (blast radius 0): {sum(1 for _, n in ranked if n == 0)}")
    print(f"Wrote {args.out}")


def _self_check():
    """ponytail: one runnable check on the only non-trivial logic here."""
    edges = {"core": set(), "mid": {"core"}, "leaf": {"mid"}, "solo": set()}
    radius, direct = blast_radius(edges)
    assert radius == {"core": 2, "mid": 1, "leaf": 0, "solo": 0}, radius
    assert direct["core"] == 1, direct  # transitive 2, direct 1
    print("self-check OK")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()
