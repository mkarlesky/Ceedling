#!/bin/bash
# How Rake parses a task argument before a Ceedling task sees it, and what the CLI then selects
here="$(cd "$(dirname "$0")" && pwd)"
TASKS=('test:path[test\unit]' 'test:path[test\\unit]' 'test:pattern[\.c$]' 'test:pattern[test_\a]')
BUNDLE_GEMFILE=/home/user/Ceedling/Gemfile bundle exec ruby "$here/rake_args.rb" "${TASKS[@]}"
cd "$here/proj"
for t in "${TASKS[@]}"; do
  echo "=== $t"; ../run.sh "$t" --verbosity=obnoxious 2>&1 | grep -E "Launching|Parsing test_[A-Za-z_]+\.c for test case|Found no" | tr '\n' ';'; echo
done
