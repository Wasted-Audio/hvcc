# External Generators

It's possible to implement custom generators without modifying HVCC. For this, you need to:

* subclass `hvcc.types.compiler.Generator` abstract class in your module (e.g. a Python file)
* add `-G your_module_name` command-line argument when executing `hvcc`

It's recommended to have only one Generator subclass per module, otherwise any one of them can be executed.

Check out `hvcc.generators.c2daisy.c2daisy` or `hvcc.generators.c2dpf.c2dpf` modules for reference implementations.

## Example

This example demonstrates how to create a custom generator that prints a message into stdout.

This is `example_hvcc_generator.py`:

```python
import time

from typing import Dict, Optional

from hvcc.types.compiler import CompilerResp, ExternInfo, Generator
from hvcc.types.meta import Meta


class ExampleHvccGenerator(Generator):
    @classmethod
    def compile(
            cls,
            c_src_dir: str,
            out_dir: str,
            externs: ExternInfo,
            patch_name: Optional[str] = None,
            patch_meta: Meta = Meta(),
            num_input_channels: int = 0,
            num_output_channels: int = 0,
            copyright: Optional[str] = None,
            verbose: Optional[bool] = False
    ) -> CompilerResp:
        begin_time = time.time()
        print("--> Invoking ExampleHvccGenerator")
        time.sleep(1)
        end_time = time.time()

        # Please see code example on how CompilerResp class is used and adapt to your case.
        return CompilerResp(
            stage='example_hvcc_generator',  # module name
            compile_time=end_time - begin_time,
            in_dir=c_src_dir,
            out_dir=out_dir
        )
```

With this file in your current directory, execute the following command:

```bash
hvcc patch.pd -G example_hvcc_generator
```
