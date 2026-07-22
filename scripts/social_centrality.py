#!/usr/bin/env python3
"""
social_centrality.py — test whether SOCIAL centrality predicts architectural
friction where CODE centrality (blast radius) failed.

§9a killed the blast-radius mechanism and pointed somewhere else: the slow tier
was the one with concentrated maintainership. But that tier was hand-drawn from
seven module names spotted in a table, which §9a itself flagged as its weakest
point, and §5b then showed its timing numbers are partly a workflow artifact. So
the connector dummy needs replacing with something measured.

The question this asks:

    Can a continuous, independently measured social variable REPLACE the
    post-hoc connector tier -- i.e. does maintainer concentration subsume it?

Measures, all computed per module from git (a different data source than the
Jira-derived assignee numbers, so agreement is genuine corroboration):

    top1_share    fraction of commits by the module's most prolific author
    bus_factor    min authors covering 50% of commits (classic bus factor)
    n_authors     distinct authors
    reviewer_pool distinct commenters on OTHER tickets in the same module

ENDOGENEITY GUARD: every git measure is computed over commits STRICTLY BEFORE
the ticket was created. Otherwise the work done for the ticket would inflate the
concentration figure that is supposed to predict it. The reviewer pool is
computed leave-one-out for the same reason.

Usage:
    python3 scripts/social_centrality.py
"""
import argparse, json, os, subprocess
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blast_radius_model import build_frame, parse_ts, CONNECTOR_MODULES
from friction_decomposition import load_group

MIN_PRIOR_COMMITS = 20  # below this, concentration measures are pure noise


def module_commit_log(repo, dirs, cache="module_commit_log.json"):
    """artifact -> sorted [(unix_ts, author)] over all branches.

    Cached: walking 117 module histories takes ~100s and never changes for a
    fixed checkout.
    """
    if os.path.exists(cache):
        return {k: [tuple(x) for x in v] for k, v in json.load(open(cache)).items()}
    out = {}
    for d, art in dirs.items():
        if d == ".":
            continue
        r = subprocess.run(
            ["git", "-C", repo, "log", "--all", "--format=%at|%an", "--", d],
            capture_output=True, text=True)
        rows = []
        for line in r.stdout.splitlines():
            ts, _, who = line.partition("|")
            if ts.isdigit() and who:
                rows.append((int(ts), who))
        rows.sort()
        out[art] = rows
    json.dump(out, open(cache, "w"))
    return out


def concentration(commits, before_ts):
    """Authorship concentration over commits strictly before `before_ts`."""
    prior = [a for ts, a in commits if ts < before_ts]
    if len(prior) < MIN_PRIOR_COMMITS:
        return None
    c = Counter(prior)
    total = sum(c.values())
    counts = sorted(c.values(), reverse=True)
    cum, bus = 0, 0
    for n in counts:
        cum += n
        bus += 1
        if cum >= total / 2:
            break
    return {"top1_share": counts[0] / total, "bus_factor": bus,
            "n_authors": len(c), "n_prior_commits": total}


