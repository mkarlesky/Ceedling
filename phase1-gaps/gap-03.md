# GAP-03, the remainder: GCC 15 and an end-to-end DC-032 build

## Summary

GCC 15 hides #1463 when the module's types are tagged, and only then. The official `gcc:15` image gives GCC 15.3.0, which defaults to C23. Experiment e2 behaves on GCC 15 exactly as on clang 15 and GCC 13. The untagged redefinition fails under C17 and C23, and the flagged header compiles. A tagged enum or struct defined identically twice compiles under GCC 15's C23 and fails under C17 and on GCC 13. A real Ceedling build of #1463's shape repeats this. With an untagged type it fails on GCC 15 and GCC 13 with #1463's error. With a tagged type it passes on GCC 15 and fails on GCC 13 and on GCC 15 with `-std=c17`. A #1463 contract row must therefore use an untagged type, or pin `-std=c17`, to fail on every compiler tried. DC-032 is now observed end to end on GCC 13.3.0 and GCC 15.3.0. Through `:paths: :include: [.]` the mock's source is `./src/drivers/foo.h`, the `.d` says `src/drivers/foo.h`, and the sibling `helper.h` is never isolated. When the test includes `helper.h` first, the test then runs the real inline body in place of the mock and fails with `Expected 100 Was 6`. MinGW was out of reach and was not approximated.

Finding IDs restart at GAP3-01, as the brief asks. The earlier GAP-03 investigator used GAP3-01 to GAP3-12 too, so a merged ledger needs this stream's IDs renamed or qualified. This report cites the earlier GAP3-12 as "the earlier GAP3-12".

## What I ran

All work is under `phase1-gaps/gap-03/`. The checkout is master `402e4912cf160f43938a4557554a2bba6cd52f13`. Every Ceedling log shows `Launching Ceedling from /home/user/Ceedling/`, set through `:project: :which_ceedling:`, and every build ran with `--verbosity=obnoxious`.

- **Compilers.** GCC 15.3.0 came from `docker pull gcc:15`, digest `sha256:60a0af4b79226d7cb062cc18dcb56f91b4385aace8f6d514f114c3f1af363ef1`, Debian 13, as `gcc15-image.txt` records. Its `__STDC_VERSION__` is `202311L` by default. GCC 13.3.0 is the container's own `gcc`, default `201710L`. The PPA was not needed.
- **e2.** `e2/` holds stream 4's files exactly as the brief gives them, with `results.txt` as stream 4 recorded it on clang 15. `e2/run-gcc.sh` is `run.sh` with `gcc` in place of `clang`. `run-e2-all.sh` runs it on GCC 15 by default, with `-std=c17` and with `-std=c23`, and on GCC 13 by default and with `-std=c2x`. Output is `e2/results-gcc15.txt`.
- **Tagged variant.** `e2_tagged/` keeps e2's include chain. `src/b/b.h` defines a tagged enum and a tagged struct, and `gen/types_enum.h` and `gen/types_struct.h` each define one again, identically. Two controls are added. `gen/types_enum_differs.h` adds an enumerator, and `src/u/u.h` with `gen/types_ustruct.h` define an untagged struct twice. Output is `e2_tagged/results.txt`.
- **Ceedling with GCC 15.** `bin-gcc15/gcc` is a wrapper that runs `gcc` from the `gcc:15` image with the checkout mounted at its own path. `run-ceedling.sh` puts it first on `PATH`, so Ceedling's default tools run GCC 15. The same script without the wrapper runs GCC 13. Each run copies the project to `work/`, which git ignores, and builds from clean. The test executables linked by GCC 15 ran on the host.
- **Projects.** `p1463/untagged`, `p1463/tagged` and `p1463/tagged_c17` reproduce #1463. `dc032/` holds five projects for DC-032. `extract.sh` trims each full log to the lines cited here and copies the cited generated files out of `build/` into `results/<project>-<compiler>.txt`. Full logs and `build/` trees are not committed.

## Results

### e2 and its tagged variant

GCC 15 agrees with clang 15 and GCC 13 on e2, and accepts the tagged redefinition only under C23 (GAP3-02, GAP3-03).

