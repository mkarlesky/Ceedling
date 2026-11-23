#!/bin/sh
# Tagged variant of e2. Same include chain; the generated header redefines the type identically.
# t_tag_enum_differs and t_untag_struct are controls.
CC=${CC:-gcc}
for t in t_tag_enum t_tag_struct t_tag_enum_differs t_untag_struct; do
  echo "+ $CC $* -fsyntax-only -I . $t.c"
  if $CC "$@" -fsyntax-only -I . $t.c 2>&1; then echo "RESULT $t: compiles"; else echo "RESULT $t: rejected"; fi
done
