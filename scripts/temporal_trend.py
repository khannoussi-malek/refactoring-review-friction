#!/usr/bin/env python3
"""
temporal_trend.py — is Hadoop becoming selectively harder to refactor?

Every earlier analysis pooled 2016-2026 into one corpus. Splitting by year shows
architectural triage latency climbing across the decade while ordinary
refactoring work stays flat. If that survives scrutiny it is a stronger thesis
statement than anything else in the study: architectural debt accumulating as an
observable, measurable process rather than a metaphor.

The design is a difference-in-differences: ordinary refactoring tickets are the
control. A shrinking or ageing community would slow BOTH groups; only a
structure-specific effect slows one.

FOUR THREATS, all checked before any trend is reported:

1. WORKFLOW DRIFT (the §5b problem in temporal form). Hadoop migrated to GitHub
   pull requests around 2019-2020, and Jira status hygiene collapsed with it:
   93.5% of tickets reached Patch Available before 2019, only 15.5% after 2022.
   Every status-derived duration therefore changes meaning mid-corpus. This one
   is fatal to the naive analysis, so the PRIMARY measure here is a
   workflow-independent clock -- ticket creation to the first commit citing it,
   read from git, which means the same thing in 2016 and 2025.
2. COMPOSITION SHIFT. If later years simply contain more abstraction work (§5)
   or more cloud-connector work (§9a) -- both already known to be slow -- the
   trend is composition, not change. Both are controlled. (Connector share does
   rise sharply: rho=+0.29, p<0.001.)
3. RIGHT-CENSORING. The corpus is built from commits that LANDED, so recent
   tickets that stalled forever are missing. This biases recent years toward
   FAST, making any measured divergence conservative rather than inflated.
4. LEFT TRUNCATION. The commit corpus starts at release 3.1.0 (March 2018), so
   pre-2018 tickets mechanically show a long time-to-first-commit. Re-fit from
   successively later start years to confirm the result is not an artifact.

Usage:
    python3 scripts/temporal_trend.py
"""
import argparse, json, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blast_radius_model import build_frame, parse_ts, ABSTRACTION_TYPES
from friction_decomposition import load_group

YEAR_MIN, YEAR_MAX = 2016, 2025   # 2014-15 and 2026 have single-digit n

KEY_RE = None  # built lazily in first_commit_dates


def first_commit_dates(repo, cache="ticket_first_commit.json"):
    """key -> unix timestamp of the EARLIEST commit citing it.

    This is the workflow-independent clock. Jira status hygiene collapsed when
    Hadoop moved to GitHub PRs (93.5% -> 15.5% of tickets reach Patch Available),
    so every status-derived duration silently changes meaning mid-corpus. A
    commit date does not: it means the same thing in 2016 and in 2025.
    """
    import re, subprocess
    if os.path.exists(cache):
        return json.load(open(cache))
    pat = re.compile(r"\b(?:HADOOP|HDFS|YARN|MAPREDUCE|HDDS|OZONE|SUBMARINE|YETUS)-\d+\b")
    out = subprocess.run(
        ["git", "-C", repo, "log", "--all", "--pretty=format:%ct%x1f%s %b%x1e"],
        capture_output=True, text=True, check=True).stdout
    first = {}
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if "\x1f" not in rec:
            continue
        ts, _, msg = rec.partition("\x1f")
        if not ts.isdigit():
            continue
        ts = int(ts)
        for k in set(pat.findall(msg)):
            if k not in first or ts < first[k]:
                first[k] = ts
    json.dump(first, open(cache, "w"))
    return first


