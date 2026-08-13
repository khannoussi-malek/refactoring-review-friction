#!/usr/bin/env python3
"""
advisor_followup.py — steps 3-6 and 8 of the advisor's list, in one pass.

3. CROSS-TAB abstraction x tier. Four cells. If abstraction work sits almost
   entirely inside (or outside) the slow connector tier, Hadoop cannot separate
   the two explanations at all and the §5 headline is unanswerable here.
4. FIX THE SPLIT. "any abstraction type" is a generous rule: a ticket with 40
   Move Class and one Extract Class is coded abstraction. Re-run on (a) PURE
   tickets only -- all-abstraction vs all-relocation, mixed dropped -- and
   (b) abstraction as a continuous SHARE of the ticket's refactorings.
5. BUILD vs MERGE under the same adjustment. §5a's phase result (architectural
   work is ~4x slower to produce a patch, merged just as fast) is the only
   headline that was never adjusted -- it is Mann-Whitney medians. If it holds
   at n covariates it becomes the headline, because active build time cannot be
   volunteer queueing.
6. CLUSTERED SEs. Note up front: every model here is already ONE ROW PER TICKET
   (episodes were aggregated in blast_radius_model.build_frame), so clustering
   on ticket is arithmetically a no-op. The dependence that actually remains is
   tickets sharing a module or an assignee, so those are what get clustered.
8. POWER. How many architectural episodes does a multi-project corpus need to
   detect the fully-adjusted effect at 80%?

Usage:  python3 scripts/advisor_followup.py
"""
import argparse, json, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

from blast_radius_model import ABSTRACTION_TYPES, build_frame
from temporal_trend import assemble
from ci_rework import load_ci
from full_adjustment import experience, row

# Everything else RefactoringMiner emits at package/class-move level.
RELOCATION_TYPES = {
    "Move Class", "Move And Rename Class", "Rename Class",
    "Move Package", "Rename Package", "Merge Package", "Split Package",
}
COVARS = ["l_files", "l_churn", "l_human", "l_exp", "conn", "year"]
Z80 = stats.norm.ppf(0.975) + stats.norm.ppf(0.80)   # 2.802


def episode_type_mix(episodes_path):
    """key -> (n abstraction instances, n relocation instances)."""
    mix = {}
    for e in json.load(open(episodes_path)):
        k = e.get("issue_key")
        if not k:
            continue
        a, r = mix.get(k, (0, 0))
        for t in e["arch_types"]:
            if t in ABSTRACTION_TYPES:
                a += 1
            elif t in RELOCATION_TYPES:
                r += 1
        mix[k] = (a, r)
    return mix


def build(args):
    d = assemble(args)
    _, tk = build_frame(args)
    mod = dict(zip(tk.key, tk.top_module))
    size = json.load(open("ticket_change_size.json"))
    exp = experience(d.key)
    mix = episode_type_mix(args.episodes)

    d["top_module"] = d.key.map(lambda k: mod.get(k, "«unattributed»"))
    d["n_files"] = d.key.map(lambda k: size.get(k, [np.nan, np.nan])[0])
    d["churn"] = d.key.map(lambda k: size.get(k, [np.nan, np.nan])[1])
    d["n_human"] = [(load_ci(r.key, bool(r.arch)) or {}).get("n_human_comments", np.nan)
                    for r in d.itertuples()]
    d["exp"] = d.key.map(exp)

    n_a = d.key.map(lambda k: mix.get(k, (0, 0))[0])
    n_r = d.key.map(lambda k: mix.get(k, (0, 0))[1])
    tot = (n_a + n_r).replace(0, np.nan)
    d["abst_share"] = (n_a / tot).where(d.arch == 1)
    d["pure"] = np.where(d.arch == 0, "",
                         np.where(n_a > 0, np.where(n_r > 0, "mixed", "abstraction"),
                                  np.where(n_r > 0, "relocation", "")))
    d["abst"] = d.abstraction.astype(float)
    d["conn"] = d.connector.astype(float)
    for src, dst in [("n_files", "l_files"), ("churn", "l_churn"),
                     ("n_human", "l_human"), ("exp", "l_exp")]:
        d[dst] = np.log1p(d[src])
    return d


