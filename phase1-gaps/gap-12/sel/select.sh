#!/bin/bash
# Runs each test-selection task in proj/ and lists the tests it ran
cd "$(dirname "$0")/proj"
run() { echo "=== $*"; ../run.sh "$@" 2>&1 | grep -E "Launching|Parsing test_[A-Za-z_]+\.c for test case names|Found no|EXCEPTION|ERROR" | sed -E "s/Parsing (test_[A-Za-z_]+\.c) for test case names.../selected \1/" | tr "\n" ";"; echo; }
for a in "unit" "test/unit" "./test/unit" "test/unit/" "test\\unit" "$PWD/test/unit" "test_a" "test/unit/test_a" ".." "." "Unit" "nit" ; do run "test:path[$a]" --verbosity=obnoxious; done
for a in "test_a" "^test/" "^./test/" "\\.c$" "outside" "Unit" ; do run "test:pattern[$a]" --verbosity=obnoxious; done
run "test:pattern" --verbosity=obnoxious
run "test:path" --verbosity=obnoxious
run "test:pattern[]" --verbosity=obnoxious
run "test:path[]" --verbosity=obnoxious
for a in "test:test_a.c" "test:unit/test_a.c" "test:./test/unit/test_a.c" "test:../proj/test/unit/test_a.c" "test:../outside_tests/test_out.c" "test:test_out.c" "test:$PWD/test/unit/test_a.c"; do run "$a" --verbosity=obnoxious; done
# The valgrind plugin's copies of the same two tasks
V='--mixin==plugins: {enabled: [valgrind]}'
run "valgrind:path[unit]" "$V" --verbosity=obnoxious
run "valgrind:pattern" "$V" --verbosity=obnoxious
run "valgrind:path" "$V" --verbosity=obnoxious
S='--mixin==plugins: {enabled: [sanitize]}'
run "sanitize:pattern" "$S" --verbosity=obnoxious
run "sanitize:path[./test/unit]" "$S" --verbosity=obnoxious
