#include "src/b/b.h"

b_status_E b_do(int x)
{
  return (x > 0) ? B_OK : B_FAIL;
}
