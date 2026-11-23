#!/bin/sh
# Runs e2 and e2_tagged under GCC 15 (gcc:15 image) and the native GCC 13.
# Writes e2/results-gcc15.txt and e2_tagged/results.txt.
HERE=$(cd "$(dirname "$0")" && pwd)
{
for std in "" "-std=c17" "-std=c23"; do
  echo "===== GCC 15 (docker gcc:15) e2 ${std:-default}"
  docker run --rm -v "$HERE/e2:/w" -w /w gcc:15 sh -c "gcc --version | head -1; gcc $std -dM -E -x c /dev/null | grep __STDC_VERSION__; ./run-gcc.sh $std" 2>&1
done
for std in "" "-std=c2x"; do
  echo "===== GCC 13 native e2 ${std:-default}"
  (cd "$HERE/e2" && gcc --version | head -1 && gcc $std -dM -E -x c /dev/null | grep __STDC_VERSION__; ./run-gcc.sh $std) 2>&1
done
} > "$HERE/e2/results-gcc15.txt"
{
for std in "" "-std=c17" "-std=c23"; do
  echo "===== GCC 15 (docker gcc:15) e2_tagged ${std:-default}"
  docker run --rm -v "$HERE/e2_tagged:/w" -w /w gcc:15 sh -c "gcc --version | head -1; gcc $std -dM -E -x c /dev/null | grep __STDC_VERSION__; ./run-gcc.sh $std" 2>&1
done
for std in "" "-std=c2x"; do
  echo "===== GCC 13 native e2_tagged ${std:-default}"
  (cd "$HERE/e2_tagged" && gcc --version | head -1 && gcc $std -dM -E -x c /dev/null | grep __STDC_VERSION__; ./run-gcc.sh $std) 2>&1
done
} > "$HERE/e2_tagged/results.txt"
