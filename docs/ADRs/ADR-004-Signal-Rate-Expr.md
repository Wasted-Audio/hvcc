# ADR-004: Signal Rate Expr

Date: 2025-12-05
Issue: https://github.com/Wasted-Audio/hvcc/issues/21

## Context

The `expr~` object is one of the most common feature request of users. It would be great if we can support it.

The two main approaches here are similar to control rate `expr`. We can either decompose the expression into a heavy graph or construct C code based on it.

The advantages of the second approach are not as pronounced as with the control rate code, although debugging will be easier with specific functions to point to.

The biggest caveat is that for signal execution the functions need to be able to handle SIMD buffers.

## Decision

We will take a similar approach as with control rate `expr`. A specification is added to `heavy.ir.json` and object handling is deferred to the ir2c stage of the compiler.

In order to properly handle expression conversion we need to replace all standard math symbols with internal signal rate functions from `HvMath.h`. One library that can be used for this is Arpeggio, in which a domain specific language (DSL) can be defined.

A submodule will handle expression parsing by Arpeggio. The grammar for pd expressions will be defined and an Arpeggio node-tree can be formed in which terms can be replaced by internal library functions. Missing functions will be added to `HvMath.h`.

As with control rate expressions we will allow maximum 100 inlets/values per expression, which whould be plenty for most usecases.

Testing signal patches is still underdeveloped in Heavy. Our objective here is mainly expression accuracy so we can also sample the expression output using `snapshot~`. Because of how in Heavy the `snapshot~` behavior is delayed by one audio cycle we need to add a short delay to each sampling. This way we can use control-type tests for these expressions and evaluate the stdout compared to known values.

## MVP Definition

For the user to be able to create signal rate expressions using common functions and at least non-SIMD audio buffers/values.

## Future Improvements

* Deduplicate expressions - right now each expr object creates a new function definition
* Multiple expressions in a single object - we could split into multiple objects
* Missing functions - some are related to tables (will require passing the context) and others convert pitch or db values
* SIMD support - Most relevant functions in `HvMath.h` currently only support `HV_SIMD_NONE` single sample processing
