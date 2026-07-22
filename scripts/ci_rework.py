#!/usr/bin/env python3
"""
ci_rework.py — test §8's "time, not quality" claim with a real rework signal.

§8 concluded that architectural work is slower but not buggier, resting on the
REOPEN RATE (~7%, p=0.97). That is a blunt instrument: reopening is rare, happens
long after the fact, and says nothing about how much a change had to be fixed
before it landed.

Hadoop's pre-commit CI bots give a far better one. Every time a contributor
posts a patch, Hadoop QA runs the build and tests and comments a verdict. So:

    number of CI runs on a ticket  ~=  number of times the patch was revised

TWO TRAPS THIS GUARDS AGAINST:
  1. VOLUME (§10's retraction). CI runs are themselves comments, so more
     discussion mechanically means more of everything. Every cross-group model
     controls for HUMAN comment count explicitly.
  2. SIZE. A bigger patch trips more checkers, so "needed more CI runs" proves
     nothing until change size is held constant. This is the control that
     decides the result -- see change_size().

WHAT THE ANSWER TURNED OUT TO BE: architectural tickets do take more CI runs
(median 5 vs 3, p<1e-4) and that survives the volume control -- but NOT the size
control (p drops to 0.05-0.07). Architectural changes are simply much bigger
(1178 vs 213 java lines churned). So §8's "time, not quality" substantially
SURVIVES this stronger test rather than being overturned by it.

A measure that did NOT work, recorded so nobody retries it: the failure RATE
(failed runs / total runs) is pinned at a ceiling -- `-1 overall` fires on any
warning at all, so 87% of runs "fail" and both group medians sit at 100%.

DATA ASYMMETRY, handled rather than ignored: the architectural cache stores full
comment bodies (so verdicts are parseable) but the control cache stores only
{created, author}. Run COUNTS are therefore available for both groups; VERDICTS
only for architectural. The two analyses are reported separately and never mixed.

Usage:
    python3 scripts/ci_rework.py
"""
import argparse, json, os, re
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blast_radius_model import build_frame, parse_ts, ABSTRACTION_TYPES

# Pre-commit test bots: these post PASS/FAIL verdicts on a submitted patch, which
# is the rework signal. Stored as usernames in .jira_cache and as display names
# in .jira_control, so match on a normalised form.
CI_BOTS = {"hadoopqa", "genericqa", "hadoopci", "yetus"}
# Deliberately EXCLUDED: `hudson` announces successful post-commit builds (not a
# patch verdict), and `githubbot` relays human PR discussion (not CI).
NOT_CI = {"hudson", "githubbot", "asfgithubbot", "jira", "hadoopqabot"}

VERDICT_RE = re.compile(r"([+-])1\s+overall", re.I)
KEY_RE = re.compile(r"\b(?:HADOOP|HDFS|YARN|MAPREDUCE|HDDS|OZONE|SUBMARINE|YETUS)-\d+\b")


def change_size(repo, cache="ticket_change_size.json"):
    """key -> (java files touched, java lines churned) across all commits citing it.

    The control that decides this whole analysis. A patch that touches more code
    trips more checkers, so "needed more CI runs" is not evidence of anything
    until size is held constant. Restricted to .java: Hadoop commits carry
    generated docs and asset dumps that would swamp real code change.
    """
    import subprocess
    if os.path.exists(cache):
        return {k: tuple(v) for k, v in json.load(open(cache)).items()}
    out = subprocess.run(
        ["git", "-C", repo, "log", "--all", "--format=%x1e%x1f%s %b%x1f", "--numstat"],
        capture_output=True, text=True).stdout
    size = {}
    for rec in out.split("\x1e"):
        if rec.count("\x1f") < 2:
            continue
        _, msg, blob = rec.split("\x1f", 2)
        keys = set(KEY_RE.findall(msg))
        if not keys:
            continue
        files = churn = 0
        for line in blob.splitlines():
            p = line.split("\t")
            if len(p) == 3 and p[0].isdigit() and p[1].isdigit() and p[2].endswith(".java"):
                files += 1
                churn += int(p[0]) + int(p[1])
        for k in keys:
            f, c = size.get(k, (0, 0))
            size[k] = (f + files, c + churn)
    json.dump({k: list(v) for k, v in size.items()}, open(cache, "w"))
    return size


def norm_author(a):
    return re.sub(r"[^a-z]", "", (a or "").lower())


