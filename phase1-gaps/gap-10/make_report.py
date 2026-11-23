#!/usr/bin/env python3
"""Builds phase1-gaps/gap-10.md from phase1-gaps/gap-10.json plus the prose in this file."""
import json, os, re
from collections import Counter

here = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(here, "..", "gap-10.json")))

# Redesign note and BC flag by finding id. "BC" marks a BreakingChanges candidate.
R = {
 1: ("Keep. Directory-qualified placement is what keeps same-named Partials apart.", ""),
 2: ("Keep. Function names cannot be qualified without breaking every test that calls them.", ""),
 3: ("Keep and document the limit. A module-qualified type or variable name would change `PARTIAL_TYPE` and the original variable names.", "BC only if names gain a qualifier"),
 4: ("Keep the folder in lifecycle names. Shared mocks in 1.3 need a name that does not depend on one test's include spelling.", ""),
 5: ("Keep. A directory in the name would change `PARTIAL_TYPE`.", "BC only if names gain a directory"),
 6: ("Keep.", ""),
 7: ("Keep. A module part in the promoted name would change `PARTIAL_LOCAL_VAR`.", "BC only if names gain a module"),
 8: ("Read the module name once, after preprocessing, or stop the macro expanding it. Changelog Fixed, as for #1460.", ""),
 9: ("Keep. It is the compiler's rule, so the resolver that finds these headers must take the includer (S5-03).", ""),
 10: ("Trace before changing. The runner should spell a Partial header as the test did.", ""),
 11: ("Keep as the single module identity. Every lookup of a Partial's files should key on it.", ""),
 12: ("Docs fix.", ""),
 13: ("Keep.", ""),
 14: ("Keep.", ""),
 15: ("The unqualified name should go through the same trailing-directory resolver as S5-01 and #1459.", ""),
 16: ("Matching whole path components or the filename would change what existing invocations select. Otherwise say \"directory substring\" in the docs.", "BC candidate if tightened"),
 17: ("Keep.", ""),
 18: ("Keep.", ""),
 19: ("One implementation for `test:`, `bullseye:` and `gcov:`. Today each has its own copy of the path and pattern code.", ""),
 20: ("Docs fix.", ""),
 21: ("Docs fix, or let the task exist when assembly is off.", ""),
 22: ("Docs fix. The task is `files:header`.", ""),
 23: ("Do not register directories or globs as header files. Changelog Fixed.", ""),
 24: ("Make `:artifact` follow `:build`'s own fallback, or fix the docs. A fix moves where existing projects' artifacts are sought.", "BC candidate"),
 25: ("Clean the paths each stage resolved, not only the configured ones. Changelog Fixed.", ""),
 26: ("Keep.", ""),
 27: ("Keep.", ""),
 28: ("Keep.", ""),
 29: ("Keep.", ""),
 30: ("Keep.", ""),
 31: ("Keep.", ""),
 32: ("Keep.", ""),
 33: ("Keep.", ""),
 34: ("Keep. Values are standardized before the check.", ""),
 35: ("Keep. Merged list order feeds the search order of S5-02.", ""),
 36: ("Keep.", ""),
 37: ("Keep.", ""),
 38: ("Require `:paths` ↳ `:test` only when tests are built, or fix the docs. Changelog Fixed.", ""),
 39: ("Keep.", ""),
 40: ("Keep.", ""),
 41: ("Keep.", ""),
 42: ("Keep.", ""),
 43: ("Docs say the copy is flat.", ""),
 44: ("Keep.", ""),
 45: ("Docs fix.", ""),
 46: ("Keep. Output names take the first extension.", ""),
 47: ("Keep.", ""),
 48: ("Docs say what `-I` holds. Per-stage search paths (#1442) will change that list again.", ""),
 49: ("Docs fix. The examples are illustrative.", ""),
 50: ("Keep.", ""),
 51: ("Keep.", ""),
 52: ("Match `test:`, which raises, or document the first-wins notice.", ""),
 53: ("Docs write `<build root>`.", ""),
 54: ("Document the basename rule, or keep the configured directory.", ""),
 55: ("Keep.", ""),
 56: ("Keep.", ""),
 57: ("Keep. The Bullseye side is unrun.", ""),
 58: ("Keep.", ""),
 59: ("Keep. Anchor to the project root if a same-named directory elsewhere matters.", ""),
 60: ("Keep. The patterns depend on the spelling the coverage tool reports.", ""),
 61: ("Keep. The `#line` path is a contract with the coverage plugins, so any change to source path spelling must keep it.", ""),
}


def verdict_of(f):
    m = re.match(r"Verdict: (.*?)\.(?: |$)", f["claim"])
    if m:
        return m.group(1)
    return f["status"]


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def evid(f, n=3):
    e = f["evidence"][:n]
    s = "<br>".join("`%s`" % x for x in e)
    if len(f["evidence"]) > n:
        s += "<br>+%d more in the JSON" % (len(f["evidence"]) - n)
    return s


def final_text(f):
    return f["claim"]


ids = Counter(f["status"] for f in F)
verdicts = Counter(verdict_of(f).split(" (")[0] for f in F)

