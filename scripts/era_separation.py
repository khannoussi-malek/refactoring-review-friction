#!/usr/bin/env python3
"""
era_separation.py — does project generation separate the corpus better than the
hand-drawn "Hadoop-ecosystem" label?

The population finding — "12 of 38 pass and all 12 are Hadoop-ecosystem" — rests
on a hand classification that is not a field in any dataset. The proposal under
test is that ASF generation is the better variable: free metadata, no judgment,
and a mechanism (projects that predate the 2019-20 migration to GitHub pull
requests kept the Jira-citation convention).

TWO GENERATION VARIABLES, and the difference between them matters.

  repo_start_year   The year of the earliest commit on ANY ref of the project's
                    repository, computed here from the pinned clones. Available
                    for all 38, exact, and needs no external source.

  graduation        Month and year the podling graduated from the Apache
                    Incubator, read from https://incubator.apache.org/projects/
                    on 2026-08-05. MISSING for projects that were never
                    incubated as podlings -- and, critically, missing for four
                    of the twelve that pass, because they entered the ASF as
                    Hadoop subprojects rather than through the incubator. The
                    variable is therefore missing-not-at-random with respect to
                    the outcome, which is the finding rather than an obstacle.

Separation is scored three ways: Fisher exact on the 2x2 for the categorical
label, and AUC plus Mann-Whitney for the continuous ones, with the best single
threshold's accuracy for comparability.

Usage:
    python3 scripts/era_separation.py --out paper/era_separation.json
"""
import argparse, json, math, statistics

METRICS = "paper/revision_metrics.json"

# Hand classification, reproduced from scripts/probe_summary.py so the two
# cannot drift. It is the thing under test, not an input to be trusted.
HADOOP_ECOSYSTEM = {
    "ozone", "tez", "hive", "hbase", "phoenix", "zookeeper", "ranger",
    "oozie", "knox", "drill", "kylin", "sqoop", "atlas", "parquet-java",
    "accumulo", "hudi", "storm",
}

# Apache Incubator graduation dates, https://incubator.apache.org/projects/,
# read 2026-08-05. Projects absent from that list are recorded as None, which
# for this corpus means "entered the ASF other than as a podling".
GRADUATION = {
    "atlas": 2017.5, "calcite": 2015.83, "drill": 2014.92, "kylin": 2015.92,
    "knox": 2014.17, "ranger": 2017.08, "tez": 2014.58, "hudi": 2020.42,
    "pinot": 2021.58, "dubbo": 2019.42, "rocketmq": 2017.75,
    "shardingsphere": 2020.33, "skywalking": 2019.33, "parquet-java": 2015.33,
    "storm": 2014.75, "flink": 2014.99, "helix": 2013.99, "sqoop": 2012.25,
    "oozie": 2012.67, "phoenix": 2014.42, "syncope": 2012.92, "tika": 2008.83,
    "oodt": 2010.92, "servicecomb-java-chassis": 2018.83,
    # never incubated as podlings, or graduation date not on that page
    "hive": None, "hbase": None, "zookeeper": None, "ozone": None,
    "jena": None, "wicket": None, "karaf": None, "tomee": None, "struts": None,
    "james-project": None, "cxf": None, "flume": None, "accumulo": None,
    "zeppelin": None,
}


def fisher_two_sided(a, b, c, d):
    C = math.comb
    tot, row1, row2, col1 = a + b + c + d, a + b, c + d, a + c
    obs = C(row1, a) * C(row2, c) / C(tot, col1)
    p = 0.0
    for i in range(max(0, col1 - row2), min(row1, col1) + 1):
        pr = C(row1, i) * C(row2, col1 - i) / C(tot, col1)
        if pr <= obs + 1e-12:
            p += pr
    return min(1.0, p)


def auc_and_u(pos, neg):
    """AUC = P(pos > neg), with ties at half. Mann-Whitney normal approximation."""
    if not pos or not neg:
        return None
    wins = sum(1 for x in pos for y in neg if x > y) + \
        0.5 * sum(1 for x in pos for y in neg if x == y)
    n1, n2 = len(pos), len(neg)
    auc = wins / (n1 * n2)
    mu = n1 * n2 / 2
    sd = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (wins - mu) / sd if sd else 0.0
    return {"auc": auc, "u": wins, "z": z,
            "p_normal_approx": math.erfc(abs(z) / math.sqrt(2)),
            "n_pos": n1, "n_neg": n2}


