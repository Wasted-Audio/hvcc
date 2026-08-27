# Introduction

## What is Heavy?

Heavy is a framework for easily generating audio plugins for use in interactive sound and music applications such games, instruments or installations.

It aims to reduce the dependency on low-level programming from a creative standpoint and bridge the gap from idea to production-ready implementation.

Heavy makes use of modern software principles to generate highly optimised C/C++ code specifically targeting a wide variety of popular hardware architectures and software frameworks. It can also automatically build plugin binaries for these platforms.

## Supported Patch Formats

Currently Heavy supports compiling Pure Data (.pd) patch files.

However it's important to note that Pd is merely used as a front-end authoring editor, Heavy does not make use of any Pure Data code, and it is entirely unrelated to the embeddable Pd engine, [libpd](https://github.com/libpd/libpd).

## What is Pure Data?

[Pure Data](http://msp.ucsd.edu/software.html) (Pd) is an open source visual programming environment for real-time time audio and music creation.

Heavy can interpret and convert a subset of features from Pure Data patches:

- [Supported Pd objects](../reference/objects/supported.md)
- [Unsupported Pd objects](../reference/objects/unsupported.md)

## Supported Platforms

- Windows 10, 11 and WSA
- Mac OSX
- Linux
- PS4
- Xbox One
- iOS
- Android
- [Bela](http://bela.io)
- [Hoxton OWL](https://www.rebeltech.org/product/owl-modular/)
- [Daisy](https://www.electro-smith.com/daisy)
- Raspberry Pi
- Web (Javascript)

## Supported Frameworks

- [Unity 5](https://unity3d.com)
- [Distrho Plugin Framework](https://distrho.github.io/DPF)
  - [LV2](https://lv2plug.in)
  - [VST2](https://www.steinberg.net/technology/)
  - [VST3](https://www.steinberg.net/technology/)
  - [CLAP](https://cleveraudio.org/)
  - [JACK](https://jackaudio.org)
- [Wwise](https://www.audiokinetic.com)
- [FMOD](https://www.fmod.com)
- [Web Audio API (AudioWorkletProcessor)](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorkletProcessor)

## Optimisations

Heavy-generated code comes pre-optimised for architectures that can take advantage of AVX, SSE or NEON instructions. For more bespoke platforms, Heavy also provides a basic implementation supporting single sample block sizes.

## Licensing

In general `hvcc` is free to use, though please be aware of the following licences applied to particular parts of the system.

All the `hvcc` python compiler code is [GPLv3](https://github.com/Wasted-Audio/hvcc/blob/master/LICENSE).

The files that `hvcc` generates are split into two types:

- [Static](https://github.com/Wasted-Audio/hvcc/tree/main/hvcc/generators/ir2c/static): this code is independent of the input patch contents and provides the basic DSP functionality with which generated output can link against. It has a liberal [ISC](https://github.com/Wasted-Audio/hvcc/blob/main/hvcc/generators/ir2c/static/HeavyContext.hpp#L2) licence.

- Generated: this relates to all the source files that use information about the input patch, for example `Heavy_{{name}}.cpp`. By default all these files will have a `Copyright (c) 2018 Enzien Audio, Ltd` header, but this can be modified with the [user copyright argument](../index.md#-copyright-user-copyright).

### Generators

Some generators use other libraries and SDKs with different licensing:

- [Daisy](../generators/daisy.md) - requires [libDaisy](https://github.com/electro-smith/libDaisy) and our internal [json2daisy](https://github.com/Wasted-Audio/hvcc/tree/develop/hvcc/generators/c2daisy/json2daisy/) library, both using `MIT` license.
- [DPF](../generators/dpf.md) - requires the [DPF](https://github.com/DISTRHO/DPF) library and optionally the [DPF-Widgets](https://github.com/DISTRHO/DPF-Widgets) or [PDVG](https://github.com/wasted-Audio/PDVG) GUI libraries. These are all `ISC` licensed.
- [FMOD](../generators/fmod.md) - no SDK required for building, but requires a [license](https://www.fmod.com/licensing) for distribution.
- [Javascript](../generators/javascript.md) - requires [emscripten](https://github.com/emscripten-core/emscripten) which is dual licensed `MIT` and `University of Illinois/NCSA Open Source License`.
- [OWL](../generators/owl.md) - requires [OwlProgram](https://github.com/RebelTechnology/OwlProgram/) which uses `GPLv2`.
- [PD External](../generators/pdext.md) - requires `pd.dll` for linking on Windows, which comes from Puredata and is `BSD3` license.
- [Unity](../generators/unity.md) - no SDK required for building, but requires a Unity [license](https://unity.com/products) to use.
- [Wwise](../generators/wwise.md) - requires the [Wwise SDK](https://www.audiokinetic.com/en/public-library/2025.1.9_9197/) and a proprietary [license](https://www.audiokinetic.com/en/wwise/pricing/).

## How to start patching for heavy

See the [Getting started](patching.md) page on more information about how to construct compatible pure data patches.
