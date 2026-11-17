# ADR-007: Parameter Ordering

Date: 2026-07-16

Issue: https://github.com/Wasted-Audio/hvcc/issues/57

## Context

Until now Heavy parameter ordering was always alphabetical. However in some Generators a more specific ordering is wanted.

Internally the ordering is initially based on the receiver creation order and then later in the compiler forced to be alphabetized.

One suggestion was to use the same syntax as Faust, which is to optionally prepend a parameter with a number enclosed in brackets. This way instead of `[r Vol @hv_param]` we would write `[r [1]Vol @hv_param]`. Compared to other options this would be rather elegant and an easy syntax to convey.

## Decision

We will adjust several compiled steps to allow, order and cleanup this additional syntax.

- `core.hv2ir.HIrReceive` validates the new syntax and only string prepended with or without a number in brackets are allowed
- `core.hv2ir.HeavyGraph` sorts all the receivers based on the optional syntax and then drops it for externed parameters before returning the ir receiver dictionary
- `ir2c` and `compiler` stages no longer force alphabetical ordering
- `pd2gui` only needs to drop the syntax

Validation and sorting stages get unit tests to confirm their intended behavior.

This will only apply to input parameters and events. Output parameters and events are excluded as they are constructed individually and not as a list, which makes their sorting nearly impossible.

### Syntax rules

- Only one bracketed tag, and only at the start of the name is allowed. `[1][2]bla` is rejected.
- No non-word characters anywhere else in the name (this already applied before this change)
- A bare `[1]` with no name following it is rejected.

### Sort behavior

Tagged receivers will always sort before untagged ones, and untagged receivers fall back to the original alphabetical order. Non-extern receivers are not exempt from the tag syntax being present in their name. A bracketed prefix on a non-extern receiver becomes part of its literal identifier (and must match on the corresponding `[s ]`), rather than being stripped or treated specially. Ordering tags are only intended for use on `@hv_param`/`@hv_event` receivers.

## MVP Definition

The user should be able to, optionally, prepend their externed parameters using the bracket+number syntax and see their intended order used in the generator output.

## Future Improvements

Unless there are unforeseen edge-cases we currently don't see any other extensions to this syntax and it should be kept minimal for this specific purpose.

Potentially we can look at sorting output parameters/events in the future, but this is very low priority.
