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
import argparse, json, os, re, subprocess, sys
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


def cited_numbers(repo, rev, keys):
    """{key prefix: set of issue numbers} cited anywhere in the commit messages."""
    pat = re.compile(rf"\b({'|'.join(re.escape(k) for k in keys)})-(\d+)\b")
    cmd = ["git", "-C", repo, "log", "--pretty=format:%s%n%b", rev]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    found = defaultdict(set)
    for m in pat.finditer(out):
        found[m.group(1)].add(int(m.group(2)))
    return found


def commits_at(repo, rev):
    out = subprocess.run(["git", "-C", repo, "rev-list", "--count", rev],
                         capture_output=True, text=True, check=True).stdout
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
        except subprocess.CalledProcessError as e:
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

    # validation summary
    val = [p["live"] for p in out["projects"] if "live" in p]
    if val:
        d = [abs(v["delta_pp"]) for v in val]
        out["validation"] = {
            "n": len(val),
            "mean_abs_delta_pp": sum(d) / len(d),
            "max_abs_delta_pp": max(d),
            "worst": max(val, key=lambda v: abs(v["delta_pp"])),
        }
        print(f"\nvalidation on {len(val)} projects with a published exact rate: "
              f"mean |Δ| {sum(d)/len(d):.2f}pp, max {max(d):.2f}pp")
    json.dump(out, open(args.out, "w"), indent=1)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
