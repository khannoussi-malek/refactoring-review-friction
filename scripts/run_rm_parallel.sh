#!/usr/bin/env bash
# run_rm_parallel.sh — parallel RefactoringMiner over a tag range.
#
# RM is single-threaded, so on a many-core machine one -bt run wastes most cores.
# This splits the range's first-parent mainline into N contiguous chunks and runs
# one `RM -bc <from> <to>` per chunk in parallel (N cores). The chunks tile the
# range exactly (each side-branch commit is attributed to the chunk holding its
# merge). We VERIFY that after merging rather than trusting the math.
#
# Usage: bash scripts/run_rm_parallel.sh <repo> <start-tag> <end-tag> [N] [out.json]
set -euo pipefail

REPO="${1:?repo}"; START="${2:?start-tag}"; END="${3:?end-tag}"
N="${4:-8}"; OUT="${5:-refminer_wide.json}"
RM="./RefactoringMiner/bin/RefactoringMiner"
WORK="rm_chunks"; rm -rf "$WORK"; mkdir -p "$WORK"

git -C "$REPO" rev-list --first-parent --reverse "${START}..${END}" > "$WORK/fp.txt"
M=$(wc -l < "$WORK/fp.txt" | tr -d ' ')
echo "range ${START}..${END}: $(git -C "$REPO" rev-list --count "${START}..${END}") commits, ${M} on mainline, ${N} chunks"

# ^{commit} dereferences annotated tags to the underlying commit; a bare tag object
# sha makes RM/JGit throw "is not a commit".
prev=$(git -C "$REPO" rev-parse "${START}^{commit}")
for k in $(seq 1 "$N"); do
  if [ "$k" -eq "$N" ]; then
    cur=$(git -C "$REPO" rev-parse "${END}^{commit}")
  else
    line=$(( M * k / N )); cur=$(sed -n "${line}p" "$WORK/fp.txt")
  fi
  echo "  chunk $k/$N: ${prev:0:10}..${cur:0:10}"
  "$RM" -bc "$REPO" "$prev" "$cur" -json "$WORK/chunk_$k.json" >"$WORK/chunk_$k.log" 2>&1 &
  prev="$cur"
done

echo "launched $N RM processes; waiting..."
wait
echo "all chunks done — merging"

python3 - "$WORK" "$OUT" "$REPO" "$START" "$END" <<'PY'
import json, glob, os, sys, subprocess
work, out, repo, start, end = sys.argv[1:6]
seen, commits = set(), []
for p in sorted(glob.glob(os.path.join(work, "chunk_*.json"))):
    d = json.load(open(p))
    for c in d.get("commits", d if isinstance(d, list) else []):
        sha = c.get("sha1") or c.get("sha")
        if sha in seen:      # de-dup any boundary overlap
            continue
        seen.add(sha); commits.append(c)
json.dump({"commits": commits}, open(out, "w"))

# verify coverage against git's own range
expected = set(subprocess.run(
    ["git", "-C", repo, "rev-list", f"{start}..{end}"],
    capture_output=True, text=True, check=True).stdout.split())
got = seen
missing = expected - got
extra = got - expected
print(f"merged commits: {len(commits)}  (unique sha1: {len(got)})")
print(f"git range size: {len(expected)}")
print(f"coverage: missing={len(missing)}  extra={len(extra)}",
      "OK" if not missing and not extra else "!! MISMATCH")
PY
echo "wrote $OUT"
