#!/usr/bin/env bash
# rm_skip_range.sh — RefactoringMiner over (START, END] but SKIPPING commits listed
# in EXCLUDE_FILE (one sha/line). It splits the range at each excluded commit so RM
# never has to process it. Used to route around commits that make RM spin forever
# (e.g. jQuery/*.min.js dependency bumps). Segments run in parallel; merged to OUT.
#
# Usage: bash scripts/rm_skip_range.sh <repo> <start> <end> <exclude_file> <out.json> <tag>
set -uo pipefail
REPO="$1"; START="$2"; END="$3"; EXCLUDE_FILE="$4"; OUT="$5"; TAG="${6:-seg}"
RM="./RefactoringMiner/bin/RefactoringMiner"
WORK="rm_chunks"; mkdir -p "$WORK"
rm -f "$WORK/${TAG}_"*.json "$WORK/${TAG}_"*.log

# excluded commits that actually fall in this range, in mainline order
git -C "$REPO" rev-list --first-parent --reverse "${START}..${END}" > "$WORK/${TAG}_fp.txt"
python3 - "$WORK/${TAG}_fp.txt" "$EXCLUDE_FILE" > "$WORK/${TAG}_excl.txt" <<'PY'
import sys
order={s.strip():i for i,s in enumerate(open(sys.argv[1]))}
excl=[l.strip() for l in open(sys.argv[2]) if l.strip()]
print("\n".join(sorted((s for s in excl if s in order), key=lambda s: order[s])))
PY

run_seg() { "$RM" -bc "$REPO" "$1" "$2" -json "$WORK/${TAG}_$3.json" > "$WORK/${TAG}_$3.log" 2>&1 & }

prev=$(git -C "$REPO" rev-parse "${START}^{commit}")
i=0
while read -r e; do
  [ -z "$e" ] && continue
  par=$(git -C "$REPO" rev-parse "${e}^1")   # last good commit before e
  echo "  seg $i: ${prev:0:10}..${par:0:10}  (then skip ${e:0:10})"
  run_seg "$prev" "$par" "$i"
  prev="$e"                                   # next seg starts AFTER e → e skipped
  i=$((i+1))
done < "$WORK/${TAG}_excl.txt"
END_C=$(git -C "$REPO" rev-parse "${END}^{commit}")
echo "  seg $i: ${prev:0:10}..${END_C:0:10}"
run_seg "$prev" "$END_C" "$i"
wait

python3 - "$WORK" "$TAG" "$OUT" <<'PY'
import json, glob, os, sys
work, tag, out = sys.argv[1:4]
seen, commits = set(), []
for p in sorted(glob.glob(os.path.join(work, f"{tag}_*.json"))):
    try: d = json.load(open(p))
    except Exception as ex: print("  bad seg json", p, ex); continue
    for c in d.get("commits", []):
        s = c.get("sha1") or c.get("sha")
        if s in seen: continue
        seen.add(s); commits.append(c)
json.dump({"commits": commits}, open(out, "w"))
print(f"{tag}: merged {len(commits)} commits -> {out}")
PY
