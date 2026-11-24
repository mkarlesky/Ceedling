# Phase 3a report: the contract harness skeleton and GCC oracle

The contract tier is built, its 16 seed rows are written, and their Linux sections and compiler column are recorded on native GCC 13.3. `bundle exec rspec spec/contract` runs 151 examples with 0 failures and 11 pending here: 3 for COV-001's Bullseye leg and the row's stale-declaration check, which need Bullseye, and 8 for ORC-002, which runs on Windows only. Every divergence a run shows is one the seed's catalog entry explains, so none is left undeclared. The only `lib/` change is `attr_reader :state` on `TestInvoker`. The RuboCop compare shows 0 grown.

macOS and Windows are not recorded yet. Until the maintainer records them, the `Contract rows` CI step fails on both, as the plan intends.

## Branch and commits

Branch `phase3a/contract-harness`, from `master` 402e4912.

| # | Commit | Holds |
|---|---|---|
| 1 | Add specs for the contract harness and the pipeline state reader | Red: `spec/contract/harness/*_spec.rb`, `spec/contract/contract_rows_spec.rb`, the `#state` examples in `spec/units/test_invoker_spec.rb` |
| 2 | Expose TestInvoker's pipeline state to read-only observers | The accessor |
| 3 | Add the contract row loader and tree writer | `loader.rb`, `tree_writer.rb`, `contract.rb`, `directives.rb` |
| 4 | Add the contract probe plugin that observes a build | `probe/contract_probe.rb` |
| 5 | Add the contract runner and its report | `runner.rb`, `report.rb` |
| 6 | Add the GCC oracle and the path normalizer | `oracle.rb`, `normalizer.rb` |
| 7 | Add the contract recorder and column checks | `recorder.rb` |
| 8 | Add the seed contract rows with their Linux recordings | `spec/contract/rows/*.yml`, `spec/contract/recorded/*.yml` |
| 9 | Run the contract rows in CI on Linux, macOS and Windows | `.github/workflows/ci.yml` |
| 10 | Document the contract tier's row format, columns and recording | `spec/contract/README.md` |
| 11 | Report for Phase 3a | This file and `row-map.json` |

Every commit message ends with the `Co-Authored-By` line. A `Claude-Session` line sits just above it.

### The red commit

Each spec in the red commit failed for the reason its message gives, run at that commit:

| Spec | Failure |
|---|---|
| `harness/loader_spec.rb` | `LoadError: cannot load such file -- contract/loader` |
| `harness/normalizer_spec.rb` | `LoadError: cannot load such file -- contract/normalizer` |
| `harness/oracle_spec.rb` | `LoadError: cannot load such file -- contract/oracle` |
| `harness/runner_spec.rb` | `LoadError: cannot load such file -- contract/runner` |
| `harness/recorder_spec.rb` | `LoadError: cannot load such file -- contract/runner` |
| `contract_rows_spec.rb` | `LoadError: cannot load such file -- contract/runner` |
| `units/test_invoker_spec.rb` | 14 examples, 2 failures, both `NoMethodError: undefined method 'state' for an instance of TestInvoker` |

The must-fail self-tests are in the red commit. `recorder_spec.rb` fails a recorded column with one wrong path, and names where. `oracle_spec.rb` fails an oracle answer for an angle include that lands in its includer's directory, through a stubbed compiler. Further must-fail inputs cover an undeclared divergence, a section recorded but no longer observed, and a probe with neither an `-H` entry nor a missing-file error.

### The commits between

Each fix commit turned its own specs green, with two that wait on a later commit, both from the order the plan sets.
- The runner reports through the normalizer and asks the oracle, so `runner_spec.rb` loads only from commit 6, where it passes 11 of 11.
- `loader_spec.rb`'s "loads every row file in the tier" expects at least one row, so it fails until commit 8. Its 13 other examples pass from commit 3.

The probe has no spec of its own. `runner_spec.rb` exercises it through real builds.

## Row outcomes

Current column on Linux, GCC 13.3.0, Ruby 3.3. A failure is the recorded observation, not a spec failure. Every row's current, compiler and divergence checks pass.

