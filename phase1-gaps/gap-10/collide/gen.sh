#!/usr/bin/env bash
# Generates the same-named `_AT` module experiment projects under ./proj/<variant>/.
# Each variant has src/a/util.c and src/b/util.c, both defining a static and a public function.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
CEEDLING_ROOT="$(cd "$here/../../.." && pwd)"
rm -rf "$here/proj"; mkdir -p "$here/proj"

project_yml() { # $1 dir
cat > "$1/project.yml" <<YML
---
:project:
  :which_ceedling: $CEEDLING_ROOT
  :build_root: build
  :use_mocks: TRUE
  :use_partials: TRUE
  :use_test_preprocessor: :none
  :test_file_prefix: test_
  :default_tasks:
    - test:all
:paths:
  :test:
    - test
  :source:
    - src/**
  :include:
    - include/**
:plugins:
  :enabled:
    - report_tests_pretty_stdout
...
YML
}

mk() { # variant, a_pub, b_pub, a_static, b_static, extra_a, extra_b, test_body, test_includes
  local v=$1 d="$here/proj/$1"
  mkdir -p "$d/src/a" "$d/src/b" "$d/include/a" "$d/include/b" "$d/test"
  project_yml "$d"
  for m in a b; do
    local pub static extra
    if [ $m = a ]; then pub=$2; static=$4; extra=$6; else pub=$3; static=$5; extra=$7; fi
    cat > "$d/include/$m/util.h" <<H
#ifndef ${m^^}_UTIL_H
#define ${m^^}_UTIL_H
int $pub(int x);
#endif
H
    cat > "$d/src/$m/util.c" <<C
#include "$m/util.h"
$extra
static int $static(int x) { return x + $([ $m = a ] && echo 1 || echo 2); }
$([ "${CALL:-no}" = yes ] && echo "int $pub(int x) { return $static(x) * 10; }" || echo "int $pub(int x) { return (x + $([ $m = a ] && echo 1 || echo 2)) * 10; }")
C
  done
  printf '%s\n' "#include \"unity.h\"" "#include \"ceedling.h\"" "$9" "" "void setUp(void) {}" "void tearDown(void) {}" "" "$8" > "$d/test/test_collide.c"
}

PUB_A='#include TEST_PARTIAL_PUBLIC_MODULE_AT(a, util)'
PUB_B='#include TEST_PARTIAL_PUBLIC_MODULE_AT(b, util)'
BODY='void test_both(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); TEST_ASSERT_EQUAL_INT(30, b_pub(1)); }'

# v1: same static name, distinct public names, PUBLIC macros
mk v1_public_same_static a_pub b_pub util_helper util_helper "" "" "$BODY" "$PUB_A
$PUB_B"
# v1b: public function calls the static, so the test selects the static too
CALL=yes mk v1b_public_calls_static a_pub b_pub util_helper util_helper "" "" "$BODY" "$PUB_A
$PUB_B
TEST_PARTIAL_CONFIG_AT(a, util, util_helper)
TEST_PARTIAL_CONFIG_AT(b, util, util_helper)"
# v2: same static AND same public name (also collides in plain C if both real files linked)
mk v2_public_same_pub util_pub util_pub util_helper util_helper "" "" \
  'void test_both(void) { TEST_ASSERT_EQUAL_INT(20, util_pub(1)); }' "$PUB_A
$PUB_B"
# v3: PRIVATE macros promote the static, so same static name now collides
mk v3_private_same_static a_pub b_pub util_helper util_helper "" "" \
  'void test_both(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); TEST_ASSERT_EQUAL_INT(30, b_pub(1)); }' \
  '#include TEST_PARTIAL_PRIVATE_MODULE_AT(a, util)
#include TEST_PARTIAL_PRIVATE_MODULE_AT(b, util)'
# v4: same-name file-scope static struct variable in both modules, PUBLIC macros
mk v4_public_same_var a_pub b_pub a_helper b_helper \
  'static struct { int count; } s_ctx;' 'static struct { int count; } s_ctx;' \
  'void test_both(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); TEST_ASSERT_EQUAL_INT(30, b_pub(1)); }' "$PUB_A
$PUB_B"
# v5: distinct variable names, so only the module part of the type name could collide
mk v5_public_distinct_var a_pub b_pub a_helper b_helper \
  'static struct { int count; } a_ctx;' 'static struct { int count; } b_ctx;' \
  'void test_both(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); TEST_ASSERT_EQUAL_INT(30, b_pub(1)); }' "$PUB_A
$PUB_B"
# v6: two mock Partials of same-named modules
mk v6_mock_both a_pub b_pub a_helper b_helper "" "" \
  'void test_both(void) { a_pub_ExpectAndReturn(1, 5); b_pub_ExpectAndReturn(1, 6); TEST_ASSERT_EQUAL_INT(5, a_pub(1)); TEST_ASSERT_EQUAL_INT(6, b_pub(1)); }' \
  '#include MOCK_PARTIAL_PUBLIC_MODULE_AT(a, util)
#include MOCK_PARTIAL_PUBLIC_MODULE_AT(b, util)'
# v7: same-name plain static int variable in both modules, PUBLIC macros (no type is generated)
mk v7_public_same_plain_var a_pub b_pub a_helper b_helper \
  'static int s_count;' 'static int s_count;' \
  'void test_both(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); TEST_ASSERT_EQUAL_INT(30, b_pub(1)); }' "$PUB_A
$PUB_B"
# v6b: as v6 with the folder left out of CMock's lifecycle names
cp -r "$here/proj/v6_mock_both" "$here/proj/v6b_mock_both_no_folder"
sed -i 's/^\.\.\.$//' "$here/proj/v6b_mock_both_no_folder/project.yml"
printf ':cmock:\n  :mock_name_include_folder: FALSE\n...\n' >> "$here/proj/v6b_mock_both_no_folder/project.yml"
# v8: a module whose name is a predefined macro under GCC's default dialect (`unix`, `linux` are 1)
d="$here/proj/v8_module_named_unix"; mkdir -p "$d/src" "$d/include" "$d/test"; project_yml "$d"
printf '#ifndef UNIX_H\n#define UNIX_H\nint unix_pub(int x);\n#endif\n' > "$d/include/unix.h"
printf '#include "unix.h"\nint unix_pub(int x) { return x * 10; }\n' > "$d/src/unix.c"
printf '%s\n' '#include "unity.h"' '#include "ceedling.h"' '#include TEST_PARTIAL_PUBLIC_MODULE(unix)' '' 'void setUp(void) {}' 'void tearDown(void) {}' 'void test_it(void) { TEST_ASSERT_EQUAL_INT(10, unix_pub(1)); }' > "$d/test/test_collide.c"
# v1cc: v1 with compile_commands_json_db enabled, to see how the two same-named Partials are keyed
cp -r "$here/proj/v1_public_same_static" "$here/proj/v1cc_compile_commands"
sed -i 's/^    - report_tests_pretty_stdout/    - report_tests_pretty_stdout\n    - compile_commands_json_db/' "$here/proj/v1cc_compile_commands/project.yml"
rm -rf "$here/proj/v1cc_compile_commands/build"
# v9: the unqualified macro with two modules sharing a basename (what does `util` mean?)
cp -r "$here/proj/v1_public_same_static" "$here/proj/v9_unqualified_ambiguous"; rm -rf "$here/proj/v9_unqualified_ambiguous/build"
printf '%s\n' '#include "unity.h"' '#include "ceedling.h"' '#include TEST_PARTIAL_PUBLIC_MODULE(util)' '' 'void setUp(void) {}' 'void tearDown(void) {}' 'void test_it(void) { TEST_ASSERT_EQUAL_INT(20, a_pub(1)); }' > "$here/proj/v9_unqualified_ambiguous/test/test_collide.c"
ls "$here/proj"
