/*
 * Copyright (c) Wasted Audio 2023 - GPL-3.0-or-later
 */

#include "DistrhoUI.hpp"
#include "ResizeHandle.hpp"

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
            case {{loop.index-1}}:
                f{{v.display|lower}} = value;
                break;
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

        if (ImGui::Begin("{{name.replace('_', ' ')}}", nullptr, ImGuiWindowFlags_NoResize + ImGuiWindowFlags_NoCollapse))
        {
    {% for k, v in receivers %}
            if (ImGui::SliderFloat("{{v.display.replace('_', ' ')}}", &f{{v.display|lower}}, {{v.attributes.min}}f, {{v.attributes.max}}f))
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
            {% for i in range(0, receivers|length) -%}
                editParameter({{i}}, false);
            {% endfor %}
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
