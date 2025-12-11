# ADR-003: Control Rate Expr

Date: 2025-12-05
Issue: https://github.com/Wasted-Audio/hvcc/issues/21

## Context

The `expr` object is one of the most common feature request of users. It would be great if we can support it.

There are two main approaches that could be done to achieve this.

One is to deconstruct an expression into constituent objects of a heavy graph. This would leverage the existing primitives (and likely expand them) and result in a chain of separate objects and functions. The downside of this for control rate expression is that the order of operations needs to be enforced, thus requiring injecting trigger objects to direct the control flow. This would create very complex graphs that are particularly hard to debug.

Another approach would be to take an expression and convert it into a new composit function that is called directly in the program. This has the upside of not needing to be deconstructed and control flow can be the same as typically expected for single object calls. It will also be easier to debug as there is a single function to point to. For control messages it would result in a much more simplified graph and likely a lower memory footprint as a result (do to simpler message passing). Even though program size might be a bit bigger.

## Decision

The expr object will need a specification in `heavy.ir.json` that describes the configuration. Other than some basic validation this object can be passed down to ir2c before it needs to be handled.

In ir2c the object initialization and implementation can be constructed. Pd expression function names can be replaced with library internal functions. The final function implementation is placed in `Heavy_NAME.cpp`.

Generic object methods for initialization and message handling are added to static expr library files and missing C functions will need to be added to `HvUtils.h`.

## MVP Definition

For the user to be able to create control rate expressions using common functions and both float and integer input variables.

## Future Improvements

* Deduplicate expressions - right now each expr object creates a new function definition
* Multiple expressions in a single object - we could split into multiple objects
* Missing functions - some are related to tables (will require passing the context) and others convert pitch or db values
