#!/usr/bin/env python3
"""
springbatch_recency.py — mode 4, measured instead of sampled.

The taxonomy's worked example for "the convention changed mid-history" was
spring-batch, evidenced by `BATCH-` appearing in 4,046 of 7,034 commits overall
and in none of the 20 most recent commits sampled by hand.
`paper/manuscript/UNSOURCED.md` §9 recorded the obvious objection: the half of
that claim which establishes the convention CHANGED rested on a 20-commit hand
sample with no confidence interval, while the paper's own §5.5 recommends
computing a recent-history rate. This computes it.

Full scan of the default branch, no sampling, plus a per-year breakdown so the
shape of the change is visible rather than asserted.

The clone is a `--filter=tree:0 --bare` mirror; only commit messages are read.

Usage:
    git clone --filter=tree:0 --bare https://github.com/spring-projects/spring-batch.git sb.git
    python3 scripts/springbatch_recency.py --repo sb.git --out paper/springbatch_recency.json
"""
import argparse, json, os, re, subprocess

ENV = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
# BATCHADM is spring-batch-admin's key; both are scanned so the count cannot be
# accused of missing the project's second key.
KEYS = ("BATCH", "BATCHADM")
WINDOWS = (20, 100, 500, 1000, 2000)


def commits(repo, rev):
    out = subprocess.run(
        ["git", "-C", repo, "log", "--date=short",
         "--pretty=format:%H%x1f%ad%x1f%s%n%b%x1e", rev],
        capture_output=True, text=True, check=True, env=ENV, timeout=900).stdout
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        f = rec.split("\x1f")
        if len(f) >= 3:
            yield f[0], f[1], f[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--out", default="paper/springbatch_recency.json")
    args = ap.parse_args()

    pat = re.compile(rf"\b(?:{'|'.join(KEYS)})-\d+\b")
    rows = [(d, bool(pat.search(m))) for _s, d, m in commits(args.repo, args.rev)]
    rows_batch_only = None
    pat1 = re.compile(r"\bBATCH-\d+\b")
    rows_batch_only = [(d, bool(pat1.search(m)))
                       for _s, d, m in commits(args.repo, args.rev)]

    n = len(rows)
    head = subprocess.run(["git", "-C", args.repo, "rev-parse", args.rev],
                          capture_output=True, text=True, check=True,
                          env=ENV).stdout.strip()
    out = {
        "repo": "spring-projects/spring-batch", "head_sha": head,
        "keys_scanned": list(KEYS),
        "commits": n,
        "newest": rows[0][0], "oldest": rows[-1][0],
        "citing_any_key": sum(1 for _, c in rows if c),
        "citing_BATCH_only": sum(1 for _, c in rows_batch_only if c),
        "recent_windows": {}, "by_year": {},
    }
    out["overall_rate_any_key"] = out["citing_any_key"] / n
    out["overall_rate_BATCH_only"] = out["citing_BATCH_only"] / n

    for w in WINDOWS:
        s = rows[:w]
        out["recent_windows"][str(w)] = {
            "n": len(s), "citing": sum(1 for _, c in s if c),
            "rate": sum(1 for _, c in s if c) / len(s),
            "oldest_in_window": s[-1][0],
        }
    for y in range(int(rows[-1][0][:4]), int(rows[0][0][:4]) + 1):
        s = [c for d, c in rows if d.startswith(str(y))]
        if s:
            out["by_year"][str(y)] = {"n": len(s), "citing": sum(s),
                                      "rate": sum(s) / len(s)}

    # The last year in which the convention was used at all -- the change point,
    # located rather than asserted.
    used = [y for y, v in out["by_year"].items() if v["citing"]]
    out["last_year_convention_used"] = max(used) if used else None
    out["first_year_zero_after_use"] = None
    if used:
        for y in sorted(out["by_year"]):
            if y > max(used) and out["by_year"][y]["citing"] == 0:
                out["first_year_zero_after_use"] = y
                break

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)

    print(f"spring-batch @ {head[:10]}  {n:,} commits  {out['oldest']} .. {out['newest']}")
    print(f"  overall: {out['citing_any_key']:,} cite {'/'.join(KEYS)} = "
          f"{out['overall_rate_any_key']*100:.1f}%   "
          f"(BATCH- alone {out['overall_rate_BATCH_only']*100:.1f}%)")
    for w in WINDOWS:
        r = out["recent_windows"][str(w)]
        print(f"  most recent {w:5,d}: {r['citing']:5,d} = {r['rate']*100:5.1f}%  "
              f"(back to {r['oldest_in_window']})")
    print("  by year:", "  ".join(
        f"{y}:{v['rate']*100:.0f}%" for y, v in sorted(out["by_year"].items())
        if int(y) % 2 == 0))
    print(f"  last year the convention was used: {out['last_year_convention_used']}")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
