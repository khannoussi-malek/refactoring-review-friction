#!/usr/bin/env python3
"""
wrapper_rule_v2.py — second operationalisation of "wraps an external system".

v1 (external_wrapper_tier.py) failed on held-out data: 0 of 3 projects. The
diagnosis is in replication/REPLICATION.md and it is specific -- v1 used VENDOR
SHARE, rare third-party groupIds as a fraction of all dependencies, and that has
the wrong functional form:

    drill-mongo-storage    8 deps, 1 rare -> 0.12   (a MongoDB adapter, 39.7 d)
    drill-java-exec       54 deps, 39 rare -> 0.72  (the core engine, 11.0 d)

A thin adapter's handful of dependencies are mostly the project's own standard
stack, so its one genuine vendor SDK is diluted; a large core module accumulates
unusual libraries simply by being large. v1 measured size, not externality.

v2 replaces the share with a PRESENCE test on a different signal:

    A groupId is a FOREIGN PRODUCT namespace if it is
       (a) org.apache.<X> where <X> is not this project, or
       (b) any non-org.apache groupId declared by at most tau of the project's
           modules.
    A module is an EXTERNAL-SYSTEM WRAPPER if it declares at least one
    compile/runtime dependency in a foreign product namespace AND its transitive
    dependent count is below the project's 75th percentile.

The rationale for (a): in the Apache ecosystem, depending on another top-level
project's artifacts is the clearest mechanical evidence that a module integrates
an external system -- org.apache.kafka in drill-storage-kafka, org.apache.accumulo
in hive-accumulo-handler. It needs no vendor list. (b) keeps the non-Apache
vendors that (a) misses (org.mongodb, software.amazon) via v1's rarity idea,
which was never the broken part.

The guard loosens from the 90th to the 75th percentile of dependents, because
v1's diagnosis showed core modules are the false-positive risk and they sit far
above either cut, while adapters sit at 0-2.

DEVELOPMENT SET: Hadoop, Hive, Drill, Kylin -- all four already have their
outcomes published, so they are burned and cannot test anything. This file is
fitted on them deliberately and openly. The test is the projects cloned after
the v1 result, none of which have been touched.

KNOWN CEILING, recorded before any test: two of the slowest modules in the
development set cannot be caught by ANY dependency-based rule --
hive-webhcat-java-client (16.2 d) and drill-jdbc-all (28.2 d) both declare zero
rare and zero foreign-product dependencies. One talks HTTP to a service using
the project's ordinary HTTP client; the other is a shaded JDBC driver. If the
external-system tier is real, a dependency-based operationalisation has a
recall ceiling well below 1.0 and only a code-level signal (what SPI does this
module implement?) can go further.

Usage:
    python3 scripts/wrapper_rule_v2.py --dev          # evaluate on burned data
    python3 scripts/wrapper_rule_v2.py --predict hive # emit flags for a project
"""
import argparse, json, os, sys

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(__file__))
from replication.effective_deps import load, project_prefix_of   # noqa: E402

TAU = 0.05           # inherited from v1: "rare" = declared by <=5% of modules
GUARD_PCTL = 75      # loosened from v1's 90th
DEV = ["hadoop", "hive", "drill", "kylin"]


def project_token(prefix):
    """org.apache.hive -> 'hive'. Used to decide which apache namespaces are
    FOREIGN, so it must be derived, never hard-coded."""
    return prefix.split(".")[-1].lower()


def foreign_groups(poms, prefix, tau, apache_any=False):
    """The set of groupIds that count as a foreign product namespace.

    apache_any=True was the first v2 attempt: treat ANY org.apache.<other>
    dependency as evidence of external integration. It fails badly and is kept
    only so the failure is reproducible -- in this ecosystem every module
    depends on org.apache.hadoop or org.apache.commons, so it flagged 24 of
    Hive's 40 modules and scored below v1. Ubiquity is not externality.
    """
    token = project_token(prefix)
    n_mod = max(len(poms), 1)
    prevalence = {}
    for m in poms.values():
        for g in {g for g, _ in m["deps"]}:
            prevalence[g] = prevalence.get(g, 0) + 1
    foreign = set()
    for g, n in prevalence.items():
        if g.startswith(prefix):
            continue                                   # our own artifacts
        if apache_any and g.startswith("org.apache."):
            if g.split(".")[2].lower() != token:
                foreign.add(g)
        elif n / n_mod <= tau:
            foreign.add(g)          # rare here, whoever publishes it
    return foreign


def classify_v2(poms, prefix, tau=TAU, guard_pctl=GUARD_PCTL):
    from external_wrapper_tier import centrality       # unchanged from v1
    foreign = foreign_groups(poms, prefix, tau)
    rad = centrality(poms)
    cut = np.percentile(list(rad.values()), guard_pctl) if rad else 0
    out = {}
    for a, m in poms.items():
        hits = sorted({g for g, _ in m["deps"] if g in foreign})
        out[a] = {"wrapper": bool(hits) and rad.get(a, 0) < cut,
                  "foreign": hits, "dependents": int(rad.get(a, 0))}
    return out


# ------------------------------------------------------------------ dev eval
def load_poms(project, xmldir):
    xml = os.path.join(xmldir, f"{project}-effective.xml")
    poms = load(xml, None)
    return poms, project_prefix_of(poms, None)


