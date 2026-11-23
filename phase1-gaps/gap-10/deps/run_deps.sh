#!/usr/bin/env bash
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"; export BUNDLE_GEMFILE="$ROOT/Gemfile"
cd "$here/proj"; : > "$here/results.txt"
for t in paths:header paths:include files:header files:include files:assembly files:dependencies; do
  echo "### $t" | tee -a "$here/results.txt"
  bundle exec ruby "$ROOT/bin/ceedling" -v 4 "$t" 2>&1 | grep -E "Launching Ceedling from|^ ?-|^Path|^File|count|ERROR|EXCEPTION|Oops|\.h|inc/|vendor_dep|dependencies" | sort -u | tee -a "$here/results.txt" | tee -a "$here/cli_tasks.txt"
done
