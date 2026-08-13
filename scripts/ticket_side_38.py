#!/usr/bin/env python3
"""
ticket_side_38.py — extend the ticket-side rate to all 38 probed projects.

`scripts/ticket_coverage.py` computed the ticket-side rate for the 12 projects
that cleared the 0.80 commit-side bar, by fetching every issue key from the live
Apache Jira. `paper/numbers.md` §1c flags the consequence in bold: the resulting
12.0–69.0% range is WITHIN-PASSING variation and licenses nothing about the 26
projects below the bar, whose ticket-side rates were never measured. This closes
that gap.

WHY THIS DOES NOT FETCH JIRA. The repository's standing rule is that Jira is
live, a re-fetch returns different state, and the frozen archive is the only
admissible source. A second live sweep would also date the 26 new denominators
three weeks after the 12 existing ones, so the extended table would not be
internally comparable. Instead the denominator comes from the frozen Public Jira
Dataset (Zenodo 15719919) as already parsed into `estimates_by_org.json`, which
carries an issue count for 646 Apache projects.

THE SNAPSHOT PROBLEM, AND HOW IT IS HANDLED. That dataset is an older snapshot
than the pinned git HEADs: Ozone's tracker holds 6,121 issues in the dataset and
15,909 in the 2026 live fetch. Dividing a 2026 numerator by a snapshot
denominator would produce rates above 100%. Both sides are therefore aligned in
ISSUE-NUMBER space rather than in time. Jira numbers issues sequentially from 1
within a project, so a tracker holding N issues at the snapshot holds
approximately the first N numbers; the numerator counts only cited keys whose
number is <= N. Every ticket in the denominator has then had until the pinned
HEAD -- years, not weeks -- to receive a commit, so the numerator is not
right-censored against its own denominator.

That approximation is validated, not assumed: for the 12 projects the same
estimator is run against the live totals in `paper/ticket_coverage.json` and
compared with the published exact rate, which was computed by intersecting with
the real key set rather than by capping numbers.

READS COMMIT MESSAGES ONLY. Same restriction as `traceability_probe.py`: no
diffs, no timestamps beyond the pinned sha, no Jira API, no outcome data. A
ticket-side coverage count says nothing about how long anything took, so this is
safe over the held-out corpus.

Usage:
    python3 scripts/ticket_side_38.py --work <dir of bare clones> \
        --out paper/ticket_side_38.json
"""
import argparse, json, os, re, statistics, subprocess, sys
from collections import defaultdict

PROBE = "paper/traceability_probe.json"
LIVE = "paper/ticket_coverage.json"
FROZEN = "estimates_by_org.json"

# repo -> the Jira project key whose tickets form the published denominator.
# Taken from scripts/ticket_coverage.py so the validation compares like with
# like; the remaining 26 use the first key of their probed key set.
PRIMARY = {
    "ozone": "HDDS", "tez": "TEZ", "hive": "HIVE", "hbase": "HBASE",
    "phoenix": "PHOENIX", "zookeeper": "ZOOKEEPER", "ranger": "RANGER",
    "oozie": "OOZIE", "knox": "KNOX", "drill": "DRILL", "kylin": "KYLIN",
    "sqoop": "SQOOP",
}


def clone_path(work, name):
    for cand in (os.path.join(work, f"{name}.git"), os.path.join(work, name)):
        if os.path.isdir(cand):
            return cand
    return None


# A partial clone will silently reach out to its promisor remote for any object
# it is missing, which turns "this clone is incomplete" into a network stall
# instead of an error. Nothing here should ever touch the network.
ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")


def cited_numbers(repo, rev, keys):
    """{key prefix: set of issue numbers} cited anywhere in the commit messages."""
    pat = re.compile(rf"\b({'|'.join(re.escape(k) for k in keys)})-(\d+)\b")
    cmd = ["git", "-C", repo, "log", "--pretty=format:%s%n%b", rev]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True,
                         env=ENV, timeout=600).stdout
    found = defaultdict(set)
    for m in pat.finditer(out):
        found[m.group(1)].add(int(m.group(2)))
    return found


def commits_at(repo, rev):
    out = subprocess.run(["git", "-C", repo, "rev-list", "--count", rev],
                         capture_output=True, text=True, check=True,
                         env=ENV, timeout=600).stdout
    return int(out.strip())