| Translation unit | GCC 15 default (C23) | GCC 15 `-std=c23` | GCC 15 `-std=c17` | GCC 13 default (C17) | GCC 13 `-std=c2x` | clang 15 (stream 4) |
|---|---|---|---|---|---|---|
| e2 `t_now.c`, untagged enum twice | rejected | rejected | rejected | rejected | rejected | rejected |
| e2 `t_flagged.c`, flagged types header | compiles | compiles | compiles | compiles | compiles | compiles |
| `t_tag_enum.c`, identical tagged enum | **compiles** | **compiles** | rejected | rejected | rejected | not run |
| `t_tag_struct.c`, identical tagged struct | **compiles** | **compiles** | rejected | rejected | rejected | not run |
| `t_tag_enum_differs.c`, tagged enum with an extra enumerator | rejected | rejected | rejected | rejected | rejected | not run |
| `t_untag_struct.c`, identical untagged struct | rejected | rejected | rejected | rejected | rejected | not run |

GCC 15 rejects `t_now.c` with `redeclaration of enumerator 'B_OK'`, the same for `B_FAIL`, and `conflicting types for 'b_status_E'`. This observes the untagged half of the earlier GAP3-12. GCC 13's `-std=c2x` does not accept the tagged redefinition, so the change comes with GCC 15, not with the `-std` value alone.

### #1463 in a real Ceedling build

The project follows #1463's report and DC-012's contract tree. `src/a/a.c` includes `src/a/a.h`, `src/a/helper.h` and `src/b/b.h`. `src/a/helper.h` includes `src/b/b.h` at line 3. The configuration is #1463's, with `:include: [., src/**]`. The test uses `TEST_PARTIAL_MODULE(a)`, `TEST_PARTIAL_CONFIG(a, a_run, )` and `MOCK_PARTIAL_PUBLIC_MODULE(b)`. Partials force preprocessing, and each log shows `Enabled preprocessing.` The tagged `b.h` defines `typedef enum b_status_e { B_OK, B_FAIL } b_status_E;` and `typedef struct b_cfg_s { int gain; } b_cfg_S;`.

| Project | GCC 15.3.0 default (C23) | GCC 13.3.0 default (C17) | GCC 15.3.0 with `-std=c17` |
|---|---|---|---|
| `p1463/untagged` | fails at `test_a.c`, #1463's error | fails at `test_a.c`, #1463's error | not run |
| `p1463/tagged` | **builds, 1 test passed** | fails at `test_a.c` | fails at `test_a.c` (`p1463/tagged_c17`) |

The untagged run on GCC 15 reports `ceedling_partial_b_types.h:6:16: error: redeclaration of enumerator 'B_OK'`. The previous definition is `./src/b/b.h:3:16`, reached `from src/a/helper.h:3, from .../ceedling_partial_a_impl.h:8, from test/test_a.c:4`. That is #1463's trace line for line. Ceedling's collision NOTICE fires before the error.

The tagged run on GCC 15 compiles `test_a.c`, `ceedling_partial_a_impl.c`, `mock_ceedling_partial_b_interface.c` and the runner, links, and passes. The `.d` files of `test_a.c`, `ceedling_partial_a_impl.c` and `test_a_runner.c` each list both `src/b/b.h` and `ceedling_partial_b_types.h`. Each of those translation units holds both definitions, and C23 accepts them. On GCC 13 and on GCC 15 with `-std=c17`, the same project stops at `test_a.c` with `redeclaration of 'enum b_status_e'` and `redefinition of 'struct b_cfg_s'`.

So GCC 15 hides #1463 for tagged types. The generated files are the same on every compiler. The types header writes `#define B_H` and the types with no condition (`lib/ceedling/generators/generator_partials.rb:123-131`, `lib/ceedling/generators/partial_header_writer.rb:41-45`). Only the compiler's tolerance changes.

### DC-032 end to end

Through search path `.`, sibling isolation does nothing, on GCC 13 and GCC 15 alike. Every project has `src/drivers/foo.h` with `static inline int foo_twice(int x)`, and `src/drivers/helper.h` that quote-includes `"foo.h"`. `src/drivers/helper.c` includes `"helper.h"` and `"foo.h"`. The configuration has `:use_test_preprocessor: :tests` and `:cmock: :treat_inlines: :include`, which `isolate_sibling_headers` requires (`lib/ceedling/test_invoker/test_substitutions.rb:30-35`).

