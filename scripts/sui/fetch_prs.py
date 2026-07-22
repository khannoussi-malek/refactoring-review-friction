#!/usr/bin/env python3
"""
fetch_prs.py -- pull every PR for a repo with the fields replicate.py needs.

Paginates the GitHub GraphQL API, retries transient network failures (the
TLS handshake to api.github.com fails intermittently on long runs), and
writes a flat JSON array to stdout.

Usage:
    python3 scripts/sui/fetch_prs.py owner/name [--max-pages N] > prs.json
"""
import argparse, json, subprocess, sys, time

QUERY = """
query($owner:String!,$name:String!,$c:String){
  repository(owner:$owner,name:$name){
    pullRequests(first:100,after:$c,states:[MERGED,CLOSED,OPEN],
                 orderBy:{field:CREATED_AT,direction:ASC}){
      pageInfo{hasNextPage endCursor}
      nodes{ number createdAt mergedAt state additions deletions changedFiles
             comments{totalCount} reviews{totalCount} reviewThreads{totalCount}
             commits{totalCount} author{login} }
    }}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", help="owner/name")
    ap.add_argument("--max-pages", type=int, default=400)
    a = ap.parse_args()
    owner, name = a.repo.split("/", 1)

    nodes, cur, pages, fails = [], None, 0, 0
    while pages < a.max_pages:
        cmd = ["gh", "api", "graphql", "-f", "query=" + QUERY,
               "-F", f"owner={owner}", "-F", f"name={name}"]
        if cur:
            cmd += ["-F", "c=" + cur]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not r.stdout.strip():
            fails += 1
            if fails > 12:
                print(f"giving up after {fails} failures: {r.stderr[:200]}",
                      file=sys.stderr)
                break
            time.sleep(min(2 ** fails, 30))
            continue
        fails = 0
        j = json.loads(r.stdout)
        if "errors" in j:
            print(f"GraphQL error: {j['errors'][:1]}", file=sys.stderr)
            break
        d = j["data"]["repository"]["pullRequests"]
        nodes += d["nodes"]
        pages += 1
        print(f"  ...{len(nodes)} PRs", file=sys.stderr)
        if not d["pageInfo"]["hasNextPage"]:
            break
        cur = d["pageInfo"]["endCursor"]

    json.dump(nodes, sys.stdout)
    print(f"fetched {len(nodes)} PRs from {a.repo}", file=sys.stderr)


if __name__ == "__main__":
    main()
