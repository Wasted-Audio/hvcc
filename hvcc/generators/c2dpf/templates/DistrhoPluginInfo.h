{{copyright}}

#pragma once

#define DISTRHO_PLUGIN_NAME                 "{{name}}"
{%- if meta.plugin_uri is defined %}
#define DISTRHO_PLUGIN_URI                  "{{meta.plugin_uri}}"
#define DISTRHO_PLUGIN_CLAP_ID              "{{meta.plugin_uri}}"
{% else %}
#define DISTRHO_PLUGIN_URI                  "http://wasted.audio/lv2/plugin/{{name}}"
#define DISTRHO_PLUGIN_CLAP_ID              "http://wasted.audio/lv2/plugin/{{name}}"
{%- endif %}
#define DISTRHO_PLUGIN_NUM_INPUTS           {{num_input_channels}}
#define DISTRHO_PLUGIN_NUM_OUTPUTS          {{num_output_channels}}
#define DISTRHO_PLUGIN_IS_SYNTH             {{1 if num_output_channels > 0 and meta.midi_input else 0}}
#define DISTRHO_PLUGIN_HAS_UI               {{1 if meta.enable_ui else 0}}
#define DISTRHO_PLUGIN_IS_RT_SAFE           1
#define DISTRHO_PLUGIN_WANT_PROGRAMS        0
#define DISTRHO_PLUGIN_WANT_STATE           0
#define DISTRHO_PLUGIN_WANT_TIMEPOS         1
#define DISTRHO_PLUGIN_WANT_FULL_STATE      0
#define DISTRHO_PLUGIN_WANT_MIDI_INPUT      {{meta.midi_input if meta.midi_input is defined else 1}}
#define DISTRHO_PLUGIN_WANT_MIDI_OUTPUT     {{meta.midi_output if meta.midi_output is defined else 1}}
{%- if meta.lv2_info is defined %}
#define DISTRHO_PLUGIN_LV2_CATEGORY         "{{meta.lv2_info}}"
{%- endif %}
{%- if meta.vst3_info is defined %}
#define DISTRHO_PLUGIN_VST3_CATEGORIES      "{{meta.vst3_info}}"
{%- endif %}
{%- if meta.clap_info is defined %}
#define DISTRHO_PLUGIN_CLAP_FEATURES        "{{ meta.clap_info|join('", "') }}"
{%- endif %}

// for level monitoring
#define DISTRHO_PLUGIN_WANT_DIRECT_ACCESS   0

{%- if meta.enable_ui is defined %}
// if you are using a UI you'll probably want to modify these settings to your needs
#define DISTRHO_UI_USE_CUSTOM               1
#define DISTRHO_UI_CUSTOM_INCLUDE_PATH      "DearImGui.hpp"
#define DISTRHO_UI_CUSTOM_WIDGET_TYPE       DGL_NAMESPACE::ImGuiTopLevelWidget
#define DISTRHO_UI_DEFAULT_WIDTH            400
#define DISTRHO_UI_DEFAULT_HEIGHT           600
{%- endif %}