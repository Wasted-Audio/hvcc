{{copyright}}

#include "DistrhoUI.hpp"
#include "ResizeHandle.hpp"

START_NAMESPACE_DISTRHO

// --------------------------------------------------------------------------------------------------------------------

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
        {%- if meta.enumerators is defined and meta.enumerators[v.display] is defined -%}
            {%- set enums = meta.enumerators[v.display] -%}
            {%- set enumlen = enums|length %}
            const char* items[] = {
                {%- for i in enums %}
                "{{i}}",
                {%- endfor %}
            };

            float item_values[] = {
                {%- for i in enums %}
                {{enums[i]}}f,
                {%- endfor %}
            };

            int default_item = std::distance(item_values, std::find(item_values, item_values + {{enumlen}}, {{v.attributes.default}}f));
            static const char* current_item = items[default_item];

            if (ImGui::BeginCombo("{{v.display.replace('_', ' ')}}", current_item))
            {
                for (int n = 0; n < {{enumlen}}; n++)
                {
                    bool is_selected = (current_item == items[n]); // You can store your selection however you want, outside or inside your objects
                    if (ImGui::Selectable(items[n], is_selected))
                    {
                        current_item = items[n];
                        f{{v.display|lower}} = item_values[n];
                        editParameter({{loop.index-1}}, true);
                        setParameterValue({{loop.index-1}}, f{{v.display|lower}});
                    }
                    if (is_selected)
                        ImGui::SetItemDefaultFocus();   // You may set the initial focus when opening the combo (scrolling + for keyboard navigation support)
                }
                ImGui::EndCombo();
            }
        {%- else %}
            {%- if v.attributes.type == 'bool': %}
            if (ImGui::Toggle("{{v.display.replace('_', ' ')}}", &f{{v.display|lower}}))
            {%- else %}
            if (ImGui::SliderFloat("{{v.display.replace('_', ' ')}}", &f{{v.display|lower}}, {{v.attributes.min}}f, {{v.attributes.max}}f))
            {%- endif %}
            {
                if (ImGui::IsItemActivated())
                {
                    editParameter({{loop.index-1}}, true);
                    setParameterValue({{loop.index-1}}, f{{v.display|lower}});
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
