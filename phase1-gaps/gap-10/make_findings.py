#!/usr/bin/env python3
"""Writes phase1-gaps/gap-10/findings_src.json, the unverified GAP-10 findings.

Each finding is one checkable claim. `Verdict:` at the start of a claim is the ledger verdict
(kept, broken, partly kept, untestable). Run from anywhere. Needs no network.
"""
import json, os

D = "docs/mkdocs/"
G = "phase1-gaps/gap-10/"
C = G + "collide/"

F = []


def add(title, claim, evidence, kind="promise", issues=None, severity="none", track="unknown"):
    F.append({
        "id": "GAP10-%02d" % (len(F) + 1),
        "kind": kind,
        "title": title,
        "claim": claim,
        "evidence": evidence,
        "issues": issues or [],
        "severity": severity,
        "track_hint": track,
        "stream": "gap-10",
    })


# ---------------------------------------------------------------- same-named _AT modules
add("Two same-named _AT Partials with the same static name build and pass",
    "Verdict: kept. One test holds `#include TEST_PARTIAL_PUBLIC_MODULE_AT(a, util)` and "
    "`#include TEST_PARTIAL_PUBLIC_MODULE_AT(b, util)`. Each `util.c` defines a static `util_helper` and a public "
    "function (`a_pub`, `b_pub`). The build compiles, links and passes (TESTED 1, PASSED 1). Ceedling writes "
    "`a/ceedling_partial_util_impl.{c,h}` and `b/ceedling_partial_util_impl.{c,h}` below "
    "`build/test/partials/test/test_collide/_t_/`. Their include guards differ (`GENB59956D4_A_CEEDLING_PARTIAL_UTIL_IMPL_H_CEEDLING` "
    "and `GEN7118F419_B_...`). PUBLIC mode leaves the static out of the generated source, so the shared static name never "
    "meets itself.",
    [C + "gen.sh (variant v1_public_same_static)", C + "results.txt (v1_public_same_static exit=0)",
     C + "logs/v1_public_same_static.excerpt.txt (TESTED, PASSED)",
     C + "excerpts/v1_a_impl.h:1", C + "excerpts/v1_b_impl.h:1", C + "excerpts/v1_a_impl.c:1-5",
     "lib/ceedling/filesystem/file_path_utils.rb:496-503"],
    kind="test")

add("Same-named public or selected functions in two _AT modules fail at link",
    "Verdict: kept (inherent). Three variants fail with `multiple definition` at link, never at compile. "
    "(v2) both `util.c` define a public `util_pub`. (v1b) both public functions call `util_helper` and the test selects it "
    "with `TEST_PARTIAL_CONFIG_AT` for each module. (v3) both modules use `TEST_PARTIAL_PRIVATE_MODULE_AT`, which promotes "
    "the same-named statics. The fixture comment says the same. Directory qualification keeps the generated files apart "
    "but cannot keep the function names apart.",
    [C + "results.txt (v1b, v2, v3 exit=1)", C + "logs/v2_public_same_pub.excerpt.txt",
     C + "logs/v1b_public_calls_static.excerpt.txt", C + "logs/v3_private_same_static.excerpt.txt",
     "assets/fixtures/same_named_modules/src/drivers/uart/config.c:3-5"],
    kind="test", severity="low")

add("A variable name used by both same-named modules breaks compile or link",
    "Verdict: kept (inherent). When both `a/util.c` and `b/util.c` hold `static struct { int count; } s_ctx;`, the test "
    "fails to compile with `conflicting types for 'ceedling_partial_util_s_ctx_t'` and `conflicting types for 's_ctx'`. "
    "Both types headers (`a/` and `b/`) write `typedef struct { int count; } ceedling_partial_util_s_ctx_t;`. "
    "With a plain `static int s_count;` in both (no type) the build compiles and fails at link with `multiple definition`. "
    "With distinct variable names (`a_ctx`, `b_ctx`) it builds and passes. So the module-name-only type name collides only "
    "when the variable name also collides, and that variable collides without the type.",
    [C + "results.txt (v4, v7 exit=1; v5 exit=0)", C + "logs/v4_public_same_var.excerpt.txt",
     C + "logs/v7_public_same_plain_var.excerpt.txt", C + "logs/v5_public_distinct_var.excerpt.txt",
     C + "excerpts/v4_a_types.h:6", C + "excerpts/v4_b_types.h:6", "lib/ceedling/partials/partials.rb:93-94"],
    kind="test", severity="low")

add("Mock Partials of same-named modules stay apart only through :mock_name_include_folder",
    "Verdict: kept (default on). `MOCK_PARTIAL_PUBLIC_MODULE_AT(a, util)` and `(b, util)` in one test build and pass. "
    "CMock names the lifecycle functions `a_Mockceedling_partial_util_interface_Init` and `b_...`, and the runner calls "
    "both. With `:cmock` ↳ `:mock_name_include_folder: FALSE` the same test fails at link with `multiple definition of "
    "Mockceedling_partial_util_interface_Init`, `_Verify` and `_Destroy`. The setting defaults to true in Ceedling and to "
    "false in CMock.",
    [C + "results.txt (v6 exit=0, v6b exit=1)", C + "excerpts/v6_mock_decls.txt", C + "excerpts/v6_runner_head.c:33-34",
     C + "logs/v6b_mock_both_no_folder.excerpt.txt", "lib/ceedling/defaults.rb:409", "vendor/cmock/lib/cmock_config.rb:18"],
    kind="test", severity="low")

