#!/usr/bin/env python3
"""
full_adjustment.py — two questions the advisor asked that the study had not answered.

Q3. "Survives size, volume, experience, tier and era controls" was, until now,
    FIVE SEPARATE NESTED MODELS in three scripts (blast_radius_model.py,
    ci_rework.py, friction_decomposition.py), each adding one or two covariates
    to a different base. No script ever put all five in one equation, and none
    printed a confidence interval. This does both: the single fully-adjusted
    model for the §5 headline (abstraction vs relocation on triage latency),
    with HC3 95% CIs, back-transformed to a multiplicative effect on days, plus
    VIF so the collinearity cost of six covariates on ~240 tickets is visible.

Q4. The decade divergence (§5c) was checked at truncation windows 2016+/2018+/
    2019+ -- all of which still contain pre-migration data. The strongest test
    is the POST-migration era alone, on the workflow-independent git clock.
    Windows 2020+ and 2021+ are added here.

Usage:  python3 scripts/full_adjustment.py
"""
import argparse, json, os
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from blast_radius_model import ABSTRACTION_TYPES
from temporal_trend import assemble
from ci_rework import load_ci


def fit(d, cols, dv="y"):
    X = sm.add_constant(d[cols].astype(float))
    return sm.OLS(d[dv], X).fit(cov_type="HC3")


def row(m, c):
    """coef, 95% CI and p for one term, plus the multiplicative reading."""
    lo, hi = m.conf_int().loc[c]
    return (m.params[c], lo, hi, m.pvalues[c],
            np.exp(m.params[c]), np.exp(lo), np.exp(hi))


def show(name, m, focus, n):
    b, lo, hi, p, xb, xlo, xhi = row(m, focus)
    star = " *" if p < 0.05 else ""
    print(f"  {name:34s} n={n:3d}  {focus} {b:+.3f} "
          f"[{lo:+.3f}, {hi:+.3f}]  p={p:.4f}{star}   "
          f"x{xb:.2f} [{xlo:.2f}, {xhi:.2f}] on days")


def experience(keys, assignee_dir=".jira_assignee"):
    """Dossier's experience measure: how many of OUR tickets this assignee handled."""
    who = {}
    for k in keys:
        p = os.path.join(assignee_dir, f"{k}.json")
        who[k] = json.load(open(p)).get("assignee") if os.path.exists(p) else None
    load = pd.Series(list(who.values())).value_counts()
    return {k: (load.get(a, 0) if a else np.nan) for k, a in who.items()}


def q3(d):
    """The §5 headline under one joint model instead of five nested ones."""
    a = d[(d.arch == 1)].dropna(subset=["triage"]).copy()

    size = json.load(open("ticket_change_size.json"))
    exp = experience(a.key)

    a["n_files"] = a.key.map(lambda k: size.get(k, [np.nan, np.nan])[0])
    a["churn"] = a.key.map(lambda k: size.get(k, [np.nan, np.nan])[1])
    # load_ci, not review_signal_all.json: the latter covers architectural
    # tickets only, and every model here must use one comment-count definition
    # so the numbers compose across scripts.
    a["n_human"] = [(load_ci(k, True) or {}).get("n_human_comments", np.nan) for k in a.key]
    a["exp"] = a.key.map(exp)

    a["y"] = np.log1p(a.triage.clip(lower=0))
    a["abst"] = a.abstraction.astype(float)
    a["conn"] = a.connector.astype(float)
    for src, dst in [("n_files", "l_files"), ("churn", "l_churn"),
                     ("n_human", "l_human"), ("exp", "l_exp")]:
        a[dst] = np.log1p(a[src])

    full = ["abst", "l_files", "l_churn", "l_human", "l_exp", "conn", "year"]
    c = a.dropna(subset=full + ["y"]).copy()

    print("== Q3: abstraction vs relocation on triage latency ==")
    print(f"   architectural tickets with triage: {len(a)};  complete on all "
          f"covariates: {len(c)}  (loss: {len(a) - len(c)})")
    print(f"   raw medians — abstraction {a[a.abst == 1].triage.median():.1f} d  "
          f"vs relocation {a[a.abst == 0].triage.median():.1f} d")
    print("\n   Nested (the way it was reported), then the joint model:")

    steps = [
        ("unadjusted", ["abst"]),
        ("+ size", ["abst", "l_files", "l_churn"]),
        ("+ discussion volume", ["abst", "l_files", "l_churn", "l_human"]),
        ("+ experience", ["abst", "l_files", "l_churn", "l_human", "l_exp"]),
        ("+ tier", ["abst", "l_files", "l_churn", "l_human", "l_exp", "conn"]),
        ("+ era  = FULLY ADJUSTED", full),
    ]
    out = {}
    for name, cols in steps:
        m = fit(c, cols)
        show(name, m, "abst", len(c))
        b, lo, hi, p, xb, xlo, xhi = row(m, "abst")
        out[name] = {"coef": float(b), "ci": [float(lo), float(hi)], "p": float(p),
                     "mult": float(xb), "mult_ci": [float(xlo), float(xhi)], "n": int(len(c))}

    m = fit(c, full)
    X = sm.add_constant(c[full].astype(float))
    vif = {full[i]: float(variance_inflation_factor(X.values, i + 1)) for i in range(len(full))}
    print("\n   VIF (fully adjusted): " + "  ".join(f"{k}={v:.1f}" for k, v in vif.items()))
    print("   All covariates in the fully adjusted model:")
    for cc in full:
        b, lo, hi, p, *_ = row(m, cc)
        print(f"     {cc:9s} {b:+.3f} [{lo:+.3f}, {hi:+.3f}]  p={p:.4f}")
    out["vif"] = vif
    out["r2_full"] = float(m.rsquared)
    return out


