#!/usr/bin/env bash
# One in-repo dependency (:method :none) with a glob include and a header-file include, to see what
# `paths:include` and `files:include` list, and where :artifact falls back to.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"
d="$here/proj"; rm -rf "$d"; mkdir -p "$d/src" "$d/include" "$d/test" "$d/vendor_dep/inc/sub" "$d/vendor_dep/single"
printf 'int dep_fn(void);\n' > "$d/vendor_dep/inc/sub/dep.h"; printf 'int dep_single(void);\n' > "$d/vendor_dep/single/one.h"
printf 'int dep_fn(void){return 3;}\n' > "$d/vendor_dep/dep.c"
cat > "$d/project.yml" <<YML
---
:project:
  :which_ceedling: $ROOT
  :build_root: build
  :use_mocks: FALSE
  :release_build: TRUE
  :test_file_prefix: test_
:release_build:
  :output: app.out
:paths:
  :test:
    - test
  :source:
    - src
  :include:
    - include
:plugins:
  :enabled:
    - report_tests_pretty_stdout
    - dependencies
:dependencies:
  :deps:
    - :name: Vend
      :paths:
        :source: vendor_dep
      :fetch:
        :method: :none
      :artifacts:
        :static_libraries:
          - libvend.a
        :includes:
          - inc/**
          - single/one.h
...
YML
printf 'int main(void){return 0;}\n' > "$d/src/main.c"