out = []
w = out.append

w("# GAP-10 report: path language in the docs the promise ledger did not cover\n")
w("## Summary\n")
w("I ledgered %d path promises and findings from the user docs and plugin docs that stream 5 left out. " % len(F) +
  "The headline experiment answers the `_AT` question. Two same-named modules `a/util` and `b/util` in one test "
  "do not collide on the generated names that drop the directory, unless they already collide on a name the "
  "module owns. Type names such as `ceedling_partial_util_s_ctx_t` repeat across the two modules. They clash at "
  "compile time only when both modules declare a variable of the same name, and that variable already clashes at "
  "link without the type. Generated files, include guards and mock lifecycle names keep the directory and stay apart. ")
w("The ledger found these promises broken: a Partial module named like a predefined macro such as `unix` never "
  "reaches its file, the tasks `paths:header` and `files:include` do not exist, `files:assembly` exists with assembly off, "
  "a release build needs `:paths ↳ :test`, and the Dependencies plugin's `:artifact` path skips "
  "`:source` and its clean misses the default path. ")
w("`test:path` is a substring match on the test's directory only, not on its path. "
  "Most other path promises hold. The generated Partial headers hold bare-name includes that are right only because "
  "the compiler checks the includer's directory first. ")
w("Final status after verification: %s. " % ", ".join("%d %s" % (v, k) for k, v in sorted(ids.items())) +
  "No gcov, Bullseye or Cppcheck run happened, so those rows rest on reading the plugin code.\n")

w("## What I ran\n")
w("- Setup: `git submodule update --init`, `bundle install`, and `git log -1 --format=%h` printed `402e491`.")
w("- Builds, all with `:project` ↳ `:which_ceedling` set to this checkout. Each build ran with `-v 4`, and each excerpt log's "
  "first line shows `Launching Ceedling from /home/user/Ceedling/`.")
w("  - `phase1-gaps/gap-10/collide/` holds `gen.sh` (generates 12 projects), `run.sh` (runs them), `results.txt`, trimmed logs and generated-file excerpts.")
w("  - `phase1-gaps/gap-10/cli/` holds three tests (two named `test_foo.c`) and the `test:` task runs.")
w("  - `phase1-gaps/gap-10/deps/` holds one Dependencies project for `paths:include` and `files:header`.")
w("  - `phase1-gaps/gap-10/release/` holds four release builds and one that fails validation.")
w("  - `phase1-gaps/gap-10/dependencies_paths.txt` and `gcov_pattern_check.txt` come from direct Ruby calls.")
w("- Not run: any gcov, gcovr, ReportGenerator, Bullseye or Cppcheck task, and any Windows-only path.")
w("- Verification: %d findings in batches of 10 went to Sonnet verifiers. The batch files are in `verify/`. "
  "I gave each verifier the batch file path in place of the JSON text at the end of the prompt. "
  "Every verdict that was not `confirmed` went to an Opus adjudicator. Section \"Verification\" has the counts.\n" % len(F))

w("## The same-named `_AT` experiment\n")
w("One test file holds two `#include TEST_PARTIAL_*_MODULE_AT` lines, one for `a`, one for `b`, both naming `util`. "
  "Each `util.c` defines a static and a public function. Names inside the projects are in `collide/gen.sh`.\n")
w("| Variant | Setup | Result | Generated names that repeat |")
w("|---|---|---|---|")
rows = [
 ("v1", "PUBLIC ×2; same static `util_helper`; public `a_pub`, `b_pub`", "builds, 1 passed", "none repeat except `util_helper`, which stays static and out of the Partial"),
 ("v5", "PUBLIC ×2; `a_ctx`, `b_ctx` typed statics", "builds, 1 passed", "`ceedling_partial_util_a_ctx_t`, `..._b_ctx_t` differ"),
 ("v6", "MOCK PUBLIC ×2", "builds, 1 passed", "lifecycle names get `a_` and `b_` prefixes"),
 ("v9", "unqualified `TEST_PARTIAL_PUBLIC_MODULE(util)`, two `util.c`", "builds, 1 passed; NOTICE picks `src/a/util.c`", "one Partial only"),
 ("v1b", "PUBLIC ×2 plus `TEST_PARTIAL_CONFIG_AT` selecting `util_helper` in both", "link: multiple definition of `util_helper`", "function name"),
 ("v2", "PUBLIC ×2; same public `util_pub`", "link: multiple definition of `util_pub`", "function name"),
 ("v3", "PRIVATE ×2; same static `util_helper`", "link: multiple definition of `util_helper`", "function name"),
 ("v4", "PUBLIC ×2; `static struct { int count; } s_ctx;` in both", "compile: conflicting types for `ceedling_partial_util_s_ctx_t` and `s_ctx`", "`ceedling_partial_util_s_ctx_t`, `s_ctx`"),
 ("v7", "PUBLIC ×2; `static int s_count;` in both", "link: multiple definition of `s_count`", "variable name"),
 ("v6b", "as v6 with `:mock_name_include_folder: FALSE`", "link: multiple definition of `Mockceedling_partial_util_interface_Init`, `_Verify`, `_Destroy`", "CMock lifecycle names"),
 ("v8", "module named `unix`, `TEST_PARTIAL_PUBLIC_MODULE(unix)`", "link: undefined reference to `unix_pub`", "`ceedling_partial_1_impl.h` instead of `..._unix_...`"),
]
for r in rows:
    w("| " + " | ".join(cell(x) for x in r) + " |")
