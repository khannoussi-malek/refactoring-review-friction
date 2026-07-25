#!/usr/bin/env python3
"""
jira_estimates.py — how often do public Jira issues carry an effort estimate?

Motivation. The Hadoop pilot found effort estimates in 0 of 323 architectural
tickets, which killed the original RQ1 framing. That is one project. This
measures the base rate across the Public Jira Dataset (Zenodo 15719919): 16
public Jira repositories, 1,822 projects, ~2.7M issues.

DESCRIPTIVE ONLY. It counts presence. It does not test whether estimates predict
anything and does not compute overrun; that analysis must be pre-registered.

Reader: `scripts/jira_archive.py` streams the gzip-wrapped mongodump archive
directly out of the zip. No mongorestore, no mongod, nothing extracted — the
published restore path needs ~60 GB expanded.

THREE STATES, NEVER TWO. For every (repo, field):
    absent_from_catalogue  the org's Jira has no such field at all
    present_null           the field exists; this issue left it empty
    present_with_value     the field exists and carries a value
Collapsing the first two turns "this organisation does not track estimates" into
"this issue has no estimate", which are different claims. Mojang and MongoDB
expose none of the six time-tracking fields, so for them every zero is the first
kind.

Story points have no standard field: every organisation puts them in a
differently-numbered customfield_*. The per-repo catalogue shipped with the
dataset is enumerated and matched BY NAME; guessing an id would silently produce
zeros. See paper/estimate_field_schema.md.

Usage:
    python3 scripts/jira_estimates.py --zip <dataset.zip> --stage count
"""
import argparse, json, re, sys, zipfile
from collections import Counter, defaultdict

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from jira_archive import stream_archive

CATALOGUE = "ThePublicJiraDataset/0. DataDefinition/jira_field_information.json"
CATALOGUE_2021 = ("ThePublicJiraDataset/0. DataDefinition/May2021/"
                  "jira_field_information_MAY_2021.json")
SOURCES = "ThePublicJiraDataset/0. DataDefinition/jira_data_sources.json"

TIME_FIELDS = ["timeoriginalestimate", "timeestimate", "timespent",
               "aggregatetimeoriginalestimate", "aggregatetimeestimate",
               "aggregatetimespent"]
STORY_RE = re.compile(r"stor(y|ies)[\s_-]*point|storypoints?", re.I)
# Published dataset totals, for the validation gate.
PUBLISHED_ISSUES, PUBLISHED_PROJECTS = 2_700_000, 1822
# Repos absent from the primary catalogue; their schema comes from May 2021.
SNAPSHOT_2021 = {"MariaDB", "Mindville"}


def load_catalogues(zip_path):
    """repo -> {'time': set(ids present), 'story': {id: name}, 'snapshot': str}"""
    z = zipfile.ZipFile(zip_path)
    primary = json.loads(z.read(CATALOGUE))
    may2021 = json.loads(z.read(CATALOGUE_2021))
    out = {}
    for repo in sorted(set(primary) | SNAPSHOT_2021):
        src, tag = (primary, "2023") if repo in primary else (may2021, "MAY_2021")
        fields = src.get(repo, [])
        out[repo] = {
            "time": {f["id"] for f in fields if f["id"] in TIME_FIELDS},
            "story": {f["id"]: f.get("name") for f in fields
                      if f.get("custom") and STORY_RE.search(f.get("name") or "")},
            "snapshot": tag,
            "n_fields": len(fields),
        }
    return out


