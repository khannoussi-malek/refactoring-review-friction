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

        # A transient failure can be EMPTY stdout or MALFORMED stdout (gh emits
        # non-JSON on some rate-limit and proxy errors). Treating only the empty
        # case as retryable crashes the run and loses every page fetched so far.
        j = None
        if r.stdout.strip():
            try:
                j = json.loads(r.stdout)
            except json.JSONDecodeError:
                j = None
        if j is None:
            fails += 1
            if fails > 12:
                print(f"giving up after {fails} failures; keeping {len(nodes)} "
                      f"PRs. last stderr: {r.stderr[:200]}", file=sys.stderr)
                break
            print(f"  transient failure {fails}, retrying", file=sys.stderr)
            time.sleep(min(2 ** fails, 30))
            continue

        # Validate the SHAPE, do not assume data/errors are the only outcomes.
        # GitHub also returns bare {"message": ...} bodies (rate limit, abuse
        # detection, transient 502s) which have neither key.
        if "errors" in j:
            print(f"GraphQL error (keeping {len(nodes)} PRs): {j['errors'][:1]}",
                  file=sys.stderr)
            break
        d = (j.get("data") or {}).get("repository")
        if not d or "pullRequests" not in d:
            fails += 1
            body = json.dumps(j)[:200]
            if fails > 12:
                print(f"giving up after {fails} unusable responses; keeping "
                      f"{len(nodes)} PRs. last body: {body}", file=sys.stderr)
                break
            print(f"  unusable response {fails} ({body}), retrying",
                  file=sys.stderr)
            time.sleep(min(2 ** fails, 30))
            continue
        fails = 0
        d = d["pullRequests"]
        nodes += d["nodes"]
        pages += 1
        if pages % 5 == 0:
            print(f"  ...{len(nodes)} PRs", file=sys.stderr)
        if not d["pageInfo"]["hasNextPage"]:
            break
        cur = d["pageInfo"]["endCursor"]

    # Always emit what we have. A partial fetch is usable; a crash is not.
    json.dump(nodes, sys.stdout)
    print(f"fetched {len(nodes)} PRs from {a.repo}"
          f"{' (PARTIAL)' if pages >= a.max_pages or fails > 12 else ''}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
