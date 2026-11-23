#!/bin/bash
# Launcher path cases. Each case runs this checkout's bin/ceedling: `clean` at obnoxious verbosity
# logs which installation launched and which mixins merged, then dumpconfig shows the merged :defines.
here="$(cd "$(dirname "$0")" && pwd)"
ln -sfn . "$here/proj/lnk"   # case E reaches one mixin through this symlink
C="BUNDLE_GEMFILE=/home/user/Ceedling/Gemfile bundle exec ruby /home/user/Ceedling/bin/ceedling"
run() { echo "=== $1 (cwd $(basename "$PWD"))"; shift
  ( eval "$C"' clean --verbosity=obnoxious "$@"' ) 2>&1 | grep -E "Launching|Using:|Merging|Logfile|EXCEPTION|ERROR" | sort -u
  ( eval "$C"' dumpconfig --stdout "$@" defines' ) 2>&1 | grep -E "FROM_" ; }
cd "$here/proj"
run "A. a name found in the project file's directory" --project cfg/project.yml
run "B. a mixin name holding a dot, my.extra.yml beside the project file" --project cfg/project.yml --mixin my.extra
run "C. a filename that sits only in a :load_paths directory" --project cfg/project_lp.yml --mixin lp.yml
run "D. the same mixin by name, :load_paths cfg/mixins, cwd proj" --project cfg/project_lp.yml --mixin lp
cd "$here"
run "D2. the same project and mixin name from the parent directory" --project proj/cfg/project_lp.yml --mixin lp
run "A2. a name in the project file's directory from the parent directory" --project proj/cfg/project.yml
cd "$here/proj"
run "E. one mixin file by two spellings, lnk -> ." --project cfg/project.yml --mixin twice.yml --mixin lnk/twice.yml
mkdir -p '~root'; cp cfg/project.yml '~root/project.yml'
run "F. --project through a directory literally named ~root" --project '~root/project.yml'
echo "=== G. --logfile through a directory literally named ~root"
( eval "$C"' clean --project cfg/project.yml --logfile "~root/gap12.log" --verbosity=obnoxious' ) 2>&1 | grep -E "Launching|Logfile|EXCEPTION"
ls -d '~root/gap12.log' /root/gap12.log 2>&1 | sed 's/^/   ls: /'
rm -f /root/gap12.log; rm -rf '~root'
ln -sfn /home/user/Ceedling '~root'
printf ':project:\n  :which_ceedling: ~root\n' > which_tilde.yml
run "H. :which_ceedling ~root, where ./~root is a symlink to this checkout" --project cfg/project.yml --mixin which_tilde.yml
rm -f '~root' which_tilde.yml
echo "=== I. project-file discovery from a subdirectory of the project"
cd "$here/proj/src" && ( eval "$C"' clean --verbosity=obnoxious' ) 2>&1 | grep -E "Launching|Using:|EXCEPTION"
rm -f "$here/proj/lnk"
