# Distrho Plugin Format

This output is for the Distrho Plugin Format ([DPF](https://github.com/DISTRHO/DPF)), and can be used to build LV2, VST2 and jack standalone versions of your Heavy code.

# Build Instructions

Make sure you have a (recent) DPF in the root of your output directory

```bash
$ cd <out_dir>
$ git clone https://github.com/DISTRHO/DPF.git dpf
```

Then compile the plugins from the source folder:

```bash
$ make
```

This will result in an `bin/` folder with all binary assets.

* LV2 - move `bin/<plugin>.lv2/` folder to your local `~/.lv2/` dir
* VST2 - move `bin/<plugin>-vst.so`, can be placed directly into your `~/.vst/` dir

## Metadata

You will likely want to add more configuration options to your project. Create a json file as described in the [documentation](https://wasted-audio.github.io/hvcc/docs/03.gen.dpf.html#metadata).

## Jack

The Jack binary can be executed in place and used to test functionality `./bin/<plugin>`. Currently there is no UI, so this is not recommended. You will have to be running jack in order to use this.
