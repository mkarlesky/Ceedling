#!/usr/bin/env bash
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"; export BUNDLE_GEMFILE="$ROOT/Gemfile"
cd "$here/proj"; : > "$here/results.txt"
run() { out=$(bundle exec ruby "$ROOT/bin/ceedling" -v 4 "$@" 2>&1); echo "### $*" | tee -a "$here/results.txt"; echo "$out" | grep -E "Launching Ceedling from|TESTED|ERROR|unique|ambiguous|matches|Found no|test/(unit|integration|unit_extra)/test_foo.c" | sort -u | head -8 | tee -a "$here/results.txt"; }
run 'test:test_foo.c'
run 'test:unit/test_foo.c'
run 'test:unit\test_foo.c'
run 'test:path[unit]'
run 'test:path[unit/]'
run 'test:path[nit]'
run 'test:path[t/in]'
run 'test:path[test_foo.c]'
run 'test:path[Test]'
run 'test:path[gap-10]'
run 'test:path[test/unit\]'
run 'test:pattern[unit/test_foo]'
run 'test:pattern[^test/unit/]'