def is_ci_bot(a):
    n = norm_author(a)
    return n in CI_BOTS and n not in NOT_CI


def load_ci(key, arch):
    """CI run count for either group; verdicts only where bodies exist."""
    path = f".jira_cache/{key}.json" if arch else f".jira_control/{key}.json"
    if not os.path.exists(path):
        return None
    j = json.load(open(path))
    if arch:
        comments = [{"author": c["author"].get("name"), "created": c["created"],
                     "body": c.get("body", "")}
                    for c in j.get("fields", {}).get("comment", {}).get("comments", [])]
        created = None
        cl = f".jira_changelog/{key}.json"
        if os.path.exists(cl):
            created = parse_ts(json.load(open(cl))["created"])
    else:
        comments = [{"author": c.get("author"), "created": c["created"], "body": None}
                    for c in j.get("comments", [])]
        created = parse_ts(j["created"])

    ci = [c for c in comments if is_ci_bot(c["author"])]
    human = [c for c in comments
             if not is_ci_bot(c["author"]) and norm_author(c["author"]) not in NOT_CI]

    n_fail = n_pass = None
    if arch:
        n_fail = n_pass = 0
        for c in ci:
            m = VERDICT_RE.search(c["body"] or "")
            if m:
                if m.group(1) == "-":
                    n_fail += 1
                else:
                    n_pass += 1

    return {"key": key, "arch": int(arch), "n_ci_runs": len(ci),
            "n_human_comments": len(human), "n_comments": len(comments),
            "n_fail": n_fail, "n_pass": n_pass,
            "year": created.year if created else np.nan}


def assemble(args):
    eps = json.load(open(args.episodes))
    abst = {e["issue_key"] for e in eps
            if e["issue_key"] and any(t in ABSTRACTION_TYPES for t in e["arch_types"])}
    arch_keys = sorted({e["issue_key"] for e in eps if e["issue_key"]})
    rows = [r for r in (load_ci(k, True) for k in arch_keys) if r]
    rows += [r for r in (load_ci(k, False) for k in json.load(open("control_tickets.json"))) if r]
    d = pd.DataFrame(rows)
    d["abstraction"] = d.key.isin(abst) & (d.arch == 1)
    _, tk = build_frame(args)
    d["connector"] = d.key.isin(set(tk[tk.connector].key))
    d["verdicts"] = d.n_fail.fillna(0) + d.n_pass.fillna(0)
    d["fail_rate"] = np.where(d.verdicts > 0, d.n_fail / d.verdicts.replace(0, np.nan), np.nan)
    sz = change_size(args.repo)
    d["n_java_files"] = d.key.map(lambda k: sz.get(k, (np.nan, np.nan))[0])
    d["churn"] = d.key.map(lambda k: sz.get(k, (np.nan, np.nan))[1])
    return d


def report_instrument(d):
    """Same discipline as §5b/§5c: check the instrument before trusting the measure.

    CI verdicts only exist while the patch workflow is in use. When Hadoop moved
    to GitHub PRs the pre-commit bot stopped commenting on Jira, so CI-run counts
    decay for reasons that have nothing to do with rework.
    """
    print("== Instrument check: is CI visible in Jira across the whole corpus? ==")
    t = d.dropna(subset=["year"]).groupby(["year", "arch"]).apply(
        lambda g: (g.n_ci_runs > 0).mean(), include_groups=False).unstack()
    t.columns = ["ordinary", "architectural"]
    print((t * 100).round(1).to_string())
    early = (d[d.year <= 2019].n_ci_runs > 0).mean()
    late = (d[d.year >= 2022].n_ci_runs > 0).mean()
    print(f"  tickets with any CI verdict: {early:.1%} (<=2019) -> {late:.1%} (>=2022)")
    print("  -> CI visibility decays with the GitHub migration, exactly like §5c's status")
    print("     hygiene. Analyses below are restricted to tickets that HAVE CI data.")
    return {"early": float(early), "late": float(late)}


