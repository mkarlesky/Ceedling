#include "unity.h"
#include "ceedling.h"

#include TEST_PARTIAL_MODULE(a)
TEST_PARTIAL_CONFIG(a, a_run, )
#include MOCK_PARTIAL_PUBLIC_MODULE(b)

void setUp(void) {}
void tearDown(void) {}

void test_run(void)
{
    b_do_ExpectAndReturn(5, B_OK);
    TEST_ASSERT_EQUAL_INT(1, a_run(5));
}