def dev_eval(args):
    """Does v2 rank the known-slow modules above the rest, on burned data?"""
    print("DEVELOPMENT-SET EVALUATION (these projects are burned; this is fitting,\n"
          "not testing). v1 numbers are shown alongside for comparison.\n")
    rows = []
    for proj in DEV:
        med = module_medians(proj)
        if not med:
            print(f"  {proj}: no module outcome file, skipped")
            continue
        poms, prefix = load_poms(proj, args.xmldir)
        v2 = classify_v2(poms, prefix)
        v1 = set(json.load(open(f"predictions/{proj}.json"))["flagged"]) \
            if os.path.exists(f"predictions/{proj}.json") else set()

        w2 = [d for m, d in med.items() if v2.get(m, {}).get("wrapper")]
        r2 = [d for m, d in med.items() if not v2.get(m, {}).get("wrapper")]
        w1 = [d for m, d in med.items() if m in v1]
        r1 = [d for m, d in med.items() if m not in v1]
        p2 = (stats.mannwhitneyu(w2, r2, alternative="two-sided")[1]
              if len(w2) >= 2 and len(r2) >= 2 else float("nan"))
        p1 = (stats.mannwhitneyu(w1, r1, alternative="two-sided")[1]
              if len(w1) >= 2 and len(r1) >= 2 else float("nan"))
        print(f"  {proj:8s} modules={len(med):3d}  "
              f"v2 flags {len(w2):2d}: {np.median(w2) if w2 else float('nan'):6.1f} vs "
              f"{np.median(r2) if r2 else float('nan'):6.1f} d  p={p2:.3f}   |   "
              f"v1 flags {len(w1):2d}: {np.median(w1) if w1 else float('nan'):6.1f} vs "
              f"{np.median(r1) if r1 else float('nan'):6.1f} d  p={p1:.3f}")
        for m, d in med.items():
            rows.append({"project": proj, "module": m, "days": d,
                         "v2": bool(v2.get(m, {}).get("wrapper")), "v1": m in v1})

    # Pooled across the development set: rank modules within project, then test.
    # Module counts per project are far too small individually (that is what the
    # Hadoop p=0.133 floor showed), so pooling normalised ranks is the only way
    # to see anything at this corpus size.
    print()
    for tag in ("v1", "v2"):
        pooled_w, pooled_r = [], []
        for proj in {r["project"] for r in rows}:
            sub = [r for r in rows if r["project"] == proj]
            order = {r["module"]: i for i, r in
                     enumerate(sorted(sub, key=lambda r: r["days"]))}
            for r in sub:
                q = order[r["module"]] / max(len(sub) - 1, 1)   # 0=fastest 1=slowest
                (pooled_w if r[tag] else pooled_r).append(q)
        p = stats.mannwhitneyu(pooled_w, pooled_r, alternative="two-sided")[1]
        print(f"  POOLED {tag}: flagged mean percentile {np.mean(pooled_w):.3f} "
              f"(n={len(pooled_w)}) vs unflagged {np.mean(pooled_r):.3f} "
              f"(n={len(pooled_r)})   p={p:.4f}")
    print("\n  0.500 = no signal. >0.500 = flagged modules are slower.")
    json.dump(rows, open("wrapper_rule_v2_dev.json", "w"), indent=1)


def module_medians(project, min_tickets=10):
    """Module -> median days, from whatever outcome data already exists."""
    p = f"replication/{project}.test.json"
    if os.path.exists(p):
        return {r["module"]: r["median_days"]
                for r in json.load(open(p))["modules"] if r["n_tickets"] >= min_tickets}
    if project == "hadoop":                       # Hadoop's outcomes live elsewhere
        import argparse as _a
        sys.path.insert(0, os.path.dirname(__file__))
        from blast_radius_model import build_frame
        ns = _a.Namespace(repo="hadoop", graph="module_blast_radius.json",
                          episode_files="episode_files.json",
                          episodes="architectural_episodes_all.json",
                          changelog=".jira_changelog", props=".jira_props",
                          assignees=".jira_assignee")
        _, tk = build_frame(ns)
        d = tk.dropna(subset=["triage"])
        return {m: float(g.triage.median()) for m, g in d.groupby("top_module")
                if len(g) >= min_tickets}
    return {}


def predict(args):
    poms, prefix = load_poms(args.predict, args.xmldir)
    res = classify_v2(poms, prefix)
    flagged = sorted(a for a, v in res.items() if v["wrapper"])
    out = {"project": args.predict, "prefix": prefix, "rule": "v2",
           "tau": TAU, "guard_pctl": GUARD_PCTL, "n_modules": len(poms),
           "flagged": flagged,
           "modules": {a: {**v, "dir": poms[a]["dir"]} for a, v in res.items()}}
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"{args.predict}: {len(poms)} modules, {len(flagged)} flagged (v2)")
    for a in flagged[:40]:
        print(f"   {a:46s} deps_on {res[a]['dependents']:3d}  "
              f"[{', '.join(res[a]['foreign'][:3])}]")
    print(f"Wrote {args.out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dev", action="store_true")
    ap.add_argument("--predict")
    ap.add_argument("--xmldir", default=".")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    if args.dev:
        dev_eval(args)
    elif args.predict:
        args.out = args.out or f"predictions_v2/{args.predict}.json"
        predict(args)
    else:
        ap.error("pass --dev or --predict <project>")


if __name__ == "__main__":
    main()