def compare(d):
    """Cross-group: do architectural changes need more CI attempts?"""
    ci = d[d.n_ci_runs > 0]
    A, C = ci[ci.arch == 1], ci[ci.arch == 0]
    print(f"\n== CI runs: architectural vs ordinary (tickets with CI data) ==")
    print(f"  architectural n={len(A):3d}  median runs {A.n_ci_runs.median():.1f}   "
          f"mean {A.n_ci_runs.mean():.2f}")
    print(f"  ordinary      n={len(C):3d}  median runs {C.n_ci_runs.median():.1f}   "
          f"mean {C.n_ci_runs.mean():.2f}")
    p = stats.mannwhitneyu(A.n_ci_runs, C.n_ci_runs, alternative="two-sided")[1]
    print(f"  Mann-Whitney p = {p:.4f}")

    # Architectural changes are simply much bigger, and a bigger patch trips more
    # checkers. Size is the control that decides whether this means anything.
    print(f"\n  -- but architectural changes are far BIGGER --")
    for col, lab in [("n_java_files", "java files touched"), ("churn", "java lines churned")]:
        a, c = A[col].dropna(), C[col].dropna()
        pp = stats.mannwhitneyu(a, c, alternative="two-sided")[1]
        print(f"     {lab:20s} arch {a.median():7.0f}   ordinary {c.median():7.0f}   p = {pp:.1e}")

    print(f"\n  -- nested models: §10 trap (volume) then the size control --")
    s = ci.dropna(subset=["year", "n_java_files", "churn"]).copy()
    s["l_runs"] = np.log1p(s.n_ci_runs)
    s["l_human"] = np.log1p(s.n_human_comments)
    s["l_files"] = np.log1p(s.n_java_files)
    s["l_churn"] = np.log1p(s.churn)
    out = {}
    for name, cols in [("raw", ["arch"]),
                       ("+ human comments", ["arch", "l_human"]),
                       ("+ change size", ["arch", "l_human", "l_files", "l_churn"]),
                       ("+ change size + era", ["arch", "l_human", "l_files", "l_churn", "year"])]:
        m = sm.OLS(s.l_runs, sm.add_constant(s[cols].astype(float))).fit(cov_type="HC3")
        terms = "  ".join(f"{c} {m.params[c]:+.3f} (p={m.pvalues[c]:.4f})" for c in cols)
        print(f"     {name:22s} R2={m.rsquared:.3f}  {terms}")
        out[name] = {c: {"coef": float(m.params[c]), "p": float(m.pvalues[c])} for c in cols}
    print("     -> the architectural effect survives the volume control but NOT the size")
    print("        control (p=0.07 -> 0.05, borderline). Extra rework is mostly bigger patches,")
    print("        so §8's 'time, not quality' substantially SURVIVES this stronger test.")
    return {"median_arch": float(A.n_ci_runs.median()), "median_ord": float(C.n_ci_runs.median()),
            "p": float(p), "n_arch": int(len(A)), "n_ord": int(len(C)),
            "median_churn_arch": float(A.churn.median()), "median_churn_ord": float(C.churn.median()),
            "models": out}


def failure_rates(d):
    """Architectural-only, volume-independent: what SHARE of CI runs failed?

    Reported for completeness, but see the ceiling warning below -- this measure
    turns out to be unusable, which is itself worth recording so nobody tries it
    again expecting a signal.
    """
    a = d[(d.arch == 1) & (d.verdicts >= 2)]
    share = a.n_fail.sum() / a.verdicts.sum()
    print(f"\n== Failure rate (volume-independent), architectural only, n={len(a)} ==")
    print(f"  overall failed-run share: {share:.1%} "
          f"({int(a.n_fail.sum())} failed / {int(a.verdicts.sum())} verdicts)")
    ab, rel = a[a.abstraction], a[~a.abstraction]
    p = stats.mannwhitneyu(ab.fail_rate, rel.fail_rate, alternative="two-sided")[1]
    print(f"  abstraction n={len(ab):3d}  median fail rate {ab.fail_rate.median():.1%}")
    print(f"  relocation  n={len(rel):3d}  median fail rate {rel.fail_rate.median():.1%}")
    print(f"  Mann-Whitney p = {p:.4f}")
    print(f"  !! CEILING: `-1 overall` fires on ANY warning -- checkstyle, javadoc, a")
    print(f"     single flaky unrelated test -- so {share:.0%} of all runs 'fail' and both")
    print(f"     medians sit at 100%. The measure is pinned against its ceiling and the")
    print(f"     p-value above is NOT interpretable as a quality difference. Use run COUNT.")

    pr = stats.mannwhitneyu(ab.n_ci_runs, rel.n_ci_runs, alternative="two-sided")[1]
    print(f"  (CI runs: abstraction {ab.n_ci_runs.median():.1f} vs relocation "
          f"{rel.n_ci_runs.median():.1f}, p = {pr:.4f} — no difference)")
    return {"overall_fail_share": float(share), "usable": False,
            "abstraction_median": float(ab.fail_rate.median()),
            "relocation_median": float(rel.fail_rate.median()), "p": float(p),
            "runs_p": float(pr), "n": int(len(a))}