add("The module name in generated Partial type names carries no directory",
    "Verdict: kept. `Partials.type_name` folds `File.basename(module_name)`, so modules `a/util` and `b/util` both give "
    "`ceedling_partial_util_<variable>_t`. The experiment shows the same typedef name in both generated types headers. "
    "`PARTIAL_TYPE(util, s_ctx)` therefore cannot say which module it means.",
    [D + "testing-guide/partials/variables.md:279", D + "reference/partials-macros.md:112-113",
     "lib/ceedling/partials/partials.rb:86-94", "lib/ceedling/ceedling.h:32-33",
     C + "excerpts/v4_a_types.h:6", C + "excerpts/v4_b_types.h:6"],
    severity="low")

add("A character a C identifier cannot hold becomes an underscore in Partial type names",
    "Verdict: kept. `CIdentifier.fold` replaces each `\\W` character with `_`, one for one, and `Partials.type_name` applies "
    "it to the module's basename. `PARTIAL_TYPE` and `PARTIAL_LOCAL_TYPE` paste their arguments as tokens, so a test author "
    "writes the folded spelling (`my_sensor`), as the docs say.",
    [D + "testing-guide/partials/variables.md:279-282", D + "reference/partials-macros.md:112-113",
     "lib/ceedling/c_identifier.rb:17-19", "lib/ceedling/partials/partials.rb:93-94", "lib/ceedling/ceedling.h:32-33"])

add("A promoted function-scoped static is named from the function and variable, never the module",
    "Verdict: kept. The promoted name is `partial_<function>_<variable>` and carries no module part. File-scoped statics "
    "keep their own names and are declared `extern` in `_impl.h`. The docs promise uniqueness only among functions of one "
    "module. Two modules with a same-named function cannot be in one test in any case.",
    [D + "testing-guide/partials/variables.md:126-140", D + "reference/partials-macros.md:78-90",
     "lib/ceedling/partials/partializer_helper.rb:299-301", "lib/ceedling/ceedling.h:25",
     C + "excerpts/v4_a_impl.h:10"])

add("A Partial module name that is a predefined macro is replaced before it names the file",
    "Verdict: broken. In a GCC build the compiler predefines `unix` as 1. A test with "
    "`#include TEST_PARTIAL_PUBLIC_MODULE(unix)` and a `unix.c` module preprocesses to "
    "`#include \"ceedling_partial_1_impl.h\"`. Ceedling reads the directive as written and generates "
    "`ceedling_partial_unix_impl.{c,h}`. It also writes an empty `ceedling_partial_1_impl.h`. The test links without the "
    "module and fails with `undefined reference to 'unix_pub'`, under a notice that blames missing `#include` lines. "
    "`__PARTIALS_EXPAND(module)` expands the argument, and `_validate_module!` checks spelling only. "
    "This is the mechanism of #1460, which names the directory argument. "
    "The `_AT` module argument passes through `__PARTIALS_JOIN`, whose indirection also expands macros. "
    "That path was inferred and not built.",
    [C + "results.txt (v8_module_named_unix exit=1)", C + "logs/v8_module_named_unix.excerpt.txt",
     C + "excerpts/v8_partials_dir.txt", C + "excerpts/v8_ceedling_partial_1_impl.h:1",
     C + "excerpts/v8_preprocessed_test_head.c:3", "lib/ceedling/ceedling.h:21-22", "lib/ceedling/ceedling.h:40",
     "lib/ceedling/partials/partializer_config.rb:276-300"],
    kind="defect", issues=[], severity="medium")

add("Generated Partial headers include their siblings by bare filename",
    "Verdict: kept, by the compiler's includer-directory rule. `a/ceedling_partial_util_impl.h` holds "
    "`#include \"ceedling_partial_util_types.h\"` and `a/ceedling_partial_util_impl.c` holds "
    "`#include \"ceedling_partial_util_impl.h\"`, with no directory. The test compile puts both "
    "`-I build/.../_t_/a` and `-I build/.../_t_/b` on the command line. Each bare include finds its own sibling only "
    "because GCC checks the includer's directory before the `-I` list. A resolver that skips the includer's directory "
    "would pick the first `-I` entry (`a/`) for `b/`'s include.",
    [C + "excerpts/v4_a_impl.h:6", C + "excerpts/v1_a_impl.c:2", C + "excerpts/v4_compile_command.txt",
     "lib/ceedling/generators/partial_header_writer.rb:41-50", "lib/ceedling/generators/partial_source_writer.rb:59-63"],
    kind="mechanism", issues=["1464"], severity="low")

add("The runner of a test naming two same-named _AT Partials includes one impl header, by bare name",
    "Verdict: partly kept (observed, cause not traced). The test names `a/ceedling_partial_util_impl.h` and "
    "`b/ceedling_partial_util_impl.h`. Its generated runner holds one `#include \"ceedling_partial_util_impl.h\"` with no "
    "directory. The bare name resolves to `a/` by `-I` order. The test passes, since the runner needs neither header. "
    "I did not trace which step collapses the two includes. The runner spelling comes from `include.include_path || "
    "include.filename`.",
    [C + "excerpts/v1_runner_head.c:5", C + "gen.sh (variant v1_public_same_static)",
     "lib/ceedling/generators/generator_test_runner.rb:56-62", "lib/ceedling/test_invoker/test_runner_generatinator.rb:114-137"],
    kind="test", severity="low")

