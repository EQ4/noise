#include "block.h"

enum math_op {
    MATH_ADD,
    MATH_SUBTRACT,
    MATH_MULTIPLY,
    MATH_DIVIDE,
    MATH_NOTE_TO_FREQ
};

// Block defs

// Accumulator<> :: (double x) -> (double x_sum); Sums an input
node_t * accumulator_create();

// Constant<type value> :: () -> (type value); Returns a constant value
node_t * constant_create(object_t * constant_value);

// Debug<> :: (double x) -> (); Prints output on pull; use with run_debug(...)
node_t * debug_create();

// FunGen<> :: (double t) -> (double x); Sine fn generator. Computes x = sin(t)
node_t * fungen_create();

// Math<math_op> :: (double x[, double y]) -> (double result); Performs a basic math op on inputs (see enum math_op)
node_t * math_create(enum math_op op);
