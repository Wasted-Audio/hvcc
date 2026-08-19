# Supported PD objects and abstractions

These are all the objects that hvcc is able to parse.

You can read more about limitations in the [getting started](../../getting-started/patching.md#known-limitations) guide.

Here is a list of [unsupported Pd objects](unsupported.md).

## Message Objects

| object | limitations |
| --- | --- |
| != | <sup>1</sup> |
| % | <sup>1</sup> |
| & | <sup>1</sup> |
| && | <sup>1</sup> |
| \| | <sup>1</sup> |
| \|\| | <sup>1</sup> |
| * | <sup>1</sup> |
| + | <sup>1</sup> |
| - | <sup>1</sup> |
| / | <sup>1</sup> |
| < | <sup>1</sup> |
| << | <sup>1</sup> |
| <= | <sup>1</sup> |
| == | <sup>1</sup> |
| > | <sup>1</sup> |
| >= | <sup>1</sup> |
| >> | <sup>1</sup> |
| abs | |
| atan | |
| atan2 | <sup>1</sup> |
| b | |
| bang | |
| bendin | only some generators <sup>2</sup> |
| bendout | only some generators <sup>2</sup> |
| bng | <sup>3</sup> |
| change | |
| clip | |
| cnv | |
| cos | |
| ctlin | only some generators <sup>2</sup> |
| ctlout | only some generators <sup>2</sup> |
| dbtopow | |
| dbtorms | |
| declare | |
| del | |
| delay | does not accept tempo messages or unit argument |
| div | |
| exp | |
| expr | except some functions. <sup>4</sup> Does not support symbol input. |
| f | |
| float | |
| floatatom | converted to `[f ]` <sup>3</sup> |
| ftom | |
| hradio | converted to `[f ]` <sup>3</sup> |
| hsl | converted to `[f ]` <sup>3</sup> |
| i | |
| inlet | |
| int | |
| line | |
| list | only accepts operation argument <sup>5</sup> |
| loadbang | |
| log | |
| makenote | |
| max | <sup>1</sup> |
| metro | does not accept tempo messages or unit argument |
| min | <sup>1</sup> |
| midiin | only some generators <sup>2</sup> |
| midiout | only some generators <sup>2</sup> |
| midirealtimein | only some generators <sup>2</sup> |
| mod | |
| moses | |
| mtof | |
| nbx | converted to `[f ]` <sup>3</sup> |
| notein | only some generators <sup>2</sup> |
| noteout | only some generators <sup>2</sup> |
| outlet | |
| pack | no symbol on first inlet |
| pgmin | only some generators <sup>2</sup> |
| pgmout | only some generators <sup>2</sup> |
| pd | |
| pipe | |
| poly | |
| polytouchin | only some generators <sup>2</sup> |
| polytouchout | only some generators <sup>2</sup> |
| pow | <sup>1</sup> |
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
| t | does not support `l/list` or `p/pointer` arguments |
| table | |
| tabread | |
| tabwrite | |
| tan | |
| tgl | <sup>3</sup> |
| timer | does not accept tempo messages or unit argument |
| touchin | only some generators <sup>2</sup> |
| touchout | only some generators <sup>2</sup> |
| trigger | does not support `l/list` or `p/pointer` arguments |
| unpack | no initialization e.g. `[unpack 0 0]` |
| until | |
| vradio | converted to `[f ]` <sup>3</sup> |
| vsl | converted to `[f ]` <sup>3</sup> |
| wrap | |

1. Does not support banging the left inlet. Use a `[f ]` to store the left value and bang that instead.
2. Midi i/o objects are currently only supported for [dpf](../../generators/dpf.md), [daisy](../../generators/daisy.md) and [owl](../../generators/owl.md)
3. Supports setting send/receive configuration, see [Getting Started](../../getting-started/patching.md#gui-objects)
4. Does not support: `size()`, `sum()`, `Sum()`, `avg()`, `Avg()`, `mtof()`, `ftom()`, `dbtorms()`, `rmstodb()`, `powtodb()`, `dbtopow()`, `symbol()`, `sym()`, `tolower()`, `toupper()`, `strcat()`, `strncat()`, `strlen()`, `strcspn()`, `strbrk()`, `strcmp()`, `strcasecmp()`, `strncmp()`,`strncasecmp()`, `var()`
5. Does not support tosymbol/fromsymbol.

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
| inlet~ | does not support connections to the control inlet or second (control) outlet |
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
| threshold~ | |
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
| else/knob | converted to `[f ]` <sup>1</sup> |
| else/popmenu | converted to `[f ]` <sup>1</sup> |
| pdnam~ | only supports WaveNet models Nano, Feather, Lite, and Standard |

1. Supports setting send/receive configuration, see [Getting Started](../../getting-started/patching.md#gui-objects)

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