add("Same-named modules named by directory stay distinct modules in the Partials config",
    "Verdict: kept. `_module_key` joins a qualified macro's directory segments to the module with `File.join`, so "
    "`./drv` and `drv` give one module and `a/util` and `b/util` give two. Validation rejects an empty or quoted module, a "
    "module carrying a path, and a directory that is empty, quoted, absolute, or holds `..`. The experiment confirms two "
    "distinct generated Partials for the two modules.",
    ["lib/ceedling/partials/partializer_config.rb:250-270", "lib/ceedling/partials/partializer_config.rb:276-300",
     "lib/ceedling/partials/partializer_config.rb:323-355", C + "results.txt (v1_public_same_static exit=0)"],
    severity="none")

add("Generated Partial filenames for _AT macros carry the macro's directory, which the docs table omits",
    "Verdict: partly kept. The overview table lists `ceedling_partial_<module>_impl.h` and the sibling patterns. For "
    "`_AT` macros the file is `<dir>/ceedling_partial_<module>_impl.h`: `form_partial_filename` puts the directory "
    "first and the prefix on the basename. The unqualified macros name a file with no directory.",
    [D + "testing-guide/partials/overview.md:84-89", "lib/ceedling/filesystem/file_path_utils.rb:496-503",
     "lib/ceedling/ceedling.h:40", "lib/ceedling/ceedling.h:68", C + "excerpts/v1_a_impl.h:1"])

add("Partials are generated into a partials build directory",
    "Verdict: kept. Generated Partial files sit below `<build root>/test/partials/<test path>/_t_/`, one root per test, "
    "mirrored by directory for `_AT` macros.",
    [D + "testing-guide/partials/overview.md:55-56", "lib/ceedling/filesystem/file_path_utils.rb:305-307",
     C + "excerpts/v4_compile_command.txt", C + "logs/v1b_public_calls_static.excerpt.txt"])

add("A plain Partial build links only the Partial, never the module's own object",
    "Verdict: kept. The linker command for the same-named experiment lists the test object, `a/` and `b/` "
    "`ceedling_partial_util_impl.o`, the runner and Unity. No object of `src/a/util.c` or `src/b/util.c` is linked.",
    [D + "testing-guide/partials/overview.md:23-24", D + "testing-guide/partials/example.md:93-97",
     C + "logs/v1b_public_calls_static.excerpt.txt (Executed Command line)"],
    kind="test")

add("The unqualified Partial macro with two same-basename modules picks the first by search-path priority",
    "Verdict: partly kept. The docs say the macros \"expand into the unique names of the generated Partials header "
    "files\". `TEST_PARTIAL_PUBLIC_MODULE(util)` with `src/a/util.c` and `src/b/util.c` names one Partial. Ceedling "
    "logs `Multiple files matched 'util.c' but chose 'src/a/util.c' by search-path priority` and the test passes against "
    "`a/`'s code. Only the `_AT` macros name two.",
    [D + "testing-guide/partials/configuration.md:48", C + "results.txt (v9_unqualified_ambiguous exit=0)",
     C + "logs/v9_unqualified_ambiguous.excerpt.txt", "lib/ceedling/filesystem/file_finder_helper.rb:33-47"],
    kind="test", severity="low")

# ---------------------------------------------------------------- command line
add("test:path matches a substring of the test's directory, not of its whole path",
    "Verdict: partly kept. The docs say \"tests whose path contains the given string\". The code tests "
    "`File.dirname(test).include?(arg)` on the project-relative test path, with `\\` turned into `/`. With tests in "
    "`test/unit`, `test/unit_extra` and `test/integration`: `test:path[unit]` ran 2 tests (substring, so `unit_extra` too), "
    "`test:path[nit]` ran 2, `test:path[t/in]` ran 1, `test:path[unit/]` found none (no trailing separator in a dirname), "
    "`test:path[test_foo.c]` found none (filename excluded) and `test:path[Test]` found none (case).",
    [D + "reference/command-line.md:286-292", D + "getting-started/command-line.md:458-465",
     "lib/ceedling/rakefiles/tests/tasks_tests.rake:49-56", G + "cli/results.txt", G + "cli/run_cli.sh", G + "cli/gen_cli.sh"],
    kind="promise", severity="low")

add("test:pattern matches a regular expression against the project-relative test path",
    "Verdict: kept. The code applies `test =~ /#{regex}/` to each collected test path. Collected paths are relative to the "
    "project, so `^test/unit/` matched one test and the absolute directory of the project is never part of the text "
    "(`test:path[gap-10]` found nothing).",
    [D + "reference/command-line.md:278-284", D + "getting-started/command-line.md:444-452",
     "lib/ceedling/rakefiles/tests/tasks_tests.rake:37-47", G + "cli/results.txt", G + "cli/run_cli.sh", G + "cli/gen_cli.sh"],
    severity="none")

add("test:<name> takes as much trailing path as needed and names every match when ambiguous",
    "Verdict: kept. With `test/unit/test_foo.c`, `test/integration/test_foo.c` and `test/unit_extra/test_foo.c`, "
    "`test:test_foo.c` stops with `Ambiguous file reference 'test_foo.c' found. Include more trailing path` and lists all "
    "three. `test:unit/test_foo.c` and `test:unit\\test_foo.c` each run one test. The lookup is `PathMatcher` in strict mode.",
    [D + "getting-started/command-line.md:386-396", "lib/ceedling/filesystem/file_finder.rb:80-83",
     "lib/ceedling/filesystem/path_matcher.rb:20-37", "lib/ceedling/rakefiles/tests/rules_tests.rake:10-24",
     G + "cli/results.txt"],
    kind="test")

