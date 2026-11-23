#ifndef FOO_H
#define FOO_H
int foo_read(void);
static inline int foo_twice(int x) { return 2 * x; }
#endif