def count(args):
    cat = load_catalogues(args.zip)
    seen = Counter()                      # repo -> issues
    projects = defaultdict(set)           # repo -> {project keys}
    hits = defaultdict(Counter)           # repo -> field -> present_with_value
    nulls = defaultdict(Counter)          # repo -> field -> present_null
    apache_proj = defaultdict(Counter)    # project -> counters (base-rate detail)
    n = 0

    for _db, repo, doc in stream_archive(args.zip):
        n += 1
        if n % 250_000 == 0:
            print(f"  ... {n:,} docs", file=sys.stderr, flush=True)
        f = doc.get("fields") or {}
        if not isinstance(f, dict):
            continue
        seen[repo] += 1
        proj = f.get("project") or {}
        pkey = proj.get("key") if isinstance(proj, dict) else None
        if pkey:
            projects[repo].add(pkey)
        spec = cat.get(repo)
        if spec is None:
            continue

        any_est = False
        for tf in TIME_FIELDS:
            if tf not in spec["time"]:
                continue                              # absent_from_catalogue
            if f.get(tf) is None:
                nulls[repo][tf] += 1
            else:
                hits[repo][tf] += 1
                if tf in ("timeoriginalestimate", "aggregatetimeoriginalestimate"):
                    any_est = True
        if spec["story"]:
            if any(f.get(cid) is not None for cid in spec["story"]):
                hits[repo]["story_points"] += 1
                any_est = True
            else:
                nulls[repo]["story_points"] += 1
        if any_est:
            hits[repo]["any_estimate"] += 1

        if repo == "Apache" and pkey:
            apache_proj[pkey]["total"] += 1
            if f.get("timeoriginalestimate") is not None:
                apache_proj[pkey]["timeoriginalestimate"] += 1
            if any(f.get(cid) is not None for cid in spec["story"]):
                apache_proj[pkey]["story_points"] += 1
            if any_est:
                apache_proj[pkey]["any_estimate"] += 1

    total_projects = sum(len(v) for v in projects.values())
    result = {
        "validation": {
            "issues_parsed": n,
            "issues_published": PUBLISHED_ISSUES,
            "projects_parsed": total_projects,
            "projects_published": PUBLISHED_PROJECTS,
            "repos_parsed": len(seen),
        },
        "catalogues": {r: {"snapshot": c["snapshot"], "n_fields": c["n_fields"],
                           "time_fields_present": sorted(c["time"]),
                           "story_fields": c["story"]} for r, c in cat.items()},
        "repos": {},
        "apache_projects": {p: dict(c) for p, c in apache_proj.items()},
    }
    for repo, tot in seen.items():
        spec = cat.get(repo)
        rec = {"issues": tot, "snapshot": spec["snapshot"] if spec else None,
               "projects": len(projects[repo]), "fields": {}}
        for field in TIME_FIELDS + ["story_points"]:
            if spec is None:
                state = {"state": "no_catalogue"}
            elif field == "story_points":
                state = ({"state": "absent_from_catalogue"} if not spec["story"]
                         else {"state": "present",
                               "present_with_value": hits[repo][field],
                               "present_null": nulls[repo][field]})
            elif field not in spec["time"]:
                state = {"state": "absent_from_catalogue"}
            else:
                state = {"state": "present",
                         "present_with_value": hits[repo][field],
                         "present_null": nulls[repo][field]}
            rec["fields"][field] = state
        rec["any_estimate"] = hits[repo]["any_estimate"]
        result["repos"][repo] = rec

    json.dump(result, open(args.out, "w"), indent=1)
    report(result, args)


def _pct(a, b):
    return f"{100.0*a/b:.3f}%" if b else "—"


def report(res, args):
    v = res["validation"]
    print("\n=== VALIDATION (gate — read before any count) ===")
    print(f"  issues parsed   {v['issues_parsed']:>10,}   published ~{v['issues_published']:,}"
          f"   delta {v['issues_parsed']-v['issues_published']:+,}")
    print(f"  projects parsed {v['projects_parsed']:>10,}   published {v['projects_published']:,}"
          f"   delta {v['projects_parsed']-v['projects_published']:+,}")
    print(f"  repos parsed    {v['repos_parsed']:>10}")

    print("\n=== ESTIMATE COVERAGE (three states, never collapsed) ===")
    rows = sorted(res["repos"].items(),
                  key=lambda kv: -(kv[1]["any_estimate"] / max(kv[1]["issues"], 1)))
    print(f"{'repo':16s} {'snap':>8s} {'issues':>9s} {'proj':>5s} {'any est':>9s}  "
          f"{'orig-est':>9s} {'story pts':>10s}")
    for repo, r in rows:
        tot = r["issues"]
        oe = r["fields"]["timeoriginalestimate"]
        sp = r["fields"]["story_points"]
        oe_s = ("ABSENT" if oe["state"] != "present"
                else _pct(oe["present_with_value"], tot))
        sp_s = ("ABSENT" if sp["state"] != "present"
                else _pct(sp["present_with_value"], tot))
        print(f"{repo:16s} {str(r['snapshot']):>8s} {tot:9,d} {r['projects']:5d} "
              f"{_pct(r['any_estimate'], tot):>9s}  {oe_s:>9s} {sp_s:>10s}")
    print(f"\nWrote {args.out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--stage", choices=["count"], default="count")
    ap.add_argument("--out", default="estimates_by_org.json")
    args = ap.parse_args()
    count(args)


if __name__ == "__main__":
    main()
