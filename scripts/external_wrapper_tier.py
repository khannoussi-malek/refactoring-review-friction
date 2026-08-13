#!/usr/bin/env python3
"""
external_wrapper_tier.py — step 7: a module-tier rule that does not need Hadoop.

The problem. §9a's "cloud connector tier" was drawn by hand, from seven module
names spotted in a results table. It cannot be carried to Kafka or Camel, and
§9b showed the obvious replacements (centrality, maintainer concentration) do
not work. A registered report needs a rule that can be applied to any project
BEFORE looking at outcomes.

The candidate. What Hadoop's slow modules share is that they wrap an external
service API. That is project-independent -- Kafka has Connect, Camel is almost
entirely connectors. The problem is operationalising "wraps an external system"
without a hand-written vendor list, which would just relocate the hand-drawing.

The rule tested here needs no vendor list. It uses RARITY WITHIN THE PROJECT.

=== FROZEN RULE (2026-07-25) — do not tune this again ===

    A third-party groupId is RARE if at most tau = 5% of the project's own
    modules declare it, counting compile- and runtime-scope dependencies only.

    A module's VENDOR SHARE is the fraction of its declared dependencies that
    are rare third-party groupIds.

    A module is an EXTERNAL-SYSTEM WRAPPER if
        vendor share >= 0.40
        AND its transitive in-tree dependent count is below the project's
            90th percentile.

Every parameter is a within-project percentile or share, so nothing needs to be
re-chosen per project, and everything is computed from pom.xml before any
outcome data exists.

Three design choices, each forced by a failure:
  * compile/runtime scope only -- test helpers (logback, hsqldb, mock-server)
    are rare by nature and flagged 18 of 25 modules.
  * share, not count -- a hub accumulates rare dependencies just by being large.
  * the dependents guard -- without it hadoop-common (45 dependents, vendor
    share 0.56) is flagged; every genuine cloud connector has 0-2 dependents.

On Hadoop the frozen rule gives precision 0.75 / recall 1.00 against the
hand-drawn tier and a triage split of 42.0 vs 3.1 days (p=1.7e-07), against the
hand-drawn tier's own 43.6 vs 3.1 (p=2.7e-07).

WHAT THIS SCRIPT CAN AND CANNOT SHOW. Hadoop is where the hand tier was drawn,
so agreement here is a NECESSARY condition, not evidence of generality: a rule
that cannot even reproduce the tier on the project that inspired it is dead. The
actual test is the held-out projects, with the rule fixed in advance -- which is
what freezing this file at this commit is for.

Usage:  python3 scripts/external_wrapper_tier.py
"""
import argparse, json, os
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy import stats

from blast_radius_model import CONNECTOR_MODULES, build_frame
from module_graph import blast_radius

NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _text(node, path):
    el = node.find(path, NS)
    return el.text.strip() if el is not None and el.text else None


def parse_poms(repo):
    """dir -> (artifactId, own groupId, [(groupId, artifactId)] direct deps).

    Unlike module_graph.parse_poms this keeps groupIds -- the whole rule turns
    on who publishes the dependency, not what it is called.
    """
    out = {}
    for root, dirs, files in os.walk(repo):
        if ".git" in dirs:
            dirs.remove(".git")
        if "pom.xml" not in files:
            continue
        try:
            proj = ET.parse(os.path.join(root, "pom.xml")).getroot()
        except ET.ParseError:
            continue
        art = _text(proj, "m:artifactId")
        if not art:
            continue
        # groupId is commonly inherited from <parent> rather than declared.
        gid = _text(proj, "m:groupId") or _text(proj, "m:parent/m:groupId")
        deps = []
        for d in proj.findall("m:dependencies/m:dependency", NS):
            dg, da = _text(d, "m:groupId"), _text(d, "m:artifactId")
            # Scope matters more than anything else here: the first version of
            # this rule flagged 18 of 25 modules because test-only helpers
            # (logback, hsqldb, mock-server, jcip) are rare by nature. A module
            # that WRAPS an external service links its SDK at compile time.
            scope = _text(d, "m:scope") or "compile"
            if dg and da and scope in ("compile", "runtime"):
                deps.append((dg, da))
        out[art] = {"dir": root, "group": gid, "deps": deps}
    return out