| Row | Variant | Build | Outcome | Stage | First error line |
|---|---|---|---|---|---|
| COV-001 | none/gcov | 1 `gcov:all` | pass | | |
| COV-001 | none/bullseye | | skipped: no `covc` here | | |
| DELTA-001 | all | 1 | pass | | |
| DELTA-001 | all | 2 | pass | | |
| DELTA-002 | none/updated, all/updated | 1 | pass | | |
| DELTA-002 | none/updated, all/updated | 2 | fail | Building Test Executables | ``test/test_foo.c:5:(.text+<offset>): undefined reference to `foo_b_ExpectAndReturn'`` |
| DELTA-002 | none/unchanged, all/unchanged | 1 | pass | | |
| DELTA-002 | none/unchanged, all/unchanged | 2 | fail | Building Test Executables | ``test/test_foo.c:5:(.text+<offset>): undefined reference to `foo_a_CMockExpectAndReturn'`` |
| DELTA-003 | mocks | 1 | pass | | |
| DELTA-003 | mocks | 2 | pass, every stage skipped | | |
| GEN-001 | none | 1 | fail | Building Objects | ``EXCEPTION: Found no file `test_x_runner.c` in search paths.`` |
| ISO-001 | tests | 1 | fail | Executing | `test_helper.c:6:test_twice:FAIL: Expected 7 Was 2` |
| LINK-001 | none, tests, all | 1 | fail | Building Test Executables | ``…/mock_foox.c:52: multiple definition of `foox_read'; …foox.o:src/drivers/foox.c:2: first defined here`` |
| MOCK-001 | none/cmock, none/fff | 1 | fail | Collecting Essential Test Context | ``EXCEPTION: Found no file `drivers/foox_sfx.h` in search paths.`` |
| MOCK-001 | tests/cmock, tests/fff | 1 | fail | Collecting More Test Context | the same |
| ORC-001 | tests | 1 | pass | | |
| ORC-002 | none/gcc, none/clang | | skipped: Windows only | | |
| PART-001 | all | 1 | fail | Building Objects | `…/ceedling_partial_sensor_impl.h:4:1: error: unknown type name 'sensor_val_t'` |
| PART-002 | all | 1 | fail | Building Test Executables | ``test/test_unix.c:6:(.text+<offset>): undefined reference to `unix_pub'`` |
| PART-003 | all | 1 | fail | Building Objects | `…/ceedling_partial_b_types.h:6:16: error: redeclaration of enumerator 'B_OK'` |
| PART-004 | all/test_first | 1 | fail | Building Objects | `…/ceedling_partial_lock_interface.h:6:15: error: unknown type name 'log_op_t'`, compiling the lock mock source |
| PART-004 | all/mock_first | 1 | fail | Building Objects | the same line, compiling the test file |
| PART-005 | all | 1 | fail | Building Objects | `…/ceedling_partial_b_types.h:6:14: error: redeclaration of 'enum b_status'` |
| RES-001 | tests | 1 | fail | Building Test Executables | ``test/test_config.c:6:(.text+<offset>): undefined reference to `config_get'`` |

What each row pins beyond its outcome, from its recording:
- **ISO-001.** The mock's header is held as `./src/drivers/foo.h` (`placements.mock_headers`), while the test's `.d` lists `src/drivers/foo.h` and the markers `./src/drivers/foo.h`. `placements.isolation` is empty and no `Isolated` notice is logged.
- **DELTA-001.** Build 2 reruns stages 6, 7 and 8 for `p`. `entered.mocks_read` shows build 1's pass 2 found a stand-in at `mock_m1.h` and build 2's found build 1's real mock.
- **DELTA-002.** Build 2 leaves the flat `mock_foo.{c,h}` beside the new `drivers/mock_foo.{c,h}`, and the test compiles against the flat one.
- **DELTA-003.** Build 2's compiler column answers `src/a/foo.h` for `src/c/bar.h "foo.h"`, and build 2 skips every stage.
- **RES-001.** Ceedling holds `src/sub/config.h` for `"config.h"` and links `src/sub/config.c`. The compiler answers `src/config.h`.
- **PART-001.** Both Partials directives hold no module header, and no types header is written.
- **COV-001.** Both `util.c` sources compile under `:untested_sources: :compile`, to `build/gcov/out/src/a/util.o` and `build/gcov/out/src/b/util.o`.
- **ORC-001.** The `.d` spells `src/drivers/bar.h` and `src/drivers/foo.h`, the markers `./src/drivers/bar.h` and `./src/drivers/foo.h`, and the normalized paths and the oracle agree.

## Wall time

Per row, all its variants, on this machine:

| Row | Time |
|---|---|
| COV-001 | 0.9 s |
| DELTA-001 | 2.4 s |
| DELTA-002 | 6.5 s |
| DELTA-003 | 1.2 s |
| GEN-001 | 0.4 s |
| ISO-001 | 0.9 s |
| LINK-001 | 2.9 s |
| MOCK-001 | 1.9 s |
| ORC-001 | 1.0 s |
| PART-001 | 0.9 s |
| PART-002 | 1.5 s |
| PART-003 | 1.0 s |
| PART-004 | 2.1 s |
| PART-005 | 1.0 s |
| RES-001 | 0.9 s |
| **Rows total** | **25.4 s** |

`bundle exec rspec spec/contract`, harness specs included, took 30 s. Nothing here measures macOS or Windows. Each CI run writes `timings-<platform>.txt` into its artifact, so their times come from the first CI run. The step runs in every Ruby leg of each job's matrix, 6 on Linux and 5 each on macOS and Windows.

## Divergences

### Declared

Every one is explained by the seed's catalog entry.

| Row | At | Kind | Note, shortened |
|---|---|---|---|
| ISO-001 | `test/test_helper.c "src/drivers/mock_foo.h"` | convention | A mock include names the mocked header, which the compiler never sees |
| LINK-001 | `test/test_foox.c "drivers/mock_foox.hpp"` | convention | The same |
| DELTA-001 | `test/test_p.c "mock_m1.h"`, `test/test_p.c "mock_m2.h"` | convention | The same |
| DELTA-002 | `test/test_foo.c "mock_foo.h"` | convention | The same |
| DELTA-003 | `test/test_bar.c "mock_bar.h"` | convention | The same |
| RES-001 | `test/test_config.c "config.h"` | defect | Reconciliation pairs the pathless include with the first same-named header entered at any depth |
| PART-001 | `test/test_sensor.c TEST_PARTIAL_MODULE_AT(src/drivers, sensor)` | defect | The module header is looked up in a collection that lists `-I .` shallowly |
| PART-001 | `test/test_sensor.c MOCK_PARTIAL_PUBLIC_MODULE_AT(src/drivers, sensor)` | defect | The Mock Partial looks it up the same way |
| PART-002 | `test/test_unix.c TEST_PARTIAL_PUBLIC_MODULE(unix)` | defect | The compiler expands `unix` to 1, Ceedling reads the text |
| PART-002 | `test/test_unix_at.c TEST_PARTIAL_PUBLIC_MODULE_AT(src, unix)` | defect | The directory form's join expands the module too |

MOCK-001 shows no mock divergence, since its build stops before stage 5 records any mock.

### Undeclared

None. No row showed a current-versus-compiler difference its catalog entry does not explain.

### Observations for a ruling

These are not divergences, but each differs in detail from its catalog entry or settles something the entry left open.
1. **PART-002's directory form expands its module argument.** The catalog infers this and says it was not built. GCC 13 expands `TEST_PARTIAL_PUBLIC_MODULE_AT(src, unix)` to `"src/ceedling_partial_1_impl.h"`, so the oracle answers `missing` for `src/1.h`. I declared it a `defect` under the same mechanism. Rule on whether it belongs to DC-011 or needs its own entry.
2. **DC-054 holds only when the new mock adds a mock search path.** With the second mock's header in the first mock's directory, stages 6 to 8 did not rerun in build 2, since the composed search paths did not change. DELTA-001 puts `m2.h` in `src/n/` so they do.
3. **DELTA-002 fails at the link on GCC 13.** An implicit declaration is only a warning on GCC 13, so build 2 fails linking, as the catalog predicts for an older compiler.
4. **PART-001's first error is in the implementation header.** The catalog quotes the interface header. Here `ceedling_partial_sensor_impl.h:4:1` comes first.

## Probe reach

The probe uses only plugin hooks and `TestInvoker#state`. Three values were beyond that reach, so I stopped those parts of their sections and widened nothing.
- **Stage 3's search paths before stage 4 narrows them.** No hook fires between stages 3 and 4. `search_paths.tests.<test>.test` and `.mocks` are therefore the stage 5 snapshot, taken in `pre_test`. Without test preprocessing stage 4 does not run, so the snapshot is stage 3's list.
- **The header a plain `#include` reaches without test preprocessing.** The Testable keeps the include's text, not the header stage 13's search found. Under `:none` and `:mocks`, `resolved` gives only the sources paired with a plain include.
- **Which compiler a compile ran.** Not recorded. ORC-002's clang leg sets the tools through the row's project, and I checked on Linux that it builds with clang.