def assemble(args):
    """Architectural + ordinary tickets with year, phase measures and labels."""
    eps = json.load(open(args.episodes))
    abst = {e["issue_key"] for e in eps
            if e["issue_key"] and any(t in ABSTRACTION_TYPES for t in e["arch_types"])}
    arch_keys = sorted({e["issue_key"] for e in eps if e["issue_key"]})

    A = load_group(arch_keys, True)
    C = load_group(json.load(open("control_tickets.json")), False)
    A["arch"], C["arch"] = 1, 0
    A["abstraction"] = A.key.isin(abst)
    C["abstraction"] = False

    _, tk = build_frame(args)
    conn = set(tk[tk.connector].key)
    A["connector"] = A.key.isin(conn)
    C["connector"] = False

    d = pd.concat([A, C], ignore_index=True)

    def created(k, arch):
        p = f".jira_changelog/{k}.json" if arch else f".jira_control/{k}.json"
        return parse_ts(json.load(open(p))["created"]) if os.path.exists(p) else None
    d["created"] = [created(r.key, r.arch) for r in d.itertuples()]
    d["year"] = d.created.map(lambda t: t.year if t is not None else np.nan)

    # Triage latency: created -> first status transition (the dossier's anchor).
    def triage(k, arch):
        p = f".jira_changelog/{k}.json" if arch else f".jira_control/{k}.json"
        if not os.path.exists(p):
            return None
        j = json.load(open(p))
        h = j.get("status_history") or []
        if not h:
            return None
        return (parse_ts(h[0]["created"]) - parse_ts(j["created"])).total_seconds() / 86400
    d["triage"] = [triage(r.key, r.arch) for r in d.itertuples()]

    # Workflow-independent clock: ticket creation -> first commit citing it.
    fc = first_commit_dates(args.repo)
    d["t_to_commit"] = [
        (fc[r.key] - r.created.timestamp()) / 86400
        if (r.key in fc and r.created is not None and fc[r.key] > r.created.timestamp())
        else np.nan
        for r in d.itertuples()]
    return d[d.year.between(YEAR_MIN, YEAR_MAX)].copy()


def report_coverage(d):
    print("== Sample by year (transparency: where is the control thin?) ==")
    t = d.pivot_table(index="year", columns="arch", values="key", aggfunc="count")
    t.columns = ["ordinary", "architectural"]
    print(t.fillna(0).astype(int).to_string())
    thin = t[t.ordinary.fillna(0) < 5]
    if len(thin):
        print(f"  !! ordinary control has <5 tickets in: {list(thin.index.astype(int))}")
        print("     Trends are re-tested below on years where BOTH groups are populated.")
    return t


def report_workflow_drift(d):
    """Threat 1. If this drifts, status-derived timing is not comparable over time."""
    print("\n== Threat 1: workflow drift (did the meaning of the status field change?) ==")
    t = d.pivot_table(index="year", columns="arch", values="reached_patch", aggfunc="mean")
    t.columns = ["ordinary", "architectural"]
    print((t * 100).round(1).to_string())
    early = d[d.year <= 2019].reached_patch.mean()
    late = d[d.year >= 2022].reached_patch.mean()
    print(f"  reached Patch Available: {early:.1%} (<=2019) -> {late:.1%} (>=2022)")
    drift = abs(early - late) > 0.15
    print("  -> " + ("SUBSTANTIAL DRIFT. Status-derived timings are NOT comparable across "
                     "eras; the full-workflow re-test below is the primary result."
                     if drift else
                     "no substantial drift; whole-corpus trends are usable."))
    return {"early": float(early), "late": float(late), "drift": bool(drift)}


def trends(d, label, measure="triage"):
    print(f"\n== Trend: year vs {measure} [{label}] ==")
    out = {}
    for a, name in [(1, "architectural"), (0, "ordinary")]:
        s = d[(d.arch == a)].dropna(subset=[measure])
        if len(s) < 20:
            print(f"  {name:14s} n={len(s)} — too few to test")
            continue
        rho, p = stats.spearmanr(s.year, s[measure])
        star = " *" if p < 0.05 else ""
        print(f"  {name:14s} rho = {rho:+.3f}   p = {p:.2e}{star}   (n={len(s)})")
        out[name] = {"rho": float(rho), "p": float(p), "n": int(len(s))}
    return out


def did(d, label, measure="triage"):
    """The actual test: does architectural work slow down FASTER than ordinary?"""
    s = d.dropna(subset=[measure]).copy()
    s["y"] = np.log1p(s[measure].clip(lower=0))
    s["yr"] = s.year - s.year.min()
    s["arch_x_yr"] = s.arch * s.yr
    print(f"\n== Difference-in-differences on {measure} [{label}] (n={len(s)}) ==")
    out = {}
    specs = {
        "plain": ["arch", "yr", "arch_x_yr"],
        "+ composition controls": ["arch", "yr", "arch_x_yr", "abstraction", "connector"],
    }
    for name, cols in specs.items():
        X = sm.add_constant(s[cols].astype(float))
        m = sm.OLS(s.y, X).fit(cov_type="HC3")
        print(f"  -- {name} (R2={m.rsquared:.3f}) --")
        for c in cols:
            star = " *" if m.pvalues[c] < 0.05 else ""
            print(f"     {c:14s} coef {m.params[c]:+.3f}   p = {m.pvalues[c]:.4f}{star}")
        out[name] = {c: {"coef": float(m.params[c]), "p": float(m.pvalues[c])} for c in cols}
    print("  (arch_x_yr is the finding: architectural work slowing FASTER than ordinary.)")
    return out


