CHANGELOG
=====

Next Release
-----

Features:

* Only disable DSP with new `--nodsp` flag
* Use pydantic types to define metadata objects
* DPF: CV flag in portgroups
* DPF: flag to disable scoped denormals

Bugfixes

* wwise: allow Bang messages in OnSendMessageCallback()
* Improve `[cos~]` precision.

0.12.0
-----

* Core: parse remote/send messages
* Core: MIDI i/o added to memoryPool
* Core: support `[else/knob]` as `[float]`
* Daisy: set heavy context after hw.init()
* OWL: add Polytouchin and Polytouchout
* JS: webmidi input
* Docs: add instructions for loading custom samples in JS
* Small Bugfixes:
  * MIDI out objects in output Paremeters
  * JS: AudioWorklet fillTableWithFloatBuffer

0.11.0
-----

* Core: add attributes and send type to send params
* DPF: add "read only" outputParameter type based on send params
* JS: add output Parameter and output Event to generator and html template
* Daisy: update `wstd2daisy` and allow for setting `displayprocess` code into the template
* Testing: move `tinywav` to git submodule
* JS Bugfix: printHook and sendHook for AudioWorklet; mention emsdk limitations in docs
* Object Bugfix: `[stripnote]` missing right inlet
* Small Bugfixes:
  * set default name argument
  * `emcc` call on Windows - thanks to @vulcu
  * deallocation in test_signal - thanks to @eu-ch
  * quotes around WWISE paths - thanks to @eu-ch

0.10.0
-----

* Objects: `[bang~]`
* Object improvements: support `[clear(` message for `[delwrite~]`
* Documentation fixes/additions
* Daisy: ability to set samplerate and blocksize
* Daisy: adding midirealtimein, polytouchin/out, midiin (midiout WIP)
* Daisy: use `libdaisy_path` in meta config; both string/path and int/depth possible
* DPF: enum for UI parameter IDs
* DPF bugfixes: correct input PortGroup names; correct UI slider updates; midiout reimplementation
* Wwise: complete rewrite/refactor - now uses SDK build tools - thanks to @eu-ch !!
* Bugfix: correct alignment in AVX pow~ implementation
* Cleanup: remove deprecated build.json
* Deprecate py37, enable py312

0.9.0
-----

* Daisy: set bootloader type in Makefile
* Daisy: MIDI i/o for NoteOn/Off, ControlChange, ProgramChange, ChannelPressure, and PitchBend
* Daisy: USB MIDI toggle (disabled by debug printing)
* Daisy: allow for debug printing (off by default, increases program size due to formatting)
* DPF bugfixes: broken midi template include; MIDI_RT_CLOCK fails under certain conditions
* Pdext bugfixes: Windows library linking

0.8.0
-----

* DPF: enumerated parameters
* DPF: special `__hv_dpf_bpm` receiver of transport BPM value
* Pdext: migrate to `pd-lib-builder` and newer `m_pd.h` and add some initial documentation.
* deprecated: Fabric generator - no longer supported
* docs: updates on missing objects and limitations
* bugfix: issues #24, #50, #100, #106

0.7.0
-----

* improvements: add type annotations to all methods; run mypy over the whole library
* DPF: basic UI generation using dpf-widgets (imgui + modgui)
* DPF: basic port groups support
* abstractions: use duplicate of delread4~.pd for vd~.pd
* deprecated: internal Bela implementation (use downstream instead)
* docs: add notes
* docs: fix markdown syntax
* bugfixes: issues #86, #87 and #93

0.6.3
-----

* add polytouchin and polytouchout
* add tests for midi input objects
* bugfixes for midi objects bendin, ctlin, notein, pgmin, pgmout, touchin

0.6.2
-----

* dpf: add CLAP to docs; cleanup templates
* dpf: bugfix -> wrong frame count used for sendMessageToReceiverV()
* general: style fixes
* general: py311 support
* general: un/supported objects

0.6.1
-----

* bugfix: missing parameter in named arguments
* update: json2daisy

0.6.0
-----

* aligned memory and freed patch instance
* js: WASM AudioWorklet
* js: deprecate asm.js
* dpf: configurable subpath
* midi: add stripnote
* deprecate max2hv
* documentation updates
* code cleanup
* tests: refactor and deprecate test_uploader

0.5.0
-----

* c2owl generator
* migrate @owl to @raw
* c2daisy json2daisy integration
* enable control and signal tests
* push f-string usage

0.4.0
-----

* Midi realtime messages
* Host transport to midi-rt
* Midi message scheduling improvements
* Bugfix: minimum midi channel
* Bugfix: windows console_script

0.3.0
-----

* Midi I/O extensions for DPF
* Midi bugfixes for [notein], [pgmin], [touchin], [bendin], [midiin]
* Midi bugfixes for [noteout], [pgmout], [touchout], [bendout], [midiout]
* Midi docs update
* DPF minimal Midi examples

0.2.0
-----

* metadata json for generator config
* add trig attribute type
* Daisy platform support
* DPF cleanup + meta + trig
* documentation update
* DPF makefiles + meaningful values + docs

0.1.2
-----

* bump versions for pypi

0.1.0
-----

* python3 package
* pep8 checks
* update docs
* bundle utils into executable package
* add bool attribute type
* improve pd search paths

0.0.1
-----

* python3 fixes
* replace VST2 with DPF builds

0.0.0
-----

* code dump by enzienaudio
