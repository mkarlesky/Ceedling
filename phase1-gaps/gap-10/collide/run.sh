#!/usr/bin/env bash
# Runs every generated variant and writes logs/<variant>.log plus a one-line result in results.txt.
here="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$here/../../.." && pwd)"; export BUNDLE_GEMFILE="$ROOT/Gemfile"
mkdir -p "$here/logs"; : > "$here/results.txt"
for d in "$here"/proj/*/; do
  v=$(basename "$d")
  ( cd "$d" && bundle exec ruby "$ROOT/bin/ceedling" -v 4 test:all > "$here/logs/$v.log" 2>&1 ); rc=$?
  echo "$v exit=$rc" | tee -a "$here/results.txt"
done

# Keep only the lines that carry the result. The full -v 4 logs are not committed.
mkdir -p "$here/logs"
for f in "$here"/logs/*.log; do
  grep -E "Launching Ceedling from|Compiling |Linking |EXCEPTION|error:|multiple definition|conflicting types|undefined reference|TESTED:|PASSED:|FAILED:|NOTICE: Multiple files|NOTICE: The linker|This test lacks|Executed Command" "$f" \
    | cut -c1-700 > "${f%.log}.excerpt.txt"
  rm -f "$f"
done
