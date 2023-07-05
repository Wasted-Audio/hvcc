{{copyright}}

#include "DistrhoUI.hpp"
#include "ResizeHandle.hpp"

START_NAMESPACE_DISTRHO

// --------------------------------------------------------------------------------------------------------------------

{%- if meta.enumerators is defined %}
struct EnumParam
{
    const char* label;
    float value;
};
{%- endif %}


class ImGuiPluginUI : public UI
{
    {% for k, v in receivers -%}
        {%- if v.attributes.type == 'bool': %}
        bool f{{v.display|lower}} = {{v.attributes.default}}f != 0.0f;
        {%- else %}
        float f{{v.display|lower}} = {{v.attributes.default}}f;
        {%- endif %}
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
                {%- if v.attributes.type == 'bool': %}
                f{{v.display|lower}} = value != 0.0f;
                {%- else %}
                f{{v.display|lower}} = value;
                {%- endif %}
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
    {%- for k, v in receivers %}
        {%- set v_display = v.display|lower %}
        {%- if meta.enumerators is defined and meta.enumerators[v.display] is defined -%}
            {%- set enums = meta.enumerators[v.display] -%}
            {%- set enumlen = enums|length %}
            {%- set enum_list = v_display + "_list" %}

            EnumParam {{enum_list}}[] = {
                {%- for i in enums %}
                { "{{i}}", {{enums[i]}}f },
                {%- endfor %}
            };

            {%- for i in enums %}
               {%- if enums[i] == v.attributes.default %}
            int default_item = {{loop.index-1}};
               {%- endif %}
            {%- endfor %}
            static const char* current_item = {{enum_list}}[default_item].label;

            if (ImGui::BeginCombo("{{v.display.replace('_', ' ')}}", current_item))
            {
                for (int n = 0; n < {{enumlen}}; n++)
                {
                    bool is_selected = (current_item == {{enum_list}}[n].label);
                    if (ImGui::Selectable({{enum_list}}[n].label, is_selected))
                    {
                        current_item = {{enum_list}}[n].label;
                        f{{v_display}} = {{enum_list}}[n].value;
                        editParameter({{loop.index-1}}, true);
                        setParameterValue({{loop.index-1}}, f{{v_display}});
                    }
                    if (is_selected)
                        ImGui::SetItemDefaultFocus();
                }
                ImGui::EndCombo();
            }
        {%- else %}
            {%- if v.attributes.type == 'bool': %}
            if (ImGui::Toggle("{{v.display.replace('_', ' ')}}", &f{{v_display}}))
            {%- else %}
            if (ImGui::SliderFloat("{{v.display.replace('_', ' ')}}", &f{{v_display}}, {{v.attributes.min}}f, {{v.attributes.max}}f))
            {%- endif %}
            {
                if (ImGui::IsItemActivated())
                {
                    editParameter({{loop.index-1}}, true);
                    setParameterValue({{loop.index-1}}, f{{v_display}});
                }
            }
        {%- endif %}
    {% endfor %}
            if (ImGui::IsItemDeactivated())
            {
            {%- for i in range(0, receivers|length) %}
                editParameter({{i}}, false);
            {%- endfor %}
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
