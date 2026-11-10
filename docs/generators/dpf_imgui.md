# ImGui

The DPF wrapper is able to generate a generic plugin UI using the [Dear ImGui](https://github.com/ocornut/imgui) framework that is included in the [DPF-Widgets](https://github.com/DISTRHO/DPF-Widgets) collection.

See the [examples](https://github.com/Wasted-Audio/hvcc-examples-dpf) project for various implementations of ImGui plugins.

## Settings

You can enable the ImGui export by setting `"enable_ui": 1` and optionally giving a `ui_size` in the metadata json.

```json
{
    "dpf": {
        "enable_ui": 1,
        "ui_size": {
            "width": 400,
            "height": 300
        }
    }
}
```

## Parameters

Exposed parameters will be converted to appropriate controls based on their type. More custom controls will require manually editing the generated C++ source. Send parameters will show up as read-only indicators.

| type           | UI          |
| ----           | --          |
| float          | SliderFloat |
| int            | SliderInt   |
| bool           | Toggle      |
| int+enumerator | Combobox    |
| @hv_event      | Button      |

## Enumerator

In order to get a proper list of options in your Combobox you need to add an enumerator dictionary to your metadata json. The key needs to exactly match your receiver name. Selecting an item will send its 0-based integer index to the patch.

```json
{
    "dpf": {
        "enumerators": {
            "Room_Size": [
                "Small",
                "Medium",
                "Large"
            ]
        }
    }
}
```
