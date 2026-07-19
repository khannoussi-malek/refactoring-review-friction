#!/usr/bin/env bash
# setup.sh — one-time environment setup. Needs JDK 17+, Python 3, git.
# Heavy step: building RefactoringMiner downloads Gradle + deps (a few min).
set -euo pipefail

echo "== Python env (for the citation/filter scripts and later survival modelling) =="
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet pandas lifelines   # lifelines = survival analysis, for Q3

echo "== Build RefactoringMiner from source =="
if [ ! -d RefactoringMiner-src ]; then
  git clone --depth 1 https://github.com/tsantalis/RefactoringMiner.git RefactoringMiner-src
fi
( cd RefactoringMiner-src && ./gradlew distZip )
ZIP=$(ls RefactoringMiner-src/build/distributions/RefactoringMiner-*.zip | head -1)
rm -rf RefactoringMiner && unzip -q -o "$ZIP" -d _rm_unzip
mv "$(ls -d _rm_unzip/RefactoringMiner-*/ | head -1)" RefactoringMiner && rmdir _rm_unzip

echo
echo "Done. Verify with:  ./RefactoringMiner/bin/RefactoringMiner -h"
echo "Activate the Python env each session with:  source .venv/bin/activate"
