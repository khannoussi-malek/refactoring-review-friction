#!/usr/bin/env python3
"""
flink_truncation.py — is the Flink 24.1pp gap against SEOSS 33 scope, or error?

`paper/numbers.md` §1b and `related.md` §2.1 assert that Flink's disagreement with
SEOSS 33 -- 41.98% there, 66.0% here -- is *scope*: their snapshot holds 12,419
commits against our 38,219, so we cover a decade in which Flink's citation
practice could have changed. Both places flag the claim as UNTESTED.
`paper/manuscript/UNSOURCED.md` lists it as item 2. This tests it.

TWO CHECKS, because Kylin taught us to run both.

1. CLONE DEPTH, the check that moved the paper's flagship example. Kylin's pinned
   sha turned out to reach 968 commits beginning 2022-08-01 -- 7.5% of its
   repository -- so its ticket-side rate was measured over a four-year window
   against a twelve-year tracker. If Flink's pinned sha is similarly truncated,
   the 66.0% is not a rate over Flink's history at all and the comparison with
   SEOSS is not a comparison of the same thing.

2. THE TRUNCATION TEST PROPER. Re-probe the EARLIEST 12,419 commits reachable
   from the pinned sha -- the same count SEOSS reports -- and compare with their
   41.98%. If the scope explanation holds, the early-window rate should land near
   41.98% and the difference is a decade of changed practice. If the early window
   is also near 66%, the explanation fails and the disagreement is a measurement
   difference that needs another account.

   Aligning on COMMIT COUNT rather than on a date is deliberate: SEOSS publishes
   a change-set count and not a cutoff date, so the count is the only quantity
   the two studies share.

Also sweeps all 38 probed projects for the Kylin signature, so the depth finding
is reported for the corpus rather than for one project at a time.

Reads commit messages and dates only. No Jira, no network.

Usage:
    python3 scripts/flink_truncation.py --work <dir of bare clones> \
        --out paper/flink_truncation.json
"""
import argparse, json, os, re, subprocess, sys

PROBE = "paper/traceability_probe.json"
SEOSS_FLINK_COMMITS = 12419      # SEOSS 33, Table 2, "Change Sets"
SEOSS_FLINK_RATE = 0.4198        # SEOSS 33, Table 2, "Linked Change Sets [%]"

ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, env=ENV, timeout=900)


def log_records(repo, rev):
    """(committer-date, message) oldest-first."""
    out = git(repo, "log", "--reverse", "--date=short",
              "--pretty=format:%ad%x1f%s%n%b%x1e", rev).stdout
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        f = rec.split("\x1f")
        if len(f) >= 2:
            yield f[0], f[1]