def model(d, dv, focus, extra=COVARS, groups=None):
    """OLS on log1p(dv). HC3 unless a cluster grouping is given."""
    cols = [focus] + list(extra)
    s = d.dropna(subset=cols + [dv]).copy()
    s["y"] = np.log1p(s[dv].clip(lower=0))
    X = sm.add_constant(s[cols].astype(float))
    if groups is None:
        m = sm.OLS(s.y, X).fit(cov_type="HC3")
    else:
        m = sm.OLS(s.y, X).fit(cov_type="cluster",
                               cov_kwds={"groups": s[groups], "use_correction": True})
    return m, s


def line(label, m, s, focus):
    b, lo, hi, p, xb, xlo, xhi = row(m, focus)
    star = " *" if p < 0.05 else ""
    print(f"  {label:36s} n={len(s):3d}  {b:+.3f} [{lo:+.3f}, {hi:+.3f}]  "
          f"p={p:.4f}{star}   x{xb:.2f} [{xlo:.2f}, {xhi:.2f}]")
    return {"n": int(len(s)), "coef": float(b), "ci": [float(lo), float(hi)],
            "p": float(p), "mult": float(xb), "se": float(m.bse[focus])}


def step3(d):
    print("\n=== 3. Cross-tab: abstraction x connector tier (architectural only) ===")
    a = d[(d.arch == 1)].dropna(subset=["triage"])
    tab = a.pivot_table(index="abstraction", columns="connector", values="triage",
                        aggfunc=["count", "median"])
    print(tab.to_string())
    ct = pd.crosstab(a.abstraction, a.connector)
    odds, p = stats.fisher_exact(ct.values) if ct.shape == (2, 2) else (np.nan, np.nan)
    share_in = a[a.connector].abstraction.mean()
    share_out = a[~a.connector].abstraction.mean()
    print(f"\n  abstraction share INSIDE connectors  {share_in:.0%}  (n={a.connector.sum()})")
    print(f"  abstraction share OUTSIDE connectors {share_out:.0%}  (n={(~a.connector).sum()})")
    print(f"  Fisher exact on the 2x2: OR={odds:.2f}, p={p:.3f}")
    print("  -> If these shares are similar, the two factors are separable in Hadoop and")
    print("     the joint model is identified; if one cell is near-empty, it is not.")
    return {"counts": ct.to_dict(), "abst_share_connector": float(share_in),
            "abst_share_rest": float(share_out), "fisher_or": float(odds), "fisher_p": float(p)}


def step4(d):
    print("\n=== 4. The split, done two stricter ways (outcome: triage latency) ===")
    a = d[d.arch == 1].copy()
    n_mix = (a.pure == "mixed").sum()
    print(f"  tickets: abstraction-only {(a.pure=='abstraction').sum()}, "
          f"relocation-only {(a.pure=='relocation').sum()}, mixed {n_mix} "
          f"({n_mix/len(a):.0%} — these were coded 'abstraction' by the any-rule)")
    out = {}
    pure = a[a.pure.isin(["abstraction", "relocation"])].copy()
    pure["abst"] = (pure.pure == "abstraction").astype(float)
    print(f"\n  (a) PURE tickets only, mixed dropped:")
    print(f"      raw medians — abstraction {pure[pure.abst==1].triage.median():.1f} d  "
          f"vs relocation {pure[pure.abst==0].triage.median():.1f} d")
    m, s = model(pure, "triage", "abst", extra=[])
    out["pure_unadjusted"] = line("pure, unadjusted", m, s, "abst")
    m, s = model(pure, "triage", "abst")
    out["pure_adjusted"] = line("pure, FULLY ADJUSTED", m, s, "abst")

    print(f"\n  (b) abstraction as a continuous share (0=all relocation, 1=all abstraction):")
    m, s = model(a, "triage", "abst_share", extra=[])
    out["share_unadjusted"] = line("share, unadjusted", m, s, "abst_share")
    m, s = model(a, "triage", "abst_share")
    out["share_adjusted"] = line("share, FULLY ADJUSTED", m, s, "abst_share")
    print("  (the share coefficient is the 0->100% abstraction contrast, so it is")
    print("   directly comparable to the binary one above)")
    return out