def rate(numbers, n):
    """Cited keys numbered <= n, over n."""
    if not n:
        return None, 0
    hit = sum(1 for x in numbers if x <= n)
    return hit / n, hit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="paper/ticket_side_38.json")
    ap.add_argument("--table", default="paper/table3_ticket_side.md")
    args = ap.parse_args()

    probe = json.load(open(PROBE))["projects"]
    live = {r["project"]: r for r in json.load(open(LIVE))["projects"]}
    frozen_all = json.load(open(FROZEN))["projects"]
    frozen = {k.split("|", 1)[1]: v["total"]
              for k, v in frozen_all.items() if k.startswith("Apache|")}

    out = {
        "denominator_source": {
            "frozen": f"{FROZEN} -> Apache|<KEY>.total (Zenodo 15719919, "
                      f"{json.load(open(FROZEN))['validation']['issues_parsed']} "
                      f"issues parsed)",
            "live": f"{LIVE} (Apache Jira REST, keys only, 2026-07-25) — 12 projects",
        },
        "estimator": "|{cited own-project keys with number <= N}| / N",
        "projects": [],
        "missing_clones": [],
    }

    for r in probe:
        name = r["project"]
        repo = clone_path(args.work, name)
        if repo is None:
            out["missing_clones"].append(name)
            print(f"{name:26s} clone missing — skipped", file=sys.stderr)
            continue
        keys = r["keys_multi"].split(",")
        sha = r["head_sha"]
        try:
            nums = cited_numbers(repo, sha, keys)
            n_commits = commits_at(repo, sha)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            out["missing_clones"].append(name)
            print(f"{name:26s} pinned sha unreachable: {e}", file=sys.stderr)
            continue

        per_key = {}
        for k in keys:
            got = nums.get(k, set())
            n_frozen = frozen.get(k)
            tau_f, hit_f = rate(got, n_frozen) if n_frozen else (None, 0)
            per_key[k] = {
                "distinct_keys_cited": len(got),
                "max_number_cited": max(got) if got else 0,
                "tracker_issues_frozen": n_frozen,
                "cited_within_frozen_range": hit_f,
                "ticket_side_frozen": tau_f,
            }

        prim = PRIMARY.get(name, keys[0])
        rec = {
            "project": name,
            "head_sha": sha,
            "commits_at_pinned_sha": n_commits,
            "commits_scanned_in_probe": r["commits_scanned"],
            "commit_side_rate": r["rate_multi"],
            "passes_bar": r["passes_bar"],
            "drop_reason": r["drop_reason"],
            "keys_probed": keys,
            "primary_key": prim,
            "per_key": per_key,
            "keys_with_no_tracker_record": [k for k in keys if k not in frozen],
        }

        # aggregate over the keys that have a tracker record at all
        num = sum(per_key[k]["cited_within_frozen_range"] for k in keys
                  if per_key[k]["tracker_issues_frozen"])
        den = sum(per_key[k]["tracker_issues_frozen"] for k in keys
                  if per_key[k]["tracker_issues_frozen"])
        rec["ticket_side_frozen"] = num / den if den else None
        rec["frozen_numerator"], rec["frozen_denominator"] = num, den

        # Diagnostic, not decoration. If most cited keys are numbered ABOVE the
        # snapshot's issue count, the repository at the pinned sha barely
        # overlaps the ticket population the denominator describes -- which is
        # what a truncated or rewritten git history looks like from here.
        cited_all = sum(len(nums.get(k, set())) for k in keys)
        rec["distinct_keys_cited_total"] = cited_all
        rec["cited_above_frozen_range"] = cited_all - num
        rec["share_cited_above_frozen_range"] = (
            (cited_all - num) / cited_all if cited_all else None)
        rec["small_denominator"] = bool(den and den < 500)

        # The arithmetic ceiling. A commit that cites a ticket adds at most one
        # NEW distinct ticket to the numerator, so cited_tickets <= CSR*commits
        # and therefore TRR <= CSR * commits / tickets. `fill` is the share of
        # that attainable maximum actually reached -- the part of TRR that is
        # NOT explained by how many commits the project has per ticket.
        if den:
            rec["commits_per_ticket"] = r["commits_scanned"] / den
            rec["ceiling"] = r["rate_multi"] * r["commits_scanned"] / den
            rec["fill"] = (rec["ticket_side_frozen"] / rec["ceiling"]
                           if rec["ceiling"] else None)
        else:
            rec["commits_per_ticket"] = rec["ceiling"] = rec["fill"] = None

        # validation arm: same estimator, live denominator, primary key only
        if name in live:
            n_live = live[name]["jira_tickets_total"]
            tau_l, hit_l = rate(nums.get(prim, set()), n_live)
            rec["live"] = {
                "tracker_issues_live": n_live,
                "cited_within_live_range": hit_l,
                "ticket_side_estimated": tau_l,
                "ticket_side_published": live[name]["ticket_side_rate"],
                "delta_pp": (tau_l - live[name]["ticket_side_rate"]) * 100,
                "published_distinct_keys_cited": live[name].get("distinct_keys_cited"),
                "published_cited_keys_not_in_jira": live[name].get("cited_keys_not_in_jira"),
            }
        out["projects"].append(rec)

        tf = rec["ticket_side_frozen"]
        print(f"{name:26s} commit-side {r['rate_multi']*100:5.1f}%  "
              f"ticket-side(frozen) "
              f"{('%5.1f%%' % (tf*100)) if tf is not None else '  n/a'}  "
              f"[{num:,}/{den:,}]"
              + (f"  live est {rec['live']['ticket_side_estimated']*100:5.1f}% "
                 f"vs published {rec['live']['ticket_side_published']*100:5.1f}% "
                 f"(Δ{rec['live']['delta_pp']:+.1f}pp)" if name in live else ""))
        sys.stdout.flush()
        json.dump(out, open(args.out, "w"), indent=1)

    # ---- taxonomy mode 6, measured across the whole probe ---------------------
    # A key that commit messages cite and the tracker has no project record for
    # exists only in git. Enumerating the tracker cannot recover it.
    orphans = []
    for p in out["projects"]:
        for k in p["keys_with_no_tracker_record"]:
            orphans.append({"project": p["project"], "key": k,
                            "distinct_keys_cited": p["per_key"][k]["distinct_keys_cited"]})
    out["orphan_keys"] = {
        "n_keys": len(orphans),
        "n_keys_actually_cited": sum(1 for o in orphans if o["distinct_keys_cited"]),
        "n_projects_affected": len({o["project"] for o in orphans
                                    if o["distinct_keys_cited"]}),
        "keys": sorted(orphans, key=lambda o: -o["distinct_keys_cited"]),
    }
    o = out["orphan_keys"]
    print(f"\nprobed keys with no project record in the frozen tracker corpus: "
          f"{o['n_keys']} ({o['n_keys_actually_cited']} of them actually cited, "
          f"across {o['n_projects_affected']} projects)")
    for row in o["keys"]:
        if row["distinct_keys_cited"]:
            print(f"    {row['project']:26s} {row['key']:12s} "
                  f"{row['distinct_keys_cited']:5,d} distinct keys cited")

    # ---- the question the extension exists to answer -------------------------
    # Does a high commit-side rate predict a usable ticket-side rate? Spearman,
    # because neither rate is normal and the relationship need not be linear.
    usable = [p for p in out["projects"]
              if p["ticket_side_frozen"] is not None and not p["small_denominator"]]
    def spearman(xs, ys):
        def ranks(v):
            order = sorted(range(len(v)), key=lambda i: v[i])
            r = [0.0] * len(v)
            i = 0
            while i < len(order):                 # average ties
                j = i
                while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                    j += 1
                avg = (i + j) / 2 + 1
                for k in range(i, j + 1):
                    r[order[k]] = avg
                i = j + 1
            return r
        rx, ry = ranks(xs), ranks(ys)
        n = len(xs)
        mx, my = sum(rx) / n, sum(ry) / n
        num_ = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
        den_ = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
        return num_ / den_ if den_ else None
    cs = [p["commit_side_rate"] for p in usable]
    tsf = [p["ticket_side_frozen"] for p in usable]
    passing = [p for p in usable if p["passes_bar"]]
    dropped = [p for p in usable if not p["passes_bar"]]
    def rng(ps):
        # statistics.median, not v[len(v)//2]. The latter returns the UPPER of
        # the two middle values at even n and was wrong for the 12-project
        # passing group: it gave 55.53% where the median is 52.60%.
        v = sorted(p["ticket_side_frozen"] for p in ps)
        return {"n": len(v), "min": v[0] if v else None, "max": v[-1] if v else None,
                "median": statistics.median(v) if v else None,
                "median_upper_middle_legacy": v[len(v) // 2] if v else None}
    out["association"] = {
        "n_with_usable_denominator": len(usable),
        "excluded_small_denominator": [p["project"] for p in out["projects"]
                                       if p["small_denominator"]],
        "excluded_no_tracker_record": [p["project"] for p in out["projects"]
                                       if p["ticket_side_frozen"] is None],
        "spearman_commit_side_vs_ticket_side": spearman(cs, tsf),
        "passing": rng(passing),
        "dropped": rng(dropped),
        "dropped_above_worst_passing": sorted(
            p["project"] for p in dropped
            if passing and p["ticket_side_frozen"] > min(
                q["ticket_side_frozen"] for q in passing)),
        # The worst passing project is Kylin, whose rate the paper itself calls
        # a truncation artifact, so "higher than the worst passing one" invites
        # the objection that it rests on that artifact. Recompute the same
        # comparison against the worst passing project OTHER than the weakest,
        # so the claim can be stated with its own robustness attached.
        "dropped_above_second_worst_passing": sorted(
            p["project"] for p in dropped
            if len(passing) > 1 and p["ticket_side_frozen"] > sorted(
                q["ticket_side_frozen"] for q in passing)[1]),
        "second_worst_passing": (
            sorted(passing, key=lambda q: q["ticket_side_frozen"])[1]["project"]
            if len(passing) > 1 else None),
        "second_worst_passing_rate": (
            sorted(q["ticket_side_frozen"] for q in passing)[1]
            if len(passing) > 1 else None),
    }
    # Sensitivity: drop the projects where most cited keys postdate the snapshot.
    # For those the repository barely overlaps the ticket population the
    # denominator describes, so the rate is about a truncated history rather than
    # about traceability, and it belongs outside the association.
    FLAG = 0.5
    keep = [p for p in usable
            if (p["share_cited_above_frozen_range"] or 0) <= FLAG]
    out["association"]["sensitivity_excluding_truncated_history"] = {
        "threshold_share_cited_above_snapshot": FLAG,
        "excluded": sorted(p["project"] for p in usable if p not in keep),
        "n": len(keep),
        "spearman": spearman([p["commit_side_rate"] for p in keep],
                             [p["ticket_side_frozen"] for p in keep]),
        "passing": rng([p for p in keep if p["passes_bar"]]),
        "dropped": rng([p for p in keep if not p["passes_bar"]]),
    }
    s = out["association"]["sensitivity_excluding_truncated_history"]

    a = out["association"]
    print(f"\ncommit-side vs ticket-side, {a['n_with_usable_denominator']} projects "
          f"with a usable denominator: Spearman rho = "
          f"{a['spearman_commit_side_vs_ticket_side']:+.3f}")
    print(f"  passing bar (n={a['passing']['n']}): ticket-side "
          f"{a['passing']['min']*100:.1f}–{a['passing']['max']*100:.1f}%, "
          f"median {a['passing']['median']*100:.1f}%")
    print(f"  dropped     (n={a['dropped']['n']}): ticket-side "
          f"{a['dropped']['min']*100:.1f}–{a['dropped']['max']*100:.1f}%, "
          f"median {a['dropped']['median']*100:.1f}%")
    print(f"  dropped projects above the worst passing project: "
          f"{len(a['dropped_above_worst_passing'])}")
    print(f"  sensitivity, excluding {len(s['excluded'])} truncated-history cases "
          f"({', '.join(s['excluded'])}): n={s['n']}, rho={s['spearman']:+.3f}, "
          f"passing median {s['passing']['median']*100:.1f}%, "
          f"dropped median {s['dropped']['median']*100:.1f}%")

    # validation summary
    val = [p["live"] for p in out["projects"] if "live" in p]
    if val:
        d = [abs(v["delta_pp"]) for v in val]
        ee = [(q["project"], abs(q["ticket_side_frozen"] -
                                 q["live"]["ticket_side_published"]) * 100)
              for q in out["projects"] if "live" in q]
        ee.sort(key=lambda r: -r[1])
        csr_val = [q["commit_side_rate"] for q in out["projects"] if "live" in q]
        csr_app = [q["commit_side_rate"] for q in out["projects"]
                   if "live" not in q and q["ticket_side_frozen"] is not None
                   and not q["small_denominator"]]
        lo_v, hi_v = min(csr_val), max(csr_val)
        out["validation"] = {
            "n": len(val),
            "mean_abs_delta_pp": sum(d) / len(d),
            "max_abs_delta_pp": max(d),
            "worst": max(val, key=lambda v: abs(v["delta_pp"])),
            # The figures above validate ONE of the two approximations in play.
            # These validate the combination this table actually uses.
            "end_to_end_mean_pp": sum(x for _, x in ee) / len(ee),
            "end_to_end_max_pp": ee[0][1],
            "end_to_end_worst": ee[0][0],
            "end_to_end_within_3pp": sum(1 for _, x in ee if x <= 3.0),
            "end_to_end_max_excl_worst_pp": max(x for _, x in ee[1:]),
            "validated_csr_range": [lo_v, hi_v],
            "applied_csr_range": [min(csr_app), max(csr_app)],
            "applied_n": len(csr_app),
            "applied_inside_validated": sum(1 for a in csr_app if lo_v <= a <= hi_v),
        }
        print(f"\nvalidation on {len(val)} projects with a published exact rate: "
              f"mean |Δ| {sum(d)/len(d):.2f}pp, max {max(d):.2f}pp")
    json.dump(out, open(args.out, "w"), indent=1)
    if args.table:
        write_table(out, args.table)
        print(f"Wrote {args.table}")
    print(f"Wrote {args.out}")


def pct(x, places=1):
    """Percentages at one decimal, EXCEPT where that would render a non-zero
    value as 0.0. Kylin is 0.04% and ShardingSphere 0.01%; printing either as
    0.0% asserts an absence that the data does not contain."""
    if x is None:
        return "—"
    v = x * 100
    if v and round(v, places) == 0:
        return f"{v:.2f}%"
    return f"{v:.{places}f}%"


def write_table(out, path):
    V = out["validation"]
    """Table 3 — the extension, as a table the manuscript can reference."""
    rows = sorted(out["projects"], key=lambda r: -r["commit_side_rate"])
    a = out["association"]
    L = ["# Table 3 — ticket realisation rate across all 38 probed projects", "",
         "<!-- GENERATED by scripts/ticket_side_38.py. Do not edit by hand. -->", "",
         "Denominators come from the frozen public Jira corpus, not from a second "
         "live fetch; numerator and denominator are aligned in issue-number space "
         "(method §3.1.3).", "",
         "**Two validation figures, and the smaller one does not apply to this "
         "table.** Against the 12 projects with a published exact rate, "
         "number-capping alone is accurate to "
         f"{V['mean_abs_delta_pp']:.2f}pp mean / {V['max_abs_delta_pp']:.2f}pp "
         "max. But this table also substitutes a frozen snapshot for the live "
         "tracker, and the END-TO-END error of that combination is "
         f"**{V['end_to_end_mean_pp']:.2f}pp mean / {V['end_to_end_max_pp']:.2f}pp "
         f"max** ({V['end_to_end_worst']}), with {V['end_to_end_within_3pp']} of "
         f"12 within 3pp (worst of those {V['end_to_end_max_excl_worst_pp']:.2f}pp). "
         "**Quote the end-to-end figure for anything in this table.**", "",
         "**The estimator is applied entirely outside the range it was validated "
         "on.** The 12 validation projects span commit-side "
         f"{V['validated_csr_range'][0]*100:.1f}–{V['validated_csr_range'][1]*100:.1f}%; "
         f"the {V['applied_n']} projects that carry the association below span "
         f"{V['applied_csr_range'][0]*100:.1f}–{V['applied_csr_range'][1]*100:.1f}%. "
         f"The two ranges are **DISJOINT**: {V['applied_inside_validated']} of "
         f"{V['applied_n']} applied projects fall inside the validated range. Any "
         "claim resting on this table whose margin is smaller than "
         f"{V['end_to_end_max_pp']:.2f}pp is not safe on this estimator.", "",
         "**Ceiling and fill.** A commit citing a ticket adds at most one NEW "
         "distinct ticket, so TRR ≤ CSR × commits / tickets (method §3.1.4). "
         "`ceiling` is that bound; `TRR/ceiling` the share of it reached. A "
         "ceiling above 100% does not bind — it means the repository has more "
         "citing commits than the snapshot has tickets, which is what a 2026 "
         "commit window against an older tracker produces.", "",
         "| # | project | bar | commit-side | commits/ticket | ceiling | **ticket realisation** | TRR/ceiling | cited ≤ N | tracker N | note |",
         "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for i, r in enumerate(rows, 1):
        t = r["ticket_side_frozen"]
        note = []
        if r["ticket_side_frozen"] is None:
            note.append("no tracker record for the cited key")
        if r["small_denominator"]:
            note.append("denominator < 500, not usable")
        if (r["share_cited_above_frozen_range"] or 0) > 0.5:
            # Two decimals, not zero: 709 of 711 is 99.72%, and rounding it to
            # "100%" contradicts the non-zero numerator in the same row.
            note.append(f"{r['share_cited_above_frozen_range']*100:.2f}% of cited "
                        "keys postdate the snapshot")
        L.append(f"| {i} | {r['project']} | "
                 f"{'pass' if r['passes_bar'] else 'drop'} | "
                 f"{r['commit_side_rate']*100:.1f}% | "
                 f"{('%.2f' % r['commits_per_ticket']) if r.get('commits_per_ticket') else '—'} | "
                 f"{pct(r.get('ceiling'))} | "
                 f"{('**%s**' % pct(t)) if t is not None else '—'} | "
                 f"{('%.2f' % r['fill']) if r.get('fill') else '—'} | "
                 f"{r['frozen_numerator']:,} | {r['frozen_denominator']:,} | "
                 f"{'; '.join(note) or '—'} |")
    L += ["",
          f"**Association.** Over the {a['n_with_usable_denominator']} projects with "
          f"a usable denominator, Spearman rho between the commit-side rate and the "
          f"ticket realisation rate is **{a['spearman_commit_side_vs_ticket_side']:+.3f}**. "
          f"Projects clearing the bar (n={a['passing']['n']}) run "
          f"{a['passing']['min']*100:.1f}–{a['passing']['max']*100:.1f}% "
          f"(median {a['passing']['median']*100:.1f}%); projects the bar dropped "
          f"(n={a['dropped']['n']}) run {a['dropped']['min']*100:.1f}–"
          f"{a['dropped']['max']*100:.1f}% (median {a['dropped']['median']*100:.1f}%). "
          f"**{len(a['dropped_above_worst_passing'])} dropped projects have a higher "
          f"ticket realisation rate than the worst passing one**: "
          f"{', '.join(a['dropped_above_worst_passing']) or 'none'}. "
          f"The worst passing project is the one this paper calls a truncation "
          f"artifact, so the comparison is also run without it: against "
          f"{a['second_worst_passing']} at "
          f"{a['second_worst_passing_rate']*100:.1f}%, the next-worst passing "
          f"project, **{len(a['dropped_above_second_worst_passing'])} of "
          f"{a['dropped']['n']} dropped projects are still higher**. The claim "
          f"does not rest on the artifact.",
          "",
          "**Excluded from the association.** Denominator under 500 issues: "
          f"{', '.join(a['excluded_small_denominator']) or 'none'}. No tracker "
          f"record for the probed key at all: "
          f"{', '.join(a['excluded_no_tracker_record']) or 'none'} — these are "
          "taxonomy modes 1 and 6 rather than low rates, and scoring them would "
          "put a number where a category belongs.",
          "",
          "**Missing clones**, if any: "
          f"{', '.join(out['missing_clones']) or 'none'}.", ""]
    open(path, "w").write("\n".join(L))


if __name__ == "__main__":
    main()