add("The bullseye: and gcov: tasks reuse the test: name, pattern and path rules",
    "Verdict: kept. Both plugins resolve a single-file task with `TestTaskName.test_name` and "
    "`find_test_file_from_name`, so trailing-path disambiguation matches `test:`. Their `path` tasks use the same "
    "`File.dirname(test).include?` test, so the `test:path` limits apply to them too. Read only. I did not run these plugins.",
    [D + "plugins/bullseye/index.md:28-38", D + "plugins/gcov/overview.md:37-39",
     "plugins/bullseye/bullseye.rake:70-90", "plugins/gcov/gcov.rake:70-90"],
    kind="promise")

add("ceedling paths:header does not exist; the task is paths:include",
    "Verdict: broken. The reference lists `ceedling paths:header`. Ceedling defines a `paths:<name>` task for each key of "
    "`:paths`, and the standard sections are test, source, include and support. `ceedling paths:header` ends with "
    "`Unrecognized build task`. `paths:include` lists the include paths. The getting-started page repeats the error by "
    "listing `files:*` variants under `paths:*`.",
    [D + "reference/command-line.md:177-182", D + "getting-started/command-line.md:331-337",
     "lib/ceedling/rakefiles/base/tasks_filesystem.rake:72-80", G + "deps/cli_tasks.txt"],
    severity="low")

add("files:assembly exists even when assembly support is off",
    "Verdict: broken. Both command line pages say the task is only available when assembly support is enabled. The "
    "`files` namespace creates a task for each of tests, source, assembly, headers and support unconditionally. "
    "With `:test_build` ↳ `:use_assembly: FALSE` and no release assembly, `ceedling files:assembly` runs and prints "
    "`Assembly files: None`.",
    [D + "reference/command-line.md:202-204", D + "getting-started/command-line.md:361-363",
     "lib/ceedling/rakefiles/base/tasks_filesystem.rake:93-98", G + "deps/cli_tasks.txt"],
    severity="none")

# ---------------------------------------------------------------- dependencies plugin
add("The Dependencies doc names a files:include task that does not exist",
    "Verdict: broken. The doc lists `files:include` as \"Lists every header file Ceedling has found, including those "
    "from dependencies\". The core defines `files:header` for that. `ceedling files:include` ends with `Unrecognized build "
    "task`. `paths:include` is real.",
    [D + "plugins/dependencies.md:245-251", "lib/ceedling/rakefiles/base/tasks_filesystem.rake:94-98",
     G + "deps/results.txt", G + "deps/cli_tasks.txt"],
    severity="low")

add("Dependency include directories and globs are added to the header file collection as literal entries",
    "Verdict: defect. `include_files` maps every `:includes` entry, whether a header, a directory or a glob, to a path "
    "below the artifact path. `Dependencies#config` and `#add_headers_and_sources` push all of them into "
    "`collection_all_headers`. With `:includes: [inc/**, single/one.h]`, `files:header` lists `dependencies/Vend/inc/**` "
    "as a header file.",
    ["plugins/dependencies/lib/dependency_spec.rb:103", "plugins/dependencies/lib/dependency_spec.rb:131-133",
     "plugins/dependencies/lib/dependencies.rb:53-55", "plugins/dependencies/lib/dependencies.rb:146-149",
     G + "deps/cli_tasks.txt", G + "deps/gen_deps.sh"],
    kind="defect", severity="low")

add("A dependency's :artifact path skips :source and :fetch when :build is left out",
    "Verdict: broken. The docs say `:artifact` falls back to `:build`, and `:build` falls back to `:source`, then "
    "`:fetch`. The code reads `@paths[:artifact] || @paths[:build] || default_path`. A dependency with only "
    "`:source: ext/src` gets build `ext/src` but artifact `dependencies/<name>`. In the build, `:includes: [inc/**]` of "
    "such a dependency appears in `paths:include` as `dependencies/Vend/inc`, not `vendor_dep/inc`. A fix changes where "
    "artifacts are looked for, so it is a BreakingChanges candidate.",
    [D + "plugins/dependencies.md:71-80", "plugins/dependencies/lib/dependency_spec.rb:72-75",
     G + "dependencies_paths.txt", G + "deps/results.txt", G + "deps/cli_tasks.txt"],
    kind="promise", severity="medium")

add("dependencies:clean misses a default path that a fetch used",
    "Verdict: partly kept. The doc says clean removes \"every one of its working paths\". `working_paths` returns the "
    "configured paths only (`@paths` less `:deploy`), and the default `dependencies/<name>` is used only when a path "
    "falls back to it. With only `:artifact: out` configured, fetch and source resolve to `dependencies/<name>` while "
    "clean removes only `out`. With only `:build: b`, clean removes only `b`. Fetch then sees a non-empty fetch path and skips.",
    [D + "plugins/dependencies.md:231-233", "plugins/dependencies/lib/dependency_spec.rb:72-85",
     "plugins/dependencies/lib/dependencies.rb:94-96", "plugins/dependencies/lib/dependencies.rb:194-198",
     G + "dependencies_paths.txt"],
    kind="promise", severity="medium")