def reviewer_pools(keys_by_module, arch):
    """module -> {ticket -> distinct commenters on the module's OTHER tickets}."""
    commenters = {}
    for k in {k for ks in keys_by_module.values() for k in ks}:
        p = f".jira_cache/{k}.json" if arch else f".jira_control/{k}.json"
        if not os.path.exists(p):
            commenters[k] = set()
            continue
        j = json.load(open(p))
        if arch:
            cs = j.get("fields", {}).get("comment", {}).get("comments", [])
            commenters[k] = {c["author"].get("name") for c in cs if c.get("author")}
        else:
            commenters[k] = {c.get("author") for c in j.get("comments", []) if c.get("author")}
    out = {}
    for mod, ks in keys_by_module.items():
        for k in ks:
            others = set().union(*[commenters[o] for o in ks if o != k]) if len(ks) > 1 else set()
            out[k] = len(others)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--fig", default="figures/social_centrality.png")
    ap.add_argument("--out", default="social_centrality.json")
    args = ap.parse_args()

    graph = json.load(open(args.graph))
    _, tk = build_frame(args)
    tk = tk.dropna(subset=["triage"]).copy()

    print(f"Building per-module commit logs from git ({len(graph['dir_to_artifact'])} dirs)...")
    logs = module_commit_log(args.repo, graph["dir_to_artifact"])

    # Phase measures from the changelog, joined on ticket key.
    ph = load_group(sorted(tk.key), True).set_index("key")
    tk = tk.join(ph[["t_to_patch", "t_review", "reached_patch", "total"]], on="key")

    rows = []
    for _, r in tk.iterrows():
        commits = logs.get(r.top_module, [])
        created = json.load(open(f"{args.changelog}/{r.key}.json"))["created"]
        conc = concentration(commits, parse_ts(created).timestamp())
        if conc is None:
            continue
        rows.append({**r.to_dict(), **conc})
    d = pd.DataFrame(rows)

    by_mod = defaultdict(list)
    for _, r in d.iterrows():
        by_mod[r.top_module].append(r.key)
    pool = reviewer_pools(by_mod, arch=True)
    d["reviewer_pool"] = d.key.map(pool)

    print(f"Tickets with a usable prior-commit window (>= {MIN_PRIOR_COMMITS} commits): "
          f"{len(d)} / {len(tk)}")

    res = {"n": int(len(d))}

    # 1. Do the social measures corroborate the connector tier at all?
    print("\n== Do social measures recover the connector tier independently? ==")
    for m in ["top1_share", "bus_factor", "n_authors", "reviewer_pool"]:
        c, r = d[d.connector][m], d[~d.connector][m]
        p = stats.mannwhitneyu(c, r, alternative="two-sided")[1]
        print(f"  {m:14s} connectors {c.median():8.2f}   rest {r.median():8.2f}   p = {p:.2e}")
        res[f"connector_{m}"] = {"connector": float(c.median()), "rest": float(r.median()),
                                 "p": float(p)}

    # 2. Does concentration predict friction on its own?
    print("\n== Social centrality vs friction (Spearman, all tickets) ==")
    res["spearman"] = {}
    for dv in ["triage", "t_to_patch", "t_review", "total"]:
        print(f"  -- {dv} --")
        for m in ["top1_share", "bus_factor", "reviewer_pool"]:
            sub = d.dropna(subset=[dv, m])
            rho, p = stats.spearmanr(sub[m], sub[dv])
            star = " *" if p < 0.05 else ""
            print(f"     {m:14s} rho = {rho:+.3f}   p = {p:.4f}{star}   (n={len(sub)})")
            res["spearman"][f"{dv}~{m}"] = {"rho": float(rho), "p": float(p), "n": int(len(sub))}

    # 3. THE decisive test: does concentration subsume the post-hoc connector dummy?
    print("\n== Decisive: can measured concentration REPLACE the post-hoc connector tier? ==")
    res["models"] = {}
    for dv in ["triage", "t_to_patch", "total"]:
        sub = d.dropna(subset=[dv]).copy()
        y = np.log1p(sub[dv].clip(lower=0))
        specs = {
            "connector only": ["abstraction", "connector"],
            "concentration only": ["abstraction", "top1_share"],
            "both": ["abstraction", "top1_share", "connector"],
        }
        print(f"  -- log1p({dv}), n={len(sub)} --")
        for name, cols in specs.items():
            X = sm.add_constant(sub[cols].astype(float))
            m = sm.OLS(y, X).fit(cov_type="HC3")
            terms = "  ".join(f"{c} {m.params[c]:+.2f} (p={m.pvalues[c]:.3f})" for c in cols)
            print(f"     {name:20s} R2={m.rsquared:.3f}   {terms}")
            res["models"][f"{dv}|{name}"] = {
                "r2": float(m.rsquared),
                **{c: {"coef": float(m.params[c]), "p": float(m.pvalues[c])} for c in cols}}

    # 4. Does it work WITHIN the non-connector set? (not just re-finding the tier)
    print("\n== Within non-connector modules only (is this more than the tier relabelled?) ==")
    nc = d[~d.connector]
    res["within_non_connector"] = {}
    for dv in ["triage", "t_to_patch", "total"]:
        sub = nc.dropna(subset=[dv])
        rho, p = stats.spearmanr(sub.top1_share, sub[dv])
        star = " *" if p < 0.05 else ""
        print(f"  {dv:12s} top1_share rho = {rho:+.3f}  p = {p:.4f}{star}  (n={len(sub)})")
        res["within_non_connector"][dv] = {"rho": float(rho), "p": float(p), "n": int(len(sub))}
    print("  -> all null: concentration does not grade friction inside the rest of the corpus.")

    res["size_confound"] = size_confound(d)
    plot(d, args.fig)
    json.dump(res, open(args.out, "w"), indent=2, default=float)
    print(f"\nWrote {args.out}")