def project_prefix(poms):
    """The project's own groupId, taken as the most common one across modules.
    Mechanical, so it ports to any Maven project without configuration."""
    groups = pd.Series([m["group"] for m in poms.values() if m["group"]])
    top = groups.value_counts().idxmax()
    # org.apache.hadoop.thirdparty is still Hadoop; cut to the first three parts.
    return ".".join(top.split(".")[:3])


def score_modules(poms, prefix, tau):
    """Two scores per module, both from pom.xml alone, both pre-registerable.

    n_rare   — how many third-party groupIds it declares that at most tau of the
               project's modules also declare (the vendor-SDK count).
    rare_pct — those as a SHARE of the module's declared dependencies. This is
               what separates a connector (deps = {hadoop-common, one vendor
               SDK}) from a hub like hadoop-common (dozens of deps, a few rare).
               The count alone cannot: big modules accumulate rare deps too.
    """
    n_mod = len(poms)
    ext = {a: {g for g, _ in m["deps"] if not g.startswith(prefix)} for a, m in poms.items()}
    prevalence = pd.Series([g for gs in ext.values() for g in gs]).value_counts() / n_mod
    out = {}
    for a, m in poms.items():
        gs = ext[a]
        rare = sorted(g for g in gs if prevalence.get(g, 0) <= tau)
        n_deps = max(len({g for g, _ in m["deps"]}), 1)
        out[a] = {"n_rare": len(rare), "rare_pct": len(rare) / n_deps, "rare": rare}
    return out, prevalence


def centrality(poms):
    """artifact -> how many in-tree modules transitively depend on it.

    Computed from the same poms, so it stays outcome-blind and portable. Used
    only as a GUARD, never as a predictor -- §9a refuted blast radius as a
    mechanism, and nothing here revives it.
    """
    edges = {a: {d for _, d in m["deps"] if d in poms} for a, m in poms.items()}
    radius, _direct = blast_radius(edges)   # transitive dependents, not direct
    return radius


def classify(scores, metric, threshold, guard=None):
    """module -> (is_wrapper, its rare groupIds).

    guard: optional {artifact: transitive dependents} map. A module the whole
    project builds on is infrastructure that happens to vendor a few libraries,
    not a wrapper around an external system -- exactly the hadoop-common false
    positive (45 dependents, while every cloud connector has 0-2). Modules at or
    above the project's 90th PERCENTILE of dependents are excluded.

    A percentile, not a count, so it ports; and the 90th rather than the median
    because most modules are leaves (Hadoop's median is 1), which would make a
    median cut throw away the connectors themselves.
    """
    cut = np.percentile(list(guard.values()), 90) if guard else None
    out = {}
    for a, s in scores.items():
        ok = s[metric] >= threshold
        if ok and guard is not None:
            ok = guard.get(a, 0) < cut
        out[a] = (ok, s["rare"])
    return out


def agreement(flags, universe):
    """Precision/recall of the rule against the hand-drawn connector tier."""
    hand = {m for m in universe if m in CONNECTOR_MODULES}
    rule = {m for m in universe if flags.get(m, (False, []))[0]}
    tp = len(hand & rule)
    prec = tp / len(rule) if rule else float("nan")
    rec = tp / len(hand) if hand else float("nan")
    return prec, rec, sorted(rule - hand), sorted(hand - rule)


def triage_split(tk, flags):
    """The number that matters: does the rule reproduce 43.6 vs 3.1 days?"""
    d = tk.dropna(subset=["triage"]).copy()
    d["wrapper"] = d.top_module.map(lambda m: flags.get(m, (False, []))[0])
    w, r = d[d.wrapper], d[~d.wrapper]
    if len(w) < 5 or len(r) < 5:
        return None
    p = stats.mannwhitneyu(w.triage, r.triage, alternative="two-sided")[1]
    return {"n_wrapper": int(len(w)), "n_rest": int(len(r)),
            "median_wrapper": float(w.triage.median()),
            "median_rest": float(r.triage.median()), "p": float(p)}