add("Dependency artifacts resolve against the artifact path, absolute names stand, and ~ expands",
    "Verdict: kept. `artifact_at` standardizes the entry, which expands a leading `~`, then keeps an absolute path as "
    "written and joins any other below `artifact_path`.",
    [D + "plugins/dependencies.md:89-91", "plugins/dependencies/lib/dependency_spec.rb:140-144",
     "lib/ceedling/filesystem/project_paths.rb:44-50", "lib/ceedling/filesystem/project_paths.rb:115-117"])

add("dependencies:deploy copies dynamic libraries and executables beside the release executable by default",
    "Verdict: kept. The destination is `spec.deploy_path(File.dirname(PROJECT_RELEASE_BUILD_TARGET))`. The target lies "
    "below `<build root>/release/` (for example `build/release/project.out`), not in the artifacts directory.",
    [D + "plugins/dependencies.md:80", D + "plugins/dependencies.md:237-240", "plugins/dependencies/lib/dependencies.rb:111",
     "lib/ceedling/config/configurator_builder.rb:139-148", G + "release/results.txt"])

add("Dependency fetch runs in the fetch path and build steps run in the source path",
    "Verdict: kept. Fetch steps run inside `spec.fetch_path` after it is created, so a relative archive `:source` is "
    "relative to the fetch path. Each build step runs in `spec.source_path`, and the source, build and artifact paths are "
    "created first. Both use `WorkingDir.chdir`.",
    [D + "plugins/dependencies.md:114-115", D + "plugins/dependencies.md:164-166",
     "plugins/dependencies/lib/dependencies.rb:194-204", "plugins/dependencies/lib/dependencies.rb:214-220"])

add("Dependency :source artifacts join the include and source collections, not :paths :source",
    "Verdict: kept. `add_source_path` appends each `:source` directory to four include-style collections and its C files "
    "to `collection_all_source`. It does not touch `collection_paths_source`. The doc promises search paths and release "
    "sources only.",
    [D + "plugins/dependencies.md:208-209", "plugins/dependencies/lib/dependencies.rb:324-338"])

add("A :build_lib static library is built in :build and copied to :artifact when they differ",
    "Verdict: kept. The first `:static_libraries` entry is built at `<build path>/<entry>` and copied to "
    "`<artifact path>/<entry>` unless the two paths are equal. Object placement is GAP-04's.",
    [D + "plugins/dependencies.md:273-277", "plugins/dependencies/lib/dependencies.rb:233-250"])

add("files:dependencies lists every library and executable path, built or not",
    "Verdict: kept. The task prints the static libraries, dynamic libraries and executables of every spec. In the "
    "experiment it listed `dependencies/Vend/libvend.a` although nothing built it.",
    [D + "plugins/dependencies.md:241-243", "plugins/dependencies/dependencies.rake:122-130", G + "deps/results.txt"])

# ---------------------------------------------------------------- mixins, project file, which ceedling
add("Mixin names resolve through user load paths, the project file's directory, then Unity's targets",
    "Verdict: kept. `Composinator#loadinate` appends `File.dirname(project_filepath)` and the built-in Unity targets "
    "directory to the user load paths and deduplicates by expanded path. `BUILTIN_MIXIN_LOAD_PATHS` holds the Unity "
    "`test/targets` directory.",
    [D + "configuration/mixins.md:402-405", D + "configuration/mixins.md:488-498",
     "bin/composinator.rb:30-34", "bin/mixins.rb:9"])

add("Mixin and mixin-variable file paths are relative to the working directory",
    "Verdict: kept. Filepaths go to `File.exist?` as written, so they resolve against the working directory. The mixin "
    "directory fallback uses the project file's own directory.",
    [D + "configuration/mixins.md:414", D + "configuration/mixins.md:439-440", "bin/mixin_resolvinator.rb:62-70", "bin/mixin_resolvinator.rb:93-96",
     "bin/composinator.rb:32"])

add("A mixin simple name is told from a filepath by extension or the forward slash only",
    "Verdict: untestable here (Windows). `PathValidator#filepath?` returns true for a value with an extension or one "
    "containing `File::SEPARATOR`, which is `/` on every platform. The docs say \"no path separator\" and the project "
    "docs accept `\\`. Whether a Windows `--mixin bar\\base` (no extension) reaches this test unstandardized was not traced.",
    [D + "configuration/mixins.md:348-350", "bin/path_validator.rb:33-36"],
    severity="low")

add("A mixin's list entries land before the base list, except tool arguments",
    "Verdict: kept. `RecursiveMerger` builds `mixin_val + config_val` for lists and `config_val + mixin_val` for "
    "`:tools` ↳ `<tool>` ↳ `:arguments`. A higher-priority mixin's `:paths` entries therefore come first. Search order "
    "inside the merged list is not changed afterwards.",
    [D + "configuration/mixins.md:96-120", D + "configuration/mixins.md:296-305", "bin/recursive_merger.rb:81-92",
     "bin/recursive_merger.rb:126-128"])

add("Mixin load paths are searched top-down and each path tries every YAML extension",
    "Verdict: kept. `load_paths.product(yaml_extensions)` yields every extension of the first path before the next path.",
    [D + "configuration/mixins.md:478-484", "bin/mixin_resolvinator.rb:108-112"])

