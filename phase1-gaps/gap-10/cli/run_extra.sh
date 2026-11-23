#!/usr/bin/env bash
# Runner :includes spelling, and a project with no :paths :include (with and without TEST_INCLUDE_PATH).
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"; export BUNDLE_GEMFILE="$ROOT/Gemfile"
cd "$here/proj"; out="$here/results_extra.txt"; : > "$out"
c() { bundle exec ruby "$ROOT/bin/ceedling" -v 4 "$@" 2>&1; }
echo "### runner :includes, test:unit/test_foo.c" >> "$out"
c -p project.runner.yml test:unit/test_foo.c | grep -E "Launching Ceedling from|TESTED|PASSED|ERROR|EXCEPTION" >> "$out"
sed -n 1,8p build/test/runners/test/unit/test_foo_runner.c >> "$out"
echo "### no :include, test with TEST_INCLUDE_PATH" >> "$out"
c -p project.noinc.yml test:unit_extra/test_tip.c | grep -E "TESTED|PASSED|ERROR|EXCEPTION" >> "$out"
echo "### no :include, plain test" >> "$out"
c -p project.noinc.yml test:unit/test_foo.c | grep -E "TESTED|PASSED|ERROR|EXCEPTION" >> "$out"