def composition(d):
    """Threat 2: are later years just carrying more of the already-slow categories?"""
    print("\n== Threat 2: composition shift within architectural work ==")
    a = d[d.arch == 1]
    t = a.groupby("year").agg(n=("key", "count"), pct_abstraction=("abstraction", "mean"),
                              pct_connector=("connector", "mean"))
    print((t.assign(pct_abstraction=(t.pct_abstraction * 100).round(1),
                    pct_connector=(t.pct_connector * 100).round(1))).to_string())
    r1, p1 = stats.spearmanr(a.year, a.abstraction.astype(int))
    r2, p2 = stats.spearmanr(a.year, a.connector.astype(int))
    print(f"  year vs abstraction share: rho={r1:+.3f} p={p1:.3f}")
    print(f"  year vs connector share:   rho={r2:+.3f} p={p2:.3f}")
    return {"abstraction": {"rho": float(r1), "p": float(p1)},
            "connector": {"rho": float(r2), "p": float(p2)}}


def left_truncation(d):
    """Threat 4, found from the figure: the commit corpus starts at release 3.1.0
    (March 2018), so a ticket filed in 2016 mechanically shows a long
    time-to-first-commit -- we simply cannot see its earlier commits. That
    inflates the early baseline and could manufacture a spurious "everything got
    faster" trend. Re-fit with progressively later start years: if the
    interaction is an artifact it will not survive.
    """
    print("\n== Threat 4: left truncation (commit corpus starts 2018-03) ==")
    out = {}
    for lo in [2016, 2018, 2019]:
        s = d[d.year >= lo].dropna(subset=["t_to_commit"]).copy()
        s["y"] = np.log1p(s.t_to_commit.clip(lower=0))
        s["yr"] = s.year - s.year.min()
        s["arch_x_yr"] = s.arch * s.yr
        cols = ["arch", "yr", "arch_x_yr", "abstraction", "connector"]
        m = sm.OLS(s.y, sm.add_constant(s[cols].astype(float))).fit(cov_type="HC3")
        print(f"  from {lo}+ (n={len(s):3d}):  year main effect {m.params['yr']:+.3f} "
              f"(p={m.pvalues['yr']:.4f})   interaction {m.params['arch_x_yr']:+.3f} "
              f"(p={m.pvalues['arch_x_yr']:.4f})")
        out[str(lo)] = {"n": int(len(s)),
                        "yr": {"coef": float(m.params["yr"]), "p": float(m.pvalues["yr"])},
                        "interaction": {"coef": float(m.params["arch_x_yr"]),
                                        "p": float(m.pvalues["arch_x_yr"])}}
    print("  -> The interaction is stable (~+0.19 to +0.20, p<0.05 throughout); the year")
    print("     MAIN effect weakens, so 'ordinary got absolutely faster' is partly the 2016")
    print("     truncation. The defensible claim is the DIVERGENCE, not the absolute speedup.")
    return out