What stage 4's second pass read at a mock's path needed no hook. Its own directives-only output keeps every `#define`, so `entered.mocks_read` reads a generated mock's include guard from it.

## RuboCop

`CEEDLING_LINT=true ruby /tmp/lint_compare.rb /tmp/base "$PWD"` over all 18 changed `.rb` files prints `0 grown, 0 shrunk`. Two offenses an earlier draft had, `Performance/DeletePrefix` and `Performance/DoubleStartEndWith`, were fixed before commit.

## Other suites

- `bundle exec rspec spec/units`: 6885 examples, 0 failures.
- `bundle exec rspec spec/integration`: 885 examples, 0 failures, 15 pending.
- No system spec was run, since no system behavior changed.

## Choices the plan left to me

**Row format.**
1. `platform_note` gives the reason a row narrows `platforms`, and the loader requires it then.
2. `legs` hold separate builds of one row: CMock and FFF in MOCK-001, gcov and Bullseye in COV-001, MinGW GCC and clang in ORC-002, test updated or unchanged in DELTA-002, and the two include orders in PART-004. A leg may add plugins and project configuration, replace the steps, name tools it `requires`, and name a compiler `cc` for the oracle. A leg whose tool or compiler is absent is skipped. That is how COV-001's Bullseye leg skips here.
3. A variant is keyed `mode` for a row without legs and `mode/leg` otherwise.
4. A divergence's `at` is `resolved <includer> <directive>`. A declared divergence no variant shows fails the row too, so declarations stay current.
5. `target` maps a variant key to a list of promised build reports, giving only the sections promised, and is asserted as pending.
6. The loader requires a Partials row to list only `all`.

