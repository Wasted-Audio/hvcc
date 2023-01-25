/*
 * ImGui plugin example
 * Copyright (C) 2021 Jean Pierre Cimalando <jp-dev@inbox.ru>
 * Copyright (C) 2021-2022 Filipe Coelho <falktx@falktx.com>
 * SPDX-License-Identifier: ISC
 */

#include "DistrhoUI.hpp"
#include "ResizeHandle.hpp"
// #include "PluginFont.cpp"

START_NAMESPACE_DISTRHO

// --------------------------------------------------------------------------------------------------------------------

class ImGuiPluginUI : public UI
{
    {% for k, v in receivers -%}
        float f{{v.display|lower}} = {{v.attributes.default}}f;
    {% endfor %}
    ResizeHandle fResizeHandle;

    // ----------------------------------------------------------------------------------------------------------------

public:
   /**
      UI class constructor.
      The UI should be initialized to a default state that matches the plugin side.
    */
    ImGuiPluginUI()
        : UI(DISTRHO_UI_DEFAULT_WIDTH, DISTRHO_UI_DEFAULT_HEIGHT),
          fResizeHandle(this)
    {
        setGeometryConstraints(DISTRHO_UI_DEFAULT_WIDTH, DISTRHO_UI_DEFAULT_HEIGHT, true);

        // hide handle if UI is resizable
        if (isResizable())
            fResizeHandle.hide();
    }

protected:
    // ----------------------------------------------------------------------------------------------------------------
    // DSP/Plugin Callbacks

   /**
      A parameter has changed on the plugin side.@n
      This is called by the host to inform the UI about parameter changes.
    */
    void parameterChanged(uint32_t index, float value) override
    {
    {%- if receivers|length > 0 %}
        switch (index) {
            {% for k, v  in receivers -%}
            case {{loop.index-1}}: {
                f{{v.display|lower}} = value;
                break;
            }
            {% endfor %}
            default: return;
        }
    {% else %}
        // nothing to do
    {%- endif %}
        repaint();
    }

    // ----------------------------------------------------------------------------------------------------------------
    // Widget Callbacks

   /**
      ImGui specific onDisplay function.
    */
    void onImGuiDisplay() override  
    {
        const float width = getWidth();
        const float height = getHeight();
        const float margin = 20.0f * getScaleFactor();

        ImGui::SetNextWindowPos(ImVec2(margin, margin));
        ImGui::SetNextWindowSize(ImVec2(width - 2 * margin, height - 2 * margin));

        if (ImGui::Begin("{{name}}", nullptr, ImGuiWindowFlags_NoResize + ImGuiWindowFlags_NoCollapse))
        {

            // if (ImGui::SliderFloat("Gain (dB)", &fGain, -90.0f, 30.0f))
            // if (ImGuiKnobs::Knob("Gain (dB)", &fGain, -90.0f, 30.0f, 1.0f, "%.1fdB", ImGuiKnobVariant_Tick))
            // if (ImGuiKnobs::Knob("Gain (dB)", &fGain, -90.0f, 30.0f, 1.0f, "%.1fdB", ImGuiKnobVariant_SteppedTick, 0, ImGuiKnobFlags_ValueTooltip + ImGuiKnobFlags_DoubleClickReset + ImGuiKnobFlags_Logarithmic, 13))
            // if (ImGuiKnobs::Knob("Gain (Hz)", &fGain, 322.0f, 5551.5f, 100.0f, "%.1fHz", ImGuiKnobVariant_SteppedTick, 0, ImGuiKnobFlags_ValueTooltip + ImGuiKnobFlags_DoubleClickReset + ImGuiKnobFlags_Logarithmic, 13))
            // if (ImGui::SliderFloat("Mid Freq (Hz)", &fGain, 322.0f, 5551.0f, "%.1fHz", ImGuiSliderFlags_Logarithmic))
            

    {% for k, v in receivers -%}
        {%- if v.attributes.type == 'db': %}
            if (ImGuiKnobs::Knob("{{v.display.replace('_', ' ')}}", &f{{v.display|lower}}, {{v.attributes.min}}f, {{v.attributes.max}}, 0.2f, "%.1fdB", ImGuiKnobVariant_SteppedTick, 100, ImGuiKnobFlags_DoubleClickReset + ImGuiKnobFlags_ValueTooltip + ImGuiKnobFlags_NoInput + ImGuiKnobFlags_dB, 5))
        {%- elif v.attributes.type == 'log_hz': %}
            auto ImGuiKnob_Flags = ImGuiKnobFlags_ValueTooltip + ImGuiKnobFlags_DoubleClickReset + ImGuiKnobFlags_Logarithmic + ImGuiKnobFlags_NoInput;
            if (ImGuiKnobs::Knob("{{v.display.replace('_', ' ')}}", &f{{v.display|lower}}, {{v.attributes.min}}f, {{v.attributes.max}}f, 50.0f, "%.1fHz", ImGuiKnobVariant_SteppedTick, 100, ImGuiKnob_Flags, 7))
        {%- endif %}
            {
                if (ImGui::IsItemActivated())
                {
                    editParameter({{loop.index-1}}, true);
                    if (ImGui::IsMouseDoubleClicked(0))
                        f{{v.display|lower}} = {{v.attributes.default}}f;

                    setParameterValue({{loop.index-1}}, f{{v.display|lower}});
                }
            }
    {% endfor %}
            if (ImGui::IsItemDeactivated())
            {
                editParameter(0, false);
            }
        }
        ImGui::End();
    }

    DISTRHO_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(ImGuiPluginUI)
};

// --------------------------------------------------------------------------------------------------------------------

UI* createUI()
{
    return new ImGuiPluginUI();
}

// --------------------------------------------------------------------------------------------------------------------

END_NAMESPACE_DISTRHO
