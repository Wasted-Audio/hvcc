# Distrho Plugin Format Generator example help

DPF generator supports extra configuration via a supplied meta-data file. Each of these are optional and have either a default value or are entirely optional (description and homepage). Midi i/o ports are on by default, but can be set to `0` and they will be disabled.

```json
{
    "dpf": {
        "description": "super simple test patch",
        "maker": "nobody",
        "homepage": "https://wasted.audio/plugin/test",
        "plugin_uri": "lv2://wasted.audio/lv2/testplugin",
        "version": "6, 6, 6",
        "license": "WTFPL",
        "midi_input": 0,
        "midi_output": 1,
        "plugin_formats": [
            "lv2_dsp",
            "vst"
        ]
    }
}
```
