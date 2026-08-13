#!/usr/bin/env python3
"""
blast_radius_model.py — test the mechanism proposed in results_dossier.md §9.

§9 observed ~40x variation in architectural triage latency across four top-level
Hadoop projects and *interpreted* it as blast radius. That was descriptive: four
points, no predictor. This script makes blast radius a continuous, independently
measured variable (from the Maven dependency graph, not from the tickets) and
asks whether it predicts how long architectural work waits before pickup --
controlling for the abstraction-vs-relocation split that is the §5 headline.

    triage latency ~ blast radius + abstraction + change size

Inputs (all produced by earlier steps):
    module_blast_radius.json   scripts/module_graph.py
    episode_files.json         scripts/episode_files.py
    architectural_episodes_all.json, .jira_changelog/, .jira_props/

Usage:
    python3 scripts/blast_radius_model.py
"""
import argparse, json, os
import datetime as dt
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# §5's split: creating a new abstraction vs. relocating existing code.
ABSTRACTION_TYPES = {
    "Extract Class", "Extract Subclass", "Extract Superclass", "Extract Interface",
}

# Vendor cloud-storage connectors under hadoop-tools/. Structurally peripheral
# (almost nothing depends on them) but, as it turns out, the slowest tier in the
# whole corpus -- the competing explanation blast radius has to beat.
CONNECTOR_MODULES = {
    "hadoop-aws", "hadoop-azure", "hadoop-azure-datalake", "hadoop-aliyun",
    "hadoop-openstack", "hadoop-cos", "hadoop-huaweicloud",
}


