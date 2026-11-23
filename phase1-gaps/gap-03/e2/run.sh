#!/bin/sh
# Stream 4 experiment e2 (#1463 shape). Apple clang 15.
set -x
clang -fsyntax-only -I . t_now.c
clang -fsyntax-only -I . t_flagged.c && echo flagged-ok
