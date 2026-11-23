#!/usr/bin/env bash
# Release `:output` placement: default name, a relative name with a directory, an absolute name, and `~`.
here="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$here/../../.." && pwd)"; export BUNDLE_GEMFILE="$ROOT/Gemfile"
rm -rf "$here/proj"; : > "$here/results.txt"
mk() { # name output
  d="$here/proj/$1"; mkdir -p "$d/src/drv" "$d/inc" "$d/test" "$d/test" "$d/test"
  printf '#include "drv/led.h"\nint main(void){return led();}\n' > "$d/src/main.c"
  mkdir -p "$d/inc/drv"; printf 'int led(void);\n' > "$d/inc/drv/led.h"; printf '#include "drv/led.h"\nint led(void){return 0;}\n' > "$d/src/drv/led.c"
  printf 'x' > "$d/extra.txt"
  { echo "---"; echo ":project:"; echo "  :which_ceedling: $ROOT"; echo "  :build_root: build"; echo "  :release_build: TRUE"
    echo ":release_build:"; [ -n "$2" ] && echo "  :output: $2"; echo "  :artifacts:"; echo "    - extra.txt"
    echo ":paths:"; echo "  :test:"; echo "    - test"; echo "  :source:"; echo "    - src/**"; echo "  :include:"; echo "    - inc"; echo "..."; } > "$d/project.yml"
}
mk default ""
mk rel_dir "sub/app.out"
mk abs "$here/proj/abs_out/app.out"
mk home "~/gap10_release_test/app.out"
for v in default rel_dir abs home; do
  ( cd "$here/proj/$v" && bundle exec ruby "$ROOT/bin/ceedling" -v 4 release > ../$v.log 2>&1 ); rc=$?
  { echo "### $v exit=$rc"; grep -c "Launching Ceedling from $ROOT/" "$here/proj/$v.log" | sed 's/^/launch lines: /'
    ( cd "$here/proj/$v" && find build -type f -not -path 'build/vendor/*' -not -path '*/dependencies/*' | sort )
    [ "$v" = abs ] && find "$here/proj/abs_out" -type f | sed "s#$here/##"
    [ "$v" = home ] && find "$HOME/gap10_release_test" -type f | sed "s#$HOME#~#"; } | tee -a "$here/results.txt"
done
rm -rf "$HOME/gap10_release_test"

# A release-only project without :paths :test (project-file docs say :build_root and :paths :source suffice)
m="$here/proj/min"; mkdir -p "$m/src"; printf 'int main(void){return 0;}\n' > "$m/src/main.c"
printf -- '---\n:project:\n  :which_ceedling: %s\n  :build_root: build\n  :release_build: TRUE\n:paths:\n  :source:\n    - src\n...\n' "$ROOT" > "$m/project.yml"
( cd "$m" && bundle exec ruby "$ROOT/bin/ceedling" -v 4 release 2>&1 | grep -E "Launching Ceedling from|Required|EXCEPTION" > "$here/results_min_release.txt" )
cat "$here/results_min_release.txt" | tee -a "$here/results.txt"
