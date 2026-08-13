#!/usr/bin/env python3
"""
revision_metrics.py — the quantities the MSR major revision turns on.

Six computations, all from committed artifacts plus the pinned clones. Nothing
here touches Jira.

1. THE ARITHMETIC CEILING.  A commit that cites a ticket contributes at most one
   NEW distinct ticket to the numerator of the ticket realisation rate, so

       cited_tickets  <=  CSR * commits                    (commit-side supply)
       TRR = cited_tickets / tickets  <=  CSR * commits / tickets

   Write  ceiling(p) = CSR(p) * commits(p) / tickets(p)  and
   fill(p) = TRR(p) / ceiling(p), the share of the attainable maximum actually
   reached. `fill` is bounded above by 1 and is the part of TRR that is NOT
   explained by how many commits the project has per ticket.

2. CLONE DEPTH.  Whether the pinned head_sha reaches the project's whole
   history, or only a truncated recent window. A project whose default branch
   was re-initialised is measured over a window its tracker outruns, and BOTH
   its ticket-side numbers are artefacts of that, not of its traceability.

3. MEDIANS, computed with statistics.median.  `ticket_side_38.py` used
   `v[len(v)//2]`, which is the upper of the two middle values at even n and
   therefore wrong for the 12-project passing group.

4. INFERENCE.  Fisher-z confidence interval, a permutation p-value, and the
   correlation detectable at 80% power for the n in hand.

5. THE DIRECTION TENSION.  Spearman(CSR, TRR) computed two ways: over the 12
   projects where both sides are measured live and exactly, and over the 33 with
   a usable frozen denominator. These do not have to agree and the point is to
   show whether they do.

6. THE ESTIMATOR, END TO END.  The published validation compares number-capping
   at a LIVE denominator against the exact live rate. Table 3 uses number-capping
   at a FROZEN denominator. This computes the error of the thing actually used.

Usage:
    python3 scripts/revision_metrics.py --work <dir of bare clones> \
        --out paper/revision_metrics.json
"""
import argparse, json, math, os, statistics, subprocess, sys

PROBE = "paper/traceability_probe.json"
LIVE = "paper/ticket_coverage.json"
EXT = "paper/ticket_side_38.json"

ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")


# ---------------------------------------------------------------- statistics
def _ranks(v):
    n = len(v)
    idx = sorted(range(n), key=lambda i: v[i])
    r = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[idx[k]] = avg
        i = j + 1
    return r


def spearman(x, y):
    n = len(x)
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def fisher_ci(rho, n, z=1.959963985):
    """95% CI. Valid for |rho| < 1 and n > 3."""
    if n <= 3 or abs(rho) >= 1:
        return None, None
    zr = 0.5 * math.log((1 + rho) / (1 - rho))
    se = 1 / math.sqrt(n - 3)
    return math.tanh(zr - z * se), math.tanh(zr + z * se)


def perm_p(x, y, iters=200000, seed=20260805):
    """Two-sided permutation p-value for Spearman. Deterministic seed.

    Exact enumeration is 33! permutations, so this is a Monte Carlo estimate;
    the seed is fixed so the number is reproducible.
    """
    import random
    rng = random.Random(seed)
    obs = abs(spearman(x, y))
    ys = list(y)
    hits = 0
    for _ in range(iters):
        rng.shuffle(ys)
        if abs(spearman(x, ys)) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (iters + 1)


def detectable_rho(n, power=0.80, alpha=0.05):
    """Smallest |rho| detectable at the given power, via the Fisher-z
    approximation: z_r = (z_{1-a/2} + z_{1-b}) / sqrt(n-3)."""
    if n <= 3:
        return None
    z_a, z_b = 1.959963985, 0.8416212336
    return math.tanh((z_a + z_b) / math.sqrt(n - 3))


# ---------------------------------------------------------------- git probes
def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=ENV, timeout=600)


