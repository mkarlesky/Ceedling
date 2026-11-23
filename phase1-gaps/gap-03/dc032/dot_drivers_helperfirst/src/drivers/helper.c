#include "helper.h"
#include "foo.h"

int helper_value(void)
{
  return foo_read() + 1;
}
