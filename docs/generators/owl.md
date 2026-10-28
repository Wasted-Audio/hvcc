# OWL

This generator targets [Open Ware Laboratory](https://www.openwarelab.org/).

The main project output for this generator can be found in  `<output_dir>/owl/`.

## Inputs and Outputs

### Parameters

There is a legacy and a recommended way to assign `[receive]` objects to specific OWL parameters. The legacy way is to use e.g. `[receive Channel-A]` to receive a value (between 0 and 1) from OWL parameter A. The recommended way is to use the `@raw` attribute.

```sh
[receive NAME @raw PARAM MIN MAX DEFAULT]
```

receive a value called `NAME`, assigned to OWL parameter `PARAM`, in the range `MIN` to `MAX`, with default value `DEFAULT`.

example:

```sh
[r Freq @raw A 220 880 440]
```

defines a receiver (r is shorthand for receive) called Freq, assigned to OWL parameter A. The output is a float in the range 220.0 to 880.0 with default value 440.0.

MIN, MAX and DEFAULT are optional. If omitted, MIN is 0, MAX is 1, and DEFAULT is calculated as the midway between the two. It is fine to declare only MIN and MAX, only MIN, none, or all.

The compiler supports up to 32 parameters, in four groups of eight, named from A to H, AA to AH and BA to BH, but the available hardware assignments vary depending on the OWL device. Magus has 20 CV inputs/outputs, OWL Pedal, OWL Modular and Wizard have 5, Alchemist has 4. All 32 OWL parameters can also be controlled by MIDI, as each is associated with a MIDI CC controller.

Output parameters can be assigned in the same way, using `[send]` instead of `[receive]`. The compiler will add `>` to the end of the parameter name, to ensure it is recognised as an output.

### Buttons, Gates and Triggers

For hardware that supports input and output triggers, gates, and buttons, these can be assigned with the names `B1` through `B11`, or `Push` for PUSHBUTTON. Output values from `[receive]` are `0` for _off_, `1` for _on_. Any `[send]` value greater than `0.5` will be interpreted as on.

## MIDI

Patches can send and receive MIDI messages with the usual Pd Vanilla MIDI I/O objects: `[notein]`, `[bendin]`, `[ctlin]`, `[touchin]`, `[polytouchin]`, `[pgmin]`, and `[noteout]`, `[bendout]`, `[ctlout]`, `[touchout]`, `[polytouchout]`, `[pgmout]`.

## Implementation

This generator uses some separate "raw" code paths to link the parameter controls. Instead of `@hv_param` currently `@raw` and `@raw_param` are used.

Legacy `@owl` and `@owl_param` are still functional for backwards compatibility.

It currently also overloads `HvMessage.c` and `HvUtils.h` with some different optimizations for this target.

Relevant files:

- custom interpreter: `hvcc/interpreters/pd2hv/pdowl.py`
- generator: `hvcc/generators/c2owl/c2owl.py`
- custom deps:
  - `hvcc/generators/c2owl/deps/HvMessage.c`
  - `hvcc/generators/c2owl/deps/HvUtils.h`
- templates:
  - `hvcc/generators/c2owl/templates/HeavyOwl.hpp`
  - `hvcc/generators/c2owl/templates/HeavyOwlConstants.h`

## Debugging

A very useful feature for debugging is the `[print]` object. If you send a message to `[print]` it will be sent out as an OWL patch message. This means that if you are using the patch library and are connected to the device then the messages will appear in the browser. You can add a string construction argument which will be concatenated with the received message. Messages are limited to maximum 62 characters long. If you have several `[print]` objects in your patch then only the most recently fired message will be sent. If you want to view several values simultaneously you can always `[pack]` them together into one message. On a device that has a screen (such as the Magus) the message will also appear in realtime on the screen.

## Compilation

Requires the [OwlProgram](https://github.com/Wasted-Audio/OwlProgram) SDK, `make` and `gcc-arm-none-eabi` to build.