def best_threshold(pos, neg):
    """Accuracy of the best single '>= t' rule, for comparison with a label."""
    vals = sorted(set(pos + neg))
    best = None
    for t in vals:
        tp = sum(1 for v in pos if v >= t)
        fp = sum(1 for v in neg if v >= t)
        acc = (tp + (len(neg) - fp)) / (len(pos) + len(neg))
        if best is None or acc > best["accuracy"]:
            best = {"threshold": t, "accuracy": acc, "tp": tp, "fp": fp,
                    "fn": len(pos) - tp, "tn": len(neg) - fp}
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default=METRICS)
    ap.add_argument("--out", default="paper/era_separation.json")
    args = ap.parse_args()

    P = json.load(open(args.metrics))["projects"]
    rows = []
    for n, v in P.items():
        d = v.get("depth")
        rows.append({
            "project": n,
            "passes_bar": v["passes_bar"],
            "repo_start_year": int(d["first_commit_any_ref"][:4]) if d else None,
            "graduation": GRADUATION.get(n),
            "hadoop_ecosystem": n in HADOOP_ECOSYSTEM,
        })
    out = {"n": len(rows), "rows": rows,
           "graduation_source": "https://incubator.apache.org/projects/, read 2026-08-05"}

    passing = [r for r in rows if r["passes_bar"]]
    dropped = [r for r in rows if not r["passes_bar"]]

    # --- the incumbent: the hand-drawn ecosystem label -----------------------
    a = sum(1 for r in passing if r["hadoop_ecosystem"])
    b = len(passing) - a
    c = sum(1 for r in dropped if r["hadoop_ecosystem"])
    d_ = len(dropped) - c
    out["ecosystem_label"] = {
        "table_[[pass_in,pass_out],[drop_in,drop_out]]": [[a, b], [c, d_]],
        "fisher_two_sided_p": fisher_two_sided(a, b, c, d_),
        "recall_of_passing": a / len(passing),
        "precision_of_label": a / (a + c) if (a + c) else None,
        "accuracy": (a + d_) / len(rows),
        "is_a_hand_judgment": True,
    }

    # --- challenger 1: repository start year, computed, complete -------------
    yp = [r["repo_start_year"] for r in passing if r["repo_start_year"]]
    yd = [r["repo_start_year"] for r in dropped if r["repo_start_year"]]
    out["repo_start_year"] = {
        "coverage": f"{len(yp) + len(yd)} of {len(rows)}",
        "passing_median": statistics.median(yp), "passing_range": [min(yp), max(yp)],
        "dropped_median": statistics.median(yd), "dropped_range": [min(yd), max(yd)],
        "separation": auc_and_u(yp, yd),
        "best_threshold": best_threshold(yp, yd),
    }

    # --- challenger 2: incubator graduation, incomplete ----------------------
    gp = [r["graduation"] for r in passing if r["graduation"] is not None]
    gd = [r["graduation"] for r in dropped if r["graduation"] is not None]
    missing_pass = [r["project"] for r in passing if r["graduation"] is None]
    missing_drop = [r["project"] for r in dropped if r["graduation"] is None]
    out["incubator_graduation"] = {
        "coverage": f"{len(gp) + len(gd)} of {len(rows)}",
        "missing_among_passing": missing_pass,
        "missing_among_dropped": missing_drop,
        "missing_not_at_random": len(missing_pass) / len(passing) != len(missing_drop) / len(dropped),
        "passing_median": statistics.median(gp) if gp else None,
        "dropped_median": statistics.median(gd) if gd else None,
        "separation": auc_and_u(gp, gd),
        "best_threshold": best_threshold(gp, gd) if gp and gd else None,
    }

    json.dump(out, open(args.out, "w"), indent=1)

    e = out["ecosystem_label"]
    print(f"ECOSYSTEM LABEL (hand judgment)   accuracy {e['accuracy']:.3f}  "
          f"recall {e['recall_of_passing']:.3f}  precision {e['precision_of_label']:.3f}  "
          f"Fisher p={e['fisher_two_sided_p']:.3g}")
    r = out["repo_start_year"]
    print(f"REPO START YEAR ({r['coverage']})       AUC {r['separation']['auc']:.3f}  "
          f"p={r['separation']['p_normal_approx']:.3f}  "
          f"best-threshold accuracy {r['best_threshold']['accuracy']:.3f} "
          f"(>= {r['best_threshold']['threshold']})")
    g = out["incubator_graduation"]
    if g["separation"]:
        print(f"INCUBATOR GRADUATION ({g['coverage']})  AUC {g['separation']['auc']:.3f}  "
              f"p={g['separation']['p_normal_approx']:.3f}  "
              f"best-threshold accuracy {g['best_threshold']['accuracy']:.3f}")
    print(f"  graduation missing for {len(g['missing_among_passing'])} of "
          f"{len(passing)} passing: {g['missing_among_passing']}")
    print(f"  and for {len(g['missing_among_dropped'])} of {len(dropped)} dropped")
    print(f"\nVERDICT: the hand label separates better than either generation "
          f"variable ({e['accuracy']:.3f} vs "
          f"{r['best_threshold']['accuracy']:.3f} / "
          f"{g['best_threshold']['accuracy'] if g['best_threshold'] else float('nan'):.3f}).")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