def clone_depth(work, name, sha):
    p = os.path.join(work, name + ".git")
    if not os.path.isdir(p):
        return None
    r = git(p, "rev-list", "--count", sha)
    if r.returncode != 0:
        return None
    pinned = int(r.stdout.strip())
    allrefs = int(git(p, "rev-list", "--count", "--all").stdout.strip() or 0)
    first = git(p, "log", "--reverse", "--format=%ad", "--date=short", sha).stdout
    first = first.split("\n", 1)[0].strip()
    last = git(p, "log", "-1", "--format=%ad", "--date=short", sha).stdout.strip()
    first_all = git(p, "log", "--reverse", "--format=%ad", "--date=short",
                    "--all").stdout.split("\n", 1)[0].strip()
    return {
        "commits_at_pinned_sha": pinned,
        "commits_all_refs": allrefs,
        "pinned_share_of_all_refs": pinned / allrefs if allrefs else None,
        "first_commit_on_pinned_branch": first,
        "last_commit_on_pinned_branch": last,
        "first_commit_any_ref": first_all,
        "branch_starts_after_repo": first != first_all,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="paper/revision_metrics.json")
    args = ap.parse_args()

    probe = {p["project"]: p for p in json.load(open(PROBE))["projects"]}
    live = {r["project"]: r for r in json.load(open(LIVE))["projects"]}
    ext = {p["project"]: p for p in json.load(open(EXT))["projects"]}

    out = {"projects": {}}

    # ------------------------------------------------ per-project quantities
    for name, pr in probe.items():
        rec = {"commit_side_rate": pr["rate_multi"],
               "commits_scanned": pr["commits_scanned"],
               "passes_bar": pr["passes_bar"]}

        d = clone_depth(args.work, name, pr["head_sha"])
        rec["depth"] = d
        if d and d["commits_at_pinned_sha"] != pr["commits_scanned"]:
            rec["depth_mismatch_vs_probe"] = True

        # live arm: exact tickets, exact TRR
        if name in live:
            t = live[name]["jira_tickets_total"]
            trr = live[name]["ticket_side_rate"]
            ceil = pr["rate_multi"] * pr["commits_scanned"] / t
            rec["live"] = {
                "tickets": t, "trr": trr,
                "commits_per_ticket": pr["commits_scanned"] / t,
                "ceiling": ceil,
                "fill": trr / ceil if ceil else None,
                "ceiling_binds": ceil < 1.0,
            }

        # frozen arm
        e = ext.get(name)
        if e and e["ticket_side_frozen"] is not None and e["frozen_denominator"]:
            t = e["frozen_denominator"]
            trr = e["ticket_side_frozen"]
            ceil = pr["rate_multi"] * pr["commits_scanned"] / t
            rec["frozen"] = {
                "tickets": t, "trr": trr,
                "commits_per_ticket": pr["commits_scanned"] / t,
                "ceiling": ceil,
                "fill": trr / ceil if ceil else None,
                "ceiling_binds": ceil < 1.0,
                "small_denominator": e["small_denominator"],
                "share_cited_above_snapshot": e["share_cited_above_frozen_range"],
            }
        out["projects"][name] = rec

    P = out["projects"]

    # ------------------------------------------------ medians, done properly
    def med(vals):
        return statistics.median(vals) if vals else None
    fr = [(n, P[n]["frozen"]["trr"]) for n in P
          if "frozen" in P[n] and not P[n]["frozen"]["small_denominator"]]
    passing = [v for n, v in fr if P[n]["passes_bar"]]
    dropped = [v for n, v in fr if not P[n]["passes_bar"]]
    out["medians"] = {
        "method": "statistics.median (mean of the two middle values at even n)",
        "passing_n": len(passing), "passing_median": med(passing),
        "dropped_n": len(dropped), "dropped_median": med(dropped),
        "gap_pp": (med(passing) - med(dropped)) * 100,
        "published_passing_median_v_len_over_2": sorted(passing)[len(passing) // 2],
        "passing_median_excluding_kylin": med([v for n, v in fr
                                               if P[n]["passes_bar"] and n != "kylin"]),
    }

    # ------------------------------------------------ inference on the frozen rho
    xs = [P[n]["commit_side_rate"] for n, _ in fr]
    ys = [v for _, v in fr]
    rho = spearman(xs, ys)
    lo, hi = fisher_ci(rho, len(xs))
    out["frozen_association"] = {
        "n": len(xs), "spearman": rho, "ci95": [lo, hi],
        "permutation_p_two_sided": perm_p(xs, ys),
        "detectable_at_80pc_power": detectable_rho(len(xs)),
        "projects": [n for n, _ in fr],
    }

    # ------------------------------------------------ the direction tension
    lv = [(n, P[n]["commit_side_rate"], P[n]["live"]["trr"]) for n in P if "live" in P[n]]
    lx = [r[1] for r in lv]; ly = [r[2] for r in lv]
    rho_l = spearman(lx, ly)
    lo_l, hi_l = fisher_ci(rho_l, len(lx))
    out["live_association"] = {
        "n": len(lx), "spearman": rho_l, "ci95": [lo_l, hi_l],
        "permutation_p_two_sided": perm_p(lx, ly),
        "detectable_at_80pc_power": detectable_rho(len(lx)),
        "projects": [r[0] for r in lv],
        "commit_side_spread_ratio": max(lx) / min(lx),
        "commits_per_ticket_spread_ratio": (
            max(P[n]["live"]["commits_per_ticket"] for n, _, _ in lv) /
            min(P[n]["live"]["commits_per_ticket"] for n, _, _ in lv)),
    }
    # same, on the frozen arm, for a like-for-like spread comparison
    fx = [P[n]["commit_side_rate"] for n, _ in fr]
    out["frozen_association"]["commit_side_spread_ratio"] = max(fx) / min(fx) if min(fx) else None
    cpt = [P[n]["frozen"]["commits_per_ticket"] for n, _ in fr]
    out["frozen_association"]["commits_per_ticket_spread_ratio"] = max(cpt) / min(cpt)

    # ------------------------------------------------ estimator, end to end
    rows = []
    for n in P:
        e = ext.get(n)
        if not e or "live" not in e:
            continue
        pub = e["live"]["ticket_side_published"]
        rows.append({
            "project": n,
            "published_exact_live": pub,
            "number_capped_live": e["live"]["ticket_side_estimated"],
            "number_capped_frozen": e["ticket_side_frozen"],
            "err_number_capping_pp": abs(e["live"]["ticket_side_estimated"] - pub) * 100,
            "err_end_to_end_pp": abs(e["ticket_side_frozen"] - pub) * 100,
        })
    rows.sort(key=lambda r: -r["err_end_to_end_pp"])
    nc = [r["err_number_capping_pp"] for r in rows]
    ee = [r["err_end_to_end_pp"] for r in rows]
    ex_k = [r["err_end_to_end_pp"] for r in rows if r["project"] != "kylin"]
    out["estimator"] = {
        "n": len(rows),
        "number_capping_only": {"mean_pp": sum(nc) / len(nc), "max_pp": max(nc),
                                "worst": rows[0]["project"] if False else
                                max(rows, key=lambda r: r["err_number_capping_pp"])["project"]},
        "end_to_end": {"mean_pp": sum(ee) / len(ee), "max_pp": max(ee),
                       "worst": rows[0]["project"],
                       "mean_pp_excluding_worst": sum(ex_k) / len(ex_k),
                       "max_pp_excluding_worst": max(ex_k),
                       "n_within_3pp": sum(1 for v in ee if v <= 3.0)},
        "ratio_mean": (sum(ee) / len(ee)) / (sum(nc) / len(nc)),
        "ratio_max": max(ee) / max(nc),
        "rows": rows,
        "validated_commit_side_range": [min(P[r["project"]]["commit_side_rate"] for r in rows),
                                        max(P[r["project"]]["commit_side_rate"] for r in rows)],
    }
    applied = [P[n]["commit_side_rate"] for n, _ in fr if n not in {r["project"] for r in rows}]
    v0, v1 = out["estimator"]["validated_commit_side_range"]
    out["estimator"]["applied_only_commit_side_range"] = [min(applied), max(applied)]
    out["estimator"]["applied_inside_validated_range"] = sum(1 for a in applied if v0 <= a <= v1)
    out["estimator"]["applied_n"] = len(applied)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)

    # ------------------------------------------------ report
    m = out["medians"]
    print(f"MEDIANS  passing n={m['passing_n']} median={m['passing_median']*100:.2f}% "
          f"(published used v[n//2] = {m['published_passing_median_v_len_over_2']*100:.2f}%)")
    print(f"         dropped n={m['dropped_n']} median={m['dropped_median']*100:.2f}%  "
          f"gap={m['gap_pp']:+.2f}pp")
    print(f"         passing median excluding kylin = "
          f"{m['passing_median_excluding_kylin']*100:.2f}%")
    for k in ("frozen_association", "live_association"):
        a = out[k]
        print(f"\n{k}: n={a['n']} rho={a['spearman']:+.4f} "
              f"CI95=[{a['ci95'][0]:+.3f},{a['ci95'][1]:+.3f}] "
              f"perm p={a['permutation_p_two_sided']:.3f} "
              f"detectable@80%={a['detectable_at_80pc_power']:.3f}")
        print(f"    CSR spread {a['commit_side_spread_ratio']:.2f}x   "
              f"commits/ticket spread {a['commits_per_ticket_spread_ratio']:.2f}x")
    e = out["estimator"]
    print(f"\nESTIMATOR n={e['n']}")
    print(f"  number-capping only : mean {e['number_capping_only']['mean_pp']:.2f}pp "
          f"max {e['number_capping_only']['max_pp']:.2f}pp ({e['number_capping_only']['worst']})")
    print(f"  END TO END          : mean {e['end_to_end']['mean_pp']:.2f}pp "
          f"max {e['end_to_end']['max_pp']:.2f}pp ({e['end_to_end']['worst']})")
    print(f"     excluding {e['end_to_end']['worst']}: mean "
          f"{e['end_to_end']['mean_pp_excluding_worst']:.2f}pp "
          f"max {e['end_to_end']['max_pp_excluding_worst']:.2f}pp; "
          f"{e['end_to_end']['n_within_3pp']} of {e['n']} within 3pp")
    print(f"  ratio mean {e['ratio_mean']:.1f}x  max {e['ratio_max']:.1f}x")
    print(f"  validated CSR range {e['validated_commit_side_range'][0]*100:.1f}-"
          f"{e['validated_commit_side_range'][1]*100:.1f}%   applied-only "
          f"{e['applied_only_commit_side_range'][0]*100:.1f}-"
          f"{e['applied_only_commit_side_range'][1]*100:.1f}%   "
          f"overlap {e['applied_inside_validated_range']} of {e['applied_n']}")

    print("\nTRUNCATED DEFAULT BRANCHES (pinned branch starts after the repository does):")
    for n in sorted(P):
        d = P[n].get("depth")
        if d and d["branch_starts_after_repo"]:
            print(f"  {n:26s} pinned {d['commits_at_pinned_sha']:6,d} of "
                  f"{d['commits_all_refs']:6,d} all-refs "
                  f"({d['pinned_share_of_all_refs']*100:4.1f}%)  branch "
                  f"{d['first_commit_on_pinned_branch']} .. {d['last_commit_on_pinned_branch']}  "
                  f"repo from {d['first_commit_any_ref']}")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