add("A test suite needs :paths :include and/or TEST_INCLUDE_PATH, and no :include entry is required",
    "Verdict: kept. A project with no `:paths` ↳ `:include` passes validation. A test using `TEST_INCLUDE_PATH(include)` "
    "built and passed. The same project without the macro stopped with `Found no file `foo.h` in search paths`.",
    [D + "configuration/project-file.md:75-80", G + "cli/results_extra.txt", G + "cli/run_extra.sh",
     "lib/ceedling/config/configurator_setup.rb:117-119"],
    kind="test")

add("A release build needs :paths :test although the project file docs list only :build_root and :paths :source",
    "Verdict: broken. A project with `:release_build: TRUE`, `:project` ↳ `:build_root` and `:paths` ↳ `:source`, and no "
    "`:paths` ↳ `:test`, stops with `Required config file entry :paths ↳ :test does not exist.` The check lists "
    "`:paths` ↳ `:test` for every build.",
    [D + "configuration/project-file.md:82-85", "lib/ceedling/config/configurator_setup.rb:117-119",
     G + "release/results_min_release.txt"],
    kind="test", severity="low")

add("Second-tier keys ending in _path or _paths get Ruby expansion and standard separators",
    "Verdict: kept. `eval_paths` expands every second-tier key that matches `/_path(s)?$/` under each top-level "
    "section, and `standardize_convention_paths` standardizes the same set. `:project` ↳ `:build_root`, "
    ":release_build ↳ :artifacts` and `:paths`/`:files` are handled by their own lines.",
    [D + "configuration/project-file.md:200-205", "lib/ceedling/config/configurator.rb:368-376",
     "lib/ceedling/config/configurator.rb:689-691", "lib/ceedling/config/configurator.rb:702-706"])

add("Which Ceedling picks WHICH_CEEDLING, then :which_ceedling, then vendor/ceedling, then the gem, with ~ expanded",
    "Verdict: kept. `InstallationSelector#select` takes the first of the environment variable, the config value and "
    "`vendor/ceedling` and falls back to the launcher's own root. `validate` standardizes the value, which expands `~`. "
    "Every experiment log here shows `Launching Ceedling from /home/user/Ceedling/` from `:which_ceedling`.",
    [D + "configuration/which-ceedling.md:40-56", "bin/installation_selector.rb:21-30", "bin/installation_selector.rb:61-72",
     C + "logs/v1_public_same_static.excerpt.txt (first line)"])

add("A relative which-ceedling path and vendor/ceedling are resolved from the working directory",
    "Verdict: kept. The selector checks `vendor/ceedling` and the configured path with `directory?`, which reads relative "
    "to the working directory. It never uses the project file's directory.",
    [D + "configuration/which-ceedling.md:60", D + "configuration/which-ceedling.md:78-81",
     "bin/installation_selector.rb:14", "bin/installation_selector.rb:38-45", "bin/installation_selector.rb:61-66"])

add("A symlink to the running installation is the same installation",
    "Verdict: kept. `Installation#identity` returns `File.realpath(@root)`, so two spellings of one directory compare equal.",
    [D + "configuration/which-ceedling.md:124", "lib/ceedling/installation.rb:73-77"])

# ---------------------------------------------------------------- configuration reference
add("A relative release :output is linked below build/release and copied flat into artifacts/release",
    "Verdict: partly kept. The docs say the artifact \"is to be found in <build path>/artifacts/release/\". With "
    "`:output: sub/app.out` the linker output is `build/release/sub/app.out`, and `artifactinate` copies it to "
    "`build/artifacts/release/app.out` without the `sub/`. The default name `project.out` is also copied there. "
    "`:artifacts` entries are copied to the same directory.",
    [D + "configuration/reference/release-build.md:28-32", D + "configuration/reference/release-build.md:53-58",
     "lib/ceedling/config/configurator_builder.rb:139-148", "lib/ceedling/release_invoker/release_build_executor.rb:91-107",
     G + "release/results.txt"],
    kind="test")

add("An absolute or ~ release :output names the release itself",
    "Verdict: kept. `release_place` keeps an absolute name as written and joins any other below the release root. `~` is "
    "expanded by `ProjectPaths.standardize`. Builds with an absolute `:output` and a `~/...` `:output` linked to those paths "
    "and still copied to `build/artifacts/release/app.out`.",
    [D + "configuration/reference/release-build.md:34-35", "lib/ceedling/config/configurator_builder.rb:359-362",
     "lib/ceedling/filesystem/project_paths.rb:44-50", G + "release/results.txt"],
    kind="test")

add("The release-build doc example names build/release/out/c/, which the layout does not use",
    "Verdict: broken (illustrative). The `:artifacts` example is `build/release/out/c/top_secret.s19`. Release objects sit "
    "at `build/release/out/<source directory>/<name>.o` (`build/release/out/src/main.o`, `.../src/drv/led.o`). No `c/` "
    "directory exists.",
    [D + "configuration/reference/release-build.md:22-25", "lib/ceedling/filesystem/file_path_utils.rb:193-196",
     "lib/ceedling/config/configurator_builder.rb:432", G + "release/results.txt"],
    kind="test", severity="none")

add("The :extension lists name output files by their first entry",
    "Verdict: partly kept. Each type accepts a list and Ceedling collects files under any of them. Derived output names "
    "(objects, dependency files, maps) use `.primary`, the first entry, so a second entry never names an output.",
    [D + "configuration/reference/extension.md:5-11", D + "configuration/reference/extension.md:80-87",
     "lib/ceedling/filesystem/file_path_utils.rb:181-196", "lib/ceedling/filesystem/file_path_utils.rb:381-383"])