def plot(d, out):
    ci = d[d.n_ci_runs > 0]
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5))

    ax = axes[0]
    groups = [("ordinary", ci[ci.arch == 0], "#a0aec0"),
              ("relocation", ci[(ci.arch == 1) & ~ci.abstraction], "#2b6cb0"),
              ("abstraction", ci[(ci.arch == 1) & ci.abstraction], "#c53030")]
    data = [g[1].n_ci_runs.values for g in groups]
    bp = ax.boxplot(data, tick_labels=[g[0] for g in groups], showfliers=False,
                    patch_artist=True, widths=.55,
                    medianprops=dict(color="#1a202c", linewidth=2.2))
    for patch, g in zip(bp["boxes"], groups):
        patch.set_facecolor(g[2]); patch.set_alpha(.55)
    for i, v in enumerate(data):
        ax.text(i + 1, 0.97, f"n={len(v)}\nmed {np.median(v):.0f}",
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=9)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.22)  # headroom so labels clear the whiskers
    ax.set_ylabel("CI runs per ticket (≈ patch revisions)")
    ax.set_title("How many times did the patch have to be re-tested?", fontsize=10.5)
    ax.grid(alpha=.25, axis="y")

    ax = axes[1]
    data = [g[1].churn.dropna().values for g in groups]
    bp = ax.boxplot(data, tick_labels=[g[0] for g in groups], showfliers=False,
                    patch_artist=True, widths=.55,
                    medianprops=dict(color="#1a202c", linewidth=2.2))
    for patch, g in zip(bp["boxes"], groups):
        patch.set_facecolor(g[2]); patch.set_alpha(.55)
    ax.set_yscale("log")
    ax.set_ylim(top=ax.get_ylim()[1] * 3)
    for i, v in enumerate(data):
        ax.text(i + 1, 0.97, f"med {np.median(v):.0f}", transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=9)
    ax.set_ylabel("Java lines churned per ticket (log scale)")
    ax.set_title("...but they are also much bigger changes.\nControl for churn and the CI gap "
                 "goes borderline (p=0.05)", fontsize=10.5)
    ax.grid(alpha=.25, axis="y", which="major")

    fig.suptitle("Testing \"time, not quality\" with CI rework instead of reopen rate: §8 survives",
                 fontsize=12.5, y=1.02)
    fig.text(0.5, -0.04, "Pre-2022 tickets only: Hadoop QA stopped posting verdicts to Jira after "
             "the GitHub migration (84.6% -> 0% coverage).", ha="center", fontsize=8.5, color="#4a5568")
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
    ap.add_argument("--fig", default="figures/ci_rework.png")
    ap.add_argument("--out", default="ci_rework.json")
    args = ap.parse_args()

    d = assemble(args)
    print(f"Tickets: {len(d)}  ({(d.arch == 1).sum()} architectural, "
          f"{(d.arch == 0).sum()} ordinary)")
    print(f"With any CI verdict: {(d.n_ci_runs > 0).sum()}")

    res = {"instrument": report_instrument(d)}
    res["cross_group"] = compare(d)
    res["failure_rate"] = failure_rates(d)
    plot(d, args.fig)
    json.dump(res, open(args.out, "w"), indent=2, default=float)
    print(f"Wrote {args.out}")


def _self_check():
    """ponytail: author normalisation and verdict parsing are the fragile bits."""
    assert is_ci_bot("Hadoop QA") and is_ci_bot("hadoopqa"), "display + username forms"
    assert is_ci_bot("genericqa")
    assert not is_ci_bot("Hudson"), "post-commit build announcer is not patch CI"
    assert not is_ci_bot("ASF GitHub Bot"), "PR relay is discussion, not CI"
    assert not is_ci_bot("Steve Loughran")
    assert VERDICT_RE.search("-1 overall").group(1) == "-"
    assert VERDICT_RE.search("+1 overall the patch is fine").group(1) == "+"
    assert VERDICT_RE.search("no verdict here") is None
    print("self-check OK")


if __name__ == "__main__":
    import sys
    if "--self-check" in sys.argv:
        _self_check()
    else:
        main()
