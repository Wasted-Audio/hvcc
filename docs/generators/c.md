# C

This is the default generator and outputs only the IR and HeavyLang results, the converted C code of the patch, and all required Heavy library files to the output directory.

It is the responsibility of the user to create the appropriate wrapper for integrating this code.

Created directories:

- `hv`: Has the HeavyLang version of the PD patch as JSON.
- `ir`: Has the Heavy IR version of the patch as JSON.
- `c`: Contains the generated C code together with all the required Heavy library files.

See the [C API](../reference/c.md) and [C++ API](../reference/cpp.md) reference for details on interfacing with the generated context.
