#ifndef B_H
#define B_H
typedef enum b_status_e { B_OK, B_FAIL } b_status_E;
typedef struct b_cfg_s { int x; } b_cfg_S;
b_status_E b_do(int x);
#endif
