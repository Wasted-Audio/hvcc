{{copyright}}

#include "DistrhoUI.hpp"
#include "DistrhoPluginInfo.h"
#include "nanovg.h"

#include "Common.hpp"
#include "{{class_name}}.hpp"

START_NAMESPACE_DISTRHO

// -----------------------------------------------------------------------------------------------------------

{%- if (receivers|length > 0) or (senders|length > 0) %}
enum HeavyParams {
    {%- for k, v in receivers + senders %}
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
        // case kSlider:
        //     mySlider->setValue(value);
        //     break;
        // case kSlider2:
        //     mySlider2->setValue(value);
        //     break;
        // case kToggle:
        //     myToggle->setDown(static_cast<bool>(value));
        //     break;
        // case kToggle2:
        //     myToggle2->setDown(static_cast<bool>(value));
        //     break;
        // case kRadio:
        //     myRadio->setValue(value);
        //     break;
        // case kRadio2:
        //     myRadio2->setValue(value);
        //     break;
        // case kNumber:
        //     myNumber->setValue(value);
        //     break;
        // case kFloat:
        //     myFloat->setValue(value);
        //     break;
        // case kKnob:
        //     myKnob->setValue(value);
        //     break;
        // case kKnob2:
        //     myKnob2->setValue(value);
        //     break;
        // case kKnob3:
        //     myKnob3->setValue(value);
        //     break;
        default:
            break;
    }
    repaint();
}

void {{class_name}}::sliderValueChanged(SubWidget *const widget, float value)
{
    printf("value changed: %f\n", value);
    const uint id = widget->getId();
    setParameterValue(id, value);
}

void {{class_name}}::switchClicked(SubWidget *const widget, bool down)
{
    printf("switch clicked: %d\n", down);
    const uint id = widget->getId();
    setParameterValue(id, static_cast<float>(down));
}

void {{class_name}}::bangClicked(SubWidget *const widget)
{
    printf("bang clicked\n");
    const uint id = widget->getId();
    setParameterValue(id, 1.0f);
}

void {{class_name}}::radioValueChanged(SubWidget *const widget, uint index)
{
    printf("radio clicked: %d\n", index);
    const uint id = widget->getId();
    setParameterValue(id, static_cast<float>(index));
}

void {{class_name}}::numberValueChanged(SubWidget *const widget, float value)
{
    printf("number value changed: %f\n", value);
    const uint id = widget->getId();
    setParameterValue(id, value);
}

void {{class_name}}::knobValueChanged(SubWidget *const widget, float value)
{
    printf("knob value changed: %f\n", value);
    const uint id = widget->getId();
    setParameterValue(id, value);
}


UI *createUI()
{
    return new {{class_name}}();
}

// -----------------------------------------------------------------------------------------------------------

END_NAMESPACE_DISTRHO