def q4(d):
    """§5c's divergence using post-migration data only, on the git clock."""
    print("\n== Q4: decade divergence, post-migration windows (outcome: "
          "log1p(days from ticket creation to first citing commit)) ==")
    out = {}
    for lo in [2016, 2018, 2019, 2020, 2021]:
        s = d[d.year >= lo].dropna(subset=["t_to_commit"]).copy()
        s["y"] = np.log1p(s.t_to_commit.clip(lower=0))
        s["yr"] = s.year - s.year.min()
        s["arch_x_yr"] = s.arch * s.yr
        cols = ["arch", "yr", "arch_x_yr", "abstraction", "connector"]
        s[["abstraction", "connector"]] = s[["abstraction", "connector"]].astype(float)
        m = fit(s, cols)
        b, l, h, p, *_ = row(m, "arch_x_yr")
        n_ord = int((s.arch == 0).sum())
        star = " *" if p < 0.05 else ""
        print(f"  {lo}+ : n={len(s):3d} (ordinary controls {n_ord:3d})  "
              f"interaction {b:+.3f} [{l:+.3f}, {h:+.3f}]  p={p:.4f}{star}")
        out[str(lo)] = {"n": int(len(s)), "n_ordinary": n_ord, "coef": float(b),
                        "ci": [float(l), float(h)], "p": float(p)}
    print("  (The control arm is what runs out: see n_ordinary.)")
    return out


def _self_check():
    """The one thing that silently breaks: covariates joined onto the wrong keys."""
    size = json.load(open("ticket_change_size.json"))
    eps = json.load(open("architectural_episodes_all.json"))
    keys = {e["issue_key"] for e in eps if e["issue_key"]}
    hit_size = len(keys & set(size)) / len(keys)
    hit_com = sum(load_ci(k, True) is not None for k in keys) / len(keys)
    assert hit_size > 0.9, f"change-size join covers only {hit_size:.0%} of arch tickets"
    assert hit_com > 0.9, f"comment-volume join covers only {hit_com:.0%} of arch tickets"
    assert ABSTRACTION_TYPES, "abstraction type set is empty"
    print(f"self-check ok: size join {hit_size:.0%}, comment join {hit_com:.0%} "
          f"of {len(keys)} architectural tickets")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--out", default="full_adjustment.json")
    args = ap.parse_args()

    _self_check()
    d = assemble(args)
    res = {"q3_joint_model": q3(d), "q4_post_migration": q4(d)}
    json.dump(res, open(args.out, "w"), indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
