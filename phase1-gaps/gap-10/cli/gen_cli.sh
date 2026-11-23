#!/usr/bin/env bash
# Two same-named tests in different directories, for the `test:path[]` and `test:<name>` doc promises.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"
d="$here/proj"; rm -rf "$d"; mkdir -p "$d/test/unit" "$d/test/integration" "$d/test/unit_extra" "$d/src" "$d/include"
cat > "$d/project.yml" <<YML
---
:project:
  :which_ceedling: $ROOT
  :build_root: build
  :use_mocks: FALSE
  :test_file_prefix: test_
:paths:
  :test:
    - test/**
  :source:
    - src
  :include:
    - include
:plugins:
  :enabled:
    - report_tests_pretty_stdout
...
YML
printf 'int foo(void);\n' > "$d/include/foo.h"; printf '#include "foo.h"\nint foo(void){return 1;}\n' > "$d/src/foo.c"
for t in unit integration unit_extra; do
  printf '#include "unity.h"\n#include "foo.h"\nvoid setUp(void){}\nvoid tearDown(void){}\nvoid test_foo(void){TEST_ASSERT_EQUAL_INT(1, foo());}\n' > "$d/test/$t/test_foo.c"
done

# Unity runner :includes and a project with no :paths :include
python3 - "$d" <<'PY'
import sys
d=sys.argv[1]; s=open(d+'/project.yml').read()
open(d+'/project.runner.yml','w').write(s.replace(":plugins:", ":test_runner:\n  :includes:\n    - foo.h\n    - sub/missing.h\n:plugins:",1))
open(d+'/project.noinc.yml','w').write(s.replace("  :include:\n    - include\n",""))
PY
mkdir -p "$d/include/sub"; printf '#pragma once\n' > "$d/include/sub/missing.h"
printf '#include "unity.h"\nTEST_INCLUDE_PATH("include")\n#include "foo.h"\nvoid setUp(void){}\nvoid tearDown(void){}\nvoid test_foo(void){TEST_ASSERT_EQUAL_INT(1, foo());}\n' > "$d/test/unit_extra/test_tip.c"
