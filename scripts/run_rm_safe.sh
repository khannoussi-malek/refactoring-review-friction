#!/usr/bin/env bash
# run_rm_safe.sh — parallel RefactoringMiner over a tag range, self-healing against
# commits that make RM hang (e.g. *.min.js dependency bumps).
#
# Strategy: split into MANY small chunks and run them in a pool. A background
# watchdog kills any chunk whose log stops advancing for STALL seconds — so one
# pathological commit wedges only its own small chunk, not the whole run. We then
# merge the chunks that finished and report coverage honestly. (Killed chunks'
# JSON is truncated/invalid and skipped — that's the coverage we knowingly trade.)
#
# Usage: bash scripts/run_rm_safe.sh <repo> <start> <end> [N=16] [STALL=150] [out.json]
set -uo pipefail
REPO="${1:?repo}"; START="${2:?start}"; END="${3:?end}"
N="${4:-16}"; STALL="${5:-150}"; OUT="${6:-refminer_range.json}"
RM="./RefactoringMiner/bin/RefactoringMiner"
WORK="rm_chunks/$(echo "${START}_${END}" | tr '/.' '__')"; rm -rf "$WORK"; mkdir -p "$WORK"

git -C "$REPO" rev-list --first-parent --reverse "${START}..${END}" > "$WORK/fp.txt"
M=$(wc -l < "$WORK/fp.txt" | tr -d ' ')
echo "range ${START}..${END}: $(git -C "$REPO" rev-list --count "${START}..${END}") commits, ${N} chunks, stall=${STALL}s"

# launch chunks (pool of 8 via a simple gate)
prev=$(git -C "$REPO" rev-parse "${START}^{commit}")
declare -a PID CHUNKLOG
maxpar=8
for k in $(seq 1 "$N"); do
  if [ "$k" -eq "$N" ]; then cur=$(git -C "$REPO" rev-parse "${END}^{commit}")
  else line=$(( M * k / N )); cur=$(sed -n "${line}p" "$WORK/fp.txt"); fi
  # throttle to maxpar live jobs
  while [ "$(jobs -rp | wc -l | tr -d ' ')" -ge "$maxpar" ]; do sleep 1; done
  "$RM" -bc "$REPO" "$prev" "$cur" -json "$WORK/chunk_$k.json" > "$WORK/chunk_$k.log" 2>&1 &
  PID[$k]=$!; CHUNKLOG[$k]="$WORK/chunk_$k.log"
  prev="$cur"
done

# watchdog: kill any chunk whose log hasn't been touched in STALL seconds
while :; do
  live=0
  for k in $(seq 1 "$N"); do
    p=${PID[$k]:-}; [ -z "$p" ] && continue
    kill -0 "$p" 2>/dev/null || { PID[$k]=""; continue; }
    live=$((live+1))
    # staleness: seconds since the chunk log was last written (macOS stat)
    mt=$(stat -f %m "${CHUNKLOG[$k]}" 2>/dev/null || echo 0)
    now=$(date +%s)
    if [ $((now - mt)) -ge "$STALL" ]; then
      echo "  watchdog: chunk $k stalled ${STALL}s — killing (pathological commit)"
      kill "$p" 2>/dev/null; PID[$k]=""
    fi
  done
  [ "$live" -eq 0 ] && break
  sleep 20
done
echo "all chunks settled — merging"

python3 - "$WORK" "$OUT" "$REPO" "$START" "$END" <<'PY'
import json, glob, os, sys, subprocess
work, out, repo, start, end = sys.argv[1:6]
seen, commits, bad = set(), [], 0
for p in sorted(glob.glob(os.path.join(work, "chunk_*.json"))):
    try: d = json.load(open(p))
    except Exception: bad += 1; continue
    for c in d.get("commits", []):
        s = c.get("sha1") or c.get("sha")
        if s in seen: continue
        seen.add(s); commits.append(c)
json.dump({"commits": commits}, open(out, "w"))
exp = set(subprocess.run(["git","-C",repo,"rev-list",f"{start}..{end}"],
      capture_output=True, text=True).stdout.split())
cov = len(seen & exp)
print(f"{out}: {len(commits)} commits, {sum(len(c.get('refactorings',[])) for c in commits)} refactorings, "
      f"coverage {cov}/{len(exp)} ({cov/len(exp):.0%}), {bad} chunks lost to hangs")
PY
