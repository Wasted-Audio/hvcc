# ADR-005: PDNAM External

Date: 2026-04-20

PR: https://github.com/Wasted-Audio/hvcc/pull/365

## Context

Recently someone posted a very small NAM implementation, called [MicroNAM](https://github.com/jaffco/MicroNAM), that can be embedded and run on STM32 via ie. the Daisy platform. Immediately the thought came up that this would be very nice to integrate into Heavy.

Because until now there was no basic NAM loader for PD first an external, based on NeuralAudio library, called [PDNAM](https://github.com/wasted-Audio/pdnam) was created. It takes only a single argument to a NAM model json file. Due to its simplicity a port to Heavy should be relatively easy.

### Capabilities

MicroNAM supports loading 4 WaveNet model types:

- Nano
- Feather
- Lite
- Standard

We should be able to load all of these in our implementation as well.

Included in MicroNAM is a python script that converts a WaveNet model file to a C header. We should be able to call this code, or a derivative, from HVCC.

Since MicroNAM is written in C++ we will need to have a C extern wrapper so it can be loaded by Heavy C code.

## Decision

A new internal object `__nam~f` will be defined that defers the implementation of `[pdnam~]` using an abstraction. During the IR stage we will then parse the first argument - path to the NAM file - to detect which model type is being used. At this stage we will then overload the specific object type, depending on the model. All types are defined in the core `heavy.ir.json`.

Subsequently the `ir2c` stage will then handle these new object types returning the specific `c_struct`, initialization, free, and process methods to use. The implementations for these are defined in `HvSignalNam.h` and `HvSignalNam.c`. During initialization the size of the model weights is returned to include in the Heavy memory accounting logic.

Because MicroNAM is written in C++ we need to create `MicroNAM_C.h/cpp` C externs that handle all the initialization, processing and freeing in our Heavy implementation. MicroNAM is added as a submodule as part of the `static/` files. The C externs and MicroNAM code will be included in the output when the `SignalNam` objects are used.

In order to include the model weights as a header we will extend `HeavyObject` with a new method `get_C_gen_header_code` that is currently only used by our `SignalNam` class. Here we can then convert the NAM file to a newly generated header. The `ir2c` stage will then collect any such generated headers and write them to the output directory.

For inferring the model type and creating the model weights name and header file we will modify and include the original MicroNAM python script and use it as a local `SignalNamHeader` module, for use in the various mentioned processing stages.

## MVP Definition

The user should be able to create a patch using `[pdnam~ <path_to_nam_file>]` and have it converted to C and run during processing. The resulting output should be very comparable to the `pdnam~` runtime.

## Future Improvements

We can possibly load NAM models more dynamically by parsing the JSON and updating the model weights. This would be limited to a specific model type and adds other complexity, so is currently unwanted.

We will stick to a pure static implementation for the time being.

Right now SIMD implementations are missing, these could possibly be added in the future.