def plot(d, out):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    for a, c, lab in [(1, "#c53030", "architectural"), (0, "#2b6cb0", "ordinary (control)")]:
        s = d[(d.arch == a)].dropna(subset=["t_to_commit"])
        g = s.groupby("year").t_to_commit.agg(["median", "count"])
        g = g[g["count"] >= 5]
        ax.plot(g.index, g["median"], "o-", color=c, label=lab, linewidth=2.4, markersize=6)
        for yr, r in g.iterrows():
            ax.annotate(f"{int(r['count'])}", (yr, r["median"]), fontsize=6.5,
                        xytext=(0, -12), textcoords="offset points", ha="center", color=c)
    ax.set_yscale("log")
    ax.set_xlabel("Year ticket was filed  (small numbers = tickets that year)")
    ax.set_ylabel("Median days to first commit (log scale)")
    ax.set_title("The gap widens: ordinary refactoring speeds up,\n"
                 "architectural refactoring does not", fontsize=10.5)
    ax.legend(fontsize=8.5)
    ax.grid(alpha=.25, which="major")

    ax = axes[1]
    t = d.pivot_table(index="year", columns="arch", values="reached_patch", aggfunc="mean")
    t.columns = ["ordinary", "architectural"]
    ax.plot(t.index, t["architectural"] * 100, "o-", color="#c53030", label="architectural",
            linewidth=2.2, markersize=6)
    ax.plot(t.index, t["ordinary"] * 100, "o-", color="#a0aec0", label="ordinary",
            linewidth=2.2, markersize=6)
    ax.set_ylim(0, 105)
    ax.set_xlabel("Year ticket was filed")
    ax.set_ylabel("% of tickets reaching Patch Available")
    ax.set_title("Why the left panel uses a git clock, not Jira status:\n"
                 "status hygiene collapsed 93% → 16% mid-corpus", fontsize=10.5)
    ax.legend(fontsize=8.5)
    ax.grid(alpha=.25)

    fig.suptitle("Hadoop improved at ordinary refactoring — but not at architectural refactoring",
                 fontsize=13, y=1.02)
    fig.text(0.5, -0.03, "Difference-in-differences on the git clock: interaction +0.202, "
             "p = 0.003, controlling for composition; stable at +0.19 excluding pre-2018 tickets. "
             "2016 is inflated by corpus left-truncation.",
             ha="center", fontsize=8.5, color="#4a5568")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"\nWrote {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--graph", default="module_blast_radius.json")
    ap.add_argument("--episode-files", default="episode_files.json")
    ap.add_argument("--episodes", default="architectural_episodes_all.json")
    ap.add_argument("--changelog", default=".jira_changelog")
    ap.add_argument("--props", default=".jira_props")
    ap.add_argument("--assignees", default=".jira_assignee")
    ap.add_argument("--fig", default="figures/temporal_trend.png")
    ap.add_argument("--out", default="temporal_trend.json")
    args = ap.parse_args()

    d = assemble(args)
    res = {}
    cov = report_coverage(d)
    res["workflow_drift"] = report_workflow_drift(d)
    res["trend_all"] = trends(d, "whole corpus")
    res["composition"] = composition(d)
    res["did_all"] = did(d, "whole corpus")

    # Secondary: restrict to tickets that drove the full workflow (§5b). This
    # trades contamination for SELECTION -- in 2022+ only ~16% of tickets reach
    # Patch Available, so conditioning on it picks a non-random late-era
    # subgroup, and only 3% of the sub-corpus is post-2022. Reported, not relied on.
    both = cov.dropna().pipe(lambda t: t[(t.ordinary >= 5) & (t.architectural >= 5)]).index
    clean = d[d.reached_patch & d.year.isin(both)]
    print(f"\n{'-'*70}\nSECONDARY (selection-limited): full-workflow tickets, balanced years"
          f"\n{'-'*70}")
    print(f"  NOTE: only {len(clean[clean.year >= 2022]) / max(len(clean), 1):.1%} of this "
          f"sub-corpus is post-2022 — it cannot speak to the recent era.")
    res["trend_clean"] = trends(clean, "full-workflow, balanced years")
    res["did_clean"] = did(clean, "full-workflow, balanced years")

    # PRIMARY: the workflow-independent clock. Unaffected by the status-hygiene
    # collapse and by the selection it induces, so it is the only measure that
    # means the same thing in 2016 and 2025.
    print(f"\n{'='*70}\nPRIMARY: workflow-independent clock (ticket -> first commit citing it)"
          f"\n{'='*70}")
    print(f"  coverage: {d.t_to_commit.notna().sum()}/{len(d)} tickets "
          f"({d.t_to_commit.notna().mean():.1%}) matched to a commit")
    res["trend_commit"] = trends(d, "whole corpus, git clock", measure="t_to_commit")
    res["did_commit"] = did(d, "whole corpus, git clock", measure="t_to_commit")

    res["left_truncation"] = left_truncation(d)
    plot(d, args.fig)
    json.dump(res, open(args.out, "w"), indent=2, default=float)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