**Project and build.**
7. The base project sets `:mock_prefix: mock_`, since Ceedling's default prefix is `Mock` and every catalog row spells `mock_`. It also sets `:use_backtrace: :none`, so no row depends on gdb.
8. Ceedling runs with `CEEDLING_DECORATORS=0`, so every platform logs the same text.
9. Ceedling loads a plugin from `<load path>/<name>/lib/<name>.rb`, so the runner copies the probe from its planned path into a temporary plugin directory for each variant.

**Report.**
10. `outcome.stages` lists each stage heading's progress lines, which is how delta rows show what reran. The first error line prefers a tool's or a test's own error to the exception Ceedling raises around it.
11. `resolved` adds ` source` keys for a Partial's source and for a plain include's paired sources. The paired sources are the test's sources sharing the header's stem.
12. `placements` lists the generated files on disk below each test's generated roots after the build, sorting mocks, stand-ins and header copies apart. It adds each compiled object, each mock's header as Ceedling holds it, and what the build itself generated.
13. `entered` splits into `dependencies`, from the `.d` files, `markers`, from stage 4's directives-only output, and `mocks_read`.
14. Normalized paths write `%{ceedling}/` for this checkout, `<system>` for other files outside the workspace, and `<tmp>` for a build's temporary directory names. Log text masks times and linker section offsets. A `..` segment is kept.

**Oracle.**
15. `-I` comes from `:test`, `:support`, `:include` and `:libraries`, in the order `TestSearchPaths` lists them. I checked that its glob order matches Ceedling's on PART-004's tree. `:files` entries name headers, not directories, so they add none.
16. Unity, CMock, CException and `ceedling.h` includes are left out of both columns.
17. A Partials directive is answered by expanding its macro with the checkout's own `ceedling.h` and the row's test defines, then resolving `<dir>/<module>.h` from the includer's directory.
18. The compiler column is a list with one answer map per build step, since a delta row's tree changes between builds.

**Recording and CI.**
19. With recording on, or on a mismatch, a row writes its whole recorded file with this platform merged in to `$CONTRACT_OUT/<ID>.yml`, so a CI artifact file can be copied into `recorded/` as it is. `CONTRACT_OUT` defaults to `ceedling-contract` in the system temp directory.
20. The CI step runs in every Ruby leg, with `CONTRACT_OUT=tmp/contract` and a 15-minute timeout. It uploads an artifact named `contract-<os>-ruby-<version>` on every run.

**Seed rows.** Where the catalog gave only file names, I wrote the contents.
21. DELTA-003 holds `src/a/.keep`, since Ceedling refuses a `:paths` entry that does not exist in build 1.
22. PART-002 holds both of DC-011 row 2's cases in one project, as two test files, and runs on Linux only. MinGW does not predefine `unix`, and as far as I know Apple Clang does not either, so other platforms would not test the expansion and their compiler answers would disagree with the one stored column.
23. MOCK-001 and LINK-001 cover only row 1 of their entries, the `.h` mock and the `.hpp` mock.
24. RES-001 adds `src/config.c` and `src/sub/config.c` with different functions, so the wrong pairing shows in the link.
25. COV-001 sets `:untested_sources: :compile` and turns gcov summaries off, so both sources reach compilation and no row needs gcovr.

**Commits.**
26. The directive scanner went in with the loader, the report with the runner, and the row driver with the red commit.
27. Before any push I rewrote the local red commit to drop a catalog-style ID it used as a rejected-ID example. It now uses `AB-032`.

## Left for the maintainer

- Record `macos` locally with `CONTRACT_RECORD=1 bundle exec rspec spec/contract`, and run COV-001's Bullseye leg where `covc` is installed.
- Record `windows` from the CI artifact by copying its `<ID>.yml` files into `spec/contract/recorded/`. ORC-002's clang leg runs only if `clang` is on the runner's PATH. Its link needs the MSVC toolchain clang targets there, and if that fails the failure is recorded as current.
- Rule on the four observations above.
- No public docs change. The harness changes no user-visible behavior, so there is no Changelog text to draft.