#  A phase measure only means something on the tickets that actually drove that
#  phase: t_review is 0 for a ticket that never reached Patch Available, and
#  t_active is 0 for the ~75% that never log In Progress (§5b). Pooling those
#  zeros in is what made the first run report a median active time of 0.00.
PHASE_SUBSET = {"t_to_patch": "reached_patch", "t_review": "reached_patch",
                "t_active": "used_in_progress", "total": None}


def step5(d):
    print("\n=== 5. Build vs merge, adjusted (the unadjusted §5a result) ===")
    print("  Each phase is restricted to the tickets that drive it (§5b).")
    out = {}
    for grp_lab, frame, focus in [("A: architectural vs ordinary", d, "arch"),
                                  ("B: abstraction vs relocation (architectural only)",
                                   d[d.arch == 1], "abst")]:
        print(f"\n  {grp_lab}")
        for dv, lab in [("t_to_patch", "days to first patch (BUILD)"),
                        ("t_review", "days in review (MERGE)"),
                        ("t_active", "active coding (In Progress)"),
                        ("total", "total lifetime")]:
            gate = PHASE_SUBSET[dv]
            f = frame[frame[gate]] if gate else frame
            sub = f.dropna(subset=[dv])
            hi = sub[sub[focus] == 1][dv].median()
            lo = sub[sub[focus] == 0][dv].median()
            # The tier dummy is 0 by construction for every control ticket, so in
            # panel A it is an "architectural AND connector" indicator, not a real
            # covariate -- it absorbs the slowest architectural tickets and makes
            # the group effect conservative. Both specs are shown.
            for tier, tlab in ([(True, "+tier"), (False, "-tier")] if focus == "arch"
                               else [(True, "")]):
                cov = COVARS if tier else [c for c in COVARS if c != "conn"]
                m, s = model(f, dv, focus, extra=cov)
                out[f"{focus}_{dv}{'' if tier else '_no_tier'}"] = line(
                    f"{lab:30s} med {hi:6.2f}/{lo:5.2f} {tlab:5s}", m, s, focus)
    return out


def step6(d):
    print("\n=== 6. Clustered standard errors ===")
    print("  NOTE: the analysis frame is already one row per TICKET (349 episodes were")
    print("  aggregated to 323 tickets upstream), so clustering on ticket is a no-op.")
    print("  Clustering on what is actually shared instead:")
    a = d[d.arch == 1]
    out = {}
    for grp, lab in [(None, "HC3 (as reported)"),
                     ("top_module", "cluster by module"),
                     ("assignee", "cluster by assignee")]:
        sub = a.dropna(subset=[grp]) if grp else a
        m, s = model(sub, "triage", "abst", groups=grp)
        n_g = s[grp].nunique() if grp else np.nan
        out[lab] = line(f"{lab} (groups={n_g if grp else '-'})", m, s, "abst")
    print("  Module clusters are few (~11 attributed + unattributed), so that SE is itself")
    print("  unreliable — cluster-robust inference wants 40+ groups. Reported, not relied on.")
    return out


