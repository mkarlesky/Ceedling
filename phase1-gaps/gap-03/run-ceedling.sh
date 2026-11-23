#!/bin/sh
# Usage: run-ceedling.sh <project dir> <gcc13|gcc15> [ceedling args...]
# Copies the project to work/<name>-<cc>/ (ignored by git), builds there from clean, and writes
# the full log to work/<name>-<cc>.log. Ceedling runs from this checkout (:which_ceedling).
HERE=$(cd "$(dirname "$0")" && pwd)
SRC=$1; CC=$2; shift 2
NAME=$(echo "$SRC" | tr / -)-$CC
WORK=$HERE/work/$NAME
rm -rf "$WORK"; mkdir -p "$HERE/work"; cp -r "$HERE/$SRC" "$WORK"
if [ "$CC" = gcc15 ]; then PATH=$HERE/bin-gcc15:$PATH; export PATH; fi
cd "$WORK"
{
  echo "### project $SRC, compiler $CC: $(gcc --version | head -1)"
  echo "### default C standard: $(gcc -dM -E -x c /dev/null | grep __STDC_VERSION__)"
  BUNDLE_GEMFILE=/home/user/Ceedling/Gemfile bundle exec ruby /home/user/Ceedling/bin/ceedling "${@:-test:all}" --verbosity=obnoxious
  echo "### ceedling exit status $?"
} > "$HERE/work/$NAME.log" 2>&1
tail -1 "$HERE/work/$NAME.log"
