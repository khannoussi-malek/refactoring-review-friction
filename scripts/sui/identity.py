#!/usr/bin/env python3
"""
identity.py -- resolve git author aliases before computing any social variable.

Motivation: in start-ui-web the same developer appears as
    ivan@dalmet.fr                        59 commits, 0% via PR
    ivan-dalmet@users.noreply.github.com  16 commits, 100% via PR
because local CLI commits and GitHub-web commits carry different addresses.
Counted as two people, this corrupts every ownership, concentration and
centrality measure -- including making one person look like two with opposite
workflow habits.

Resolution rules, most reliable first:
  1. GitHub noreply addresses encode the login: "ID+login@users.noreply.github.com"
     or "login@users.noreply.github.com" -> login.
  2. Identical author NAME (git %an), case-folded.
  3. Identical email local-part, normalised (dots/dashes stripped).

Rule 1 is authoritative. Rules 2-3 are heuristics and are reported separately so
their merges can be inspected rather than trusted blindly.

Usage:
    python3 scripts/sui/identity.py --repo <path> [--apply-to <commits.json>]
"""
import argparse, collections, json, re, subprocess, sys

NOREPLY = re.compile(r"^(?:\d+\+)?([A-Za-z0-9-]+)@users\.noreply\.github\.com$", re.I)


def sh(repo, *a):
    return subprocess.run(["git", "-C", repo] + list(a),
                          capture_output=True, text=True).stdout


def norm_local(email):
    return re.sub(r"[.\-_]", "", email.split("@")[0]).lower()


def build_identities(repo):
    """-> (email -> canonical_id, report dict)"""
    pairs = collections.Counter()
    for line in sh(repo, "log", "--all", "--format=%ae\x02%an").strip().split("\n"):
        if "\x02" in line:
            e, n = line.split("\x02", 1)
            pairs[(e.lower().strip(), n.strip())] += 1

    emails = collections.Counter()
    email_names = collections.defaultdict(collections.Counter)
    for (e, n), c in pairs.items():
        emails[e] += c
        email_names[e][n] += c

    # union-find over emails
    parent = {e: e for e in emails}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            # prefer the higher-volume root so canonical ids are recognisable
            if emails[ra] < emails[rb]:
                ra, rb = rb, ra
            parent[rb] = ra

    merges = {"noreply_login": [], "same_name": [], "same_localpart": []}

    # rule 1: noreply login
    by_login = collections.defaultdict(list)
    for e in emails:
        m = NOREPLY.match(e)
        if m:
            by_login[m.group(1).lower()].append(e)
    # a login also matches a non-noreply email whose local part equals it
    for e in emails:
        if NOREPLY.match(e):
            continue
        lp = norm_local(e)
        for login in by_login:
            if re.sub(r"[-_.]", "", login) == lp:
                by_login[login].append(e)
    for login, es in by_login.items():
        if len(es) > 1:
            for x in es[1:]:
                union(es[0], x)
            merges["noreply_login"].append((login, sorted(set(es))))

    # rule 2: identical author name
    by_name = collections.defaultdict(set)
    for e, names in email_names.items():
        for n in names:
            if n and n.lower() not in ("unknown", "github", "dependabot[bot]"):
                by_name[n.lower()].add(e)
    for n, es in by_name.items():
        es = sorted(es)
        if len(es) > 1 and len({find(x) for x in es}) > 1:
            for x in es[1:]:
                union(es[0], x)
            merges["same_name"].append((n, es))

    # rule 3: identical normalised local part
    by_lp = collections.defaultdict(set)
    for e in emails:
        by_lp[norm_local(e)].add(e)
    for lp, es in by_lp.items():
        es = sorted(es)
        if len(es) > 1 and len({find(x) for x in es}) > 1:
            for x in es[1:]:
                union(es[0], x)
            merges["same_localpart"].append((lp, es))

    mapping = {e: find(e) for e in emails}
    return mapping, emails, email_names, merges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()

    mapping, emails, email_names, merges = build_identities(a.repo)
    groups = collections.defaultdict(list)
    for e, c in mapping.items():
        groups[c].append(e)

    n_raw = len(emails)
    n_res = len(groups)
    print(f"raw git author emails : {n_raw}")
    print(f"resolved identities   : {n_res}   ({n_raw - n_res} merged)")

    for rule, label in (("noreply_login", "GitHub login (authoritative)"),
                        ("same_name", "identical author name (heuristic)"),
                        ("same_localpart", "identical local-part (heuristic)")):
        ms = merges[rule]
        if not ms:
            continue
        print(f"\n-- {label}: {len(ms)} merge(s) --")
        for key, es in sorted(ms)[:12]:
            tot = sum(emails[e] for e in es)
            print(f"   {key}  ({tot} commits)")
            for e in es:
                print(f"      {emails[e]:5}  {e}")

    print("\n-- concentration, before vs after resolution --")
    raw_top = emails.most_common(1)[0]
    res = collections.Counter()
    for e, c in emails.items():
        res[mapping[e]] += c
    res_top = res.most_common(1)[0]
    tot = sum(emails.values())
    print(f"   top author share  raw {100*raw_top[1]/tot:5.1f}%  "
          f"->  resolved {100*res_top[1]/tot:5.1f}%")
    print(f"   top identity: {res_top[0]} ({res_top[1]} commits)")
    print("\n   top 5 resolved identities:")
    for ident, c in res.most_common(5):
        n = len(groups[ident])
        print(f"     {c:5}  {ident}" + (f"   [{n} aliases]" if n > 1 else ""))

    if a.out:
        json.dump({"mapping": mapping,
                   "groups": {k: v for k, v in groups.items() if len(v) > 1},
                   "counts": dict(emails)}, open(a.out, "w"), indent=2)
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
