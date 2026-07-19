#!/usr/bin/env python3
"""
pr_review_signal.py — extract the F2 "structural review discussion" signal for
each architectural episode.

Key insight from the week-1 slice: in Apache projects the real code review lives
on the GitHub PR, NOT natively in Jira -- but Apache's `githubbot` mirrors the
whole PR thread (including inline "commented on code" review comments) into the
Jira ticket's comments. So one public Jira REST call per ticket yields the full
review discussion. No GitHub OAuth token, no separate PR crawler.

This turns each episode's issue key into an F2 signal:
  - n_review  : relayed PR review comments (human reviewers, incl. inline code)
  - n_human   : native Jira human comments
  - n_ci      : Yetus/CI reports (noise, excluded from the signal)
  - struct_hits / f2_structural_review : does the discussion cite structure?

Usage:
    python3 pr_review_signal.py --selftest
    python3 pr_review_signal.py --issue HADOOP-18679
    python3 pr_review_signal.py --episodes architectural_episodes.json --out review_signal.json
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

JIRA = "https://issues.apache.org/jira/rest/api/2/issue/{key}?fields=summary,comment"
CACHE = ".jira_cache"  # ponytail: on-disk cache so re-runs don't re-hit Apache Jira

# Yetus/precommit CI boilerplate — this is noise, not review discussion.
CI = re.compile(r"green_heart|:x:|shadedclient|spotbugs|mvninstall|Apache Yetus"
                r"|automatically generated|precommit|Powered by")
# Structural / architectural language in the review discussion (the F2 signal).
STRUCT = re.compile(
    r"\b(refactor|architect|structur|coupl|cohes|abstract|interface|responsibilit"
    r"|split|extract|decoupl|encapsulat|modular|god class|too big|separation"
    r"|move (the )?class|package layout|too much)\w*", re.I)


def fetch(key, delay):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, key + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    req = urllib.request.Request(JIRA.format(key=key), headers={"User-Agent": "rq1-slice"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    json.dump(data, open(p, "w"))
    time.sleep(delay)  # ponytail: polite fixed delay; add backoff if ASF rate-limits at scale
    return data


def classify(data):
    f = data.get("fields", {})
    comments = (f.get("comment") or {}).get("comments", [])
    review, human, ci, opened, other = [], [], 0, 0, 0
    for c in comments:
        name = (c.get("author") or {}).get("displayName", "").strip().lower()
        body = c.get("body", "") or ""
        if name == "asf github bot":
            if "opened a new pull request" in body:
                opened += 1
            elif CI.search(body):
                ci += 1
            elif "commented on" in body:      # relayed reviewer discussion (incl. inline code review)
                review.append(body)
            else:
                other += 1                    # merge/close/edit notifications
        else:
            human.append(body)
    disc = review + human
    struct = sum(1 for b in disc if STRUCT.search(b))
    return dict(summary=f.get("summary"),
                n_review=len(review), n_human=len(human), n_ci=ci,
                n_opened=opened, n_other=other, n_discussion=len(disc),
                struct_hits=struct, f2_structural_review=struct > 0)


def keys_from_args(args):
    if args.issue:
        return [args.issue]
    eps = json.load(open(args.episodes))
    return [e["issue_key"] for e in eps if e.get("issue_key")]


def selftest():
    sample = {"fields": {"summary": "x", "comment": {"comments": [
        {"author": {"displayName": "ASF GitHub Bot"},
         "body": "steveloughran commented on code in PR #1: extract this into a separate interface, the class is doing too much"},
        {"author": {"displayName": "ASF GitHub Bot"}, "body": "+1 green_heart mvninstall Apache Yetus"},
        {"author": {"displayName": "ASF GitHub Bot"}, "body": "steveloughran opened a new pull request, #1: URL ..."},
        {"author": {"displayName": "Jane Dev"}, "body": "looks fine to me"},
    ]}}}
    r = classify(sample)
    assert r["n_review"] == 1, r
    assert r["n_ci"] == 1, r
    assert r["n_opened"] == 1, r
    assert r["n_human"] == 1, r
    assert r["struct_hits"] == 1 and r["f2_structural_review"] is True, r
    # a discussion with no structural language must NOT trip F2
    plain = {"fields": {"comment": {"comments": [
        {"author": {"displayName": "Jane"}, "body": "please rebase and fix the typo"}]}}}
    assert classify(plain)["f2_structural_review"] is False
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes")
    ap.add_argument("--issue")
    ap.add_argument("--out", default="review_signal.json")
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        selftest(); return
    if not args.episodes and not args.issue:
        ap.error("need --episodes or --issue")

    rows, hit = {}, 0
    print(f"{'KEY':<14}{'review':>7}{'human':>6}{'ci':>4}{'struct':>7}   F2")
    for k in keys_from_args(args):
        try:
            r = classify(fetch(k, args.delay))
        except urllib.error.URLError as e:
            rows[k] = {"error": str(e)}
            print(f"{k:<14}  ERROR {e}")
            continue
        rows[k] = r
        hit += r["f2_structural_review"]
        print(f"{k:<14}{r['n_review']:>7}{r['n_human']:>6}{r['n_ci']:>4}"
              f"{r['struct_hits']:>7}   {'YES' if r['f2_structural_review'] else 'no'}")
    print(f"\nF2 structural-review present: {hit}/{len(rows)} episodes")
    json.dump(rows, open(args.out, "w"), indent=2)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
