#include "src/a/a.h"
#include "src/a/helper.h"
#include "src/b/b.h"

int a_run(int x)
{
  return (b_do(x) == B_OK) ? 1 : 0;
}
