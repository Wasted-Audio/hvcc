# OWL

The main project output for this generator can be found in  `<output_dir>/owl/`.

## implementation

This generator uses some separate "raw" code paths to link the DSP graph. Instead of `@hv_param` currently `@raw` and `@raw_param` are used.

Legacy `@owl` and `@owl_param` are still functional for backwards compatibility.

It currently also overloads `HvMessage.c` and `HvUtils.h` with some different optimizations for this target.

Relevant files:

* custom interpreter: `hvcc/interpreters/pd2hv/pdowl.py`
* generator: `hvcc/generators/c2owl/c2owl.py`
* custom deps:
  * `hvcc/generators/c2owl/deps/HvMessage.c`
  * `hvcc/generators/c2owl/deps/HvUtils.h`
* templates:
  * `hvcc/generators/c2owl/templates/HeavyOwl.hpp`
  * `hvcc/generators/c2owl/templates/HeavyOwlConstants.h`

## Debugging

A very useful feature for debugging is the `[print]` object. If you send a message to `[print]` it will be sent out as an OWL patch message. This means that if you are using the patch library and are connected to the device then the messages will appear in the browser. You can add a string construction argument which will be concatenated with the received message. Messages are limited to maximum 62 characters long. If you have several `[print]` objects in your patch then only the most recently fired message will be sent. If you want to view several values simultaneously you can always `[pack]` them together into one message. On a device that has a screen (such as the Magus) the message will also appear in realtime on the screen.
