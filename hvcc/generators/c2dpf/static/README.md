# Distrho Plugin Format

This output is for the Distrho Plugin Format ([DPF](https://github.com/DISTRHO/DPF)), and can be used to build LV2, VST2 and jack standalone versions of your Heavy code.

# Build Instructions

Make sure you have a (recent) DPF in the root of your output directory

`$ git clone https://github.com/DISTRHO/DPF.git <out_dir>/dpf`

Then compile the plugins from the source folder:

`$ cd <out_dir>/plugin/source/ && make`

This will result in an `<out_dir>/bin/` folder with all binary assets.

## LV2

After this you will likely have to create the `.ttl` files for the LV2 version. First make sure you have a functioning `lv2_ttl_generator`:

`$ cd <out_dir>/dpf/utils/lv2-ttl-generator && make`

Then run it on your LV2 build from the binary directory and move the files into the target dir:

`$ cd bin/ && ../dpf/utils/lv2_ttl_generator <plugin>.lv2/<plugin>_dsp.so && mv *ttl <plugin>.lv2/`

You can now add your `<plugin>.lv2/` forder to your local `~/.lv2/` directory.

## VST2

The VST2, `bin/<plugin>-vst.so`, can be placed directly into your `~/.vst/` dir and accessed by your DAW of choice.

## Jack

The Jack binary can be executed in place and used to test functionality `./bin/<plugin>`. Currently there is no UI, so this is not recommended. You will have to be running jack in order to use this.
