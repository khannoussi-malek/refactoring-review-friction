#!/usr/bin/env bash
# run_refactoringminer.sh — detect refactorings across history -> JSON.
#
# RefactoringMiner is method/class-centric and running it over a FULL long
# history is slow. For the week-1 slice, start with a recent tag range
# (option B) rather than all commits (option A).
#
# Verify flags on your build with:  ./RefactoringMiner/bin/RefactoringMiner -h
set -euo pipefail

RM_BIN="${RM_BIN:-./RefactoringMiner/bin/RefactoringMiner}"
REPO="${1:?usage: run_refactoringminer.sh <repo-path> <branch-or-tag-range> [out.json]}"

# ---- Option A: all commits on a branch (slow on long histories) ----
#   ./run_refactoringminer.sh /path/to/repo trunk out.json
BRANCH="${2:-master}"
OUT="${3:-refminer_out.json}"
"$RM_BIN" -a "$REPO" "$BRANCH" -json "$OUT"

# ---- Option B: between two tags (recommended first pass) ----
#   "$RM_BIN" -bt "$REPO" rel/1.0 rel/1.1 -json "$OUT"
# ---- Option C: a single commit (to eyeball one refactoring) ----
#   "$RM_BIN" -c "$REPO" <sha1> -json "$OUT"

echo "Wrote $OUT"
