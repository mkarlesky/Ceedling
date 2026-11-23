#!/bin/sh
# e2 unchanged, with GCC in place of clang. $CC defaults to gcc. Extra args (e.g. -std=c17) go to every compile.
CC=${CC:-gcc}
set -x
$CC "$@" -fsyntax-only -I . t_now.c
$CC "$@" -fsyntax-only -I . t_flagged.c && echo flagged-ok
