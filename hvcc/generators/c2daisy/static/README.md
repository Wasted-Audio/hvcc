# Daisy

To build this code, navigate into the source folder and run `make`.

Flashing can be done over USB with `make program-dfu`. Make sure your Daisy is in DFU mode ([check this out if you're not sure how to do that](https://github.com/electro-smith/DaisyWiki/wiki/1.-Setting-Up-Your-Development-Environment#4-Run-the-Blink-Example)). If you have an ST-Link or other JTAG programmer, you can use `make program`.

If you've made hardware based on the Daisy Seed or Patch Submodule, you can supply custom json for the board description.