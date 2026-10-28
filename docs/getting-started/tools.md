# CLI & Tools

The installation ships with two commandline tools.

## HVCC

This is the main compiler tool and is used for converting PD patch files to C/C++ and different wrapper/generator outputs.

Its general usage is described in the [README](../index.md#basic-usage).

Some additional flags:

- `-G, --ext-gen`: External generator module loading, used for [custom](../generators/custom.md) generators.
- `--gui`: Enables GUI object parsing into GUI IR.
- `--nodsp`: Generates control-only patches without audio signal processing.
- `--results_path`: Emits compilation metrics and manifest as JSON.
- `-v, --verbose`: Adds additional output at compilation steps.
- `-V, --version`: Outputs the current hvcc version.

## Hvutil

This additional tool provides some commands that can help during development:

- `hvutil pdobjects`: Dumps all supported message and signal objects as JSON.
- `hvutil hvhash <string>`: Hashes strings to 32-bit hex integers (essential for C/C++ API parameter addressing).
- `hvutil metaschema`: Outputs the full JSON schema for `meta.json`.
