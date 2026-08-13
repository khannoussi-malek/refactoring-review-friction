#!/usr/bin/env bash
# prepare.sh — everything a held-out project needs BEFORE outcomes exist.
#
#   1. traceability probe (commit messages only)
#   2. mvn help:effective-pom
#   3. the FROZEN v1 rule -> predictions/<project>.json
#
# Deliberately stops there. Outcomes are pulled by outcomes.py in a later
# commit, so the ordering stays auditable in git history.
#
# Usage: scripts/replication/prepare.sh <project> <JIRA_KEY> [xmldir]
set -uo pipefail
cd "$(dirname "$0")/../.."

P="$1"; KEY="$2"; XMLDIR="${3:-/tmp}"
REPO="corpora/$P"
MVN="${MVN_BIN:-mvn}"
PY="./.venv/bin/python"

[ -d "$REPO/.git" ] || { echo "$P: NOT CLONED"; exit 1; }

RATE=$($PY scripts/citation_rate.py --repo "$REPO" --key "$KEY" 2>/dev/null \
       | awk '/citing a key/{gsub(/[()%]/,"",$NF); print $NF}')
[ -z "$RATE" ] && { echo "$P: probe failed"; exit 1; }

# The 80% bar was fixed before any project was cloned (see PREDICTIONS.md).
if [ "$(printf '%.0f' "$RATE")" -lt 80 ]; then
  echo "$P: traceability ${RATE}% — DROPPED"; exit 2
fi

if [ ! -s "$XMLDIR/$P-effective.xml" ]; then
  ( cd "$REPO" && timeout 1500 "$MVN" -q -B help:effective-pom \
      -Doutput="$XMLDIR/$P-effective.xml" >/dev/null 2>&1 )
fi
[ -s "$XMLDIR/$P-effective.xml" ] || { echo "$P: traceability ${RATE}% but effective-pom FAILED"; exit 3; }

NMOD=$($PY scripts/replication/effective_deps.py --xml "$XMLDIR/$P-effective.xml" \
        --project "$P" --repo-root "$PWD/$REPO" --out "predictions/$P.json" 2>&1 \
        | head -1)
echo "$P: traceability ${RATE}% | $NMOD"
