#!/usr/bin/env python3
"""
entity_tracking.py — can a class identity be followed across refactorings?

Task 18. The violation-symptom design (and the superseded SATD design before it)
needs to anchor on an ENTITY -- a class -- observe a symptom against it at time
t0, and detect an architectural refactoring OF THAT SAME ENTITY at t1. That only
works if the entity's identity survives the moves and renames that happen in
between. `paper/ENTITY_IDENTIFIERS.md` established that RefactoringMiner's output
CARRIES fully-qualified names. It did not establish that those names CHAIN.

This measures whether they chain, against an independent oracle.

THE ORACLE. git's own rename detection (`--find-renames`) over the same commits.
A top-level Java class lives in a file whose path is its FQN, so a class that
moves or is renamed produces a file rename in git. If RefactoringMiner emitted a
class-level identity edge for that commit whose endpoints match the two paths,
the identity is recoverable; if it did not, the entity silently changes name and
any chain anchored on it breaks.

The oracle is not perfect and its two error directions are opposite:
  * git misses a rename when the file changed by more than the similarity
    threshold (default 50%), so some real moves are absent from the denominator;
  * git invents a rename when an unrelated file happens to be similar, so some
    denominator entries are not moves at all.
Both are reported rather than assumed away: --threshold sweeps the first.

WHAT IS COUNTED AS AN IDENTITY EDGE. Only refactorings that map one existing
class onto one continuing class:
    Move Class, Rename Class, Move And Rename Class
`Change Type Declaration Kind` keeps the FQN and is counted as a no-op edge.
Extract Class / Superclass / Interface / Subclass CREATE a class -- they are
births, not identity edges, and are counted separately. Split Class and Merge
Class fork and join identity; they are reported and excluded from chains because
"the same entity" stops being well defined.

TOP-LEVEL ONLY. A nested class (`Outer.Inner`) has no file of its own, so the
git oracle cannot see it. FQNs are filtered to those whose only capitalised
segment is the last one. The count excluded by this rule is reported.

Usage:
    python3 scripts/entity_tracking.py --repo hadoop --rm refminer_all.json \
        --out paper/entity_tracking.json
"""
import argparse, json, os, re, subprocess, sys
from collections import Counter, defaultdict

# One existing class -> one continuing class.
IDENTITY_TYPES = {"Move Class", "Rename Class", "Move And Rename Class"}
# Same FQN on both sides; identity trivially preserved.
NOOP_TYPES = {"Change Type Declaration Kind"}
# A new class comes into existence. Not an identity edge.
BIRTH_TYPES = {"Extract Class", "Extract Superclass", "Extract Interface",
               "Extract Subclass"}
# Identity forks or joins. Reported, excluded from chains.
FORK_TYPES = {"Split Class", "Merge Class"}
# Package- and folder-level moves. The question is whether these are accompanied
# by per-class edges or replace them.
BULK_TYPES = {"Move Package", "Rename Package", "Merge Package", "Split Package",
              "Move Source Folder"}

FQN = r"[\w$]+(?:\.[\w$]+)+"
RE_MOVE = re.compile(rf"^Move Class ({FQN}) moved to ({FQN})$")
RE_RENAME = re.compile(rf"^Rename Class ({FQN}) renamed to ({FQN})$")
RE_MOVEREN = re.compile(rf"^Move And Rename Class ({FQN}) moved and renamed to ({FQN})$")
RE_PKG = re.compile(rf"^(?:Move|Rename) Package ({FQN}) to ({FQN})$")

CAP = re.compile(r"^[A-Z]")


def is_top_level(fqn):
    """True when exactly one segment is capitalised and it is the last.

    `org.apache.hadoop.fs.MultipartUploader`      -> True  (has a file)
    `...recovery.LeveldbRMStateStore.Compaction`  -> False (nested; no file)
    """
    segs = fqn.split(".")
    caps = [i for i, s in enumerate(segs) if CAP.match(s)]
    return caps == [len(segs) - 1]


def fqn_suffix(fqn):
    """The path tail a top-level class must have: a/b/C.java."""
    return "/" + fqn.replace(".", "/") + ".java"


SRC_ROOT = re.compile(r"^java\d*$")
PKG_ROOT = {"org", "com", "net", "io", "edu", "gov"}


