# Supported PD objects and abstractions

These are all the objects that hvcc is able to parse.

You can read more about limitations in the [getting started](../../getting-started/patching.md#known-limitations) guide.

Here is a list of [unsupported Pd objects](unsupported.md).

## Message Objects

| object | limitations |
| --- | --- |
| != | |
| % | |
| & | |
| && | |
| \| | |
| \|\| | |
| * | |
| + | |
| - | |
| / | |
| < | |
| << | |
| <= | |
| == | |
| > | |
| >= | |
| >> | |
| abs | |
| atan | |
| atan2 | |
| b | |
| bang | |
| bendin | only some generators <sup>1</sup> |
| bendout | only some generators <sup>1</sup> |
| bng | <sup>2</sup> |
| change | |
| clip | |
| cnv | |
| cos | |
| ctlin | only some generators <sup>1</sup> |
| ctlout | only some generators <sup>1</sup> |
| dbtopow | |
| dbtorms | |
| declare | |
| del | |
| delay | does not accept tempo messages or unit argument |
| div | |
| exp | |
| expr | except some functions. <sup>3</sup> Does not support symbol input. |
| else/knob | converted to `[f ]` <sup>2</sup> |
| f | |
| float | |
| floatatom | converted to `[f ]` <sup>2</sup> |
| ftom | |
| hradio | converted to `[f ]` <sup>2</sup> |
| hsl | converted to `[f ]` <sup>2</sup> |
| i | |
| inlet | |
| int | |
| line | |
| list | only accepts operation argument <sup>4</sup> |
| loadbang | |
| log | |
| makenote | |
| max | |
| metro | does not accept tempo messages or unit argument |
| min | |
| midiin | only some generators <sup>1</sup> |
| midiout | only some generators <sup>1</sup> |
| midirealtimein | only some generators <sup>1</sup> |
| mod | |
| moses | |
| mtof | |
| nbx | converted to `[f ]` <sup>2</sup> |
| notein | only some generators <sup>1</sup> |
| noteout | only some generators <sup>1</sup> |
| outlet | |
| pack | no symbol on first inlet |
| pgmin | only some generators <sup>1</sup> |
| pgmout | only some generators <sup>1</sup> |
| pd | |
| pipe | |
| poly | |
| polytouchin | only some generators <sup>1</sup> |
| polytouchout | only some generators <sup>1</sup> |
| pow | |
| powtodb | |
| print | |
| r | |
| random | |
| receive | |
| rmstodb | |
| route | right inlet not supported |
| s | |
| sel | |
| select | right inlet not supported |
| send | |
| sin | |
| spigot | |
| sqrt | |
| stripnote | |
| swap | |
| symbol | |
| symbolatom | |
| t | |
| table | |
| tabread | |
| tabwrite | |
| tan | |
| tgl | <sup>2</sup> |
| timer | does not accept tempo messages or unit argument |
| touchin | only some generators <sup>1</sup> |
| touchout | only some generators <sup>1</sup> |
| trigger | |
| unpack | no initialization e.g. `[unpack 0 0]` |
| until | |
| vradio | converted to `[f ]` <sup>2</sup> |
| vsl | converted to `[f ]` <sup>2</sup> |
| wrap | |

1. Midi i/o objects are currently only supported for [dpf](../../generators/dpf.md), [daisy](../../generators/daisy.md) and [owl](../../generators/owl.md)
2. Supports setting send/receive configuration, see [Getting Started](../../getting-started/patching.md#gui-objects)
3. Does not support: `size()`, `sum()`, `Sum()`, `avg()`, `Avg()`, `mtof()`, `ftom()`, `dbtorms()`, `rmstodb()`, `powtodb()`, `dbtopow()`, `symbol()`, `sym()`, `tolower()`, `toupper()`, `strcat()`, `strncat()`, `strlen()`, `strcspn()`, `strbrk()`, `strcmp()`, `strcasecmp()`, `strncmp()`,`strncasecmp()`, `var()`
4. Does not support tosymbol/fromsymbol.

## Signal Objects

| object | limitations |
| --- | --- |
| *~ | |
| +~ | |
| -~ | |
| /~ | |
| abs~ | |
| adc~ | |
| bang~ | |
| biquad~ | |
| block~ | Allowed to be used, but completely ignored. |
| bp~ | |
| catch~ | |
| clip~ | |
| complex-mod~ | |
| cos~ | |
| cpole~ | |
| czero_rev~ | arguments and control connections are ignored |
| czero~ | arguments and control connections are ignored |
| dac~ | |
| dbtopow~ | |
| dbtorms~ | |
| delread~ | |
| delread4~ | |
| delwrite~ | |
| env~ | |
| exp~ | |
| expr~ | except some functions.<sup>1</sup> Only supports signal inputs. Does not work with SIMD optimizations! |
| ftom~ | |
| hilbert~ | |
| hip~ | |
| inlet~ | |
| line~ | |
| lop~ | right inlet does not support signals |
| max~ | |
| min~ | |
| mtof~ | |
| noise~ | |
| osc~ | |
| outlet~ | |
| phasor~ | |
| powtodb~ | |
| pow~ | |
| q8_rsqrt~ | |
| q8_sqrt~ | |
| receive~ | |
| rmstodb~ | |
| rpole~ | |
| rsqrt~ | |
| rzero_rev~ | arguments and control connections are ignored |
| rzero~ | arguments and control connections are ignored |
| r~ | |
| samphold~ | |
| samplerate~ | |
| send~ | |
| sig~ | |
| snapshot~ | outputs on the next audiocycle. does not support `[set(` messages.  |
| sqrt~ | |
| s~ | |
| tabosc4~ | |
| tabplay~ | |
| tabread4~ | right inlet does not do anything |
| tabread~ | |
| tabwrite~ | |
| throw~ | |
| vcf~ | |
| vd~ | |
| wrap~ | |

1. Does not support: `size()`, `sum()`, `Sum()`, `avg()`, `Avg()`, `mtof()`, `ftom()`, `dbtorms()`, `rmstodb()`, `powtodb()`, `dbtopow()`

## Cyclone

Objects ported from [cyclone](https://github.com/porres/pd-cyclone) library.

| object | remarks |
| --- | --- |
| acosh~ | |
| acos~ | |
| asinh~ | |
| asin~ | |
| atan2~ | |
| atanh~ | |
| atan~ | |
| bitand~ | only supports mode 1 |
| bitor~ | only supports mode 1 |
| bitnot~ | only supports mode 1 |
| bitsafe~ | |
| bitxor~ | only supports mode 1 |
| cartopol~ | |
| cosh~ | |
| cosx~ | |
| equals~ | alias: ==~ |
| greaterthaneq~ | alias: >=~ |
| greaterthan~ | alias: >~ |
| lessthaneq~ | alias: <=~ |
| lessthan~ | alias: <~ |
| notequals~ | alias: !=~ |
| poltocar~ | |
| sinh~ | |
| sinx~ | |
| tanh~ | |
| tanx~ | |

## Other externals

Objects ported from other PD externals

| object | limitations |
| --- | --- |
| pdnam~ | only supports WaveNet models Nano, Feather, Lite, and Standard |

## Supported Abstractions

These are commonly used - or built in - abstractions that consist of compatible vanilla objects.

| object | limitations |
| --- | --- |
| else/above | |
| else/add | |
| else/avg | |
| else/car2pol | |
| else/sysrt.in | |
| else/sysrt.out | |
| else/trig2bang | |
| rev1~ | |
| rev2~ | |
| rev3~ | |

## `-p` Search Paths

`hvcc` will iterate through various directories when resolving patch objects and abstractions. The `-p` or `--search_paths` argument can be used to add additional folders for `hvcc` to look in.

This can be handy when using a third-party patch library such as [heavylib](https://github.com/Wasted-Audio/heavylib).

```bash
hvcc ~/myProject/_main.pd -o ~/Desktop/somewhere/else/ -n mySynth -p ~/Workspace/Projects/Enzien/heavylib/ ~/Desktop/myLib/
```
