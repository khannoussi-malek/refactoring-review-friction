#!/usr/bin/env python3
"""
traceability_probe.py — the traceability sweep, as a machine-readable artifact.

paper/numbers.md flagged the 38-project table as the least traceable thing in
the repo: citation_rate.py prints to stdout, every rate was hand-transcribed
into markdown, and six projects' commit counts were lost when the clones were
deleted. This rebuilds the whole table from scratch and writes JSON.

It does not reimplement the scan. It imports `git_log` from citation_rate.py so
the two can never diverge.

READS COMMIT MESSAGES ONLY. No diffs, no timestamps beyond the HEAD sha, no
Jira API calls, no outcome data of any kind. That is what makes it safe to run
over the held-out projects: a citation rate says nothing about how long anything
took.

Clones are `--no-checkout`: the probe needs `git log` and nothing else, so a
working tree is pure cost. The original sweep cloned 22 working trees it never
needed.

Usage:
    python3 scripts/traceability_probe.py --work <dir> --out paper/traceability_probe.json
"""
import argparse, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_rate import git_log            # same scanner as the original probe

BAR = 0.80

# name, primary key, full multi-key set. Multi-key sets come from empirically
# scanning each repo's own commit messages for issue-key-shaped tokens, not from
# guessing: a single-key probe reads Hadoop as 26% when the true rate is 92%.
PROJECTS = [
    ("hive",                     "HIVE",      "HIVE"),
    ("hbase",                    "HBASE",     "HBASE"),
    ("flink",                    "FLINK",     "FLINK"),
    ("phoenix",                  "PHOENIX",   "PHOENIX"),
    ("drill",                    "DRILL",     "DRILL"),
    ("kylin",                    "KYLIN",     "KYLIN"),
    ("accumulo",                 "ACCUMULO",  "ACCUMULO"),
    ("atlas",                    "ATLAS",     "ATLAS"),
    ("calcite",                  "CALCITE",   "CALCITE,OPTIQ"),
    ("cxf",                      "CXF",       "CXF"),
    ("flume",                    "FLUME",     "FLUME"),
    ("helix",                    "HELIX",     "HELIX"),
    ("hudi",                     "HUDI",      "HUDI"),
    ("karaf",                    "KARAF",     "KARAF,FELIX"),
    ("knox",                     "KNOX",      "KNOX"),
    ("oozie",                    "OOZIE",     "OOZIE"),
    ("ozone",                    "HDDS",      "HDDS,OZONE"),
    ("parquet-java",             "PARQUET",   "PARQUET"),
    ("ranger",                   "RANGER",    "RANGER"),
    ("tez",                      "TEZ",       "TEZ"),
    ("tika",                     "TIKA",      "TIKA"),
    ("zookeeper",                "ZOOKEEPER", "ZOOKEEPER"),
    ("james-project",            "JAMES",     "JAMES,MAILBOX"),
    ("jena",                     "JENA",      "JENA"),
    ("oodt",                     "OODT",      "OODT"),
    ("pinot",                    "PINOT",     "PINOT,THIRDEYE"),
    ("sqoop",                    "SQOOP",     "SQOOP"),
    ("storm",                    "STORM",     "STORM"),
    ("struts",                   "WW",        "WW"),
    ("syncope",                  "SYNCOPE",   "SYNCOPE"),
    ("tomee",                    "TOMEE",     "TOMEE,OPENEJB"),
    ("wicket",                   "WICKET",    "WICKET"),
    ("zeppelin",                 "ZEPPELIN",  "ZEPPELIN"),
    ("dubbo",                    "DUBBO",     "DUBBO"),
    ("rocketmq",                 "ROCKETMQ",  "ROCKETMQ,RIP"),
    ("servicecomb-java-chassis", "SCB",       "SCB"),
    ("shardingsphere",           "RS",        "RS"),
    ("skywalking",               "SWIP",      "SWIP"),
]

# A GitHub-issue reference: "#1234", "GH-1234", or a merge-PR subject. Counting
# these turns the "reason" column from an assumption into a measurement.
GH_RE = re.compile(r"(?:\bGH-\d+\b|#\d{2,}\b)")


def clone(name, work, skip_clone=False):
    dest = os.path.join(work, name)
    url = f"https://github.com/apache/{name}.git"
    if not os.path.isdir(os.path.join(dest, ".git")):
        if skip_clone:
            raise FileNotFoundError(dest)
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout",
                        "--quiet", url, dest], check=True)
    return dest, url


def head_sha(repo):
    return subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def pattern(keys):
    return re.compile(rf"\b(?:{'|'.join(re.escape(k) for k in keys.split(','))})-\d+\b")


def probe(name, single, multi, work, skip_clone=False):
    repo, url = clone(name, work, skip_clone)
    p_single, p_multi = pattern(single), pattern(multi)
    total = n_single = n_multi = n_gh = 0
    for _sha, subj, body in git_log(repo, None):
        total += 1
        msg = f"{subj}\n{body}"
        if p_single.search(msg):
            n_single += 1
        if p_multi.search(msg):
            n_multi += 1
        if GH_RE.search(msg):
            n_gh += 1
    return _derive({
        "project": name,
        "clone_url": url,
        "head_sha": head_sha(repo),
        "commits_scanned": total,
        "key_single": single,
        "keys_multi": multi,
        "commits_citing_single": n_single,
        # Task 5b canonical names: both reference channels, every project.
        "jira_key_refs": n_multi,
        "github_issue_refs": n_gh,
    })


