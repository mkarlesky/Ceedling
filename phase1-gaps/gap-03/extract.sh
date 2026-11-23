#!/bin/sh
# Trims each full log in work/ to the lines this report cites, and copies the generated
# files it cites out of each work/<name>/build/ tree. Output goes to results/.
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$HERE/results; rm -rf "$OUT"; mkdir -p "$OUT"
for log in "$HERE"/work/*.log; do
  name=$(basename "$log" .log); W=$HERE/work/$name; R=$OUT/$name.txt
  {
    echo "# Trimmed from the full --verbosity=obnoxious log of work/$name.log ($(wc -l < "$log") lines)."
    echo "# Kept: the run header, Ceedling's launch lines, step headings, NOTICEs, compiler errors,"
    echo "# the test file's compile command, test results and the exit status. Line numbers are the full log's."
    grep -n -E '^### |Launching Ceedling|which Ceedling|^(Preprocessing|Generating|Compiling|Linking|Running) |NOTICE|EXCEPTION| error: | note: |^(In file included|  +from )|-c "test/test_[a-z]*\.c"|^test_[a-z]*\.c:[0-9]+:|^(TESTED|PASSED|FAILED|IGNORED):|Tests [0-9]+ Failures' "$log"
    for d in $(cd "$W" 2>/dev/null && find build/test/dependencies -name 'test_*.d*' | sort); do
      echo; echo "# ---- generated file $d"; cat "$W/$d"
    done
    case $name in p1463-*)
      for f in ceedling_partial_b_types.h ceedling_partial_b_interface.h ceedling_partial_a_impl.h ceedling_partial_a_impl.c; do
        echo; echo "# ---- generated file build/test/partials/test/test_a/_t_/$f"; cat "$W/build/test/partials/test/test_a/_t_/$f"
      done
      for d in ceedling_partial_a_impl.d test_a_runner.d mock_ceedling_partial_b_interface.d; do
        p=build/test/dependencies/test/test_a/_t_/$d
        [ -f "$W/$p" ] && { echo; echo "# ---- generated file $p"; cat "$W/$p"; }
      done;;
    esac
    case $name in dc032-*)
      echo; echo "# ---- files under build/test/mocks"; (cd "$W" && find build/test/mocks -type f | sort)
      c=$(cd "$W" && find build/test/mocks -name foo.h); echo; echo "# ---- generated file $c (CMock's copy under :treat_inlines: :include)"; cat "$W/$c"
      echo; echo "# ---- line markers naming src/drivers in the preprocessed test file (build/test/preprocess/files/.../full_expansion/test/test_helper.c)"
      grep -h '^# [0-9]* ".*src/drivers' "$W"/build/test/preprocess/files/test/test_helper/_t_/full_expansion/test/test_helper.c;;
    esac
  } > "$R"
done
ls -la "$OUT"
