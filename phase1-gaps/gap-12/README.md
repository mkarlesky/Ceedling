# GAP-12 scratch projects

Each directory holds a small project, the scripts that ran it, and what they printed. Every script runs this checkout's `bin/ceedling` through `bundle exec`, and each project sets `:project: :which_ceedling: /home/user/Ceedling`. Each captured result shows ` > Launching Ceedling from /home/user/Ceedling/`, except cases that stop before the launch.

## rel/: release placement and lookup

- `proj/` has sources in `src/`, `src/drv/`, `src/other/`, `src/_t_/`, one in `../shared/`, an assembly file, `:output: bin/app.out`, and two `:artifacts` sharing the basename `notes.txt`.
- `run.sh <args>` runs Ceedling in `proj/`.
- `logs_release_full.log` is `ceedling release --verbosity=obnoxious` from a clean build.
- `release_tree.txt` lists the files below `build/` after that build, and what the copied `notes.txt` holds.
- `logs_release_compile.txt` is one clean `release:compile:<spelling>` run per spelling. The run that tested `dup.c` had `src/drv/dup.c` and `src/other/dup.c` present.
- `cexception_release.log` is a release with `--mixin "=project: {use_exceptions: true}"`.
- `output_climb.log` is a release with `--mixin "=release_build: {output: ../../escaped.out}"`. The link wrote `proj/escaped.out`, which was then deleted.
- `files_include_release.log` is a release where `src/main.c` included `ext.h`, found only through `--mixin "=files: {include: [extinc/ext.h]}"`.
- `vendor_name_sequence.txt`, `vendor_name_1.log`, `vendor_name_4_test.log` and `vendor_name_5.log` are a release with `src/mylib/unity.c`, then `test:all` with a test path added, then the release again.

The temporary sources for these cases were removed afterwards, so `proj/` holds only the base project.

## sel/: test selection

- `proj/` has tests at `test/unit/`, `test/unit_extra/`, `test/community/`, the project root through `:files: :test:`, and `../outside_tests/`.
- `select.sh` runs each `test:path`, `test:pattern`, `test:<file>`, `valgrind:` and `sanitize:` case. `selection_results.txt` shows what each one selected, one `selected <test>` per test the task parsed.
- `collection_spelling.txt` shows the test file spellings a `test:pattern[.]` build compiled.
- `rake_args.sh` and `rake_args.rb` show how Rake 13.2.1 parses a backslash in a task argument. `rake_args_results.txt` is their output.

## binx/: launcher paths

- `proj/cfg/project.yml` enables a mixin by name. `proj/cfg/project_lp.yml` adds `:mixins: :load_paths: [cfg/mixins]`.
- `bin_cases.sh` runs cases A to I and `bin_results.txt` holds their output. Each case's log lines are sorted with `sort -u`, so their order is not the order of the run.
- Cases F to H make a directory or symlink literally named `~root` in `proj/` and remove it afterwards. Case G wrote `/root/gap12.log`, which the script then deleted.
