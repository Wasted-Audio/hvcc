{{copyright}}

#include "DistrhoUI.hpp"
#include "ResizeHandle.hpp"

START_NAMESPACE_DISTRHO

// --------------------------------------------------------------------------------------------------------------------
{%- if (receivers|length > 0) or (senders|length > 0) %}
enum HeavyParams {
    {%- for k, v in receivers + senders -%}
    {{v.display|upper}},
    {%- endfor %}
};
{%- endif %}

class ImGuiPluginUI : public UI
{
    {% for k, v in receivers + senders -%}
        {%- if v.attributes.type == 'bool': %}
    bool f{{v.display|lower}} = {{v.attributes.default}}f != 0.0f;
        {%- elif v.attributes.type == 'int': %}
    int f{{v.display|lower}} = {{v.attributes.default}};
        {%- else %}
    float f{{v.display|lower}} = {{v.attributes.default}}f;
        {%- endif %}
    {%- endfor %}

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
    {%- if (receivers|length > 0) or (senders|length > 0) %}
        switch (index) {
            {% for k, v  in receivers + senders -%}
            case {{v.display|upper}}:
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
    {%- for k, v in receivers + senders %}
        {%- set v_display = v.display|lower %}
        {%- if meta.enumerators != None and meta.enumerators[v.display] is defined -%}
            {%- set enums = meta.enumerators[v.display] -%}
            {%- set enumlen = enums|length %}
            {%- set enum_list = v_display + "_list" %}

            const char* {{enum_list}}[{{enumlen}}] = {
                {%- for i in enums %}
                "{{i}}",
                {%- endfor %}
            };

            if (ImGui::BeginCombo("{{v.display.replace('_', ' ')}}", {{enum_list}}[f{{v_display}}]))
            {
                for (int n = 0; n < {{enumlen}}; n++)
                {
                    bool is_selected = (f{{v_display}} == n);
                    if (ImGui::Selectable({{enum_list}}[n], is_selected))
                    {
                        f{{v_display}} = n;
                        editParameter({{v.display|upper}}, true);
                        setParameterValue({{v.display|upper}}, f{{v_display}});
                    }
                    if (is_selected)
                        ImGui::SetItemDefaultFocus();
                }
                ImGui::EndCombo();
            }
        {%- else %}
            {%- if v.attributes.type == 'bool': %}
            if (ImGui::Toggle("{{v.display.replace('_', ' ')}}", &f{{v_display}}))
            {%- elif v.attributes.type == 'int' %}
            if (ImGui::SliderInt("{{v.display.replace('_', ' ')}}", &f{{v_display}}, {{v.attributes.min}}f, {{v.attributes.max}}f))
            {%- else %}
            if (ImGui::SliderFloat("{{v.display.replace('_', ' ')}}", &f{{v_display}}, {{v.attributes.min}}f, {{v.attributes.max}}f))
            {%- endif %}
            {
            {%- if not v.type == "send" %}
                if (ImGui::IsItemActivated())
                {
                    editParameter({{v.display|upper}}, true);
                }
                setParameterValue({{v.display|upper}}, f{{v_display}});
            {%- endif %}
            }
        {%- endif %}
    {% endfor %}
            if (ImGui::IsItemDeactivated())
            {
            {% for k, v  in receivers + senders -%}
                editParameter({{v.display|upper}}, false);
            {% endfor -%}
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
