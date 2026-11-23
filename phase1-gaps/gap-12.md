# GAP-12: release, launcher and test-selection path handling

## Summary

This report inventories 18 path sites the earlier streams passed over. They cover the release build, the launcher in `bin/`, and the test-selection tasks. Release placement follows the governing rule. Each object, `.d` file and list file sits at its source's path from the project root, and each object finds its source again by decoding that path. The release build departs from the rule at its edges. A release source named like a vendor framework file is looked up by basename in the test build input, and a relative `:output` with `..` puts the artifact outside the build root. Artifacts are copied flat, so two with one basename overwrite each other. The launcher spells paths with `ProjectPaths.standardize` and then makes them absolute with `File.expand_path`. That pair reads a `~user` path two ways in `--project`, `--logfile` and `:which_ceedling`, and it dedupes mixins by text, so one file reached through a symlink merges twice. The test-selection tasks compare text. `test:path` takes any substring of a test's directory, so `unit` selects `test/community`. Four plugins copy the rule. The 40 findings are in `gap-12.json`. 39 were confirmed and one was revised. 14 are defects, none of them covered by an in-scope issue.

## What I ran

All runs used this checkout at 402e4912 through `bundle exec ruby bin/ceedling`, with `:which_ceedling` set to `/home/user/Ceedling`. Every captured run logs ` > Launching Ceedling from /home/user/Ceedling/`, except the cases that stop before the launch. `phase1-gaps/gap-12/README.md` lists each script and result file.

- **`rel/`** runs a release with sources inside and outside the project, an assembly file, a `_t_` directory, `:output: bin/app.out` and two same-named artifacts. It then runs `release:compile:` once per path spelling, with CException on, with a climbing `:output`, with a `:files` header, and with a source named `unity.c`.
- **`sel/`** runs `test:path`, `test:pattern`, `test:<file>`, `valgrind:` and `sanitize:` over tests in `test/unit`, `test/unit_extra`, `test/community`, the project root and `../outside_tests`. It also parses task arguments with Rake 13.2.1 directly.
- **`binx/`** runs the launcher cases: mixin names and filenames, load paths from two working directories, a symlinked mixin spelling, `~root` spellings, and discovery from a subdirectory.

## Inventory

The table follows stream 1's site format. These sites resolve build paths, task arguments and launcher settings rather than `#include` text, so the `""` vs `<>` column reads "none" throughout. Callers name release steps from `lib/ceedling/release_invoker/README.md`, the launcher's command flow, or the Rake task.

