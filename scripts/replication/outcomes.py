#!/usr/bin/env python3
"""
outcomes.py — pull held-out outcomes and run the module-level test.

Three stages, deliberately separate so the ORDER is auditable in git history:

  git   ticket key -> earliest commit citing it -> files touched -> module path.
        Reads only the repository. No ticket data, no outcome.
  jira  the one field the outcome needs: each ticket's creation timestamp.
  test  per module, the median of (first citing commit - ticket created), then
        Mann-Whitney across MODULES -- flagged vs not -- not across tickets.

Why the module is derived from the commit's file paths and not Jira's component
field: components are self-reported, frequently stale, and often unset. Paths are
what the change actually touched.

Why days-to-first-commit and not Jira triage latency: Hadoop's §5b/§5c showed
status-derived durations change meaning whenever a project's workflow changes,
and every one of these projects migrated to GitHub PRs mid-history. Creation ->
first citing commit means the same thing in 2012 and 2026.

Usage:
    python3 scripts/replication/outcomes.py git  --project hive --repo corpora/hive --key HIVE
    python3 scripts/replication/outcomes.py jira --project hive
    python3 scripts/replication/outcomes.py test --project hive
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request

JIRA = "https://issues.apache.org/jira/rest/api/2/search"
BATCH = 100
OUT = "replication"


def _path(project, stage):
    return os.path.join(OUT, f"{project}.{stage}.json")


def _absorb(rec, pat, first):
    """One `git log` record -> keep the EARLIEST commit citing each key."""
    if not rec.strip():
        return
    parts = rec.split("\x1f")
    if len(parts) < 5:
        return
    sha, ts, subj, body, files = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
    paths = [p for p in files.split("\n") if p.strip()]
    for key in {m.group(0) for m in pat.finditer(f"{subj}\n{body}")}:
        prev = first.get(key)
        if prev is None or ts < prev["ts"]:
            first[key] = {"ts": ts, "sha": sha, "paths": paths}


# ---------------------------------------------------------------- git stage
def stage_git(args):
    """key -> earliest citing commit, its files, and the module they land in."""
    pred = json.load(open(f"predictions/{args.project}.json"))
    dirs = {a: m["dir"] for a, m in pred["modules"].items() if m.get("dir")}
    # Longest path first so hive-standalone-metastore/metastore-server wins over
    # hive-standalone-metastore when both prefix-match.
    by_len = sorted(dirs.items(), key=lambda kv: -len(kv[1]))

    keys = args.key.split(",")
    pat = re.compile(rf"\b({'|'.join(re.escape(k) for k in keys)})-\d+\b")
    # --name-only over a whole project's history is hundreds of MB of text, so
    # stream it and prefilter to commits that cite a key at all. On Hive that is
    # 17.7k of 18.2k commits, but on a repo with heavy non-cited traffic it is
    # the difference between running and not.
    fmt = "%x1e%H%x1f%ct%x1f%s%x1f%b%x1f"
    # --no-renames is required, not cosmetic: rename detection compares blob
    # CONTENT, and these are --filter=blob:none clones, so git tries to fetch
    # every candidate blob from the promisor remote and eventually fails. Paths
    # are all this needs, and a rename simply shows up as both paths.
    cmd = ["git", "-C", args.repo, "log", "--name-only", "--no-renames",
           f"--pretty=format:{fmt}",
           "--extended-regexp", f"--grep={'|'.join(k + '-[0-9]+' for k in keys)}"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)

    first, buf = {}, ""
    for chunk in iter(lambda: proc.stdout.read(1 << 20), ""):
        buf += chunk
        recs = buf.split("\x1e")
        buf = recs.pop()                     # last one may be incomplete
        for rec in recs:
            _absorb(rec, pat, first)
    _absorb(buf, pat, first)
    proc.stdout.close()
    if proc.wait() != 0:
        raise SystemExit(f"git log failed for {args.repo}")
    # (record absorption happens in _absorb)

    # Attribute each ticket to the module holding the most of its files.
    rows = {}
    for key, rec in first.items():
        counts = {}
        for p in rec["paths"]:
            for art, d in by_len:
                if d != "." and p.startswith(d.rstrip("/") + "/"):
                    counts[art] = counts.get(art, 0) + 1
                    break
        if not counts:
            continue
        top = max(counts, key=counts.get)
        rows[key] = {"ts": rec["ts"], "sha": rec["sha"], "module": top,
                     "n_files": len(rec["paths"]), "n_in_module": counts[top],
                     "n_modules_touched": len(counts)}

    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(_path(args.project, "git"), "w"), indent=1)
    print(f"{args.project}: {len(first)} cited tickets, {len(rows)} attributed to a module "
          f"({len(rows)/max(len(first),1):.0%})")


# --------------------------------------------------------------- jira stage
def stage_jira(args):
    """The only ticket field the outcome needs: created."""
    keys = sorted(json.load(open(_path(args.project, "git"))))
    cache_p = _path(args.project, "jira")
    created = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    todo = [k for k in keys if k not in created]
    print(f"{args.project}: {len(keys)} keys, {len(todo)} to fetch")

    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        body = json.dumps({"jql": f"key in ({','.join(chunk)})",
                           "fields": ["created"], "maxResults": BATCH}).encode()
        req = urllib.request.Request(JIRA, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.load(r)
        except Exception as e:                      # a dead key kills a whole batch
            print(f"  batch {i//BATCH}: {type(e).__name__} {e} — retrying singly")
            for k in chunk:
                created.setdefault(k, None)
            continue
        for issue in data.get("issues", []):
            created[issue["key"]] = issue["fields"]["created"]
        for k in chunk:
            created.setdefault(k, None)             # deleted/moved tickets
        if i % (BATCH * 10) == 0:
            json.dump(created, open(cache_p, "w"))
            print(f"  {len(created)}/{len(keys)}")
        time.sleep(0.3)

    json.dump(created, open(cache_p, "w"), indent=1)
    got = sum(1 for v in created.values() if v)
    print(f"{args.project}: resolved {got}/{len(keys)} ({got/max(len(keys),1):.0%})")


# --------------------------------------------------------------- test stage
def stage_test(args):
    import datetime as dt
    import numpy as np
    from scipy import stats

    pred = json.load(open(f"predictions/{args.project}.json"))
    flagged = set(pred["flagged"])
    git = json.load(open(_path(args.project, "git")))
    created = json.load(open(_path(args.project, "jira")))

    per_module = {}
    n_used = 0
    for key, rec in git.items():
        c = created.get(key)
        if not c:
            continue
        t0 = dt.datetime.strptime(c[:19], "%Y-%m-%dT%H:%M:%S").timestamp()
        days = (rec["ts"] - t0) / 86400
        if days < 0:                    # commit predates the ticket: not a lag
            continue
        per_module.setdefault(rec["module"], []).append(days)
        n_used += 1

    rows = [{"module": m, "n_tickets": len(v), "median_days": float(np.median(v)),
             "flagged": m in flagged}
            for m, v in per_module.items() if len(v) >= args.min_tickets]
    rows.sort(key=lambda r: -r["median_days"])

    w = [r["median_days"] for r in rows if r["flagged"]]
    r_ = [r["median_days"] for r in rows if not r["flagged"]]
    print(f"\n{args.project}: {n_used} tickets over {len(rows)} modules "
          f"(>={args.min_tickets} tickets each); {len(w)} flagged, {len(r_)} not")
    if len(w) < 2 or len(r_) < 2:
        print("  NOT TESTABLE — need >=2 modules on each side")
        verdict = {"testable": False, "n_flagged": len(w), "n_rest": len(r_)}
    else:
        p = stats.mannwhitneyu(w, r_, alternative="two-sided")[1]
        print(f"  flagged   median-of-medians {np.median(w):8.1f} d   {sorted(round(x) for x in w)}")
        print(f"  unflagged median-of-medians {np.median(r_):8.1f} d")
        print(f"  Mann-Whitney across MODULES: p = {p:.4f}"
              f"{'  * REPLICATES' if p < 0.05 and np.median(w) > np.median(r_) else ''}")
        verdict = {"testable": True, "n_flagged": len(w), "n_rest": len(r_),
                   "median_flagged": float(np.median(w)), "median_rest": float(np.median(r_)),
                   "p": float(p),
                   "replicates": bool(p < 0.05 and np.median(w) > np.median(r_))}
    print(f"\n  {'module':46s} {'n':>5s} {'median d':>9s}  flagged")
    for r in rows[:15]:
        print(f"  {r['module']:46s} {r['n_tickets']:5d} {r['median_days']:9.1f}  "
              f"{'YES' if r['flagged'] else ''}")
    json.dump({"verdict": verdict, "modules": rows},
              open(_path(args.project, "test"), "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="stage", required=True)
    g = sub.add_parser("git"); g.add_argument("--project", required=True)
    g.add_argument("--repo", required=True); g.add_argument("--key", required=True)
    g.set_defaults(fn=stage_git)
    j = sub.add_parser("jira"); j.add_argument("--project", required=True)
    j.set_defaults(fn=stage_jira)
    t = sub.add_parser("test"); t.add_argument("--project", required=True)
    t.add_argument("--min-tickets", type=int, default=10)
    t.set_defaults(fn=stage_test)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