def step8(res_step4, n_episodes=349, n_tickets=323, n_commits=8919):
    """Two questions, and the second one is the one that matters.

    (i) How many INDEPENDENT tickets to detect the adjusted effect at 80%?
    (ii) How many PROJECTS? Tickets within a project are not independent. With P
         projects of m tickets each and intra-project correlation ICC,
         n_eff = P*m / (1 + (m-1)*ICC), which as m -> infinity approaches P/ICC.
         So P projects impose a HARD CEILING of P/ICC effective observations --
         no amount of extra mining inside those projects can pass it. Required
         per-project size: m = n_ind(1-ICC) / (P - n_ind*ICC), infeasible when
         P <= n_ind*ICC.
    """
    print("\n=== 8. Power ===")
    ref = res_step4["pure_adjusted"]
    print(f"  Anchor: fully adjusted PURE-split effect, coef {ref['coef']:+.3f} "
          f"(x{ref['mult']:.2f}), SE {ref['se']:.3f} at n={ref['n']} tickets.")
    print(f"  Hadoop yield: {n_episodes} episodes / {n_commits} commits = 1 per "
          f"{n_commits/n_episodes:.0f} commits; {n_tickets/n_episodes:.2f} tickets per episode.")

    print(f"\n  (i) Independent tickets required at 80% power:")
    targets = [("observed adjusted (x1.50)", abs(ref["coef"])), ("x1.4", np.log(1.4)),
               ("x1.3", np.log(1.3)), ("x1.2", np.log(1.2))]
    need = {}
    for lab, beta in targets:
        n_ind = ref["n"] * (ref["se"] * Z80 / beta) ** 2
        need[lab] = n_ind
        commits = n_ind / (n_tickets / n_episodes) * (n_commits / n_episodes)
        print(f"    {lab:26s} n = {n_ind:6.0f} tickets   (~{commits:,.0f} commits to mine "
              f"at Hadoop's yield)")

    print(f"\n  (ii) Projects, not tickets, are the binding constraint.")
    print(f"       Effective-n ceiling with P projects = P/ICC, whatever the corpus size.")
    out = {"independent": {k: float(v) for k, v in need.items()}, "by_projects": {}}
    for icc in [0.02, 0.05]:
        print(f"\n       ICC = {icc}:  {'P':>4s} {'ceiling n_eff':>14s}   "
              f"tickets/project needed for the observed effect")
        n_ind = need["observed adjusted (x1.50)"]
        for P in [3, 5, 10, 20, 40]:
            ceiling = P / icc
            if P <= n_ind * icc:
                msg = f"IMPOSSIBLE (need P > {n_ind*icc:.0f})"
                m = None
            else:
                m = n_ind * (1 - icc) / (P - n_ind * icc)
                msg = f"{m:,.0f} tickets each  (~{m*(n_commits/n_tickets):,.0f} commits each)"
            print(f"       {'':13s}{P:>4d} {ceiling:>14.0f}   {msg}")
            out["by_projects"][f"icc{icc}_P{P}"] = {"ceiling": float(ceiling),
                                                    "tickets_per_project": m}
    print("\n  -> Kafka + HBase + Camel (P=3) cannot reach it at any corpus size. The registered")
    print("     report needs breadth: ~10-20 projects, each contributing a modest number of")
    print("     episodes, not three deeply-mined ones. This is the same conclusion §9b reached")
    print("     from the module side (size and concentration are one variable in one project).")
    return out


def _self_check():
    """The split rule is the whole result; assert the two type sets are disjoint
    and jointly cover what RefactoringMiner actually emitted."""
    assert not (ABSTRACTION_TYPES & RELOCATION_TYPES), "type sets overlap"
    seen = {t for e in json.load(open("architectural_episodes_all.json")) for t in e["arch_types"]}
    missed = seen - ABSTRACTION_TYPES - RELOCATION_TYPES
    assert not missed, f"architectural types classified as neither side: {missed}"
    print(f"self-check ok: {len(seen)} architectural types, all classified, sets disjoint")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--out", default="advisor_followup.json")
    args = ap.parse_args()

    _self_check()
    d = build(args)
    res = {}
    res["crosstab"] = step3(d)
    res["split"] = step4(d)
    res["phases"] = step5(d)
    res["clustered"] = step6(d)
    res["power"] = step8(res["split"])
    json.dump(res, open(args.out, "w"), indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