w("")
w("The generated identifiers in the passing build are these. Files sit below `build/test/partials/test/test_collide/_t_/`.\n")
w("- Files: `a/ceedling_partial_util_impl.{c,h}` and `b/ceedling_partial_util_impl.{c,h}`.")
w("- Include guards: `GENB59956D4_A_CEEDLING_PARTIAL_UTIL_IMPL_H_CEEDLING` and `GEN7118F419_B_CEEDLING_PARTIAL_UTIL_IMPL_H_CEEDLING`.")
w("- Type names (v4): `ceedling_partial_util_s_ctx_t` in both types headers.")
w("- Mock names (v6): `a_Mockceedling_partial_util_interface_Init` and `b_Mockceedling_partial_util_interface_Init`.")
w("- Promoted statics: `partial_<function>_<variable>`, with no module part.\n")
w("The answer to the question is no, with one qualification. The module name without its directory appears only in type "
  "names. A type name repeats across the two modules only when the variable's name repeats, and then the variable "
  "collides by itself. Nothing else tested collides on the module name alone. The qualification is that "
  "`PARTIAL_TYPE(util, s_ctx)` cannot say which module it means. That matters only to a design that wants both modules' "
  "variables of one name in one test, and the variable name would still have to differ.\n")

w("## Ledger\n")
w("Verdicts are kept, broken, partly kept and untestable, as in stream 5. \"Defect\" marks a finding that is not a promise. "
  "BC means a compiler-faithful or tidier redesign would contradict the promise and needs a BreakingChanges entry. "
  "Doc cites are in each finding's JSON `evidence`. Experiment files are under `phase1-gaps/gap-10/`.\n")
w("| ID | Promise | Verdict | Evidence | Issue | Redesign note | BC |")
w("|---|---|---|---|---|---|---|")
for i, f in enumerate(F, 1):
    note, bc = R[i]
    iss = ", ".join("#" + x for x in f["issues"]) if f["issues"] else "none"
    v = verdict_of(f)
    if f["status"] == "refuted":
        v = "refuted after review"
    elif f["status"] == "revised":
        v = v + " (revised)"
    w("| %s | %s | %s | %s | %s | %s | %s |" % (f["id"], cell(f["title"]), cell(v), cell(evid(f)), iss, cell(note), cell(bc)))
w("")

w("## Defects and open questions\n")
w("### Defects\n")
for f in F:
    if f["kind"] == "defect" or verdict_of(f).startswith("broken"):
        w("- **%s** %s. %s" % (f["id"], f["title"], f["claim"].split(". ", 1)[-1] if f["claim"].startswith("Verdict:") else f["claim"]))
w("")
w("### Open questions\n")
w("- The runner of a test naming two same-named `_AT` Partials includes one impl header by bare name (GAP10-10). I did not trace which step collapses the two.")
w("- Windows behavior of mixin names and `~` in `:which_ceedling` (GAP10-34, GAP10-40). Traced from code only. No Windows run, and no `~` run for which-ceedling.")
w("- Whether `_AT`'s module argument is macro-replaced the way the unqualified argument is (GAP10-08). The code path suggests it. I did not build it.")
w("- Bullseye's claim that stored source paths are relative to the coverage file, and every gcov, gcovr and ReportGenerator row. No tool ran.")
w("- GAP-04 overlap. I left out the Dependencies `:includes` directory rule and `:build_lib` object placement, and Bullseye's coverage filters, as the brief says.")
w("")
w("### Doc rows that matter for a redesign\n")
w("- The generated Partial headers and sources depend on the includer's directory for their own bare-name includes (GAP10-09). Any resolver that skips the includer breaks them when two same-named Partials share the `-I` list.")
w("- `test:path` selects by directory substring (GAP10-16). A rewrite that matches path components is a BreakingChanges entry.")
w("- The Dependencies plugin's path fallbacks (GAP10-24, GAP10-25) disagree with its docs in ways that depend on which paths a project names.\n")

w("## Verification\n")
w("Status counts: %s. Verifier verdicts: %s." % (
    ", ".join("%d %s" % (v, k) for k, v in sorted(ids.items())),
    ", ".join("%d %s" % (v, k) for k, v in sorted(Counter(f["verdict"]["verdict"] for f in F).items()))))
adj = [f for f in F if f["ruling"]]
if adj:
    w("")
    w("Adjudicated findings:\n")
    for f in adj:
        w("- **%s** verifier %s, adjudicator %s. %s" % (f["id"], f["verdict"]["verdict"], f["ruling"]["final"], f["ruling"]["reason"]))
w("")
open(os.path.join(here, "..", "gap-10.md"), "w").write("\n".join(out) + "\n")
print("report written", len(out), "lines")
