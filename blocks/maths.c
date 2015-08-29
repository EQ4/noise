#include <math.h>
#include <stdlib.h>
#include "block.h"
#include "blockdef.h"
#include "error.h"
#include "util.h"

static error_t add_pull(node_t * node, object_t ** output)
{
    error_t e = SUCCESS;
    object_t * input0 = NULL;
    e |= node_pull(node, 0, &input0);

    object_t * input1 = NULL;
    e |= node_pull(node, 1, &input1);

    if (input0 == NULL || input1 == NULL) {
        output = NULL;
        return e;
    }

    double x = CAST_OBJECT(double, input0);
    double y = CAST_OBJECT(double, input1);

    // Do the magic here:
    double result = x + y;
    // --

    CAST_OBJECT(double, node->state) = result;
    *output = node->state;

    return e;
}

static error_t subtract_pull(node_t * node, object_t ** output)
{
    error_t e = SUCCESS;
    object_t * input0 = NULL;
    e |= node_pull(node, 0, &input0);

    object_t * input1 = NULL;
    e |= node_pull(node, 1, &input1);

    if (input0 == NULL || input1 == NULL) {
        output = NULL;
        return e;
    }

    double x = CAST_OBJECT(double, input0);
    double y = CAST_OBJECT(double, input1);

    // Do the magic here:
    double result = x - y;
    // --

    CAST_OBJECT(double, node->state) = result;
    *output = node->state;

    return e;
}

static error_t multiply_pull(node_t * node, object_t ** output)
{
    error_t e = SUCCESS;
    object_t * input0 = NULL;
    e |= node_pull(node, 0, &input0);

    object_t * input1 = NULL;
    e |= node_pull(node, 1, &input1);

    if (input0 == NULL || input1 == NULL) {
        output = NULL;
        return e;
    }

    double x = CAST_OBJECT(double, input0);
    double y = CAST_OBJECT(double, input1);

    // Do the magic here:
    double result = x * y;
    // --

    CAST_OBJECT(double, node->state) = result;
    *output = node->state;

    return e;
}

static error_t divide_pull(node_t * node, object_t ** output)
{
    error_t e = SUCCESS;
    object_t * input0 = NULL;
    e |= node_pull(node, 0, &input0);

    object_t * input1 = NULL;
    e |= node_pull(node, 1, &input1);

    if (input0 == NULL || input1 == NULL) {
        output = NULL;
        return e;
    }

    double x = CAST_OBJECT(double, input0);
    double y = CAST_OBJECT(double, input1);

    // Do the magic here:
    double result = x / y;
    // --

    CAST_OBJECT(double, node->state) = result;
    *output = node->state;

    return e;
}


static error_t note_to_freq_pull(node_t * node, object_t ** output)
{
    error_t e = SUCCESS;
    object_t * input0 = NULL;
    e |= node_pull(node, 0, &input0);

    if (input0 == NULL) {
        output = NULL;
        return e;
    }

    double note = CAST_OBJECT(double, input0);
    CAST_OBJECT(double, node->state) = pow(2,(note-69)/12)*440;
    *output = node->state;

    return e;
}

 
node_t * math_create(enum math_op op)
{
    pull_fn_pt node_pull_fn;
    size_t n_inputs = 2;
    const char * name;
    switch(op)
    {
    case MATH_ADD:
        node_pull_fn = &add_pull;
        name = "Add";
        break;
    case MATH_SUBTRACT:
        node_pull_fn = &subtract_pull;
        name = "Subtract";
        break;
    case MATH_MULTIPLY:
        node_pull_fn = &multiply_pull;
        name = "Multiply";
        break;
    case MATH_DIVIDE:
        node_pull_fn = &divide_pull;
        name = "Divide";
        break;
    case MATH_NOTE_TO_FREQ:
        node_pull_fn = &note_to_freq_pull;
        name = "Note to Freq.";
        n_inputs = 1;
        break;
    default:
        return NULL;
    }

    node_t * node = node_alloc(n_inputs, 1, double_type);
    node->name = strdup(name);
    node->destroy = &node_destroy_generic;
    
    // Define inputs
    if (n_inputs == 1) {
        node->inputs[0] = (struct node_input) {
            .type = double_type,
            .name = strdup("freq"),
        };
    } else {
        node->inputs[0] = (struct node_input) {
            .type = double_type,
            .name = strdup("x"),
        };
        node->inputs[1] = (struct node_input) {
            .type = double_type,
            .name = strdup("y"),
        };
    }

    // Define outputs (0: double sum)
    node->outputs[0] = (struct endpoint) {
        .node = node,
        .pull = node_pull_fn,
        .type = double_type,
        .name = strdup("result"),
    };

    return node;
}