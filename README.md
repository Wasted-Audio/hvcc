![Build Status](https://github.com/Wasted-Audio/hvcc/actions/workflows/python.yml/badge.svg)

:warning: This is an attempt to modernize `hvcc` to work with `python3` and add some additional targets. :warning:

:warning: Not all functionality is being tested. Feedback is appreciated. :warning:

# Heavy Compiler Collection (hvcc)

`hvcc` is a python-based dataflow audio programming language compiler that generates C/C++ code and a variety of specific framework wrappers.

## Background

The original need for `hvcc` arose from running against performance limitations while creating interactive music and sound products for the iPhone. [Pure Data](https://puredata.info) (libpd) was the only real choice for a design tool as it was embeddable and provided a high enough abstraction level that musicians or sound designers could be creative.

The goal was to leverage Pure Data as a design interface and statically interpret the resultant patches to generate a low-level, portable and optimised C/C++ program that would be structured to take advantage of modern hardware whilst still generating the same behaviour and audio output as Pure Data.

It has since then been expanded to provide further support for many different platforms and frameworks, targeting game audio design, daw plugins and embedded production tools.

## Requirements

* python 3.7 or higher
    - `jinja2` (for generator templating)
    - `nose2` (for tests, optional)

## Installation
hvcc is available from pypi.org and can be installed using python3 pip:

`$ pip3 install hvcc`

If you want to develop hvcc you can install it from the source directory:

`$ git clone https://github.com/dromer/hvcc.git`

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

Available generator options:

* `c`
* `bela`
* `fabric`
* `js`
* `pdext`
* `unity`
* `dpf`
  * `vst2`
  * `lv2`
  * `jack`
* `wwise`


### `-p` Search Paths

`hvcc` will iterate through various directories when resolving patch objects and abstractions. The `-p` or `--search_paths` argument can be used to add additional folders for `hvcc` to look in.

This can be handy when using a third-party patch library for example https://github.com/enzienaudio/heavylib.

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth -p "[~/Workspace/Projects/Enzien/heavylib/, ~/Desktop/myLib/]"`

### `--copyright` User Copyright

By default all the generated source files via `hvcc` will have the following copyright text applied to the top of the file:

`Copyright (c) 2018 Enzien Audio, Ltd.`

This can be changed with `--copyright` parameter

`$ hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth --copyright "Copyright (c) Los Pollos Hermanos 2019"`

### `--help`

Displays all the available parameters and options for hvcc.

## Documentation

* [Introduction](/docs/01.introduction.md)
  - [What is heavy?](/docs/01.introduction.md#what-is-heavy)
  - [Supported patch formats](/docs/01.introduction.md#supported-patch-formats)
  - [Supported platforms](/docs/01.introduction.md#supported-platforms)
  - [Supported frameworks](/docs/01.introduction.md#supported-frameworks)
  - [Licensing](/docs/01.introduction.md#licensing)
* [Getting Started](/docs/02.getting_started.md)
* [Unity](/docs/05.unity.md)
* [Wwise](/docs/06.wwise.md)
* [Javascript](/docs/07.javascript.md)
* [DPF](/docs/08.dpf.md)
* [MIDI](/docs/09.midi.md)
* [C API](/docs/10.c.md)
* [C++ API](/docs/11.cpp.md)
* [Heavy Lang Info](/docs/12.heavy_lang.md)
* [Heavy IR Info](/docs/13.heavy_ir_lang.md)

## Contact
There are several places where heavy/hvcc conversation is happening:
* [Discord](https://discord.gg/fmxJveg)
* [IRC](irc://irc.libera.chat/#dataflow)
* A number of forums:
  * [Bela](https://forum.bela.io/?q=hvcc)
  * [Rebel Technology](https://community.rebeltech.org/tags/puredata)
  * [Daisy](https://forum.electro-smith.com/t/pure-data/110)

Or you can use the [discussions](https://github.com/Wasted-Audio/hvcc/discussions) tab of this repository