def depth(repo, sha):
    pinned = int(git(repo, "rev-list", "--count", sha).stdout.strip() or 0)
    allrefs = int(git(repo, "rev-list", "--count", "--all").stdout.strip() or 0)
    first = git(repo, "log", "--reverse", "--format=%ad", "--date=short",
                sha).stdout.split("\n", 1)[0].strip()
    last = git(repo, "log", "-1", "--format=%ad", "--date=short", sha).stdout.strip()
    first_all = git(repo, "log", "--reverse", "--format=%ad", "--date=short",
                    "--all").stdout.split("\n", 1)[0].strip()
    return {"commits_at_pinned_sha": pinned, "commits_all_refs": allrefs,
            "pinned_share_of_all_refs": pinned / allrefs if allrefs else None,
            "first_commit_on_pinned_branch": first,
            "last_commit_on_pinned_branch": last,
            "first_commit_any_ref": first_all,
            "branch_starts_after_repo": bool(first and first_all and first != first_all)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="paper/flink_truncation.json")
    args = ap.parse_args()

    probe = {p["project"]: p for p in json.load(open(PROBE))["projects"]}
    out = {"seoss_reference": {"project": "Flink", "commits": SEOSS_FLINK_COMMITS,
                               "linked_change_sets": SEOSS_FLINK_RATE,
                               "source": "Rath & Mäder 2019, SEOSS 33, Table 2"}}

    # ---------------- 1. clone depth, all 38 --------------------------------
    depths = {}
    for name, pr in probe.items():
        p = os.path.join(args.work, name + ".git")
        if not os.path.isdir(p):
            continue
        d = depth(p, pr["head_sha"])
        d["commits_scanned_in_probe"] = pr["commits_scanned"]
        d["probe_matches_pinned"] = d["commits_at_pinned_sha"] == pr["commits_scanned"]
        depths[name] = d
    out["clone_depth"] = depths
    out["truncated_branches"] = sorted(
        (n for n, d in depths.items() if d["branch_starts_after_repo"]),
        key=lambda n: depths[n]["pinned_share_of_all_refs"])

    # ---------------- 2. the truncation test on Flink ------------------------
    fl = os.path.join(args.work, "flink.git")
    if not os.path.isdir(fl):
        print("flink clone missing", file=sys.stderr)
        json.dump(out, open(args.out, "w"), indent=1)
        return
    keys = probe["flink"]["keys_multi"].split(",")
    pat = re.compile(rf"\b(?:{'|'.join(re.escape(k) for k in keys)})-\d+\b")

    recs = list(log_records(fl, probe["flink"]["head_sha"]))
    n = len(recs)
    hits = [bool(pat.search(m)) for _d, m in recs]

    def window(a, b):
        s = hits[a:b]
        return {"n": len(s), "citing": sum(s),
                "rate": sum(s) / len(s) if s else None,
                "first_date": recs[a][0] if s else None,
                "last_date": recs[min(b, n) - 1][0] if s else None}

    out["flink"] = {
        "head_sha": probe["flink"]["head_sha"],
        "commits_total": n,
        "rate_full": sum(hits) / n,
        "rate_published_in_probe": probe["flink"]["rate_multi"],
        # THE TEST: the earliest 12,419 commits, matching SEOSS's change-set count
        "earliest_seoss_window": window(0, SEOSS_FLINK_COMMITS),
        "remainder_after_seoss_window": window(SEOSS_FLINK_COMMITS, n),
        "by_year": {},
    }
    for y in range(int(recs[0][0][:4]), int(recs[-1][0][:4]) + 1):
        s = [h for (d, _m), h in zip(recs, hits) if d.startswith(str(y))]
        if s:
            out["flink"]["by_year"][str(y)] = {
                "n": len(s), "citing": sum(s), "rate": sum(s) / len(s)}

    w = out["flink"]["earliest_seoss_window"]
    out["flink"]["verdict"] = {
        "seoss_rate": SEOSS_FLINK_RATE,
        "our_rate_over_the_same_commit_count": w["rate"],
        "gap_pp": (w["rate"] - SEOSS_FLINK_RATE) * 100,
        "gap_pp_full_history": (out["flink"]["rate_full"] - SEOSS_FLINK_RATE) * 100,
        "scope_explanation_supported": abs(w["rate"] - SEOSS_FLINK_RATE) < 0.10,
    }

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)

    f = out["flink"]
    d = depths.get("flink", {})
    print("FLINK clone depth")
    print(f"  pinned sha reaches   : {d.get('commits_at_pinned_sha'):,} commits")
    print(f"  all refs             : {d.get('commits_all_refs'):,} "
          f"({d.get('pinned_share_of_all_refs', 0)*100:.1f}% on the pinned branch)")
    print(f"  pinned branch spans  : {d.get('first_commit_on_pinned_branch')} .. "
          f"{d.get('last_commit_on_pinned_branch')}")
    print(f"  repository begins    : {d.get('first_commit_any_ref')}")
    print(f"  truncated?           : {'YES' if d.get('branch_starts_after_repo') else 'NO'}")
    print("\nFLINK truncation test")
    print(f"  full history         : {sum(hits):,}/{n:,} = {f['rate_full']*100:.1f}%")
    print(f"  earliest {SEOSS_FLINK_COMMITS:,}      : {w['citing']:,}/{w['n']:,} = "
          f"{w['rate']*100:.1f}%   ({w['first_date']} .. {w['last_date']})")
    print(f"  SEOSS 33 reports     : {SEOSS_FLINK_RATE*100:.2f}% over {SEOSS_FLINK_COMMITS:,}")
    print(f"  gap on matched count : {f['verdict']['gap_pp']:+.1f}pp "
          f"(against {f['verdict']['gap_pp_full_history']:+.1f}pp on full history)")
    print(f"  scope explanation    : "
          f"{'SUPPORTED' if f['verdict']['scope_explanation_supported'] else 'NOT SUPPORTED'}")
    print("\n  by year:", "  ".join(f"{y}:{v['rate']*100:.0f}%"
                                    for y, v in sorted(f["by_year"].items())))
    print("\nTRUNCATED BRANCHES ACROSS THE 38")
    for nm in out["truncated_branches"]:
        dd = depths[nm]
        print(f"  {nm:16s} {dd['commits_at_pinned_sha']:6,d} / "
              f"{dd['commits_all_refs']:6,d} = {dd['pinned_share_of_all_refs']*100:5.1f}%  "
              f"branch from {dd['first_commit_on_pinned_branch']}, "
              f"repo from {dd['first_commit_any_ref']}")
    bad = [n_ for n_, dd in depths.items() if not dd["probe_matches_pinned"]]
    print(f"\nprobe commit count reproduced at the pinned sha for "
          f"{len(depths) - len(bad)} of {len(depths)}"
          + (f"; MISMATCH: {bad}" if bad else ""))
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