add("Unity runner :includes entries are written to the runner as typed",
    "Verdict: kept. With `:test_runner` ↳ `:includes: [foo.h, sub/missing.h]` the runner holds `#include \"foo.h\"` and "
    "`#include \"sub/missing.h\"`, and the compiler finds both through the `:include` path.",
    [D + "configuration/reference/test-runner.md:68-75", G + "cli/results_extra.txt (runner head and run)", G + "cli/run_extra.sh"],
    kind="test")

add("The ${5} search path list holds more than the :paths and path-macro entries the tools doc names",
    "Verdict: partly kept. The doc says `-I\"${5}\"` expands to the search paths of `:paths` plus build directive path "
    "macros. The real test compile line puts the test's mocks root, Partials roots and each Partial subdirectory first, "
    "then `:include` entries, then the vendor roots. `:paths` ↳ `:test` and ↳ `:source` directories are not on it.",
    [D + "configuration/reference/tools.md:121", D + "configuration/reference/tools.md:320",
     C + "excerpts/v4_compile_command.txt", G + "cli/results.txt (compile commands: -I\"include\" -I\"build/vendor/unity/src\")"],
    kind="test", severity="low")

add("The tools doc's compile and link examples show a layout Ceedling does not build",
    "Verdict: broken (illustrative). The example compile line has `-I\"project/tests\" -I\"project/source\"` and outputs "
    "`build/tests/out/source.o`. The linker example writes `build\\tests\\out\\test_thing.exe`. Ceedling builds objects "
    "at `build/test/out/<test path>/_t_/<mirrored source path>.o`. Source and test directories are not `-I` entries.",
    [D + "configuration/reference/tools.md:378-383", D + "configuration/reference/tools.md:398-401",
     C + "excerpts/v4_compile_command.txt", C + "logs/v1b_public_calls_static.excerpt.txt"],
    kind="test")

add("A tool executable written as a path is checked on disk and a bare name in the system search path",
    "Verdict: kept. `explicit_path?` is true when the executable holds `/` or `\\`. Such a name is checked as a file "
    "relative to the working directory. A bare name is looked for in the system search paths.",
    [D + "configuration/reference/tools.md:317", D + "configuration/reference/tools.md:339",
     "lib/ceedling/tools/tool_validator.rb:41-52", "lib/ceedling/tools/tool_validator.rb:87-100",
     "lib/ceedling/tools/tool_validator.rb:122-126"])

# ---------------------------------------------------------------- plugins
add("compile_commands.json is keyed by the compiled source path and rewrites a temporary copy to its original",
    "Verdict: kept. The plugin writes `<build root>/artifacts/compile_commands.json`. Its in-memory database is keyed "
    "by `entry['file']`, the compiled source path, so a later compile replaces an earlier one. A same-named pair of "
    "generated Partials gets two entries (`.../_t_/a/ceedling_partial_util_impl.c`, `.../_t_/b/...`). A compile of a "
    "temporary copy has the copy's path replaced by the original in the command line.",
    [D + "plugins/compile-commands-json-db.md:21-27", "plugins/compile_commands_json_db/lib/compile_commands_json_db.rb:19",
     "plugins/compile_commands_json_db/lib/compile_commands_json_db.rb:36", "plugins/compile_commands_json_db/lib/compile_commands_json_db.rb:55-61",
     C + "excerpts/v1cc_compile_commands_keys.txt"],
    kind="test")

add("cppcheck:<filename> takes a trailing path and chooses silently among same-named sources",
    "Verdict: partly kept. The docs say \"by filename with no path\". The rule calls `find_source_file`, which uses the "
    "non-strict lookup: a trailing path narrows the match, and an ambiguous name resolves to the first source in "
    "collection order with a one-time NOTICE and no error. The `test:` tasks raise on the same ambiguity.",
    [D + "plugins/cppcheck.md:513-515", "plugins/cppcheck/cppcheck.rake:40-48", "lib/ceedling/filesystem/file_finder.rb:237-239",
     "lib/ceedling/filesystem/file_finder.rb:468-481", "lib/ceedling/filesystem/file_finder_helper.rb:33-47"],
    severity="low")

add("Plugin docs spell the default build root where the plugin follows :build_root",
    "Verdict: partly kept. The Cppcheck, Bullseye and Gcov docs print `build/artifacts/...` and `build/gcov/out/`. The "
    "plugins build those paths from `PROJECT_BUILD_ARTIFACTS_ROOT` and `PROJECT_BUILD_ROOT`, so the doc paths hold only for "
    "`:build_root: build`. Other docs of the same plugins write `<build root>`.",
    [D + "plugins/cppcheck.md:535-542", D + "plugins/bullseye/index.md:206", D + "plugins/bullseye/index.md:351-356",
     D + "plugins/gcov/setup.md:122-123", D + "plugins/gcov/gcovr.md:4",
     "plugins/cppcheck/lib/cppcheck_constants.rb:13-15", "plugins/bullseye/lib/bullseye_constants.rb:13-22"],
    severity="none")

add("Cppcheck report filenames lose any directory and take the plugin's extension",
    "Verdict: partly kept. `form_artifact_filepath` is `File.join(CPPCHECK_ARTIFACTS_PATH, File.basename(filename).ext(extension))`. "
    "A configured name with a directory keeps only its basename. `ext` replaces the configured name's extension with "
    "the plugin's own (`.sarif`, `.txt`, `.xml`). The docs call each setting a filename and show names with the right extension.",
    [D + "plugins/cppcheck.md:174-215", D + "plugins/cppcheck.md:544-545", "plugins/cppcheck/lib/cppcheck_reports.rb:41-46"],
    severity="none")

