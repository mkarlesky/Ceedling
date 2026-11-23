#include "unity.h"
#include "src/drivers/mock_foo.h"
#include "helper.h"

void setUp(void) {}
void tearDown(void) {}

void test_helper_value(void)
{
    foo_read_ExpectAndReturn(4);
    TEST_ASSERT_EQUAL_INT(5, helper_value());
}
