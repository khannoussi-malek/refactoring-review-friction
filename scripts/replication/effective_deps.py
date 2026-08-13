#!/usr/bin/env python3
"""
effective_deps.py — apply the FROZEN tier rule to a project's EFFECTIVE poms.

Why not raw pom.xml. A module's raw pom shows only what it declares; everything
inherited from the parent (and every version resolved through
<dependencyManagement> or an imported BOM) is invisible. The frozen rule divides
rare third-party groupIds by TOTAL declared dependencies, so a project that puts
its common dependencies in the parent would show an inflated vendor share for
every module. `mvn help:effective-pom` resolves all of that first.

This script does NOT reimplement the rule. It builds the same {artifact: {...}}
structure that external_wrapper_tier.py expects and calls the frozen
score_modules / centrality / classify. If the rule needs to change, this file is
the wrong place to change it -- and the point of freezing is that it does not.

Generate the input first (~2 min for a 119-module project):

    mvn -q -B help:effective-pom -Doutput=/abs/path/<project>-effective.xml

Usage:
    python3 scripts/replication/effective_deps.py --xml hive-effective.xml \\
        --project hive --out predictions/hive.json
"""
import argparse, json, os, sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from external_wrapper_tier import score_modules, centrality, classify   # FROZEN

NS = {"m": "http://maven.apache.org/POM/4.0.0"}
TAU, CUT = 0.05, 0.40          # frozen parameters — see external_wrapper_tier.py


def _text(node, path):
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else None


def module_dir(proj, repo_root):
    """Effective poms carry absolute build paths; recover the module directory
    from sourceDirectory (or the build directory) and make it repo-relative."""
    for path in ("m:build/m:sourceDirectory", "m:build/m:directory"):
        v = _text(proj, path)
        if not v:
            continue
        d = v
        for suffix in ("/src/main/java", "/src/main/scala", "/target"):
            if d.endswith(suffix):
                d = d[: -len(suffix)]
                break
        return os.path.relpath(d, repo_root) if repo_root else d
    return None


def load(xml_path, repo_root):
    """Effective-pom XML -> the structure the frozen rule consumes."""
    root = ET.parse(xml_path).getroot()
    projects = root.findall("m:project", NS) or ([root] if root.tag.endswith("project") else [])
    out = {}
    for proj in projects:
        art = _text(proj, "m:artifactId")
        if not art:
            continue
        gid = _text(proj, "m:groupId") or _text(proj, "m:parent/m:groupId")
        deps = []
        for d in proj.findall("m:dependencies/m:dependency", NS):
            dg, da = _text(d, "m:groupId"), _text(d, "m:artifactId")
            scope = _text(d, "m:scope") or "compile"
            if dg and da and scope in ("compile", "runtime"):
                deps.append((dg, da))
        # A module listed twice (profiles) keeps the richer dependency set.
        if art not in out or len(deps) > len(out[art]["deps"]):
            out[art] = {"dir": module_dir(proj, repo_root), "group": gid, "deps": deps}
    return out


def project_prefix_of(poms, override=None):
    """Frozen rule's prefix detection, with an override for projects whose
    modules do not share a three-part groupId."""
    if override:
        return override
    import pandas as pd
    groups = pd.Series([m["group"] for m in poms.values() if m["group"]])
    return ".".join(groups.value_counts().idxmax().split(".")[:3])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--repo-root", default=None, help="to make module dirs relative")
    ap.add_argument("--prefix", default=None, help="override groupId prefix detection")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    poms = load(args.xml, args.repo_root)
    if not poms:
        raise SystemExit(f"no projects parsed from {args.xml}")
    prefix = project_prefix_of(poms, args.prefix)

    scores, prevalence = score_modules(poms, prefix, TAU)
    guard = centrality(poms)
    flags = classify(scores, "rare_pct", CUT, guard=guard)

    flagged = sorted(a for a, (w, _) in flags.items() if w)
    payload = {
        "project": args.project, "prefix": prefix, "n_modules": len(poms),
        "tau": TAU, "cut": CUT, "guard": "dependents < 90th percentile",
        "flagged": flagged,
        "modules": {a: {"vendor_share": round(scores[a]["rare_pct"], 4),
                        "n_deps": len({g for g, _ in poms[a]["deps"]}),
                        "dependents": int(guard.get(a, 0)),
                        "rare_groups": scores[a]["rare"],
                        "dir": poms[a]["dir"],
                        "flagged": bool(flags[a][0])}
                    for a in sorted(poms)},
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(payload, open(args.out, "w"), indent=2)

    print(f"{args.project}: {len(poms)} modules, prefix '{prefix}', "
          f"{len(flagged)} flagged as external-system wrappers")
    for a in flagged:
        m = payload["modules"][a]
        print(f"   {a:44s} share {m['vendor_share']:.2f}  deps {m['n_deps']:3d}  "
              f"dependents {m['dependents']:3d}  [{', '.join(m['rare_groups'][:3])}]")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
