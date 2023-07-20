# Heavy Compiler Collection (hvcc)

[![Build Status](https://github.com/Wasted-Audio/hvcc/actions/workflows/build.yml/badge.svg)](https://github.com/Wasted-Audio/hvcc/actions)

`hvcc` is a python-based dataflow audio programming language compiler that generates C/C++ code and a variety of specific framework wrappers.

## Background

Originaly created by Enzien Audio, the need for `hvcc` arose from running against performance limitations while creating interactive music and sound products for the iPhone. [Pure Data](https://puredata.info) (libpd) was the only real choice for a design tool as it was embeddable and provided a high enough abstraction level that musicians or sound designers could be creative.

The goal was to leverage Pure Data as a design interface and statically interpret the resultant patches to generate a low-level, portable and optimised C/C++ program that would be structured to take advantage of modern hardware whilst still generating the same behaviour and audio output as Pure Data.

It has since then been expanded to provide further support for many different platforms and frameworks, targeting game audio design, daw plugins and embedded production tools. In 2021 Wasted Audio took over maintenance of the project.

## Requirements

* python 3.7 or higher
  * `jinja2` (for generator templating)
  * `importlib_resources` (for reading static resources)
  * `json2daisy` (for daisy integration)
  * `tox` (for tests, optional)
  * `numpy/scipy` (for tests, optional)
  * `midifile` (for tests, optional)
  * `clang/clang++` (for building tests, optional)

## Installation

hvcc is available from pypi.org and can be installed using python3 pip:

`$ pip3 install hvcc`

If you want to develop hvcc you can install it from the source directory:

`$ git clone https://github.com/Wasted-Audio/hvcc.git`

`$ cd hvcc/`

`$ pip3 install -e .`

## Usage

`hvcc` requires at least one argument that determines the top-level patch file to be loaded.

Generate a C/C++ program from `input.pd` and place the files in `~/myProject/`

`$ hvcc ~/myProject/_main.pd`

This command will generate the following directories:

* `~/myProject/hv` heavylang representation of the input pd patch(es)
* `~/myProject/ir` heavyir representation of the heavylang patch
* `~/myProject/c` final generated C/C++ source files (this is what you would use in your project)

### `-o` Select output directory

As seen in the above command, typical output of `hvcc` is split into several directories that contain the intermediate files used by the compiler itself, the final generated source files, and any additional framework specific files and projects.

The `-o` or `--out_dir` parameter will specify where the output files are placed after a successful compile.

For example:

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/`

Will place all the generated files in `~/Desktop/somewhere/else/`.

### `-n` Specify Patch Name

The `-n` or `--name` parameter can be used to easily namespace the generated code so that there are no conflicts when integrating multiple patches into the same project.

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth`

### `-g` Generators

Once `hvcc` has generated internal information about the patch the `-g` or `--gen` parameter can be used to specify the output files it should generate. By default it will always include `c` for the C/C++ source files and additional generators can specified for certain framework targets.

For example:

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth -g unity`

Will also generate a `unity` section in the output directory contain all the build projects and source files to compile a Unity plugin.

It is also possible to pass a list of generators:

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth -g unity wwise js`

A list of available generator options can be found [here](/docs/03.generators.md)

### `-p` Search Paths

`hvcc` will iterate through various directories when resolving patch objects and abstractions. The `-p` or `--search_paths` argument can be used to add additional folders for `hvcc` to look in. Note that this argument is not needed for abstractions in the same folder as the top-level patch.

This can be handy when using a third-party patch library like [heavylib](https://github.com/Wasted-Audio/heavylib) for example.

Simply append any folder paths after the `-p` flag like so:

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth -p ~/Workspace/Projects/Enzien/heavylib/ ~/Desktop/myLib/`

### `-m` Meta Data

`hvcc` can take extra meta-data via a supplied json file. It depends on the generator which fields are supported.

### `--copyright` User Copyright

By default all the generated source files via `hvcc` will have the following copyright text applied to the top of the file:

`Copyright (c) 2018 Enzien Audio, Ltd.`

This can be changed with `--copyright` parameter

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth --copyright "Copyright (c) Los Pollos Hermanos 2019"`

### `--help`

Displays all the available parameters and options for hvcc.

## Documentation

* [Introduction](/docs/01.introduction.md)
  * [What is heavy?](/docs/01.introduction.md#what-is-heavy)
  * [Supported patch formats](/docs/01.introduction.md#supported-patch-formats)
  * [Supported platforms](/docs/01.introduction.md#supported-platforms)
  * [Supported frameworks](/docs/01.introduction.md#supported-frameworks)
  * [Licensing](/docs/01.introduction.md#licensing)
* [Getting Started](/docs/02.getting_started.md)
* [Generators](/docs/03.generators.md)
* [MIDI](/docs/04.midi.md)
* [C API](/docs/05.c.md)
* [C++ API](/docs/06.cpp.md)
* [Heavy Lang Info](/docs/07.heavy_lang.md)
* [Heavy IR Info](/docs/08.heavy_ir_lang.md)
* [Supported vanilla objects](/docs/09.supported_vanilla_objects.md)
* [Unsupported vanilla objects](/docs/10.unsupported_vanilla_objects.md)

## Contact

There are several places where heavy/hvcc conversation is happening:

* [Discord](https://discord.gg/fmxJveg)
* [IRC](https://web.libera.chat/#hvcc)
* A number of forums:
  * [Bela](https://forum.bela.io/?q=hvcc)
  * [Rebel Technology](https://community.rebeltech.org/tags/puredata)
  * [Daisy](https://forum.electro-smith.com/c/integrations/pure-data/32)
  * [MOD](https://forum.moddevices.com/c/developers/pure-data/56)

Or you can use the [discussions](https://github.com/Wasted-Audio/hvcc/discussions) tab of this repository
