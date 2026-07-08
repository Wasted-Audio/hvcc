{{copyright}}

#include "DistrhoUI.hpp"
#include "DistrhoPluginInfo.h"
#include "nanovg.h"

#include "{{class_name}}.hpp"

START_NAMESPACE_DISTRHO

// -----------------------------------------------------------------------------------------------------------

{%- if (receivers|length > 0) or (senders|length > 0) or (events|length > 0) %}
enum HeavyParams {
    {%- for k, v in receivers + senders + events %}
    k{{v.display|capitalize}},
    {%- endfor %}
    kParameterCount
};
{%- endif %}

{{class_name}}::{{class_name}}()
    : UI(DISTRHO_UI_DEFAULT_WIDTH, DISTRHO_UI_DEFAULT_HEIGHT)
{
    const float width = getWidth();
    const float height = getHeight();
    const double scaleFactor = getScaleFactor();

    {%- if meta.ui_theme is not none %}
        {%- for k, set in meta.ui_themes[meta.ui_theme] -%}
            {%- if k == "obj_corner_radius" and set is not none %}
    Corners::objectCornerRadius = {{set}};
            {%- elif k == "cnv_color" and set is not none %}
    Colors::cnvColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "cnv_txt_color" and set is not none%}
    Colors::cnvTextColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "io_color" and set is not none %}
    Colors::ioColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "bg_color" and set is not none %}
    Colors::bgColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "sel_color" and set is not none %}
    Colors::selColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "com_txt_color" and set is not none %}
    Colors::comTextColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- elif k == "out_color" and set is not none %}
    Colors::outColor = nvgRGB{{set.as_rgb_tuple()}};
            {%- endif %}
        {%- endfor %}
    {%- endif %}

    // mainpatch
    mainPatch = new PDMainpatch(this);
    mainPatch->setSize(width * scaleFactor, height * scaleFactor);

    {%- for i in gui_objects -%}
    {{i}}
    {%- endfor %}
}

{{class_name}}::~{{class_name}}()
{
}

void {{class_name}}::onNanoDisplay()
{
    const float width = getWidth();
    const float height = getHeight();
    const double scaleFactor = getScaleFactor();

    NVGcontext* nvg = getContext();

    nvgFillColor(nvg, Colors::cnvColor);
    nvgBeginPath(nvg);
    nvgRect(nvg, 0, 0, width * scaleFactor, height * scaleFactor);
    nvgFill(nvg);
    nvgStroke(nvg);
}

void {{class_name}}::parameterChanged(uint32_t index, float value)
{
    switch (index)
    {
{%- for k, v in receivers %}
        case k{{v.display|capitalize}}:
    {%- if v.attributes.type == "bool" %}
            {{v.display}}->setDown(static_cast<bool>(value));
    {%- else %}
            {{v.display}}->setValue(value);
    {%- endif %}
            break;
{%- endfor %}
        default:
            break;
    }
    repaint();
}

void {{class_name}}::sliderValueChanged(SubWidget *const widget, float value)
{
    const uint id = widget->getId();
    setParameterValue(id, value);
}

void {{class_name}}::switchClicked(SubWidget *const widget, bool down)
{
    const uint id = widget->getId();
    setParameterValue(id, static_cast<float>(down));
}

void {{class_name}}::bangClicked(SubWidget *const widget)
{
    const uint id = widget->getId();
    setParameterValue(id, 1.0f);
}

void {{class_name}}::radioValueChanged(SubWidget *const widget, uint index)
{
    const uint id = widget->getId();
    setParameterValue(id, static_cast<float>(index));
}

void {{class_name}}::numberValueChanged(SubWidget *const widget, float value)
{
    const uint id = widget->getId();
    setParameterValue(id, value);
}

void {{class_name}}::knobValueChanged(SubWidget *const widget, float value)
{
    const uint id = widget->getId();
    setParameterValue(id, value);
}


UI *createUI()
{
    return new {{class_name}}();
}

// -----------------------------------------------------------------------------------------------------------

END_NAMESPACE_DISTRHO