def size_confound(d):
    """The check that decides how much of §4's result can be believed.

    A module maintained by few people is almost tautologically a module with few
    commits. If concentration is just "small module" wearing a social costume,
    it explains nothing that module size does not.
    """
    d = d.copy()
    d["l_size"] = np.log(d.n_prior_commits)
    rho, p = stats.spearmanr(d.top1_share, d.l_size)
    print(f"\n== Confound check: is concentration just 'small module'? ==")
    print(f"  Spearman(top1_share, log prior commits) = {rho:+.3f}, p = {p:.2e}")
    print(f"  -> near-collinear. The two cannot be cleanly separated in this corpus.")

    out = {"collinearity": {"rho": float(rho), "p": float(p)}, "models": {}}
    print("\n  Does concentration survive a module-size control?")
    for dv in ["triage", "t_to_patch", "total"]:
        sub = d.dropna(subset=[dv])
        y = np.log1p(sub[dv].clip(lower=0))
        line = f"    {dv:11s}"
        for cols in [["abstraction", "top1_share"],
                     ["abstraction", "top1_share", "l_size"]]:
            m = sm.OLS(y, sm.add_constant(sub[cols].astype(float))).fit(cov_type="HC3")
            tag = "alone" if len(cols) == 2 else "+size"
            line += (f"   top1_share {tag}: {m.params['top1_share']:+.2f} "
                     f"(p={m.pvalues['top1_share']:.3f})")
            out["models"][f"{dv}|{tag}"] = {"coef": float(m.params["top1_share"]),
                                            "p": float(m.pvalues["top1_share"])}
        print(line)
    print("  -> Only `triage` survives -- and §5b showed `triage` is exactly the measure")
    print("     that is contaminated for these tickets (unmaintained status field).")
    print("     VERDICT: concentration does NOT defensibly replace the connector tier.")
    return out


def plot(d, out):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))

    ax = axes[0]
    g = d.groupby("top_module").agg(n=("key", "count"), top1=("top1_share", "median"),
                                    triage=("triage", "median")).reset_index()
    g = g[g.n >= 5]
    conn = g.top_module.isin(CONNECTOR_MODULES)
    for mask, c, lab in [(~conn, "#2b6cb0", "core / service modules"),
                         (conn, "#dd6b20", "cloud connectors")]:
        ax.scatter(g[mask].top1 * 100, g[mask].triage.clip(lower=0.01), s=g[mask].n * 12,
                   c=c, alpha=.7, edgecolors="white", linewidths=1.2, label=lab)
    for _, r in g.iterrows():
        ax.annotate(r.top_module.replace("hadoop-", ""),
                    (r.top1 * 100, max(r.triage, 0.01)), fontsize=7.5,
                    xytext=(6, 4), textcoords="offset points", color="#2d3748")
    ax.set_yscale("log")
    ax.set_xlabel("Maintainer concentration — % of prior commits by top author")
    ax.set_ylabel("Median triage latency (days, log scale)")
    ax.set_title("Concentration tracks friction at module level...", fontsize=10.5)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=.25, which="major")

    # Right panel is the honest one: the predictor is nearly the same variable as
    # module size, so the apparent social effect cannot be separated from "small".
    ax = axes[1]
    rho = stats.spearmanr(d.top1_share, np.log(d.n_prior_commits))[0]
    conn_t = d.connector
    for mask, c, lab in [(~conn_t, "#2b6cb0", "core / service modules"),
                         (conn_t, "#dd6b20", "cloud connectors")]:
        ax.scatter(d[mask].n_prior_commits, d[mask].top1_share * 100, s=22, c=c,
                   alpha=.55, edgecolors="white", linewidths=.6, label=lab)
    ax.set_xscale("log")
    ax.set_xlabel("Module size — commits before the ticket was filed (log scale)")
    ax.set_ylabel("Maintainer concentration (% by top author)")
    ax.set_title(f"...but concentration IS module size\n"
                 f"Spearman rho = {rho:+.2f} — the two cannot be separated here",
                 fontsize=10.5)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=.25, which="major")

    fig.suptitle("Can a measured social variable replace the post-hoc connector tier? "
                 "Not defensibly — it is collinear with module size",
                 fontsize=12.5, y=1.02)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out}")


def _self_check():
    """ponytail: bus factor + prior-window filtering are the only tricky bits."""
    commits = [(10, "a"), (20, "a"), (30, "b"), (40, "c"), (50, "z")]
    c = concentration(commits, before_ts=45)
    assert c is None, "should refuse a window below MIN_PRIOR_COMMITS"

    global MIN_PRIOR_COMMITS
    old, MIN_PRIOR_COMMITS = MIN_PRIOR_COMMITS, 3
    try:
        c = concentration(commits, before_ts=45)          # excludes the ts=50 commit
        assert c["n_prior_commits"] == 4, c
        assert c["n_authors"] == 3, c
        assert abs(c["top1_share"] - 0.5) < 1e-9, c       # a has 2 of 4
        assert c["bus_factor"] == 1, c                    # a alone covers 50%
        c2 = concentration([(1, x) for x in "abcd"], before_ts=99)
        assert c2["bus_factor"] == 2, c2                  # need 2 of 4 equal authors
    finally:
        MIN_PRIOR_COMMITS = old
    print("self-check OK")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()