| Project | `:include:` | Test includes, in order | Mock source in the NOTICE | `.d` entry | `helper.h` isolated | GCC 13.3.0 | GCC 15.3.0 |
|---|---|---|---|---|---|---|---|
| `dot` | `[.]` | `src/drivers/mock_foo.h`, `src/drivers/helper.h` | `./src/drivers/foo.h` | `src/drivers/foo.h` | no | pass | pass |
| `dot_drivers` | `[., src/drivers]` | `src/drivers/mock_foo.h`, `helper.h` | `./src/drivers/foo.h` | `src/drivers/foo.h` | no | pass | pass |
| `control` | `[src/drivers]` | `mock_foo.h`, `helper.h` | `src/drivers/foo.h` | `src/drivers/foo.h` | **yes** | pass | pass |
| `dot_helperfirst` | `[.]` | `src/drivers/helper.h`, `src/drivers/mock_foo.h` | `./src/drivers/foo.h` | `src/drivers/foo.h` | no | **1 of 2 fail** | **1 of 2 fail** |
| `dot_drivers_helperfirst` | `[., src/drivers]` | `helper.h`, `src/drivers/mock_foo.h` | `./src/drivers/foo.h` | `src/drivers/foo.h` | no | **1 of 2 fail** | **1 of 2 fail** |
| `control_helperfirst` | `[src/drivers]` | `helper.h`, `mock_foo.h` | `src/drivers/foo.h` | `src/drivers/foo.h` | **yes** | pass | pass |

The `./` spelling reaches the mock's `source`. The source-isolation NOTICE prints the matched mock's `source` (`lib/ceedling/test_invoker/test_build_executor.rb:894-899` and `:940-942`), and it reads `mocked header './src/drivers/foo.h'` in every `dot` build. The planner stores what `MockLocator#locate` returns as the mock's `source` (`lib/ceedling/test_invoker/test_build_planner.rb:68`, `:88`).

The compiler drops `./` in the `.d` and keeps it in line markers. Each `test_helper.d` lists `src/drivers/helper.h src/drivers/foo.h`. In `dot`, the preprocessed test file under `build/test/preprocess/files/` has `# 1 "./src/drivers/helper.h"` and `# 1 "./src/drivers/foo.h"`, because the test reaches `helper.h` through `-I .`. In `dot_drivers`, the markers read `src/drivers/...`, because the test includes `"helper.h"`, which is found through `-I src/drivers`. The mock's source is `./src/drivers/foo.h` in both. Ceedling's dependency parser keeps each token as written, apart from unescaping `\ ` and `\#` (`lib/ceedling/dependencies/gcc_dependency_parser.rb:43-63`).

Header isolation then skips the mocked header. `isolate_sibling_headers` takes the mocks' sources as written (`lib/ceedling/test_invoker/test_substitutions.rb:59-62`) and skips each one the `.d` does not list in the same spelling (`lib/ceedling/test_invoker/test_build_executor.rb:1075`). No `Isolated` NOTICE appears in any of the eight `dot` builds. The two `control` projects log `Isolated 'src/drivers/helper.h'` and recompile the test with the isolation directory first, writing `test_helper.d.isolated_retry`.

The miss causes a false test failure. With `helper.h` first, the real `foo.h` arrives first with its inline body. CMock's copy carries the same guard `FOO_H` and adds nothing. `test_foo_twice_is_mocked` calls the real `foo_twice` and fails with `Expected 100 Was 6` in both `helperfirst` projects that use `.`, on both compilers. The control passes both tests. With the mock first, CMock's copy arrives first and the real header adds nothing, so the missed isolation is harmless and the build passes.

Source isolation is unaffected by the spelling. `inline_mocked_sibling_header` compares `File.expand_path` of both directories (`lib/ceedling/test_invoker/test_build_executor.rb:892-896`). Every `dot` build compiles an isolated copy of `helper.c`. Header isolation and source isolation thus compare the same `source` in two different ways.