def path_to_fqn(path):
    """The FQN a top-level class at this path must have, or None.

    A git rename is only an IDENTITY change if the fully-qualified name changes.
    Hadoop moves whole source roots -- `src/main/java` to `src/test/java`, or to
    `src/main/java8` -- and every file under them is renamed by git while its
    package and class name stay exactly as they were. Those renames need no
    RefactoringMiner edge, because nothing an FQN-anchored chain depends on
    moved. Counting them in the denominator would manufacture a failure.

    The source root is the last path segment named `java` or `javaNN`; failing
    that, the first segment that is a conventional package root.
    """
    segs = path.split("/")
    if not segs[-1].endswith(".java"):
        return None
    idx = None
    for i, s in enumerate(segs[:-1]):
        if SRC_ROOT.match(s):
            idx = i + 1
    if idx is None:
        for i, s in enumerate(segs[:-1]):
            if s in PKG_ROOT:
                idx = i
                break
    if idx is None:
        return None
    return ".".join(segs[idx:-1] + [segs[-1][:-5]])


def parse_edges(rm_path):
    """commit sha -> {identity: [(old,new)], bulk: [...], births: n, ...}"""
    data = json.load(open(rm_path))
    per_commit = {}
    tally = Counter()
    unparsed = []
    for c in data["commits"]:
        rec = {"identity": [], "identity_nested": [], "bulk": [], "births": 0,
               "forks": 0, "noop": 0}
        for r in c["refactorings"]:
            t, desc = r["type"], r["description"]
            if t in IDENTITY_TYPES:
                m = RE_MOVE.match(desc) or RE_RENAME.match(desc) or RE_MOVEREN.match(desc)
                if not m:
                    unparsed.append((t, desc[:120]))
                    tally["identity_unparsed"] += 1
                    continue
                old, new = m.group(1), m.group(2)
                if is_top_level(old) and is_top_level(new):
                    rec["identity"].append((old, new))
                    tally["identity_top_level"] += 1
                else:
                    rec["identity_nested"].append((old, new))
                    tally["identity_nested"] += 1
            elif t in BULK_TYPES:
                m = RE_PKG.match(desc)
                rec["bulk"].append({"type": t,
                                    "src": m.group(1) if m else None,
                                    "dst": m.group(2) if m else None,
                                    "description": desc})
                tally["bulk"] += 1
            elif t in BIRTH_TYPES:
                rec["births"] += 1
                tally["births"] += 1
            elif t in FORK_TYPES:
                rec["forks"] += 1
                tally["forks"] += 1
            elif t in NOOP_TYPES:
                rec["noop"] += 1
                tally["noop"] += 1
        per_commit[c["sha1"]] = rec
    return per_commit, tally, unparsed