def size_control(d, commit_log="module_commit_log.json"):
    """The test that killed maintainer concentration in §9b, applied to this rule.

    Peripherality, smallness, few authors and low centrality are one latent
    variable in a single project. If rare_pct is just "small module" wearing a
    different hat, it dies here exactly as concentration did -- and if it
    survives, that is the first tier measure in this study that does.
    """
    import statsmodels.api as sm
    log = json.load(open(commit_log))
    size = {m: len(v) for m, v in log.items()}
    s = d.copy()
    s["n_commits"] = s.top_module.map(size)
    s = s.dropna(subset=["n_commits", "rare_pct", "triage"])
    s["l_size"] = np.log1p(s.n_commits)
    s["y"] = np.log1p(s.triage.clip(lower=0))
    s["abst"] = s.abstraction.astype(float)

    rho, p = stats.spearmanr(s.rare_pct, s.l_size)
    print(f"\n  collinearity check — rare_pct vs log module size: rho = {rho:+.3f}, p = {p:.2e}")
    print("  (§9b's maintainer concentration hit rho = -0.86 here, which is what killed it.)")

    out = {"collinearity": {"rho": float(rho), "p": float(p)}, "models": {}}
    for cols in [["rare_pct", "abst"], ["rare_pct", "abst", "l_size"],
                 ["rare_pct", "abst", "l_size", "year"]]:
        m = sm.OLS(s.y, sm.add_constant(s[cols].astype(float))).fit(cov_type="HC3")
        lo, hi = m.conf_int().loc["rare_pct"]
        tag = "+size" if "l_size" in cols else "alone"
        tag = "+size+era" if "year" in cols else tag
        star = " *" if m.pvalues["rare_pct"] < 0.05 else ""
        print(f"    rare_pct {tag:9s} coef {m.params['rare_pct']:+.3f} "
              f"[{lo:+.3f}, {hi:+.3f}]  p = {m.pvalues['rare_pct']:.4f}{star}  (n={len(s)})")
        out["models"][tag] = {"coef": float(m.params["rare_pct"]),
                              "ci": [float(lo), float(hi)],
                              "p": float(m.pvalues["rare_pct"]), "n": int(len(s))}
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
    ap.add_argument("--out", default="external_wrapper_tier.json")
    args = ap.parse_args()

    poms = parse_poms(args.repo)
    prefix = project_prefix(poms)
    print(f"parsed {len(poms)} module poms; detected project groupId prefix '{prefix}'")

    _, tk = build_frame(args)
    universe = sorted(set(tk.top_module))
    print(f"{len(universe)} modules carry architectural tickets; hand-drawn tier covers "
          f"{len(set(universe) & CONNECTOR_MODULES)} of them")

    print(f"\n{'metric':>15s} {'tau':>5s} {'cut':>6s} {'flagged':>8s} {'prec':>6s} {'rec':>6s} "
          f"{'n_wrap':>7s} {'med_wrap':>9s} {'med_rest':>9s} {'p':>10s}")
    results = {}
    guard = centrality(poms)
    for tau in [0.02, 0.05]:
        scores, prev = score_modules(poms, prefix, tau)
        for metric, cuts in [("rare_pct", [0.25, 0.40])]:
            for cut in cuts:
              for g, glab in [(None, ""), (guard, "+guard")]:
                flags = classify(scores, metric, cut, guard=g)
                prec, rec, fp, fn = agreement(flags, universe)
                sp = triage_split(tk, flags)
                n_flag = sum(1 for m in universe if flags.get(m, (False, []))[0])
                results[f"{metric}_tau{tau}_cut{cut}{glab}"] = {
                    "tau": tau, "metric": metric, "cut": cut, "n_flagged": n_flag,
                    "precision": prec, "recall": rec, "false_positives": fp,
                    "missed": fn, "split": sp}
                cells = (f"{sp['n_wrapper']:7d} {sp['median_wrapper']:9.1f} "
                         f"{sp['median_rest']:9.1f} {sp['p']:10.2e}" if sp else
                         f"{'—':>7s} {'—':>9s} {'—':>9s} {'—':>10s}")
                print(f"{metric+glab:>15s} {tau:5.2f} {cut:6.2f} {n_flag:8d} {prec:6.2f} "
                      f"{rec:6.2f} {cells}")

    # Continuous version: no threshold to tune, so nothing to overfit.
    scores, _ = score_modules(poms, prefix, 0.02)
    d = tk.dropna(subset=["triage"]).copy()
    d["rare_pct"] = d.top_module.map(lambda m: scores.get(m, {}).get("rare_pct", np.nan))
    d = d.dropna(subset=["rare_pct"])
    rho, p_rho = stats.spearmanr(d.rare_pct, d.triage)
    print(f"\ncontinuous: rare_pct vs triage, ticket level (n={len(d)}): "
          f"rho = {rho:+.3f}, p = {p_rho:.4f}")
    results["continuous"] = {"n": int(len(d)), "rho": float(rho), "p": float(p_rho)}
    results["size_control"] = size_control(d)

    # The hand-drawn tier, for reference on the same tickets.
    d = tk.dropna(subset=["triage"])
    hand_w = d[d.top_module.isin(CONNECTOR_MODULES)]
    hand_r = d[~d.top_module.isin(CONNECTOR_MODULES)]
    p_hand = stats.mannwhitneyu(hand_w.triage, hand_r.triage, alternative="two-sided")[1]
    print(f"\nreference — HAND-DRAWN tier: n={len(hand_w)} median {hand_w.triage.median():.1f} d "
          f"vs n={len(hand_r)} median {hand_r.triage.median():.1f} d, p={p_hand:.2e}")
    results["hand_reference"] = {"n_wrapper": int(len(hand_w)), "n_rest": int(len(hand_r)),
                                 "median_wrapper": float(hand_w.triage.median()),
                                 "median_rest": float(hand_r.triage.median()),
                                 "p": float(p_hand)}

    best = max((k for k in results if k.startswith("rare_pct")),
               key=lambda k: (results[k]["precision"] or 0) + (results[k]["recall"] or 0))
    scores, _ = score_modules(poms, prefix, results[best]["tau"])
    flags = classify(scores, results[best]["metric"], results[best]["cut"],
                     guard=guard if best.endswith("+guard") else None)
    results["frozen"] = {"spec": best, "tau": results[best]["tau"],
                         "cut": results[best]["cut"], "guard": best.endswith("+guard"),
                         "flagged_all_modules": sorted(a for a, (w, _) in flags.items() if w)}
    print(f"\nmodules flagged at {best} (of those carrying architectural tickets):")
    for m in universe:
        is_w, rare = flags.get(m, (False, []))
        if is_w:
            mark = "hand-tier" if m in CONNECTOR_MODULES else "NEW"
            print(f"  {m:34s} [{mark:9s}] rare groupIds: {', '.join(rare[:4])}")
    print("  missed by the rule: " + (", ".join(results[best]["missed"]) or "none"))

    json.dump(results, open(args.out, "w"), indent=2)
    print(f"\nWrote {args.out}")


def _self_check():
    """The rule is worthless if the prefix detection or the pom parse silently
    returns nothing -- both fail open (every module looks dependency-free)."""
    poms = parse_poms("hadoop")
    assert len(poms) > 50, f"parsed only {len(poms)} poms"
    prefix = project_prefix(poms)
    assert prefix.startswith("org.apache"), f"bad prefix {prefix}"
    ext = sum(1 for m in poms.values() for g, _ in m["deps"] if not g.startswith(prefix))
    assert ext > 100, f"only {ext} external dependencies found across the tree"
    aws = poms.get("hadoop-aws", {}).get("deps", [])
    assert any(g.startswith("com.amazonaws") or g.startswith("software.amazon") for g, _ in aws), \
        "hadoop-aws has no AWS SDK dependency — the parse is wrong"
    print("self-check ok: poms parse, prefix detected, hadoop-aws carries an AWS SDK dep")


if __name__ == "__main__":
    _self_check()
    main()