## Findings

Each finding was checked by an adversarial verifier, and each one not confirmed went to an adjudicator. The ledger `phase1-gaps/gap-03.json` holds the settled text, verdicts and rulings.

- **GAP3-01.** `gcc:15` is GCC 15.3.0 and defaults to C23. GCC 13.3.0 defaults to C17.
- **GAP3-02.** e2 on GCC 15 rejects `t_now.c` under C23 and C17 and compiles `t_flagged.c`, as GCC 13 and clang 15 do.
- **GAP3-03.** GCC 15's C23 accepts an identical tagged enum or struct redefinition. C17 and GCC 13 reject it. Differing content and untagged types are rejected everywhere.
- **GAP3-04, defect, high, #1463.** A real Ceedling build reproduces #1463 with an untagged type on GCC 15 and GCC 13.
- **GAP3-05, defect, high, #1463.** With tagged types the build passes on GCC 15's default and fails on GCC 13 and GCC 15 `-std=c17`. Three translation units hold both definitions.
- **GAP3-06, test, revised.** A #1463 contract row must use an untagged type or pin `-std=c17`. No dialect before C17 was run, and clang was run only on the untagged case. Stream 4's clang run prints no version, and only `e2/run.sh`'s comment names Apple clang 15.
- **GAP3-07, spelling.** Through `.`, the mock's source is `./src/drivers/foo.h`.
- **GAP3-08, spelling, revised.** GCC 13 and 15 write `src/drivers/foo.h` in the `.d`. Line markers keep `./` where the compiler reached the file through `-I .`, as in `dot`, and not in `dot_drivers`, where it went through `-I src/drivers`.
- **GAP3-09, defect, medium.** Sibling isolation never isolates `helper.h` through `.`. It does under `[src/drivers]`.
- **GAP3-10, defect, medium.** The miss runs the real inline body in place of the mock, a false failure.
- **GAP3-11, mechanism.** Source isolation normalizes with `File.expand_path` and works through `.`.
- **GAP3-12, test.** DC-032's second contract row as written passes today. It needs `helper.h` first and a test of the inline function's mock.

## What this changes in the catalog

DC-012's contract row should use an untagged type. Its own text already suggests this, and GAP3-05 confirms the risk it inferred. A tagged row passes on GCC 15's default with the defect in place. Pinning `-std=c17` in the contract project also works for tagged types. Earlier dialects were not run. A third option, inferred and not run, is to assert the defect directly, such as one definition of `b_status_E` in the preprocessed test file, which no compiler's tolerance can hide. Differing content is not a practical choice. The types header copies the module's own definitions, so a real build would need a define that changes them between the two preprocessing passes. That is inferred from the generator and was not tested.

DC-012's severity holds. #1463's reporter used GCC 16.2.0, and the report's type is untagged, which fails under C23 too.

DC-032's evidence no longer rests on reading the code. The spelling split, the `.d` spelling and the missed isolation are all observed on GCC 13 and GCC 15. The consequence is also observed. It is a false test failure when the sibling arrives first, and nothing when the mock arrives first. A false pass is possible in principle when a test expects the real behavior of a mocked inline function. That was not built. Medium still fits.

DC-032's second contract row needs two changes to fail today. The test must include `helper.h` before the mock, and it must test an inline function's mock. Otherwise the row passes against today's code (GAP3-12).

## Open questions

- **MinGW was not run.** No Windows host or MinGW toolchain is reachable here. A Linux-hosted MinGW cross compiler was not used, because the brief rules it out and its `.d` and line-marker spelling might not match a native MSYS2 GCC. #1463's reporter used MSYS2 GCC 16.2.0. Whether MinGW writes `./` in the `.d` is still open.
- **GCC 16 was not run.** I infer that it keeps C23 as its default and so behaves as GCC 15 does here.
- **Newer clang was not run.** Only stream 4's clang 15 result exists. Whether a clang release with C23 tag compatibility accepts the tagged redefinition is unknown.
- **The implementation header's flag.** DC-012's track says the implementation header must set the same `_WANTED` flag. These builds do not test that patch. They show only that `ceedling_partial_a_impl.c` is a third translation unit that holds both definitions.
