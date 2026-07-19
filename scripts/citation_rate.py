#!/usr/bin/env python3
"""
citation_rate.py — Filter 3 probe (issue-to-commit traceability).

Measures what fraction of a project's commits reference a Jira issue key
(e.g. LANG-1234). That rate is the hard ceiling on how many detected
refactorings you can ever trace back to the ticket that carries the signal.

Usage:
    python3 citation_rate.py --repo ../commons-lang --key LANG
    python3 citation_rate.py --repo /path/to/hadoop --key HADOOP --since 2015-01-01
"""
import argparse, re, subprocess, sys
from collections import Counter

def git_log(repo, since):
    # %H = hash, then full raw subject+body, records separated by \x1e, fields by \x1f
    fmt = "%H%x1f%s%x1f%b%x1e"
    cmd = ["git", "-C", repo, "log", f"--pretty=format:{fmt}"]
    if since:
        cmd.append(f"--since={since}")
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec:
            continue
        parts = rec.split("\x1f")
        if len(parts) >= 3:
            yield parts[0], parts[1], parts[2]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--key", required=True, help="Jira project key prefix(es), comma-separated for monorepos, e.g. HADOOP,HDFS,YARN,MAPREDUCE")
    ap.add_argument("--since", default=None, help="optional git --since date, e.g. 2015-01-01")
    ap.add_argument("--samples", type=int, default=8)
    args = ap.parse_args()

    prefixes = [k.strip() for k in args.key.split(",") if k.strip()]
    pat = re.compile(rf"\b(?:{'|'.join(re.escape(k) for k in prefixes)})-\d+\b")
    total = cited = 0
    subject_cited = 0
    keys = Counter()
    sample = []

    for h, subj, body in git_log(args.repo, args.since):
        total += 1
        msg = f"{subj}\n{body}"
        found = pat.findall(msg)
        if found:
            cited += 1
            if pat.search(subj):
                subject_cited += 1
            keys.update(found)
            if len(sample) < args.samples:
                sample.append((h[:10], subj[:72]))

    if total == 0:
        print("No commits found. Check --repo path.", file=sys.stderr)
        sys.exit(1)

    print(f"Project key prefix : {', '.join(prefixes)}")
    print(f"Commits scanned    : {total}")
    print(f"Commits citing a key: {cited}  ({cited/total:.1%})")
    print(f"  ...in the subject : {subject_cited}  ({subject_cited/total:.1%})")
    print(f"Distinct issue keys : {len(keys)}")
    print(f"\nInterpretation: ~{cited/total:.0%} of commits are traceable to a ticket.")
    print("That is your Filter-3 ceiling. Multiply it by estimate-availability and")
    print("linked-review rates to estimate how many episodes survive ALL three filters.")
    print("\nSample cited commits:")
    for h, s in sample:
        print(f"  {h}  {s}")

if __name__ == "__main__":
    main()
