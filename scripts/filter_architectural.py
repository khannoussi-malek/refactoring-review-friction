#!/usr/bin/env python3
"""
filter_architectural.py — turn RefactoringMiner output into candidate
ARCHITECTURAL episodes, and (optionally) annotate each with the Jira key
its commit cites, so you can see traceability at a glance.

This is Definition-1 (the outcome) in starter form: RefactoringMiner is
method/class-centric, so here we (a) keep the package-level refactoring
types outright, and (b) keep Move-Class moves whose source/target package
differ, flagging those that cross a top-level "module" boundary. The
module depth is a knob — this is exactly the decision to settle with the
group before scaling.

Usage:
    python3 filter_architectural.py --rm refminer_out.json
    python3 filter_architectural.py --rm refminer_out.json --repo ../commons-lang --key LANG --module-depth 4
"""
import argparse, json, re, subprocess
from collections import Counter, defaultdict

# Package-level / structural types kept outright (architecture-adjacent).
PACKAGE_TYPES = {
    "Move Package", "Split Package", "Merge Package", "Rename Package",
    "Extract Class", "Extract Subclass", "Extract Superclass", "Extract Interface",
    "Extract And Move Class", "Move And Rename Class",
}
# Class-move types where we additionally require a package change to count.
CLASS_MOVE_TYPES = {"Move Class"}

FQN = re.compile(r"\b([a-z][\w.]*\.[A-Z]\w+)\b")  # crude package.Class matcher

def pkg_of(fqn: str) -> str:
    return fqn.rsplit(".", 1)[0] if "." in fqn else ""

def top_module(pkg: str, depth: int) -> str:
    return ".".join(pkg.split(".")[:depth])

def load_commit_keys(repo, key):
    """Map commit sha1 -> first cited issue key (if any). `key` may be
    comma-separated for monorepos, e.g. HADOOP,HDFS,YARN,MAPREDUCE."""
    if not repo or not key:
        return {}
    prefixes = [k.strip() for k in key.split(",") if k.strip()]
    pat = re.compile(rf"\b(?:{'|'.join(re.escape(k) for k in prefixes)})-\d+\b")
    fmt = "%H%x1f%s %b%x1e"
    # --all: episodes may live on a release branch that isn't an ancestor of the
    # checked-out HEAD (trunk). Without it the sha->key map misses those commits
    # and every release-branch episode is falsely annotated "no ticket".
    out = subprocess.run(["git", "-C", repo, "log", "--all", f"--pretty=format:{fmt}"],
                         capture_output=True, text=True, check=True).stdout
    m = {}
    for rec in out.split("\x1e"):
        rec = rec.strip("\n")
        if not rec or "\x1f" not in rec:
            continue
        h, msg = rec.split("\x1f", 1)
        found = pat.search(msg)
        if found:
            m[h] = found.group(0)
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rm", required=True, help="RefactoringMiner -json output file")
    ap.add_argument("--repo", default=None, help="repo path, to annotate episodes with cited issue keys")
    ap.add_argument("--key", default=None, help="Jira project key prefix(es), comma-separated for monorepos, e.g. HADOOP,HDFS,YARN,MAPREDUCE")
    ap.add_argument("--module-depth", type=int, default=4,
                    help="how many package segments define a 'module' (e.g. 4 = org.apache.commons.lang3)")
    ap.add_argument("--out", default="architectural_episodes.json")
    args = ap.parse_args()

    data = json.load(open(args.rm))
    commits = data.get("commits", data if isinstance(data, list) else [])
    keys = load_commit_keys(args.repo, args.key)

    episodes = []
    type_counter = Counter()
    total_refs = 0

    for c in commits:
        sha = c.get("sha1") or c.get("sha")
        refs = c.get("refactorings", [])
        total_refs += len(refs)
        arch = []
        cross_module = False
        for r in refs:
            t = r.get("type", "").strip()
            desc = r.get("description", "")
            if t in PACKAGE_TYPES:
                arch.append(t); type_counter[t] += 1
            elif t in CLASS_MOVE_TYPES:
                fqns = FQN.findall(desc)
                if len(fqns) >= 2:
                    p_src, p_dst = pkg_of(fqns[0]), pkg_of(fqns[-1])
                    if p_src != p_dst:
                        arch.append(t); type_counter[t] += 1
                        if top_module(p_src, args.module_depth) != top_module(p_dst, args.module_depth):
                            cross_module = True
        if arch:
            episodes.append({
                "sha1": sha,
                "arch_types": arch,
                "n_arch": len(arch),
                "cross_module": cross_module,
                "issue_key": keys.get(sha),
            })

    traceable = sum(1 for e in episodes if e["issue_key"])
    crossers = sum(1 for e in episodes if e["cross_module"])
    json.dump(episodes, open(args.out, "w"), indent=2)

    print(f"Commits with refactorings : {len(commits)}")
    print(f"Total refactorings        : {total_refs}")
    print(f"Candidate arch episodes   : {len(episodes)}")
    print(f"  ...cross-module moves   : {crossers}")
    if keys:
        rate = (traceable/len(episodes)) if episodes else 0
        print(f"  ...traceable to a ticket: {traceable}  ({rate:.0%})")
    print(f"\nTop architectural types:")
    for t, n in type_counter.most_common():
        print(f"  {n:5d}  {t}")
    print(f"\nWrote {args.out}  → open it and hand-pick 5 for the tracing worksheet.")

if __name__ == "__main__":
    main()