def git_renames(repo, shas, threshold, extra=()):
    """sha -> [(old_path, new_path)] for *.java, from git's own detection.

    One `git log --no-walk --stdin` process for all commits; 8,919 subprocess
    calls would dominate the runtime for no benefit.
    """
    cmd = ["git", "-C", repo, "log", "--no-walk", "--stdin", "--name-status",
           f"--find-renames={threshold}", "-l0", "--diff-filter=R",
           "--format=\x1e%H", *extra, "--", "*.java"]
    p = subprocess.run(cmd, input="\n".join(shas), capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"git failed: {p.stderr[:400]}")
    out = defaultdict(list)
    for block in p.stdout.split("\x1e"):
        block = block.strip("\n")
        if not block:
            continue
        lines = block.split("\n")
        sha = lines[0].strip()
        for line in lines[1:]:
            if not line.startswith("R"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                out[sha].append((parts[1], parts[2]))
    return out


def match_rename(rename, edges):
    """Is this (old_path, new_path) explained by one of the commit's edges?"""
    old_p, new_p = rename
    for old_f, new_f in edges:
        if old_p.endswith(fqn_suffix(old_f)) and new_p.endswith(fqn_suffix(new_f)):
            return (old_f, new_f)
    return None


def build_chains(order, per_commit):
    """Longest forward chain per entity, following identity edges in time order.

    `succ[fqn]` is the name the entity takes next. Following it repeatedly gives
    the chain. A name reused as a source twice (two different commits moving the
    same FQN) means the FQN was recreated; the first edge wins and the collision
    is counted.
    """
    succ, collisions = {}, 0
    for sha in order:
        for old, new in per_commit.get(sha, {}).get("identity", []):
            if old in succ:
                collisions += 1
                continue
            succ[old] = new
    lengths = Counter()
    starts = set(succ) - set(succ.values())
    for s in starts:
        n, cur, seen = 0, s, set()
        while cur in succ and cur not in seen:
            seen.add(cur)
            cur = succ[cur]
            n += 1
        lengths[n] += 1
    return lengths, collisions, len(succ)


# Not type declarations: RefactoringMiner has no class to emit an edge for, so
# counting them as unexplained would charge the tool for a file it cannot see.
NON_TYPE_FILES = {"package-info.java", "module-info.java"}


def is_identity_change(old_p, new_p):
    """Does this git rename change the class's fully-qualified name?

    Returns True (identity changed, an edge is required), False (FQN intact),
    or None (not a type declaration, or the path has no recoverable package).
    """
    if (old_p.rsplit("/", 1)[-1] in NON_TYPE_FILES
            or new_p.rsplit("/", 1)[-1] in NON_TYPE_FILES):
        return None
    a, b = path_to_fqn(old_p), path_to_fqn(new_p)
    if a is None or b is None:
        return None            # cannot tell; reported separately
    return a != b


def path_chains(order, renames, per_commit):
    """Follow each entity's FQN chain and score each link.

    Only FQN-changing renames are links: a source-root move leaves the FQN
    intact, so it is not a step an FQN-anchored chain has to survive.
    Returns {chain_length: [n_chains, n_fully_covered]} -- the direct answer to
    "what fraction of entities survive N operations".
    """
    nxt, link_covered = {}, {}
    for sha in order:
        edges = per_commit.get(sha, {}).get("identity", [])
        for old_p, new_p in renames.get(sha, []):
            if is_identity_change(old_p, new_p) is not True:
                continue
            a, b = path_to_fqn(old_p), path_to_fqn(new_p)
            if a in nxt:
                continue
            nxt[a] = b
            link_covered[a] = match_rename((old_p, new_p), edges) is not None
    starts = set(nxt) - set(nxt.values())
    by_len = defaultdict(lambda: [0, 0])
    for s in starts:
        cur, n, ok, seen = s, 0, True, set()
        while cur in nxt and cur not in seen:
            seen.add(cur)
            ok = ok and link_covered[cur]
            cur = nxt[cur]
            n += 1
        by_len[n][0] += 1
        by_len[n][1] += 1 if ok else 0
    return {k: v for k, v in sorted(by_len.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="hadoop")
    ap.add_argument("--rm", default="refminer_all.json")
    ap.add_argument("--out", default="paper/entity_tracking.json")
    ap.add_argument("--threshold", default="50%")
    ap.add_argument("--sweep", default="30%,50%,70%,90%")
    args = ap.parse_args()

    per_commit, tally, unparsed = parse_edges(args.rm)
    shas = list(per_commit)

    # chronological order, from the repository rather than from file order
    log = subprocess.run(["git", "-C", args.repo, "log", "--all", "--format=%H %ct"],
                         capture_output=True, text=True, check=True).stdout
    ts = {}
    for line in log.splitlines():
        h, t = line.split()
        ts[h] = int(t)
    missing = [s for s in shas if s not in ts]
    if missing:
        raise SystemExit(f"{len(missing)} mined commits absent from {args.repo}")
    order = sorted(shas, key=lambda s: ts[s])

    result = {
        "repo": args.repo, "rm_file": os.path.basename(args.rm),
        "commits_mined": len(shas),
        "identity_types": sorted(IDENTITY_TYPES),
        "counts": dict(tally),
        "unparsed_examples": unparsed[:10],
        "rename_threshold": args.threshold,
    }

    print(f"commits mined           : {len(shas):,}")
    for k, v in sorted(tally.items()):
        print(f"  {k:24s}: {v:,}")

    # ---- coverage of git-detected renames, at several thresholds -------------
    sweep = {}
    for th in args.sweep.split(","):
        ren = git_renames(args.repo, order, th)
        total = fqn_changing = fqn_preserving = undecidable = matched = 0
        ex = []
        for sha, rs in ren.items():
            edges = per_commit[sha]["identity"]
            for r in rs:
                total += 1
                ident = is_identity_change(*r)
                if ident is None:
                    undecidable += 1
                    continue
                if not ident:
                    fqn_preserving += 1
                    continue
                fqn_changing += 1
                if match_rename(r, edges):
                    matched += 1
                elif True:
                    ex.append({"sha": sha, "from": r[0], "to": r[1],
                               "from_fqn": path_to_fqn(r[0]),
                               "to_fqn": path_to_fqn(r[1]),
                               "commit_had_identity_edges": len(edges),
                               "commit_had_bulk": len(per_commit[sha]["bulk"])})
        sweep[th] = {"git_renames": total,
                     "fqn_preserving": fqn_preserving,
                     "undecidable_path": undecidable,
                     "fqn_changing": fqn_changing,
                     "explained_by_rm": matched,
                     "coverage": matched / fqn_changing if fqn_changing else None,
                     "unexplained_examples": ex}
        print(f"\nrename threshold {th:>4s}: {total:,} java renames = "
              f"{fqn_preserving:,} FQN-preserving + {undecidable:,} undecidable + "
              f"{fqn_changing:,} FQN-changing")
        print(f"                  of the FQN-changing: {matched:,} explained by a "
              f"RefactoringMiner identity edge "
              f"({(matched/fqn_changing*100 if fqn_changing else 0):.1f}%)")
    result["coverage_sweep"] = sweep

    # ---- what the residual looks like, mechanically -------------------------
    # Not an adjudication: no rater decides here. The split is computed from the
    # two FQNs, so a reader can see whether the misses are package-only moves
    # (a Move Class the detector did not emit) or pairings of unrelated names
    # (git's similarity heuristic pairing an add with a delete).
    import difflib
    res = Counter()
    for e in sweep[args.threshold]["unexplained_examples"]:
        a, b = e["from_fqn"], e["to_fqn"]
        pa, na = a.rsplit(".", 1)
        pb, nb = b.rsplit(".", 1)
        sim = difflib.SequenceMatcher(None, na, nb).ratio()
        if na == nb:
            res["package_only_move"] += 1
        elif sim >= 0.6 and pa == pb:
            res["rename_in_place_similar_name"] += 1
        elif sim >= 0.6:
            res["move_and_rename_similar_name"] += 1
        else:
            res["unrelated_names"] += 1
    result["residual_categories"] = dict(res)
    print("\n  residual (unexplained FQN-changing renames), mechanical split:")
    for k, v in res.most_common():
        print(f"    {v:4d}  {k}")

    # ---- the operating point -------------------------------------------------
    renames = git_renames(args.repo, order, args.threshold)

    # ---- do package-level moves come with per-class edges? -------------------
    bulk_rows = []
    for sha in order:
        rec = per_commit[sha]
        if not rec["bulk"]:
            continue
        rs = [r for r in renames.get(sha, []) if is_identity_change(*r) is True]
        cov = sum(1 for r in rs if match_rename(r, rec["identity"]))
        bulk_rows.append({
            "sha": sha,
            "bulk": [b["type"] for b in rec["bulk"]],
            "src_dst": [(b["src"], b["dst"]) for b in rec["bulk"]],
            "fqn_changing_renames": len(rs),
            "explained_by_class_edges": cov,
            "identity_edges_in_commit": len(rec["identity"]),
        })
    tot_r = sum(b["fqn_changing_renames"] for b in bulk_rows)
    tot_c = sum(b["explained_by_class_edges"] for b in bulk_rows)
    result["bulk_move_commits"] = {
        "n_commits": len(bulk_rows),
        "fqn_changing_renames": tot_r,
        "explained_by_class_edges": tot_c,
        "coverage": tot_c / tot_r if tot_r else None,
        "rows": bulk_rows,
    }
    print(f"\ncommits carrying a package/folder-level move : {len(bulk_rows)}")
    print(f"  FQN-changing renames in those commits      : {tot_r:,}")
    print(f"  also carrying a per-class identity edge    : {tot_c:,} "
          f"({(tot_c/tot_r*100 if tot_r else 0):.1f}%)")

    # Move Package is the case the design actually asks about; a Move Source
    # Folder is a build-layout change and mostly leaves FQNs alone.
    PKG_OPS = {"Move Package", "Rename Package", "Merge Package", "Split Package"}
    split = {}
    for label, pred in (("package_level_op", lambda b: PKG_OPS & set(b)),
                        ("source_folder_only", lambda b: not (PKG_OPS & set(b)))):
        rows = [r for r in bulk_rows if pred(r["bulk"])]
        t = sum(r["fqn_changing_renames"] for r in rows)
        c = sum(r["explained_by_class_edges"] for r in rows)
        split[label] = {"commits": len(rows), "fqn_changing_renames": t,
                        "explained_by_class_edges": c,
                        "coverage": c / t if t else None}
        print(f"    {label:20s}: {len(rows):3d} commits, {c:4d}/{t:4d} covered "
              f"({(c/t*100 if t else 0):.1f}%)")
    result["bulk_move_commits"]["split"] = split

    # ---- reverse direction: RM edges git did not see -------------------------
    rm_edges = rm_unconfirmed = 0
    for sha in order:
        rs = renames.get(sha, [])
        for e in per_commit[sha]["identity"]:
            rm_edges += 1
            if not any(match_rename(r, [e]) for r in rs):
                rm_unconfirmed += 1
    result["rm_edges_not_seen_by_git"] = {
        "rm_top_level_identity_edges": rm_edges,
        "not_matched_by_a_git_rename": rm_unconfirmed,
        "share": rm_unconfirmed / rm_edges if rm_edges else None,
    }
    print(f"\nRefactoringMiner top-level identity edges     : {rm_edges:,}")
    print(f"  with no git rename at the matching paths    : {rm_unconfirmed:,} "
          f"({(rm_unconfirmed/rm_edges*100 if rm_edges else 0):.1f}%)")

    # ---- do chains terminate on something that exists? -----------------------
    def java_tree(rev):
        t = subprocess.run(["git", "-C", args.repo, "ls-tree", "-r",
                            "--name-only", rev],
                           capture_output=True, text=True, check=True).stdout
        return [p for p in t.splitlines() if p.endswith(".java")]

    succ = {}
    last_edge_commit = {}
    for sha in order:
        for old, new in per_commit[sha]["identity"]:
            if old in succ:
                continue
            succ[old] = new
            last_edge_commit[new] = sha
    terminals = set(succ.values()) - set(succ)

    # Two reference points. At HEAD a class may simply have been deleted since;
    # at the commit that produced it, a chain that does not resolve is a chain
    # that never landed on a real file.
    head_paths = java_tree("HEAD")
    res_head = sum(1 for t in terminals
                   if any(p.endswith(fqn_suffix(t)) for p in head_paths))
    trees = {}
    res_own = 0
    for t in terminals:
        sha = last_edge_commit[t]
        if sha not in trees:
            trees[sha] = java_tree(sha)
        if any(p.endswith(fqn_suffix(t)) for p in trees[sha]):
            res_own += 1
    result["chain_terminals"] = {
        "terminals": len(terminals),
        "resolve_at_the_commit_that_produced_them": res_own,
        "resolve_to_a_file_at_head": res_head,
        "head_java_files": len(head_paths),
    }
    print(f"\nchain terminals resolving at their own commit: {res_own:,} of "
          f"{len(terminals):,} ({res_own/len(terminals)*100:.1f}%)")
    print(f"chain terminals still present at HEAD        : {res_head:,} of "
          f"{len(terminals):,} ({res_head/len(terminals)*100:.1f}%) "
          f"against {len(head_paths):,} java files at HEAD")

    # How complete is the mined window? A chain can only be as complete as the
    # commit range the detector was run over.
    log2 = subprocess.run(["git", "-C", args.repo, "log", "--format=%H %ct"],
                          capture_output=True, text=True, check=True).stdout
    reach = [(l.split()[0], int(l.split()[1])) for l in log2.splitlines()]
    lo, hi = min(ts[s] for s in shas), max(ts[s] for s in shas)
    window = [h for h, t in reach if lo <= t <= hi]
    mined_in_window = len(set(window) & set(shas))
    result["mined_window"] = {
        "mined_commits": len(shas),
        "head_reachable_commits_in_window": len(window),
        "mined_and_head_reachable": mined_in_window,
        "window_coverage": mined_in_window / len(window) if window else None,
    }
    print(f"\nmined window: {mined_in_window:,} of {len(window):,} "
          f"HEAD-reachable commits in the date range "
          f"({mined_in_window/len(window)*100:.1f}%)")

    # ---- chains -------------------------------------------------------------
    lengths, collisions, n_edges = build_chains(order, per_commit)
    result["rm_chains"] = {"edges": n_edges, "source_collisions": collisions,
                           "length_distribution": dict(sorted(lengths.items()))}
    print(f"\nRefactoringMiner identity graph: {n_edges:,} edges, "
          f"{collisions} reused sources")
    print("  chain length distribution (ops per entity):",
          dict(sorted(lengths.items())))

    pc = path_chains(order, renames, per_commit)
    result["git_path_chains"] = {str(k): {"chains": v[0], "fully_tracked": v[1]}
                                 for k, v in pc.items()}
    print("\n  git rename-chain length : chains : fully tracked by RM")
    for k, (n, ok) in pc.items():
        print(f"    {k:>3d} ops : {n:6,d} : {ok:6,d}  ({ok/n*100:5.1f}%)")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(result, open(args.out, "w"), indent=1)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