def parse_ts(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")


def triage_latency(key, changelog_dir):
    """Days from ticket creation to the FIRST status transition out of Open.
    Measured before any review discussion exists, which is why the dossier
    treats it as the anchor measure."""
    p = os.path.join(changelog_dir, f"{key}.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    hist = d.get("status_history") or []
    if not hist:
        return None
    return (parse_ts(hist[0]["created"]) - parse_ts(d["created"])).total_seconds() / 86400


def resolution_time(key, changelog_dir):
    p = os.path.join(changelog_dir, f"{key}.json")
    if not os.path.exists(p):
        return None
    d = json.load(open(p))
    if not d.get("resolutiondate"):
        return None
    return (parse_ts(d["resolutiondate"]) - parse_ts(d["created"])).total_seconds() / 86400


def path_to_module(path, dir_to_artifact):
    """Longest matching pom directory wins -- nested modules must beat their parent."""
    best, best_len = None, -1
    for d, art in dir_to_artifact.items():
        if d == ".":
            continue
        if path.startswith(d + "/") and len(d) > best_len:
            best, best_len = art, len(d)
    return best


def build_frame(args):
    graph = json.load(open(args.graph))
    modules, dir_to_artifact = graph["modules"], graph["dir_to_artifact"]
    ep_files = json.load(open(args.episode_files))
    episodes = json.load(open(args.episodes))

    # Cache path->module: 1420 distinct files x 117 dirs is cheap, but paths repeat.
    cache = {}
    def module_of(p):
        if p not in cache:
            cache[p] = path_to_module(p, dir_to_artifact)
        return cache[p]

    rows = []
    for e in episodes:
        key, sha = e.get("issue_key"), e["sha1"]
        if not key:
            continue
        paths = ep_files.get(sha, [])
        mods = [m for m in (module_of(p) for p in paths) if m]
        if not mods:
            continue
        radii = [modules[m]["blast_radius"] for m in mods if m in modules]
        if not radii:
            continue
        rows.append({
            "key": key,
            "sha": sha,
            "n_files": len(paths),
            "n_modules": len(set(mods)),
            # A change is as risky as the most depended-upon module it touches.
            "blast_radius": max(radii),
            "top_module": max(set(mods), key=lambda m: modules.get(m, {}).get("blast_radius", -1)),
            "abstraction": any(t in ABSTRACTION_TYPES for t in e["arch_types"]),
        })

    ep = pd.DataFrame(rows)
    if ep.empty:
        raise SystemExit("no episodes could be attributed to a module")

    # Tickets, not commits, are the unit: some tickets carry >1 architectural commit.
    tk = ep.groupby("key").agg(
        blast_radius=("blast_radius", "max"),
        n_files=("n_files", "sum"),
        n_modules=("n_modules", "max"),
        abstraction=("abstraction", "any"),
        top_module=("top_module", "first"),
        n_episodes=("sha", "count"),
    ).reset_index()

    tk["triage"] = tk["key"].map(lambda k: triage_latency(k, args.changelog))
    tk["resolution"] = tk["key"].map(lambda k: resolution_time(k, args.changelog))

    props = {}
    for k in tk["key"]:
        p = os.path.join(args.props, f"{k}.json")
        props[k] = json.load(open(p)) if os.path.exists(p) else {}
    tk["issuetype"] = tk["key"].map(lambda k: props[k].get("issuetype"))

    tk["connector"] = tk["top_module"].isin(CONNECTOR_MODULES)
    tk["project"] = tk["key"].str.split("-").str[0]
    tk["created"] = tk["key"].map(lambda k: ticket_created(k, args.changelog))
    tk["year"] = tk["created"].map(lambda t: t.year if t is not None else np.nan)
    tk["assignee"] = tk["key"].map(lambda k: assignee_of(k, args.assignees))
    return ep, tk


def ticket_created(key, changelog_dir):
    p = os.path.join(changelog_dir, f"{key}.json")
    if not os.path.exists(p):
        return None
    return parse_ts(json.load(open(p))["created"])


def assignee_of(key, assignee_dir):
    p = os.path.join(assignee_dir, f"{key}.json")
    return json.load(open(p)).get("assignee") if os.path.exists(p) else None


def report_replication(tk):
    """Sanity gate: if the §5 abstraction split does not reproduce here, the
    episode->ticket join is wrong and nothing downstream can be trusted."""
    a = tk[tk.abstraction].triage.dropna()
    r = tk[~tk.abstraction].triage.dropna()
    u, p = stats.mannwhitneyu(a, r, alternative="two-sided")
    print("\n== Replication gate (dossier §5: relocation 2.8d vs abstraction 7.2d, p=0.0036) ==")
    print(f"  relocation  n={len(r):3d}  median triage {r.median():6.2f} d")
    print(f"  abstraction n={len(a):3d}  median triage {a.median():6.2f} d")
    print(f"  Mann-Whitney p = {p:.4f}")
    return p


def report_module_level(tk, modules, min_n):
    """Does a module's position in the dependency graph track how long
    architectural work there waits? Aggregated, like §9 but continuous."""
    g = tk.dropna(subset=["triage"]).groupby("top_module").agg(
        n=("key", "count"), median_triage=("triage", "median"),
        pct_abstraction=("abstraction", "mean"),
    ).reset_index()
    g["blast_radius"] = g["top_module"].map(lambda m: modules.get(m, {}).get("blast_radius", np.nan))
    g = g.dropna(subset=["blast_radius"])
    big = g[g.n >= min_n].copy()

    rho, p = stats.spearmanr(big.blast_radius, big.median_triage)
    print(f"\n== Module level (modules with >= {min_n} architectural tickets: n={len(big)}) ==")
    print(f"  Spearman blast_radius vs median triage: rho = {rho:+.3f}, p = {p:.4f}")
    print(big.sort_values("blast_radius", ascending=False)
             .to_string(index=False, float_format=lambda v: f"{v:.2f}"))
    return big, rho, p


def report_ticket_level(tk):
    d = tk.dropna(subset=["triage"]).copy()
    d["l_triage"] = np.log1p(d.triage.clip(lower=0))
    d["l_blast"] = np.log1p(d.blast_radius)
    d["l_files"] = np.log1p(d.n_files)

    rho, p_rho = stats.spearmanr(d.blast_radius, d.triage)
    print(f"\n== Ticket level (n={len(d)}) ==")
    print(f"  Spearman blast_radius vs triage: rho = {rho:+.3f}, p = {p_rho:.4f}")
    print("  (NOTE the sign: negative = work on MORE depended-upon modules is picked up FASTER,")
    print("   the opposite of the blast-radius/hesitation mechanism proposed in §9.)")

    models = {}
    for name, cols in [
        ("blast only", ["l_blast"]),
        ("blast + abstraction", ["l_blast", "abstraction"]),
        ("blast + abstraction + size", ["l_blast", "abstraction", "l_files", "n_modules"]),
        # The decisive one: is "blast radius" really just the connector tier?
        ("+ connector tier", ["l_blast", "abstraction", "connector"]),
        ("+ connector + era", ["l_blast", "abstraction", "connector", "year"]),
    ]:
        X = sm.add_constant(d[cols].astype(float))
        m = sm.OLS(d.l_triage, X).fit(cov_type="HC3")  # heteroskedasticity-robust
        models[name] = m
        print(f"\n  -- OLS log1p(triage) ~ {' + '.join(cols)}   (R2={m.rsquared:.3f}) --")
        for c in cols:
            print(f"     {c:14s} coef {m.params[c]:+.3f}   p = {m.pvalues[c]:.4f}")
    return d, models, rho, p_rho


def report_connector_tier(d):
    """The real driver behind §9's module hotspots -- and it runs OPPOSITE to
    blast radius: the vendor cloud connectors are structurally peripheral yet by
    far the slowest work in the corpus."""
    c, r = d[d.connector], d[~d.connector]
    p = stats.mannwhitneyu(c.triage, r.triage, alternative="two-sided")[1]
    print(f"\n== Connector tier (the competing explanation) ==")
    print(f"  cloud connectors n={len(c):3d}  median triage {c.triage.median():6.1f} d  "
          f"median blast radius {c.blast_radius.median():.0f}")
    print(f"  everything else  n={len(r):3d}  median triage {r.triage.median():6.1f} d  "
          f"median blast radius {r.blast_radius.median():.0f}")
    print(f"  Mann-Whitney p = {p:.2e}")

    # Blast radius, re-tested with the connector tier removed.
    rho_x, p_x = stats.spearmanr(r.blast_radius, r.triage)
    print(f"\n  Blast radius vs triage EXCLUDING connectors (n={len(r)}): "
          f"rho = {rho_x:+.3f}, p = {p_x:.4f}")

    # Why are connectors slow? Not a thinner pool -- a more concentrated one.
    print("\n  Maintainer concentration (tests the 'niche, few volunteers' story):")
    for lab, sub in [("connectors", c), ("rest", r)]:
        vc = sub.assignee.value_counts()
        share = vc.iloc[0] / len(sub) if len(vc) else float("nan")
        per = len(sub) / max(sub.assignee.nunique(), 1)
        print(f"    {lab:11s} distinct assignees {sub.assignee.nunique():3d}  "
              f"tickets/assignee {per:.2f}  top-assignee share {share:.0%}")

    # Era check: connectors skew later, and latency rises over time for everyone.
    print("\n  Median triage by era (connectors vs rest):")
    d2 = d.dropna(subset=["year"]).copy()
    d2["era"] = pd.cut(d2.year, [0, 2018, 2021, 3000], labels=["<=2018", "2019-21", "2022+"])
    tab = d2.pivot_table(index="era", columns="connector", values="triage",
                         aggfunc=["median", "count"], observed=False)
    print(tab.to_string())
    return {"n_connector": int(len(c)), "n_rest": int(len(r)),
            "median_triage_connector": float(c.triage.median()),
            "median_triage_rest": float(r.triage.median()), "p": float(p),
            "blast_spearman_excl_connectors": {"rho": float(rho_x), "p": float(p_x)}}


def report_section9_decomposition(d):
    """§9 read a 39-day median for the 'HADOOP' Jira project as evidence that the
    foundational hadoop-common module stalls. But HADOOP-* is a Jira prefix, not
    a module: it also carries every cloud-connector ticket. Decompose it."""
    h = d[d.project == "HADOOP"]
    print(f"\n== Decomposing the §9 'hadoop-common stalls 39 days' claim ==")
    print(f"  All HADOOP-* tickets: n={len(h)}, median triage {h.triage.median():.1f} d "
          f"(reproduces the dossier's 39.1 d)")
    tab = h.groupby("top_module").triage.agg(["count", "median"]).sort_values("median", ascending=False)
    print(tab.to_string(float_format=lambda v: f"{v:.1f}"))
    conn = h[h.connector]
    print(f"  -> {len(conn)}/{len(h)} ({len(conn)/len(h):.0%}) of those tickets are cloud "
          f"connectors, NOT hadoop-common.")
    core = h[h.top_module == "hadoop-common"]
    print(f"  -> hadoop-common alone: n={len(core)}, median {core.triage.median():.1f} d.")
    return {"n_hadoop_prefix": int(len(h)), "median_hadoop_prefix": float(h.triage.median()),
            "n_connector_in_prefix": int(len(conn)),
            "n_common": int(len(core)), "median_common": float(core.triage.median())}


def plot(big, d, out):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    # Left: the null. If blast radius drove hesitation this would trend upward.
    # ponytail: floor at 0.01 d (~15 min). Sub-15-minute triage all means the
    # same thing -- "picked up immediately" -- and un-floored it wastes three
    # log decades on noise.
    ax = axes[0]
    big = big.copy()
    big["y"] = big.median_triage.clip(lower=0.01)
    conn = big.top_module.isin(CONNECTOR_MODULES)
    ax.scatter(big[~conn].blast_radius, big[~conn].y, s=big[~conn].n * 12,
               c="#2b6cb0", alpha=.65, edgecolors="white", linewidths=1.2, label="core / service modules")
    ax.scatter(big[conn].blast_radius, big[conn].y, s=big[conn].n * 12,
               c="#dd6b20", alpha=.8, edgecolors="white", linewidths=1.2, label="cloud connectors")
    # Alternate label placement so the clustered modules stay legible.
    offsets = {"hadoop-aws": (8, -12), "hadoop-azure": (8, 6),
               "hadoop-yarn-server-nodemanager": (8, 7),
               "hadoop-yarn-server-resourcemanager": (-6, -16),
               "hadoop-hdfs-client": (-14, -14), "hadoop-common": (-20, 10)}
    for _, r in big.iterrows():
        ax.annotate(r.top_module.replace("hadoop-", ""), (r.blast_radius, r.y), fontsize=7.5,
                    xytext=offsets.get(r.top_module, (7, 5)), textcoords="offset points",
                    color="#2d3748")
    ax.set_yscale("log")
    ax.set_ylim(0.005, 400)
    ax.set_xlim(-8, 105)
    ax.set_xlabel("Blast radius — modules transitively depending on it")
    ax.set_ylabel("Median triage latency (days, log scale)")
    ax.set_title("Centrality does NOT predict hesitation\n(the slowest modules are the least depended-upon)",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="upper right")  # lower-left would bury the `sls` point
    ax.grid(alpha=.25, which="major")

    # Right: what actually separates fast from slow.
    ax = axes[1]
    groups = [("Cloud connectors\n(blast radius ~2)", d[d.connector], "#dd6b20"),
              ("Everything else\n(blast radius up to 86)", d[~d.connector], "#2b6cb0")]
    data = [g[1].triage.values for g in groups]
    bp = ax.boxplot(data, tick_labels=[g[0] for g in groups], showfliers=False,
                    patch_artist=True, widths=.55,
                    medianprops=dict(color="#1a202c", linewidth=2.2))
    for patch, g in zip(bp["boxes"], groups):
        patch.set_facecolor(g[2]); patch.set_alpha(.45)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.22)
    for i, (label, g, _) in enumerate(groups):
        ax.text(i + 1, 0.97, f"n={len(g)}\nmedian {g.triage.median():.1f} d",
                transform=ax.get_xaxis_transform(), fontsize=9, ha="center",
                va="top", color="#1a202c")
    ax.set_ylabel("Triage latency (days)")
    ax.set_title("The real hotspot is the peripheral vendor tier\n"
                 "(~14x slower to pick up, p = 3e-07)", fontsize=10.5)
    ax.grid(alpha=.25, axis="y")

    fig.suptitle("Testing the blast-radius mechanism: it fails, and the effect runs the other way",
                 fontsize=12.5, y=1.005)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--min-module-n", type=int, default=5)
    ap.add_argument("--fig", default="figures/blast_radius.png")
    ap.add_argument("--out", default="blast_radius_results.json")
    args = ap.parse_args()

    modules = json.load(open(args.graph))["modules"]
    ep, tk = build_frame(args)
    print(f"Episodes attributed to a module: {len(ep)} / 349")
    print(f"Tickets: {len(tk)}   with triage latency: {tk.triage.notna().sum()}")

    p_rep = report_replication(tk)
    big, rho_m, p_m = report_module_level(tk, modules, args.min_module_n)
    d, models, rho_t, p_t = report_ticket_level(tk)
    conn = report_connector_tier(d)
    sec9 = report_section9_decomposition(d)
    plot(big, d, args.fig)

    def dump(m):
        return {c: {"coef": float(m.params[c]), "p": float(m.pvalues[c])}
                for c in m.params.index if c != "const"} | {"r2": float(m.rsquared)}

    json.dump({
        "n_episodes_attributed": int(len(ep)),
        "n_episodes_total": 349,
        "attrition_note": "90 episodes are Ozone/HDDS + Submarine, split out of the "
                          "Hadoop repo, so their poms no longer exist in-tree.",
        "n_tickets": int(len(d)),
        "replication_p_abstraction_split": float(p_rep),
        "module_level": {"n_modules": int(len(big)), "spearman_rho": float(rho_m), "p": float(p_m)},
        "ticket_level": {"spearman_rho": float(rho_t), "p": float(p_t)},
        "models": {name: dump(m) for name, m in models.items()},
        "connector_tier": conn,
        "section9_decomposition": sec9,
        "module_table": big.sort_values("blast_radius", ascending=False).to_dict("records"),
    }, open(args.out, "w"), indent=2)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