| # | Site | Inputs | Rule | Tie-break | Case | `""` vs `<>` | Miss | Callers |
|---|---|---|---|---|---|---|---|---|
| R1 | `ReleaseBuildPlanner#plan` `lib/ceedling/release_invoker/release_build_planner.rb:34-61` | `collection_release_build_input` and the link-only list, or one source path | each list goes through `mirror_build_objects` with `release: true`, then the two lists are joined | duplicates by `ProjectPaths.absolute` within a list `file_path_utils.rb:611`, then a text `uniq` across lists `:60` | exact | none | `DestinationCollision` raises within one list only | "Determining Objects to be Built" |
| R2 | `compile_release_component` `release_build_executor.rb:115-177` | one object path | `find_build_input_file` with `RELEASE_SYM`. The vendor-framework name branch comes first `file_finder.rb:177-185`, then the decoded exact query `:212`, `:352-365` | exact absolute match before tail match `file_finder.rb:256-265` | exact | none | `:error` | "Building Objects" |
| R3 | `.d` and list files `file_path_utils.rb:185-202` | an object path | `.d` mirrors the object's subpath below the dependencies root. The list file sits beside the object | none | exact | none | none | "Building Objects" |
| R4 | `ReleaseBuildExecutor#link` `release_build_executor.rb:46-89` | `project_release_build_target`, the object list | libraries split off by path ending `:227-242`. The target is linked at its configured spelling, and its directory is created `:64` | none | exact | none | none | "Building Release Artifact" |
| R5 | `ReleaseBuildExecutor#artifactinate` `release_build_executor.rb:91-108` | the target, the map, `:release_build` ↳ `:artifacts` | `FileWrapper#cp` into `project_release_artifacts_path`, flat | the last copy wins | exact | none | a missing file is skipped after `exist_with_retry?` | "Collecting Artifacts" |
| R6 | `release:compile:` rule `lib/ceedling/rakefiles/release/rules_release.rake:26-34` | the task name | strip the task root, `find_source_file` by trailing segments, non-strict `file_finder.rb:237-239`, `:468-481` | the first in collection order, with a NOTICE | exact | none | `:error` | Rake rule |
| R7 | `release:assemble:` rule `rules_release.rake:37-47` | the task name | as R6 with `find_assembly_file` | as R6 | exact | none | `:error` | Rake rule |
| B1 | `Projectinator#load` `bin/projectinator.rb:31-84` | `--project`, `CEEDLING_PROJECT_FILE`, the working directory | the first given wins. Else `./project.yml` or `./ceedling.yml` in the working directory only | both defaults present raises | file system | none | raises | each command that loads a project, through `Composinator#loadinate` |
| B2 | mixin lookup `bin/composinator.rb:30-34`, `bin/mixin_resolvinator.rb:62-112` | `:mixins` ↳ `:enabled`, `--mixin`, `:load_paths` | a value with an extension or `/` is a path from the working directory `bin/path_validator.rb:33-36`. A name is joined with each load path, then the project file's directory, then Unity's targets, for each YAML extension | the first existing file | file system | none | logs an error, then raises | `loadinate` |
| B3 | mixin dedupe `bin/mixinator.rb:91`, `:131-137`, `bin/composinator.rb:34` | the assembled mixin list, load paths, env vars | `File.expand_path` text | the first occurrence | exact | none | none | `loadinate` |
| B4 | log path `bin/cli_helper.rb:216-259` | `:project` ↳ `:build_root`, `--log`, `--logfile` | `<build_root>/logs/ceedling.log` or `--logfile`, then `File.expand_path` and `mkdir` | none | file system | none | an empty build root raises | `build`, `dumpconfig`, `check`, `environment`, task listing `bin/cli_handler.rb:226`, `:322`, `:353`, `:378`, `:643` |
| B5 | `InstallationSelector#select` `bin/installation_selector.rb:24-72` | `WHICH_CEEDLING`, `:which_ceedling`, `./vendor/ceedling` | the first set wins. `gem` in any case means the launcher. A path is checked with `directory?`, then expanded | none | `gem` folds case | none | raises | `Launchinator#launch` and `#resolve` |
| B6 | plugin load paths `lib/ceedling/rake_app/rakefile_component_resolver.rb:46-80` | `:plugins` ↳ `:load_paths` | inline Ruby expansion and `standardize`, then the first `<path>/<plugin>/<plugin>.rake` | text `uniq!` | file system | none | the plugin is skipped | `CliHelper#build_rake_task_registry` `bin/cli_helper.rb:123-133` |
| T1 | `test:pattern` `lib/ceedling/rakefiles/tests/tasks_tests.rake:37-47` | the Rake argument | `test =~ /#{regex}/` over `COLLECTION_ALL_TESTS` | none | exact | none | logs an error | Rake task |
| T2 | `test:path` `tasks_tests.rake:50-60` | the Rake argument | `File.dirname(test).include?(arg)` after `\` to `/` | none | exact | none | logs an error, a missing argument raises | Rake task |
| T3 | sanitize copies `plugins/sanitize/sanitize.rake:59-89` | as T1, T2 | as T1 with `Regexp.new`, and as T2 | none | exact | none | as T1, T2. A missing pattern raises | Rake task |
| T4 | valgrind copies `plugins/valgrind/valgrind.rake:60-90` | as T1, T2 | as T3 | none | exact | none | as T3 | Rake task |
| T5 | `test:<file>` rule `lib/ceedling/rakefiles/tests/rules_tests.rake:10-25` | the task name | `TestTaskName.test_name`, `..` resolved against `''`, strict trailing-segment match `file_finder.rb:80-83` | an ambiguous name raises | exact | none | `:error` | Rake rule |

The gcov and bullseye copies of T1 and T2 at `plugins/gcov/gcov.rake:51-81` and `plugins/bullseye/bullseye.rake:51-81` match T3. GAP-04 covered them.

## Spellings

Each row gives the forms a path takes in and out of a site and where text is compared.

| # | Input forms | Output form | Text comparisons |
|---|---|---|---|
| R1 | collection entries, relative to the working directory, with `../` for outside the project. The link-only list holds the bare name `CException.o` `configurator_builder.rb:327` | `build/release/out/<encoded dir>/<name>.o`, relative. `..` becomes `_up_`, and `_t_` stays as it is | text `uniq` across the two lists `release_build_planner.rb:60` |
| R2 | an R1 object | the collection entry, as collected | the vendor branch compares basenames `file_finder.rb:179`. The exact query compares `ProjectPaths.absolute` |
| R3 | an R1 object | `build/release/dependencies/<subpath>/<name>.d` and `<object dir>/<name>.<list ext>` | none, containment by directory `path_mirror.rb:68-71` |
| R4 | `:output`, standardized and joined under `build/release` unless absolute `configurator_builder.rb:139-149`, `:360-362` | the same text, never normalized. `build/release/../../escaped.out` is kept as written | the library split matches the path's ending `release_build_executor.rb:229` |
| R5 | the R4 target, the map, `:artifacts` as standardized `configurator.rb:668-675` | `build/artifacts/release/<basename>` | none |
| R6, R7 | bare name, trailing path, `./`-prefixed, `\`-separated, absolute, `../` as collected | the collection entry | an absolute query compares `File.expand_path` text `path_matcher.rb:53-58`. A relative one compares exact trailing segments `:176-179`. `..` is not resolved |
| B1 | `--project` or the env var, standardized. The defaults are `./project.yml` and `./ceedling.yml` | an absolute path from `File.expand_path`. `:history` holds the standardized spelling, or the `./` constant for a default | none |
| B2 | load paths and `:enabled` after expansion and `standardize`, relative to the working directory. The project file's directory is absolute | `File.join(load path, name + ext)`, so relative or absolute by its load path | the name-or-path test is on text `path_validator.rb:33-36` |
| B3 | as B2 | the first of each `File.expand_path` key | `File.expand_path` text, with no symlink resolution and no case folding |
| B4 | the build root standardized, `--logfile` standardized `bin/cli_handler.rb:199` | absolute, from `File.expand_path` | none |
| B5 | the value stripped, then standardized `installation_selector.rb:42`, `:50`, `:62` | `File.expand_path` in `Installation#initialize` and `AppConfig#set_paths` | `casecmp?( 'gem' )` `:28`. `Installation#==` compares `File.realpath` |
| B6 | the entry expanded and standardized | as standardized | text `uniq!` |
| T1, T3, T4 | Rake's unescaped argument | the matching collection entries | regex on the entry's text, relative and with its extension |
| T2, T3, T4 | Rake's unescaped argument, `\` swapped for `/` | as T1 | `String#include?` on `File.dirname(test)` |
| T5 | bare, trailing, `./`, `\`, absolute, `../` | the collection entry | as R6, after `..` is resolved against `''` |

Rake 13.2.1 unescapes every `\x` in a bracketed argument before a task sees it `phase1-gaps/gap-12/sel/rake_args_results.txt`. A single `\` never reaches T1 to T4. A task name with no brackets keeps its backslashes, so R6 and T5 see them.

## Defects

The defects are listed most severe first. None is covered by an in-scope issue.

- **GAP12-07, medium.** A release object whose basename plus `.c` names a vendor framework file goes to the vendor-framework branch first. That branch has no release guard `file_finder.rb:177-185`, so it matches by basename in `collection_existing_test_build_input`. A release with `src/mylib/unity.c` builds from a clean tree. Once a test build fills `build/vendor`, the same release stops with `Ambiguous file reference 'unity.c'` `rel/vendor_name_sequence.txt`. The object's own path names its source exactly, but the name is tried first.
- **GAP12-34, medium.** `test:path` keeps a test when its directory text contains the argument `tasks_tests.rake:53`. This departs from containment by whole directories `PATH_HANDLING.md:24`. `unit` selects `test/community`, and `test/unit` selects `test/unit_extra`. `./test/unit`, `test/unit/` and an absolute path select nothing. The sanitize, valgrind, gcov and bullseye copies behave the same.
- **GAP12-10, low.** A relative `:output` is joined under `build/release` with no containment check `configurator_builder.rb:360-362`. `../../escaped.out` links into the project directory.
- **GAP12-13, low.** `artifactinate` copies every artifact into one flat directory. Two `:artifacts` named `notes.txt` leave one file, and the later one wins with no message.
- **GAP12-14, low.** Each assembled object waits 0.37 s for a `.d` file that `as` never writes. A release whose linker writes no map waits again for the map. Both log at NORMAL.
- **GAP12-16, low.** `release:compile:dup.c` compiles the first of two `dup.c` files with a NOTICE. `test:<file>` raises on the same ambiguity.
- **GAP12-17, low.** `release:compile:../proj/src/drv/uart.c` names a real source but fails, since `find_source_file` never resolves `..`.
- **GAP12-21, GAP12-22, GAP12-23, low.** `--project`, `CEEDLING_PROJECT_FILE`, `--logfile` and `:which_ceedling` keep `~user` literal through `standardize`, then hand it to `File.expand_path`, which reads it as that user's home. `--logfile '~root/gap12.log'` wrote `/root/gap12.log`. `ProjectPaths.absolute` guards against this `project_paths.rb:146-151`, but these sites do not use it.
- **GAP12-29, low.** `--mixin twice.yml --mixin lnk/twice.yml`, with `lnk` a symlink to `.`, merges one file twice. The dedupe compares `File.expand_path` text.
- **GAP12-33, low.** `test:pattern` with no argument runs every test. The plugin copies raise on `Regexp.new(nil)`.
- **GAP12-36, low.** The docs promise `\` as a `test:path` separator, but Rake removes a single backslash first. `test:pattern[\.c$]` reaches the task as `.c$`.
- **GAP12-37, low.** `test:path` with no argument raises `undefined method 'tr' for nil`.

## Other departures

These findings are not defects, but each puts a name or text in place of a path.

- **GAP12-05.** The CException link-only object is the bare name `CException.o`. It lands on the vendored source's object only because both encode to an empty subpath.
- **GAP12-11.** A release entry counts as a library when its path ends in a library extension.
- **GAP12-18.** `PathMatcher` compares an absolute query as `File.expand_path` text, with no symlink resolution and no case folding on Windows.
- **GAP12-25.** `gem` stands for the launcher, so a directory named `gem` needs another spelling.
- **GAP12-28.** A mixin value is a path when it has any extension or a `/`. `my.extra` is never looked up by name, and `lp.yml` is never looked up in load paths. The docs define this split.
- **GAP12-35.** The docs say `test:path` matches a test's path, but only its directory is tested.
- **GAP12-39.** `test:<file>` refuses `../proj/test/unit/test_a.c`, which re-enters the project.

The fix already in place is listed as GAP12-31. `prepare_plugin_load_paths` takes an `expand:` lambda `rakefile_component_resolver.rb:46`, and `bin/cli_helper.rb:128` passes Ruby expansion, so `bin/` and `lib/` read plugin load paths alike.

## Against the governing rule

Release compiles hand include resolution to GCC. The planner passes `:paths` ↳ `:include` as `-I` `release_build_planner.rb:51`, so quoted and angle-bracket includes resolve as the compiler does. A `:files` ↳ `:include` header is unreachable, as `docs/mkdocs/configuration/reference/files.md:119` says (GAP12-19). None of the Ceedling conventions applies in a release.

Nothing in these sites ties a generated file to one test. Release output has no per-test directory. The selection tasks only pass test paths to `TestInvoker`.

## Open questions

- **Symlinked `:which_ceedling`.** Plugin paths come from `File.expand_path` of the selected root `bin/app_cfg.rb:140-148`. `BuildSubpath::INSTALLATION_ROOT` comes from `__dir__`, which Ruby resolves to a real path. A `:which_ceedling` reached through a symlink may therefore place a plugin's files by `_up_` rather than `_ceedling_`. That is an inference. I did not run it.
- **Release on Windows.** Every run here was on Linux. GAP12-18's case behavior and the `_abs_` placement of a release source on another drive come from reading the code.
- **The `:artifacts` example.** `release-build.md` shows `build/release/out/c/top_secret.s19`. The `out/c/` directory is not where today's placement puts output. Whether the example means a tool's own output path is open.
