# MetaModule

Heavy can automatically convert your patches for the [4ms MetaModule](https://metamodule.info/).

Since you can only provide a single input patch to HVCC it is currently limited to create only a single module as part of the generated plugin.

The generator can be activated using `-g meta`.

## Inputs and Outputs

[Exposed receive objects](../getting-started/patching.md#exposing-parameters) will automatically become a parameter for the module. You can also set a range.

It is currently not possible to set a specific type, so all parameters are floats.

Send objects will become LEDs on the panel. These can also have a range, but will be normalized so they are always 0-1 for their brightness.

All audio inputs and outputs will become jack sockets. Values are normalized from `-10 - 10` to `-1 - 1` and back to match typical PD audio operations with the MetaModule CV standard. You will need to do additional scaling in your patch if you want to use the raw CV values internally (e.g. for Pitch calculations).

## Metadata

In order to set custom information you should supply a `metadata.json` using `-m`. We will use the `meta` subsection:

```json
{
    "name": "testplugin",
    "meta": {
        "slug": "plugin-slug",
        "name": "Plugin Name",
        "version": "1.0.0",
        "license": "GPL-3.0-only",
        "brand": "Heavy",
        "author": "Heavy User",
        "description": "Description of the plugin",
        "modules": [
            {
                "slug": "module-slug",
                "name": "Module Name",
                "description": "Description of the module",
                "tags": ["VCO"],
                "assets": null
            }
        ]
    }
}
```

You can optionally supply a list of assets that make the panel, controls and sockets of your module. If you don't add the `assets` section a panel will be generated automatically. Make sure that your description here is exact and complete. You have to use the same names for all receivers and senders and use the correct amount of input and output IDs. Do note that audio i/o starts counting from 0, where PD counts from 1.

```json
    {
        "panel": {
            "image": "path/to/panel_image.png",
            "size": {
                "x": 75,
                "y": 240
            }
        },
        "knobs": [
            {
                "param": "<receiver_name>",
                "coords": {
                    "x": 20,
                    "y": 20
                },
                "image": "path/to/knob_image.png"
            }
        ],
        "inputs": [
            {
                "id": 0,
                "coords": {
                    "x": 18,
                    "y": 60
                },
                "image": "path/to/socket_image.png"
            }
        ],
        "outputs": [
            {
                "id": 0,
                "coords": {
                    "x": 18,
                    "y": 100
                },
                "image": "path/to/socket_image.png"
            }
        ],
        "leds": [
            {
                "led": "<sender_name>",
                "coords": {
                    "x": 25,
                    "y": 40
                },
                "image": "path/to/led_image.png"
            }
        ]
    }
```