def _derive(r):
    """Rates are DERIVED, never stored pre-rounded.

    Storing round(rate, 4) and then formatting to 1dp double-rounds: knox is
    2694/3194 = 84.3456%, which round-4 turns into 0.8435 and a .1f format then
    renders as 84.4% -- while citation_rate.py, formatting the full-precision
    value once, prints 84.3%. That single artifact manufactured both of the
    "discrepancies" in the first sweep (knox and helix). Keep full precision and
    format exactly once, at the edge.
    """
    n = r["commits_scanned"] or 1
    r["rate_single"] = r["commits_citing_single"] / n
    r["rate_multi"] = r["jira_key_refs"] / n
    r["rate_github_issue"] = r["github_issue_refs"] / n
    r["passes_bar"] = r["rate_multi"] >= BAR
    r["bar"] = BAR
    # legacy alias kept so nothing already written breaks
    r["commits_citing_multi"] = r["jira_key_refs"]
    r["commits_citing_github_issue"] = r["github_issue_refs"]
    return r


def drop_reason(r):
    """Determinable from commit messages alone; otherwise null."""
    if r["passes_bar"]:
        return None
    if r["rate_github_issue"] > r["rate_multi"]:
        return "github_issue_references_dominate"
    if r["rate_multi"] >= 0.70:
        return "below_bar_narrowly"
    if r["rate_multi"] < 0.15:
        return "jira_effectively_unused"
    return "low_commit_message_hygiene"


def write_table(records, path):
    rows = sorted(records, key=lambda r: -r["rate_multi"])
    out = ["| # | project | HEAD | commits | single-key | multi-key | verdict | drop reason (measured) |",
           "|---|---|---|---:|---:|---:|---|---|"]
    for i, r in enumerate(rows, 1):
        out.append(
            f"| {i} | {r['project']} | `{r['head_sha'][:10]}` | {r['commits_scanned']:,} | "
            f"{r['rate_single']*100:.1f}% | **{r['rate_multi']*100:.1f}%** | "
            f"{'pass' if r['passes_bar'] else 'drop'} | {r['drop_reason'] or '—'} |")
    n_pass = sum(1 for r in rows if r["passes_bar"])
    out.append(f"\n**{n_pass} of {len(rows)} pass the {BAR:.2f} bar.**")
    open(path, "w").write("\n".join(out) + "\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="scratch dir for --no-checkout clones")
    ap.add_argument("--out", default="paper/traceability_probe.json")
    ap.add_argument("--table", default="paper/traceability_table.md")
    ap.add_argument("--only", default=None)
    ap.add_argument("--skip-clone", action="store_true",
                    help="probe only what is already on disk")
    ap.add_argument("--refresh", action="store_true",
                    help="re-probe projects already in the output file")
    args = ap.parse_args()
    os.makedirs(args.work, exist_ok=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    # Resumable: merge into whatever is already recorded, keyed by project, so
    # the sweep can be run repeatedly while clones are still arriving.
    existing = {}
    if os.path.exists(args.out):
        for r in json.load(open(args.out))["projects"]:
            r.setdefault("jira_key_refs", r.get("commits_citing_multi"))
            r.setdefault("github_issue_refs", r.get("commits_citing_github_issue"))
            existing[r["project"]] = _derive(r)   # recompute rates at full precision

    records = list(existing.values())
    for name, single, multi in PROJECTS:
        if args.only and args.only != name:
            continue
        if name in existing and not args.refresh:
            continue
        try:
            r = probe(name, single, multi, args.work, args.skip_clone)
        except FileNotFoundError:
            print(f"{name:26s} not cloned yet — skipped", file=sys.stderr)
            continue
        except subprocess.CalledProcessError as e:
            print(f"{name:26s} CLONE/SCAN FAILED: {e}", file=sys.stderr)
            continue
        records = [x for x in records if x["project"] != name]
        r["drop_reason"] = drop_reason(r)
        records.append(r)
        print(f"{name:26s} n={r['commits_scanned']:6,d}  single={r['rate_single']*100:5.1f}%  "
              f"multi={r['rate_multi']*100:5.1f}%  gh={r['rate_github_issue']*100:5.1f}%  "
              f"{'PASS' if r['passes_bar'] else 'drop'}")
        sys.stdout.flush()
        order = {n: i for i, (n, _, _) in enumerate(PROJECTS)}
        records.sort(key=lambda x: order.get(x["project"], 999))
        json.dump({"bar": BAR, "n_probed": len(records), "projects": records},
                  open(args.out, "w"), indent=1)

    write_table(records, args.table)
    print(f"\nWrote {args.out} and {args.table}")


if __name__ == "__main__":
    main()