add("Whole-project Cppcheck passes the :paths include and source lists, or none with a project file",
    "Verdict: kept. `generate_reports` passes `COLLECTION_PATHS_INCLUDE` and `COLLECTION_PATHS_SOURCE`, or empty lists when "
    "`:cppcheck` ↳ `:project` is set. `:includes` and `:excludes` entries become `--include=` and `-i` options as written. "
    "Test-only search paths, generated roots and `TEST_INCLUDE_PATH` entries are not passed.",
    [D + "plugins/cppcheck.md:237-251", D + "plugins/cppcheck.md:28", "plugins/cppcheck/lib/cppcheck.rb:59-66",
     "plugins/cppcheck/lib/cppcheck.rb:321-327"])

add("Cppcheck suppression files come from :paths :cppcheck and :files :cppcheck",
    "Verdict: kept. Each `:paths` ↳ `:cppcheck` entry contributes its `*.xml` and `*<extension>` files, a path that "
    "does not exist logs a warning, and `:files` ↳ `:cppcheck` revises the list. `files:cppcheck` lists the result.",
    [D + "plugins/cppcheck.md:433-445", D + "plugins/cppcheck.md:521-531", "plugins/cppcheck/lib/cppcheck.rb:250-275",
     "plugins/cppcheck/cppcheck.rake:49-62"])

add("The Bullseye coverage file is test.cov in the working directory",
    "Verdict: kept (the Bullseye behavior itself is untestable here). `BULLSEYE_COVFILE_PATH` is the literal `test.cov`, "
    "a path relative to the working directory, which is the project root whenever the project file is loaded from it. "
    "The Bullseye claim that sources are stored relative to the file and that this root is the common ancestor was not run.",
    [D + "plugins/bullseye/index.md:55-62", "plugins/bullseye/lib/bullseye_constants.rb:35",
     "plugins/bullseye/lib/bullseye.rb:453-475"])

add("Untested sources compile with the :include collection, matchers keyed by the source's own path",
    "Verdict: kept. Both plugins compile an untested source with `form_test_object_filepath(filepath, context:)`, "
    "resolve flags and defines against that source's filepath, and Bullseye passes `collection_paths_include` as its "
    "search paths. An object sits below `<build root>/<plugin>/out/` at the source's own directory, so same-named "
    "sources in different directories do not share an object. Not run.",
    [D + "plugins/bullseye/index.md:149-155", D + "plugins/gcov/setup.md:119-123", D + "plugins/gcov/setup.md:146-150",
     "plugins/bullseye/lib/bullseye.rb:236-246", "plugins/gcov/lib/gcov.rb:167", "lib/ceedling/filesystem/file_path_utils.rb:633-639"],
    kind="promise")

add("Gcovr's default exclusions are path-segment patterns built from :paths, :test_file_prefix and :build_root",
    "Verdict: kept. `build_report_exclusions` builds `.*(?:^|/)<test path>/(?:.*/)?<prefix>[^/]+<ext>$` for each "
    "`:paths` ↳ `:test` entry, `.*(?:^|/)<support path>/.+<ext>$` for each support entry, and "
    "`.*(?:^|/)<build root>/.+\\.c$`. The patterns do not start at the project root. A test path `test` also matches "
    "`drivers/legacy/test/test_wire.c` and does not match `latest/test_x.c` (a check of the pattern in Ruby; gcovr "
    "uses Python's `re`, same for this pattern).",
    [D + "plugins/gcov/gcovr.md:54-121", "plugins/gcov/lib/gcovr_reportinator.rb:508-541", "plugins/gcov/lib/gcov_reportinator.rb:62-71",
     G + "gcov_pattern_check.txt"],
    kind="promise", severity="low")

add("ReportGenerator filters are relative ./ globs for test paths and the build root, plus ceedling_partial_*",
    "Verdict: kept. `build_filefilter_exclusions` writes `-./<test path>/**/*` for each test path and "
    "`-./<build root>/**/*`. With Partials on, `-ceedling_partial_*` is added. The patterns assume project-relative "
    "paths spelled with a leading `./`. The `.gcno` scan skips test-prefixed files anywhere and mocks, runners, "
    "`unity` and `cmock` only below the build root.",
    [D + "plugins/gcov/reportgenerator.md:28-96", "plugins/gcov/lib/reportgenerator_reportinator.rb:177-187",
     "plugins/gcov/lib/reportgenerator_reportinator.rb:329-336", "plugins/gcov/lib/reportgenerator_reportinator.rb:357-372"],
    kind="promise")

add("A Partial's #line directives name the module's project-relative source file",
    "Verdict: kept. The generated `a/ceedling_partial_util_impl.c` holds `#line 4 \"src/a/util.c\"` ahead of the function, "
    "the path as the project spells it. The coverage plugins' retargeting of Partial coverage onto the original relies "
    "on that path. Not run with a coverage tool.",
    [D + "plugins/bullseye/index.md:428-439", D + "plugins/gcov/troubleshooting.md:8-21", C + "excerpts/v1_a_impl.c:4"],
    kind="promise")

json.dump(F, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings_src.json"), "w"), indent=1, ensure_ascii=False)
print(len(F), "findings")
