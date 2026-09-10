# NanoVG

The DPF wrapper is able to generate a custom UI using the [PDVG](https://github.com/Wasted-Audio/pdvg) framework that implements a set of [NanoVG](https://github.com/memononen/nanovg) widgets. This is the same graphics library used by [plugdata](https://github.com/plugdata-team/plugdata) and this UI generator tries to match plugdata rendering as close as possible.

See the [examples](https://github.com/Wasted-Audio/hvcc-examples-dpf) project for various implementations of NanoVG plugins.

## Settings

You can enable the NanoVG export by setting `"enable_ui": 2`. The size will be automatically updated based on the visible UI size of your main patch canvas.

```json
{
    "dpf": {
        "enable_ui": 2
    }
}
```

## Objects

Object position, size, labels, colors, and other object settings will be translated to the generated GUI. For proper subpatch support you currently need to use our [fork of DPF](https://github.com/Wasted-Audio/DPF).

### Parameters

You need to make sure that all parameters are associated with PD Graphical objects by using the object [receive config](../getting-started/patching.md#gui-objects). Set the complete configuration, with min/max/default/type, as you would normally on a receiver. Objects need to be visible in the main patch canvas, otherwise you will get errors. Send parameters, useful as read-only indicators, are currently not supported.

- Number box (nbx)
- Vertical slider (vsl)
- Horizontal slider (hsl)
- Vertical radio buttons (vradio)
- Horizontal radio buttons (hradio)
- Bang (bng)
- Toggle (tgl)
- Knob (knob, else/knob)
- Float atom (floatatom)

### Other objects

- Canvas (cnv)
- Comment (text)

## Theme

You can optionally set a theme and theme colors. When using the theme the compiler will override all object color settings to match plugdata default object colors. Multiple themes can be included in the config and in the future it will be possible to switch themes in the generated UI.

All theme options are optional and can set a specific global corner radius and various colors. Color names can be an RGB decimal tuple, hexadecimal RGB value or a human readable [color name](https://www.w3.org/TR/css-color-3/#svg-color).

```json
{
    "dpf": {
        "ui_theme_set": true,
        "ui_theme": "default",
        "ui_themes": {
            "default": {
                "obj_corner_radius": 2.75,
                "cnv_color": [100, 20, 50],
                "cnv_txt_color": "#ffffff",
                "io_color": "indianred",
                "bg_color": "cadetblue",
                "sel_color": "#123456",
                "com_txt_color": "#666666",
                "out_color": "black"
            }
        }
    }
}
```
