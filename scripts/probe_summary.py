#!/usr/bin/env python3
"""
probe_summary.py — the distributional facts about the 38-project probe.

Written 2026-08-05 because a claim the manuscript wanted to make — "the median
sits near 35%" — could not be reproduced from `paper/traceability_probe.json`
under any grouping. Rather than quote it or drop it silently, this computes every
grouping a reader might mean and writes them out, so the claim can be replaced
with a sourced one and the discrepancy recorded.

Reads the committed probe artifact only. No clone, no network.

Usage:
    python3 scripts/probe_summary.py --out paper/probe_summary.json
"""
import argparse, json, statistics


def stats(vals):
    v = sorted(vals)
    if not v:
        return None
    return {"n": len(v), "min": v[0], "max": v[-1],
            "median": statistics.median(v), "mean": sum(v) / len(v)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default="paper/traceability_probe.json")
    ap.add_argument("--out", default="paper/probe_summary.json")
    args = ap.parse_args()

    d = json.load(open(args.probe))
    ps = d["projects"]
    bar = d["bar"]

    groups = {
        "all_probed": [p["rate_multi"] for p in ps],
        "cleared_the_bar": [p["rate_multi"] for p in ps if p["passes_bar"]],
        "dropped": [p["rate_multi"] for p in ps if not p["passes_bar"]],
        "single_key_all": [p["rate_single"] for p in ps],
        "below_60pc": [p["rate_multi"] for p in ps if p["rate_multi"] < 0.60],
    }
    out = {"probe": args.probe, "bar": bar,
           "groups": {k: stats(v) for k, v in groups.items()}}

    # what lowering the bar would have bought, since the manuscript states it
    for cut in (0.80, 0.70, 0.60, 0.50):
        out.setdefault("pass_counts_at", {})[f"{cut:.2f}"] = sum(
            1 for p in ps if p["rate_multi"] >= cut)

    # the best project below the bar, and the best that is not Hadoop-ecosystem.
    # Family is a hand classification -- it is not a field in the probe -- so the
    # list is written here explicitly rather than inferred.
    HADOOP_ECOSYSTEM = {
        "ozone", "tez", "hive", "hbase", "phoenix", "zookeeper", "ranger",
        "oozie", "knox", "drill", "kylin", "sqoop", "atlas", "parquet-java",
        "accumulo", "hudi", "storm",
    }
    out["family_note"] = ("HADOOP_ECOSYSTEM is a hand classification made in this "
                          "script, not a recorded field in the probe. "
                          "paper/numbers.md §7 records that family is not a "
                          "recorded field; any claim keyed on it inherits that.")
    dropped = [p for p in ps if not p["passes_bar"]]
    out["best_dropped"] = max(
        ({"project": p["project"], "rate": p["rate_multi"]} for p in dropped),
        key=lambda r: r["rate"])
    outside = [p for p in ps if p["project"] not in HADOOP_ECOSYSTEM]
    out["best_outside_hadoop_ecosystem"] = max(
        ({"project": p["project"], "rate": p["rate_multi"]} for p in outside),
        key=lambda r: r["rate"])
    out["cleared_bar_outside_hadoop_ecosystem"] = [
        p["project"] for p in outside if p["passes_bar"]]

    json.dump(out, open(args.out, "w"), indent=1)
    for k, v in out["groups"].items():
        print(f"{k:22s} n={v['n']:2d}  min={v['min']*100:5.1f}%  "
              f"median={v['median']*100:5.1f}%  mean={v['mean']*100:5.1f}%  "
              f"max={v['max']*100:5.1f}%")
    print("\npass count at bar:", out["pass_counts_at"])
    print("best dropped:", out["best_dropped"])
    print("best outside the Hadoop ecosystem:", out["best_outside_hadoop_ecosystem"])
    print("cleared the bar outside the Hadoop ecosystem:",
          out["cleared_bar_outside_hadoop_ecosystem"] or "none")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
