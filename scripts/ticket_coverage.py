#!/usr/bin/env python3
"""
ticket_coverage.py — the OTHER traceability rate.

`citation_rate.py` measures the commit side: of the commits, how many cite a
ticket? That is what the 0.80 bar is defined on. It says nothing about the
ticket side: of the project's tickets, how many are ever cited by a commit?

The two can diverge sharply. A project can have 97% of commits citing tickets
while most of its tickets never receive a commit at all -- filed, triaged,
abandoned. paper/numbers.md §4 flags exactly this as the open question behind
the "714/714, true by construction" claim.

=== HARD FIELD RESTRICTION ===

This fetches ISSUE KEYS ONLY. It must never touch created, resolutiondate,
status, changelog, or any other temporal field, because nine of these twelve
projects are a held-out corpus and observing an outcome spends them.

The restriction is enforced three ways, not merely intended:
  1. FIELDS is the literal list sent to the API and is asserted to be ["key"].
  2. Every response issue is screened against FORBIDDEN; a hit raises
     immediately rather than being filtered out quietly.
  3. Only the key string is ever retained -- the parsed issue object is
     discarded inside the loop and never reaches a data structure.

Key existence is not an outcome. Nothing here can be turned into a duration.

Usage:
    python3 scripts/ticket_coverage.py --work <clonedir> --out paper/ticket_coverage.json
"""
import argparse, json, os, re, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_rate import git_log

JIRA = "https://issues.apache.org/jira/rest/api/2/search"
FIELDS = ["key"]                      # the entire field list sent to the API
FORBIDDEN = {"created", "resolutiondate", "updated", "status", "changelog",
             "timeoriginalestimate", "timeestimate", "timespent", "resolution",
             "duedate", "lastViewed", "statuscategorychangedate", "aggregatetimespent"}
PAGE = 1000

# repo -> (Jira project key, key set used to scan commit messages)
PASSING = [
    ("ozone",     "HDDS",      "HDDS,OZONE"),
    ("tez",       "TEZ",       "TEZ"),
    ("hive",      "HIVE",      "HIVE"),
    ("hbase",     "HBASE",     "HBASE"),
    ("phoenix",   "PHOENIX",   "PHOENIX"),
    ("zookeeper", "ZOOKEEPER", "ZOOKEEPER"),
    ("ranger",    "RANGER",    "RANGER"),
    ("oozie",     "OOZIE",     "OOZIE"),
    ("knox",      "KNOX",      "KNOX"),
    ("drill",     "DRILL",     "DRILL"),
    ("kylin",     "KYLIN",     "KYLIN"),
    ("sqoop",     "SQOOP",     "SQOOP"),
]


def _screen(issue):
    """Fail loudly if the API ever hands back a field we must not see."""
    f = issue.get("fields") or {}
    leaked = FORBIDDEN & set(f)
    if leaked:
        raise SystemExit(f"FIELD RESTRICTION VIOLATED: API returned {sorted(leaked)} "
                         f"for {issue.get('key')}. Aborting rather than filtering.")


def fetch_keys(project):
    """Every issue key in a Jira project. Keys only — see the module docstring."""
    assert FIELDS == ["key"], "field list must remain keys-only"
    keys, start, total = set(), 0, None
    while True:
        body = json.dumps({"jql": f"project = {project} ORDER BY key ASC",
                           "fields": FIELDS, "startAt": start,
                           "maxResults": PAGE}).encode()
        req = urllib.request.Request(JIRA, data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
        total = data.get("total", 0)
        issues = data.get("issues", [])
        if not issues:
            break
        for issue in issues:
            _screen(issue)
            keys.add(issue["key"])       # only the key survives this loop
        start += len(issues)
        print(f"    {project}: {len(keys):,}/{total:,}", end="\r", flush=True)
        if start >= total:
            break
        time.sleep(0.2)
    print(" " * 40, end="\r")
    return keys, total


def cited_keys(repo, keyspec, project):
    """Distinct keys of THIS project cited by any commit message."""
    pat = re.compile(rf"\b(?:{'|'.join(re.escape(k) for k in keyspec.split(','))})-\d+\b")
    own = re.compile(rf"^{re.escape(project)}-\d+$")
    found, commits = set(), 0
    for _sha, subj, body in git_log(repo, None):
        commits += 1
        for m in pat.finditer(f"{subj}\n{body}"):
            k = m.group(0)
            if own.match(k):
                found.add(k)
    return found, commits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", default="paper/ticket_coverage.json")
    ap.add_argument("--probe", default="paper/traceability_probe.json")
    args = ap.parse_args()

    print(f"API field list sent on every request: {FIELDS}")
    print(f"Screened against: {sorted(FORBIDDEN)}\n")

    commit_side = {r["project"]: r for r in json.load(open(args.probe))["projects"]}
    out = {"api_fields_requested": FIELDS, "forbidden_fields_screened": sorted(FORBIDDEN),
           "jira": JIRA, "projects": []}

    for repo, proj, keyspec in PASSING:
        path = os.path.join(args.work, repo)
        if not os.path.isdir(os.path.join(path, ".git")):
            print(f"{repo:12s} clone missing — skipped")
            continue
        cited, n_commits = cited_keys(path, keyspec, proj)
        all_keys, total = fetch_keys(proj)
        matched = cited & all_keys
        rec = {
            "project": repo, "jira_project": proj,
            "jira_tickets_total": len(all_keys),
            "jira_reported_total": total,
            "tickets_cited_by_a_commit": len(matched),
            "ticket_side_rate": len(matched) / len(all_keys) if all_keys else 0.0,
            "commit_side_rate": commit_side[repo]["rate_multi"],
            "commits_scanned": commit_side[repo]["commits_scanned"],
            "distinct_keys_cited_in_commits": len(cited),
            "cited_keys_not_in_jira": len(cited - all_keys),
        }
        out["projects"].append(rec)
        print(f"{repo:12s} tickets {len(all_keys):7,d}  cited {len(matched):7,d}  "
              f"ticket-side {rec['ticket_side_rate']*100:5.1f}%   "
              f"commit-side {rec['commit_side_rate']*100:5.1f}%")
        sys.stdout.flush()
        json.dump(out, open(args.out, "w"), indent=1)

    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
