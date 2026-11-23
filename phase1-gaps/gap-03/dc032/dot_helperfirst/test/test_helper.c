#include "unity.h"
#include "src/drivers/helper.h"
#include "src/drivers/mock_foo.h"

void setUp(void) {}
void tearDown(void) {}

void test_helper_value(void)
{
    foo_read_ExpectAndReturn(4);
    TEST_ASSERT_EQUAL_INT(5, helper_value());
}

void test_foo_twice_is_mocked(void)
{
    foo_twice_ExpectAndReturn(3, 100);
    TEST_ASSERT_EQUAL_INT(100, foo_twice(3));
}
