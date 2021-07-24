#pragma once

#define DISTRHO_PLUGIN_BRAND           "Wasted Audio"
#define DISTRHO_PLUGIN_NAME            "{{name}}"
#define DISTRHO_PLUGIN_URI             "http://wasted.audio/lv2/plugin/{{name}}"
#define DISTRHO_PLUGIN_HOMEPAGE        "https://github.com/wasted.audio/{{name}}"
#define DISTRHO_PLUGIN_UNIQUE_ID       'p','l','u','g'
#define DISTRHO_PLUGIN_VERSION         0,0,0
#define DISTRHO_PLUGIN_LABEL           "my plugin"
#define DISTRHO_PLUGIN_LICENSE         "http://spdx.org/licenses/BSL-1.0"
#define DISTRHO_PLUGIN_MAKER           "Wasted Audio"
#define DISTRHO_PLUGIN_DESCRIPTION     "a plugin that does stuff"
#define DISTRHO_PLUGIN_NUM_INPUTS      {{num_input_channels}}
#define DISTRHO_PLUGIN_NUM_OUTPUTS     {{num_output_channels}}
#define DISTRHO_PLUGIN_IS_SYNTH        {{1 if num_input_channels == 0 and num_output_channels > 0 else 1}}
#define DISTRHO_PLUGIN_HAS_UI          0
#define DISTRHO_PLUGIN_HAS_EMBED_UI    0
#define DISTRHO_PLUGIN_HAS_EXTERNAL_UI 0
#define DISTRHO_PLUGIN_IS_RT_SAFE      1
#define DISTRHO_PLUGIN_WANT_PROGRAMS   0
#define DISTRHO_PLUGIN_WANT_STATE      0
#define DISTRHO_PLUGIN_WANT_FULL_STATE 0
#define DISTRHO_PLUGIN_NUM_PROGRAMS    0
#define DISTRHO_PLUGIN_WANT_MIDI_INPUT 1

// for level monitoring
#define DISTRHO_PLUGIN_WANT_DIRECT_ACCESS 1
